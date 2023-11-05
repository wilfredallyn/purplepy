from analyze import get_events_by_time
import dash
from dash import callback, dcc, html, dash_table
from dash.dependencies import Input, Output, State
from db import get_sql_engine
from db import neo4j_driver, Session
import os
from plot import plot_histogram
import plotly.express as px
from query import query_db
from sqlalchemy.orm import sessionmaker
from utils import get_pubkey_hex, get_npub


dash.register_page(__name__, path="/user", name="User")
# dash.register_page(__name__, path_template="/user/<npub>")


def get_biggest_fans(tx, npub, num_fans=5):
    pubkey = get_pubkey_hex(npub)
    query = """
        MATCH (user:User)-[r:MENTIONS_VIA|REACTS_VIA]->(e:Event)-[:TARGETS]->(target:User {pubkey: $pubkey})
        WITH user,
             COUNT(CASE WHEN TYPE(r) = 'MENTIONS_VIA' THEN 1 END) AS mentions,
             COUNT(CASE WHEN TYPE(r) = 'REACTS_VIA' THEN 1 END) AS reactions,
             COUNT(DISTINCT e) AS total_count
        RETURN user.pubkey, total_count, mentions, reactions
        ORDER BY total_count DESC
        LIMIT $num_fans
    """
    return tx.run(query, pubkey=pubkey, num_fans=num_fans).data()


def layout(npub=None, num_fans=5):
    layout = html.Div(
        [
            dcc.Store(id="store-data", data={"npub": npub}),
            html.Div(
                [
                    html.Label("Enter npub:"),
                    dcc.Input(id="input-npub", type="text", value=npub if npub else ""),
                    html.Button("Submit", id="submit-npub-button", n_clicks=0),
                ],
                style={"padding": "20px"},
            ),
            dcc.Checklist(
                id="plot-type-checklist",
                options=[
                    {"label": "Kind", "value": "kind"},
                    {"label": "Day of week", "value": "day_of_week"},
                    {"label": "Hour of day", "value": "hour_of_day"},
                ],
                value=["kind"],
                inline=False,
                style={"width": "50%", "maxWidth": "400px"},
            ),
            dcc.Loading(
                id="loading",
                type="default",
                children=[
                    dcc.Graph(id="graph-output"),
                ],
            ),
            html.H3(f"Biggest Fans"),
            dash_table.DataTable(
                id="results-table",
                columns=[
                    {"name": i, "id": i} for i in ["npub", "mentions", "reactions"]
                ],
                data=[],
            ),
        ]
    )
    return layout


@callback(
    [Output("graph-output", "figure"), Output("results-table", "data")],
    # Input("store-data", "data"),  # add to query with npub in querystring
    Input("plot-type-checklist", "value"),
    Input("submit-npub-button", "n_clicks"),
    State("input-npub", "value"),
    prevent_initial_call=True,
)
def update_graph(
    groupby_cols, n_clicks, input_npub, num_fans=5
):  # add data to query with npub in querystring
    # if not data["npub"] and n_clicks > 0:
    #     npub = input_npub
    # else:
    #     npub = data["npub"]
    if n_clicks == 0:
        return px.scatter(template=None), [{}]
    npub = input_npub
    df = query_db(
        Session=Session,
        npub=npub,
        kind=None,
    )
    df = get_events_by_time(df)

    if df.empty:
        return (px.scatter(template=None),)

    fig = plot_histogram(
        df, groupby_cols=groupby_cols, title=f"Histogram of events for {npub}"
    )

    with neo4j_driver.session() as session:
        results = session.read_transaction(get_biggest_fans, npub, num_fans)

    table_data = [
        {
            "npub": get_npub(record["user.pubkey"]),
            "mentions": record["mentions"],
            "reactions": record["reactions"],
        }
        for record in results
    ]
    return fig, table_data
