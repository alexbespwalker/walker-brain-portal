"""Pagination component for Walker Brain Portal."""

import streamlit as st
from utils.theme import COLORS, TYPOGRAPHY


def paginated_controls(
    total_label: str = "results",
    page_size: int = 50,
    key: str = "page",
) -> tuple[int, int]:
    """Render pagination controls. Returns (offset, page_number).

    Place this BEFORE the results loop and after the count header.
    """
    page = st.session_state.get(key, 0)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("Previous", key=f"{key}_prev", disabled=(page == 0), use_container_width=True):
            st.session_state[key] = max(0, page - 1)
            st.rerun()
    with col2:
        st.markdown(
            f'<div style="text-align:center; padding:6px 0; '
            f'font-size:{TYPOGRAPHY["size"]["sm"]}; color:{COLORS["text_secondary"]}; '
            f'font-weight:{TYPOGRAPHY["weight"]["medium"]};">'
            f'Page {page + 1}</div>',
            unsafe_allow_html=True,
        )
    with col3:
        if st.button("Next", key=f"{key}_next", use_container_width=True):
            st.session_state[key] = page + 1
            st.rerun()

    offset = page * page_size
    return offset, page
