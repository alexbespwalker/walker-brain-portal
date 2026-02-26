"""Design tokens, global CSS, and theming utilities for Walker Brain Portal."""

import streamlit as st

# ---------------------------------------------------------------------------
# Color palette — "Dark Authority, Warm Signal"
# ---------------------------------------------------------------------------
COLORS = {
    "primary": "#D4A03C",
    "primary_light": "#E4B94E",
    "primary_dark": "#B8882E",
    "primary_muted": "#D4A03C1A",
    "secondary": "#6C5CE7",
    "accent": "#00B894",
    "success": "#00B894",
    "warning": "#FDCB6E",
    "error": "#E17055",
    "info": "#74B9FF",
    "background": "#0F1117",
    "surface": "#1A1D26",
    "surface_variant": "#232733",
    "surface_elevated": "#2A2E3B",
    "text_primary": "#F0F0F5",
    "text_secondary": "#9CA3B4",
    "text_hint": "#6B7280",
    "text_on_primary": "#0F1117",
    "divider": "#2A2E3B",
    "border": "#2A2E3B",
    # Tints for card backgrounds (subtle on dark)
    "tint_primary": "rgba(212, 160, 60, 0.06)",
    "tint_success": "rgba(0, 184, 148, 0.06)",
    "tint_warning": "rgba(253, 203, 110, 0.06)",
    "tint_error": "rgba(225, 112, 85, 0.06)",
    "tint_primary_strong": "rgba(212, 160, 60, 0.12)",
    "tint_primary_decorative": "rgba(212, 160, 60, 0.20)",
    "tint_purple": "rgba(108, 92, 231, 0.06)",
}

# ---------------------------------------------------------------------------
# Typography — DM Sans (body) + DM Serif Display (headlines/metrics)
# ---------------------------------------------------------------------------
TYPOGRAPHY = {
    "font_family": "'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    "font_family_display": "'DM Serif Display', Georgia, 'Times New Roman', serif",
    "font_family_mono": "'JetBrains Mono', 'Fira Code', monospace",
    "size": {
        "xs": "0.75rem",
        "sm": "0.8125rem",
        "base": "0.875rem",
        "md": "1rem",
        "lg": "1.125rem",
        "xl": "1.25rem",
        "2xl": "1.5rem",
        "3xl": "2.25rem",
    },
    "weight": {
        "normal": 400,
        "medium": 500,
        "semibold": 600,
        "bold": 700,
    },
    "line_height": {
        "tight": 1.25,
        "normal": 1.5,
        "relaxed": 1.75,
    },
    "letter_spacing": {
        "tight": "-0.02em",
        "normal": "0",
        "wide": "0.03em",
        "wider": "0.06em",
    },
}

# ---------------------------------------------------------------------------
# Spacing (4px grid)
# ---------------------------------------------------------------------------
SPACING = {
    "xs": "4px",
    "sm": "8px",
    "md": "12px",
    "lg": "16px",
    "xl": "24px",
    "2xl": "32px",
    "3xl": "48px",
}

# ---------------------------------------------------------------------------
# Shadows & Borders — higher opacity for dark backgrounds
# ---------------------------------------------------------------------------
SHADOWS = {
    "sm": "0 1px 3px rgba(0,0,0,0.3), 0 1px 2px rgba(0,0,0,0.2)",
    "md": "0 4px 6px rgba(0,0,0,0.35), 0 2px 4px rgba(0,0,0,0.25)",
    "lg": "0 10px 15px rgba(0,0,0,0.4), 0 4px 6px rgba(0,0,0,0.3)",
    "glow_gold": "0 0 20px rgba(212, 160, 60, 0.15)",
    "glow_purple": "0 0 20px rgba(108, 92, 231, 0.15)",
}

BORDERS = {
    "radius_sm": "8px",
    "radius_md": "12px",
    "radius_lg": "16px",
    "radius_xl": "20px",
    "radius_pill": "9999px",
}

# ---------------------------------------------------------------------------
# Global CSS  (injected once per page via inject_theme())
# ---------------------------------------------------------------------------
_GOOGLE_FONTS_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Serif+Display&display=swap" rel="stylesheet">'
)

