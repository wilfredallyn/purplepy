from datetime import timedelta
from nostr_sdk import (
    Client,
    Keys,
    Options,
)


def init_client():
    keys = Keys.generate()
    opts = Options().timeout(timedelta(seconds=30))
    client = Client.with_opts(keys, opts)
    client.add_relay("wss://relay.damus.io")
    client.add_relay("wss://nostr.oxtr.dev")
    client.add_relay("wss://relay.nostr.band")
    client.add_relay("wss://relay.primal.net")
    client.add_relay("wss://relay.mostr.pub")
    client.add_relay("wss://relay.nostr.band")
    client.connect()
    return client
