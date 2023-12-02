from dotenv import load_dotenv
import json
from log import logger
import os
import pandas as pd


load_dotenv()


def parse_event_json(db_file):
    NEO4J_IMPORT_DIR = os.getenv("NEO4J_IMPORT_DIR")
    data = []
    with open(db_file, "r") as file:
        for line in file:
            data.append(json.loads(line))
    df = pd.DataFrame(data)
    df = df[df["id"].notna() & (df["id"] != "")]
    df = df.set_index("id")

    df_reply = parse_reply_tags(df.copy())
    df_reply.to_csv(os.path.join(NEO4J_IMPORT_DIR, "replys.csv"))

    df_mention = parse_mention_tags(df.copy())
    df_mention.to_csv(os.path.join(NEO4J_IMPORT_DIR, "mentions.csv"))

    df_reaction = parse_reactions(df.copy())
    df_reaction.to_csv(os.path.join(NEO4J_IMPORT_DIR, "reactions.csv"))

    df_follow = parse_follows(df.copy())
    df_follow.to_csv(os.path.join(NEO4J_IMPORT_DIR, "follows.csv"))

    df_user = parse_user_metadata(df.copy())
    df_user.to_csv(os.path.join(NEO4J_IMPORT_DIR, "users.csv"))
    return


def parse_user_metadata(df):
    # df_metadata.columns from postprocess: ['id', 'content', 'created_at', 'kind', 'pubkey', 'sig', 'tags', 'kind_name']
    df_metadata = df[df.kind == 0].copy().reset_index(drop=False)
    df_content = (
        df_metadata["content"]
        .apply(lambda s: safe_json_loads(s))
        .apply(pd.Series)
        .reset_index(drop=True)
        .drop(columns=["created_at", "pubkey"], errors="ignore")
    )
    df_user = (
        pd.concat(
            [
                df_metadata[["id", "pubkey", "created_at", "tags"]],
                df_content,
            ],
            axis=1,
        )
    ).set_index("pubkey")
    return df_user


def safe_json_loads(s):
    try:
        return json.loads(s.replace(r"\n", " "))
    except json.JSONDecodeError:
        logger.error(f"Error parsing JSON content: {s}")
        return {}


def parse_tags(df, filter_tag=None, keep_col=None, keep_last=False):
    # filter_tag = "p", "e", ["p", "e"], etc.
    cols = ["id", "pubkey", "created_at", "tags"]
    if keep_col:
        cols.append(keep_col)
    df = df.reset_index()[cols].explode("tags")
    df["tag_type"] = df["tags"].str[0]

    if filter_tag:
        if isinstance(filter_tag, str):
            filter_tag = [filter_tag]

        df = df[df["tags"].str[0].isin(filter_tag)]
        for tag in filter_tag:
            mask = df["tag_type"] == tag
            df.loc[mask, tag] = df.loc[mask, "tags"].str[1]

    df = df.drop(columns=["tags", "tag_type"]).reset_index(drop=True)

    # save last p, e tags for reactions https://github.com/nostr-protocol/nips/blob/master/25.md#tags
    if keep_last:
        df = df.groupby(["id", "pubkey"], as_index=False).last()
    return df


def parse_reply_tags(df):
    df = df.explode("tags")
    df = df[df["tags"].str[0] == "e"]
    e_rows = df.apply(parse_reply_row, axis=1).dropna().tolist()

    # https://github.com/nostr-protocol/nips#standardized-tags
    # https://github.com/nostr-protocol/nips/blob/master/10.md#marked-e-tags-preferred
    df_reply = pd.DataFrame(
        e_rows,
        columns=["id", "pubkey", "ref_id", "created_at", "kind", "relay_url", "marker"],
    ).set_index("id")
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
            logger.error(f"expected 2-4 fields for e tags: {row}: {lst}")
    return None


def parse_mention_tags(df):
    df = df.explode("tags")
    df = df[df["tags"].str[0] == "p"]
    p_rows = df.apply(parse_mention_row, axis=1).dropna().tolist()

    # https://github.com/nostr-protocol/nips/blob/master/02.md#petname-scheme
    # https://github.com/nostr-protocol/nips/blob/master/10.md#the-p-tag
    df_mention = pd.DataFrame(
        p_rows,
        columns=[
            "id",
            "pubkey",
            "ref_pubkey",
            "created_at",
            "kind",
            "relay_url",
            "petname",
        ],
    ).set_index("id")
    return df_mention


def parse_mention_row(row):
    lst = row["tags"]
    if lst and lst[0] == "p":
        if len(lst) == 4:
            # ['p', '97c70a...', 'wss://relayable.org', 'hodlbod']
            # ['p', 'fa984b..', '', 'mention' ]
            # return [id, pubkey, ref_pubkey, created_at, kind, relay_url, petname]
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
            # return [id, pubkey, ref_pubkey, created_at, kind, relay_url, petname]
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
            # return [id, pubkey, ref_pubkey, created_at, kind, relay_url, petname]
            return [row.name, row.pubkey, lst[1], row.created_at, row.kind, None, None]
        elif len(lst) > 4:
            logger.error(f"> 4 fields for p tags: {row.name}: {lst}")
    return None


def parse_follows(df):
    df_follows = (
        parse_tags(df[df["kind"] == 3], filter_tag="p")
        .dropna(subset=["p"])
        .set_index(["pubkey", "p"])
    )
    return df_follows


def parse_reactions(df):
    df_reactions = parse_tags(
        df[df["kind"] == 7], filter_tag=["e", "p"], keep_col="content", keep_last=True
    )
    # event_id cannot be null
    df_reactions = df_reactions[df_reactions["e"].notna() & (df_reactions["e"] != "")]
    df_reactions = df_reactions.set_index("id")
    return df_reactions
