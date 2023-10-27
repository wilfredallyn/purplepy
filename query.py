from datetime import datetime, timedelta
from ingest import parse_mention_tags, parse_reply_tags
import pandas as pd
import json
from nostr_sdk import Keys, Client, Filter, Options, PublicKey, Timestamp
from sqla_models import Event, Reply
from sqlalchemy import func
from utils import postprocess


def init_client():
    keys = Keys.generate()
    opts = Options().timeout(timedelta(seconds=1000))
    client = Client.with_opts(keys, opts)
    client.add_relay("wss://relay.damus.io")
    client.add_relay("wss://nostr.oxtr.dev")
    client.add_relay("wss://relay.nostr.band")
    client.add_relay("wss://relay.primal.net")
    client.add_relay("wss://relay.mostr.pub")
    client.connect()
    # return None if can't connect
    return client


def query_relay(
    client, npub=None, kind=None, num_days=None, num_limit=None, timeout_secs=30
):
    filter = Filter()
    if kind:
        filter = filter.kind(kind)
    if npub:
        # fix: check if hex or bech32
        # PublicKey.from_hex('22dd8df1fed1da2574c4917146d93dcb679549aeead8f98cbbaf166d183662ad').to_bech32()
        pk = PublicKey.from_bech32(npub)
        filter = filter.author(pk.to_hex())
    if num_days:
        filter = filter.since(get_filter_timestamp(num_days=num_days))
    if num_limit:
        filter = filter.limit(num_limit)
    events = client.get_events_of([filter], timedelta(seconds=timeout_secs))
    df = pd.DataFrame([json.loads(event.as_json()) for event in events]).set_index("id")
    df = postprocess(df)
    df_reply = parse_reply_tags(df)
    df_mention = parse_mention_tags(df)
    return df, df_reply, df_mention


def query_db(Session, npub=None, kind=None):
    # fix: check if hex or bech32
    # PublicKey.from_hex('22dd8df1fed1da2574c4917146d93dcb679549aeead8f98cbbaf166d183662ad').to_bech32()
    with Session() as session:
        subquery = (
            session.query(Reply.ref_id, func.count(Reply.id).label("reply_count"))
            .group_by(Reply.ref_id)
            .subquery()
        )

        sqla_query = session.query(Event, subquery.c.reply_count).outerjoin(
            subquery, subquery.c.ref_id == Event.id
        )

        if npub:
            pk = PublicKey.from_bech32(npub).to_hex()
            sqla_query = sqla_query.filter(Event.pubkey == pk)
        if kind:
            sqla_query = sqla_query.filter(Event.kind == int(kind))
        results = sqla_query.all()

    data = []
    for event, reply_count in results:
        row = event.__dict__.copy()
        row["reply_count"] = reply_count
        data.append(row)
    df = pd.DataFrame(data)
    if "kind" in df.columns:
        df["kind"] = df["kind"].astype(str)
    if df.empty:
        return df
    else:
        return postprocess(df.set_index("id"), dedupe=True)


def get_filter_timestamp(num_days: int):
    ts = int((datetime.now() - timedelta(days=num_days)).timestamp())
    return Timestamp.from_secs(ts)


def get_replys_db(event_id, df_reply):
    return df_reply[df_reply.ref_id == event_id].sort_values(
        "created_at", ascending=True
    )


# print("Getting events from relays...")
# filter = Filter().authors([keys.public_key().to_hex()])
# events = client.get_events_of([filter], timedelta(seconds=10))
# for event in events:
#     print(event.as_json())

# filter = Filter().pubkey(pk).kind(4).since(Timestamp.now())
# client.subscribe([filter])

# write event
# event = EventBuilder.new_text_note("Hello from Rust Nostr Python bindings!", []).to_event(keys)
# event_id = client.send_event(event)

# relay stats
# while True:
#     for url, relay in client.relays().items():
#         stats = relay.stats()
#         print(f"Relay: {url}")
#         print(f"Connected: {relay.is_connected()}")
#         print(f"Status: {relay.status()}")
