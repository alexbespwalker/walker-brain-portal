"""Today's Highlights — Marketing-focused dashboard with curated picks."""

import json
import streamlit as st
import pandas as pd
from utils.auth import check_password
from utils.theme import inject_theme, styled_divider, styled_header, COLORS

if not check_password():
    st.stop()

inject_theme()

st.title(":bar_chart: Today's Highlights")
st.caption("Curated content picks for the creative team.")

from components.cards import metric_card, quote_card
from components.charts import quality_histogram, volume_trend, case_type_pie, trending_bar_chart
from utils.constants import humanize
from utils.queries import (
    get_weekly_metric_counts, get_prior_period_metrics, fetch_quotes, get_daily_volume,
)
from utils.constants import quality_band
from utils.database import query_table, get_supabase

client = get_supabase()

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

styled_divider()

# --- Section 2 & 3: Top quotes + Trending ---
left, right = st.columns([3, 2])

with left:
    styled_header("Top Quotes This Week")
    from datetime import datetime, timedelta
    week_cutoff = (datetime.utcnow() - timedelta(days=7)).isoformat()
    top_quotes = fetch_quotes(min_quality=0, max_quality=100, limit=5, start_date=week_cutoff)
    if top_quotes:
        for row in top_quotes:
            quote_card(row, show_copy=True)
    else:
        st.caption("No quote data available yet.")

with right:
    styled_header("Trending This Week")

    from datetime import datetime, timedelta
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

    # Trending case types — bar chart
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
            fig = trending_bar_chart(
                [humanize(k) for k, _ in sorted_ct],
                [v for _, v in sorted_ct],
                title="Case Types",
            )
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
