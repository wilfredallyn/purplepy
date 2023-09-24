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
    client.add_relay("wss://nostr.openchain.fr")
    client.add_relay("wss://relay.nostr.band")
    client.add_relay("wss://relay.primal.net")
    client.add_relay("wss://relay.mostr.pub")
    client.connect()
    return client


def query_events(client, kind=None, num_limit=1000):
    if kind:
        filter = Filter().kind(kind).limit(num_limit)
    else:
        filter = Filter().limit(num_limit)
    events = client.get_events_of([filter], timedelta(seconds=50))
    df = pd.DataFrame([json.loads(event.as_json()) for event in events]).set_index("id")
    return postprocess(df)


def query_events_by_author(client, npub, timeout_secs=10):
    # fix: check if hex or bech32
    # PublicKey.from_hex('22dd8df1fed1da2574c4917146d93dcb679549aeead8f98cbbaf166d183662ad').to_bech32()
    pk = PublicKey.from_bech32(npub)
    filter = Filter().author(pk.to_hex()).limit(10)
    events = client.get_events_of([filter], timedelta(seconds=timeout_secs))
    df = pd.DataFrame([json.loads(event.as_json()) for event in events]).set_index("id")
    return postprocess(df)


def query_db(Session, npub):
    # fix: check if hex or bech32
    # PublicKey.from_hex('22dd8df1fed1da2574c4917146d93dcb679549aeead8f98cbbaf166d183662ad').to_bech32()
    pk = PublicKey.from_bech32(npub).to_hex()
    with Session() as session:
        results = session.query(Events).filter(Events.pubkey == pk).all()
    df = pd.DataFrame([r.__dict__ for r in results])
    return postprocess(df)


def get_filter_timestamp(num_days: int):
    ts = int((datetime.now() - timedelta(days=num_days)).timestamp())
    return Timestamp.from_secs(ts)


# def filter_days(filter: Filter, num_days: int):
#     ts = int((datetime.now() - timedelta(days=num_days)).timestamp())
#     return filter.since())


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
