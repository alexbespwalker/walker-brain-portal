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
        "icon": "&#128203;",
        "title": "Data Explorer",
        "desc": "Toggle 116 extracted fields, export CSV, and review raw data.",
        "page": "pages/3_Call_Data_Explorer.py",
    },
    {
        "icon": "&#128172;",
        "title": "Quote Bank",
        "desc": "Search and copy quotes for social posts, ads, and landing pages.",
        "page": "pages/4_Quote_Bank.py",
    },
    {
        "icon": "&#127991;&#65039;",
        "title": "Tags & Objections",
        "desc": "Browse tag taxonomy and track objection category trends.",
        "page": "pages/5_Tags.py",
    },
    {
        "icon": "&#9881;&#65039;",
        "title": "System Health",
        "desc": "Cost tracking, quality drift alerts, and pipeline metrics.",
        "page": "pages/6_System_Health.py",
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
