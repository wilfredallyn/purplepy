import dash
from dash import callback, dcc, html, dash_table
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from nostr_sdk import PublicKey
import pandas as pd
from purple_py.db import client
from purple_py.query import search_weaviate


dash.register_page(__name__, path_template="/search", name="Search")


def layout():
    layout = html.Div(
        [
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dcc.Input(
                                        id="search-input",
                                        type="text",
                                        placeholder="Enter search term",
                                    ),
                                    html.Button(
                                        "Search", id="search-button", n_clicks=0
                                    ),
                                ]
                            ),
                            dbc.Col([html.Div(id="search-results")]),
                        ]
                    )
                ]
            )
        ]
    )
    return layout


@callback(
    Output("search-results", "children"),
    [Input("search-button", "n_clicks")],
    [State("search-input", "value")],
)
def update_output(n_clicks, value):
    if n_clicks > 0 and value:
        df = search_weaviate(client, value)
        if df is not None and not df.empty:
            return dash_table.DataTable(
                data=df.to_dict("records"),
                columns=[{"name": i, "id": i} for i in df.columns],
            )
        else:
            return "No results found"
    return "Enter a term and click search"
