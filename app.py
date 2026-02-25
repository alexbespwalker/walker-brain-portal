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
st.session_state.setdefault("user_email", None)
st.session_state.setdefault("user_display_name", None)
st.session_state.setdefault("user_is_admin", False)
st.session_state.setdefault("session_token", None)

# --- Build page list ---
# Nav order: Angle Bank → Quote Bank → Call Search → Transcript Search
#            → Today's Highlights → Signals & Objections → Testimonial Pipeline
#            → Data Explorer → Pipeline Status (admin-gated within page)
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

# --- Sidebar user label + logout (only when authenticated) ---
if st.session_state.get("authenticated"):
    with st.sidebar:
        from utils.auth import get_current_display_name, logout
        from utils.theme import COLORS, TYPOGRAPHY, SPACING

        import html as _html
        display_name = _html.escape(get_current_display_name())
        st.markdown(
            f'<div style="padding:{SPACING["sm"]} {SPACING["md"]}; '
            f'background:{COLORS["surface"]}; border:1px solid {COLORS["border"]}; '
            f'border-radius:8px; margin-bottom:{SPACING["md"]}; '
            f'font-size:{TYPOGRAPHY["size"]["sm"]}; color:{COLORS["text_secondary"]};">'
            f'Signed in as <strong style="color:{COLORS["text_primary"]};">{display_name}</strong>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if st.button("Sign out", key="sidebar_logout", use_container_width=True):
            logout()

page.run()
