from nostr_sdk import PublicKey
import pandas as pd
from purple_py.log import logger


def query_weaviate(client, npub=None, kind=None):
    where_clauses = []
    if npub:
        pk = PublicKey.from_bech32(npub).to_hex()
        npub_filter = {"path": ["pubkey"], "operator": "Equal", "valueString": pk}
        where_clauses.append(npub_filter)

    if kind:
        kind_filter = {"path": ["kind"], "operator": "Equal", "valueInt": int(kind)}
        where_clauses.append(kind_filter)

    combined_filter = None
    if where_clauses:
        if len(where_clauses) > 1:
            combined_filter = {"operator": "And", "operands": where_clauses}
        else:
            combined_filter = where_clauses[0]

    response = (
        client.query.get("Event", ["event_id, created_at, kind, content"])
        # .get("Event", ["event_id, created_at, kind, content, _additional { vector }"])
        .with_where(combined_filter)
        .with_limit(10000)
        .do()
    )

    if "errors" in response:
        logger.error(f"Error querying weaviate: {response['errors'][0]['message']}")
    else:
        return pd.DataFrame(response["data"]["Get"]["Event"])


def search_weaviate(client, text):
    response = (
        client.query.get("Event", ["event_id, created_at, kind, content"])
        .with_near_text({"concepts": [text]})
        .with_limit(10)
        .with_additional(["distance"])
        .do()
    )

    if "errors" in response:
        logger.error(f"Error querying weaviate: {response['errors'][0]['message']}")
    else:
        df = pd.DataFrame(response["data"]["Get"]["Event"])
        df["distance"] = df["_additional"].apply(
            lambda x: x["distance"] if isinstance(x, dict) else None
        )
        return df.sort_values("distance", ascending=False).drop(columns=["_additional"])
