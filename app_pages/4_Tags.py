"""Tags — Tag taxonomy browser + objection category insights."""

import json
import streamlit as st
import pandas as pd
from utils.auth import check_password
from utils.theme import inject_theme, styled_divider, styled_header

if not check_password():
    st.stop()

inject_theme()

st.title(":label: Tags & Objection Insights")
st.caption("Browse the tag taxonomy and explore objection patterns.")

from utils.database import get_supabase, query_table
from components.charts import objection_bar
from components.cards import call_card


def _get_tag_counts() -> dict[str, int]:
    """Mine tags from analysis_results. Returns {tag: count} sorted by count desc."""
    try:
        _client = get_supabase()
        rows = (
            _client.table("analysis_results")
            .select("suggested_tags")
            .not_.is_("suggested_tags", "null")
            .limit(1000)
            .execute()
            .data
        )
        tag_counts: dict[str, int] = {}
        for r in rows:
            tags = r.get("suggested_tags") or []
            if isinstance(tags, str):
                try:
                    tags = json.loads(tags)
                except (json.JSONDecodeError, TypeError):
                    tags = []
            if isinstance(tags, list):
                for tag in tags:
                    if isinstance(tag, str) and tag.strip():
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
        return tag_counts
    except Exception:
        return {}


def _show_fallback_tags():
    """Render interactive tag buttons from analysis_results when master_taxonomy is empty."""
    tag_counts = _get_tag_counts()

    if not tag_counts:
        st.caption("No tag data available yet.")
        return

    sorted_tags = sorted(tag_counts.items(), key=lambda x: -x[1])[:50]

    # Tag search input
    tag_search = st.text_input(
        "Search tags",
        key="tag_search_input",
        placeholder="e.g. slip, process, attorney...",
        label_visibility="collapsed",
    )
    if tag_search:
        sorted_tags = [(t, c) for t, c in sorted_tags if tag_search.lower() in t.lower()]
        if not sorted_tags:
            st.caption(f"No tags matching \"{tag_search}\".")
            return

    # Render clickable tag buttons in a column grid
    num_cols = 5
    tag_cols = st.columns(num_cols)
    for idx, (tag, count) in enumerate(sorted_tags):
        with tag_cols[idx % num_cols]:
            if st.button(f"{tag} ({count})", key=f"tag_btn_{tag}", use_container_width=True):
                st.session_state["tag_filter"] = tag

    # Show filtered results if a tag is selected
    active_tag = st.session_state.get("tag_filter")
    if active_tag:
        styled_divider()
        styled_header(f"Calls tagged: {active_tag}")
        if st.button("Clear filter", key="clear_tag_filter"):
            del st.session_state["tag_filter"]
            st.rerun()
        try:
            _client = get_supabase()
            tagged_rows = (
                _client.table("analysis_results")
                .select(
                    "source_transcript_id, case_type, quality_score, emotional_tone, "
                    "analyzed_at, key_quote, summary, suggested_tags"
                )
                .contains("suggested_tags", json.dumps([active_tag]))
                .order("quality_score", desc=True)
                .limit(20)
                .execute()
                .data
            )
            if tagged_rows:
                st.markdown(f"**{len(tagged_rows)} calls** with tag *{active_tag}*")
                for row in tagged_rows:
                    call_card(row)
            else:
                st.caption("No calls found with this tag.")
        except Exception:
            st.caption("Could not load tagged calls.")


# --- Section 1: Tag Browser ---
styled_header("Tag Browser")

