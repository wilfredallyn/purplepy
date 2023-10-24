from analyze import get_events_by_time
import dash
from dash import callback, dcc, html
from dash.dependencies import Input, Output, State
from db import get_sql_engine
import numpy as np
import pandas as pd
from plot import plot_by_datetime, plot_histogram
import plotly.express as px
from query import query_db
from sqlalchemy.orm import sessionmaker


dash.register_page(__name__, path_template="/user/<npub>")

engine = get_sql_engine()
Session = sessionmaker(bind=engine)


def layout(npub=None):
    layout = html.Div(
        [
            dcc.Store(id="store-data", data={"npub": npub}),
            dcc.Dropdown(
                id="plot-type-dropdown",
                options=[
                    {"label": "Histogram", "value": "histogram"},
                    {"label": "Day of week", "value": "day_of_week"},
                    {"label": "Hour of day", "value": "hour_of_day"},
                ],
                value="histogram",  # default value
                clearable=False,
                style={"width": "50%", "maxWidth": "400px"},
            ),
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
    Input("plot-type-dropdown", "value"),
)
def update_graph(data, plot_type):
    npub = data["npub"]
    df = query_db(
        Session=Session,
        npub=npub,
        kind=None,
    )
    df = get_events_by_time(df)

    if df.empty:
        return (px.scatter(template=None),)

    if plot_type == "histogram":
        fig = plot_histogram(df, title=f"Histogram of events by kind for {npub}")
    elif plot_type == "day_of_week":
        fig = plot_by_datetime(
            df, groupby_type="day", title=f"Histogram of events by day for {npub}"
        )
    elif plot_type == "hour_of_day":
        fig = plot_by_datetime(
            df, groupby_type="hour", title=f"Histogram of events by hour for {npub}"
        )
    return fig
