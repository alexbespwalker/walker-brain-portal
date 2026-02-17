"""Quote Bank — Find and copy quotes for campaigns."""

import streamlit as st
from utils.auth import check_password

if not check_password():
    st.stop()

st.title("Quote Bank")
st.caption("Find quotes for social posts, ad copy, and landing pages.")

from components.filters import (
    emotional_tone_filter, case_type_filter, quality_range_filter,
    language_filter, date_range_filter, testimonial_toggle,
)
from components.cards import quote_card
from components.pagination import paginated_controls
from utils.queries import fetch_quotes

# --- Sidebar filters ---
with st.sidebar:
    st.header("Filters")
    tones = emotional_tone_filter(key="qb_tone")
    case_types = case_type_filter(key="qb_case")
    min_q, max_q = quality_range_filter(default_min=0, default_max=100, key="qb_quality")
    languages = language_filter(key="qb_lang")
    start_date, end_date = date_range_filter(key="qb_date")
    test_only = testimonial_toggle(key="qb_testimonial")

# --- Pagination ---
offset, page = paginated_controls(total_label="quotes", key="qb_page")

# --- Fetch quotes ---
quotes = fetch_quotes(
    min_quality=min_q,
    max_quality=max_q,
    case_types=case_types,
    tones=tones,
    languages=languages,
    testimonial_only=test_only,
    start_date=str(start_date) if start_date else None,
    end_date=str(end_date) if end_date else None,
    limit=50,
    offset=offset,
)

if not quotes:
    st.info("No quotes found matching your filters. Try widening your search.")
else:
    st.markdown(f"**Showing {len(quotes)} quotes** (page {page + 1})")
    for row in quotes:
        quote_card(row, show_copy=True)
