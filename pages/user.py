from analyze import get_events_by_time
import dash
from dash import callback, dcc, html
from dash.dependencies import Input, Output, State
from db import get_sql_engine
from plot import plot_histogram
import plotly.express as px
from query import query_db
from sqlalchemy.orm import sessionmaker


dash.register_page(__name__, path="/user", name="User")
# dash.register_page(__name__, path_template="/user/<npub>")


engine = get_sql_engine()
Session = sessionmaker(bind=engine)
will_npub = "npub1xtscya34g58tk0z605fvr788k263gsu6cy9x0mhnm87echrgufzsevkk5s"


def layout(npub=None):
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
        ]
    )
    return layout


@callback(
    Output("graph-output", "figure"),
    Input("plot-type-checklist", "value"),
    Input("submit-npub-button", "n_clicks"),
    State("input-npub", "value"),
)
def update_graph(groupby_cols, n_clicks, input_npub):
    # If the button hasn't been clicked, return a blank plot.
    if n_clicks == 0:
        return px.scatter(template=None)


@callback(
    Output("graph-output", "figure"),
    # Input("store-data", "data"),  # add to query with npub in querystring
    Input("plot-type-checklist", "value"),
    Input("submit-npub-button", "n_clicks"),
    State("input-npub", "value"),
)
def update_graph(
    groupby_cols, n_clicks, input_npub
):  # add data to query with npub in querystring
    # if not data["npub"] and n_clicks > 0:
    #     npub = input_npub
    # else:
    #     npub = data["npub"]
    if n_clicks == 0:
        return px.scatter(template=None)
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
    return fig
