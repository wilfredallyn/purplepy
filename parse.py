import json
import pandas as pd


def parse_user_metadata(df):
    df_metadata = df[df.kind == 0].copy().reset_index(drop=True)
    df_content = (
        df_metadata["content"]
        .apply(json.loads)
        .apply(pd.Series)
        .reset_index(drop=True)
        .drop("pubkey", axis=1)
    )
    df_user = (
        pd.concat(
            [
                df_metadata["pubkey"],
                df_content,
            ],
            axis=1,
        )
    ).set_index("pubkey")
    return df_user


def parse_tags(df, output_col, filter_tag=None):
    # filter_tag = "p", "e", etc.
    cols = ["pubkey", "created_at", "tags"]
    df = df.reset_index(drop=True)[cols].explode("tags")
    if filter_tag:
        df = df[df["tags"].str[0] == filter_tag]
    df[output_col] = df["tags"].str[1]
    df = df.drop(columns="tags").reset_index(drop=True)
    return df


def parse_reply_tags(df):
    df = df.explode("tags")
    df = df[df["tags"].str[0] == "e"]
    e_rows = df.apply(parse_reply_row, axis=1).dropna().tolist()

    # https://github.com/nostr-protocol/nips#standardized-tags
    df_reply = pd.DataFrame(
        e_rows,
        columns=["id", "pubkey", "ref_id", "created_at", "kind", "relay_url", "marker"],
    )  # .set_index(["id", "ref_id"])
    return df_reply


def parse_reply_row(row):
    lst = row["tags"]
    if lst and lst[0] == "e":
        if len(lst) == 4:
            # lst ["e", "1fcc...", "wss://nos.lol/", "reply"]
            # return [id, pubkey, ref_id, created_at, kind, relay_url, marker]
            return [
                row.name,
                row.pubkey,
                lst[1],
                row.created_at,
                row.kind,
                lst[2],
                lst[3],
            ]
        elif len(lst) == 3:
            # ["e", "10c9a19..", "wss://nostr.wine/"]
            # ["e", "9ee62e263f..."", ""]
            # return [id, pubkey, ref_id, created_at, kind, relay_url, marker]
            return [
                row.name,
                row.pubkey,
                lst[1],
                row.created_at,
                row.kind,
                lst[2],
                None,
            ]
        elif len(lst) == 2:
            # ["e", "1fcc...""]
            # return [id, pubkey, ref_id, created_at, kind, relay_url, marker]
            return [row.name, row.pubkey, lst[1], row.created_at, row.kind, None, None]
        else:
            print(f"expected 2-4 fields for e tags: {row}: {lst}")
    return None


def parse_mention_tags(df):
    df = df.explode("tags")
    df = df[df["tags"].str[0] == "p"]
    p_rows = df.apply(parse_mention_row, axis=1).dropna().tolist()

    # https://github.com/nostr-protocol/nips/blob/master/02.md#petname-scheme
    df_mention = pd.DataFrame(
        p_rows,
        columns=[
            "id",
            "pubkey",
            "ref_id",
            "created_at",
            "kind",
            "relay_url",
            "petname",
        ],
    )  # .set_index(["id", "ref_id"])
    return df_mention


def parse_mention_row(row):
    lst = row["tags"]
    if lst and lst[0] == "p":
        if len(lst) == 4:
            # ['p', '97c70a...', 'wss://relayable.org', 'hodlbod']
            # ['p', 'fa984b..', '', 'mention' ]
            # return [id, pubkey, ref_id, created_at, kind, relay_url, petname]
            return [
                row.name,
                row.pubkey,
                lst[1],
                row.created_at,
                row.kind,
                lst[2],
                lst[3],
            ]
        elif len(lst) == 3:
            # ['p', 'fa984bd...', 'pablof7z']
            # ['p', 'b708f73...', 'wss://nostr-relay.wlvs.space']
            # return [id, pubkey, ref_id, created_at, kind, relay_url, petname]
            return [
                row.name,
                row.pubkey,
                lst[1],
                row.created_at,
                row.kind,
                lst[2],
                None,
            ]

        elif len(lst) == 2:
            # ['p', 'ee11a5']
            # return [id, pubkey, ref_id, created_at, kind, relay_url, petname]
            return [row.name, row.pubkey, lst[1], row.created_at, row.kind, None, None]
        elif len(lst) > 4:
            print(f"{row.name}: {lst}")
            raise ValueError("> 4 fields for p tags")
    return None
