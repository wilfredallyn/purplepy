from dotenv import load_dotenv
from neo4j import GraphDatabase
import os
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker


load_dotenv()


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


engine = get_sql_engine()
Session = sessionmaker(bind=engine)

neo4j_driver = get_neo4j_driver()
