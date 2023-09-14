from query import query_events
from sqlalchemy import create_engine


def temp():
    pass


def init_db(client):
    engine = create_engine("postgresql://postgres@localhost:5432/postgres")

    npub = "npub1dergggklka99wwrs92yz8wdjs952h2ux2ha2ed598ngwu9w7a6fsh9xzpc"
    df = query_events(client, npub)
    df[df.columns[:-1]].to_sql(
        "events", engine, if_exists="append", index=True, method="multi"
    )

    # from sqlalchemy.orm import sessionmaker
    # Session = sessionmaker(bind=engine)

    # session = Session()

    # for index, row in df.iterrows():
    #     session.add(Model(**row.to_dict()))
    #     if index % 1000 == 0:  # adjust the batch size as per your requirements
    #         session.commit()
    # session.commit()


# def run_ingestion():
#     npub =
