"""ATS Score Engine Module for AI Career Copilot.

Calculates comprehensive Applicant Tracking System (ATS) scores based on structured
resume JSON data extracted by the Gemini Resume Parser. Evaluates sub-scores for
skills, experience, education, projects, and overall profile completeness, while
generating actionable strengths, weaknesses, and targeted improvement suggestions.
"""

import logging
import re
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


# ============================================================================
# Exception Classes
# ============================================================================


class ATSEngineError(Exception):
    """Base exception class for ATS Score Engine errors."""

    pass


class ATSAnalysisFailedError(ATSEngineError):
    """Raised when ATS score calculation fails due to invalid input structure."""

    pass


# ============================================================================
# Sub-Score Evaluators
# ============================================================================


def calculate_completeness_score(
    structured_data: Dict[str, Any]
) -> Tuple[int, List[str], List[str]]:
    """Calculate profile completeness score (0-100) and generate feedback."""
    score = 0
    strengths = []
    weaknesses = []

    personal_info = structured_data.get("personal_information", {}) or {}

    # Check Personal Details (Max 30 points)
    p_fields = ["name", "email", "phone", "location"]
    present_p = [f for f in p_fields if personal_info.get(f)]
    p_score = int((len(present_p) / len(p_fields)) * 20)
    score += p_score

    if (
        personal_info.get("linkedin")
        or personal_info.get("github")
        or personal_info.get("website")
    ):
        score += 10
        strengths.append(
            "Contains professional online profiles (LinkedIn/GitHub/Portfolio)."
        )
    else:
        weaknesses.append(
            "Missing online profile links (LinkedIn, GitHub, or Portfolio URL)."
        )

    # Check Summary (Max 15 points)
    summary = structured_data.get("summary", "") or ""
    if len(summary.strip()) >= 50:
        score += 15
        strengths.append("Includes a well-defined professional summary.")
    elif summary.strip():
        score += 8
        weaknesses.append(
            "Professional summary is brief; consider elaborating on your career focus."
        )
    else:
        weaknesses.append("Missing a professional summary section.")

    # Check Major Sections (Max 55 points)
    sections = [
        ("skills", 15, "Skills section is present."),
        ("experience", 20, "Work experience section is present."),
        ("education", 10, "Education section is present."),
        ("projects", 10, "Projects section is present."),
    ]

    for sec_key, sec_points, _ in sections:
        items = structured_data.get(sec_key, [])
        if items:
            score += sec_points
        else:
            weaknesses.append(f"Missing {sec_key.capitalize()} section.")

    final_score = min(100, max(0, score))
    return final_score, strengths, weaknesses


def calculate_skills_score(
    skills: List[str]
) -> Tuple[int, List[str], List[str]]:
    """Calculate skills score (0-100) based on skill volume and diversity."""
    strengths = []
    weaknesses = []

    if not skills:
        weaknesses.append("No technical or professional skills were listed.")
        return 0, strengths, weaknesses

    skill_count = len(skills)
    if skill_count >= 12:
        score = 95
        strengths.append(
            f"Extensive skills list ({skill_count} skills identified)."
        )
    elif skill_count >= 8:
        score = 85
        strengths.append(f"Solid skill set ({skill_count} skills listed).")
    elif skill_count >= 4:
        score = 70
        weaknesses.append(
            "Consider expanding your skills list to include relevant frameworks and tools."
        )
    else:
        score = 50
        weaknesses.append(
            "Very few skills listed; add more technical competencies."
        )

    return score, strengths, weaknesses


def calculate_experience_score(
    experience: List[Dict[str, Any]]
) -> Tuple[int, List[str], List[str]]:
    """Calculate work experience score (0-100) evaluating metrics and detail."""
    strengths = []
    weaknesses = []

    if not experience:
        weaknesses.append("No work experience listed in resume.")
        return 0, strengths, weaknesses

    score = 60  # Baseline score for having experience

    # Check volume of positions
    if len(experience) >= 3:
        score += 15
        strengths.append(
            f"Demonstrates consistent career history ({len(experience)} roles listed)."
        )
    elif len(experience) >= 1:
        score += 10

    # Action verbs check
    action_verbs = {
        "developed",
        "built",
        "designed",
        "architected",
        "managed",
        "led",
        "implemented",
        "improved",
        "increased",
        "reduced",
        "optimized",
        "created",
        "spearheaded",
        "automated",
        "scaled",
        "integrated",
    }

    metrics_pattern = re.compile(
        r"\b(\d+%\b|\$\d+|\b\d+\s*(?:k|m|users|clients|percent|x)\b)",
        re.IGNORECASE,
    )

    has_metrics = False
    has_action_verbs = False

    for item in experience:
        descriptions = item.get("description", []) or []
        for desc in descriptions:
            if metrics_pattern.search(desc):
                has_metrics = True
            low_desc = desc.lower()
            if any(verb in low_desc for verb in action_verbs):
                has_action_verbs = True

    if has_metrics:
        score += 15
        strengths.append(
            "Work experience includes quantifiable achievements and metrics (e.g. %, $)."
        )
    else:
        weaknesses.append(
            "Work experience bullet points lack quantifiable impact metrics (e.g. %, numbers, dollar values)."
        )

    if has_action_verbs:
        score += 10
        strengths.append("Uses strong action verbs in experience descriptions.")

    final_score = min(100, max(0, score))
    return final_score, strengths, weaknesses


