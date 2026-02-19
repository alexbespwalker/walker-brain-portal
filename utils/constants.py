"""Constants for Walker Brain Portal."""

QUALITY_BANDS = {
    "POOR": (0, 29, "#d32f2f"),
    "NEEDS IMPROVEMENT": (30, 59, "#f57c00"),
    "ADEQUATE": (60, 74, "#f9a825"),
    "STRONG": (75, 89, "#388e3c"),
    "EXCEPTIONAL": (90, 100, "#1565c0"),
}

CASE_TYPE_COLORS = {
    "auto-accident": "#1f77b4",
    "MVA": "#1f77b4",
    "slip-and-fall": "#ff7f0e",
    "workers-comp": "#2ca02c",
    "premises-liability": "#d62728",
    "dog-bite": "#9467bd",
    "medical-malpractice": "#8c564b",
    "product-liability": "#e377c2",
    "wrongful-death": "#7f7f7f",
    "other": "#bcbd22",
}

OBJECTION_CATEGORIES = [
    "cost_anxiety",
    "risk_avoidance",
    "authority_doubt",
    "timing_resistance",
    "immigration_status",
    "prior_bad_experience",
    "trust_legitimacy",
    "process_confusion",
]

TESTIMONIAL_STATUSES = [
    "flagged",
    "contacted",
    "scheduled",
    "recorded",
    "published",
    "declined",
]

TESTIMONIAL_STATUS_COLORS = {
    "flagged": "#9e9e9e",
    "contacted": "#42a5f5",
    "scheduled": "#ffa726",
    "recorded": "#66bb6a",
    "published": "#1565c0",
    "declined": "#ef5350",
}

TESTIMONIAL_TYPES = [
    "not_suitable",
    "high_value_long_form",
    "quantity_short_form",
]

# Column groups for Call Data Explorer
COLUMN_GROUPS = {
    "Core": [
        "source_transcript_id", "case_type", "quality_score",
        "emotional_tone", "outcome", "analyzed_at",
    ],
    "Quality Sub-Scores": [
        "quality_sub_scores",
    ],
    "Agent Scores": [
        "agent_empathy_score", "agent_education_quality",
        "agent_objection_handling", "agent_closing_effectiveness",
    ],
    "Case Assessment": [
        "liability_clarity", "injury_severity",
        "documentation_quality", "estimated_case_value_low",
        "estimated_case_value_high",
    ],
    "Objection Taxonomy": [
        "objection_categories", "mid_call_dropout_moment",
        "conversion_driver", "drop_off_reason",
        "agent_intervention_that_worked", "moment_that_closed",
    ],
    "Language & Culture": [
        "reading_level_estimate", "communication_style",
        "spanglish_detected", "colloquialisms", "cultural_markers",
        "family_references", "verbatim_customer_language",
    ],
    "CX Intelligence": [
        "questions_repeated_by_attorney", "attorney_used_prior_info",
        "handoff_wait_time_mentioned", "attorney_sentiment",
        "attorney_rejection_reason", "testimonial_candidate",
        "testimonial_type", "review_request_eligible",
    ],
    "Content Mining": [
        "common_questions_asked", "misunderstandings",
        "education_calming_moment", "process_confusion_points",
        "other_brands_mentioned", "competitive_comparison",
        "category_confusion", "ad_or_creative_referenced",
        "ad_promise_vs_reality_mismatch", "repeated_questions_from_caller",
    ],
    "Emotional Arc": [
        "opening_emotional_state", "mid_call_emotional_shift",
        "end_state_emotion",
    ],
    "Metadata": [
        "prompt_version_used", "confidence_score", "validation_passed",
        "api_cost", "input_tokens", "output_tokens", "analysis_type",
    ],
}


TESTIMONIAL_TYPE_LABELS = {
    "not_suitable": "Not Suitable",
    "high_value_long_form": "High Value \u2014 Long Form",
    "quantity_short_form": "Short Form",
    "video_candidate": "Video Candidate",
}


TONE_BADGE_MAP: dict[str, str] = {
    # Red — distressed/negative
    "distressed": "wb-badge-error",
    "angry": "wb-badge-error",
    "fearful": "wb-badge-error",
    "frustrated": "wb-badge-error",
    # Amber — uncertain/mixed
    "anxious": "wb-badge-warning",
    "confused": "wb-badge-warning",
    "skeptical": "wb-badge-warning",
    # Green — positive
    "hopeful": "wb-badge-success",
    "grateful": "wb-badge-success",
    "relieved": "wb-badge-success",
    # Blue — neutral
    "neutral": "wb-badge-info",
    "calm": "wb-badge-info",
    "neutral_calm": "wb-badge-info",
}

# Falsy sentinel values to filter out of list displays
_FALSY_SENTINELS = {False, None, "", "none", "null", "n/a", "false", "None", "N/A"}


def humanize(snake_str: str) -> str:
    """Convert snake_case to Title Case. 'snake_case' → 'Snake Case'."""
    return snake_str.replace("_", " ").title()


def format_case_value(
    low: float | int | None,
    high: float | int | None,
    category: str | None = None,
) -> str:
    """Format estimated case value range as '$200k – $500k (High)'. Returns '—' if both None."""
    if low is None and high is None:
        return "\u2014"
    parts = []
    try:
        if low is not None:
            v = float(low)
            parts.append(f"${v / 1000:.0f}k" if v >= 1000 else f"${v:,.0f}")
        else:
            parts.append("?")
        if high is not None:
            v = float(high)
            parts.append(f"${v / 1000:.0f}k" if v >= 1000 else f"${v:,.0f}")
    except (TypeError, ValueError):
        return "\u2014"
    result = " \u2013 ".join(parts)
    if category:
        result += f" ({category})"
    return result


def get_badge_class(tone: str | None) -> str:
    """Return the CSS class for an emotional tone badge pill."""
    if not tone:
        return "wb-badge-info"
    return TONE_BADGE_MAP.get(tone.lower().strip(), "wb-badge-info")


def is_falsy_sentinel(value) -> bool:
    """Return True if value is a falsy sentinel that should be hidden from display."""
    if value in _FALSY_SENTINELS:
        return True
    if isinstance(value, str) and value.strip().lower() in _FALSY_SENTINELS:
        return True
    return False


def clean_language(val: str | None) -> str:
    """Strip wrapping single-quotes and whitespace from language values."""
    if not val:
        return ""
    return val.strip("'").strip()


def quality_band(score: int | float | str | None) -> tuple[str, str]:
    """Return (band_name, color) for a quality score."""
    if score is None:
        return ("N/A", "#9e9e9e")
    try:
        score = float(score)
    except (TypeError, ValueError):
        return ("N/A", "#9e9e9e")
    for band_name, (low, high, color) in QUALITY_BANDS.items():
        if low <= score <= high:
            return (band_name, color)
    return ("N/A", "#9e9e9e")
