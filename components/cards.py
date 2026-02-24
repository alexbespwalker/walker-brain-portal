"""Card components for Walker Brain Portal."""

import json
from html import escape as _esc
import streamlit as st
from utils.constants import (
    quality_band, clean_language, TESTIMONIAL_TYPE_LABELS,
    humanize, format_case_value, get_badge_class, is_falsy_sentinel,
)
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
            f'<div class="wb-metric-label" style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{label}</div>'
            f'<div class="wb-metric-value" style="color:{color}; font-family:{TYPOGRAPHY["font_family_display"]};">{value}</div>'
            f"{delta_html}"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.metric(label=label, value=value, delta=delta)


def _badge_pill(text: str, css_class: str) -> str:
    """Return HTML for a single badge pill."""
    return f'<span class="wb-badge {css_class}">{_esc(text)}</span>'


def quote_card(row: dict, show_copy: bool = True):
    """Render a styled quote card with left accent border and badge pills."""
    quote = row.get("key_quote", "")
    case_type = row.get("case_type", "")
    tone = row.get("emotional_tone", "")
    quality = row.get("quality_score")
    lang = row.get("original_language", "")
    date = row.get("analyzed_at", "")[:10] if row.get("analyzed_at") else ""
    tags = row.get("suggested_tags") or []
    is_testimonial = row.get("testimonial_candidate", False)
    testimonial_type = row.get("testimonial_type", "")

    band_name, band_color = quality_band(quality)
    tone_class = get_badge_class(tone)

    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except (json.JSONDecodeError, TypeError):
            tags = []

    tag_str = ", ".join(tags[:5]) if tags else ""
    lang_short = clean_language(lang)[:2].upper()

    sid = row.get("source_transcript_id", "")
    sid_short = sid[:12] if sid else ""

    # Badge pills row
    pills = []
    if case_type:
        pills.append(_badge_pill(case_type, "wb-badge-info"))
    if tone:
        pills.append(_badge_pill(tone, tone_class))
    if quality is not None:
        # Map quality band to badge class
        q_class = "wb-badge-error" if band_name in ("POOR", "NEEDS IMPROVEMENT") else \
                  "wb-badge-warning" if band_name == "ADEQUATE" else \
                  "wb-badge-success" if band_name in ("STRONG", "EXCEPTIONAL") else "wb-badge-info"
        pills.append(_badge_pill(f"Quality: {quality}", q_class))
    if lang_short:
        pills.append(_badge_pill(lang_short, "wb-badge-info"))
    pills_html = f'<div class="wb-pill-row">{"".join(pills)}</div>' if pills else ""

    # Build meta line
    meta_parts = []
    if sid_short:
        meta_parts.append(f'<code style="font-size:{TYPOGRAPHY["size"]["sm"]};">{_esc(sid_short)}</code>')
    if tag_str:
        meta_parts.append(f"Tags: {_esc(tag_str)}")
    if is_testimonial and testimonial_type:
        type_label = TESTIMONIAL_TYPE_LABELS.get(testimonial_type, testimonial_type)
        meta_parts.append(f"Testimonial: {_esc(type_label)}")
    if date:
        meta_parts.append(date)
    meta_line = " &middot; ".join(meta_parts) if meta_parts else ""

    st.markdown(
        f"""
        <div class="wb-quote-card">
            <div class="wb-quote-text">&ldquo;{_esc(quote)}&rdquo;</div>
            {pills_html}
            {"<div class='wb-quote-meta' style='margin-top:4px;'>" + meta_line + "</div>" if meta_line else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )

    if show_copy:
        from utils.export import format_quote_for_clipboard
        copy_text = format_quote_for_clipboard(quote, case_type, tone, quality, date)
        with st.expander("Copy text", expanded=False):
            st.code(copy_text, language=None)


def call_card(row: dict):
    """Compact call card for search results with badge pills."""
    case_type = row.get("case_type", "")
    quality = row.get("quality_score")
    tone = row.get("emotional_tone", "")
    date = row.get("analyzed_at", "")[:10] if row.get("analyzed_at") else ""
    summary = row.get("summary", "") or ""
    quote = row.get("key_quote", "")
    tags = row.get("suggested_tags") or []
    sid = row.get("source_transcript_id", "")
    case_value_cat = row.get("estimated_case_value_category", "") or ""

    band_name, band_color = quality_band(quality)
    tone_class = get_badge_class(tone)

    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except (json.JSONDecodeError, TypeError):
            tags = []

    tag_str = ", ".join(tags[:5]) if tags else ""

    with st.container(border=True):
        cols = st.columns([2, 1, 2, 1])
        cols[0].markdown(f"**{case_type}**")
        if case_value_cat and not is_falsy_sentinel(case_value_cat):
            cols[0].caption(f"Case value: {case_value_cat}")
        q_class = "wb-badge-error" if band_name in ("POOR", "NEEDS IMPROVEMENT") else \
                  "wb-badge-warning" if band_name == "ADEQUATE" else \
                  "wb-badge-success" if band_name in ("STRONG", "EXCEPTIONAL") else "wb-badge-info"
        cols[1].markdown(
            _badge_pill(f"Quality: {quality}", q_class),
            unsafe_allow_html=True,
        )
        cols[2].markdown(
            _badge_pill(humanize(tone) if tone else "\u2014", tone_class),
            unsafe_allow_html=True,
        )
        cols[3].caption(date)

        if sid:
            st.markdown(
                f'<code style="font-size:{TYPOGRAPHY["size"]["xs"]}; color:{COLORS["text_hint"]};">{_esc(sid[:12])}</code>',
                unsafe_allow_html=True,
            )

        if summary:
            st.caption(summary[:200] + ("..." if len(summary) > 200 else ""))
        if quote:
            st.markdown(f'> *"{quote[:200]}{"..." if len(quote) > 200 else ""}"*')
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
    """Render a single field in call detail view. Filters falsy sentinels from lists."""
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
            # Filter out falsy sentinels
            value = [item for item in value if not is_falsy_sentinel(item)]
            if not value:
                st.caption(f"**{label}:** \u2014")
                return
            items = "\n".join(f"- {item}" for item in value)
            st.markdown(f"**{label}:**\n{items}")
        elif isinstance(value, dict):
            st.markdown(f"**{label}:**")
            for k, v in value.items():
                if not is_falsy_sentinel(v):
                    st.caption(f"  {humanize(k)}: {v}")
        else:
            st.caption(f"**{label}:** {value}")
    else:
        st.caption(f"**{label}:** {value}")


def _has_real_value(val) -> bool:
    """Check if a field has a real (non-empty, non-sentinel) value."""
    if val is None:
        return False
    if isinstance(val, str) and val.strip().lower() in ("", "none", "null", "n/a"):
        return False
    if isinstance(val, list) and len(val) == 0:
        return False
    return True


def _render_chat_transcript(transcript: str):
    """Render transcript as chat-style message blocks. Agent → assistant, Caller → user."""
    import re
    # Split on speaker labels like "Agent:", "Caller:", "Representative:", "Customer:"
    pattern = re.compile(
        r"((?:Agent|Representative|Rep|Operator|Receptionist)\s*:)",
        re.IGNORECASE,
    )
    caller_pattern = re.compile(
        r"((?:Caller|Customer|Client|Speaker\s*\d*)\s*:)",
        re.IGNORECASE,
    )

    lines = transcript.split("\n")
    current_role = None
    current_text = []

    def flush():
        if current_role and current_text:
            text = "\n".join(current_text).strip()
            if text:
                with st.chat_message(current_role):
                    st.markdown(text)

    for line in lines:
        if pattern.match(line.strip()):
            flush()
            current_role = "assistant"
            current_text = [pattern.sub("", line.strip(), count=1).strip()]
        elif caller_pattern.match(line.strip()):
            flush()
            current_role = "user"
            current_text = [caller_pattern.sub("", line.strip(), count=1).strip()]
        elif current_role:
            current_text.append(line)
        else:
            # Before any speaker label, treat as system/context
            if line.strip():
                st.caption(line.strip())

    flush()


def call_detail_panel(row: dict):
    """Expanded detail panel for a call. Shows all fields grouped into tabs."""
    from utils.theme import styled_header

    # --- Call ID at top ---
    sid = row.get("source_transcript_id", "")
    if sid:
        st.markdown(
            f'<code style="font-family:{TYPOGRAPHY["font_family_mono"]}; '
            f'font-size:{TYPOGRAPHY["size"]["sm"]}; padding:4px 8px; '
            f'background:{COLORS["surface_variant"]}; border-radius:4px;">'
            f'Call ID: {_esc(sid)}</code>',
            unsafe_allow_html=True,
        )

    tab_overview, tab_case, tab_language, tab_content, tab_dev = st.tabs(
        ["Overview", "Case", "Language", "Content", "Developer"]
    )

    # --- Overview tab ---
    with tab_overview:
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
                cols[i % 4].metric(humanize(k), v if v is not None else "\u2014")
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
                try:
                    val = float(val)
                except (TypeError, ValueError):
                    agent_cols[i].caption(f"{label}: \u2014")
                    continue
                if val < 5:
                    score_color = COLORS["error"]
                elif val < 8:
                    score_color = COLORS["warning"]
                else:
                    score_color = COLORS["success"]
                agent_cols[i].progress(max(0.0, min(val / 10, 1.0)))
                agent_cols[i].caption(
                    f'<span style="color:{score_color}; font-weight:600;">{label}: {val:g}/10</span>',
                    unsafe_allow_html=True,
                )
            else:
                agent_cols[i].caption(f"{label}: \u2014")

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

    # --- Case tab ---
    with tab_case:
        # Case assessment
        styled_header("Case Assessment")
        ca_cols = st.columns(3)
        ca_cols[0].caption(f"**Liability Clarity:** {row.get('liability_clarity', '\u2014')}")
        ca_cols[1].caption(f"**Injury Severity:** {row.get('injury_severity', '\u2014')}")
        ca_cols[2].caption(f"**Documentation:** {row.get('documentation_quality', '\u2014')}")
        val_str = format_case_value(
            row.get("estimated_case_value_low"),
            row.get("estimated_case_value_high"),
            row.get("estimated_case_value_category", ""),
        )
        if val_str != "\u2014":
            st.markdown(f"**Estimated Value:** {val_str}")

        # Objection Taxonomy (10A) — conditional
        obj_fields = [
            "objection_categories", "mid_call_dropout_moment", "conversion_driver",
            "drop_off_reason", "agent_intervention_that_worked", "moment_that_closed",
        ]
        has_10a = any(_has_real_value(row.get(f)) for f in obj_fields)
        if has_10a:
            styled_header("Objection Taxonomy")
            for f in obj_fields:
                _render_field(humanize(f), row.get(f),
                             is_json=f in ["objection_categories"])
        else:
            st.caption("No objection taxonomy data available.")

    # --- Language tab ---
    with tab_language:
        # Language & Culture (10B)
        styled_header("Language & Culture")
        for f in ["reading_level_estimate", "communication_style", "spanglish_detected",
                  "colloquialisms", "cultural_markers", "family_references",
                  "verbatim_customer_language"]:
            _render_field(
                humanize(f), row.get(f),
                is_json=f in ["colloquialisms", "cultural_markers", "family_references",
                              "verbatim_customer_language"],
            )

        # CX Intelligence (10C) — conditional
        cx_fields = [
            "questions_repeated_by_attorney", "attorney_used_prior_info",
            "handoff_wait_time_mentioned", "attorney_sentiment",
            "attorney_rejection_reason",
        ]
        has_10c = any(_has_real_value(row.get(f)) for f in cx_fields)
        if has_10c:
            styled_header("CX Intelligence")
            for f in cx_fields:
                _render_field(humanize(f), row.get(f),
                             is_json=f in ["questions_repeated_by_attorney"])
        else:
            st.caption("No CX intelligence data available.")

    # --- Content tab ---
    with tab_content:
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
        has_10d = any(_has_real_value(row.get(f)) for f in cm_fields)
        if has_10d:
            styled_header("Content Mining")
            for f in cm_fields:
                if _has_real_value(row.get(f)):
                    _render_field(humanize(f), row.get(f),
                                 is_json=f in cm_json_fields)
        else:
            st.caption("No content mining data available.")

    # --- Developer tab ---
    with tab_dev:
        meta_cols = st.columns(3)
        meta_cols[0].caption(f"Prompt: {row.get('prompt_version_used', '\u2014')}")
        meta_cols[1].caption(f"Confidence: {row.get('confidence_score', '\u2014')}")
        meta_cols[2].caption(f"Validation: {'Passed' if row.get('validation_passed') else 'Failed' if row.get('validation_passed') is False else '\u2014'}")
        meta_cols2 = st.columns(3)
        try:
            _cost = float(row.get('api_cost') or 0)
        except (TypeError, ValueError):
            _cost = 0.0
        meta_cols2[0].caption(f"Cost: ${_cost:.4f}")
        meta_cols2[1].caption(f"Tokens in: {row.get('input_tokens', '\u2014')}")
        meta_cols2[2].caption(f"Tokens out: {row.get('output_tokens', '\u2014')}")
