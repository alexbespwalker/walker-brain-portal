"""Constants for Walker Brain Portal."""

QUALITY_BANDS = {
    "POOR": (0, 29, "#d32f2f"),
    "NEEDS IMPROVEMENT": (30, 59, "#f57c00"),
    "ADEQUATE": (60, 74, "#fbc02d"),
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
    "Objection Taxonomy (10A)": [
        "objection_categories", "mid_call_dropout_moment",
        "conversion_driver", "drop_off_reason",
        "agent_intervention_that_worked", "moment_that_closed",
    ],
    "Language & Culture (10B)": [
        "reading_level_estimate", "communication_style",
        "spanglish_detected", "colloquialisms", "cultural_markers",
        "family_references", "verbatim_customer_language",
    ],
    "CX Intelligence (10C)": [
        "questions_repeated_by_attorney", "attorney_used_prior_info",
        "handoff_wait_time_mentioned", "attorney_sentiment",
        "attorney_rejection_reason", "testimonial_candidate",
        "testimonial_type", "review_request_eligible",
    ],
    "Content Mining (10D)": [
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


def quality_band(score: int | float | None) -> tuple[str, str]:
    """Return (band_name, color) for a quality score."""
    if score is None:
        return ("N/A", "#9e9e9e")
    for band_name, (low, high, color) in QUALITY_BANDS.items():
        if low <= score <= high:
            return (band_name, color)
    return ("N/A", "#9e9e9e")
