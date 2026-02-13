"""Simple password authentication for Walker Brain Portal."""

import streamlit as st


def check_password() -> bool:
    """Show password gate and return True if authenticated."""
    if st.session_state.get("authenticated"):
        return True

    st.title("Walker Brain Portal")
    st.markdown("Enter the portal password to continue.")

    password = st.text_input("Password", type="password", key="password_input")
    if st.button("Log in", type="primary"):
        if password == st.secrets["auth"]["password"]:
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
        if admin_pw == st.secrets["auth"].get("admin_password", ""):
            st.session_state["admin_authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect admin password.")
    return False
