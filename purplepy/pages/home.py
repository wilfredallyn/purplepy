import dash
from dash import html, dash_table
import dash_bootstrap_components as dbc
from purplepy.db import client
from purplepy.query import get_kind_counts
from purplepy.utils import kind_name_dict


dash.register_page(__name__, path="/", name="Home")  # '/' is home page


def layout():
    layout = html.Div(
        [
            dbc.Container(
                [
                    dbc.Row(
                        [
                            html.P(
                                "This database contains mostly events between 2023-11-14 and 2023-11-21"
                            ),
                            html.Br(),
                            html.P("It contains the following events:"),
                        ]
                    ),
                    dbc.Row(
                        dbc.Col(
                            [get_db_summary(client)],
                            width={
                                "size": 10,
                                "offset": 1,
                            },
                        )
                    ),
                ],
                fluid=True,
            )
        ]
    )
    return layout


def get_db_summary(client):
    df = (
        get_kind_counts(client)
        .sort_values("count", ascending=False)
        .rename(columns={"count": "num_events"})
        .rename(columns={"kind": "kind_num"})
    )
    df["kind_num"] = df["kind_num"].astype(int)
    df["kind_name"] = df["kind_num"].map(kind_name_dict)

    cols = ["kind_num", "kind_name", "num_events"]

    output_table = dash_table.DataTable(
        id="table",
        columns=[{"name": col, "id": col} for col in cols],
        data=df[cols].to_dict("records"),
        fill_width=False,
        style_cell={"textAlign": "center"},
        sort_action="native",
    )
    return output_table
