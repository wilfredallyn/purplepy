import numpy as np
import plotly.express as px
from utils import kind_name_dict


def plot_histogram(df, title=""):
    x_order = np.sort(df["kind"].unique())
    fig = px.histogram(
        x=df.kind.astype(str),
        title=title,
        category_orders={"kind": x_order},
    )
    x_labels = [f"{x} ({kind_name_dict[x]})" for x in x_order if x in kind_name_dict]

    fig.update_xaxes(tickvals=x_order, ticktext=x_labels)
    return fig


def plot_by_day_of_week(df, title=""):
    days_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    df_grouped = df.groupby("day_of_week").size().reset_index(name="count")
    fig = px.histogram(
        df_grouped,
        x="day_of_week",
        y="count",
        title=title,
        category_orders={"day_of_week": days_order},
    )
    return fig


def plot_by_datetime(df, groupby_type, title=""):
    if groupby_type == "day":
        df_grouped = df.groupby("day_of_week").size().reset_index(name="count")
        x = "day_of_week"
        category_orders = {
            "day_of_week": [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
        }
    elif groupby_type == "hour":
        df_grouped = df.groupby("hour_of_day").size().reset_index(name="count")
        x = "hour_of_day"
        category_orders = None
    else:
        raise ValueError("expected 'day' or 'hour' for 'groupby_type'")

    fig = px.histogram(
        df_grouped,
        x=x,
        y="count",
        title=title,
        category_orders=category_orders,
    )
    return fig
