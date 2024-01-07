import dash
from dash import callback, dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
from purplepy.db import (
    client,
    neo4j_driver,
)
from purplepy.plot import plot_event_histogram
from purplepy.query import query_weaviate, get_similar_users
from purplepy.utils import get_pubkey_hex, get_npub, get_events_by_time, parse_datetime


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
            html.H3(f"Similar Users"),
            dash_table.DataTable(
                id="similar-table",
                columns=[
                    {
                        "name": "npub",
                        "id": "npub",
                        "type": "text",
                        "presentation": "markdown",
                    },
                ],
                data=[],
                style_cell={"textAlign": "left"},
                markdown_options={"link_target": "_blank"},
            ),
            html.Br(),
            html.H3(f"Biggest Fans"),
            dash_table.DataTable(
                id="fans-table",
                columns=[
                    {
                        "name": "npub",
                        "id": "npub",
                        "type": "text",
                        "presentation": "markdown",
                    },
                    {
                        "name": "mentions",
                        "id": "mentions",
                    },
                    {"name": "reactions", "id": "reactions"},
                ],
                data=[],
                style_cell={"textAlign": "left"},
                markdown_options={"link_target": "_blank"},
            ),
        ]
    )
    return layout


@callback(
    [
        Output("graph-output", "figure"),
        Output("similar-table", "data"),
        Output("fans-table", "data"),
    ],
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

    # plot histogram
    if n_clicks == 0:
        return px.scatter(template=None), [{}]
    npub = input_npub
    df = query_weaviate(
        client=client,
        npub=npub,
        kind=None,
    )
    df = get_events_by_time(df)

    if df.empty:
        return (px.scatter(template=None),)

    fig = plot_event_histogram(
        df, groupby_cols=groupby_cols, title=f"Histogram of events for {npub}"
    )

    # find similar users
    similar_data = [{"npub": "npub123"}]
    df_similar = get_similar_users(client, get_pubkey_hex(npub), limit=num_fans)
    similar_data = [
        {
            "npub": f"[{npub}](https://njump.me/{npub})",
        }
        for npub in df_similar["npub"]
    ]

    # find biggest fans
    with neo4j_driver.session() as session:
        fans_results = session.execute_read(get_biggest_fans, npub, num_fans)

    fans_data = [
        {
            "npub": f"[{get_npub(record['user.pubkey'])}](https://njump.me/{get_npub(record['user.pubkey'])})",
            "mentions": record["mentions"],
            "reactions": record["reactions"],
        }
        for record in fans_results
    ]
    return fig, similar_data, fans_data
