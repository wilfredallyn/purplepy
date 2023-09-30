from sqlalchemy import create_engine, exc


def get_sql_engine(sqlite_path="localdb.sqlite"):
    try:
        engine = create_engine("postgresql://postgres@localhost:5432/postgres")
        connection = engine.connect()
        connection.close()
        print("Using postgres for local db")
        return engine
    except exc.OperationalError:
        print(f"Using sqlite for local db (path = {sqlite_path})")
        return create_engine(f"sqlite:///{sqlite_path}")
