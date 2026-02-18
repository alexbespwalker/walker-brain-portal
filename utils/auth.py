"""Simple password authentication for Walker Brain Portal."""

import streamlit as st
from utils.theme import inject_theme, COLORS, TYPOGRAPHY, SPACING, SHADOWS, BORDERS


def check_password() -> bool:
    """Show branded password gate and return True if authenticated."""
    if st.session_state.get("authenticated"):
        return True

    inject_theme()

    st.markdown(
        f"""
        <div class="wb-login-card">
            <div style="font-size: 2rem; margin-bottom: {SPACING["sm"]};">&#129504;</div>
            <div class="wb-login-title">Walker Brain</div>
            <div class="wb-login-subtitle">Enter the portal password to continue.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Center the form inputs with columns — narrower to visually connect to card
    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        password = st.text_input("Password", type="password", key="password_input", label_visibility="collapsed", placeholder="Password")
        if st.button("Log in", type="primary", use_container_width=True):
            try:
                configured = st.secrets["auth"]["password"]
            except KeyError:
                st.error("Portal password not configured. Contact administrator.")
                return False
            if not configured:
                st.error("Portal password not configured. Contact administrator.")
            elif password == configured:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect password.")
    return False


def check_admin() -> bool:
    """Check if user has entered admin password. Returns True if admin."""
    if st.session_state.get("admin_authenticated"):
        return True

    admin_pw = st.text_input("Admin password", type="password", key="admin_pw")
    if st.button("Authenticate as admin"):
        try:
            configured = st.secrets["auth"].get("admin_password", "")
        except KeyError:
            st.error("Admin login is not configured.")
            return False
        if not configured or configured == "__DISABLED__":
            st.error("Admin login is not configured.")
        elif admin_pw == configured:
            st.session_state["admin_authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect admin password.")
    return False
