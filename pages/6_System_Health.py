"""System Health — Admin-only engineering metrics and model health."""

import streamlit as st
import pandas as pd
from utils.auth import check_password, check_admin
from utils.theme import inject_theme, styled_divider, styled_header, COLORS

if not check_password():
    st.stop()

inject_theme()

st.title(":gear: System Health")
st.caption("Engineering metrics, model health, and cost tracking.")

from utils.queries import (
    get_system_status, get_cost_tracking, get_drift_alerts, get_prompt_library,
)

# Quick status for all users (before admin check)
_quick_status = get_system_status()
if _quick_status and _quick_status.get("system_active"):
    st.markdown(
        f'<div class="wb-status-pill" style="background:#e8f5e9; color:#2e7d32;">'
        f'&#9679; System operational</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<div class="wb-status-pill" style="background:#ffebee; color:#c62828;">'
        f'&#9679; System paused</div>',
        unsafe_allow_html=True,
    )

if not check_admin():
    st.warning("Full dashboard requires admin access.")
    st.stop()

from utils.database import get_supabase, query_table, query_df
from components.charts import (
    cost_trend, quality_violin, quality_histogram, scatter_calibration,
)

client = get_supabase()

# --- System Status ---
styled_header("System Status")
status = get_system_status()
if status:
    is_active = status.get("system_active", False)
    try:
        daily_budget = float(status.get("daily_budget_limit") or 0)
    except (TypeError, ValueError):
        daily_budget = 0.0
    try:
        daily_spend = float(status.get("current_daily_spend") or 0)
    except (TypeError, ValueError):
        daily_spend = 0.0
    budget_remaining = max(0, daily_budget - daily_spend)

    cols = st.columns(4)
    cols[0].metric("Active", "Yes" if is_active else "No")
    cols[1].metric("Daily Budget", f"${daily_budget:.2f}")
    cols[2].metric("Today's Spend", f"${daily_spend:.2f}")
    cols[3].metric("Budget Remaining", f"${budget_remaining:.2f}")
else:
    st.caption("System status unavailable.")

styled_divider()

# --- Cost Tracking ---
styled_header("Cost Tracking", subtitle="Last 30 days")
cost_df = get_cost_tracking(days=30)
if not cost_df.empty and "date" in cost_df.columns and "total_cost" in cost_df.columns:
    try:
        fig = cost_trend(cost_df)
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        st.caption("Chart unavailable.")

    cost_df["total_cost"] = pd.to_numeric(cost_df["total_cost"], errors="coerce").fillna(0)
    cols = st.columns(3)
    total = cost_df["total_cost"].sum()
    avg_daily = cost_df["total_cost"].mean()
    cols[0].metric("Total (30d)", f"${total:.2f}")
    cols[1].metric("Avg daily", f"${avg_daily:.2f}")
    if "calls_processed" in cost_df.columns:
        total_calls = cost_df["calls_processed"].sum()
        cols[2].metric("Calls processed (30d)", f"{total_calls:,}")
else:
    st.caption("No cost data available.")

styled_divider()

# --- Quality Analytics ---
styled_header("Quality Distribution")
with st.spinner("Loading quality analytics..."):
    try:
        q_rows = (
            client.table("analysis_results")
            .select("quality_score, confidence_score")
            .not_.is_("quality_score", "null")
            .order("analyzed_at", desc=True)
            .limit(2000)
            .execute()
            .data
        )
        if q_rows:
            qdf = pd.DataFrame(q_rows)
            left, right = st.columns(2)
            with left:
                st.markdown("**Quality Score (violin)**")
                fig = quality_violin(qdf)
                st.plotly_chart(fig, use_container_width=True)
            with right:
                st.markdown("**Quality Score (histogram)**")
                fig = quality_histogram(qdf)
                st.plotly_chart(fig, use_container_width=True)

            if "confidence_score" in qdf.columns:
                st.markdown("**Confidence Score Distribution**")
                conf_df = qdf[qdf["confidence_score"].notna()]
                if not conf_df.empty:
                    st.bar_chart(conf_df["confidence_score"].value_counts().sort_index())
        else:
            st.caption("No quality data available.")
    except Exception:
        st.caption("Unable to load quality data.")

styled_divider()

# --- Drift Alerts ---
styled_header("Drift Alerts")
alerts = get_drift_alerts(limit=10)
if alerts:
    for alert in alerts:
        created = str(alert.get("created_at", ""))[:10]
        try:
            max_dev = float(alert.get("max_deviation") or 0)
        except (TypeError, ValueError):
            max_dev = 0.0
        report = alert.get("drift_report", "")
        if max_dev and max_dev > 3:
            severity = "High"
            badge_class = "wb-badge wb-badge-error"
        elif max_dev and max_dev > 2:
            severity = "Medium"
            badge_class = "wb-badge wb-badge-warning"
        else:
            severity = "Low"
            badge_class = "wb-badge wb-badge-info"

        label = f"{created} \u2014 {severity} ({max_dev:.1f}\u03c3)" if max_dev else created
        with st.expander(label):
            st.markdown(
                f'<span class="{badge_class}">{severity}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(report if report else "No report available.")
else:
    st.success("No drift alerts.")

styled_divider()

# --- Model Calibration (from arbitrated_labels) ---
styled_header("Model Calibration", subtitle="Grok vs Consensus")
try:
    gold = query_table("arbitrated_labels", select="production_quality_score, consensus_quality_score")
    if gold and len(gold) > 5:
        gold_df = pd.DataFrame(gold)
        gold_df = gold_df.rename(columns={
            "production_quality_score": "production_score",
            "consensus_quality_score": "consensus_score",
        })
        gold_df = gold_df.dropna()
        if not gold_df.empty:
            fig = scatter_calibration(gold_df)
            st.plotly_chart(fig, use_container_width=True)
            st.caption(f"{len(gold_df)} calibration labels")
        else:
            st.caption("No calibration data available.")
    else:
        st.caption("Not enough calibration labels for chart.")
except Exception:
    st.caption("Calibration data table not available.")

styled_divider()

# --- Pipeline Throughput ---
styled_header("Pipeline Throughput", subtitle="Last 7 days")
with st.spinner("Loading throughput data..."):
    try:
        from datetime import datetime, timedelta
        cutoff = (datetime.utcnow() - timedelta(days=7)).isoformat()
        rows = (
            client.table("analysis_results")
            .select("analyzed_at, validation_passed, confidence_score", count="exact")
            .gte("analyzed_at", cutoff)
            .execute()
        )
        total = rows.count or 0
        data = rows.data or []
        passed = sum(1 for r in data if r.get("validation_passed") is True)
        pass_rate = (passed / total * 100) if total else 0

        cols = st.columns(3)
        cols[0].metric("Processed (7d)", f"{total:,}")
        cols[1].metric("Avg/day", f"{total / 7:.0f}")
        cols[2].metric("Validation pass rate", f"{pass_rate:.1f}%")
    except Exception:
        st.caption("Throughput data unavailable.")

styled_divider()

# --- Active Prompts ---
styled_header("Active Prompts")
prompts = get_prompt_library()
if prompts:
    active = [p for p in prompts if p.get("is_active")]
    if active:
        for p in active:
            name = p.get("prompt_name", "")
            version = p.get("prompt_version", "")
            desc = p.get("description", "")
            st.markdown(f"- **{name}** ({version}): {desc}")
    else:
        st.caption("No active prompts found.")
else:
    st.caption("Prompt library unavailable.")
