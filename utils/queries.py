"""Named query functions for Walker Brain Portal.

Uses PostgREST via supabase-py for all queries.
"""

import streamlit as st
import pandas as pd
from utils.database import query_table, query_df, get_distinct_values, get_supabase


# ---------------------------------------------------------------------------
# Filter helpers
# ---------------------------------------------------------------------------

@st.cache_data(ttl=3600)
def get_case_types() -> list[str]:
    return get_distinct_values("analysis_results", "case_type")


@st.cache_data(ttl=3600)
def get_emotional_tones() -> list[str]:
    return get_distinct_values("analysis_results", "emotional_tone")


@st.cache_data(ttl=3600)
def get_outcomes() -> list[str]:
    return get_distinct_values("analysis_results", "outcome")


@st.cache_data(ttl=3600)
def get_languages() -> list[str]:
    from utils.constants import clean_language
    raw = get_distinct_values("analysis_results", "original_language")
    seen = set()
    cleaned = []
    for v in raw:
        c = clean_language(v)
        if c and c not in seen:
            seen.add(c)
            cleaned.append(c)
    return cleaned


# ---------------------------------------------------------------------------
# Quote Bank
# ---------------------------------------------------------------------------

QUOTE_COLUMNS = (
    "source_transcript_id, key_quote, case_type, emotional_tone, "
    "quality_score, original_language, suggested_tags, analyzed_at, "
    "testimonial_candidate, testimonial_type, verbatim_customer_language"
)


