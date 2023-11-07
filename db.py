from neo4j import GraphDatabase
import os
import pandas as pd
from parse import (
    parse_follows,
    parse_mention_tags,
    parse_reactions,
    parse_reply_tags,
    parse_user_metadata,
)
from sqlalchemy import create_engine, exc, inspect, MetaData, select, Table
from sqlalchemy.dialects.postgresql import insert as pg_insert, JSONB
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import UniqueConstraint
from sqla_models import User
import subprocess
from utils import postprocess
import uuid


def get_sql_engine():
    try:
        postgres_uri = os.getenv(
            "POSTGRES_URI"
        )  # postgresql://postgres@localhost:5432/postgres
        engine = create_engine(postgres_uri)
        connection = engine.connect()
        connection.close()
        print("Using postgres for local db")
        return engine
    except exc.OperationalError:
        raise ConnectionError(f"Cannot connect to PostgreSQL database")


def get_neo4j_driver():
    neo4j_uri = os.getenv("NEO4J_URI")  # bolt://localhost:7687
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    try:
        neo4j_driver = GraphDatabase.driver(neo4j_uri, auth=(username, password))
    except exc.OperationalError:
        print(f"Error connecting to neo4j")
    return neo4j_driver


def write_tables(df, engine):
    df.to_sql(
        "event",
        engine,
        if_exists="append",
        dtype={
            "tags": JSONB,
        },
    )
    df = postprocess(df)

    df_reply = parse_reply_tags(df.copy())
    df_reply.to_sql("reply", engine, if_exists="append")
    df_reply.to_csv("neo4j-import/replys.csv")

    df_mention = parse_mention_tags(df.copy())
    df_mention.to_sql("mention", engine, if_exists="append")
    df_mention.to_csv("neo4j-import/mentions.csv")

    df_reaction = parse_reactions(df.copy())
    df_reaction.to_sql("reaction", engine, if_exists="append")
    df_reaction.to_csv("neo4j-import/reactions.csv")

    df_follow = parse_follows(df.copy())
    df_follow.to_sql("follow", engine, if_exists="append")
    df_follow.to_csv("neo4j-import/follows.csv")

    df_user = parse_user_metadata(df.copy())
    user_cols = [col.name for col in inspect(User).columns]
    user_cols = [col for col in user_cols if col in df_user.columns]
    df_user[user_cols].to_sql("user", engine, if_exists="append")
    df_user.to_csv("neo4j-import/users.csv")

    # add replys after add ref_pubkey
    # for kind_name in ["follows", "mentions", "reactions", "replys", "users"]:
    for kind_name in ["follows", "mentions", "reactions", "users"]:
        load_neo4j_data(kind_name)


def load_neo4j_data(kind_name: str):
    expected_kinds = ["follows", "mentions", "reactions", "replys", "users"]
    if kind_name not in expected_kinds:
        raise ValueError(f"kind_name must be in {expected_kinds}")
    command = f"echo ':source import_{kind_name}.cql' | cypher-shell -u neo4j -p neo4j"
    result = subprocess.run(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    if result.returncode != 0:
        print("Error executing command:", result.stderr)


# TODO: add upsert
# def upsert_df(df: pd.DataFrame, table_name: str, engine):
# pass


sql_engine = get_sql_engine()
Session = sessionmaker(bind=sql_engine)
neo4j_driver = get_neo4j_driver()
