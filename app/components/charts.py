from typing import Dict

import pandas as pd
import plotly.express as px
import streamlit as st

from language import SENTIMENT_LABEL_AR

SENTIMENT_COLOR_MAP = {
    "positive": "#059669",
    "negative": "#dc2626",
    "neutral": "#d97706",
}


def render_distribution_pie(distribution: Dict[str, float]) -> None:
    keys = list(distribution.keys())
    labels = [f"{SENTIMENT_LABEL_AR.get(key, key)}" for key in keys]
    df = pd.DataFrame({"sentiment": labels, "probability": list(distribution.values()), "key": keys})
    fig = px.pie(
        df,
        names="sentiment",
        values="probability",
        hole=0.5,
        color="key",
        color_discrete_map=SENTIMENT_COLOR_MAP,
    )
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, Tahoma, Arial", size=13),
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)
