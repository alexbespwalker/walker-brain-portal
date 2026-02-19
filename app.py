"""Walker Brain Portal — Entry point."""

import streamlit as st

st.set_page_config(
    page_title="Walker Brain",
    page_icon="brain",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.auth import check_password
from utils.theme import inject_theme, styled_divider, COLORS, TYPOGRAPHY, SPACING, SHADOWS, BORDERS
from utils.queries import get_pipeline_stats

inject_theme()

if not check_password():
    st.stop()

# --- Hero section ---
st.markdown(
    f"""
    <div style="
        padding: {SPACING["3xl"]} {SPACING["2xl"]};
        text-align: center;
        margin-bottom: {SPACING["xl"]};
    ">
        <div style="font-size: 2.5rem; margin-bottom: {SPACING["sm"]};">&#129504;</div>
        <h1 style="
            font-size: {TYPOGRAPHY["size"]["3xl"]};
            font-weight: {TYPOGRAPHY["weight"]["bold"]};
            margin-bottom: {SPACING["sm"]};
            letter-spacing: -0.02em;
        ">Walker Brain</h1>
        <p style="
            font-size: {TYPOGRAPHY["size"]["md"]};
            color: {COLORS["text_secondary"]};
            max-width: 480px;
            margin: 0 auto;
            line-height: {TYPOGRAPHY["line_height"]["relaxed"]};
        ">AI-powered call analysis for Walker Advertising.<br>
        600+ legal intake calls analyzed daily.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Stats billboard ---
try:
    _stats = get_pipeline_stats()
    if _stats and _stats.get("total", 0) > 0:
        from datetime import datetime
        _since = ""
        if _stats.get("since"):
            try:
                _d = datetime.strptime(_stats["since"][:10], "%Y-%m-%d")
                _since = f"{_d.strftime('%b')} {_d.day}, {_d.year}"
            except Exception:
                _since = _stats["since"][:10]
        _dot_color = COLORS["success"] if _stats.get("active") else COLORS["error"]
        _status_text = "Pipeline active" if _stats.get("active") else "Pipeline paused"
        _total = f"{_stats['total']:,}"
        st.markdown(
            f'<div style="display:flex;gap:20px;justify-content:center;'
            f'margin:-8px auto 24px;flex-wrap:wrap;max-width:600px;">'
            f'<span style="font-size:0.9rem;color:{COLORS["text_secondary"]};">'
            f'<strong style="color:{COLORS["text_primary"]};">{_total}</strong> calls analyzed</span>'
            f'<span style="color:{COLORS["text_hint"]};">·</span>'
            f'<span style="font-size:0.9rem;color:{COLORS["text_secondary"]};">Since '
            f'<strong style="color:{COLORS["text_primary"]};">{_since}</strong></span>'
            f'<span style="color:{COLORS["text_hint"]};">·</span>'
            f'<span style="font-size:0.9rem;color:{_dot_color};">&#9679; {_status_text}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
except Exception:
    pass

# --- Navigation cards ---
NAV_ITEMS = [
    {
        "icon": "&#128202;",
        "title": "Today's Highlights",
        "desc": "Curated quotes, trending topics, and weekly metrics at a glance.",
        "page": "pages/1_Today's_Highlights.py",
    },
    {
        "icon": "&#128269;",
        "title": "Call Search",
        "desc": "Filter, browse, and deep-dive into analyzed call transcripts.",
        "page": "pages/2_Call_Search.py",
    },
    {
        "icon": "&#128172;",
        "title": "Quote Bank",
        "desc": "Search, select, and export quotes for social posts, ads, and landing pages.",
        "page": "pages/3_Quote_Bank.py",
    },
    {
        "icon": "&#127991;&#65039;",
        "title": "Tags & Objections",
        "desc": "Browse tag taxonomy and track objection category trends.",
        "page": "pages/4_Tags.py",
    },
    {
        "icon": "&#9881;&#65039;",
        "title": "System Health",
        "desc": "Cost tracking, quality drift alerts, and pipeline metrics.",
        "page": "pages/5_System_Health.py",
    },
    {
        "icon": "&#128203;",
        "title": "Data Explorer",
        "desc": "Toggle 116 extracted fields, export CSV, and review raw data.",
        "page": "pages/7_Call_Data_Explorer.py",
    },
]

cols = st.columns(3)
for i, item in enumerate(NAV_ITEMS):
    with cols[i % 3]:
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="wb-nav-card" style="border:none; box-shadow:none;">
                    <div class="wb-nav-icon">{item["icon"]}</div>
                    <div class="wb-nav-desc">{item["desc"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.page_link(item["page"], label=f"{item['title']} \u2192", use_container_width=True)
