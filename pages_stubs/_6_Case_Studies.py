"""Case Studies — Placeholder for AI-generated case study drafts."""

import streamlit as st
from utils.auth import check_password
from utils.theme import inject_theme, styled_divider, styled_header

if not check_password():
    st.stop()

inject_theme()

st.title("Case Studies")
st.info(
    "Coming soon \u2014 AI-generated case studies will appear here "
    "when Workflow 20 is activated."
)

st.markdown("""
**What this page will show:**
- AI-generated case study drafts from high-quality calls (quality >= 70)
- Review & approve workflow
- Export as Word document or Markdown

**Current status:** Workflow 20 is deferred pending frontend completion.
Use **Quote Bank** to find content-worthy calls in the meantime.
""")

# Preview: top 10 content-flagged calls as potential case studies
styled_divider()
styled_header("Potential Case Studies", subtitle="Calls flagged as content-worthy by the AI")

from utils.database import get_supabase

try:
    client = get_supabase()
    rows = (
        client.table("analysis_results")
        .select("source_transcript_id, case_type, quality_score, key_quote, analyzed_at")
        .eq("content_generation_flag", True)
        .not_.is_("key_quote", "null")
        .order("quality_score", desc=True)
        .limit(10)
        .execute()
        .data
    )
    if rows:
        for row in rows:
            date = row.get("analyzed_at", "")[:10] if row.get("analyzed_at") else ""
            with st.container(border=True):
                cols = st.columns([2, 1, 1])
                cols[0].markdown(f"**{row.get('case_type', '')}**")
                cols[1].markdown(f"Quality: **{row.get('quality_score')}**")
                cols[2].caption(date)
                if row.get("key_quote"):
                    st.markdown(f'> *"{row["key_quote"][:200]}"*')
    else:
        st.info("No content-worthy calls found yet.")
except Exception:
    st.caption("Unable to load preview data.")
