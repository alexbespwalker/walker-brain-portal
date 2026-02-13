"""Database connection and query utilities for Walker Brain Portal."""

import streamlit as st
from supabase import create_client, Client
import pandas as pd


@st.cache_resource
def get_supabase() -> Client:
    """Singleton Supabase client for the Analysis DB."""
    return create_client(
        st.secrets["database"]["url"],
        st.secrets["database"]["key"],
    )


@st.cache_data(ttl=300)
def query_table(
    table: str,
    select: str = "*",
    filters: dict | None = None,
    order: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> list[dict]:
    """Query a table via PostgREST. Returns list of row dicts.

    Args:
        table: Table or view name.
        select: Comma-separated column list.
        filters: Dict of {column: value} for .eq() filters,
                 or {column: ("operator", value)} for other operators.
        order: Column to order by, prefix with '-' for DESC.
        limit: Max rows.
        offset: Row offset for pagination.
    """
    client = get_supabase()
    q = client.table(table).select(select)

    if filters:
        for col, val in filters.items():
            if isinstance(val, tuple):
                op, v = val
                if op == "gte":
                    q = q.gte(col, v)
                elif op == "lte":
                    q = q.lte(col, v)
                elif op == "gt":
                    q = q.gt(col, v)
                elif op == "lt":
                    q = q.lt(col, v)
                elif op == "neq":
                    q = q.neq(col, v)
                elif op == "like":
                    q = q.like(col, v)
                elif op == "ilike":
                    q = q.ilike(col, v)
                elif op == "in":
                    q = q.in_(col, v)
                elif op == "not.is":
                    q = q.not_.is_(col, v)
                elif op == "is":
                    q = q.is_(col, v)
            else:
                q = q.eq(col, val)

    if order:
        if order.startswith("-"):
            q = q.order(order[1:], desc=True)
        else:
            q = q.order(order)

    if offset is not None:
        q = q.range(offset, offset + (limit or 50) - 1)
    elif limit is not None:
        q = q.limit(limit)

    return q.execute().data


@st.cache_data(ttl=300)
def run_rpc(function_name: str, params: dict | None = None) -> list[dict]:
    """Call a Supabase RPC function."""
    client = get_supabase()
    return client.rpc(function_name, params or {}).execute().data


def query_df(
    table: str,
    select: str = "*",
    filters: dict | None = None,
    order: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
) -> pd.DataFrame:
    """Query a table and return as DataFrame."""
    rows = query_table(table, select, filters, order, limit, offset)
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def upsert_row(table: str, data: dict, on_conflict: str | None = None) -> dict:
    """Insert or update a row. Not cached (write operation)."""
    client = get_supabase()
    if on_conflict:
        q = client.table(table).upsert(data, on_conflict=on_conflict)
    else:
        q = client.table(table).upsert(data)
    return q.execute().data


def update_row(table: str, data: dict, match: dict) -> dict:
    """Update rows matching the given filters. Not cached (write operation)."""
    client = get_supabase()
    q = client.table(table).update(data)
    for col, val in match.items():
        q = q.eq(col, val)
    return q.execute().data


@st.cache_data(ttl=3600)
def get_distinct_values(table: str, column: str) -> list[str]:
    """Get distinct non-null values for a column. Cached 1 hour."""
    client = get_supabase()
    rows = (
        client.table(table)
        .select(column)
        .not_.is_(column, "null")
        .execute()
        .data
    )
    return sorted(set(row[column] for row in rows if row.get(column)))
