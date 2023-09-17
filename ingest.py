from query import query_events
from sqlalchemy import create_engine


def init_db(client):
    engine = create_engine("postgresql://postgres@localhost:5432/postgres")

    npub = "npub1dergggklka99wwrs92yz8wdjs952h2ux2ha2ed598ngwu9w7a6fsh9xzpc"
    df = query_events(client, npub)
    df["tags_relay_url"] = df["tags"].apply(
        lambda x: {item[0]: item[2] for item in x if len(item) > 2}
    )
    df["tags"] = df["tags"].apply(lambda x: {item[0]: item[1] for item in x})

    engine = create_engine("postgresql://postgres@localhost:5432/postgres")
    df.to_sql(
        "events",
        engine,
        if_exists="replace",  # append
        method="multi",
        dtype={
            "tags": dialects.postgresql.JSONB,
            "tags_relay_url": dialects.postgresql.JSONB,
        },
    )
