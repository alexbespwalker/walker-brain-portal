"""Card components for Walker Brain Portal."""

import json
import streamlit as st
from utils.constants import quality_band, clean_language, TESTIMONIAL_STATUS_COLORS, TESTIMONIAL_TYPE_LABELS
from utils.theme import COLORS, TYPOGRAPHY, SPACING, SHADOWS, BORDERS


def metric_card(label: str, value, delta=None, color: str | None = None):
    """Render a styled metric card with optional delta and color accent."""
    if color:
        delta_html = ""
        if delta is not None:
            arrow = "\u25b2" if delta > 0 else "\u25bc" if delta < 0 else "\u2014"
            d_color = COLORS["success"] if delta > 0 else COLORS["error"] if delta < 0 else COLORS["text_hint"]
            sign = "+" if delta > 0 else ""
            delta_html = (
                f'<div class="wb-metric-delta" style="color:{d_color};">'
                f"{arrow} {sign}{delta} vs prior week</div>"
            )
        st.markdown(
            f'<div class="wb-metric-card" style="border-left: 3px solid {color};">'
            f'<div class="wb-metric-label">{label}</div>'
            f'<div class="wb-metric-value" style="color:{color};">{value}</div>'
            f"{delta_html}"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.metric(label=label, value=value, delta=delta)


def quote_card(row: dict, show_copy: bool = True):
    """Render a styled quote card with left accent border."""
    quote = row.get("key_quote", "")
    case_type = row.get("case_type", "")
    tone = row.get("emotional_tone", "")
    quality = row.get("quality_score")
    lang = row.get("original_language", "")
    date = row.get("analyzed_at", "")[:10] if row.get("analyzed_at") else ""
    tags = row.get("suggested_tags") or []
    is_testimonial = row.get("testimonial_candidate", False)
    testimonial_type = row.get("testimonial_type", "")

    _, band_color = quality_band(quality)

    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except (json.JSONDecodeError, TypeError):
            tags = []

    tag_str = ", ".join(tags[:5]) if tags else ""
    lang_short = clean_language(lang)[:2].upper()

    # Build meta line
    meta_parts = []
    if tag_str:
        meta_parts.append(f"Tags: {tag_str}")
    if is_testimonial and testimonial_type:
        type_label = TESTIMONIAL_TYPE_LABELS.get(testimonial_type, testimonial_type)
        meta_parts.append(f"Testimonial: {type_label}")
    if date:
        meta_parts.append(date)
    meta_line = " &middot; ".join(meta_parts) if meta_parts else ""

    st.markdown(
        f"""
        <div class="wb-quote-card">
            <div class="wb-quote-text">&ldquo;{quote}&rdquo;</div>
            <div class="wb-quote-meta">
                {case_type}
                &nbsp;&middot;&nbsp; {tone}
                &nbsp;&middot;&nbsp; <span style="color:{band_color}; font-weight:600;">Quality: {quality}</span>
                &nbsp;&middot;&nbsp; {lang_short}
            </div>
            {"<div class='wb-quote-meta' style='margin-top:4px;'>" + meta_line + "</div>" if meta_line else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if show_copy:
        from utils.export import format_quote_for_clipboard
        copy_text = format_quote_for_clipboard(quote, case_type, tone, quality, date)
        st.code(copy_text, language=None)


def call_card(row: dict):
    """Compact call card for search results."""
    case_type = row.get("case_type", "")
    quality = row.get("quality_score")
    tone = row.get("emotional_tone", "")
    date = row.get("analyzed_at", "")[:10] if row.get("analyzed_at") else ""
    summary = row.get("summary", "") or ""
    quote = row.get("key_quote", "")
    tags = row.get("suggested_tags") or []

    _, band_color = quality_band(quality)

    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except (json.JSONDecodeError, TypeError):
            tags = []

    tag_str = ", ".join(tags[:5]) if tags else ""

    with st.container(border=True):
        cols = st.columns([2, 1, 2, 1])
        cols[0].markdown(f"**{case_type}**")
        cols[1].markdown(
            f'<span style="color:{band_color}; font-weight:700;">Quality: {quality}</span>',
            unsafe_allow_html=True,
        )
        cols[2].caption(f"Tone: {tone}")
        cols[3].caption(date)

        if summary:
            st.caption(summary[:200] + ("..." if len(summary) > 200 else ""))
        if quote:
            st.markdown(f'> *"{quote[:150]}{"..." if len(quote) > 150 else ""}"*')
        if tag_str:
            st.caption(f"Tags: {tag_str}")


def testimonial_card(row: dict, next_status: str | None = None):
    """Card for testimonial pipeline kanban board."""
    case_type = row.get("case_type", "")
    quality = row.get("quality_score")
    quote = row.get("key_quote", "")
    t_type = row.get("testimonial_type", "")
    sid = row.get("source_transcript_id", "")
    notes = row.get("notes", "")
    status = row.get("status", "")

    _, band_color = quality_band(quality)
    type_icon = TESTIMONIAL_TYPE_LABELS.get(t_type, t_type)

    with st.container(border=True):
        st.markdown(f"**{type_icon}**")
        st.caption(f"{case_type} | Quality: {quality}")
        if quote:
            st.markdown(f'*"{quote[:80]}{"..." if len(quote) > 80 else ""}"*')
        if notes:
            st.caption(f"Notes: {notes}")

        if next_status:
            if st.button(
                f"Move to {next_status}",
                key=f"move_{sid}_{next_status}",
                type="primary",
                use_container_width=True,
            ):
                from utils.queries import update_testimonial_status
                update_testimonial_status(sid, next_status)
                st.rerun()


def _render_field(label: str, value, is_json: bool = False):
    """Render a single field in call detail view."""
    if value is None:
        st.caption(f"**{label}:** \u2014")
        return
    if is_json:
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                pass
        if isinstance(value, list):
            items = "\n".join(f"- {item}" for item in value)
            st.markdown(f"**{label}:**\n{items}")
        elif isinstance(value, dict):
            st.markdown(f"**{label}:**")
            for k, v in value.items():
                st.caption(f"  {k}: {v}")
        else:
            st.caption(f"**{label}:** {value}")
    else:
        st.caption(f"**{label}:** {value}")


def call_detail_panel(row: dict):
    """Expanded detail panel for a call. Shows all fields grouped by module."""
    from utils.theme import styled_header

    # Quality sub-scores
    styled_header("Quality Sub-Scores")
    qs = row.get("quality_sub_scores")
    if isinstance(qs, str):
        try:
            qs = json.loads(qs)
        except (json.JSONDecodeError, TypeError):
            qs = None
    if qs and isinstance(qs, dict):
        cols = st.columns(4)
        for i, (k, v) in enumerate(qs.items()):
            cols[i % 4].metric(k.replace("_", " ").title(), v if v is not None else "\u2014")
    else:
        st.caption("No sub-score data available.")

    # Agent scores
    styled_header("Agent Performance")
    agent_cols = st.columns(4)
    for i, (field, label) in enumerate([
        ("agent_empathy_score", "Empathy"),
        ("agent_education_quality", "Education"),
        ("agent_objection_handling", "Objection Handling"),
        ("agent_closing_effectiveness", "Closing"),
    ]):
        val = row.get(field)
        if val is not None:
            if val < 5:
                score_color = COLORS["error"]
            elif val < 8:
                score_color = COLORS["warning"]
            else:
                score_color = COLORS["success"]
            agent_cols[i].progress(min(val / 10, 1.0))
            agent_cols[i].caption(
                f'<span style="color:{score_color}; font-weight:600;">{label}: {val}/10</span>',
                unsafe_allow_html=True,
            )
        else:
            agent_cols[i].caption(f"{label}: \u2014")

    # Case assessment
    styled_header("Case Assessment")
    ca_cols = st.columns(3)
    ca_cols[0].caption(f"**Liability Clarity:** {row.get('liability_clarity', '\u2014')}")
    ca_cols[1].caption(f"**Injury Severity:** {row.get('injury_severity', '\u2014')}")
    ca_cols[2].caption(f"**Documentation:** {row.get('documentation_quality', '\u2014')}")
    low = row.get("estimated_case_value_low")
    high = row.get("estimated_case_value_high")
    cat = row.get("estimated_case_value_category", "")
    if low is not None or high is not None:
        val_str = f"${low:,.0f}" if low else "?"
        val_str += f" \u2014 ${high:,.0f}" if high else ""
        if cat:
            st.markdown(f"**Estimated Value:** {val_str} ({cat})")
        else:
            st.markdown(f"**Estimated Value:** {val_str}")

    # Emotional arc
    styled_header("Emotional Arc")
    opening = row.get("opening_emotional_state", "\u2014")
    mid = row.get("mid_call_emotional_shift", "\u2014")
    end = row.get("end_state_emotion", "\u2014")
    st.markdown(
        f'<span style="font-size:{TYPOGRAPHY["size"]["base"]};">'
        f"{opening} &rarr; {mid} &rarr; {end}</span>",
        unsafe_allow_html=True,
    )

    # Objection Taxonomy (10A) — only show if data exists
    obj_fields = [
        "objection_categories", "mid_call_dropout_moment", "conversion_driver",
        "drop_off_reason", "agent_intervention_that_worked", "moment_that_closed",
    ]
    has_10a = any(row.get(f) is not None for f in obj_fields)
    if has_10a:
        styled_header("Objection Taxonomy")
        for f in obj_fields:
            _render_field(f.replace("_", " ").title(), row.get(f),
                         is_json=f in ["objection_categories"])

    # Language & Culture (10B)
    styled_header("Language & Culture")
    for f in ["reading_level_estimate", "communication_style", "spanglish_detected",
              "colloquialisms", "cultural_markers", "family_references",
              "verbatim_customer_language"]:
        _render_field(
            f.replace("_", " ").title(), row.get(f),
            is_json=f in ["colloquialisms", "cultural_markers", "family_references",
                          "verbatim_customer_language"],
        )

    # CX Intelligence (10C) — only show if data exists
    cx_fields = [
        "questions_repeated_by_attorney", "attorney_used_prior_info",
        "handoff_wait_time_mentioned", "attorney_sentiment",
        "attorney_rejection_reason",
    ]
    has_10c = any(row.get(f) is not None for f in cx_fields)
    if has_10c:
        styled_header("CX Intelligence")
        for f in cx_fields:
            _render_field(f.replace("_", " ").title(), row.get(f),
                         is_json=f in ["questions_repeated_by_attorney"])

    # Content Mining (10D) — always show header, but skip None fields
    cm_fields = [
        "common_questions_asked", "misunderstandings",
        "education_calming_moment", "process_confusion_points",
        "other_brands_mentioned", "competitive_comparison",
        "category_confusion", "ad_or_creative_referenced",
        "ad_promise_vs_reality_mismatch", "repeated_questions_from_caller",
    ]
    cm_json_fields = {
        "common_questions_asked", "misunderstandings",
        "process_confusion_points", "other_brands_mentioned",
        "repeated_questions_from_caller",
    }
    has_10d = any(row.get(f) is not None for f in cm_fields)
    if has_10d:
        styled_header("Content Mining")
        for f in cm_fields:
            if row.get(f) is not None:
                _render_field(f.replace("_", " ").title(), row.get(f),
                             is_json=f in cm_json_fields)

    # Metadata
    with st.expander("Developer Info", expanded=False):
        meta_cols = st.columns(3)
        meta_cols[0].caption(f"Prompt: {row.get('prompt_version_used', '\u2014')}")
        meta_cols[1].caption(f"Confidence: {row.get('confidence_score', '\u2014')}")
        meta_cols[2].caption(f"Validation: {'Passed' if row.get('validation_passed') else 'Failed' if row.get('validation_passed') is False else '\u2014'}")
        meta_cols2 = st.columns(3)
        meta_cols2[0].caption(f"Cost: ${row.get('api_cost', 0) or 0:.4f}")
        meta_cols2[1].caption(f"Tokens in: {row.get('input_tokens', '\u2014')}")
        meta_cols2[2].caption(f"Tokens out: {row.get('output_tokens', '\u2014')}")