GLOBAL_CSS = f"""
<style>
/* --- Google Fonts --- */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Serif+Display&display=swap');

/* --- Animated gold shimmer bar --- */
@keyframes goldShimmer {{
    0% {{ background-position: -200% center; }}
    100% {{ background-position: 200% center; }}
}}

/* --- Base typography & dark background --- */
html, body, [class*="css"] {{
    font-family: {TYPOGRAPHY["font_family"]};
    background-color: {COLORS["background"]};
    color: {COLORS["text_primary"]};
}}

/* --- Gold shimmer header bar --- */
.stApp::before {{
    content: "";
    display: block;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(
        90deg,
        {COLORS["primary_dark"]},
        {COLORS["primary"]},
        {COLORS["primary_light"]},
        {COLORS["primary"]},
        {COLORS["primary_dark"]}
    );
    background-size: 200% auto;
    animation: goldShimmer 4s linear infinite;
    z-index: 9999;
}}

/* --- Hide Streamlit chrome --- */
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
[data-testid="stToolbar"] {{display: none !important;}}
header[data-testid="stHeader"] {{
    background: transparent;
}}

/* --- Sidebar polish --- */
section[data-testid="stSidebar"] {{
    background: {COLORS["surface_variant"]};
    border-right: 1px solid {COLORS["divider"]};
}}
section[data-testid="stSidebar"] .stMarkdown h2 {{
    font-size: {TYPOGRAPHY["size"]["md"]};
    font-weight: {TYPOGRAPHY["weight"]["semibold"]};
    color: {COLORS["text_primary"]};
    margin-bottom: {SPACING["sm"]};
    letter-spacing: -0.01em;
}}

/* --- Card / container styling --- */
div[data-testid="stVerticalBlockBorderWrapper"] > div {{
    border-radius: {BORDERS["radius_md"]} !important;
    border-color: {COLORS["border"]} !important;
}}

/* --- Metric cards (native st.metric) --- */
div[data-testid="stMetric"] {{
    background: {COLORS["surface"]};
    border-radius: {BORDERS["radius_md"]};
    padding: {SPACING["md"]} {SPACING["lg"]};
    box-shadow: {SHADOWS["sm"]};
}}
div[data-testid="stMetric"] label {{
    font-size: {TYPOGRAPHY["size"]["sm"]};
    color: {COLORS["text_secondary"]};
    font-weight: {TYPOGRAPHY["weight"]["medium"]};
    text-transform: uppercase;
    letter-spacing: {TYPOGRAPHY["letter_spacing"]["wide"]};
}}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
    font-family: {TYPOGRAPHY["font_family_display"]};
    font-weight: {TYPOGRAPHY["weight"]["bold"]};
    color: {COLORS["text_primary"]};
}}

/* --- Expanders --- */
details[data-testid="stExpander"] {{
    border: 1px solid {COLORS["border"]};
    border-radius: {BORDERS["radius_md"]};
    box-shadow: {SHADOWS["sm"]};
    background: {COLORS["surface"]};
}}
details[data-testid="stExpander"] summary {{
    font-weight: {TYPOGRAPHY["weight"]["medium"]};
    color: {COLORS["text_primary"]};
}}

/* --- Tabs --- */
button[data-baseweb="tab"] {{
    font-family: {TYPOGRAPHY["font_family"]};
    font-weight: {TYPOGRAPHY["weight"]["medium"]};
    font-size: {TYPOGRAPHY["size"]["sm"]};
    color: {COLORS["text_secondary"]};
}}

/* --- Buttons --- */
button[data-testid="stBaseButton-primary"] {{
    border-radius: {BORDERS["radius_sm"]};
    font-weight: {TYPOGRAPHY["weight"]["semibold"]};
    font-size: {TYPOGRAPHY["size"]["sm"]};
    letter-spacing: 0.01em;
    box-shadow: {SHADOWS["sm"]};
    transition: box-shadow 0.15s ease;
}}

/* --- Data tables --- */
div[data-testid="stDataFrame"] {{
    border-radius: {BORDERS["radius_md"]};
    box-shadow: {SHADOWS["sm"]};
}}

/* --- Selectbox / multiselect / text input --- */
div[data-baseweb="select"] {{
    border-radius: {BORDERS["radius_sm"]} !important;
}}
input[data-testid="stTextInput"] {{
    border-radius: {BORDERS["radius_sm"]} !important;
}}

/* --- Status badges (WCAG AA 4.5:1 contrast on dark surfaces) --- */
.wb-badge {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: {BORDERS["radius_pill"]};
    font-size: {TYPOGRAPHY["size"]["xs"]};
    font-weight: {TYPOGRAPHY["weight"]["semibold"]};
    letter-spacing: {TYPOGRAPHY["letter_spacing"]["wide"]};
    text-transform: uppercase;
}}
.wb-badge-success {{ background: rgba(0, 184, 148, 0.15); color: #34EBC1; }}
.wb-badge-warning {{ background: rgba(253, 203, 110, 0.15); color: #FDE68A; }}
.wb-badge-error {{ background: rgba(225, 112, 85, 0.15); color: #F09080; }}
.wb-badge-info {{ background: rgba(116, 185, 255, 0.15); color: #93CBFF; }}

/* --- Soft horizontal divider --- */
.wb-divider {{
    border: none;
    height: 1px;
    background: linear-gradient(
        to right,
        transparent,
        {COLORS["border"]},
        transparent
    );
    margin: {SPACING["xl"]} 0;
}}

/* --- Section header --- */
.wb-section-header {{
    font-family: {TYPOGRAPHY["font_family"]};
    font-size: {TYPOGRAPHY["size"]["lg"]};
    font-weight: {TYPOGRAPHY["weight"]["semibold"]};
    color: {COLORS["text_primary"]};
    margin-top: {SPACING["xl"]};
    margin-bottom: {SPACING["md"]};
    padding-bottom: {SPACING["sm"]};
    border-bottom: 2px solid {COLORS["primary"]};
    display: inline-block;
    letter-spacing: -0.01em;
}}
.wb-section-subtitle {{
    font-size: {TYPOGRAPHY["size"]["sm"]};
    color: {COLORS["text_secondary"]};
    margin-top: {SPACING["xs"]};
    font-weight: {TYPOGRAPHY["weight"]["normal"]};
}}

/* --- Metric card (custom HTML) --- */
.wb-metric-card {{
    background: {COLORS["surface"]};
    border: 1px solid {COLORS["border"]};
    border-radius: {BORDERS["radius_md"]};
    padding: {SPACING["lg"]};
    box-shadow: {SHADOWS["sm"]};
    transition: box-shadow 0.2s ease;
}}
.wb-metric-card:hover {{
    box-shadow: {SHADOWS["md"]}, {SHADOWS["glow_gold"]};
}}
.wb-metric-label {{
    font-size: {TYPOGRAPHY["size"]["xs"]};
    font-weight: {TYPOGRAPHY["weight"]["semibold"]};
    color: {COLORS["text_secondary"]};
    margin-bottom: {SPACING["xs"]};
    white-space: nowrap;
    text-transform: uppercase;
    letter-spacing: {TYPOGRAPHY["letter_spacing"]["wide"]};
}}
.wb-metric-value {{
    font-family: {TYPOGRAPHY["font_family_display"]};
    font-size: clamp(1.25rem, 2.5vw, {TYPOGRAPHY["size"]["3xl"]});
    font-weight: {TYPOGRAPHY["weight"]["bold"]};
    line-height: {TYPOGRAPHY["line_height"]["tight"]};
    margin-bottom: 2px;
}}
.wb-metric-delta {{
    font-size: {TYPOGRAPHY["size"]["xs"]};
    margin-top: 2px;
}}

/* --- Quote card --- */
.wb-quote-card {{
    background: {COLORS["surface"]};
    border-left: 3px solid {COLORS["primary"]};
    border-radius: {BORDERS["radius_md"]};
    padding: {SPACING["2xl"]};
    box-shadow: {SHADOWS["sm"]};
    margin-bottom: {SPACING["md"]};
    position: relative;
}}
.wb-quote-card::before {{
    content: "\\201C";
    position: absolute;
    top: 12px;
    left: 16px;
    font-family: {TYPOGRAPHY["font_family_display"]};
    font-size: 3rem;
    color: {COLORS["tint_primary_decorative"]};
    line-height: 1;
    pointer-events: none;
}}

/* --- Badge pill row --- */
.wb-pill-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    align-items: center;
    margin-top: {SPACING["sm"]};
    margin-bottom: {SPACING["xs"]};
}}
.wb-quote-text {{
    font-size: {TYPOGRAPHY["size"]["base"]};
    font-style: italic;
    color: {COLORS["text_primary"]};
    line-height: {TYPOGRAPHY["line_height"]["relaxed"]};
    margin-bottom: {SPACING["sm"]};
    padding-left: 24px;
}}
.wb-quote-meta {{
    font-size: {TYPOGRAPHY["size"]["xs"]};
    color: {COLORS["text_secondary"]};
}}

/* --- Nav card (landing page) --- */
.wb-nav-card {{
    background: {COLORS["surface"]};
    border: 1px solid {COLORS["border"]};
    border-radius: {BORDERS["radius_lg"]};
    padding: {SPACING["xl"]};
    box-shadow: {SHADOWS["sm"]};
    transition: box-shadow 0.2s ease, border-color 0.2s ease;
    text-align: center;
    min-height: 140px;
}}
.wb-nav-card:hover {{
    box-shadow: {SHADOWS["md"]}, {SHADOWS["glow_gold"]};
    border-color: {COLORS["primary"]};
}}
.wb-nav-icon {{
    font-size: 2rem;
    margin-bottom: {SPACING["sm"]};
}}
.wb-nav-title {{
    font-size: {TYPOGRAPHY["size"]["md"]};
    font-weight: {TYPOGRAPHY["weight"]["semibold"]};
    color: {COLORS["text_primary"]};
    margin-bottom: {SPACING["xs"]};
}}
.wb-nav-desc {{
    font-size: {TYPOGRAPHY["size"]["sm"]};
    color: {COLORS["text_secondary"]};
    line-height: {TYPOGRAPHY["line_height"]["normal"]};
}}

/* --- Login card --- */
.wb-login-card {{
    max-width: 400px;
    margin: 48px auto 0 auto;
    background: {COLORS["surface"]};
    border: 1px solid {COLORS["border"]};
    border-radius: {BORDERS["radius_lg"]};
    padding: {SPACING["2xl"]} {SPACING["2xl"]} {SPACING["xl"]};
    box-shadow: {SHADOWS["lg"]}, {SHADOWS["glow_gold"]};
    text-align: center;
}}
.wb-login-title {{
    font-family: {TYPOGRAPHY["font_family_display"]};
    font-size: {TYPOGRAPHY["size"]["2xl"]};
    font-weight: {TYPOGRAPHY["weight"]["bold"]};
    color: {COLORS["text_primary"]};
    margin-bottom: {SPACING["xs"]};
}}
.wb-login-subtitle {{
    font-size: {TYPOGRAPHY["size"]["sm"]};
    color: {COLORS["text_secondary"]};
    margin-bottom: {SPACING["xl"]};
}}

/* --- Kanban column header --- */
.wb-kanban-header {{
    border-radius: {BORDERS["radius_sm"]};
    padding: {SPACING["sm"]} {SPACING["md"]};
    text-align: center;
    margin-bottom: {SPACING["sm"]};
    font-weight: {TYPOGRAPHY["weight"]["semibold"]};
    font-size: {TYPOGRAPHY["size"]["sm"]};
}}

/* --- Status pill --- */
.wb-status-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 12px;
    border-radius: {BORDERS["radius_pill"]};
    font-size: {TYPOGRAPHY["size"]["xs"]};
    font-weight: {TYPOGRAPHY["weight"]["semibold"]};
}}

/* --- Page title area --- */
h1 {{
    font-family: {TYPOGRAPHY["font_family_display"]} !important;
    font-weight: {TYPOGRAPHY["weight"]["bold"]} !important;
    letter-spacing: {TYPOGRAPHY["letter_spacing"]["tight"]} !important;
    color: {COLORS["text_primary"]} !important;
}}

/* --- Code blocks --- */
code {{
    font-family: {TYPOGRAPHY["font_family_mono"]};
    font-size: {TYPOGRAPHY["size"]["sm"]};
}}

/* --- Progress bars (agent scores) --- */
div[data-testid="stProgress"] > div > div {{
    border-radius: 4px;
}}

/* --- Data table horizontal scroll --- */
div[data-testid="stDataFrame"] {{
    overflow-x: auto !important;
}}

/* --- Code block overflow wrapping --- */
div[data-testid="stCodeBlock"] pre {{
    white-space: pre-wrap;
    word-wrap: break-word;
    max-height: 200px;
    overflow-y: auto;
}}

/* --- Disabled button styling (pagination) --- */
button[data-testid="stBaseButton-secondary"][disabled] {{
    opacity: 0.35;
    cursor: not-allowed;
}}

/* --- Reduce top padding on main content area --- */
.block-container {{
    padding-top: 2rem !important;
}}

/* --- Tab active indicator --- */
button[data-baseweb="tab"][aria-selected="true"] {{
    border-bottom: 3px solid {COLORS["primary"]} !important;
    font-weight: {TYPOGRAPHY["weight"]["semibold"]} !important;
    color: {COLORS["text_primary"]} !important;
}}

/* --- Sidebar nav link hover / active --- */
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] {{
    border-radius: 6px;
    transition: background-color 0.15s ease;
    border-left: 3px solid transparent;
}}
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:hover {{
    background-color: rgba(212, 160, 60, 0.06);
    border-left-color: rgba(212, 160, 60, 0.3);
}}
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"] {{
    background-color: rgba(212, 160, 60, 0.10);
    border-left-color: {COLORS["primary"]};
    font-weight: {TYPOGRAPHY["weight"]["semibold"]};
}}

/* --- Empty state (standardized across all pages) --- */
.wb-empty-state {{
    padding: {SPACING["2xl"]} {SPACING["xl"]};
    border: 1px dashed {COLORS["border"]};
    border-radius: {BORDERS["radius_md"]};
    background: {COLORS["surface"]};
    text-align: center;
    box-shadow: {SHADOWS["sm"]};
    margin-bottom: {SPACING["lg"]};
}}
.wb-empty-state-icon {{
    font-size: 1.8rem;
    margin-bottom: {SPACING["md"]};
    opacity: 0.4;
}}
.wb-empty-state-text {{
    font-size: {TYPOGRAPHY["size"]["base"]};
    color: {COLORS["text_hint"]};
    line-height: {TYPOGRAPHY["line_height"]["relaxed"]};
    max-width: 400px;
    margin: 0 auto;
}}
.wb-empty-state-text strong {{
    color: {COLORS["text_secondary"]};
}}

/* --- Angle card --- */
.wb-angle-card {{
    border: 1px solid {COLORS["border"]};
    border-radius: {BORDERS["radius_md"]};
    padding: {SPACING["lg"]} {SPACING["xl"]};
    margin-bottom: {SPACING["xs"]};
    background: {COLORS["surface"]};
    box-shadow: {SHADOWS["sm"]};
}}
.wb-angle-card:hover {{
    box-shadow: {SHADOWS["md"]};
}}
.wb-angle-badges {{
    margin-bottom: {SPACING["sm"]};
}}
.wb-angle-title {{
    font-size: 1.05rem;
    font-weight: {TYPOGRAPHY["weight"]["bold"]};
    color: {COLORS["text_primary"]};
    margin-bottom: 6px;
}}
.wb-angle-summary {{
    font-size: {TYPOGRAPHY["size"]["base"]};
    color: {COLORS["text_secondary"]};
    line-height: {TYPOGRAPHY["line_height"]["normal"]};
}}
.wb-angle-section-label {{
    font-size: {TYPOGRAPHY["size"]["xs"]};
    font-weight: {TYPOGRAPHY["weight"]["semibold"]};
    color: {COLORS["text_secondary"]};
    margin-bottom: {SPACING["xs"]};
    text-transform: uppercase;
    letter-spacing: {TYPOGRAPHY["letter_spacing"]["wide"]};
}}
.wb-angle-quotes {{
    margin-top: 10px;
}}
.wb-angle-quotes li {{
    margin-bottom: 6px;
    font-style: italic;
    color: {COLORS["text_secondary"]};
    font-size: {TYPOGRAPHY["size"]["base"]};
}}
.wb-angle-arc {{
    margin-top: 10px;
    padding: {SPACING["sm"]} {SPACING["md"]};
    background: {COLORS["surface_elevated"]};
    border-radius: {BORDERS["radius_sm"]};
    font-size: {TYPOGRAPHY["size"]["xs"]};
}}
.wb-angle-why {{
    margin-top: 10px;
    font-size: {TYPOGRAPHY["size"]["base"]};
    color: {COLORS["text_secondary"]};
}}
.wb-angle-meta {{
    margin-top: {SPACING["sm"]};
    font-size: {TYPOGRAPHY["size"]["xs"]};
    color: {COLORS["text_hint"]};
}}

/* --- NSM Banner --- */
.wb-nsm-banner {{
    display: flex;
    align-items: center;
    gap: {SPACING["md"]};
    padding: {SPACING["md"]} {SPACING["xl"]};
    background: linear-gradient(90deg, rgba(212,160,60,0.10) 0%, transparent 100%);
    border-left: 3px solid {COLORS["primary"]};
    border-radius: {BORDERS["radius_sm"]};
    margin-bottom: {SPACING["md"]};
}}
.wb-nsm-value {{
    font-family: {TYPOGRAPHY["font_family_display"]};
    font-size: 1.5rem;
    font-weight: {TYPOGRAPHY["weight"]["bold"]};
    color: {COLORS["primary"]};
}}
.wb-nsm-label {{
    font-size: {TYPOGRAPHY["size"]["sm"]};
    color: {COLORS["text_secondary"]};
    font-weight: {TYPOGRAPHY["weight"]["medium"]};
}}
.wb-nsm-billboard {{
    background: linear-gradient(135deg, {COLORS["surface"]} 0%, rgba(212,160,60,0.08) 100%);
    border: 1px solid rgba(212,160,60,0.25);
    border-left: 4px solid {COLORS["primary"]};
    border-radius: {BORDERS["radius_lg"]};
    padding: {SPACING["xl"]};
    box-shadow: {SHADOWS["md"]}, {SHADOWS["glow_gold"]};
}}
.wb-nsm-billboard-zero {{
    background: {COLORS["surface"]};
    border: 1px dashed {COLORS["border"]};
    border-left: 4px solid {COLORS["text_hint"]};
    border-radius: {BORDERS["radius_lg"]};
    padding: {SPACING["xl"]};
    box-shadow: {SHADOWS["sm"]};
}}

/* --- Feedback pill --- */
.wb-feedback-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px {SPACING["lg"]};
    border-radius: {BORDERS["radius_pill"]};
    font-size: {TYPOGRAPHY["size"]["xs"]};
    font-weight: {TYPOGRAPHY["weight"]["semibold"]};
    letter-spacing: {TYPOGRAPHY["letter_spacing"]["wide"]};
    text-transform: uppercase;
}}
.wb-feedback-comment {{
    margin: 6px 0 {SPACING["sm"]} 0;
    padding: {SPACING["sm"]} 14px;
    background: {COLORS["surface_elevated"]};
    border-left: 3px solid {COLORS["border"]};
    border-radius: 6px;
    font-size: {TYPOGRAPHY["size"]["sm"]};
    color: {COLORS["text_secondary"]};
    font-style: italic;
    line-height: {TYPOGRAPHY["line_height"]["normal"]};
}}

/* --- Target badge --- */
.wb-target-badge {{
    display: inline-block;
    padding: 3px {SPACING["md"]};
    border-radius: {BORDERS["radius_pill"]};
    font-size: {TYPOGRAPHY["size"]["xs"]};
    font-weight: {TYPOGRAPHY["weight"]["semibold"]};
    color: {COLORS["primary_light"]};
    background: rgba(212,160,60,0.12);
    letter-spacing: 0.04em;
    text-transform: uppercase;
}}

/* --- Sidebar wordmark --- */
.wb-sidebar-wordmark {{
    margin-bottom: {SPACING["lg"]};
    padding-bottom: {SPACING["md"]};
    border-bottom: 1px solid {COLORS["divider"]};
}}
.wb-sidebar-wordmark .wb-wm-walker {{
    font-family: {TYPOGRAPHY["font_family"]};
    font-weight: 700;
    font-size: 1.1rem;
    letter-spacing: {TYPOGRAPHY["letter_spacing"]["wider"]};
    color: {COLORS["text_primary"]};
    text-transform: uppercase;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.wb-sidebar-wordmark .wb-wm-brain {{
    font-family: {TYPOGRAPHY["font_family_display"]};
    font-style: italic;
    font-size: 1.1rem;
    color: {COLORS["primary"]};
    margin-left: 4px;
    white-space: nowrap;
}}
</style>
"""

