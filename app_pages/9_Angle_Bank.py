"""Angle Bank — Browse and filter creative angle briefs from WF 20."""

import json
from html import escape as _esc
import streamlit as st
from utils.auth import check_password
from utils.theme import inject_theme, COLORS, TYPOGRAPHY, SPACING, SHADOWS, BORDERS
from utils.database import query_table
from components.pagination import paginated_controls

if not check_password():
    st.stop()

inject_theme()

st.title(":bulb: Angle Bank")
st.caption("Creative angle briefs generated from high-quality intake calls.")

# --- Constants ---
CONTENT_TYPE_LABELS = {
    "educational_explainer": "Educational Explainer",
    "social_hook": "Social Hook",
    "case_study_brief": "Case Study Brief",
    "testimonial_angle": "Testimonial Angle",
}

CONTENT_TYPE_COLORS = {
    "educational_explainer": "#1565c0",
    "social_hook": "#7b1fa2",
    "case_study_brief": "#ef6c00",
    "testimonial_angle": "#2e7d32",
}

INTENT_COLORS = {
    "Educate": "#1565c0",
    "Empathize": "#7b1fa2",
    "Empower": "#2e7d32",
    "Activate": "#ef6c00",
}

FUNNEL_COLORS = {
    "Problem Aware": "#d32f2f",
    "Solution Aware": "#f57c00",
    "Service Aware": "#388e3c",
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
    """Return HTML for a colored badge pill."""
    hc = color.lstrip("#")
    r, g, b = int(hc[:2], 16), int(hc[2:4], 16), int(hc[4:6], 16)
    bg = f"rgba({r},{g},{b},0.12)"
    return (
        f'<span style="display:inline-block; padding:2px 10px; border-radius:12px; '
        f'font-size:0.78rem; font-weight:600; color:{color}; background:{bg}; '
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
    ct_color = CONTENT_TYPE_COLORS.get(content_type, "#757575")
    intent_color = INTENT_COLORS.get(content_intent, "#757575")
    funnel_color = FUNNEL_COLORS.get(funnel_hint, "#757575")
    status_color = "#2e7d32" if status == "approved" else "#f57c00"

    # Badge row
    badges_html = _badge(ct_label, ct_color)
    if content_intent:
        badges_html += _badge(content_intent, intent_color)
    if funnel_hint:
        badges_html += _badge(funnel_hint, funnel_color)
    badges_html += _badge(status.replace("_", " ").title(), status_color)
    if injury_type:
        badges_html += _badge(injury_type, "#546e7a")
    if quality is not None:
        q_color = "#388e3c" if quality >= 75 else "#f57c00" if quality >= 60 else "#d32f2f"
        badges_html += _badge(f"Q: {quality}", q_color)

    # Quotes HTML
    quotes_html = ""
    if key_quotes and isinstance(key_quotes, list):
        quotes_items = "".join(
            f'<li style="margin-bottom:6px; font-style:italic; color:{COLORS["text_secondary"]};">'
            f'"{_esc(q)}"</li>'
            for q in key_quotes[:3] if q
        )
        if quotes_items:
            quotes_html = (
                f'<div style="margin-top:10px;">'
                f'<div style="font-size:0.78rem; font-weight:600; color:{COLORS["text_secondary"]}; '
                f'margin-bottom:4px;">KEY QUOTES</div>'
                f'<ul style="margin:0; padding-left:18px; font-size:0.85rem;">{quotes_items}</ul>'
                f'</div>'
            )

    # Emotional arc HTML
    arc_html = ""
    if emotional_arc and isinstance(emotional_arc, dict):
        arc_parts = []
        for phase, label in [("opening", "Opening"), ("mid", "Turning Point"), ("closing", "Closing")]:
            val = emotional_arc.get(phase, "")
            if val:
                arc_parts.append(
                    f'<span style="font-size:0.78rem;"><strong>{label}:</strong> {_esc(str(val))}</span>'
                )
        if arc_parts:
            arc_html = (
                f'<div style="margin-top:10px; padding:8px 12px; background:rgba(0,0,0,0.03); '
                f'border-radius:8px; border-left:3px solid {ct_color};">'
                f'<div style="font-size:0.78rem; font-weight:600; color:{COLORS["text_secondary"]}; '
                f'margin-bottom:4px;">EMOTIONAL ARC</div>'
                + "<br>".join(arc_parts)
                + '</div>'
            )

    # Why this angle
    why_html = ""
    if why_this_angle:
        why_html = (
            f'<div style="margin-top:10px; font-size:0.85rem; color:{COLORS["text_secondary"]};">'
            f'<strong>Why this works:</strong> {_esc(why_this_angle)}</div>'
        )

    # Meta line
    meta_parts = [f"Created {created}"] if created else []
    if model:
        meta_parts.append(model.split("/")[-1])
    if row.get("api_cost") is not None:
        meta_parts.append(f"${float(row['api_cost']):.4f}")
    meta_html = (
        f'<div style="margin-top:8px; font-size:0.72rem; color:{COLORS["text_hint"]};">'
        + " &middot; ".join(meta_parts)
        + '</div>'
    ) if meta_parts else ""

    # Full card
    st.markdown(
        f'<div style="border:1px solid {BORDERS["color"]}; border-radius:{BORDERS["radius"]}; '
        f'padding:16px 20px; margin-bottom:12px; border-left:4px solid {ct_color}; '
        f'background:{COLORS["surface"]}; box-shadow:{SHADOWS["sm"]};">'
        f'<div style="margin-bottom:8px;">{badges_html}</div>'
        f'<div style="font-size:1.05rem; font-weight:700; color:{COLORS["text_primary"]}; '
        f'margin-bottom:6px;">{_esc(creative_angle)}</div>'
        f'<div style="font-size:0.88rem; color:{COLORS["text_secondary"]}; line-height:1.5;">'
        f'{_esc(call_summary)}</div>'
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
    st.info("No creative angles found. Run WF 20 manually from n8n to generate the first batch.")
else:
    # Summary metrics
    m_cols = st.columns(4)
    m_cols[0].metric("Total Angles", total)

    pending = sum(1 for r in filtered if r.get("status") == "pending_review")
    approved = sum(1 for r in filtered if r.get("status") == "approved")
    m_cols[1].metric("Pending Review", pending)
    m_cols[2].metric("Approved", approved)

    # Content type breakdown
    ct_counts = {}
    for r in filtered:
        ct = r.get("content_type", "other")
        ct_counts[ct] = ct_counts.get(ct, 0) + 1
    ct_summary = ", ".join(
        f"{CONTENT_TYPE_LABELS.get(k, k)}: {v}"
        for k, v in sorted(ct_counts.items(), key=lambda x: -x[1])
    )
    m_cols[3].metric("Types", len(ct_counts))
    st.caption(ct_summary)

    st.markdown("---")

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

    for row in filtered[start_idx:end_idx]:
        content = _parse_content(row)
        angle_card(row, content)
