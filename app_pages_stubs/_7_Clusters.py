"""Clusters — Placeholder for call pattern discovery."""

import streamlit as st
from utils.auth import check_password
from utils.theme import inject_theme

if not check_password():
    st.stop()

inject_theme()

st.title("Call Clusters")
st.info(
    "Coming soon \u2014 monthly call pattern discovery will appear here "
    "when Workflow 50 is activated."
)

st.markdown("""
**What this page will show:**
- Semantic clusters of similar calls
- Common themes, quotes, and content opportunities per cluster
- Drill-down into cluster members

**Current status:** Embedding infrastructure ready (954+ calls have vectors).
Clustering workflow (WF 50) is deferred.
""")
