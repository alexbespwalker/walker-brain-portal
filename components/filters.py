"""Reusable sidebar filter components for Walker Brain Portal."""

import streamlit as st
from datetime import datetime, timedelta
from utils.queries import get_case_types, get_emotional_tones, get_outcomes, get_languages
from utils.constants import QUALITY_BANDS

# Darkened text colors for WCAG AA compliance on light backgrounds.
# Amber/orange bands need darker text to meet 4.5:1 contrast on 15% alpha bg.
_BAND_TEXT_COLORS = {
    "POOR": "#d32f2f",
    "NEEDS IMPROVEMENT": "#7a3d00",
    "ADEQUATE": "#7a5200",
    "STRONG": "#388e3c",
    "EXCEPTIONAL": "#1565c0",
}


def case_type_filter(key: str = "case_type") -> list[str] | None:
    """Multiselect for case types. Returns None if 'All' selected."""
    options = get_case_types()
    selected = st.multiselect("Case Type", options, key=key)
    return selected or None


def quality_range_filter(
    default_min: int = 0,
    default_max: int = 100,
    key: str = "quality",
) -> tuple[int, int]:
    """Slider for quality score range with band legend."""
    result = st.slider(
        "Quality Score",
        min_value=0,
        max_value=100,
        value=(default_min, default_max),
        key=key,
    )
    band_spans = []
    for name, (low, high, color) in QUALITY_BANDS.items():
        short = name if len(name) <= 12 else name[:12].rstrip() + "."
        hc = color.lstrip("#")
        r, g, b = int(hc[:2], 16), int(hc[2:4], 16), int(hc[4:6], 16)
        bg = f"rgba({r},{g},{b},0.15)"
        text_color = _BAND_TEXT_COLORS.get(name, color)
        band_spans.append(
            f'<span style="font-size:0.7rem; padding:1px 6px; border-radius:8px; '
            f'background:{bg}; color:{text_color};">{short} {low}-{high}</span>'
        )
    st.markdown(
        '<div style="display:flex; gap:4px; flex-wrap:wrap; margin-top:-8px;">'
        + " ".join(band_spans)
        + '</div>',
        unsafe_allow_html=True,
    )
    return result


def date_range_filter(
    default_days: int = 30,
    key: str = "date_range",
) -> tuple[str, str]:
    """Date picker for date range. Returns ISO strings."""
    col1, col2 = st.columns(2)
    default_start = datetime.utcnow().date() - timedelta(days=default_days)
    default_end = datetime.utcnow().date()
    with col1:
        start = st.date_input("From", value=default_start, key=f"{key}_start")
    with col2:
        end = st.date_input("To", value=default_end, key=f"{key}_end")
    return start.isoformat(), end.isoformat() + "T23:59:59"


def language_filter(key: str = "language") -> list[str] | None:
    """Multiselect for language."""
    options = get_languages()
    selected = st.multiselect("Language", options, key=key)
    return selected or None


def emotional_tone_filter(key: str = "tone") -> list[str] | None:
    """Multiselect for emotional tone. Queries live distinct values."""
    options = get_emotional_tones()
    selected = st.multiselect("Emotional Tone", options, key=key)
    return selected or None


def outcome_filter(key: str = "outcome") -> list[str] | None:
    """Multiselect for outcome."""
    options = get_outcomes()
    selected = st.multiselect("Outcome", options, key=key)
    return selected or None


def text_search_filter(key: str = "text_search") -> str | None:
    """Text input for searching summaries, quotes, topics."""
    text = st.text_input(
        "Search (summary, quote, topic)",
        key=key,
        placeholder="e.g. back pain, trucking, fee...",
    )
    return text if text else None


def testimonial_toggle(key: str = "testimonial_only") -> bool:
    """Checkbox to filter only testimonial candidates."""
    return st.checkbox("Testimonial candidates only", key=key)


def content_worthy_toggle(key: str = "content_worthy") -> bool:
    """Checkbox to filter only content-worthy calls."""
    return st.checkbox("Content-worthy only", key=key)


def has_quote_toggle(key: str = "has_quote") -> bool:
    """Checkbox to filter calls with quotes."""
    return st.checkbox("Has quote", key=key)


def clear_filters(key_prefix: str) -> None:
    """Render a 'Clear all filters' button that resets session state for the given prefix."""
    clear_key = f"clear_filters_{key_prefix}"
    if st.button("Clear all filters", key=clear_key, use_container_width=True):
        for k in list(st.session_state.keys()):
            if k.startswith(key_prefix) and k != clear_key:
                del st.session_state[k]
        st.rerun()
