"""Testimonial Pipeline — Track testimonial candidates through production."""

import streamlit as st
from utils.auth import check_password
from utils.theme import inject_theme, COLORS, SPACING, BORDERS, TYPOGRAPHY

if not check_password():
    st.stop()

inject_theme()

st.title(":star: Testimonial Pipeline")
st.caption("Track testimonial candidates from flagged through published.")

st.info("93 testimonials ready for review. Content generation pipeline launches next sprint.")

from utils.queries import get_testimonial_pipeline, update_testimonial_status
from utils.constants import TESTIMONIAL_STATUSES, TESTIMONIAL_STATUS_COLORS, TESTIMONIAL_TYPES
from components.cards import testimonial_card

# --- Sidebar filters ---
with st.sidebar:
    st.header("Filters")
    filter_type = st.selectbox(
        "Testimonial Type",
        options=["All"] + TESTIMONIAL_TYPES,
        key="tp_type",
    )
    filter_status = st.selectbox(
        "Status",
        options=["All"] + TESTIMONIAL_STATUSES,
        key="tp_status",
    )

# Status progression map (what status comes next)
NEXT_STATUS = {
    "flagged": "contacted",
    "contacted": "scheduled",
    "scheduled": "recorded",
    "recorded": "published",
}

# Active statuses for kanban
KANBAN_STATUSES = ["flagged", "contacted", "scheduled", "recorded", "published"]

# --- Fetch data ---
all_items = get_testimonial_pipeline(
    status=filter_status if filter_status != "All" else None,
    testimonial_type=filter_type if filter_type != "All" else None,
)

# Group by status
by_status: dict[str, list] = {s: [] for s in KANBAN_STATUSES}
declined_items = []
for item in all_items:
    s = item.get("status", "flagged")
    if s == "declined":
        declined_items.append(item)
    elif s in by_status:
        by_status[s].append(item)

# --- Kanban board ---
cols = st.columns(len(KANBAN_STATUSES))
for i, status in enumerate(KANBAN_STATUSES):
    items = by_status[status]
    color = TESTIMONIAL_STATUS_COLORS.get(status, COLORS["text_hint"])
    with cols[i]:
        st.markdown(
            f'<div class="wb-kanban-header" style="background:{color}20; color:{color};">'
            f'{status.title()} ({len(items)})</div>',
            unsafe_allow_html=True,
        )
        for item in items[:20]:
            sid = item.get("source_transcript_id", "")
            next_s = NEXT_STATUS.get(status)

            testimonial_card(item, next_status=next_s)

            # Decline button
            if status in ("flagged", "contacted", "scheduled"):
                st.text_input("Decline reason", key=f"decline_notes_{sid}", label_visibility="collapsed", placeholder="Decline reason (optional)")
                if st.button("Decline", key=f"decline_{sid}", type="secondary"):
                    notes = st.session_state.get(f"decline_notes_{sid}", "")
                    update_testimonial_status(sid, "declined", notes=notes)
                    st.rerun()

# --- Declined section ---
if declined_items:
    with st.expander(f"Declined ({len(declined_items)})"):
        for item in declined_items:
            sid = item.get("source_transcript_id", "")
            case_type = item.get("case_type", "")
            quality = item.get("quality_score")
            quote = item.get("key_quote", "")
            notes = item.get("notes", "")
            with st.container(border=True):
                st.caption(f"{case_type} | Quality: {quality}")
                if quote:
                    st.markdown(f'*"{quote[:80]}..."*')
                if notes:
                    st.caption(f"Notes: {notes}")
                if st.button("Restore to Flagged", key=f"restore_{sid}"):
                    update_testimonial_status(sid, "flagged")
                    st.rerun()
