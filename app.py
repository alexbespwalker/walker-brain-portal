"""Walker Brain Portal — Entry point."""

import streamlit as st

st.set_page_config(
    page_title="Walker Brain",
    page_icon="\U0001F9E0",
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
    st.Page("app_pages/9_Angle_Bank.py",           title="Angle Bank",           icon="\U0001F4A1"),
    st.Page("app_pages/3_Quote_Bank.py",          title="Quote Bank",           icon="\U0001F4AC"),
    st.Page("app_pages/2_Call_Search.py",          title="Call Search",          icon="\U0001F50D"),
    st.Page("app_pages/6_Transcript_Search.py",    title="Transcript Search",    icon="\U0001F50E"),
    st.Page("app_pages/1_Today's_Highlights.py",   title="Today's Highlights",   icon="\U0001F4CA"),
    st.Page("app_pages/4_Tags.py",                 title="Signals & Objections", icon="\U0001F3F7"),
    st.Page("app_pages/8_Testimonial_Pipeline.py", title="Testimonial Pipeline", icon="\u2B50"),
    st.Page("app_pages/7_Call_Data_Explorer.py",   title="Data Explorer",        icon="\U0001F4CB"),
    st.Page("app_pages/5_System_Health.py",        title="Pipeline Status",      icon="\u2699"),
]

page = st.navigation(_pages)
page.run()