# ---------------------------------------------------------------------------
# Plotly template (shared across all charts)
# ---------------------------------------------------------------------------
PLOTLY_TEMPLATE = dict(
    font_family="DM Sans",
    font_color=COLORS["text_secondary"],
    font_size=12,
    title_font_size=14,
    title_font_color=COLORS["text_primary"],
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(
        gridcolor=COLORS["border"],
        linecolor=COLORS["border"],
        zerolinecolor=COLORS["border"],
        title_font_size=12,
        tickfont_size=11,
    ),
    yaxis=dict(
        gridcolor=COLORS["border"],
        linecolor=COLORS["border"],
        zerolinecolor=COLORS["border"],
        title_font_size=12,
        tickfont_size=11,
    ),
    colorway=[
        COLORS["primary"], COLORS["secondary"], COLORS["accent"],
        COLORS["info"], COLORS["error"], COLORS["warning"],
        "#A29BFE", "#FD79A8", "#FFEAA7", "#55EFC4",
    ],
    hoverlabel=dict(
        bgcolor=COLORS["surface_variant"],
        font_size=12,
        font_family="DM Sans",
        font_color=COLORS["text_primary"],
    ),
    margin=dict(l=40, r=20, t=30, b=40),
)

# ---------------------------------------------------------------------------
# Theme injection (call once per page, before any content)
# ---------------------------------------------------------------------------
def inject_theme():
    """Inject global CSS + Google Fonts. Must be called on every page render.

    Streamlit rebuilds the entire HTML on each rerun, so the CSS must be
    injected every time — a session-state guard would cause the styles to
    disappear after the first interaction.
    """
    st.markdown(_GOOGLE_FONTS_LINK, unsafe_allow_html=True)
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Reusable styled components
# ---------------------------------------------------------------------------

