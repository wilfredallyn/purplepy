import pandas as pd
import json
from nostr_sdk import Keys, Client, EventBuilder, Filter, PublicKey
from datetime import timedelta
import time


def query_events(client, npub):
    pk = PublicKey.from_bech32(npub)
    filter = Filter().kind(1).author(pk.to_hex()).limit(10)
    events = client.get_events_of([filter], timedelta(seconds=10))
    df = pd.DataFrame([json.loads(event.as_json()) for event in events]).set_index("id")
    return df


def query_db(engine, sql_query):
    return pd.read_sql(sql_query, engine)
