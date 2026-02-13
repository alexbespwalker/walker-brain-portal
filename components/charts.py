"""Plotly chart builders for Walker Brain Portal."""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.constants import QUALITY_BANDS, CASE_TYPE_COLORS


def quality_histogram(df: pd.DataFrame, column: str = "quality_score") -> go.Figure:
    """Quality score histogram with band overlays."""
    fig = go.Figure()

    # Band overlays
    for band_name, (low, high, color) in QUALITY_BANDS.items():
        fig.add_vrect(
            x0=low, x1=high,
            fillcolor=color, opacity=0.08,
            layer="below", line_width=0,
            annotation_text=band_name,
            annotation_position="top",
            annotation_font_size=9,
            annotation_font_color=color,
        )

    fig.add_trace(go.Histogram(
        x=df[column].dropna(),
        nbinsx=20,
        marker_color="#1565c0",
        opacity=0.7,
    ))

    fig.update_layout(
        xaxis_title="Quality Score",
        yaxis_title="Count",
        margin=dict(l=40, r=20, t=30, b=40),
        height=300,
        showlegend=False,
    )
    return fig


def case_type_pie(df: pd.DataFrame, column: str = "case_type") -> go.Figure:
    """Pie chart of case type distribution."""
    counts = df[column].value_counts().reset_index()
    counts.columns = ["case_type", "count"]

    colors = [CASE_TYPE_COLORS.get(ct, "#bcbd22") for ct in counts["case_type"]]

    fig = go.Figure(go.Pie(
        labels=counts["case_type"],
        values=counts["count"],
        marker_colors=colors,
        hole=0.4,
        textposition="inside",
        textinfo="label+percent",
    ))
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        height=300,
        showlegend=False,
    )
    return fig


def volume_trend(df: pd.DataFrame) -> go.Figure:
    """Daily volume trend line chart. Expects columns: date, count."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["count"],
        mode="lines+markers",
        line=dict(color="#1565c0", width=2),
        marker=dict(size=6),
        name="Calls",
    ))
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Calls Processed",
        margin=dict(l=40, r=20, t=20, b=40),
        height=250,
    )
    return fig


def objection_bar(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart of objection category frequencies.

    Expects columns: obj_category, frequency.
    """
    df_sorted = df.sort_values("frequency", ascending=True)
    fig = go.Figure(go.Bar(
        x=df_sorted["frequency"],
        y=df_sorted["obj_category"],
        orientation="h",
        marker_color="#f57c00",
    ))
    fig.update_layout(
        xaxis_title="Count",
        margin=dict(l=150, r=20, t=20, b=40),
        height=max(200, len(df_sorted) * 35),
    )
    return fig


def cost_trend(df: pd.DataFrame) -> go.Figure:
    """Daily cost trend chart. Expects columns: date, total_cost."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["total_cost"],
        mode="lines+markers",
        line=dict(color="#388e3c", width=2),
        fill="tozeroy",
        fillcolor="rgba(56,142,60,0.1)",
        name="Daily Cost",
    ))
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Cost ($)",
        margin=dict(l=40, r=20, t=20, b=40),
        height=250,
    )
    return fig


def quality_violin(df: pd.DataFrame, column: str = "quality_score") -> go.Figure:
    """Violin plot of quality score distribution."""
    fig = go.Figure(go.Violin(
        y=df[column].dropna(),
        box_visible=True,
        meanline_visible=True,
        fillcolor="#e3f2fd",
        line_color="#1565c0",
        opacity=0.7,
    ))
    fig.update_layout(
        yaxis_title="Quality Score",
        margin=dict(l=40, r=20, t=20, b=20),
        height=300,
    )
    return fig


def scatter_calibration(
    df: pd.DataFrame,
    x_col: str = "production_score",
    y_col: str = "consensus_score",
) -> go.Figure:
    """Scatter plot for Grok vs consensus calibration."""
    fig = go.Figure()

    # Identity line
    fig.add_trace(go.Scatter(
        x=[0, 100], y=[0, 100],
        mode="lines",
        line=dict(dash="dash", color="#999"),
        showlegend=False,
    ))

    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col],
        mode="markers",
        marker=dict(size=8, color="#1565c0"),
        name="Calls",
    ))

    fig.update_layout(
        xaxis_title="Grok Production Score",
        yaxis_title="Consensus Score",
        margin=dict(l=40, r=20, t=20, b=40),
        height=350,
    )
    return fig
