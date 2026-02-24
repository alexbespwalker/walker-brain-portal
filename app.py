"""Walker Brain Portal — Entry point."""

import streamlit as st

st.set_page_config(
    page_title="Walker Brain",
    page_icon="brain",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.theme import inject_theme

inject_theme()

# Initialize auth state before any navigation runs
st.session_state.setdefault("authenticated", False)
st.session_state.setdefault("admin_authenticated", False)

# --- Build page list ---
# Nav order: Quote Bank → Call Search → Transcript Search → Today's Highlights
#            → Signals & Objections → Testimonial Pipeline → Data Explorer
#            → Pipeline Status (admin-gated within page)
_pages = [
    st.Page("app_pages/9_Angle_Bank.py",           title="Angle Bank",           icon=":bulb:"),
    st.Page("app_pages/3_Quote_Bank.py",          title="Quote Bank",           icon=":speech_balloon:"),
    st.Page("app_pages/2_Call_Search.py",          title="Call Search",          icon=":mag:"),
    st.Page("app_pages/6_Transcript_Search.py",    title="Transcript Search",    icon=":mag_right:"),
    st.Page("app_pages/1_Today's_Highlights.py",   title="Today's Highlights",   icon=":bar_chart:"),
    st.Page("app_pages/4_Tags.py",                 title="Signals & Objections", icon=":label:"),
    st.Page("app_pages/8_Testimonial_Pipeline.py", title="Testimonial Pipeline", icon=":star:"),
    st.Page("app_pages/7_Call_Data_Explorer.py",   title="Data Explorer",        icon=":clipboard:"),
    st.Page("app_pages/5_System_Health.py",        title="Pipeline Status",      icon=":gear:"),
]

page = st.navigation(_pages)
page.run()
