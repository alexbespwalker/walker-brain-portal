"""Clusters — Placeholder for call pattern discovery."""

import streamlit as st
from utils.auth import check_password

if not check_password():
    st.stop()

st.title("Call Clusters")
st.info(
    "Coming soon — monthly call pattern discovery will appear here "
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
