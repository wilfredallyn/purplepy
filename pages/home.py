import dash
from dash import dcc, html, callback, Output, Input
from db import Session
import plotly.express as px
import dash_bootstrap_components as dbc
from sqlalchemy import func
from sqla_models import Event
from utils import parse_datetime_str


dash.register_page(__name__, path="/", name="Home")  # '/' is home page


def get_local_db_summary():
    with Session() as session:
        query = session.query(
            func.count(Event.id).label("total_events"),
            func.min(Event.created_at).label("start_date"),
            func.max(Event.created_at).label("end_date"),
        ).select_from(Event)

        result = query.one_or_none()
        num_events = result.total_events
        if result and num_events > 0:
            start_date = parse_datetime_str(result.start_date)
            end_date = parse_datetime_str(result.end_date)
            summary_text = f"There are {num_events} events between {start_date} and {end_date} in the local database"
        else:
            summary_text = "There are no events in the local database"
    return summary_text


def layout():
    summary_text = get_local_db_summary()
    layout = html.Div(
        [
            html.P(f"{summary_text}"),
        ]
    )
    return layout
