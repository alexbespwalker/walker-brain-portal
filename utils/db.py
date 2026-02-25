"""Auth DB helpers — thin wrappers around Walker Brain auth RPCs."""

from __future__ import annotations

from typing import Any

from utils.database import get_supabase


def authenticate_user(email: str, password: str) -> dict[str, Any] | None:
    """Authenticate via wb_authenticate_user RPC. Returns user dict or None."""
    client = get_supabase()
    resp = client.rpc(
        "wb_authenticate_user",
        {"p_email": email, "p_password": password},
    ).execute()
    rows = resp.data or []
    return rows[0] if rows else None


def create_session(user_id: int, user_name: str) -> str:
    """Create a DB-backed session token (7-day TTL)."""
    client = get_supabase()
    resp = client.rpc(
        "wb_create_session",
        {"p_user_id": user_id, "p_user_name": user_name},
    ).execute()
    return resp.data


def validate_session(token: str) -> dict[str, Any] | None:
    """Validate a session token. Returns user dict or None."""
    client = get_supabase()
    resp = client.rpc(
        "wb_validate_session",
        {"p_token": token},
    ).execute()
    rows = resp.data or []
    return rows[0] if rows else None


def delete_session(token: str) -> None:
    """Delete a session (logout)."""
    client = get_supabase()
    client.rpc(
        "wb_delete_session",
        {"p_token": token},
    ).execute()
