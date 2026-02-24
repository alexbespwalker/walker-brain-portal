"""Call Data Explorer — QA & review with expandable table of all extracted fields."""

import json
import streamlit as st
import pandas as pd
from utils.auth import check_password
from utils.theme import inject_theme, styled_divider, styled_header

if not check_password():
    st.stop()

inject_theme()

st.title(":clipboard: Call Data Explorer")
st.caption("Explore all extracted fields. Toggle column groups to customize your view.")

from components.filters import (
    case_type_filter, quality_range_filter, date_range_filter, language_filter,
)
from components.cards import call_detail_panel, _render_chat_transcript
from components.pagination import paginated_controls
from utils.queries import fetch_explorer_data, get_call_detail, get_transcript, count_explorer_rows
from utils.export import download_csv
from utils.constants import COLUMN_GROUPS, humanize

# --- Sidebar ---
with st.sidebar:
    st.header("Filters")
    case_types = case_type_filter(key="ex_case")
    min_q, max_q = quality_range_filter(key="ex_quality")
    start_date, end_date = date_range_filter(key="ex_date")
    languages = language_filter(key="ex_lang")

    st.header("Column Groups")
    active_groups = {}
    for group_name in COLUMN_GROUPS:
        default_on = group_name == "Core"
        active_groups[group_name] = st.checkbox(
            group_name, value=default_on, key=f"cg_{group_name}"
        )

# Build column list from active groups
columns = []
for group_name, is_active in active_groups.items():
    if is_active:
        columns.extend(COLUMN_GROUPS[group_name])
# Deduplicate while preserving order
seen = set()
unique_columns = []
for c in columns:
    if c not in seen:
        seen.add(c)
        unique_columns.append(c)
columns = unique_columns

if not columns:
    st.warning("Select at least one column group.")
    st.stop()

# --- Reset page when filters change ---
_fkey = f"{case_types}|{min_q}|{max_q}|{start_date}|{end_date}|{languages}"
if st.session_state.get("ex_page_filter_hash") != _fkey:
    st.session_state["ex_page"] = 0
    st.session_state["ex_page_filter_hash"] = _fkey

# --- Count + Pagination ---
total = count_explorer_rows(
    case_types=case_types, min_quality=min_q, max_quality=max_q,
    start_date=start_date, end_date=end_date, languages=languages,
)
offset, page = paginated_controls(total_label="rows", key="ex_page", total_count=total)

# --- Fetch data ---
with st.spinner("Loading data..."):
    df = fetch_explorer_data(
        columns=columns,
        case_types=case_types,
        min_quality=min_q,
        max_quality=max_q,
        start_date=start_date,
        end_date=end_date,
        languages=languages,
        limit=50,
        offset=offset,
    )

if df.empty:
    st.info("No data found matching your filters.")
else:
    st.markdown(f"**{len(df)} rows** (page {page + 1})")

    # Warn about zero-quality rows
    if "quality_score" in df.columns:
        zero_quality = df[df["quality_score"] == 0]
        if not zero_quality.empty:
            st.info(f"{len(zero_quality)} rows have quality_score = 0 (voicemails / dropped calls)")

    # Export
    download_csv(df, filename="walker_brain_explorer.csv")

    # Render table with NULL handling
    display_df = df.copy()
    for col in display_df.columns:
        display_df[col] = display_df[col].apply(
            lambda x: (
                json.dumps(x, indent=1) if isinstance(x, (list, dict))
                else "\u2014" if x is None
                else x
            )
        )

    # Truncate source_transcript_id to 8 chars
    if "source_transcript_id" in display_df.columns:
        display_df["source_transcript_id"] = display_df["source_transcript_id"].apply(
            lambda x: (x[:8] + "\u2026") if isinstance(x, str) and len(x) > 8 else x
        )

    # Pretty-print quality_sub_scores as compact readable string
    if "quality_sub_scores" in display_df.columns:
        def _fmt_sub_scores(val):
            if val == "\u2014" or val is None:
                return "\u2014"
            try:
                d = json.loads(val) if isinstance(val, str) else val
            except (json.JSONDecodeError, TypeError):
                return val
            if not isinstance(d, dict):
                return val
            abbr = {"case_potential": "Case", "narrative_quality": "Narr",
                    "agent_performance": "Agent", "completeness": "Compl"}
            parts = []
            for k, label in abbr.items():
                v = d.get(k)
                if v is not None:
                    parts.append(f"{label}:{v}")
            return " | ".join(parts) if parts else val

        display_df["quality_sub_scores"] = display_df["quality_sub_scores"].apply(_fmt_sub_scores)

    # Format timestamps for readability
    if "analyzed_at" in display_df.columns:
        display_df["analyzed_at"] = pd.to_datetime(
            display_df["analyzed_at"], errors="coerce"
        ).dt.strftime("%b %d, %Y %I:%M %p")

    # Humanize column headers
    display_df = display_df.rename(columns=humanize)

    col_config = {}
    if "Quality Sub Scores" in display_df.columns:
        col_config["Quality Sub Scores"] = st.column_config.TextColumn(
            "Quality Sub-Scores", width="large",
        )
    st.dataframe(
        display_df,
        use_container_width=True,
        height=500,
        column_config=col_config,
    )

    # Expandable row detail
    styled_divider()
    styled_header("Row Detail", subtitle="Select a call ID to view all fields.")

    if "source_transcript_id" in df.columns:
        selected_id = st.selectbox(
            "Select call",
            options=df["source_transcript_id"].tolist(),
            format_func=lambda x: (x or "unknown")[:8] + "\u2026",
            key="ex_select_call",
        )

        if selected_id:
            # "Open in Call Search" navigation button
            if st.button("Open in Call Search", key=f"ex_nav_{selected_id}"):
                st.session_state["jump_to_call_id"] = selected_id
                st.switch_page("app_pages/2_Call_Search.py")

            with st.expander(f"Full detail: {selected_id[:8]}\u2026", expanded=True):
                detail = get_call_detail(selected_id)
                if detail:
                    call_detail_panel(detail)

                    if st.button("Load transcript", key=f"ex_tx_{selected_id}"):
                        transcript = get_transcript(selected_id)
                        if transcript:
                            _render_chat_transcript(transcript)
                            st.code(transcript, language=None)
                        else:
                            st.caption("Transcript not available.")
                else:
                    st.warning("Could not load call details.")
