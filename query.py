from datetime import timedelta
import pandas as pd
import json
from nostr_sdk import Keys, Client, Filter, Options, PublicKey
from sqla_models import Events


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
    return df


def query_events_by_author(client, npub):
    # fix: check if hex or bech32
    # PublicKey.from_hex('22dd8df1fed1da2574c4917146d93dcb679549aeead8f98cbbaf166d183662ad').to_bech32()
    pk = PublicKey.from_bech32(npub)
    filter = Filter().author(pk.to_hex()).limit(10)
    events = client.get_events_of([filter], timedelta(seconds=10))
    df = pd.DataFrame([json.loads(event.as_json()) for event in events]).set_index("id")
    return df


def query_db(Session, npub):
    # fix: check if hex or bech32
    # PublicKey.from_hex('22dd8df1fed1da2574c4917146d93dcb679549aeead8f98cbbaf166d183662ad').to_bech32()
    pk = PublicKey.from_bech32(npub).to_hex()
    with Session() as session:
        results = session.query(Events).filter(Events.pubkey == pk).all()
    df = pd.DataFrame([r.__dict__ for r in results])
    if "_sa_instance_state" in df.columns:
        df = df.drop("_sa_instance_state", axis=1)
    return df
