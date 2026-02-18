"""Plotly chart builders for Walker Brain Portal."""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.constants import QUALITY_BANDS, CASE_TYPE_COLORS
from utils.theme import PLOTLY_TEMPLATE, COLORS


def _apply_template(fig: go.Figure, **overrides) -> go.Figure:
    """Apply the shared Plotly template with optional per-chart overrides."""
    layout = {**PLOTLY_TEMPLATE, **overrides}
    fig.update_layout(**layout)
    return fig


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
        marker_color=COLORS["primary"],
        opacity=0.75,
    ))

    return _apply_template(
        fig,
        xaxis_title="Quality Score",
        yaxis_title="Count",
        height=300,
        showlegend=False,
    )


def case_type_pie(df: pd.DataFrame, column: str = "case_type") -> go.Figure:
    """Donut chart of case type distribution."""
    counts = df[column].value_counts().reset_index()
    counts.columns = ["case_type", "count"]

    colors = [CASE_TYPE_COLORS.get(ct, "#bcbd22") for ct in counts["case_type"]]

    fig = go.Figure(go.Pie(
        labels=counts["case_type"],
        values=counts["count"],
        marker_colors=colors,
        hole=0.45,
        textposition="inside",
        textinfo="label+percent",
        textfont_size=11,
    ))
    return _apply_template(
        fig,
        height=300,
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
    )


def volume_trend(df: pd.DataFrame) -> go.Figure:
    """Daily volume trend line chart. Expects columns: date, count."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["count"],
        mode="lines+markers",
        line=dict(color=COLORS["primary"], width=2.5),
        marker=dict(size=7, color=COLORS["primary"]),
        fill="tozeroy",
        fillcolor=f"{COLORS['primary']}0a",
        name="Calls",
    ))
    return _apply_template(
        fig,
        xaxis_title="Date",
        yaxis_title="Calls Processed",
        height=250,
    )


def objection_bar(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart of objection category frequencies.

    Expects columns: obj_category, frequency.
    """
    df_sorted = df.sort_values("frequency", ascending=True).copy()
    df_sorted["obj_category"] = df_sorted["obj_category"].apply(
        lambda x: x.replace("_", " ").title() if isinstance(x, str) else x
    )
    total = df_sorted["frequency"].sum()
    if total > 0:
        df_sorted["pct"] = (df_sorted["frequency"] / total * 100).round(1)
        df_sorted["label"] = df_sorted.apply(
            lambda r: f"{r['frequency']} ({r['pct']}%)", axis=1
        )
    else:
        df_sorted["label"] = df_sorted["frequency"].astype(str)
    fig = go.Figure(go.Bar(
        x=df_sorted["frequency"],
        y=df_sorted["obj_category"],
        orientation="h",
        marker_color=COLORS["warning"],
        text=df_sorted["label"],
        textposition="outside",
    ))
    return _apply_template(
        fig,
        xaxis_title="Count",
        height=max(200, len(df_sorted) * 35),
        margin=dict(l=150, r=60, t=20, b=40),
    )


def cost_trend(df: pd.DataFrame) -> go.Figure:
    """Daily cost trend chart. Expects columns: date, total_cost."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["total_cost"],
        mode="lines+markers",
        line=dict(color=COLORS["success"], width=2.5),
        marker=dict(size=6, color=COLORS["success"]),
        fill="tozeroy",
        fillcolor=f"{COLORS['success']}10",
        name="Daily Cost",
    ))
    return _apply_template(
        fig,
        xaxis_title="Date",
        yaxis_title="Cost ($)",
        height=250,
    )


def quality_violin(df: pd.DataFrame, column: str = "quality_score") -> go.Figure:
    """Violin plot of quality score distribution."""
    fig = go.Figure(go.Violin(
        y=df[column].dropna(),
        box_visible=True,
        meanline_visible=True,
        fillcolor="#e3f2fd",
        line_color=COLORS["primary"],
        opacity=0.8,
    ))
    return _apply_template(
        fig,
        yaxis_title="Quality Score",
        height=300,
        margin=dict(l=40, r=20, t=20, b=20),
    )


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
        line=dict(dash="dash", color=COLORS["neutral"][400]),
        showlegend=False,
    ))

    fig.add_trace(go.Scatter(
        x=df[x_col],
        y=df[y_col],
        mode="markers",
        marker=dict(size=9, color=COLORS["primary"], opacity=0.8),
        name="Calls",
    ))

    return _apply_template(
        fig,
        xaxis_title="Grok Production Score",
        yaxis_title="Consensus Score",
        height=350,
    )