def fetch_quotes(
    min_quality: int = 0,
    max_quality: int = 100,
    case_types: list[str] | None = None,
    tones: list[str] | None = None,
    languages: list[str] | None = None,
    testimonial_only: bool = False,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Fetch quotes from analysis_results with filters."""
    client = get_supabase()
    q = (
        client.table("analysis_results")
        .select(QUOTE_COLUMNS)
        .not_.is_("key_quote", "null")
        .neq("key_quote", "")
        .gte("quality_score", min_quality)
        .lte("quality_score", max_quality)
        .order("quality_score", desc=True)
        .order("analyzed_at", desc=True)
    )
    if offset > 0:
        q = q.range(offset, offset + limit - 1)
    else:
        q = q.limit(limit)
    if case_types:
        q = q.in_("case_type", case_types)
    if tones:
        q = q.in_("emotional_tone", tones)
    if languages:
        q = q.in_("original_language", languages)
    if testimonial_only:
        q = q.eq("testimonial_candidate", True)
    if start_date:
        q = q.gte("analyzed_at", start_date)
    if end_date:
        q = q.lte("analyzed_at", end_date)
    return q.execute().data


# ---------------------------------------------------------------------------
# Call Search
# ---------------------------------------------------------------------------

SEARCH_COLUMNS = (
    "source_transcript_id, case_type, quality_score, emotional_tone, "
    "outcome, analyzed_at, original_language, key_quote, summary, "
    "primary_topic, suggested_tags, content_generation_flag, "
    "testimonial_candidate, testimonial_type, confidence_score, "
    "estimated_case_value_category"
)

DETAIL_COLUMNS = (
    "quality_sub_scores, agent_empathy_score, agent_education_quality, "
    "agent_objection_handling, agent_closing_effectiveness, "
    "liability_clarity, injury_severity, documentation_quality, "
    "estimated_case_value_low, estimated_case_value_high, "
    "objection_categories, mid_call_dropout_moment, conversion_driver, "
    "drop_off_reason, agent_intervention_that_worked, moment_that_closed, "
    "reading_level_estimate, communication_style, spanglish_detected, "
    "colloquialisms, cultural_markers, family_references, verbatim_customer_language, "
    "questions_repeated_by_attorney, attorney_used_prior_info, "
    "handoff_wait_time_mentioned, attorney_sentiment, attorney_rejection_reason, "
    "common_questions_asked, misunderstandings, education_calming_moment, "
    "process_confusion_points, other_brands_mentioned, competitive_comparison, "
    "category_confusion, ad_or_creative_referenced, ad_promise_vs_reality_mismatch, "
    "repeated_questions_from_caller, "
    "opening_emotional_state, mid_call_emotional_shift, end_state_emotion, "
    "prompt_version_used, validation_passed, api_cost, input_tokens, output_tokens, "
    "has_attorney_leg, analysis_type, estimated_case_value_category"
)


def search_calls(
    text_search: str | None = None,
    case_types: list[str] | None = None,
    min_quality: int = 0,
    max_quality: int = 100,
    start_date: str | None = None,
    end_date: str | None = None,
    languages: list[str] | None = None,
    tones: list[str] | None = None,
    has_quote: bool = False,
    content_worthy: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Search calls with full filter set."""
    client = get_supabase()
    q = (
        client.table("analysis_results")
        .select(SEARCH_COLUMNS)
        .gte("quality_score", min_quality)
        .lte("quality_score", max_quality)
        .order("analyzed_at", desc=True)
    )
    if offset > 0:
        q = q.range(offset, offset + limit - 1)
    else:
        q = q.limit(limit)
    if text_search:
        safe = (text_search.replace("\\", "\\\\").replace("%", "\\%")
                .replace("_", "\\_").replace("(", "\\(").replace(")", "\\)")
                .replace(".", "\\.").replace(",", "\\,"))
        q = q.or_(
            f"summary.ilike.%{safe}%,"
            f"key_quote.ilike.%{safe}%,"
            f"primary_topic.ilike.%{safe}%"
        )
    if case_types:
        q = q.in_("case_type", case_types)
    if tones:
        q = q.in_("emotional_tone", tones)
    if languages:
        q = q.in_("original_language", languages)
    if start_date:
        q = q.gte("analyzed_at", start_date)
    if end_date:
        q = q.lte("analyzed_at", end_date)
    if has_quote:
        q = q.not_.is_("key_quote", "null").neq("key_quote", "")
    if content_worthy:
        q = q.eq("content_generation_flag", True)
    return q.execute().data


def get_call_detail(source_transcript_id: str) -> dict | None:
    """Fetch full detail for a single call."""
    client = get_supabase()
    rows = (
        client.table("analysis_results")
        .select(f"{SEARCH_COLUMNS}, {DETAIL_COLUMNS}")
        .eq("source_transcript_id", source_transcript_id)
        .limit(1)
        .execute()
        .data
    )
    return rows[0] if rows else None


def get_transcript(source_transcript_id: str) -> str | None:
    """Lazy-load transcript for a single call."""
    client = get_supabase()
    rows = (
        client.table("analysis_results")
        .select("transcript_original")
        .eq("source_transcript_id", source_transcript_id)
        .limit(1)
        .execute()
        .data
    )
    if rows and rows[0].get("transcript_original"):
        return rows[0]["transcript_original"]
    return None


# ---------------------------------------------------------------------------
# Call Data Explorer
# ---------------------------------------------------------------------------

def fetch_explorer_data(
    columns: list[str],
    case_types: list[str] | None = None,
    min_quality: int = 0,
    max_quality: int = 100,
    start_date: str | None = None,
    end_date: str | None = None,
    languages: list[str] | None = None,
    limit: int = 50,
    offset: int = 0,
) -> pd.DataFrame:
    """Fetch data for Call Data Explorer with selected column groups."""
    client = get_supabase()
    select_str = ", ".join(columns)
    q = (
        client.table("analysis_results")
        .select(select_str)
        .gte("quality_score", min_quality)
        .lte("quality_score", max_quality)
        .order("analyzed_at", desc=True)
    )
    if offset > 0:
        q = q.range(offset, offset + limit - 1)
    else:
        q = q.limit(limit)
    if case_types:
        q = q.in_("case_type", case_types)
    if languages:
        q = q.in_("original_language", languages)
    if start_date:
        q = q.gte("analyzed_at", start_date)
    if end_date:
        q = q.lte("analyzed_at", end_date)

    rows = q.execute().data
    return pd.DataFrame(rows) if rows else pd.DataFrame()


# ---------------------------------------------------------------------------
# Dashboard / Today's Highlights
# ---------------------------------------------------------------------------

def get_weekly_metric_counts(days: int = 7) -> dict:
    """Get aggregated counts for dashboard metric cards."""
    client = get_supabase()
    from datetime import datetime, timedelta
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()

    quotes = (
        client.table("analysis_results")
        .select("source_transcript_id", count="exact")
        .not_.is_("key_quote", "null")
        .neq("key_quote", "")
        .gte("analyzed_at", cutoff)
        .execute()
    )
    testimonials = (
        client.table("analysis_results")
        .select("source_transcript_id", count="exact")
        .eq("testimonial_candidate", True)
        .gte("analyzed_at", cutoff)
        .execute()
    )
    content = (
        client.table("analysis_results")
        .select("source_transcript_id", count="exact")
        .eq("content_generation_flag", True)
        .gte("analyzed_at", cutoff)
        .execute()
    )
    quality_rows = (
        client.table("analysis_results")
        .select("quality_score")
        .not_.is_("quality_score", "null")
        .gte("analyzed_at", cutoff)
        .execute()
        .data
    )
    scores = sorted([r["quality_score"] for r in quality_rows])
    median = scores[len(scores) // 2] if scores else 0

    return {
        "quotes": quotes.count or 0,
        "testimonials": testimonials.count or 0,
        "content_worthy": content.count or 0,
        "median_quality": median,
    }


def get_prior_period_metrics(days: int = 7) -> dict:
    """Get metric counts for the period immediately BEFORE the current window."""
    client = get_supabase()
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    cutoff_current = (now - timedelta(days=days)).isoformat()
    cutoff_prior = (now - timedelta(days=days * 2)).isoformat()

    quotes = (
        client.table("analysis_results")
        .select("source_transcript_id", count="exact")
        .not_.is_("key_quote", "null")
        .gte("analyzed_at", cutoff_prior)
        .lt("analyzed_at", cutoff_current)
        .execute()
    )
    testimonials = (
        client.table("analysis_results")
        .select("source_transcript_id", count="exact")
        .eq("testimonial_candidate", True)
        .gte("analyzed_at", cutoff_prior)
        .lt("analyzed_at", cutoff_current)
        .execute()
    )
    content = (
        client.table("analysis_results")
        .select("source_transcript_id", count="exact")
        .eq("content_generation_flag", True)
        .gte("analyzed_at", cutoff_prior)
        .lt("analyzed_at", cutoff_current)
        .execute()
    )
    quality_rows = (
        client.table("analysis_results")
        .select("quality_score")
        .not_.is_("quality_score", "null")
        .gte("analyzed_at", cutoff_prior)
        .lt("analyzed_at", cutoff_current)
        .execute()
        .data
    )
    scores = sorted([r["quality_score"] for r in quality_rows])
    median = scores[len(scores) // 2] if scores else 0

    return {
        "quotes": quotes.count or 0,
        "testimonials": testimonials.count or 0,
        "content_worthy": content.count or 0,
        "median_quality": median,
    }


def get_top_quotes(days: int = 7, limit: int = 5) -> list[dict]:
    """Top N quotes by quality in the last N days."""
    from datetime import datetime, timedelta
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    return fetch_quotes(min_quality=0, max_quality=100, limit=limit, start_date=cutoff)


def get_daily_volume(days: int = 7) -> pd.DataFrame:
    """Daily call volume for the trend chart."""
    client = get_supabase()
    from datetime import datetime, timedelta

    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    rows = (
        client.table("analysis_results")
        .select("analyzed_at, quality_score")
        .gte("analyzed_at", cutoff)
        .order("analyzed_at")
        .execute()
        .data
    )
    if not rows:
        return pd.DataFrame(columns=["date", "count", "avg_quality"])

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["analyzed_at"]).dt.date
    daily = df.groupby("date").agg(
        count=("quality_score", "size"),
        avg_quality=("quality_score", "mean"),
    ).reset_index()
    return daily


# ---------------------------------------------------------------------------
# Testimonial Pipeline
# ---------------------------------------------------------------------------

def get_testimonial_pipeline(
    status: str | None = None,
    testimonial_type: str | None = None,
) -> list[dict]:
    """Fetch testimonial pipeline entries."""
    client = get_supabase()
    q = (
        client.table("testimonial_pipeline")
        .select("*")
        .order("quality_score", desc=True)
    )
    if status:
        q = q.eq("status", status)
    if testimonial_type:
        q = q.eq("testimonial_type", testimonial_type)
    return q.execute().data


def update_testimonial_status(
    source_transcript_id: str,
    new_status: str,
    updated_by: str = "portal",
    notes: str | None = None,
) -> dict:
    """Update a testimonial's status."""
    from utils.database import update_row
    from datetime import datetime

    data = {
        "status": new_status,
        "status_updated_at": datetime.utcnow().isoformat(),
        "status_updated_by": updated_by,
    }
    if notes is not None:
        data["notes"] = notes
    return update_row(
        "testimonial_pipeline",
        data,
        {"source_transcript_id": source_transcript_id},
    )


# ---------------------------------------------------------------------------
# System Health
# ---------------------------------------------------------------------------

def get_system_status() -> dict | None:
    """Fetch current system status."""
    rows = query_table("system_status", limit=1)
    return rows[0] if rows else None


def get_cost_tracking(days: int = 30) -> pd.DataFrame:
    """Fetch cost tracking data."""
    from datetime import datetime, timedelta
    cutoff = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    return query_df(
        "cost_tracking",
        order="-date",
        filters={"date": ("gte", cutoff)},
    )


def get_drift_alerts(limit: int = 10) -> list[dict]:
    """Fetch recent drift alerts."""
    return query_table("drift_alerts", order="-created_at", limit=limit)


def get_prompt_library() -> list[dict]:
    """Fetch all prompts."""
    return query_table("prompt_library", order="-created_at")


# ---------------------------------------------------------------------------
# Freshness + pipeline stats (for app.py billboard and page headers)
# ---------------------------------------------------------------------------

@st.cache_data(ttl=300)
def get_last_updated() -> str | None:
    """Return the most recent analyzed_at timestamp as a human-readable string."""
    client = get_supabase()
    rows = (
        client.table("analysis_results")
        .select("analyzed_at")
        .order("analyzed_at", desc=True)
        .limit(1)
        .execute()
        .data
    )
    if rows and rows[0].get("analyzed_at"):
        from datetime import datetime, timezone
        ts = rows[0]["analyzed_at"]
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            hour = dt.hour % 12 or 12
            am_pm = "AM" if dt.hour < 12 else "PM"
            return f"{dt.strftime('%b')} {dt.day}, {dt.year} at {hour}:{dt.strftime('%M')} {am_pm} UTC"
        except Exception:
            return ts[:16]
    return None


@st.cache_data(ttl=600)
def get_pipeline_stats() -> dict:
    """Get aggregate stats for the app.py orientation billboard."""
    client = get_supabase()
    count_res = (
        client.table("analysis_results")
        .select("source_transcript_id", count="exact")
        .execute()
    )
    total = count_res.count or 0

    min_res = (
        client.table("analysis_results")
        .select("analyzed_at")
        .order("analyzed_at")
        .limit(1)
        .execute()
        .data
    )
    since = min_res[0]["analyzed_at"][:10] if min_res else None

    status_res = (
        client.table("system_status")
        .select("system_active")
        .limit(1)
        .execute()
        .data
    )
    is_active = status_res[0].get("system_active", False) if status_res else False

    return {"total": total, "since": since, "active": is_active}


# ---------------------------------------------------------------------------
# Count helpers (for pagination)
# ---------------------------------------------------------------------------

def count_quotes(
    min_quality: int = 0,
    max_quality: int = 100,
    case_types: list[str] | None = None,
    tones: list[str] | None = None,
    languages: list[str] | None = None,
    testimonial_only: bool = False,
    start_date: str | None = None,
    end_date: str | None = None,
) -> int:
    """Count total quotes matching filters."""
    client = get_supabase()
    q = (
        client.table("analysis_results")
        .select("source_transcript_id", count="exact")
        .not_.is_("key_quote", "null")
        .neq("key_quote", "")
        .gte("quality_score", min_quality)
        .lte("quality_score", max_quality)
    )
    if case_types:
        q = q.in_("case_type", case_types)
    if tones:
        q = q.in_("emotional_tone", tones)
    if languages:
        q = q.in_("original_language", languages)
    if testimonial_only:
        q = q.eq("testimonial_candidate", True)
    if start_date:
        q = q.gte("analyzed_at", start_date)
    if end_date:
        q = q.lte("analyzed_at", end_date)
    return q.execute().count or 0


def count_calls(
    text_search: str | None = None,
    case_types: list[str] | None = None,
    min_quality: int = 0,
    max_quality: int = 100,
    start_date: str | None = None,
    end_date: str | None = None,
    languages: list[str] | None = None,
    tones: list[str] | None = None,
    has_quote: bool = False,
    content_worthy: bool = False,
) -> int:
    """Count total calls matching filters."""
    client = get_supabase()
    q = (
        client.table("analysis_results")
        .select("source_transcript_id", count="exact")
        .gte("quality_score", min_quality)
        .lte("quality_score", max_quality)
    )
    if text_search:
        safe = (text_search.replace("\\", "\\\\").replace("%", "\\%")
                .replace("_", "\\_").replace("(", "\\(").replace(")", "\\)")
                .replace(".", "\\.").replace(",", "\\,"))
        q = q.or_(
            f"summary.ilike.%{safe}%,"
            f"key_quote.ilike.%{safe}%,"
            f"primary_topic.ilike.%{safe}%"
        )
    if case_types:
        q = q.in_("case_type", case_types)
    if tones:
        q = q.in_("emotional_tone", tones)
    if languages:
        q = q.in_("original_language", languages)
    if start_date:
        q = q.gte("analyzed_at", start_date)
    if end_date:
        q = q.lte("analyzed_at", end_date)
    if has_quote:
        q = q.not_.is_("key_quote", "null").neq("key_quote", "")
    if content_worthy:
        q = q.eq("content_generation_flag", True)
    return q.execute().count or 0


def count_explorer_rows(
    case_types: list[str] | None = None,
    min_quality: int = 0,
    max_quality: int = 100,
    start_date: str | None = None,
    end_date: str | None = None,
    languages: list[str] | None = None,
) -> int:
    """Count total rows for Data Explorer matching filters."""
    client = get_supabase()
    q = (
        client.table("analysis_results")
        .select("source_transcript_id", count="exact")
        .gte("quality_score", min_quality)
        .lte("quality_score", max_quality)
    )
    if case_types:
        q = q.in_("case_type", case_types)
    if languages:
        q = q.in_("original_language", languages)
    if start_date:
        q = q.gte("analyzed_at", start_date)
    if end_date:
        q = q.lte("analyzed_at", end_date)
    return q.execute().count or 0
