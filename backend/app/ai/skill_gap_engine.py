"""Skill Gap Engine Module for AI Career Copilot.

Analyzes candidate skills extracted from resumes against industry-standard
requirements for supported target job roles. Identifies matched skills, missing skills,
recommended skills, match percentage, and a prioritized learning order.
"""

import logging
import re
from typing import Any, Dict, List, Set, Tuple

logger = logging.getLogger(__name__)


# ============================================================================
# Exception Classes
# ============================================================================


class SkillGapEngineError(Exception):
    """Base exception class for Skill Gap Engine errors."""

    pass


class InvalidTargetRoleError(SkillGapEngineError):
    """Raised when an unsupported target job role is provided."""

    pass


class SkillGapAnalysisFailedError(SkillGapEngineError):
    """Raised when skill gap analysis fails due to input format errors."""

    pass


# ============================================================================
# Role Skill Taxonomies
# ============================================================================

SUPPORTED_TARGET_ROLES: Dict[str, Dict[str, List[str]]] = {
    "Backend Developer": {
        "core_skills": [
            "Python",
            "Node.js",
            "Java",
            "Go",
            "FastAPI",
            "Django",
            "Express",
            "PostgreSQL",
            "MySQL",
            "MongoDB",
            "REST API",
            "Docker",
            "Git",
        ],
        "recommended_skills": [
            "Redis",
            "Celery",
            "gRPC",
            "Microservices",
            "GraphQL",
            "CI/CD",
            "AWS",
            "System Design",
        ],
    },
    "Frontend Developer": {
        "core_skills": [
            "HTML",
            "CSS",
            "JavaScript",
            "TypeScript",
            "React",
            "Vue.js",
            "Angular",
            "Next.js",
            "Tailwind CSS",
            "REST API",
            "Git",
        ],
        "recommended_skills": [
            "Redux",
            "Zustand",
            "Webpack",
            "Vite",
            "Performance Optimization",
            "Jest",
            "Cypress",
        ],
    },
    "Full Stack Developer": {
        "core_skills": [
            "JavaScript",
            "TypeScript",
            "React",
            "Node.js",
            "Python",
            "HTML",
            "CSS",
            "PostgreSQL",
            "MongoDB",
            "REST API",
            "Docker",
            "Git",
        ],
        "recommended_skills": [
            "Next.js",
            "FastAPI",
            "GraphQL",
            "Redis",
            "CI/CD",
            "AWS",
            "System Design",
        ],
    },
    "AI Engineer": {
        "core_skills": [
            "Python",
            "PyTorch",
            "TensorFlow",
            "Machine Learning",
            "Deep Learning",
            "NLP",
            "LLMs",
            "LangChain",
            "Scikit-Learn",
            "Pandas",
            "NumPy",
            "Git",
        ],
        "recommended_skills": [
            "Transformers",
            "Vector Databases",
            "RAG",
            "Model Deployment",
            "FastAPI",
            "Docker",
            "MLOps",
            "CUDA",
        ],
    },
    "Data Analyst": {
        "core_skills": [
            "Python",
            "SQL",
            "Excel",
            "Tableau",
            "Power BI",
            "Pandas",
            "NumPy",
            "Data Visualization",
            "Data Cleaning",
            "Statistics",
        ],
        "recommended_skills": [
            "R",
            "BigQuery",
            "Snowflake",
            "ETL",
            "A/B Testing",
            "Jupyter",
        ],
    },
    "Cloud Engineer": {
        "core_skills": [
            "AWS",
            "Azure",
            "GCP",
            "Docker",
            "Kubernetes",
            "Terraform",
            "Linux",
            "Networking",
            "CI/CD",
            "Bash",
            "Python",
            "Git",
        ],
        "recommended_skills": [
            "Ansible",
            "CloudFormation",
            "Prometheus",
            "Grafana",
            "Security",
            "IAM",
        ],
    },
    "Software Engineer": {
        "core_skills": [
            "Data Structures",
            "Algorithms",
            "Python",
            "Java",
            "C++",
            "JavaScript",
            "Git",
            "SQL",
            "Object-Oriented Programming",
            "System Design",
        ],
        "recommended_skills": [
            "Docker",
            "CI/CD",
            "Unit Testing",
            "Agile",
            "Cloud Computing",
        ],
    },
}


# Alias mapping to handle common user role naming variations
ROLE_ALIASES: Dict[str, str] = {
    "software engineer": "Software Engineer",
    "software developer": "Software Engineer",
    "backend developer": "Backend Developer",
    "backend engineer": "Backend Developer",
    "frontend developer": "Frontend Developer",
    "frontend engineer": "Frontend Developer",
    "full stack developer": "Full Stack Developer",
    "fullstack developer": "Full Stack Developer",
    "fullstack engineer": "Full Stack Developer",
    "ai engineer": "AI Engineer",
    "ml engineer": "AI Engineer",
    "machine learning engineer": "AI Engineer",
    "data analyst": "Data Analyst",
    "cloud engineer": "Cloud Engineer",
    "devops engineer": "Cloud Engineer",
}


# ============================================================================
# Skill Matching Helper Functions
# ============================================================================


def normalize_skill(skill_name: str) -> str:
    """Normalize skill name string for fuzzy matching (lowercase, stripped)."""
    if not skill_name:
        return ""
    cleaned = skill_name.lower().strip()
    cleaned = re.sub(r"[\.\-\_\/\s]+", "", cleaned)
    return cleaned


