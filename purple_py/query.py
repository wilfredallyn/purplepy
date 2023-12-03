from nostr_sdk import PublicKey
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
        return response["data"]["Get"]["Event"]


# def get_events_by_time(df):
#     if "created_at" in df.columns:
#         df["created_at"] = df["created_at"].apply(parse_datetime)
#     df["day_of_week"] = df["created_at"].dt.day_name()
#     df["hour_of_day"] = df["created_at"].dt.hour
#     return df
