import numpy as np
import plotly.express as px
from utils import kind_name_dict


def plot_histogram(df, groupby_cols=None, title=""):
    df_grp = df.groupby(groupby_cols).size().reset_index(name="count")
    fig = px.histogram(
        x=df_grp,
        y="count",
        title=title,
    )
    return fig


def plot_histogram(df, groupby_cols=None, title=""):
    if groupby_cols is None:
        groupby_cols = []
    elif isinstance(groupby_cols, str):
        groupby_cols = [groupby_cols]

    df_grp = df.groupby(groupby_cols).size().reset_index(name="count")

    if len(groupby_cols) == 1:
        fig = px.histogram(df_grp, x=groupby_cols[0], y="count", title=title)
    elif len(groupby_cols) > 1:
        fig = px.histogram(
            df_grp, x=groupby_cols[0], y="count", color=groupby_cols[1], title=title
        )
    else:
        fig = px.histogram(df_grp, x="count", title=title)
    return fig