def styled_divider():
    """Render a soft gradient divider (replaces st.markdown('---'))."""
    st.markdown('<hr class="wb-divider">', unsafe_allow_html=True)


def styled_header(text: str, subtitle: str | None = None):
    """Render a branded section header with optional subtitle."""
    html = f'<div class="wb-section-header">{text}</div>'
    if subtitle:
        html += f'<div class="wb-section-subtitle">{subtitle}</div>'
    st.markdown(html, unsafe_allow_html=True)


def inject_plotly_title_fix():
    """Hide Plotly 'undefined' chart titles via JS injection.

    Streamlit's HTML sanitizer strips CSS rules targeting SVG elements inside
    Plotly charts, so we use st.components.v1.html() to bypass the sanitizer
    and inject a MutationObserver that hides any .g-gtitle element whose text
    reads 'undefined'.  Call once per page that renders Plotly charts.
    """
    import streamlit.components.v1 as components
    components.html(
        """
        <script>
        (function() {
            function hideUndefinedTitles() {
                var titles = window.parent.document.querySelectorAll('.g-gtitle');
                for (var i = 0; i < titles.length; i++) {
                    var txt = titles[i].textContent || '';
                    if (txt.trim() === 'undefined') {
                        titles[i].style.display = 'none';
                    }
                }
            }
            // Run immediately and also observe for dynamic chart renders
            hideUndefinedTitles();
            var observer = new MutationObserver(function() { hideUndefinedTitles(); });
            observer.observe(window.parent.document.body, { childList: true, subtree: true });
            // Also run on a short delay to catch late Plotly renders
            setTimeout(hideUndefinedTitles, 1000);
            setTimeout(hideUndefinedTitles, 3000);
            setTimeout(hideUndefinedTitles, 5000);
        })();
        </script>
        """,
        height=0,
        scrolling=False,
    )


def empty_state(icon: str, message: str, detail: str = ""):
    """Render a standardized empty state with icon, message, and optional detail.

    Uses the .wb-empty-state CSS class for consistent styling across all pages.
    """
    detail_html = f"<strong>{detail}</strong>" if detail else ""
    st.markdown(
        f'<div class="wb-empty-state">'
        f'<div class="wb-empty-state-icon">{icon}</div>'
        f'<div class="wb-empty-state-text">{message} {detail_html}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
