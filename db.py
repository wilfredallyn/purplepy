from neo4j import GraphDatabase
import os
from sqlalchemy import create_engine, exc, inspect, MetaData, select, Table
from sqlalchemy.dialects.postgresql import insert as pg_insert, JSONB
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import UniqueConstraint
from sqla_models import User
import pandas as pd
from parse import (
    parse_follows,
    parse_mention_tags,
    parse_reactions,
    parse_reply_tags,
    parse_user_metadata,
)
from utils import postprocess
import uuid


def get_sql_engine(sqlite_path="localdb.sqlite"):
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
        print(f"Using sqlite for local db (path = {sqlite_path})")
        return create_engine(f"sqlite:///{sqlite_path}")


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
    user_cols = [col for col in user_cols if col != "pubkey"]
    df_user[user_cols].to_sql("user", engine, if_exists="append")
    df_user.to_csv("neo4j-import/users.csv")


def upsert_df(df: pd.DataFrame, table_name: str, engine):
    pass


# TODO: debug upsert

# meta = MetaData(bind=engine)
# meta.reflect()
# table = Table(table_name, meta, autoload_with=engine)

# # Check if table exists
# if table_name not in meta.tables:
#     df.to_sql(table_name, engine)
#     return True

# # If it already exists...
# temp_table_name = f"temp_{uuid.uuid4().hex[:6]}"
# df.to_sql(temp_table_name, engine, index=True)

# temp_table = Table(temp_table_name, meta, autoload_with=engine)

# # Prepare the insert statement
# insert_stmt = pg_insert(table).from_select(
#     names=[c.name for c in temp_table.c], select=select([temp_table])
# )

# # Prepare the upsert (on conflict do update)
# pk_columns = [table.c[name] for name in df.index.names]
# do_update_stmt = insert_stmt.on_conflict_do_update(
#     index_elements=pk_columns,
#     set_={
#         c.name: insert_stmt.excluded[c.name] for c in table.c if c not in pk_columns
#     },
# )

# with engine.begin() as conn:
#     # Add unique constraint to pk columns if not exist
#     constraint_name = f"{table_name}_unique_constraint_for_upsert"
#     if not engine.dialect.has_table(engine, table_name):
#         conn.execute(
#             table.append_constraint(
#                 UniqueConstraint(*pk_columns, name=constraint_name)
#             )
#         )

#     conn.execute(do_update_stmt)
#     conn.execute(temp_table.drop())

# return True


sql_engine = get_sql_engine()
Session = sessionmaker(bind=sql_engine)
neo4j_driver = get_neo4j_driver()
