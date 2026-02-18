"""Call Data Explorer — QA & review with expandable table of all extracted fields."""

import json
import streamlit as st
import pandas as pd
from utils.auth import check_password
from utils.theme import inject_theme, styled_divider, styled_header

if not check_password():
    st.stop()

inject_theme()

st.title("Call Data Explorer")
st.caption("Explore all extracted fields. Toggle column groups to customize your view.")

from components.filters import (
    case_type_filter, quality_range_filter, date_range_filter, language_filter,
)
from components.cards import call_detail_panel
from components.pagination import paginated_controls
from utils.queries import fetch_explorer_data, get_call_detail, get_transcript
from utils.export import download_csv
from utils.constants import COLUMN_GROUPS

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

# --- Pagination ---
offset, page = paginated_controls(total_label="rows", key="ex_page")

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

    # Format timestamps for readability
    if "analyzed_at" in display_df.columns:
        display_df["analyzed_at"] = pd.to_datetime(
            display_df["analyzed_at"], errors="coerce"
        ).dt.strftime("%b %d, %Y %I:%M %p")

    st.dataframe(
        display_df,
        use_container_width=True,
        height=500,
    )

    # Expandable row detail
    styled_divider()
    styled_header("Row Detail", subtitle="Select a call ID to view all fields.")

    if "source_transcript_id" in df.columns:
        selected_id = st.selectbox(
            "Select call",
            options=df["source_transcript_id"].tolist(),
            format_func=lambda x: (x or "unknown")[:16] + "...",
            key="ex_select_call",
        )

        if selected_id:
            with st.expander(f"Full detail: {selected_id[:16]}...", expanded=True):
                detail = get_call_detail(selected_id)
                if detail:
                    call_detail_panel(detail)

                    if st.button("Load transcript", key=f"ex_tx_{selected_id}"):
                        transcript = get_transcript(selected_id)
                        if transcript:
                            st.text_area(
                                "Full Transcript",
                                value=transcript,
                                height=400,
                                key=f"ex_tx_area_{selected_id}",
                            )
                        else:
                            st.caption("Transcript not available.")
                else:
                    st.warning("Could not load call details.")
