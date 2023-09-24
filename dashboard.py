import dash
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from query import init_client, query_db, query_events_by_author
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils import format_table


# for querying network
client = init_client()

# for querying local db
engine = create_engine("postgresql://postgres@localhost:5432/postgres")
Session = sessionmaker(bind=engine)
# Base = declarative_base()


app = dash.Dash(__name__)

app.layout = html.Div(
    [
        dcc.Input(id="npub-input", type="text", placeholder="Enter npub value"),
        html.Button("Submit", id="submit-btn", n_clicks=0),
        dcc.RadioItems(
            id="toggle-btn",
            options=[
                {"label": "Query Network", "value": "network"},
                {"label": "Local DB", "value": "local"},
            ],
            value="network",
            labelStyle={"display": "inline-block"},
        ),
        dcc.Loading(
            id="loading",
            type="default",
            children=[
                dcc.Graph(id="graph-output"),
                html.Div(id="message-output"),
                dash_table.DataTable(id="table-output"),
            ],
        ),
    ]
)


@app.callback(
    [
        Output("graph-output", "figure"),
        Output("message-output", "children"),
        Output("table-output", "data"),
        Output("table-output", "columns"),
    ],
    [
        Input("submit-btn", "n_clicks"),
    ],
    [
        dash.dependencies.State("npub-input", "value"),
        dash.dependencies.State("toggle-btn", "value"),
    ],
)
def update_graph(n_clicks, npub, toggle_value):
    if not npub:
        return px.scatter(), "Please enter a valid npub value.", None, None

    if toggle_value == "network":
        df = query_events_by_author(client, npub)
    elif toggle_value == "local":
        df = query_db(Session, npub)

    if df.empty:
        return px.scatter(), "No data found for the provided npub.", None, None

    fig = px.histogram(
        x=df.kind.astype(str), title=f"Histogram of events by kind for {npub}"
    )

    table_data, table_columns = format_table(df)
    return fig, "Submit button clicked!", table_data, table_columns


if __name__ == "__main__":
    app.run_server(debug=True)


# stacked histogram of kind distribution (df has multiple npubs)
# df.kind = df.kind.astype(str)
# px.histogram(df, x="pubkey", color="kind")
