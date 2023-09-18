import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
from sqlalchemy import create_engine, Column, BigInteger, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import JSONB

# Setup app and layout
app = dash.Dash(__name__)
app.layout = html.Div(
    [
        html.Label("Enter Pubkey:"),
        dcc.Input(id="pubkey-input", type="text", value=""),
        html.Button("Submit", id="submit-btn", n_clicks=0),
        dcc.Graph(id="histogram-graph"),
    ]
)

# Database connection
DATABASE_URL = (
    "postgresql://postgres@localhost:5432/postgres"  # Change this to your database URL
)
engine = create_engine(DATABASE_URL)

# ORM setup
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Events(Base):
    __tablename__ = "events"
    id = Column(String, primary_key=True)
    created_at = Column(BigInteger)
    kind = Column(BigInteger)
    tags = Column(JSONB)
    tags_relay_url = Column(JSONB)
    pubkey = Column(String)
    content = Column(String)
    sig = Column(String)


@app.callback(
    Output("histogram-graph", "figure"),
    [Input("submit-btn", "n_clicks")],
    [dash.dependencies.State("pubkey-input", "value")],
)
def update_histogram(n_clicks, pubkey_value):
    if not pubkey_value:
        return {
            "data": [],
            "layout": {
                "title": "Please enter a pubkey and click Submit.",
                "xaxis": {"title": "Kind"},
                "yaxis": {"title": "Count"},
            },
        }

    session = Session()
    events_with_pubkey = session.query(Events).filter_by(pubkey=pubkey_value).all()
    kinds = [str(event.kind) for event in events_with_pubkey if event.kind is not None]
    session.close()

    fig = px.histogram(
        x=kinds, title=f"Histogram of events by kind for pubkey {pubkey_value}"
    )
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
