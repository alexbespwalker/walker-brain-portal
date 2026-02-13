"""Pagination component for Walker Brain Portal."""

import streamlit as st


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
        if st.button("Previous", key=f"{key}_prev", disabled=(page == 0)):
            st.session_state[key] = max(0, page - 1)
            st.rerun()
    with col2:
        st.caption(f"Page {page + 1}")
    with col3:
        if st.button("Next", key=f"{key}_next"):
            st.session_state[key] = page + 1
            st.rerun()

    offset = page * page_size
    return offset, page
