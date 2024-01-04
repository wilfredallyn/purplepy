import atexit
from datetime import datetime, timezone
from dotenv import load_dotenv
import json
import lmdb
import numpy as np
from purple_py.config import (
    MIN_CONTENT_LENGTH,
    NEO4J_IMPORT_DIR,
    NEO4J_PASSWORD,
    NEO4J_URI,
    NEO4J_USERNAME,
    STRFRY_PATH,
    WEAVIATE_BATCH_SIZE,
    WEAVIATE_CLIENT_URL,
    WEAVIATE_PAGE_LIMIT,
)
from purple_py.query import filter_users, get_user_uuid
from purple_py.log import logger
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from sentence_transformers import SentenceTransformer
import subprocess
import sys
import weaviate


def load_events_into_weaviate(client):
    # vectorize event content: parse content from events for embeddings
    process_output = {}
    process_output["event_id_list"] = []
    process_output["content_list"] = []

    process_output = read_strfry_db(
        client,
        process_fn=get_content_for_embeddings,
        process_output=process_output,
    )
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    process_output["embedding_list"] = embedding_model.encode(
        process_output["content_list"]
    )

    # load data into weaviate
    process_output["pubkey_dict"] = {}
    process_output = query_db_for_record(
        client=client,
        process_fn=create_weaviate_record,
        process_input=process_output,
    )
    add_npub_cross_ref(client)
    add_npub_mean_vec(client)


def read_strfry_db(client, process_fn, process_output):
    try:
        env = lmdb.open(path=STRFRY_PATH, max_dbs=10)
    except FileNotFoundError as e:
        msg = f"The strfry db directory '{e.filename}' does not exist"
        print(msg)
        logger.exception(msg)
        sys.exit(1)
    db_id = env.open_db(b"rasgueadb_defaultDb__Event__id")
    db_payload = env.open_db(b"rasgueadb_defaultDb__EventPayload")

    client.batch.configure(batch_size=WEAVIATE_BATCH_SIZE)
    with client.batch as batch:
        with env.begin(db=db_id) as txn:
            cursor = txn.cursor(db=db_id)
            for key, value in cursor:
                pl = txn.get(value, db=db_payload)
                if pl is not None:
                    # event_id = key.hex()[:64]
                    event_json = json.loads(pl[1:].decode("utf-8"))
                    process_output = process_fn(event_json, process_output, batch)
    return process_output


def get_content_for_embeddings(event_json, process_output, batch):
    # filter kinds by adding kind numbers to text_kinds
    # text_kinds = [1, 31922, 31923]
    if (
        "content" in event_json
        and len(event_json["content"]) >= MIN_CONTENT_LENGTH
        # and event_json["kind"] in text_kinds
    ):
        process_output["event_id_list"].append(event_json["id"])
        process_output["content_list"].append(event_json["content"])
    return process_output


def query_db_for_record(client, process_fn, process_input):
    try:
        env = lmdb.open(path=STRFRY_PATH, max_dbs=10)
    except FileNotFoundError as e:
        msg = f"The strfry db directory '{e.filename}' does not exist"
        print(msg)
        logger.exception(msg)
        sys.exit(1)
    db_id = env.open_db(b"rasgueadb_defaultDb__Event__id")
    db_payload = env.open_db(b"rasgueadb_defaultDb__EventPayload")

    event_id_list = process_input["event_id_list"]
    client.batch.configure(batch_size=WEAVIATE_BATCH_SIZE)
    with client.batch as batch:
        with env.begin() as txn:
            db_id_cursor = txn.cursor(db=db_id)
            for event_id in event_id_list:
                event_id_bytes = bytes.fromhex(event_id)
                if db_id_cursor.set_range(event_id_bytes):
                    k, v = db_id_cursor.item()
                    if k[:32] == event_id_bytes:
                        pl = txn.get(v, db=db_payload)
                        if pl:
                            event_json = json.loads(pl[1:].decode("utf-8"))
                            process_input = process_fn(event_json, batch, process_input)
                        else:
                            raise Exception("db corrupt!?")
                    else:
                        print("not found")
                else:
                    print("not found")
    return process_input


def create_weaviate_record(event_json, batch, process_input):
    event_id_list = process_input["event_id_list"]
    embedding_list = process_input["embedding_list"]

    pubkey = event_json["pubkey"]
    event_id = event_json["id"]
    event_idx = event_id_list.index(event_id)

    dt_utc = datetime.fromtimestamp(event_json["created_at"], timezone.utc)
    event_properties = {
        "event_id": event_id,
        "created_at": dt_utc.isoformat(),
        "pubkey": pubkey,
        "kind": event_json["kind"],
        "content": event_json["content"],
    }
    batch.add_data_object(
        data_object=event_properties,
        class_name="Event",
        vector=embedding_list[event_idx],
    )
    if pubkey not in process_input["pubkey_dict"]:
        process_input["pubkey_dict"][pubkey] = None
        user_properties = {
            "pubkey": pubkey,
        }
        batch.add_data_object(
            data_object=user_properties,
            class_name="User",
        )
    return process_input


