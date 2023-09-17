import pandas as pd
import json
from nostr_sdk import Keys, Client, EventBuilder, Filter, PublicKey
from datetime import timedelta
import time

from sqlalchemy import create_engine, Column, BigInteger, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Events(Base):
    __tablename__ = "events"
    id = Column(String, primary_key=True)
    created_at = Column(BigInteger)
    kind = Column(BigInteger)
    tags = Column(JSONB)
    tags_relay_url = Column(JSONB)
    pubkey = Column(String)
    sig = Column(String)
    content = Column(String)


def query_events(client, kind=None, num_limit=1000):
    if kind:
        filter = Filter().kind(kind).limit(num_limit)
    else:
        filter = Filter().limit(num_limit)
    events = client.get_events_of([filter], timedelta(seconds=50))
    df = pd.DataFrame([json.loads(event.as_json()) for event in events]).set_index("id")
    return df


def query_events_by_author(client, npub):
    pk = PublicKey.from_bech32(npub)
    filter = Filter().kind(1).author(pk.to_hex()).limit(10)
    events = client.get_events_of([filter], timedelta(seconds=10))
    df = pd.DataFrame([json.loads(event.as_json()) for event in events]).set_index("id")
    return df


def query_events_db(engine):
    # query nested jsonb: sql_query = "SELECT * FROM events WHERE tags->>'t' = 'sm41623576'";
    # return pd.read_sql(sql_query, engine)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        results = session.query(Events).all()

    # Convert the results into a pandas DataFrame
    df = pd.DataFrame([r.__dict__ for r in results])
    df = df.drop("_sa_instance_state", axis=1)
    return df
