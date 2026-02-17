"""Walker Brain Portal — Entry point."""

import streamlit as st

st.set_page_config(
    page_title="Walker Brain",
    page_icon="brain",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.auth import check_password

if not check_password():
    st.stop()

st.title("Walker Brain Portal")
st.markdown(
    "AI-powered call analysis for Walker Advertising. "
    "Use the sidebar to navigate between pages."
)

st.markdown("---")

col1, col2, col3 = st.columns(3)
col1.page_link("pages/1_Today's_Highlights.py", label="Today's Highlights", icon="📊")
col2.page_link("pages/2_Quote_Bank.py", label="Quote Bank", icon="💬")
col3.page_link("pages/3_Call_Search.py", label="Call Search", icon="🔍")

col4, col5, col6 = st.columns(3)
col4.page_link("pages/4_Call_Data_Explorer.py", label="Call Data Explorer", icon="📋")
col5.page_link("pages/8_Tags.py", label="Tags & Objections", icon="🏷️")
col6.page_link("pages/9_System_Health.py", label="System Health", icon="⚙️")
