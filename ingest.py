import pandas as pd
from parse import (
    parse_follows,
    parse_mention_tags,
    parse_reactions,
    parse_reply_tags,
    parse_user_metadata,
)
from query import query_relay
from sqlalchemy import create_engine, inspect
from sqlalchemy.dialects.postgresql import JSONB
from sqla_models import User


def init_db(client):
    engine = create_engine("postgresql://postgres@localhost:5432/postgres")

    npub = "npub1dergggklka99wwrs92yz8wdjs952h2ux2ha2ed598ngwu9w7a6fsh9xzpc"
    df = query_relay(client, npub)

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


def write_tables(df, engine):
    df.to_sql(
        "event",
        engine,
        if_exists="append",
        dtype={
            "tags": JSONB,
        },
    )

    df_reply = parse_reply_tags(df)
    df_reply.to_sql("reply", engine, if_exists="append")
    df_reply.to_csv("neo4j-import/replys.csv")

    df_mention = parse_mention_tags(df)
    df_mention.to_sql("mention", engine, if_exists="append")
    df_mention.to_csv("neo4j-import/mentions.csv")

    df_reaction = parse_reactions(df)
    df_reaction.to_sql("reaction", engine, if_exists="append")
    df_reaction.to_csv("neo4j-import/reactions.csv")

    df_follow = parse_follows(df)
    df_follow.to_sql("follow", engine, if_exists="append")
    df_follow.to_csv("neo4j-import/follows.csv")

    df_user = parse_user_metadata(df)
    user_cols = [col.name for col in inspect(User).columns]
    user_cols = [col for col in user_cols if col != "pubkey"]
    df_user[user_cols].to_sql("user", engine, if_exists="replace")
    df_user.to_csv("neo4j-import/users.csv")
