import dash
from dash import html
from dotenv import load_dotenv
from neo4j import GraphDatabase
from nostr_sdk import PublicKey
import os
import pandas as pd


load_dotenv()


dash.register_page(__name__, path_template="/network", name="Network")


uri = os.getenv("NEO4J_URI")  # bolt://localhost:7687
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(uri, auth=(username, password))


def get_top_followed_pubkeys(tx):
    query = """
        MATCH (follower:User)-[:FOLLOWS]->(followed:User)
        RETURN followed.pubkey AS pubkey, COUNT(follower) AS followers_count
        ORDER BY followers_count DESC
        LIMIT 10
    """
    return tx.run(query).data()


def layout():
    with driver.session() as session:
        result = session.read_transaction(get_top_followed_pubkeys)

    df = pd.DataFrame(result)
    df["pubkey"] = df["pubkey"].apply(lambda x: PublicKey.from_hex(x).to_bech32())

    table_data = [html.Tr([html.Th(col) for col in df.columns])] + [
        html.Tr([html.Td(df.iloc[i][col]) for col in df.columns])
        for i in range(len(df))
    ]

    layout = html.Div([html.H3("Top 10 Most Followed Pubkeys"), html.Table(table_data)])

    return layout
