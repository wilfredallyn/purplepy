import pandas as pd
from query import query_events
from sqlalchemy import create_engine


def init_db(client):
    engine = create_engine("postgresql://postgres@localhost:5432/postgres")

    npub = "npub1dergggklka99wwrs92yz8wdjs952h2ux2ha2ed598ngwu9w7a6fsh9xzpc"
    df = query_events(client, npub)

    # loses association with key (e or p may have different relay url)
    df["tags_relay_url"] = df["tags"].apply(
        lambda x: {item[0]: item[2] for item in x if len(item) > 2} or None
    )
    df["tags"] = df["tags"].apply(
        lambda x: {item[0]: item[1] if len(item) > 1 else None for item in x} or None
    )

    engine = create_engine("postgresql://postgres@localhost:5432/postgres")
    df.to_sql(
        "events",
        engine,
        if_exists="replace",  # append
        method="multi",
        dtype={
            "tags": JSONB,
            "tags_relay_url": JSONB,
        },
    )


def parse_reply_tags(df):
    e_rows = []
    for _, row in df.iterrows():
        for lst in row["tags"]:
            if lst and lst[0] == "e":
                if len(lst) == 4:
                    # ["e", "1fcc...", "wss://nos.lol/", "reply"]
                    e_rows.append(
                        [row.name, row.created_at, lst[1], row.kind, lst[2], lst[3]]
                    )
                elif len(lst) == 3:
                    # ['e', '10c9a19..', 'wss://nostr.wine/']
                    # ['e', '9ee62e263f', '']
                    e_rows.append(
                        [row.name, lst[1], row.created_at, row.kind, lst[2], None]
                    )
                elif len(lst) == 2:
                    # ["e", "1fcc...""]
                    e_rows.append(
                        [row.name, lst[1], row.created_at, row.kind, None, None]
                    )
                else:
                    print(f"expected 2-4 fields for e tags: {row}: {lst}")
                    # fix: be169dcde5d3a423916827449f37bd09be0e2cbb34ddf62204d6c0ba97d03a0c: many relay_urls
                    # raise ValueError("expected 2-4 fields for e tags")

    # https://github.com/nostr-protocol/nips#standardized-tags
    df_reply = pd.DataFrame(
        e_rows,
        columns=["source_id", "event_id", "created_at", "kind", "relay_url", "marker"],
    )  # .set_index(["source_id", "event_id"])
    return df_reply


def parse_mention_tags(df):
    p_rows = []
    for _, row in df.iterrows():
        for lst in row["tags"]:
            if lst and lst[0] == "p":
                if len(lst) == 4:
                    # ['p', '97c70a...', 'wss://relayable.org', 'hodlbod']
                    # ['p', 'fa984b..', '', 'mention' ]
                    p_rows.append(
                        [row.name, lst[1], row.created_at, row.kind, lst[2], lst[3]]
                    )
                elif len(lst) == 3:
                    # ['p', 'fa984bd...', 'pablof7z']
                    # ['p', 'b708f73...', 'wss://nostr-relay.wlvs.space']
                    p_rows.append(
                        [row.name, lst[1], row.created_at, row.kind, lst[2], None]
                    )
                elif len(lst) == 2:
                    # ['p', 'ee11a5']
                    p_rows.append(
                        [row.name, lst[1], row.created_at, row.kind, None, None]
                    )
                elif len(lst) > 4:
                    print(f"{row.name}: {lst}")
                    raise ValueError("> 4 fields for p tags")

    # https://github.com/nostr-protocol/nips/blob/master/02.md#petname-scheme
    df_mention = pd.DataFrame(
        p_rows,
        columns=["source_id", "user_id", "created_at", "kind", "relay_url", "petname"],
    )  # .set_index(["source_id", "event_id"])
    return df_mention


def get_thread(event_id, df_reply):
    return df_reply[df_reply.event_id == event_id].sort_values(
        "created_at", ascending=True
    )
