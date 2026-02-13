"""Tags — Tag taxonomy browser + objection category insights."""

import json
import streamlit as st
import pandas as pd
from utils.auth import check_password

if not check_password():
    st.stop()

st.title("Tags & Objection Insights")
st.caption("Browse the tag taxonomy and explore objection patterns.")

from utils.database import get_supabase, query_table
from components.charts import objection_bar

# --- Section 1: Tag Browser ---
st.markdown("### Tag Browser")

try:
    # Try to load from master_taxonomy if it exists
    taxonomy = query_table("master_taxonomy", order="tag_name")
    if taxonomy:
        # Build lookup of tag_id -> tag_name for parent resolution
        id_to_name: dict[int, str] = {}
        for t in taxonomy:
            tid = t.get("tag_id")
            if tid is not None:
                id_to_name[tid] = t.get("tag_name", f"Tag {tid}")

        # Group by parent_tag_id (integer FK)
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
                    st.caption(f"  {tag} — {count} uses")

        if orphans:
            st.markdown("**Top-level tags:**")
            for t in orphans:
                tag = t.get("tag_name", "")
                count = t.get("usage_count", 0)
                st.caption(f"  {tag} — {count} uses")
    else:
        st.info("No taxonomy data available yet. Tags will appear when WF 30 runs.")
except Exception:
    # master_taxonomy may not exist yet — show tags from analysis_results
    st.caption("Loading tags from analyzed calls...")

    try:
        client = get_supabase()
        rows = (
            client.table("analysis_results")
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
            sorted_tags = sorted(tag_counts.items(), key=lambda x: -x[1])
            for tag, count in sorted_tags[:50]:
                st.caption(f"{tag}: {count} calls")
        else:
            st.caption("No tags found.")
    except Exception:
        st.caption("Unable to load tag data.")


# --- Section 2: Objection Category Insights ---
st.markdown("---")
st.markdown("### Objection Category Insights")

try:
    # Try the v_objection_frequencies view first
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
        fig = objection_bar(obj_df)
        st.plotly_chart(fig, use_container_width=True)

        # Week-over-week trends
        if "freq_this_week" in obj_df.columns and "freq_last_week" in obj_df.columns:
            st.markdown("**Week-over-week changes:**")
            for _, row in obj_df.iterrows():
                this_w = row.get("freq_this_week", 0) or 0
                last_w = row.get("freq_last_week", 0) or 0
                delta = this_w - last_w
                arrow = "+" if delta > 0 else ""
                st.caption(
                    f"  {row['obj_category']}: {this_w} this week "
                    f"({arrow}{delta} vs last week)"
                )
    else:
        # Fallback: compute from analysis_results directly
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
                    if isinstance(c, str):
                        obj_counts[c] = obj_counts.get(c, 0) + 1

        if obj_counts:
            obj_df = pd.DataFrame(
                [{"obj_category": k, "frequency": v}
                 for k, v in obj_counts.items()]
            )
            fig = objection_bar(obj_df)
            st.plotly_chart(fig, use_container_width=True)

            # Top verbatim phrases per category
            st.markdown("**Top objection categories (7d):**")
            sorted_objs = sorted(obj_counts.items(), key=lambda x: -x[1])
            for cat, count in sorted_objs[:8]:
                st.caption(f"  {cat}: {count} calls")
        else:
            st.caption("No objection data available this week.")

except Exception as e:
    st.caption(f"Unable to load objection data.")
