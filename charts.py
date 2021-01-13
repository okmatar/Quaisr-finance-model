import plotly.graph_objects as go
import pandas as pd


def read_csv(fname):
    position = pd.read_csv(fname, index_col=0, parse_dates=True)
    return position


def position():
    position_low = read_csv("scenarios/scenario_low/outputs/position.csv")
    position_medium = read_csv("scenarios/scenario_medium/outputs/position.csv")
    position_high = read_csv("scenarios/scenario_high/outputs/position.csv")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=position_medium.index,
            y=position_medium.cumulative,
            mode="lines",
            name="medium",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=position_low.index, y=position_low.cumulative, mode="lines", name="low"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=position_high.index, y=position_high.cumulative, mode="lines", name="high"
        )
    )

    fig.update_layout(
        title="Cumulative cash position",
        xaxis_title="",
        yaxis_title="Cumulative cash position (£)",
        template="plotly_dark",
    )

    fig.show()


position()
