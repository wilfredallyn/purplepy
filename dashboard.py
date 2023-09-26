import dash
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output
import numpy as np
import plotly.express as px
import pandas as pd
from query import init_client, query_db, query_events
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils import format_table, kind_name_dict


# for querying network
client = init_client()

# for querying local db
engine = create_engine("postgresql://postgres@localhost:5432/postgres")
Session = sessionmaker(bind=engine)
# Base = declarative_base()


app = dash.Dash(__name__)

app.layout = html.Div(
    [
        dcc.Input(id="npub", type="text", placeholder="Enter npub value"),
        dcc.Input(id="kind", type="text", placeholder="Enter kind value (Optional)"),
        dcc.Input(
            id="num_days",
            type="number",
            placeholder="Enter num_days value (Default: 1)",
        ),
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
        dash.dependencies.State("npub", "value"),
        dash.dependencies.State("kind", "value"),
        dash.dependencies.State("num_days", "value"),
        dash.dependencies.State("toggle-btn", "value"),
    ],
)
def update_graph(n_clicks, npub, kind_value, num_days, toggle_value):
    num_days = int(num_days) if num_days else 1
    df = pd.DataFrame()
    if toggle_value == "network" and client:
        df = query_events(
            client=client,
            kind=kind_value,
            npub=npub,
            num_days=num_days,
            num_limit=None,
            timeout_secs=30,
        )
    elif toggle_value == "local":
        df = query_db(
            Session=Session,
            npub=npub,
            kind=kind_value,
        )

    if df.empty:
        return px.scatter(), "No data found for the given fields", None, None

    x_order = np.sort(df["kind"].unique())
    fig = px.histogram(
        x=df.kind.astype(str),
        title=f"Histogram of events by kind for {npub}",
        category_orders={"kind": x_order},
    )
    x_labels = [f"{x} ({kind_name_dict[x]})" for x in x_order]

    fig.update_xaxes(tickvals=x_order, ticktext=x_labels)

    table_data, table_columns = format_table(df)
    return fig, "Submit button clicked!", table_data, table_columns


if __name__ == "__main__":
    app.run_server(debug=True)


# stacked histogram of kind distribution (df has multiple npubs)
# df.kind = df.kind.astype(str)
# px.histogram(df, x="pubkey", color="kind")
