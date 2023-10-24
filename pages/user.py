from analyze import get_events_by_time
import dash
from dash import callback, dcc, html
from dash.dependencies import Input, Output, State
from db import get_sql_engine
from plot import plot_histogram
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
        ]
    )
    return layout


@callback(
    Output("graph-output", "figure"),
    Input("store-data", "data"),
    Input("plot-type-checklist", "value"),
)
def update_graph(data, groupby_cols):
    npub = data["npub"]
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
    return fig
