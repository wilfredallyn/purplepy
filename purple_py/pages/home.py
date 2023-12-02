import dash
from dash import html


dash.register_page(__name__, path="/", name="Home")  # '/' is home page


def layout():
    layout = html.Div([])
    return layout
