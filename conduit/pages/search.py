import dash
from dash import callback, dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from nostr_sdk import PublicKey
import pandas as pd
from conduit.db import client
from conduit.query import search_weaviate
from conduit.utils import format_data_table

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
                        ]
                    ),
                    dbc.Row(
                        [
                            dbc.Col([html.Div(id="search-results")]),
                        ]
                    ),
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
    output_cols = ["content", "pubkey", "created_at", "kind"]
    if n_clicks > 0 and value:
        df = search_weaviate(client, value)
        if df is not None and not df.empty:
            df = df[output_cols]
            return format_data_table(df)
        else:
            return "No results found"
    return "Enter a term and click search"
