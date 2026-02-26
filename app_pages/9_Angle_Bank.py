"""Angle Bank — Browse and filter creative angle briefs from WF 20."""

import json
from html import escape as _esc
import streamlit as st
from utils.auth import check_password, get_current_user
from utils.theme import inject_theme, styled_divider, empty_state, COLORS, TYPOGRAPHY, SPACING, SHADOWS, BORDERS
from utils.database import query_table
from utils.constants import CONTENT_TYPE_COLORS, INTENT_COLORS, FUNNEL_COLORS
from utils.queries import (
    get_nsm_weekly_count, update_angle_feedback, get_ledger_detail, get_feedback_stats,
)
from components.pagination import paginated_controls

if not check_password():
    st.stop()

inject_theme()

st.title(":bulb: Angle Bank")
st.caption("Creative angle briefs generated from high-quality intake calls.")

# --- NSM Header Stat ---
_nsm = get_nsm_weekly_count()
if _nsm["this_week"] > 0:
    _delta_html = ""
    if _nsm["delta"] != 0:
        _arrow = "\u25b2" if _nsm["delta"] > 0 else "\u25bc"
        _d_color = COLORS["success"] if _nsm["delta"] > 0 else COLORS["error"]
        _sign = "+" if _nsm["delta"] > 0 else ""
        _delta_html = (
            f' <span style="font-size:{TYPOGRAPHY["size"]["xs"]}; color:{_d_color}; font-weight:600;">'
            f'{_arrow} {_sign}{_nsm["delta"]} vs last week</span>'
        )
    st.markdown(
        f'<div class="wb-nsm-banner">'
        f'<span class="wb-nsm-value">{_nsm["this_week"]}</span>'
        f'<span class="wb-nsm-label">unique angle{"s" if _nsm["this_week"] != 1 else ""} '
        f'surfaced this week{_delta_html}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
else:
    empty_state(
        "&#128161;",
        "No angles surfaced yet this week.",
        "Run WF 20 from n8n to generate the first batch.",
    )

# --- Feedback counter ---
_fb_stats = get_feedback_stats()
if _fb_stats["total"] > 0:
    st.markdown(
        f'<div class="wb-quote-meta" style="padding:{SPACING["xs"]} 0 {SPACING["sm"]} 0;">'
        f'{_fb_stats["reviewed"]} of {_fb_stats["total"]} reviewed'
        f' &middot; Team used <strong style="color:{COLORS["primary"]};">{_fb_stats["used_this_month"]}</strong> this month'
        f'</div>',
        unsafe_allow_html=True,
    )

# --- Constants ---
CONTENT_TYPE_LABELS = {
    "educational_explainer": "Educational Explainer",
    "social_hook": "Social Hook",
    "case_study_brief": "Case Study Brief",
    "testimonial_angle": "Testimonial Angle",
}

STATUS_OPTIONS = ["pending_review", "approved"]


def _parse_content(row: dict) -> dict:
    """Parse content_text JSONB field into a dict."""
    ct = row.get("content_text")
    if isinstance(ct, dict):
        return ct
    if isinstance(ct, str):
        try:
            return json.loads(ct)
        except (json.JSONDecodeError, TypeError):
            return {}
    return {}


def _badge(text: str, color: str) -> str:
    """Return HTML for a colored badge pill using theme badge class."""
    hc = color.lstrip("#")
    r, g, b = int(hc[:2], 16), int(hc[2:4], 16), int(hc[4:6], 16)
    bg = f"rgba({r},{g},{b},0.12)"
    return (
        f'<span class="wb-badge" style="color:{color}; background:{bg}; '
        f'margin-right:6px; margin-bottom:4px;">{_esc(str(text))}</span>'
    )


def angle_card(row: dict, content: dict):
    """Render a single creative angle card."""
    content_type = row.get("content_type", "")
    injury_type = row.get("injury_type", "Other")
    quality = row.get("quality_score")
    status = row.get("status", "")
    created = (row.get("created_at") or "")[:10]
    model = row.get("generation_model", "")

    creative_angle = content.get("creative_angle", "")
    call_summary = content.get("call_summary", "")
    content_intent = content.get("content_intent", "")
    key_quotes = content.get("key_quotes", [])
    emotional_arc = content.get("emotional_arc", {})
    why_this_angle = content.get("why_this_angle", "")
    funnel_hint = content.get("funnel_stage_hint", "")

    ct_label = CONTENT_TYPE_LABELS.get(content_type, content_type.replace("_", " ").title())
    ct_color = CONTENT_TYPE_COLORS.get(content_type, COLORS["text_hint"])
    intent_color = INTENT_COLORS.get(content_intent, COLORS["text_hint"])
    funnel_color = FUNNEL_COLORS.get(funnel_hint, COLORS["text_hint"])
    status_color = COLORS["success"] if status == "approved" else COLORS["warning"]

    # Badge row
    badges_html = _badge(ct_label, ct_color)
    if content_intent:
        badges_html += _badge(content_intent, intent_color)
    if funnel_hint:
        badges_html += _badge(funnel_hint, funnel_color)
    badges_html += _badge(status.replace("_", " ").title(), status_color)
    if injury_type:
        badges_html += _badge(injury_type, COLORS["text_secondary"])
    if quality is not None:
        q_color = COLORS["success"] if quality >= 75 else COLORS["warning"] if quality >= 60 else COLORS["error"]
        badges_html += _badge(f"Q: {quality}", q_color)

    # Quotes HTML
    quotes_html = ""
    if key_quotes and isinstance(key_quotes, list):
        quotes_items = "".join(
            f'<li>"{_esc(q)}"</li>'
            for q in key_quotes[:3] if q
        )
        if quotes_items:
            quotes_html = (
                f'<div class="wb-angle-quotes">'
                f'<div class="wb-angle-section-label">KEY QUOTES</div>'
                f'<ul style="margin:0; padding-left:18px;">{quotes_items}</ul>'
                f'</div>'
            )

    # Emotional arc HTML
    arc_html = ""
    if emotional_arc and isinstance(emotional_arc, dict):
        arc_parts = []
        for phase, label in [("opening", "Opening"), ("mid", "Turning Point"), ("closing", "Closing")]:
            val = emotional_arc.get(phase, "")
            if val:
                arc_parts.append(f'<span><strong>{label}:</strong> {_esc(str(val))}</span>')
        if arc_parts:
            arc_html = (
                f'<div class="wb-angle-arc" style="border-left:3px solid {ct_color};">'
                f'<div class="wb-angle-section-label">EMOTIONAL ARC</div>'
                + "<br>".join(arc_parts)
                + '</div>'
            )

    # Why this angle
    why_html = ""
    if why_this_angle:
        why_html = (
            f'<div class="wb-angle-why">'
            f'<strong>Why this works:</strong> {_esc(why_this_angle)}</div>'
        )

    # Meta line
    meta_parts = [f"Created {created}"] if created else []
    if model:
        meta_parts.append(model.split("/")[-1])
    if row.get("api_cost") is not None:
        meta_parts.append(f"${float(row['api_cost']):.4f}")
    meta_html = (
        f'<div class="wb-angle-meta">'
        + " &middot; ".join(meta_parts)
        + '</div>'
    ) if meta_parts else ""

    # Full card using theme CSS class
    st.markdown(
        f'<div class="wb-angle-card" style="border-left:4px solid {ct_color};">'
        f'<div class="wb-angle-badges">{badges_html}</div>'
        f'<div class="wb-angle-title">{_esc(creative_angle)}</div>'
        f'<div class="wb-angle-summary">{_esc(call_summary)}</div>'
        f'{quotes_html}'
        f'{arc_html}'
        f'{why_html}'
        f'{meta_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


# --- Sidebar filters ---
with st.sidebar:
    st.header("Filters")

    # Status
    status_filter = st.multiselect(
        "Status",
        options=STATUS_OPTIONS,
        default=STATUS_OPTIONS,
        format_func=lambda s: s.replace("_", " ").title(),
        key="ab_status",
    )

    # Content type
    ct_options = list(CONTENT_TYPE_LABELS.keys())
    ct_selected = st.multiselect(
        "Content Type",
        options=ct_options,
        format_func=lambda k: CONTENT_TYPE_LABELS.get(k, k),
        key="ab_content_type",
    )

    # Content intent (applied in Python after fetch)
    intent_selected = st.multiselect(
        "Content Intent",
        options=["Educate", "Empathize", "Empower", "Activate"],
        key="ab_intent",
    )

    # Quality range
    min_q, max_q = st.slider("Quality Score", 0, 100, (70, 100), key="ab_quality")

    # Date range
    from datetime import datetime, timedelta
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "From",
            value=datetime.utcnow().date() - timedelta(days=30),
            key="ab_date_start",
        )
    with col2:
        end_date = st.date_input(
            "To",
            value=datetime.utcnow().date(),
            key="ab_date_end",
        )


# --- Reset page when filters change ---
_fkey = f"{status_filter}|{ct_selected}|{intent_selected}|{min_q}|{max_q}|{start_date}|{end_date}"
if st.session_state.get("ab_page_filter_hash") != _fkey:
    st.session_state["ab_page"] = 0
    st.session_state["ab_page_filter_hash"] = _fkey

# --- Build PostgREST filters ---
filters = {}

if status_filter:
    filters["status"] = ("in", status_filter)
else:
    filters["status"] = ("in", STATUS_OPTIONS)

if ct_selected:
    filters["content_type"] = ("in", ct_selected)

filters["quality_score"] = ("gte", min_q)
if max_q < 100:
    # Add separate filter for max — query_table only supports one filter per column
    # We'll handle this in Python post-filter
    pass

if start_date:
    filters["created_at"] = ("gte", start_date.isoformat())

# --- Fetch data ---
with st.spinner("Loading angles..."):
    rows = query_table(
        "content_generation_queue",
        select="*",
        filters=filters,
        order="-created_at",
        limit=200,
    )

# --- Post-fetch filters (JSONB fields + max quality) ---
filtered = []
for row in rows:
    # Max quality filter
    qs = row.get("quality_score")
    if qs is not None and qs > max_q:
        continue

    # End date filter
    created = row.get("created_at", "")
    if end_date and created and created[:10] > end_date.isoformat():
        continue

    # Content intent filter (from JSONB)
    if intent_selected:
        content = _parse_content(row)
        if content.get("content_intent") not in intent_selected:
            continue

    filtered.append(row)

# --- Display ---
total = len(filtered)

if total == 0:
    empty_state(
        "&#128161;",
        "No creative angles found matching your filters.",
        "Try adjusting the date range or quality threshold, or run WF 20 from n8n to generate new angles.",
    )
else:
    # Summary metrics
    from components.cards import metric_card

    pending = sum(1 for r in filtered if r.get("status") == "pending_review")
    approved = sum(1 for r in filtered if r.get("status") == "approved")

    # Content type breakdown
    ct_counts = {}
    for r in filtered:
        ct = r.get("content_type", "other")
        ct_counts[ct] = ct_counts.get(ct, 0) + 1

    m_cols = st.columns(4)
    with m_cols[0]:
        metric_card("Total Angles", total, color=COLORS["primary"])
    with m_cols[1]:
        metric_card("Pending Review", pending, color=COLORS["warning"])
    with m_cols[2]:
        metric_card("Approved", approved, color=COLORS["success"])
    with m_cols[3]:
        metric_card("Types", len(ct_counts), color=COLORS["info"])

    ct_summary = ", ".join(
        f"{CONTENT_TYPE_LABELS.get(k, k)}: {v}"
        for k, v in sorted(ct_counts.items(), key=lambda x: -x[1])
    )
    st.caption(ct_summary)

    styled_divider()

    # Paginate
    page_size = 20
    page_num = st.session_state.get("ab_page", 0)
    total_pages = max(1, -(-total // page_size))  # ceil division
    page_num = min(page_num, total_pages - 1)

    nav1, nav2, nav3 = st.columns([1, 2, 1])
    with nav1:
        if st.button("Previous", key="ab_prev", disabled=(page_num == 0), use_container_width=True):
            st.session_state["ab_page"] = max(0, page_num - 1)
            st.rerun()
    with nav2:
        st.markdown(
            f'<div style="text-align:center; padding:6px 0; font-size:{TYPOGRAPHY["size"]["sm"]}; '
            f'color:{COLORS["text_secondary"]}; font-weight:{TYPOGRAPHY["weight"]["medium"]};">'
            f'Page {page_num + 1} of {total_pages} &middot; {total} angles</div>',
            unsafe_allow_html=True,
        )
    with nav3:
        if st.button("Next", key="ab_next", disabled=(page_num >= total_pages - 1), use_container_width=True):
            st.session_state["ab_page"] = page_num + 1
            st.rerun()

    # Render cards
    start_idx = page_num * page_size
    end_idx = min(start_idx + page_size, total)

    # Pre-fetch ledger detail for this page's transcript IDs
    page_rows = filtered[start_idx:end_idx]
    page_tids = tuple(
        r.get("source_transcript_id", "") for r in page_rows if r.get("source_transcript_id")
    )
    ledger_map = get_ledger_detail(page_tids) if page_tids else {}

    current_user = get_current_user()

    for i, row in enumerate(page_rows):
        content = _parse_content(row)
        angle_card(row, content)

        # Feedback buttons (only for rows in surfacing_ledger)
        sid = row.get("source_transcript_id", "")
        ledger_info = ledger_map.get(sid, {})
        ledger_status = ledger_info.get("usage_status") if ledger_info else None

        if ledger_status == "surfaced":
            # Comment input + action buttons
            comment = st.text_input(
                "Optional comment",
                key=f"comment_{start_idx + i}",
                placeholder="Why this angle works (or doesn't)...",
                label_visibility="collapsed",
            )
            bcol1, bcol2, bcol3 = st.columns([1, 1, 2])
            with bcol1:
                if st.button(
                    "\u2713  Used in Campaign",
                    key=f"used_{start_idx + i}",
                    type="primary",
                    use_container_width=True,
                ):
                    update_angle_feedback(sid, "used", comment=comment or None, user_email=current_user)
                    # Invalidate caches that depend on ledger data
                    get_ledger_detail.clear()
                    get_feedback_stats.clear()
                    st.toast("Marked as Used!")
                    st.rerun()
            with bcol2:
                if st.button(
                    "Pass",
                    key=f"pass_{start_idx + i}",
                    use_container_width=True,
                ):
                    update_angle_feedback(sid, "passed", comment=comment or None, user_email=current_user)
                    get_ledger_detail.clear()
                    get_feedback_stats.clear()
                    st.toast("Marked as Pass")
                    st.rerun()
            # Spacing after buttons
            st.markdown('<div style="margin-bottom:8px;"></div>', unsafe_allow_html=True)

        elif ledger_status in ("used", "passed"):
            if ledger_status == "used":
                _b_icon = "\u2713"
                _b_color = COLORS["success"]
                _b_bg = "rgba(0,184,148,0.10)"
                _b_border = "rgba(0,184,148,0.25)"
                _b_shadow = "0 0 8px rgba(0,184,148,0.12)"
                _b_label = "Used in Campaign"
            else:
                _b_icon = "\u2014"
                _b_color = COLORS["text_hint"]
                _b_bg = "rgba(107,114,128,0.08)"
                _b_border = "rgba(107,114,128,0.20)"
                _b_shadow = "none"
                _b_label = "Passed"

            # Status pill
            _fb_by = ledger_info.get("feedback_by", "")
            _fb_at = (ledger_info.get("feedback_at") or "")[:10]
            _attribution = ""
            if _fb_by or _fb_at:
                _parts = []
                if _fb_by:
                    _parts.append(_esc(_fb_by))
                if _fb_at:
                    _parts.append(_fb_at)
                _attribution = (
                    f' <span style="font-weight:400; text-transform:none; letter-spacing:normal;">'
                    f'&middot; {" &middot; ".join(_parts)}</span>'
                )

            st.markdown(
                f'<div class="wb-feedback-pill" style="color:{_b_color}; background:{_b_bg}; '
                f'border:1px solid {_b_border}; box-shadow:{_b_shadow};">'
                f'{_b_icon} {_b_label}{_attribution}</div>',
                unsafe_allow_html=True,
            )

            # Show comment if present
            _fb_comment = ledger_info.get("feedback_comment")
            if _fb_comment:
                st.markdown(
                    f'<div class="wb-feedback-comment">'
                    f'&ldquo;{_esc(_fb_comment)}&rdquo;</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(f'<div style="margin-bottom:{SPACING["sm"]};"></div>', unsafe_allow_html=True)
        else:
            # No ledger entry — just spacing
            st.markdown('<div style="margin-bottom:8px;"></div>', unsafe_allow_html=True)
