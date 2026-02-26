"""Today's Highlights — Marketing-focused dashboard with curated picks."""

import json
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from utils.auth import check_password
from utils.theme import inject_theme, styled_divider, styled_header, empty_state, COLORS, BORDERS, TYPOGRAPHY, SHADOWS, SPACING
from components.cards import metric_card, quote_card
from components.charts import quality_histogram, volume_trend, case_type_pie, trending_bar_chart
from utils.constants import humanize, quality_band
from utils.queries import (
    get_weekly_metric_counts, get_prior_period_metrics, fetch_quotes, get_daily_volume,
    get_last_updated, get_nsm_weekly_count, get_nsm_weekly_history,
)
from utils.database import query_table, get_supabase

if not check_password():
    st.stop()

inject_theme()

st.title(":bar_chart: Today's Highlights")
_last_updated = get_last_updated()
if _last_updated:
    st.caption(f"Curated content picks for the creative team. · Data last updated: {_last_updated}")
else:
    st.caption("Curated content picks for the creative team.")

client = get_supabase()

# --- North Star Metric (top billboard) ---
nsm = get_nsm_weekly_count()
nsm_left, nsm_right = st.columns([2, 1])
with nsm_left:
    if nsm["this_week"] == 0 and nsm["last_week"] == 0:
        # Zero state: muted billboard, no gold glow, instructional text
        st.markdown(
            f'<div class="wb-nsm-billboard-zero">'
            f'<div style="font-size:{TYPOGRAPHY["size"]["xs"]}; color:{COLORS["text_hint"]}; '
            f'text-transform:uppercase; letter-spacing:0.08em; font-weight:600; '
            f'margin-bottom:{SPACING["sm"]}; font-family:{TYPOGRAPHY["font_family"]};">North Star Metric</div>'
            f'<div style="font-family:{TYPOGRAPHY["font_family_display"]}; font-size:clamp(1.5rem, 3vw, 2.5rem); '
            f'font-weight:700; color:{COLORS["text_hint"]}; line-height:1.1;">\u2014</div>'
            f'<div style="font-size:{TYPOGRAPHY["size"]["base"]}; color:{COLORS["text_secondary"]}; '
            f'margin-top:6px; font-family:{TYPOGRAPHY["font_family"]}; line-height:{TYPOGRAPHY["line_height"]["normal"]};">'
            f'Awaiting first WF 20 run. Angles will appear here once the surfacing pipeline executes.</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        _nsm_value = str(nsm["this_week"])
        if nsm["delta"] != 0:
            _arrow = "\u25b2" if nsm["delta"] > 0 else "\u25bc"
            _d_color = COLORS["success"] if nsm["delta"] > 0 else COLORS["error"]
            _sign = "+" if nsm["delta"] > 0 else ""
            _nsm_delta_html = (
                f'<div style="font-size:{TYPOGRAPHY["size"]["sm"]}; color:{_d_color}; '
                f'margin-top:6px; font-family:{TYPOGRAPHY["font_family"]}; font-weight:500;">'
                f'{_arrow} {_sign}{nsm["delta"]} vs prior week</div>'
            )
        else:
            _nsm_delta_html = (
                f'<div style="font-size:{TYPOGRAPHY["size"]["sm"]}; color:{COLORS["text_hint"]}; '
                f'margin-top:6px; font-family:{TYPOGRAPHY["font_family"]};">\u2014 No change</div>'
            )
        st.markdown(
            f'<div class="wb-nsm-billboard">'
            f'<div style="font-size:{TYPOGRAPHY["size"]["xs"]}; color:{COLORS["primary_light"]}; '
            f'text-transform:uppercase; letter-spacing:0.08em; font-weight:600; '
            f'margin-bottom:{SPACING["sm"]}; font-family:{TYPOGRAPHY["font_family"]};">North Star Metric</div>'
            f'<div style="font-family:{TYPOGRAPHY["font_family_display"]}; font-size:clamp(2rem, 4vw, 3.5rem); '
            f'font-weight:700; color:{COLORS["text_primary"]}; line-height:1.1;">{_nsm_value}</div>'
            f'<div style="font-size:{TYPOGRAPHY["size"]["base"]}; color:{COLORS["text_secondary"]}; '
            f'margin-top:{SPACING["xs"]}; font-family:{TYPOGRAPHY["font_family"]};">unique angles surfaced this week</div>'
            f'{_nsm_delta_html}'
            f'</div>',
            unsafe_allow_html=True,
        )
with nsm_right:
    # NSM sparkline (6-week history)
    _sparkline_data = get_nsm_weekly_history(weeks=6)
    _has_data = any(d["count"] > 0 for d in _sparkline_data)
    if _has_data:
        import plotly.graph_objects as go
        _fig = go.Figure()
        _fig.add_trace(go.Scatter(
            x=[d["week_start"] for d in _sparkline_data],
            y=[d["count"] for d in _sparkline_data],
            mode="lines",
            line=dict(color=COLORS["primary"], width=2),
            fill="tozeroy",
            fillcolor=COLORS["tint_primary_strong"],
            hovertemplate="%{x}: %{y} angles<extra></extra>",
        ))
        _fig.update_layout(
            height=80,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            showlegend=False,
        )
        st.plotly_chart(_fig, use_container_width=True, config={"displayModeBar": False})

    # Target badge
    st.markdown(
        '<div class="wb-target-badge">TARGET: WoW Growth</div>',
        unsafe_allow_html=True,
    )

styled_divider()

# --- Section 1: Metric cards ---
with st.spinner("Loading metrics..."):
    metrics = get_weekly_metric_counts(days=7)
    prior = get_prior_period_metrics(days=7)

col1, col2, col3, col4 = st.columns(4)
with col1:
    metric_card("New Quotes (7d)", metrics["quotes"],
                delta=metrics["quotes"] - prior["quotes"], color=COLORS["primary"])
with col2:
    metric_card("Testimonials (7d)", metrics["testimonials"],
                delta=metrics["testimonials"] - prior["testimonials"], color=COLORS["success"])
with col3:
    metric_card("Content-Worthy (7d)", metrics["content_worthy"],
                delta=metrics["content_worthy"] - prior["content_worthy"], color=COLORS["info"])
with col4:
    median = metrics["median_quality"]
    band_name, band_color = quality_band(median)
    band_short = band_name[:5] + "." if len(band_name) > 8 else band_name
    metric_card("Quality (7d)", f"{median} — {band_short}",
                delta=median - prior["median_quality"], color=band_color)

# --- Section 2 & 3: Top quotes + Trending ---
left, right = st.columns([3, 2])

with left:
    styled_header("Top Quotes This Week")
    week_cutoff = (datetime.utcnow() - timedelta(days=7)).isoformat()
    top_quotes = fetch_quotes(min_quality=0, max_quality=100, limit=5, start_date=week_cutoff)
    if top_quotes:
        for row in top_quotes:
            quote_card(row, show_copy=False)
    else:
        st.caption("No quote data available yet.")

with right:
    styled_header("Trending This Week")

    cutoff_7d = (datetime.utcnow() - timedelta(days=7)).isoformat()

    # Top objection categories — bar chart
    try:
        rows = (
            client.table("analysis_results")
            .select("objection_categories")
            .not_.is_("objection_categories", "null")
            .gte("analyzed_at", cutoff_7d)
            .execute()
            .data
        )
        obj_counts: dict[str, int] = {}
        for r in rows:
            cats = r.get("objection_categories") or []
            if isinstance(cats, str):
                try:
                    cats = json.loads(cats)
                except (json.JSONDecodeError, TypeError):
                    cats = []
            if isinstance(cats, list):
                for c in cats:
                    if isinstance(c, str) and c.strip() and c.lower() not in ("undefined", "none", "null", "n/a"):
                        obj_counts[c] = obj_counts.get(c, 0) + 1
        if obj_counts:
            sorted_obj = sorted(obj_counts.items(), key=lambda x: -x[1])[:8]
            fig = trending_bar_chart(
                [humanize(k) for k, _ in sorted_obj],
                [v for _, v in sorted_obj],
                title="Top Objections",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No objection data this week.")
    except Exception:
        st.caption("Objection data unavailable.")

    # Trending case types — bar chart (click to drill into Call Search)
    try:
        rows_7d = (
            client.table("analysis_results")
            .select("case_type")
            .not_.is_("case_type", "null")
            .gte("analyzed_at", cutoff_7d)
            .execute()
            .data
        )
        ct_counts: dict[str, int] = {}
        for r in rows_7d:
            ct = r.get("case_type", "")
            if ct:
                ct_counts[ct] = ct_counts.get(ct, 0) + 1
        if ct_counts:
            sorted_ct = sorted(ct_counts.items(), key=lambda x: -x[1])[:6]
            ct_raw = [k for k, _ in sorted_ct]
            ct_display = [humanize(k) for k in ct_raw]
            ct_values = [v for _, v in sorted_ct]
            fig = trending_bar_chart(ct_display, ct_values, title="Case Types ↗ click to filter", customdata=ct_raw)
            try:
                ct_event = st.plotly_chart(
                    fig, use_container_width=True,
                    on_select="rerun", key="hl_case_types_chart",
                )
                if ct_event and ct_event.selection and ct_event.selection.points:
                    pt = ct_event.selection.points[0]
                    raw_ct = (pt.get("customdata") or [None])[0]
                    if not raw_ct:
                        raw_ct = pt.get("y")
                    if raw_ct:
                        st.session_state["cs_case"] = [raw_ct]
                        st.switch_page("app_pages/2_Call_Search.py")
            except Exception:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No case type data this week.")
    except Exception:
        st.caption("Case type data unavailable.")

    # Testimonial types — bar chart
    try:
        testimonials = (
            client.table("analysis_results")
            .select("testimonial_type")
            .eq("testimonial_candidate", True)
            .gte("analyzed_at", cutoff_7d)
            .execute()
            .data
        )
        tt_counts: dict[str, int] = {}
        for r in testimonials:
            tt = r.get("testimonial_type", "")
            if tt:
                tt_counts[tt] = tt_counts.get(tt, 0) + 1
        if tt_counts:
            from utils.constants import TESTIMONIAL_TYPE_LABELS
            sorted_tt = sorted(tt_counts.items(), key=lambda x: -x[1])
            fig = trending_bar_chart(
                [TESTIMONIAL_TYPE_LABELS.get(k, k) for k, _ in sorted_tt],
                [v for _, v in sorted_tt],
                title="Testimonial Candidates",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No testimonial candidates this week.")
    except Exception:
        st.caption("Testimonial data unavailable.")

    # Top FAQ signals — bar chart
    try:
        faq_rows = (
            client.table("analysis_results")
            .select("repeated_questions_from_caller")
            .not_.is_("repeated_questions_from_caller", "null")
            .gte("analyzed_at", cutoff_7d)
            .execute()
            .data
        )
        faq_counts: dict[str, int] = {}
        for r in faq_rows:
            qs = r.get("repeated_questions_from_caller") or []
            if isinstance(qs, str):
                try:
                    qs = json.loads(qs)
                except (json.JSONDecodeError, TypeError):
                    qs = []
            if isinstance(qs, list):
                for q in qs:
                    if isinstance(q, str) and q.strip():
                        faq_counts[q] = faq_counts.get(q, 0) + 1
        if faq_counts:
            sorted_faq = sorted(faq_counts.items(), key=lambda x: -x[1])[:6]
            fig = trending_bar_chart(
                [k for k, _ in sorted_faq],
                [v for _, v in sorted_faq],
                title="Top FAQ Signals",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No FAQ signals this week.")
    except Exception:
        st.caption("FAQ data unavailable.")


# --- Section 4: Volume & Quality Trend ---
styled_divider()
chart_left, chart_right = st.columns(2)

with chart_left:
    styled_header("Call Volume", subtitle="Last 7 days")
    daily = get_daily_volume(days=7)
    if not daily.empty:
        try:
            fig = volume_trend(daily)
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.caption("Chart unavailable.")
    else:
        st.caption("No volume data available.")

with chart_right:
    styled_header("Quality Distribution", subtitle="Last 7 days")
    try:
        quality_rows = (
            client.table("analysis_results")
            .select("quality_score")
            .not_.is_("quality_score", "null")
            .gte("analyzed_at", cutoff_7d)
            .execute()
            .data
        )
        if quality_rows:
            qdf = pd.DataFrame(quality_rows)
            fig = quality_histogram(qdf)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No quality data available.")
    except Exception:
        st.caption("Quality distribution unavailable.")

# --- Section 5: Case Type Distribution ---
styled_divider()
styled_header("Case Type Distribution", subtitle="Last 7 days")

try:
    case_type_rows = (
        client.table("analysis_results")
        .select("case_type")
        .not_.is_("case_type", "null")
        .gte("analyzed_at", cutoff_7d)
        .execute()
        .data
    )
    if case_type_rows:
        ct_df = pd.DataFrame(case_type_rows)
        fig = case_type_pie(ct_df)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("No case type data available.")
except Exception:
    st.caption("Case type distribution unavailable.")
