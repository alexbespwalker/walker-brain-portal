"""Design tokens, global CSS, and theming utilities for Walker Brain Portal."""

import streamlit as st

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------
COLORS = {
    "primary": "#1565c0",
    "primary_light": "#1e88e5",
    "primary_dark": "#0d47a1",
    "secondary": "#7b1fa2",
    "accent": "#00897b",
    "success": "#2e7d32",
    "warning": "#f57f17",
    "error": "#c62828",
    "info": "#0277bd",
    "neutral": {
        50: "#fafafa",
        100: "#f5f5f5",
        200: "#eeeeee",
        300: "#e0e0e0",
        400: "#bdbdbd",
        500: "#9e9e9e",
        600: "#757575",
        700: "#616161",
        800: "#424242",
        900: "#212121",
    },
    "background": "#ffffff",
    "surface": "#ffffff",
    "surface_variant": "#f8f9fa",
    "text_primary": "#212121",
    "text_secondary": "#616161",
    "text_hint": "#9e9e9e",
    "divider": "#e0e0e0",
    # Tints for card backgrounds (color + 08 alpha)
    "tint_primary": "#1565c008",
    "tint_success": "#2e7d3208",
    "tint_warning": "#f57f1708",
    "tint_error": "#c6282808",
}

# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------
TYPOGRAPHY = {
    "font_family": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    "font_family_mono": "'JetBrains Mono', 'Fira Code', monospace",
    "size": {
        "xs": "0.75rem",
        "sm": "0.8125rem",
        "base": "0.875rem",
        "md": "1rem",
        "lg": "1.125rem",
        "xl": "1.25rem",
        "2xl": "1.5rem",
        "3xl": "1.875rem",
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
# Shadows & Borders
# ---------------------------------------------------------------------------
SHADOWS = {
    "sm": "0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06)",
    "md": "0 4px 6px rgba(0,0,0,0.07), 0 2px 4px rgba(0,0,0,0.05)",
    "lg": "0 10px 15px rgba(0,0,0,0.07), 0 4px 6px rgba(0,0,0,0.04)",
}

BORDERS = {
    "radius_sm": "6px",
    "radius_md": "8px",
    "radius_lg": "12px",
    "radius_xl": "16px",
}

# ---------------------------------------------------------------------------
# Global CSS  (injected once per page via inject_theme())
# ---------------------------------------------------------------------------
_GOOGLE_FONTS_LINK = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">'
)

GLOBAL_CSS = f"""
<style>
/* --- Google Fonts --- */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* --- Base typography --- */
html, body, [class*="css"] {{
    font-family: {TYPOGRAPHY["font_family"]};
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
    border-color: {COLORS["neutral"][200]} !important;
}}

/* --- Metric cards --- */
div[data-testid="stMetric"] {{
    background: {COLORS["surface_variant"]};
    border-radius: {BORDERS["radius_md"]};
    padding: {SPACING["md"]} {SPACING["lg"]};
    box-shadow: {SHADOWS["sm"]};
}}
div[data-testid="stMetric"] label {{
    font-size: {TYPOGRAPHY["size"]["sm"]};
    color: {COLORS["text_secondary"]};
    font-weight: {TYPOGRAPHY["weight"]["medium"]};
    text-transform: uppercase;
    letter-spacing: 0.03em;
}}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
    font-weight: {TYPOGRAPHY["weight"]["bold"]};
    color: {COLORS["text_primary"]};
}}

/* --- Expanders --- */
details[data-testid="stExpander"] {{
    border: 1px solid {COLORS["neutral"][200]};
    border-radius: {BORDERS["radius_md"]};
    box-shadow: {SHADOWS["sm"]};
}}
details[data-testid="stExpander"] summary {{
    font-weight: {TYPOGRAPHY["weight"]["medium"]};
}}

/* --- Tabs --- */
button[data-baseweb="tab"] {{
    font-family: {TYPOGRAPHY["font_family"]};
    font-weight: {TYPOGRAPHY["weight"]["medium"]};
    font-size: {TYPOGRAPHY["size"]["sm"]};
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

/* --- Status badges --- */
.wb-badge {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: {TYPOGRAPHY["size"]["xs"]};
    font-weight: {TYPOGRAPHY["weight"]["semibold"]};
    letter-spacing: 0.02em;
    text-transform: uppercase;
}}
.wb-badge-success {{ background: #e8f5e9; color: #2e7d32; }}
.wb-badge-warning {{ background: #fff3e0; color: #e65100; }}
.wb-badge-error {{ background: #ffebee; color: #c62828; }}
.wb-badge-info {{ background: #e3f2fd; color: #0d47a1; }}

/* --- Soft horizontal divider --- */
.wb-divider {{
    border: none;
    height: 1px;
    background: linear-gradient(
        to right,
        transparent,
        {COLORS["neutral"][300]},
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
    border: 1px solid {COLORS["neutral"][200]};
    border-radius: {BORDERS["radius_md"]};
    padding: {SPACING["lg"]};
    box-shadow: {SHADOWS["sm"]};
    transition: box-shadow 0.15s ease;
}}
.wb-metric-card:hover {{
    box-shadow: {SHADOWS["md"]};
}}
.wb-metric-label {{
    font-size: {TYPOGRAPHY["size"]["xs"]};
    font-weight: {TYPOGRAPHY["weight"]["semibold"]};
    color: {COLORS["text_secondary"]};
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: {SPACING["xs"]};
}}
.wb-metric-value {{
    font-size: 1.75rem;
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
    padding: {SPACING["lg"]};
    box-shadow: {SHADOWS["sm"]};
    margin-bottom: {SPACING["md"]};
}}
.wb-quote-text {{
    font-size: {TYPOGRAPHY["size"]["base"]};
    font-style: italic;
    color: {COLORS["text_primary"]};
    line-height: {TYPOGRAPHY["line_height"]["relaxed"]};
    margin-bottom: {SPACING["sm"]};
}}
.wb-quote-meta {{
    font-size: {TYPOGRAPHY["size"]["xs"]};
    color: {COLORS["text_secondary"]};
}}

/* --- Nav card (landing page) --- */
.wb-nav-card {{
    background: {COLORS["surface"]};
    border: 1px solid {COLORS["neutral"][200]};
    border-radius: {BORDERS["radius_lg"]};
    padding: {SPACING["xl"]};
    box-shadow: {SHADOWS["sm"]};
    transition: box-shadow 0.15s ease, border-color 0.15s ease;
    text-align: center;
    min-height: 140px;
}}
.wb-nav-card:hover {{
    box-shadow: {SHADOWS["md"]};
    border-color: {COLORS["primary_light"]};
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
    font-size: {TYPOGRAPHY["size"]["xs"]};
    color: {COLORS["text_secondary"]};
    line-height: {TYPOGRAPHY["line_height"]["normal"]};
}}

/* --- Login card --- */
.wb-login-card {{
    max-width: 400px;
    margin: 80px auto;
    background: {COLORS["surface"]};
    border: 1px solid {COLORS["neutral"][200]};
    border-radius: {BORDERS["radius_lg"]};
    padding: {SPACING["3xl"]} {SPACING["2xl"]};
    box-shadow: {SHADOWS["lg"]};
    text-align: center;
}}
.wb-login-title {{
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
    border-radius: 20px;
    font-size: {TYPOGRAPHY["size"]["xs"]};
    font-weight: {TYPOGRAPHY["weight"]["semibold"]};
}}

/* --- Page title area --- */
h1 {{
    font-family: {TYPOGRAPHY["font_family"]} !important;
    font-weight: {TYPOGRAPHY["weight"]["bold"]} !important;
    letter-spacing: -0.02em !important;
    color: {COLORS["text_primary"]} !important;
}}

/* --- Code blocks (for copy-to-clipboard) --- */
code {{
    font-family: {TYPOGRAPHY["font_family_mono"]};
    font-size: {TYPOGRAPHY["size"]["sm"]};
}}

/* --- Progress bars (agent scores) --- */
div[data-testid="stProgress"] > div > div {{
    border-radius: 4px;
}}
</style>
"""

# ---------------------------------------------------------------------------
# Plotly template (shared across all charts)
# ---------------------------------------------------------------------------
PLOTLY_TEMPLATE = dict(
    font_family=TYPOGRAPHY["font_family"].split(",")[0].strip("'"),
    font_color=COLORS["text_secondary"],
    font_size=12,
    title_font_size=14,
    title_font_color=COLORS["text_primary"],
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(
        gridcolor=COLORS["neutral"][200],
        linecolor=COLORS["neutral"][300],
        zerolinecolor=COLORS["neutral"][300],
        title_font_size=12,
        tickfont_size=11,
    ),
    yaxis=dict(
        gridcolor=COLORS["neutral"][200],
        linecolor=COLORS["neutral"][300],
        zerolinecolor=COLORS["neutral"][300],
        title_font_size=12,
        tickfont_size=11,
    ),
    colorway=[
        COLORS["primary"], COLORS["accent"], COLORS["secondary"],
        COLORS["success"], COLORS["warning"], COLORS["error"],
        COLORS["info"], "#ff6f00", "#4527a0", "#00695c",
    ],
    hoverlabel=dict(
        bgcolor=COLORS["neutral"][800],
        font_size=12,
        font_family=TYPOGRAPHY["font_family"].split(",")[0].strip("'"),
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
