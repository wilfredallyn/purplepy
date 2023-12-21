import dash
from dash import html
from purple_py.db import client
from purple_py.query import get_kind_counts


dash.register_page(__name__, path="/", name="Home")  # '/' is home page


def layout():
    layout = html.Div(
        [
            html.P(f"{get_db_summary(client)}"),
        ]
    )
    return layout


def get_db_summary(client):
    df = get_kind_counts(client)
    kind_string = ", ".join(
        [f"{row['kind']} ({row['count']} events)" for _, row in df.iterrows()]
    )
    output = f"This database contains mostly events between 2023-11-14 and 2023-11-21. It contains the following kinds: {kind_string}"
    return output
