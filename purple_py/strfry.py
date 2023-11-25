from datetime import datetime, timezone
import json
import lmdb
import os

STRFRY_PATH = "/home/wa/Documents/strfry/strfry-db-test"
# STRFRY_PATH = os.getenv("STRFRY_DB_FOLDER")
WEAVIATE_BATCH_SIZE = os.getenv("WEAVIATE_CLIENT_BATCH_SIZE")
WEAVIATE_BATCH_SIZE = int(WEAVIATE_BATCH_SIZE) if WEAVIATE_BATCH_SIZE else 1000
MIN_CONTENT_LENGTH = os.getenv("MIN_CONTENT_LENGTH")
MIN_CONTENT_LENGTH = int(MIN_CONTENT_LENGTH) if MIN_CONTENT_LENGTH else 50


# pass in function to process for every record?
def read_strfy_db(client, process_fn, process_output):
    env = lmdb.open(path=STRFRY_PATH, max_dbs=10)
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
    text_kinds = [1, 31922, 31923]
    if (
        "content" in event_json
        and len(event_json["content"]) >= MIN_CONTENT_LENGTH
        and event_json["kind"] in text_kinds
    ):
        process_output["event_id_list"].append(event_json["id"])
        process_output["content_list"].append(event_json["content"])
    return process_output


def load_weaviate_data(event_json, batch, process_input):
    # encode embeddings, query for event_id, create data object
    event_id_list, content_list = process_input


def query_db_for_record(client, process_fn, process_input):
    env = lmdb.open(path=STRFRY_PATH, max_dbs=10)
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