with st.spinner("Loading tags..."):
    try:
        taxonomy = query_table("master_taxonomy", order="tag_name")
        if taxonomy:
            id_to_name: dict[int, str] = {}
            for t in taxonomy:
                tid = t.get("tag_id")
                if tid is not None:
                    id_to_name[tid] = t.get("tag_name", f"Tag {tid}")

            parents: dict[int, list] = {}
            orphans = []
            for t in taxonomy:
                parent_id = t.get("parent_tag_id")
                if parent_id is not None:
                    parents.setdefault(parent_id, []).append(t)
                else:
                    orphans.append(t)

            for parent_id, children in sorted(parents.items(), key=lambda x: id_to_name.get(x[0], "")):
                parent_name = id_to_name.get(parent_id, f"Category {parent_id}")
                with st.expander(f"{parent_name} ({len(children)} tags)"):
                    for child in children:
                        tag = child.get("tag_name", "")
                        count = child.get("usage_count", 0)
                        st.caption(f"  {tag} \u2014 {count} uses")

            if orphans:
                st.markdown("**Top-level tags:**")
                for t in orphans:
                    tag = t.get("tag_name", "")
                    count = t.get("usage_count", 0)
                    st.caption(f"  {tag} \u2014 {count} uses")
        else:
            _show_fallback_tags()
    except Exception:
        _show_fallback_tags()


# --- Section 2: Objection Category Insights ---
styled_divider()
styled_header("Objection Category Insights")

with st.spinner("Loading objection data..."):
    try:
        client = get_supabase()
        try:
            obj_data = (
                client.table("v_objection_frequencies")
                .select("*")
                .execute()
                .data
            )
        except Exception:
            obj_data = None

        if obj_data:
            obj_df = pd.DataFrame(obj_data)
            # Pre-filter junk categories before charting
            _junk = {"undefined", "none", "null", "n/a", ""}
            if "obj_category" in obj_df.columns:
                obj_df = obj_df[
                    obj_df["obj_category"].apply(
                        lambda x: isinstance(x, str) and x.strip().lower() not in _junk
                    )
                ].copy()
            try:
                fig = objection_bar(obj_df)
                st.plotly_chart(fig, use_container_width=True)
            except Exception:
                st.caption("Chart unavailable.")

            if "freq_this_week" in obj_df.columns and "freq_last_week" in obj_df.columns:
                total_this = sum((row.get("freq_this_week") or 0) for _, row in obj_df.iterrows())
                total_last = sum((row.get("freq_last_week") or 0) for _, row in obj_df.iterrows())
                has_baseline = total_last > 0 and total_last >= total_this * 0.10
                if has_baseline:
                    _skip = {"undefined", "none", "null", "n/a", ""}
                    st.markdown("**Week-over-week changes:**")
                    for _, row in obj_df.iterrows():
                        _cat_raw = row.get("obj_category")
                        if not isinstance(_cat_raw, str) or _cat_raw.strip().lower() in _skip:
                            continue
                        this_w = row.get("freq_this_week", 0) or 0
                        last_w = row.get("freq_last_week", 0) or 0
                        delta = this_w - last_w
                        arrow = "+" if delta > 0 else ""
                        cat_label = _cat_raw.replace("_", " ").title()
                        st.caption(
                            f"  {cat_label}: {this_w} this week "
                            f"({arrow}{delta} vs last week)"
                        )
                else:
                    st.caption("*Trend comparison collecting \u2014 check back next week once a baseline week of data is available.*")
        else:
            from datetime import datetime, timedelta
            cutoff_7d = (datetime.utcnow() - timedelta(days=7)).isoformat()

            rows = (
                client.table("analysis_results")
                .select("objection_categories")
                .not_.is_("objection_categories", "null")
                .gte("analyzed_at", cutoff_7d)
                .execute()
                .data
            )
            obj_counts: dict[str, int] = {}
            for r in rows:
                cats = r.get("objection_categories") or []
                if isinstance(cats, str):
                    try:
                        cats = json.loads(cats)
                    except (json.JSONDecodeError, TypeError):
                        cats = []
                if isinstance(cats, list):
                    for c in cats:
                        if isinstance(c, str) and c.strip() and c.lower() not in ("undefined", "none", "null", "n/a"):
                            obj_counts[c] = obj_counts.get(c, 0) + 1

            if obj_counts:
                obj_df = pd.DataFrame(
                    [{"obj_category": k, "frequency": v}
                     for k, v in obj_counts.items()]
                )
                try:
                    fig = objection_bar(obj_df)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception:
                    st.caption("Chart unavailable.")
            else:
                st.caption("No objection data available yet.")

    except Exception:
        st.caption("Objection data unavailable.")
