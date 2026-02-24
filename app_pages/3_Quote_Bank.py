"""Quote Bank — Find and copy quotes for campaigns."""

import io
import pandas as pd
import streamlit as st
from utils.auth import check_password
from utils.theme import inject_theme

if not check_password():
    st.stop()

inject_theme()

st.title(":speech_balloon: Quote Bank")

from components.filters import (
    emotional_tone_filter, case_type_filter, quality_range_filter,
    language_filter, date_range_filter, testimonial_toggle, clear_filters,
)
from components.cards import quote_card
from components.pagination import paginated_controls
from utils.queries import fetch_quotes, count_quotes, get_last_updated
from utils.export import download_csv, generate_word_doc, format_quote_for_clipboard

# --- Sidebar filters ---
with st.sidebar:
    st.header("Filters")
    _lu = get_last_updated()
    if _lu:
        st.caption(f"Updated: {_lu}")
    test_only = testimonial_toggle(key="qb_testimonial")
    tones = emotional_tone_filter(key="qb_tone")
    case_types = case_type_filter(key="qb_case")
    min_q, max_q = quality_range_filter(default_min=0, default_max=100, key="qb_quality")
    languages = language_filter(key="qb_lang")
    start_date, end_date = date_range_filter(key="qb_date")
    from utils.theme import styled_divider
    styled_divider()
    clear_filters("qb")

# --- Reset page when filters change ---
_fkey = f"{test_only}|{tones}|{case_types}|{min_q}|{max_q}|{languages}|{start_date}|{end_date}"
if st.session_state.get("qb_page_filter_hash") != _fkey:
    st.session_state["qb_page"] = 0
    st.session_state["qb_page_filter_hash"] = _fkey

# --- Count + Pagination ---
total = count_quotes(
    min_quality=min_q, max_quality=max_q, case_types=case_types,
    tones=tones, languages=languages, testimonial_only=test_only,
    start_date=str(start_date) if start_date else None,
    end_date=str(end_date) if end_date else None,
)
offset, page = paginated_controls(total_label="quotes", key="qb_page", total_count=total)

# --- Fetch quotes ---
with st.spinner("Loading quotes..."):
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
    st.info("No quotes found matching your filters.")
else:
    # --- Header row: count + export controls ---
    sel_count = sum(
        1 for row in quotes
        if st.session_state.get(f"qb_sel_{row.get('source_transcript_id', '')}", False)
    )
    sel_rows = [
        row for row in quotes
        if st.session_state.get(f"qb_sel_{row.get('source_transcript_id', '')}", False)
    ]

    hdr_cols = st.columns([3, 1, 1])
    hdr_cols[0].markdown(f"**{len(quotes)} quotes** (page {page + 1})")

    # Word doc export — selected or all visible
    _export_rows = sel_rows if sel_rows else quotes
    _export_label = f"Word ({sel_count} selected)" if sel_rows else f"Word ({len(quotes)} visible)"
    try:
        from datetime import datetime as _dt
        _doc_title = f"Quote Export — {_dt.now().strftime('%b %d, %Y')}"
        _blocks = []
        for _r in _export_rows:
            _q = _r.get("key_quote", "")
            if _q:
                _blocks.append({
                    "heading": f"{_r.get('case_type', '')} — {(_r.get('analyzed_at') or '')[:10]}",
                    "body": format_quote_for_clipboard(
                        _q, _r.get("case_type"), _r.get("emotional_tone"),
                        _r.get("quality_score"), (_r.get("analyzed_at") or "")[:10],
                    ),
                })
        if _blocks:
            with hdr_cols[1]:
                st.download_button(
                    label=_export_label,
                    data=generate_word_doc(_doc_title, _blocks),
                    file_name="quotes_export.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
    except Exception:
        pass

    # CSV export
    _csv_rows = sel_rows if sel_rows else quotes
    _csv_label = f"CSV ({sel_count} selected)" if sel_rows else "CSV"
    with hdr_cols[2]:
        _csv_df = pd.DataFrame(_csv_rows)
        _csv_buf = io.StringIO()
        _csv_df.to_csv(_csv_buf, index=False)
        st.download_button(
            label=_csv_label,
            data=_csv_buf.getvalue(),
            file_name="quotes_export.csv",
            mime="text/csv",
            use_container_width=True,
        )

    if sel_count == 0:
        st.caption("Check boxes to select specific quotes for export.")

    # --- Render quote cards with selection checkboxes ---
    for row in quotes:
        sid = row.get("source_transcript_id", "")
        chk_col, card_col = st.columns([0.05, 0.95])
        with chk_col:
            st.checkbox("", key=f"qb_sel_{sid}", label_visibility="collapsed")
        with card_col:
            quote_card(row, show_copy=False)