def calculate_education_score(
    education: List[Dict[str, Any]]
) -> Tuple[int, List[str], List[str]]:
    """Calculate education score (0-100)."""
    strengths = []
    weaknesses = []

    if not education:
        weaknesses.append("No education details provided.")
        return 40, strengths, weaknesses

    score = 75  # Baseline for having education entries

    for item in education:
        if item.get("degree") and item.get("institution"):
            score += 15
            strengths.append(
                "Education section clearly specifies degree and institution."
            )
            break

    final_score = min(100, max(0, score))
    return final_score, strengths, weaknesses


def calculate_projects_score(
    projects: List[Dict[str, Any]]
) -> Tuple[int, List[str], List[str]]:
    """Calculate projects score (0-100)."""
    strengths = []
    weaknesses = []

    if not projects:
        weaknesses.append("No projects listed.")
        return 50, strengths, weaknesses

    score = 70
    if len(projects) >= 2:
        score += 15
        strengths.append(f"Includes multiple key projects ({len(projects)} listed).")

    has_links = any(p.get("link") for p in projects if isinstance(p, dict))
    if has_links:
        score += 15
        strengths.append("Projects section includes live links or repository URLs.")
    else:
        weaknesses.append(
            "Projects lack links to source code repositories or live demos."
        )

    final_score = min(100, max(0, score))
    return final_score, strengths, weaknesses


# ============================================================================
# Main ATS Engine Calculation Function
# ============================================================================


def evaluate_ats_score(structured_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate overall ATS score breakdown, strengths, weaknesses, and improvement suggestions.

    Args:
        structured_data: Extracted structured resume JSON dictionary.

    Returns:
        Dictionary payload containing score breakdown and detailed feedback.

    Raises:
        ATSAnalysisFailedError: If structured_data is invalid or non-dict.
    """
    if not isinstance(structured_data, dict):
        logger.error(
            "Invalid structured_data passed to evaluate_ats_score: %s",
            type(structured_data),
        )
        raise ATSAnalysisFailedError(
            "Input structured_data must be a valid dictionary."
        )

    logger.info("Evaluating ATS score for structured resume data")

    all_strengths: List[str] = []
    all_weaknesses: List[str] = []
    suggestions: List[str] = []

    # 1. Calculate sub-scores
    completeness_score, c_str, c_weak = calculate_completeness_score(
        structured_data
    )
    all_strengths.extend(c_str)
    all_weaknesses.extend(c_weak)

    skills_score, s_str, s_weak = calculate_skills_score(
        structured_data.get("skills", []) or []
    )
    all_strengths.extend(s_str)
    all_weaknesses.extend(s_weak)

    experience_score, exp_str, exp_weak = calculate_experience_score(
        structured_data.get("experience", []) or []
    )
    all_strengths.extend(exp_str)
    all_weaknesses.extend(exp_weak)

    education_score, edu_str, edu_weak = calculate_education_score(
        structured_data.get("education", []) or []
    )
    all_strengths.extend(edu_str)
    all_weaknesses.extend(edu_weak)

    projects_score, proj_str, proj_weak = calculate_projects_score(
        structured_data.get("projects", []) or []
    )
    all_strengths.extend(proj_str)
    all_weaknesses.extend(proj_weak)

    # 2. Calculate Overall Weighted ATS Score (0-100)
    # Weights: Experience (30%), Skills (25%), Completeness (20%), Education (15%), Projects (10%)
    overall_score = int(
        (experience_score * 0.30)
        + (skills_score * 0.25)
        + (completeness_score * 0.20)
        + (education_score * 0.15)
        + (projects_score * 0.10)
    )
    overall_score = min(100, max(0, overall_score))

    # 3. Generate actionable improvement suggestions
    if experience_score < 85:
        suggestions.append(
            "Add measurable impact metrics to your work experience bullet points (e.g., 'Increased performance by 35%')."
        )
    if skills_score < 85:
        suggestions.append(
            "Incorporate more industry-relevant tools, libraries, and technical frameworks into your skills section."
        )
    if completeness_score < 90:
        suggestions.append(
            "Ensure all key contact details, a GitHub/LinkedIn link, and a concise summary statement are present."
        )
    if projects_score < 85:
        suggestions.append(
            "Add repository links (GitHub) or live deployment links for your projects to demonstrate practical application."
        )
    if not suggestions:
        suggestions.append(
            "Your resume meets high ATS standards! Keep key skill keywords updated with current industry trends."
        )

    # Deduplicate strengths and weaknesses while preserving order
    unique_strengths = list(dict.fromkeys(all_strengths))
    unique_weaknesses = list(dict.fromkeys(all_weaknesses))
    unique_suggestions = list(dict.fromkeys(suggestions))

    result = {
        "overall_score": overall_score,
        "skills_score": skills_score,
        "experience_score": experience_score,
        "education_score": education_score,
        "projects_score": projects_score,
        "completeness_score": completeness_score,
        "strengths": unique_strengths,
        "weaknesses": unique_weaknesses,
        "improvement_suggestions": unique_suggestions,
    }

    logger.info(
        "ATS score evaluation completed successfully (Overall Score: %d)",
        overall_score,
    )
    return result
