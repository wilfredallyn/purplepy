from datetime import datetime, timedelta
import pandas as pd
import json
from nostr_sdk import Keys, Client, Filter, Options, PublicKey, Timestamp
from sqla_models import Event, Reply
from sqlalchemy import func
from utils import postprocess


def query_relay(
    client,
    npub=None,
    kind=None,
    num_days=None,
    num_limit=None,
    timeout_secs=30,
):
    filter = Filter()
    if kind:
        filter = filter.kind(kind)
    if npub:
        # fix: check if hex or bech32
        pk = PublicKey.from_bech32(npub)
        filter = filter.author(pk.to_hex())
    if num_days:
        filter = filter.since(get_filter_timestamp(num_days=num_days))
    if num_limit:
        filter = filter.limit(num_limit)
    events = client.get_events_of([filter], timedelta(seconds=timeout_secs))

    events_with_id = [
        json.loads(event.as_json())
        for event in events
        if "id" in json.loads(event.as_json())
    ]
    df = pd.DataFrame(events_with_id)
    if not df.empty:
        df = df.set_index("id")
    return df


def query_db(Session, npub=None, kind=None):
    # fix: check if hex or bech32
    with Session() as session:
        subquery = (
            session.query(Reply.ref_id, func.count(Reply.id).label("reply_count"))
            .group_by(Reply.ref_id)
            .subquery()
        )

        sqla_query = session.query(Event, subquery.c.reply_count).outerjoin(
            subquery, subquery.c.ref_id == Event.id
        )

        if npub:
            pk = PublicKey.from_bech32(npub).to_hex()
            sqla_query = sqla_query.filter(Event.pubkey == pk)
        if kind:
            sqla_query = sqla_query.filter(Event.kind == int(kind))
        results = sqla_query.all()

    data = []
    for event, reply_count in results:
        row = event.__dict__.copy()
        row["reply_count"] = reply_count
        data.append(row)
    df = pd.DataFrame(data)
    if "kind" in df.columns:
        df["kind"] = df["kind"].astype(str)
    if df.empty:
        return df
    else:
        return postprocess(df.set_index("id"), dedupe=True)


def get_filter_timestamp(num_days: int):
    ts = int((datetime.now() - timedelta(days=num_days)).timestamp())
    return Timestamp.from_secs(ts)


def get_table(Session, sqla_table):
    with Session() as session:
        sqla_query = session.query(sqla_table)
        results = sqla_query.all()
    df = pd.DataFrame([r.__dict__ for r in results])
    df = df.drop("_sa_instance_state", axis=1)

    primary_key_col = [key.name for key in sqla_table.__table__.primary_key][0]
    df = df.set_index(primary_key_col)
    return df
