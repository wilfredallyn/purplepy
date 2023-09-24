import dash
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output
from datetime import datetime, timedelta
from nostr_sdk import Keys, Client, Options
import plotly.express as px
import pandas as pd
from query import query_events_by_author
import json


keys = Keys.generate()
opts = Options().timeout(timedelta(seconds=1000))
client = Client.with_opts(keys, opts)
client.add_relay("wss://relay.damus.io")
client.add_relay("wss://nostr.oxtr.dev")
client.add_relay("wss://nostr.openchain.fr")
client.connect()


app = dash.Dash(__name__)

app.layout = html.Div(
    [
        dcc.Input(id="npub-input", type="text", placeholder="Enter npub value"),
        html.Button("Submit", id="submit-btn", n_clicks=0),
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


def format_table(df):
    df = df.applymap(
        lambda x: str(x) if not isinstance(x, (str, int, float, bool)) else x
    )
    df.created_at = df.created_at.apply(
        lambda x: datetime.fromtimestamp(x).strftime("%Y-%m-%d %I:%M%p")
    )
    cols = ["created_at", "kind", "content"]
    table_data = df[cols].to_dict("records")
    table_columns = [{"name": i, "id": i} for i in cols]
    # table_data = df.to_dict("records")
    # table_columns = [{"name": i, "id": i} for i in df.columns]
    return table_data, table_columns


@app.callback(
    [
        Output("graph-output", "figure"),
        Output("message-output", "children"),
        Output("table-output", "data"),  # Add this line
        Output("table-output", "columns"),  # Add this line
    ],
    [Input("submit-btn", "n_clicks")],
    [dash.dependencies.State("npub-input", "value")],
)
def update_graph(n_clicks, npub):
    if not npub:
        return px.scatter(), "Please enter a valid npub value.", None, None

    # Query client
    df = query_events_by_author(client, npub)
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
