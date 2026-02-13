"""System Health — Admin-only engineering metrics and model health."""

import streamlit as st
import pandas as pd
from utils.auth import check_password, check_admin

if not check_password():
    st.stop()

st.title("System Health")
st.caption("Engineering metrics, model health, and cost tracking.")

if not check_admin():
    st.warning("This page requires admin access.")
    st.stop()

from utils.queries import (
    get_system_status, get_cost_tracking, get_drift_alerts, get_prompt_library,
)
from utils.database import get_supabase, query_table, query_df
from components.charts import (
    cost_trend, quality_violin, quality_histogram, scatter_calibration,
)

client = get_supabase()

# --- System Status ---
st.markdown("### System Status")
status = get_system_status()
if status:
    is_active = status.get("system_active", False)
    daily_budget = status.get("daily_budget_limit", 0) or 0
    daily_spend = status.get("current_daily_spend", 0) or 0
    budget_remaining = daily_budget - daily_spend

    cols = st.columns(4)
    cols[0].metric("Active", "Yes" if is_active else "No")
    cols[1].metric("Daily Budget", f"${daily_budget:.2f}")
    cols[2].metric("Today's Spend", f"${daily_spend:.2f}")
    cols[3].metric("Budget Remaining", f"${budget_remaining:.2f}")
else:
    st.caption("System status unavailable.")

st.markdown("---")

# --- Cost Tracking ---
st.markdown("### Cost Tracking (30 days)")
cost_df = get_cost_tracking(days=30)
if not cost_df.empty and "date" in cost_df.columns and "total_cost" in cost_df.columns:
    fig = cost_trend(cost_df)
    st.plotly_chart(fig, use_container_width=True)

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

st.markdown("---")

# --- Quality Analytics ---
st.markdown("### Quality Distribution")
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

st.markdown("---")

# --- Drift Alerts ---
st.markdown("### Drift Alerts")
alerts = get_drift_alerts(limit=10)
if alerts:
    for alert in alerts:
        created = str(alert.get("created_at", ""))[:10]
        max_dev = alert.get("max_deviation", 0)
        report = alert.get("drift_report", "")
        severity = "High" if max_dev and max_dev > 3 else "Medium" if max_dev and max_dev > 2 else "Low"
        with st.expander(f"{created} — {severity} ({max_dev:.1f}σ)" if max_dev else f"{created}"):
            st.markdown(report if report else "No report available.")
else:
    st.success("No drift alerts.")

st.markdown("---")

# --- Model Calibration (from arbitrated_labels) ---
st.markdown("### Model Calibration (Grok vs Consensus)")
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

st.markdown("---")

# --- Pipeline Throughput ---
st.markdown("### Pipeline Throughput")
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

st.markdown("---")

# --- Active Prompts ---
st.markdown("### Active Prompts")
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
