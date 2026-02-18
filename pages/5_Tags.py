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

def _show_fallback_tags():
    """Mine tags from analysis_results when master_taxonomy is empty/missing."""
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
                    if isinstance(tag, str):
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1

        if tag_counts:
            from html import escape as _esc
            sorted_tags = sorted(tag_counts.items(), key=lambda x: -x[1])
            badges_html = (
                '<div style="display:flex; flex-wrap:wrap; gap:4px; max-width:100%;">'
                + "".join(
                    f'<span class="wb-badge wb-badge-info" style="margin:2px;'
                    f'{" font-size:0.8rem;" if count > 50 else ""}">'
                    f'{_esc(tag)} <b>{count}</b></span>'
                    for tag, count in sorted_tags[:50]
                )
                + '</div>'
            )
            st.markdown(badges_html, unsafe_allow_html=True)
        else:
            st.caption("No tag data available yet.")
    except Exception:
        st.caption("Tag data unavailable.")


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
            st.caption("Loading tags from analyzed calls...")
            _show_fallback_tags()
    except Exception:
        st.caption("Loading tags from analyzed calls...")
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
                    st.markdown("**Week-over-week changes:**")
                    for _, row in obj_df.iterrows():
                        this_w = row.get("freq_this_week", 0) or 0
                        last_w = row.get("freq_last_week", 0) or 0
                        delta = this_w - last_w
                        arrow = "+" if delta > 0 else ""
                        cat_label = row["obj_category"].replace("_", " ").title() if isinstance(row["obj_category"], str) else row["obj_category"]
                        st.caption(
                            f"  {cat_label}: {this_w} this week "
                            f"({arrow}{delta} vs last week)"
                        )
                else:
                    st.info("Baseline week \u2014 prior period not yet available for comparison.")
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
                        if isinstance(c, str) and c.strip() and c.lower() != "undefined":
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
