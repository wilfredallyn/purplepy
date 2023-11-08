import numpy as np
import plotly.express as px


def plot_histogram(df, groupby_cols=None, title=""):
    if groupby_cols is None:
        groupby_cols = []
    elif isinstance(groupby_cols, str):
        groupby_cols = [groupby_cols]

    if len(groupby_cols) == 0:
        fig = px.histogram(df_grp, x="count", title=title)
    else:
        df_grp = df.groupby(groupby_cols).size().reset_index(name="count")
        if len(groupby_cols) == 1:
            fig = px.histogram(df_grp, x=groupby_cols[0], y="count", title=title)
        else:  # len(groupby_cols) > 1
            fig = px.histogram(
                df_grp, x=groupby_cols[0], y="count", color=groupby_cols[1], title=title
            )
    return fig
