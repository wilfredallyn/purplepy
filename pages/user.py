import dash
from dash import callback, dcc, html
from dash.dependencies import Input, Output, State
from db import get_sql_engine
import numpy as np
import pandas as pd
import plotly.express as px
from query import query_db
from sqlalchemy.orm import sessionmaker
from utils import kind_name_dict

dash.register_page(__name__, path_template="/user/<npub>")

engine = get_sql_engine()
Session = sessionmaker(bind=engine)


def layout(npub=None):
    layout = html.Div(
        [
            dcc.Store(id="store-data", data={"npub": npub}),
            dcc.Loading(
                id="loading",
                type="default",
                children=[
                    dcc.Graph(id="graph-output"),
                ],
            ),
        ]
    )
    return layout
    # return html.Div(f"The user requested: {npub}.")


@callback(
    Output("graph-output", "figure"),
    Input("store-data", "data"),
)
def update_graph(data):
    npub = data["npub"]
    df = query_db(
        Session=Session,
        npub=npub,
        kind=None,
    )

    if df.empty:
        return (px.scatter(template=None),)

    x_order = np.sort(df["kind"].unique())
    fig = px.histogram(
        x=df.kind.astype(str),
        title=f"Histogram of events by kind for {npub}",
        category_orders={"kind": x_order},
    )
    x_labels = [f"{x} ({kind_name_dict[x]})" for x in x_order if x in kind_name_dict]

    fig.update_xaxes(tickvals=x_order, ticktext=x_labels)
    return fig

    # fig: groupby day of week
    # fig = px.histogram(
    #     x=df.kind.astype(str),
    #     title=f"Histogram of events by kind for {npub}",
    #     category_orders={"kind": x_order},
    # )
    # return fig
