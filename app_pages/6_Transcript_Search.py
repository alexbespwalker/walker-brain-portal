"""Transcript Search — Full-text keyword search across analyzed call transcripts."""

from html import escape as _esc
from datetime import datetime

import streamlit as st

from utils.auth import check_password
from utils.database import get_supabase
from utils.theme import inject_theme, styled_divider, styled_header

if not check_password():
    st.stop()

inject_theme()

st.title(":mag_right: Transcript Search")
st.caption("Search across analyzed call transcripts by keyword. Uses full-text indexing for fast results.")

# --- Search form (st.form prevents a query on every keystroke) ---
with st.form("transcript_search_form"):
    keyword = st.text_input(
        "Search keyword",
        placeholder='e.g. "surgery", "insurance denied", "hit and run"',
        help="Searches the full call transcript text for the keyword.",
    )
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        min_quality = st.slider(
            "Minimum quality score", min_value=0, max_value=100, value=0, step=5
        )
    with col2:
        max_results = st.selectbox("Max results", options=[10, 20, 50], index=1)
    with col3:
        st.markdown("<div style='padding-top:28px;'>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Search", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- Results ---
if submitted and keyword.strip():
    with st.spinner("Searching transcripts..."):
        client = get_supabase()
        results = client.rpc(
            "search_transcripts",
            {
                "query": keyword.strip(),
                "min_quality": min_quality,
                "max_results": max_results,
            },
        ).execute().data

    if not results:
        st.info(
            f'No transcripts found for "{keyword.strip()}". '
            "Try a different keyword or lower the minimum quality score."
        )
    else:
        count = len(results)
        st.markdown(
            f"**{count} result{'s' if count != 1 else ''}** for `{_esc(keyword.strip())}`"
        )
        styled_divider()

        for row in results:
            quality = row.get("quality_score") or 0
            case_type = row.get("case_type") or "Unknown"
            call_date = row.get("call_start_date", "")
            headline = row.get("headline") or ""
            # snippet comes from ts_headline and may contain <b> highlight tags — render as HTML
            snippet = row.get("snippet") or ""

            # Quality badge
            if quality >= 75:
                q_class = "wb-badge-success"
            elif quality >= 50:
                q_class = "wb-badge-warning"
            else:
                q_class = "wb-badge-error"

            # Format date
            date_str = ""
            if call_date:
                try:
                    dt = datetime.fromisoformat(call_date.replace("Z", "+00:00"))
                    date_str = dt.strftime("%b %d, %Y")
                except Exception:
                    date_str = str(call_date)[:10]

            date_html = (
                f'<span style="font-size:0.75rem;color:#757575;">{_esc(date_str)}</span>'
                if date_str
                else ""
            )
            headline_html = (
                f'<div style="font-weight:600;font-size:0.9375rem;margin:8px 0 4px;color:#212121;">'
                f"{headline}</div>"  # headline may contain <b> tags from ts_headline
                if headline
                else ""
            )
            snippet_html = (
                f'<div style="font-size:0.875rem;color:#424242;line-height:1.6;">'
                f"{snippet}</div>"  # snippet contains <b> highlight tags from ts_headline
                if snippet
                else '<div class="wb-quote-meta">No excerpt available.</div>'
            )

            st.markdown(
                f"""
                <div class="wb-quote-card" style="margin-bottom:12px;">
                    <div class="wb-pill-row">
                        <span class="wb-badge {q_class}">Quality: {quality}</span>
                        <span class="wb-badge wb-badge-info">{_esc(case_type)}</span>
                        {date_html}
                    </div>
                    {headline_html}
                    {snippet_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

elif submitted and not keyword.strip():
    st.warning("Please enter a keyword to search.")
