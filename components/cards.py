"""Card components for Walker Brain Portal."""

import json
import streamlit as st
from utils.constants import quality_band, TESTIMONIAL_STATUS_COLORS


def metric_card(label: str, value, delta=None, color: str | None = None):
    """Render a metric card with optional delta and color."""
    if color:
        st.markdown(
            f'<div style="background:{color}15; border-left:4px solid {color}; '
            f'padding:12px 16px; border-radius:4px; margin-bottom:8px;">'
            f'<div style="font-size:0.85em; color:#666;">{label}</div>'
            f'<div style="font-size:1.8em; font-weight:700; color:{color};">{value}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.metric(label=label, value=value, delta=delta)


def quote_card(row: dict, show_copy: bool = True):
    """Render a quote card with metadata and copy buttons."""
    quote = row.get("key_quote", "")
    case_type = row.get("case_type", "")
    tone = row.get("emotional_tone", "")
    quality = row.get("quality_score")
    lang = row.get("original_language", "")
    date = row.get("analyzed_at", "")[:10] if row.get("analyzed_at") else ""
    tags = row.get("suggested_tags") or []
    is_testimonial = row.get("testimonial_candidate", False)
    testimonial_type = row.get("testimonial_type", "")
    sid = row.get("source_transcript_id", "")

    _, band_color = quality_band(quality)

    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except (json.JSONDecodeError, TypeError):
            tags = []

    tag_str = ", ".join(tags[:5]) if tags else ""
    lang_short = (lang or "")[:2].upper()

    with st.container(border=True):
        st.markdown(f'*"{quote}"*')
        cols = st.columns([2, 2, 1, 1])
        cols[0].caption(f"{case_type}")
        cols[1].caption(f"{tone}")
        cols[2].caption(
            f'<span style="color:{band_color}; font-weight:600;">{quality}</span>',
            unsafe_allow_html=True,
        )
        cols[3].caption(lang_short)

        if tag_str:
            st.caption(f"Tags: {tag_str}")
        if is_testimonial and testimonial_type:
            st.caption(f"Testimonial candidate: {testimonial_type}")
        st.caption(date)

        if show_copy:
            c1, c2 = st.columns(2)
            c1.code(quote, language=None)
            from utils.export import format_quote_for_clipboard
            c2.code(
                format_quote_for_clipboard(quote, case_type, tone, quality, date),
                language=None,
            )


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
            f'<span style="color:{band_color}; font-weight:700;">{quality}</span>',
            unsafe_allow_html=True,
        )
        cols[2].caption(tone)
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
    status_color = TESTIMONIAL_STATUS_COLORS.get(status, "#9e9e9e")

    type_icon = {
        "not_suitable": "Not Suitable",
        "high_value_long_form": "Long-form",
        "quantity_short_form": "Short-form",
    }.get(t_type, t_type)

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
        st.caption(f"**{label}:** —")
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
    # Quality sub-scores
    st.markdown("##### Quality Sub-Scores")
    qs = row.get("quality_sub_scores")
    if isinstance(qs, str):
        try:
            qs = json.loads(qs)
        except (json.JSONDecodeError, TypeError):
            qs = None
    if qs and isinstance(qs, dict):
        cols = st.columns(4)
        for i, (k, v) in enumerate(qs.items()):
            cols[i % 4].metric(k.replace("_", " ").title(), v if v is not None else "—")
    else:
        st.caption("—")

    # Agent scores
    st.markdown("##### Agent Performance")
    agent_cols = st.columns(4)
    for i, (field, label) in enumerate([
        ("agent_empathy_score", "Empathy"),
        ("agent_education_quality", "Education"),
        ("agent_objection_handling", "Objection Handling"),
        ("agent_closing_effectiveness", "Closing"),
    ]):
        val = row.get(field)
        if val is not None:
            agent_cols[i].progress(min(val / 10, 1.0), text=f"{label}: {val}/10")
        else:
            agent_cols[i].caption(f"{label}: —")

    # Case assessment
    st.markdown("##### Case Assessment")
    for field in ["liability_clarity", "injury_severity",
                  "documentation_quality", "estimated_case_value_low",
                  "estimated_case_value_high", "estimated_case_value_category"]:
        _render_field(field.replace("_", " ").title(), row.get(field))

    # Emotional arc
    st.markdown("##### Emotional Arc")
    arc_cols = st.columns(3)
    arc_cols[0].caption(f"Opening: {row.get('opening_emotional_state', '—')}")
    arc_cols[1].caption(f"Mid-call: {row.get('mid_call_emotional_shift', '—')}")
    arc_cols[2].caption(f"End: {row.get('end_state_emotion', '—')}")

    # Objection Taxonomy (10A)
    obj_fields = [
        "objection_categories", "mid_call_dropout_moment", "conversion_driver",
        "drop_off_reason", "agent_intervention_that_worked", "moment_that_closed",
    ]
    has_10a = any(row.get(f) is not None for f in obj_fields)
    st.markdown("##### Objection Taxonomy (WF 10A)")
    if has_10a:
        for f in obj_fields:
            _render_field(f.replace("_", " ").title(), row.get(f),
                         is_json=f in ["objection_categories"])
    else:
        st.caption("*(not applicable — no objections raised)*")

    # Language & Culture (10B)
    st.markdown("##### Language & Culture (WF 10B)")
    for f in ["reading_level_estimate", "communication_style", "spanglish_detected",
              "colloquialisms", "cultural_markers", "family_references",
              "verbatim_customer_language"]:
        _render_field(
            f.replace("_", " ").title(), row.get(f),
            is_json=f in ["colloquialisms", "cultural_markers", "family_references",
                          "verbatim_customer_language"],
        )

    # CX Intelligence (10C)
    cx_fields = [
        "questions_repeated_by_attorney", "attorney_used_prior_info",
        "handoff_wait_time_mentioned", "attorney_sentiment",
        "attorney_rejection_reason",
    ]
    has_10c = any(row.get(f) is not None for f in cx_fields)
    st.markdown("##### CX Intelligence (WF 10C)")
    if has_10c:
        for f in cx_fields:
            _render_field(f.replace("_", " ").title(), row.get(f),
                         is_json=f in ["questions_repeated_by_attorney"])
    else:
        st.caption("*(not applicable — no attorney leg)*")

    # Content Mining (10D)
    st.markdown("##### Content Mining (WF 10D)")
    for f in ["common_questions_asked", "misunderstandings",
              "education_calming_moment", "process_confusion_points",
              "other_brands_mentioned", "competitive_comparison",
              "category_confusion", "ad_or_creative_referenced",
              "ad_promise_vs_reality_mismatch", "repeated_questions_from_caller"]:
        _render_field(
            f.replace("_", " ").title(), row.get(f),
            is_json=f in [
                "common_questions_asked", "misunderstandings",
                "process_confusion_points", "other_brands_mentioned",
                "repeated_questions_from_caller",
            ],
        )

    # Metadata
    st.markdown("##### Metadata")
    meta_cols = st.columns(3)
    meta_cols[0].caption(f"Prompt: {row.get('prompt_version_used', '—')}")
    meta_cols[1].caption(f"Confidence: {row.get('confidence_score', '—')}")
    meta_cols[2].caption(f"Validation: {'Passed' if row.get('validation_passed') else 'Failed' if row.get('validation_passed') is False else '—'}")
    meta_cols2 = st.columns(3)
    meta_cols2[0].caption(f"Cost: ${row.get('api_cost', 0) or 0:.4f}")
    meta_cols2[1].caption(f"Tokens in: {row.get('input_tokens', '—')}")
    meta_cols2[2].caption(f"Tokens out: {row.get('output_tokens', '—')}")
