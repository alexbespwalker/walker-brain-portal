"""Call Search — Research tool for browsing and deep-diving into calls."""

import json
import streamlit as st
import pandas as pd
from utils.auth import check_password
from utils.theme import inject_theme, styled_header

if not check_password():
    st.stop()

inject_theme()

st.title(":mag: Call Search")
st.caption("Filter, browse, and deep-dive into analyzed calls.")

from components.filters import (
    text_search_filter, case_type_filter, quality_range_filter,
    date_range_filter, language_filter, emotional_tone_filter,
    has_quote_toggle, content_worthy_toggle,
)
from components.cards import call_card, call_detail_panel
from components.pagination import paginated_controls
from utils.queries import search_calls, get_call_detail, get_transcript, count_calls
from utils.export import download_csv

# --- Sidebar filters ---
with st.sidebar:
    st.header("Filters")
    text = text_search_filter(key="cs_text")
    case_types = case_type_filter(key="cs_case")
    min_q, max_q = quality_range_filter(key="cs_quality")
    start_date, end_date = date_range_filter(key="cs_date")
    languages = language_filter(key="cs_lang")
    tones = emotional_tone_filter(key="cs_tone")
    has_quote = has_quote_toggle(key="cs_quote")
    content_worthy = content_worthy_toggle(key="cs_content")

# --- Reset page when filters change ---
_fkey = f"{text}|{case_types}|{min_q}|{max_q}|{start_date}|{end_date}|{languages}|{tones}|{has_quote}|{content_worthy}"
if st.session_state.get("cs_page_filter_hash") != _fkey:
    st.session_state["cs_page"] = 0
    st.session_state["cs_page_filter_hash"] = _fkey

# --- Count + Pagination ---
total = count_calls(
    text_search=text, case_types=case_types, min_quality=min_q, max_quality=max_q,
    start_date=start_date, end_date=end_date, languages=languages, tones=tones,
    has_quote=has_quote, content_worthy=content_worthy,
)
offset, page = paginated_controls(total_label="calls", key="cs_page", total_count=total)

# --- Fetch results ---
with st.spinner("Searching calls..."):
    results = search_calls(
        text_search=text,
        case_types=case_types,
        min_quality=min_q,
        max_quality=max_q,
        start_date=start_date,
        end_date=end_date,
        languages=languages,
        tones=tones,
        has_quote=has_quote,
        content_worthy=content_worthy,
        limit=50,
        offset=offset,
    )

if not results:
    st.info("No calls found matching your filters.")
else:
    st.markdown(f"**{len(results)} calls** (page {page + 1})")

    # Export button
    df_export = pd.DataFrame(results)
    for col in ["suggested_tags"]:
        if col in df_export.columns:
            df_export[col] = df_export[col].apply(
                lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x
            )
    download_csv(df_export, filename="walker_brain_calls.csv")

    # Render each result
    for row in results:
        sid = row.get("source_transcript_id", "")
        call_card(row)

        with st.expander(f"Full Analysis \u2014 {row.get('case_type', '')} ({row.get('analyzed_at', '')[:10]})"):
            detail = get_call_detail(sid)
            if detail:
                styled_header("Summary")
                st.markdown(detail.get("summary", "\u2014"))

                if detail.get("key_quote"):
                    from html import escape as _esc
                    styled_header("Key Quote")
                    st.markdown(
                        f'<div class="wb-quote-card"><div class="wb-quote-text">&ldquo;{_esc(detail["key_quote"])}&rdquo;</div></div>',
                        unsafe_allow_html=True,
                    )

                call_detail_panel(detail)

                # Transcript (lazy-loaded)
                if st.button(f"Load transcript", key=f"tx_{sid}"):
                    transcript = get_transcript(sid)
                    if transcript:
                        st.text_area(
                            "Full Transcript",
                            value=transcript,
                            height=400,
                            key=f"tx_area_{sid}",
                        )
                    else:
                        st.caption("Transcript not available.")
            else:
                st.warning("Could not load call details.")
