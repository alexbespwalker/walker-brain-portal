"""Email/password authentication for Walker Brain Portal (Invoca pattern)."""

from __future__ import annotations

import streamlit as st

from utils.theme import inject_theme, COLORS, TYPOGRAPHY, SPACING, SHADOWS, BORDERS
from utils.db import authenticate_user, create_session, validate_session, delete_session, register_user


def check_password() -> bool:
    """Authenticate via DB-backed email/password with session persistence.

    Flow:
    1. session_state["authenticated"] — same-tab fast path
    2. query_params["_session"] — cross-refresh persistence via DB
    3. Login form — email + password
    """
    # 1. Already authenticated this tab
    if st.session_state.get("authenticated"):
        return True

    # 2. Session token in URL — validate against DB
    session_token = st.query_params.get("_session")
    if session_token:
        user = validate_session(session_token)
        if user:
            st.session_state["authenticated"] = True
            st.session_state["user_email"] = user["user_email"]
            st.session_state["user_display_name"] = user.get("user_display_name") or user["user_email"]
            st.session_state["user_is_admin"] = user.get("user_is_admin", False)
            st.session_state["session_token"] = session_token
            return True
        else:
            # Expired/invalid token — clear it
            del st.query_params["_session"]

    # 3. Show login form
    inject_theme()

    st.markdown(
        f"""
        <div class="wb-login-card">
            <div style="font-size: 2rem; margin-bottom: {SPACING["sm"]};">&#129504;</div>
            <div class="wb-login-title">Walker Brain</div>
            <div class="wb-login-subtitle">Sign in with your company email</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, center, _ = st.columns([1, 1.2, 1])
    with center:
        sign_in_tab, create_tab = st.tabs(["Sign in", "Create account"])

        with sign_in_tab:
            email = st.text_input(
                "Email", key="login_email",
                placeholder="you@walkeradvertising.com",
                label_visibility="collapsed",
            )
            password = st.text_input(
                "Password", type="password", key="login_password",
                placeholder="Password",
                label_visibility="collapsed",
            )
            if st.button("Sign in", type="primary", use_container_width=True):
                if not email or not password:
                    st.error("Enter both email and password.")
                else:
                    user = authenticate_user(email.strip(), password)
                    if user:
                        display = user.get("user_display_name") or user["user_email"]
                        token = create_session(user["user_id"], display)
                        st.session_state["authenticated"] = True
                        st.session_state["user_email"] = user["user_email"]
                        st.session_state["user_display_name"] = display
                        st.session_state["user_is_admin"] = user.get("user_is_admin", False)
                        st.session_state["session_token"] = token
                        st.query_params["_session"] = token
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")

        with create_tab:
            reg_email = st.text_input(
                "Email", key="reg_email",
                placeholder="you@walkeradvertising.com",
                label_visibility="collapsed",
            )
            reg_name = st.text_input(
                "Display name", key="reg_name",
                placeholder="Display name",
                label_visibility="collapsed",
            )
            reg_password = st.text_input(
                "Password", type="password", key="reg_password",
                placeholder="Password",
                label_visibility="collapsed",
            )
            reg_confirm = st.text_input(
                "Confirm password", type="password", key="reg_confirm",
                placeholder="Confirm password",
                label_visibility="collapsed",
            )
            if st.button("Create account", type="primary", use_container_width=True):
                if not reg_email or not reg_name or not reg_password or not reg_confirm:
                    st.error("All fields are required.")
                elif reg_password != reg_confirm:
                    st.error("Passwords do not match.")
                else:
                    try:
                        new_user = register_user(reg_email.strip(), reg_password, reg_name.strip())
                        if new_user:
                            # Auto-login after registration
                            user = authenticate_user(reg_email.strip(), reg_password)
                            if user:
                                display = user.get("user_display_name") or user["user_email"]
                                token = create_session(user["user_id"], display)
                                st.session_state["authenticated"] = True
                                st.session_state["user_email"] = user["user_email"]
                                st.session_state["user_display_name"] = display
                                st.session_state["user_is_admin"] = user.get("user_is_admin", False)
                                st.session_state["session_token"] = token
                                st.query_params["_session"] = token
                                st.rerun()
                            else:
                                st.success("Account created! Please sign in.")
                        else:
                            st.error("Registration failed. Please try again.")
                    except Exception as e:
                        err = str(e)
                        if "unique" in err.lower() or "duplicate" in err.lower() or "already exists" in err.lower():
                            st.error("Account already exists. Sign in instead.")
                        elif "walkeradvertising.com" in err:
                            st.error("Registration restricted to @walkeradvertising.com emails.")
                        else:
                            st.error("Registration failed. Please try again or contact an administrator.")

    st.stop()
    return False


def get_current_user() -> str | None:
    """Return the logged-in user's email, or None."""
    return st.session_state.get("user_email")


def get_current_display_name() -> str:
    """Return display name, falling back to email."""
    return st.session_state.get("user_display_name") or st.session_state.get("user_email", "")


def check_admin() -> bool:
    """Return True if the current user has admin role."""
    return st.session_state.get("user_is_admin", False)


def logout() -> None:
    """Delete DB session and clear all auth state."""
    token = st.session_state.get("session_token")
    if token:
        try:
            delete_session(token)
        except Exception:
            pass  # best-effort cleanup

    for key in ("authenticated", "user_email", "user_display_name", "user_is_admin", "session_token"):
        st.session_state.pop(key, None)
    if "_session" in st.query_params:
        del st.query_params["_session"]
    st.rerun()
