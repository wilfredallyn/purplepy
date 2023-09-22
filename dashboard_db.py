import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from datetime import timedelta
from nostr_sdk import Keys, Client, EventBuilder, Filter, Options, PublicKey
import plotly.express as px
import pandas as pd
from query import query_events_by_author
import json
from sqla_models import Events
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# keys = Keys.generate()
# opts = Options().timeout(timedelta(seconds=1000))
# client = Client.with_opts(keys, opts)
# client.add_relay("wss://relay.damus.io")
# client.add_relay("wss://nostr.oxtr.dev")
# client.add_relay("wss://nostr.openchain.fr")
# client.connect()

DATABASE_URL = "postgresql://postgres@localhost:5432/postgres"
engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)
Base = declarative_base()


app = dash.Dash(__name__)

app.layout = html.Div(
    [
        dcc.Input(id="npub-input", type="text", placeholder="Enter npub value"),
        html.Button("Submit", id="submit-btn", n_clicks=0),
        dcc.Loading(
            id="loading",
            type="default",  # or "circle" or "cube" or "dot" based on your preference
            children=[dcc.Graph(id="graph-output"), html.Div(id="message-output")],
        ),
    ]
)


@app.callback(
    [
        Output("graph-output", "figure"),
        Output("message-output", "children"),
    ],  # Add another output for the message
    [Input("submit-btn", "n_clicks")],
    [dash.dependencies.State("npub-input", "value")],
)
def update_graph(n_clicks, npub):
    if not npub:
        return px.scatter(), "Please enter a valid npub value."

    # Query local db
    # session = Session()

    # events_with_pubkey = (
    #     session.query(Events).filter_by(pubkey=npub)
    #     # .filter_by(pubkey=PublicKey.from_bech32(npub).to_hex())
    #     .all()
    #     # .group_by().count()
    # )
    # print(events_with_pubkey)
    # kinds = [str(event.kind) for event in events_with_pubkey if event.kind is not None]
    # session.close()

    # fig = px.histogram(x=kinds, title=f"Histogram of events by kind for pubkey {npub}")

    # Query client
    # df = query_events_by_author(client, npub)
    # if df.empty:
    #     return px.scatter(), "No data found for the provided npub."

    # fig = px.histogram(
    #     x=df.kind.astype(str), title=f"Histogram of events by kind for {npub}"
    # )

    return fig, "Submit button clicked!"


if __name__ == "__main__":
    app.run_server(debug=True)


# stacked histgram of kind distribution
# dft.kind = dft.kind.astype(str)
# px.histogram(dft, x="pubkey", color="kind")