def resolve_target_role(role_name: str) -> str:
    """Validate and resolve target role string against supported taxonomy.

    Args:
        role_name: User-provided role title.

    Returns:
        Canonical role title string.

    Raises:
        InvalidTargetRoleError: If the role is not supported.
    """
    if not role_name or not role_name.strip():
        raise InvalidTargetRoleError("Target role string cannot be empty.")

    normalized = role_name.strip().lower()

    if normalized in ROLE_ALIASES:
        return ROLE_ALIASES[normalized]

    for supported_role in SUPPORTED_TARGET_ROLES:
        if supported_role.lower() == normalized:
            return supported_role

    supported_list = ", ".join(list(SUPPORTED_TARGET_ROLES.keys()))
    raise InvalidTargetRoleError(
        f"Target role '{role_name}' is not supported. Supported roles: {supported_list}"
    )


def extract_skills_from_resume(structured_data: Dict[str, Any]) -> List[str]:
    """Gather all skills listed explicitly or mentioned in experience/projects.

    Args:
        structured_data: Structured resume JSON.

    Returns:
        List of unique skill strings extracted from candidate profile.
    """
    all_skills: Set[str] = set()

    # Explicit skills section
    raw_skills = structured_data.get("skills", []) or []
    for sk in raw_skills:
        if isinstance(sk, str) and sk.strip():
            all_skills.add(sk.strip())

    # Skills from work experience technologies
    experience = structured_data.get("experience", []) or []
    for exp in experience:
        if isinstance(exp, dict):
            techs = exp.get("technologies", []) or []
            for t in techs:
                if isinstance(t, str) and t.strip():
                    all_skills.add(t.strip())

    # Skills from projects technologies
    projects = structured_data.get("projects", []) or []
    for proj in projects:
        if isinstance(proj, dict):
            techs = proj.get("technologies", []) or []
            for t in techs:
                if isinstance(t, str) and t.strip():
                    all_skills.add(t.strip())

    return list(all_skills)


# ============================================================================
# Core Skill Gap Analysis Engine
# ============================================================================


def evaluate_skill_gap(
    structured_data: Dict[str, Any], target_role: str
) -> Dict[str, Any]:
    """Execute skill gap analysis comparing candidate skills against target role taxonomy.

    Args:
        structured_data: Structured resume JSON dictionary.
        target_role: Name of the target job role to analyze.

    Returns:
        Dictionary payload containing matched_skills, missing_skills,
        recommended_skills, match_percentage, and priority_learning_order.

    Raises:
        InvalidTargetRoleError: If target_role is unsupported.
        SkillGapAnalysisFailedError: If structured_data is invalid.
    """
    if not isinstance(structured_data, dict):
        logger.error(
            "Invalid structured_data passed to evaluate_skill_gap: %s",
            type(structured_data),
        )
        raise SkillGapAnalysisFailedError(
            "Input structured_data must be a valid dictionary."
        )

    canonical_role = resolve_target_role(target_role)
    logger.info("Executing Skill Gap Analysis for target role: %s", canonical_role)

    role_taxonomy = SUPPORTED_TARGET_ROLES[canonical_role]
    core_skills = role_taxonomy["core_skills"]
    recommended_skills = role_taxonomy["recommended_skills"]

    candidate_skills = extract_skills_from_resume(structured_data)

    # Build normalized lookups for matching
    normalized_candidate_map = {
        normalize_skill(sk): sk for sk in candidate_skills if sk
    }

    matched_skills: List[str] = []
    missing_skills: List[str] = []

    # Evaluate Core Skills
    for core_sk in core_skills:
        norm_core = normalize_skill(core_sk)
        matched = False
        for norm_cand, orig_cand in normalized_candidate_map.items():
            if norm_core == norm_cand or norm_core in norm_cand or norm_cand in norm_core:
                matched_skills.append(core_sk)
                matched = True
                break
        if not matched:
            missing_skills.append(core_sk)

    # Evaluate Recommended Skills
    rec_missing: List[str] = []
    for rec_sk in recommended_skills:
        norm_rec = normalize_skill(rec_sk)
        matched = False
        for norm_cand in normalized_candidate_map:
            if norm_rec == norm_cand or norm_rec in norm_cand or norm_cand in norm_rec:
                if rec_sk not in matched_skills:
                    matched_skills.append(rec_sk)
                matched = True
                break
        if not matched:
            rec_missing.append(rec_sk)

    # Deduplicate matched skills
    unique_matched = list(dict.fromkeys(matched_skills))
    unique_missing = list(dict.fromkeys(missing_skills))
    unique_recommended = list(dict.fromkeys(rec_missing))

    # Calculate match percentage based on core required skills
    total_core = len(core_skills)
    matched_core_count = total_core - len(unique_missing)
    match_percentage = int((matched_core_count / max(1, total_core)) * 100)
    match_percentage = min(100, max(0, match_percentage))

    # Build Priority Learning Order: Core missing skills first, followed by top recommended skills
    priority_order = unique_missing + unique_recommended[:3]
    unique_priority = list(dict.fromkeys(priority_order))

    result = {
        "target_role": canonical_role,
        "matched_skills": unique_matched,
        "missing_skills": unique_missing,
        "recommended_skills": unique_recommended,
        "match_percentage": match_percentage,
        "priority_learning_order": unique_priority,
    }

    logger.info(
        "Skill Gap Analysis completed for %s: %d%% match (%d matched, %d missing)",
        canonical_role,
        match_percentage,
        len(unique_matched),
        len(unique_missing),
    )
    return result
