from utils import parse_datetime


def analyze_relays(client):
    for url, relay in client.relays().items():
        stats = relay.stats()
        print(f"Relay: {url}")
        print(f"Connected: {relay.is_connected()}")
        print(f"Status: {relay.status()}")
        print("Stats:")
        print(f"    Attempts: {stats.attempts()}")
        print(f"    Success: {stats.success()}")
        print(f"    Bytes sent: {stats.bytes_sent()}")
        print(f"    Bytes received: {stats.bytes_received()}")
        print(f"    Connected at: {stats.connected_at().to_human_datetime()}")
        if stats.latency() != None:
            print(f"    Latency: {stats.latency().total_seconds() * 1000} ms")

        print("###########################################")


def get_events_by_time(df):
    if "created_at" in df.columns:
        df["created_at"] = df["created_at"].apply(parse_datetime)
    df["day_of_week"] = df["created_at"].dt.day_name()
    df["hour_of_day"] = df["created_at"].dt.hour
    return df
