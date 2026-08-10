"""AI Job Recommendation Engine Module for AI Career Copilot.

Analyzes candidate resume skills, ATS evaluation scores, work experience,
and profile features to evaluate suitabilities across 10 key tech job roles.
Generates ranked job recommendations with match percentages, approximate salary ranges,
candidate strengths, missing skills, and targeted career recommendations.
"""

import logging
from typing import Any, Dict, List, Optional

from app.ai.skill_gap_engine import (
    SUPPORTED_TARGET_ROLES,
    evaluate_skill_gap,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Exception Classes
# ============================================================================


class JobRecommendationEngineError(Exception):
    """Base exception class for Job Recommendation Engine errors."""

    pass


class JobRecommendationFailedError(JobRecommendationEngineError):
    """Raised when job recommendation generation fails due to invalid input."""

    pass


# ============================================================================
# Extended Role Taxonomy & Salary Metadata
# ============================================================================

ALL_EVALUATION_ROLES: List[str] = [
    "Software Engineer",
    "Backend Developer",
    "Frontend Developer",
    "Full Stack Developer",
    "AI Engineer",
    "ML Engineer",
    "Data Analyst",
    "Cloud Engineer",
    "DevOps Engineer",
    "Mobile App Developer",
]

SALARY_TABLE: Dict[str, Dict[str, str]] = {
    "Software Engineer": {
        "Fresher": "$65,000 - $85,000 / year",
        "Junior": "$80,000 - $100,000 / year",
        "Mid-Level": "$100,000 - $135,000 / year",
        "Senior": "$135,000 - $175,000 / year",
        "Lead": "$170,000 - $220,000 / year",
    },
    "Backend Developer": {
        "Fresher": "$60,000 - $80,000 / year",
        "Junior": "$75,000 - $95,000 / year",
        "Mid-Level": "$95,000 - $130,000 / year",
        "Senior": "$130,000 - $170,000 / year",
        "Lead": "$160,000 - $210,000 / year",
    },
    "Frontend Developer": {
        "Fresher": "$55,000 - $75,000 / year",
        "Junior": "$70,000 - $90,000 / year",
        "Mid-Level": "$90,000 - $125,000 / year",
        "Senior": "$125,000 - $160,000 / year",
        "Lead": "$150,000 - $195,000 / year",
    },
    "Full Stack Developer": {
        "Fresher": "$65,000 - $85,000 / year",
        "Junior": "$80,000 - $105,000 / year",
        "Mid-Level": "$105,000 - $145,000 / year",
        "Senior": "$140,000 - $185,000 / year",
        "Lead": "$175,000 - $230,000 / year",
    },
    "AI Engineer": {
        "Fresher": "$75,000 - $95,000 / year",
        "Junior": "$90,000 - $115,000 / year",
        "Mid-Level": "$120,000 - $160,000 / year",
        "Senior": "$160,000 - $210,000 / year",
        "Lead": "$200,000 - $260,000 / year",
    },
    "ML Engineer": {
        "Fresher": "$75,000 - $95,000 / year",
        "Junior": "$90,000 - $115,000 / year",
        "Mid-Level": "$120,000 - $160,000 / year",
        "Senior": "$160,000 - $210,000 / year",
        "Lead": "$200,000 - $260,000 / year",
    },
    "Data Analyst": {
        "Fresher": "$50,000 - $70,000 / year",
        "Junior": "$65,000 - $85,000 / year",
        "Mid-Level": "$85,000 - $110,000 / year",
        "Senior": "$110,000 - $145,000 / year",
        "Lead": "$140,000 - $175,000 / year",
    },
    "Cloud Engineer": {
        "Fresher": "$65,000 - $85,000 / year",
        "Junior": "$80,000 - $105,000 / year",
        "Mid-Level": "$105,000 - $140,000 / year",
        "Senior": "$140,000 - $180,000 / year",
        "Lead": "$175,000 - $220,000 / year",
    },
    "DevOps Engineer": {
        "Fresher": "$65,000 - $85,000 / year",
        "Junior": "$80,000 - $105,000 / year",
        "Mid-Level": "$105,000 - $140,000 / year",
        "Senior": "$140,000 - $185,000 / year",
        "Lead": "$175,000 - $230,000 / year",
    },
    "Mobile App Developer": {
        "Fresher": "$55,000 - $75,000 / year",
        "Junior": "$70,000 - $90,000 / year",
        "Mid-Level": "$90,000 - $125,000 / year",
        "Senior": "$125,000 - $165,000 / year",
        "Lead": "$155,000 - $200,000 / year",
    },
}


# ============================================================================
# Core Job Recommendation Engine
# ============================================================================


def get_salary_estimate(role: str, experience_level: str) -> str:
    """Retrieve approximate salary range string based on job role and experience level."""
    role_salaries = SALARY_TABLE.get(role, SALARY_TABLE["Software Engineer"])
    exp_key = experience_level.strip().title() if experience_level else "Fresher"

    if exp_key in role_salaries:
        return role_salaries[exp_key]

    return role_salaries.get("Fresher", "$60,000 - $85,000 / year")


def evaluate_job_suitability(
    structured_data: Dict[str, Any],
    role: str,
    experience_level: str = "Fresher",
) -> Dict[str, Any]:
    """Evaluate candidate suitability and match breakdown for a specific job role."""
    # Reuse evaluate_skill_gap for consistent skill taxonomy evaluation
    lookup_role = role if role in SUPPORTED_TARGET_ROLES else "Software Engineer"
    gap_analysis = evaluate_skill_gap(structured_data, target_role=lookup_role)

    matched_skills = gap_analysis.get("matched_skills", [])
    missing_skills = gap_analysis.get("missing_skills", [])
    match_percentage = gap_analysis.get("match_percentage", 50)

    # Build Strengths
    strengths: List[str] = []
    if matched_skills:
        top_matched = ", ".join(matched_skills[:4])
        strengths.append(f"Demonstrated proficiency in key role skills: {top_matched}")
    if len(matched_skills) >= 4:
        strengths.append(f"Strong overall technical skill alignment for {role} roles")

    experience = structured_data.get("experience", []) or []
    if experience:
        strengths.append(f"Relevant professional experience ({len(experience)} position(s) listed)")

    # Build Recommendations
    recommendations: List[str] = []
    if missing_skills:
        top_missing = ", ".join(missing_skills[:3])
        recommendations.append(f"Prioritize learning {top_missing} to boost competitiveness for {role} roles")
    recommendations.append(f"Highlight projects and hands-on achievements related to {role} competencies")

    salary_range = get_salary_estimate(role, experience_level)

    return {
        "role": role,
        "match_percentage": match_percentage,
        "salary_range": salary_range,
        "strengths": strengths,
        "missing_skills": missing_skills,
        "recommendations": recommendations,
    }


def recommend_jobs(
    structured_data: Dict[str, Any],
    preferred_location: str = "Remote",
    experience_level: str = "Fresher",
    top_n: int = 5,
) -> Dict[str, Any]:
    """Generate ranked AI job recommendations for candidate profile across 10 tech roles.

    Args:
        structured_data: Structured resume JSON data.
        preferred_location: Preferred work location (default: Remote).
        experience_level: Candidate experience tier (Fresher, Junior, Mid-Level, Senior, Lead).
        top_n: Number of top recommended job roles to return (default: 5).

    Returns:
        Structured payload matching {"recommended_jobs": [...]}.

    Raises:
        JobRecommendationFailedError: If structured_data is invalid.
    """
    if not isinstance(structured_data, dict):
        logger.error("Invalid structured_data passed to recommend_jobs: %s", type(structured_data))
        raise JobRecommendationFailedError("Input structured_data must be a valid dictionary.")

    logger.info(
        "Generating job recommendations for location='%s', experience='%s'",
        preferred_location,
        experience_level,
    )

    evaluated_roles: List[Dict[str, Any]] = []

    for role in ALL_EVALUATION_ROLES:
        suitability = evaluate_job_suitability(
            structured_data=structured_data,
            role=role,
            experience_level=experience_level,
        )
        evaluated_roles.append(suitability)

    # Sort roles by match percentage descending
    evaluated_roles.sort(key=lambda x: x["match_percentage"], reverse=True)

    # Select top N recommendations
    recommended_jobs = evaluated_roles[:top_n]

    logger.info("Successfully generated %d job recommendations", len(recommended_jobs))
    return {
        "recommended_jobs": recommended_jobs
    }
