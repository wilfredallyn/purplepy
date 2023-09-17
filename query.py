import pandas as pd
import json
from nostr_sdk import Keys, Client, EventBuilder, Filter, PublicKey
from datetime import timedelta
import time


def query_events(client, kind=None, num_limit=1000):
    if kind:
        filter = Filter().kind(kind).limit(num_limit)
    else:
        filter = Filter().limit(num_limit)
    events = client.get_events_of([filter], timedelta(seconds=50))
    df = pd.DataFrame([json.loads(event.as_json()) for event in events]).set_index("id")
    return df


def query_events_by_author(client, npub):
    pk = PublicKey.from_bech32(npub)
    filter = Filter().kind(1).author(pk.to_hex()).limit(10)
    events = client.get_events_of([filter], timedelta(seconds=10))
    df = pd.DataFrame([json.loads(event.as_json()) for event in events]).set_index("id")
    return df


def query_db(engine, sql_query):
    # query nested jsonb: sql_query = "SELECT * FROM events WHERE tags->>'t' = 'sm41623576'";
    return pd.read_sql(sql_query, engine)
