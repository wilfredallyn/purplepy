from datetime import datetime, timedelta
import pandas as pd
import json
from nostr_sdk import Keys, Client, Filter, Options, PublicKey, Timestamp
from sqla_models import Events
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


def query_events(
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
    return postprocess(df)


def query_db(Session, npub=None, kind=None):
    # fix: check if hex or bech32
    # PublicKey.from_hex('22dd8df1fed1da2574c4917146d93dcb679549aeead8f98cbbaf166d183662ad').to_bech32()
    with Session() as session:
        sqla_query = session.query(Events)
        if npub:
            pk = PublicKey.from_bech32(npub).to_hex()
            sqla_query = sqla_query.filter(Events.pubkey == pk)
        if kind:
            sqla_query = sqla_query.filter(Events.kind == int(kind))
        results = sqla_query.all()
    df = pd.DataFrame([r.__dict__ for r in results])
    return postprocess(df)


def get_filter_timestamp(num_days: int):
    ts = int((datetime.now() - timedelta(days=num_days)).timestamp())
    return Timestamp.from_secs(ts)


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