def add_npub_cross_ref(client):
    offset = 0
    user_uuids_dict = {}
    with client.batch as batch:
        while True:
            events_response = (
                client.query.get(
                    "Event", ["event_id", "content", "pubkey", "_additional { id }"]
                )
                .with_limit(WEAVIATE_PAGE_LIMIT)
                .with_offset(offset)
                .do()
            )

            events = events_response["data"]["Get"]["Event"]
            if not events:
                break
            for event in events:
                pubkey = event["pubkey"]
                user_uuid = user_uuids_dict.get(pubkey)

                if not user_uuid:
                    user_response = (
                        client.query.get("User", ["_additional { id }"])
                        .with_where(
                            {
                                "operator": "Equal",
                                "path": ["pubkey"],
                                "valueString": pubkey,
                            }
                        )
                        .do()
                    )
                    if user_response["data"]["Get"]["User"]:
                        user_uuid = user_response["data"]["Get"]["User"][0][
                            "_additional"
                        ]["id"]
                        user_uuids_dict[pubkey] = user_uuid

                if user_uuid:
                    batch.add_reference(
                        from_object_uuid=user_uuid,
                        from_object_class_name="User",
                        from_property_name="hasCreated",
                        to_object_uuid=event["_additional"]["id"],
                        to_object_class_name="Event",
                    )
            if len(events) < WEAVIATE_PAGE_LIMIT:
                break
            offset += WEAVIATE_PAGE_LIMIT


def add_npub_mean_vec(client):
    df_filter = filter_users(client, min_num_events=5)
    df_vec = df_filter.groupby("pubkey")["vector"].apply(
        lambda x: np.mean(x.tolist(), axis=0)
    )

    for pubkey in df_vec.index:
        user_uuid = get_user_uuid(client, pubkey)

        # api v3 does not support batch update
        if user_uuid:
            client.data_object.update(
                uuid=user_uuid,
                class_name="User",
                data_object={},
                vector=df_vec.loc[pubkey],
            )


def create_weaviate_user_class(client):
    user_class = {
        "class": "User",
        "description": "Users",
        "vectorIndexType": "hnsw",
        "vectorIndexConfig": {
            "distance": "cosine",
        },
        # "invertedIndexConfig": {
        #     "stopwords": {
        #         "preset": "en",
        #     }
        # },
        "properties": [
            {"name": "pubkey", "dataType": ["text"]},
            {"name": "name", "dataType": ["text"]},
            {"name": "hasCreated", "dataType": ["Event"]},  # cross-reference
        ],
        "vectorizer": "text2vec-transformers",
        "moduleConfig": {
            "text2vec-transformers": {
                "vectorizeClassName": False,
            }
        },
    }
    if client.schema.exists(class_name="User"):
        client.schema.delete_class("User")
    client.schema.create_class(user_class)


def create_weaviate_event_class(client):
    event_class = {
        "class": "Event",
        "description": "Events",
        "vectorIndexType": "hnsw",
        "vectorIndexConfig": {
            "distance": "cosine",
        },
        "invertedIndexConfig": {
            "stopwords": {
                "preset": "en",
            }
        },
        "properties": [
            {
                "name": "event_id",
                "dataType": ["text"],
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": True,
                        "vectorizePropertyName": False,
                    }
                },
            },
            {
                "name": "created_at",
                "dataType": ["date"],
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": True,
                        "vectorizePropertyName": False,
                    }
                },
            },
            {
                "name": "pubkey",
                "dataType": ["text"],
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": True,
                        "vectorizePropertyName": False,
                    }
                },
            },
            {
                "name": "kind",
                "dataType": ["int"],
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": True,
                        "vectorizePropertyName": False,
                    }
                },
            },
            {
                "name": "content",
                "dataType": ["text"],
                "moduleConfig": {
                    "text2vec-transformers": {
                        "skip": False,
                        "vectorizePropertyName": False,
                    }
                },
            },
            # tags
        ],
        "vectorizer": "text2vec-transformers",
        "moduleConfig": {
            "text2vec-transformers": {
                "vectorizeClassName": False,
            }
        },
    }
    if client.schema.exists(class_name="Event"):
        client.schema.delete_class("Event")
    client.schema.create_class(event_class)


def load_neo4j_data():
    # add replys after add ref_pubkey
    expected_kinds = ["follows", "mentions", "reactions", "users"]
    # expected_kinds = ["follows", "mentions", "reactions", "replys", "users"]
    for kind_name in expected_kinds:
        command = f"echo ':source {NEO4J_IMPORT_DIR}/import_{kind_name}.cypher' | cypher-shell -u neo4j -p neo4j"
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            msg = "Error executing command:", result.stderr
            logger.exception(msg)
            print(msg)
            sys.exit(1)


def get_neo4j_driver():
    try:
        neo4j_driver = GraphDatabase.driver(
            NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
    except ServiceUnavailable as e:
        logger.exception(f"Error connecting to neo4j: {e}")
        raise
    return neo4j_driver


def close_neo4j_driver():
    neo4j_driver.close()


def get_created_at_dates(client):
    process_output = {}
    process_output["created_at_list"] = []

    process_output = read_strfry_db(
        client,
        process_fn=parse_created_at_dates,
        process_output=process_output,
    )
    created_at_list = process_output["created_at_list"]
    # start_date = np.percentile(created_at_list, 2.5)
    # end_date = np.percentile(created_at_list, 97.5)
    return created_at_list


def parse_created_at_dates(event_json, process_output, batch):
    process_output["created_at_list"].append(event_json["created_at"])
    return process_output


neo4j_driver = get_neo4j_driver()
atexit.register(close_neo4j_driver)

try:
    client = weaviate.Client(
        url=WEAVIATE_CLIENT_URL,
    )
except weaviate.exceptions.WeaviateStartUpError:
    msg = "You need to start the Weaviate docker container with command 'docker compose up -d'"
    print(msg)
    logger.exception(msg)
    sys.exit(1)
