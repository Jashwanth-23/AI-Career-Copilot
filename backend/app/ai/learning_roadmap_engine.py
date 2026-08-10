"""AI Learning Roadmap Engine Module for AI Career Copilot.

Generates a personalized, step-by-step weekly learning roadmap tailored to candidate
resume analysis, ATS scores, skill gaps, and target job roles.
Also dynamically generates 2 to 3 real-world portfolio projects using Gemini AI.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from google.genai import types

from app.core.gemini_client import get_gemini_client, get_gemini_model

logger = logging.getLogger(__name__)


# ============================================================================
# Exception Classes
# ============================================================================


class LearningRoadmapEngineError(Exception):
    """Base exception class for Learning Roadmap Engine errors."""

    pass


class RoadmapGenerationFailedError(LearningRoadmapEngineError):
    """Raised when roadmap generation fails due to invalid inputs."""

    pass


# ============================================================================
# Curated Skill Resources & Topic Knowledge Base
# ============================================================================

SKILL_CURRICULUM: Dict[str, Dict[str, Any]] = {
    "python": {
        "topics": [
            "Advanced Data Types & Generators",
            "Asynchronous Programming (asyncio)",
            "Decorators & Context Managers",
            "Unit Testing with Pytest",
        ],
        "resources": [
            "Python Official Documentation (docs.python.org)",
            "Real Python Advanced Tutorials (realpython.com)",
        ],
        "mini_project": "Build an Async Web Crawler and Data Extractor CLI",
        "milestone": "Master Advanced Asynchronous Python Development",
    },
    "fastapi": {
        "topics": [
            "Pydantic V2 Data Validation",
            "Dependency Injection System",
            "OAuth2 & JWT Authentication",
            "SQLAlchemy Async Database Integration",
        ],
        "resources": [
            "FastAPI Official Documentation (fastapi.tiangolo.com)",
            "Full Stack FastAPI Template Guide",
        ],
        "mini_project": "Develop a Production-Ready REST API Service",
        "milestone": "Build High-Performance Async Backend APIs",
    },
    "postgresql": {
        "topics": [
            "Relational Database Design & Normalization",
            "B-Tree Indexing & Query Optimization",
            "Transactions & ACID Guarantees",
            "Database Migrations with Alembic",
        ],
        "resources": [
            "PostgreSQL Tutorial (postgresqltutorial.com)",
            "Use The Index, Luke (use-the-index-luke.com)",
        ],
        "mini_project": "Design and Optimize a High-Throughput E-Commerce Schema",
        "milestone": "Master Database Architecture and Query Tuning",
    },
    "docker": {
        "topics": [
            "Containerization Fundamentals",
            "Multi-Stage Dockerfiles for Production",
            "Docker Compose Orchestration",
            "Container Security & Image Optimization",
        ],
        "resources": [
            "Docker Docs (docs.docker.com)",
            "Docker Curriculum (docker-curriculum.com)",
        ],
        "mini_project": "Containerize a Multi-Container FastAPI & PostgreSQL Application",
        "milestone": "Master Containerization & Environment Isolation",
    },
    "redis": {
        "topics": [
            "In-Memory Key-Value Data Structures",
            "Caching Strategies (Cache-Aside, Write-Through)",
            "Pub/Sub & Message Queuing",
            "Distributed Rate Limiting",
        ],
        "resources": [
            "Redis University (university.redis.io)",
            "Redis Developer Guide",
        ],
        "mini_project": "Build a Redis-Backed Distributed Rate Limiter Middleware",
        "milestone": "Implement High-Speed In-Memory Caching",
    },
    "celery": {
        "topics": [
            "Asynchronous Background Job Processing",
            "Task Queues & Brokers (Redis / RabbitMQ)",
            "Periodic Tasks (Celery Beat)",
            "Task Monitoring & Error Handling",
        ],
        "resources": [
            "Celery Documentation (docs.celeryq.dev)",
            "Real Python Asynchronous Tasks with Celery Guide",
        ],
        "mini_project": "Build an Automated Background Email Notification System",
        "milestone": "Master Distributed Asynchronous Task Execution",
    },
    "react": {
        "topics": [
            "Component Lifecycle & Custom Hooks",
            "State Management (Zustand / Redux Toolkit)",
            "Virtual DOM & Reconciliation Optimization",
            "Integration with REST & GraphQL APIs",
        ],
        "resources": [
            "React Official Docs (react.dev)",
            "FreeCodeCamp React Course",
        ],
        "mini_project": "Build a Responsive Interactive Dashboard Application",
        "milestone": "Build Scalable Modern Frontend User Interfaces",
    },
    "typescript": {
        "topics": [
            "Generics & Utility Types",
            "Strict Type Checking & Type Guarding",
            "Interfaces vs Type Aliases",
            "TypeScript with React & Node.js",
        ],
        "resources": [
            "TypeScript Handbook (typescriptlang.org)",
            "ExecuteProgram TypeScript Course",
        ],
        "mini_project": "Refactor a JavaScript Codebase to Strict TypeScript",
        "milestone": "Master Type-Safe Frontend and Node Development",
    },
    "pytorch": {
        "topics": [
            "Tensors & Automatic Differentiation (Autograd)",
            "Building Custom Neural Network Modules",
            "Model Training Loops & Loss Functions",
            "Fine-Tuning Pretrained Models with CUDA",
        ],
        "resources": [
            "PyTorch Official Tutorials (pytorch.org/tutorials)",
            "Deep Learning with PyTorch Book",
        ],
        "mini_project": "Train and Evaluate an Image Classification Model",
        "milestone": "Master Deep Learning Model Architecture",
    },
    "system design": {
        "topics": [
            "Load Balancing & Horizontal Scaling",
            "Database Sharding & Replication",
            "Microservices vs Monolith Architecture",
            "CAP Theorem & Consistent Hashing",
        ],
        "resources": [
            "System Design Primer (github.com/donnemartin/system-design-primer)",
            "ByteByteGo System Design Newsletter",
        ],
        "mini_project": "Architect a High-Availability Distributed URL Shortener",
        "milestone": "Master Large-Scale Distributed System Design",
    },
}


# ============================================================================
# Helper Functions
# ============================================================================


def clean_json_response(raw_response: str) -> str:
    """Clean markdown code block wrappers (```json ... ```) from AI response text."""
    if not raw_response:
        return ""
    cleaned = raw_response.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def generate_skill_curriculum(skill: str, week_num: int) -> Dict[str, Any]:
    """Generate structured weekly curriculum for a specified target skill."""
    norm_sk = skill.lower().strip()

    if norm_sk in SKILL_CURRICULUM:
        info = SKILL_CURRICULUM[norm_sk]
        return {
            "week": week_num,
            "focus": skill,
            "topics": info["topics"],
            "resources": info["resources"],
            "mini_project": info["mini_project"],
            "milestone": info["milestone"],
        }

    return {
        "week": week_num,
        "focus": skill,
        "topics": [
            f"Foundations and Core Syntax of {skill}",
            f"Advanced Features and Best Practices in {skill}",
            f"Integration and Production Deployment with {skill}",
            f"Debugging and Performance Tuning for {skill}",
        ],
        "resources": [
            f"Official {skill} Documentation",
            f"FreeCodeCamp & YouTube Tutorials for {skill}",
        ],
        "mini_project": f"Build a Practical Mini-Project implementing {skill}",
        "milestone": f"Achieve Working Proficiency in {skill}",
    }


import threading

# Thread-safe in-memory cache for dynamic real-world projects generated by Gemini
_PROJECTS_CACHE: Dict[Tuple[str, str, str, str], List[Dict[str, Any]]] = {}
_CACHE_LOCK = threading.Lock()


def generate_real_world_projects_with_gemini(
    structured_data: Dict[str, Any],
    skill_gap: Dict[str, Any],
    target_role: str,
) -> List[Dict[str, Any]]:
    """Dynamically generate 2 to 3 real-world portfolio projects using Gemini AI.

    No project names, role mappings, or static lists are hardcoded. Gemini AI
    evaluates target role, existing resume skills, missing skills, and experience level
    to generate 2 or 3 tailored portfolio projects.

    Args:
        structured_data: Parsed resume JSON dictionary.
        skill_gap: Skill gap analysis result dictionary.
        target_role: Selected target role string.

    Returns:
        List of 2 to 3 structured project dictionaries matching RealWorldProjectSchema.
    """
    existing_skills = structured_data.get("skills", []) or []
    missing_skills = skill_gap.get("missing_skills", []) or []
    experience = structured_data.get("experience", []) or []
    existing_projects = structured_data.get("projects", []) or []

    model_name = get_gemini_model()
    cache_key = (
        target_role.lower().strip(),
        ",".join(sorted([str(s) for s in existing_skills])),
        ",".join(sorted([str(s) for s in missing_skills])),
        model_name,
    )

    with _CACHE_LOCK:
        if cache_key in _PROJECTS_CACHE:
            logger.info("Cache hit for dynamic real-world projects (role='%s'). Reusing projects.", target_role)
            return _PROJECTS_CACHE[cache_key]

    prompt = f"""You are an expert AI Career Architect and Senior Technical Hiring Manager. Analyze this candidate's profile and generate EXACTLY 2 OR 3 real-world portfolio projects to help them get hired as a '{target_role}'.

CANDIDATE PROFILE:
- Target Role: {target_role}
- Existing Resume Skills: {json.dumps(existing_skills)}
- Missing Skills (Skill Gap): {json.dumps(missing_skills)}
- Work Experience Summary: {json.dumps(experience[:2])}
- Existing Projects: {json.dumps([p.get('name', '') for p in existing_projects if isinstance(p, dict)])}

STRICT SELECTION RULES:
1. Recommending EXACTLY 2 or 3 projects is MANDATORY. Do NOT return 1 project and do NOT return more than 3 projects.
2. Select projects that directly match '{target_role}', bridge missing skills, and build on existing knowledge.
3. Every project must be realistic, production-grade, and suitable for showcase on GitHub / Portfolio.
4. Projects must be distinct from each other and build progressively useful skills.

SCHEMA:
{{
  "target_role": "{target_role}",
  "projects": [
    {{
      "title": "Clear, dynamic project title",
      "description": "2-3 sentence project overview describing what to build",
      "difficulty": "Beginner | Intermediate | Advanced",
      "estimated_duration": "Estimated completion time (e.g. '2-3 Weeks')",
      "why_this_project": "Specific reasoning why this project bridges this candidate's gap",
      "technologies": ["List of core tech stack / frameworks"],
      "key_features": ["3-4 key production features to build"],
      "skills_developed": ["Core technical skills developed"],
      "skill_gap_addressed": ["Specific missing skills from skill gap addressed"],
      "portfolio_value": "Statement on why recruiters will value this project",
      "expected_outcome": "Demonstrable outcome or capability gained"
    }}
  ]
}}

STRICT INSTRUCTIONS:
- Return ONLY valid JSON matching the schema above.
- The "projects" array MUST contain EXACTLY 2 or 3 objects.
"""

    try:
        client = get_gemini_client()
        model_name = get_gemini_model()
        generation_config = types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
        )

        logger.info(
            "Requesting 2-3 dynamic real-world projects from Gemini AI (Model: %s) for role '%s'",
            model_name,
            target_role,
        )

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=generation_config,
        )

        raw_output = response.text if response and hasattr(response, "text") else ""
        if not raw_output or not raw_output.strip():
            logger.warning("Gemini returned empty text for project generation.")
            return []

        cleaned_json = clean_json_response(raw_output)
        parsed = json.loads(cleaned_json)
        raw_projects = parsed.get("projects", [])

        if not isinstance(raw_projects, list):
            logger.warning("Parsed projects output is not a list: %s", type(raw_projects))
            return []

        # Enforce 2 <= len(projects) <= 3
        normalized_projects: List[Dict[str, Any]] = []
        for item in raw_projects[:3]:
            if isinstance(item, dict):
                normalized_projects.append({
                    "title": item.get("title", f"Real-World {target_role} Project"),
                    "description": item.get("description", ""),
                    "difficulty": item.get("difficulty", "Intermediate"),
                    "estimated_duration": item.get("estimated_duration", "2-3 Weeks"),
                    "why_this_project": item.get("why_this_project", ""),
                    "technologies": item.get("technologies", []) or [],
                    "key_features": item.get("key_features", []) or [],
                    "skills_developed": item.get("skills_developed", []) or [],
                    "skill_gap_addressed": item.get("skill_gap_addressed", []) or [],
                    "portfolio_value": item.get("portfolio_value", ""),
                    "expected_outcome": item.get("expected_outcome", ""),
                })

        if normalized_projects:
            with _CACHE_LOCK:
                _PROJECTS_CACHE[cache_key] = normalized_projects

        logger.info(
            "Successfully dynamically generated %d real-world projects with Gemini AI for role '%s'",
            len(normalized_projects),
            target_role,
        )
        return normalized_projects

    except Exception as exc:
        logger.error(
            "Error dynamically generating real-world projects with Gemini for role '%s': %s",
            target_role,
            exc,
            exc_info=True,
        )
        return []


# ============================================================================
# Core Learning Roadmap Engine Calculation
# ============================================================================


def generate_learning_roadmap(
    structured_data: Dict[str, Any],
    ats_score: Dict[str, Any],
    skill_gap: Dict[str, Any],
    target_role: str,
) -> Dict[str, Any]:
    """Generate a personalized weekly learning roadmap payload based on candidate profile and AI evaluations.

    Args:
        structured_data: Parsed resume JSON data.
        ats_score: ATS score evaluation breakdown.
        skill_gap: Skill gap analysis breakdown.
        target_role: Target job role title.

    Returns:
        Structured roadmap payload containing target_role, estimated_duration,
        overall_progress, list of weekly learning modules, and recommended_projects.

    Raises:
        RoadmapGenerationFailedError: If inputs are invalid or incomplete.
    """
    if not isinstance(skill_gap, dict):
        logger.error("Invalid skill_gap dictionary provided to generate_learning_roadmap")
        raise RoadmapGenerationFailedError("Input skill_gap must be a valid dictionary.")

    logger.info("Generating AI Learning Roadmap for target role: %s", target_role)

    match_percentage = skill_gap.get("match_percentage", 50)
    priority_skills = skill_gap.get("priority_learning_order", []) or []
    missing_skills = skill_gap.get("missing_skills", []) or []
    recommended_skills = skill_gap.get("recommended_skills", []) or []

    # Combine all skills to learn in order of priority
    skills_to_learn = list(dict.fromkeys(priority_skills + missing_skills + recommended_skills))

    if not skills_to_learn:
        skills_to_learn = ["System Design", "Docker", "CI/CD", "AWS"]

    # Determine roadmap duration based on skill match level
    if match_percentage >= 85:
        total_weeks = 4
        duration_str = "4 Weeks"
    elif match_percentage >= 60:
        total_weeks = 8
        duration_str = "8 Weeks"
    else:
        total_weeks = 12
        duration_str = "12 Weeks"

    roadmap_items: List[Dict[str, Any]] = []

    for w in range(1, total_weeks + 1):
        skill_idx = (w - 1) % len(skills_to_learn)
        target_skill = skills_to_learn[skill_idx]
        week_item = generate_skill_curriculum(target_skill, week_num=w)
        roadmap_items.append(week_item)

    # Initial progress baseline derived from skill match score
    overall_progress = min(100, max(0, match_percentage))

    # Dynamically generate 2-3 Real-World Portfolio Projects using Gemini AI
    recommended_projects = generate_real_world_projects_with_gemini(
        structured_data=structured_data,
        skill_gap=skill_gap,
        target_role=target_role,
    )

    result = {
        "target_role": target_role,
        "estimated_duration": duration_str,
        "overall_progress": overall_progress,
        "roadmap": roadmap_items,
        "recommended_projects": recommended_projects,
    }

    logger.info(
        "Successfully generated %s AI Learning Roadmap with %d weekly modules and %d dynamic real-world projects",
        duration_str,
        len(roadmap_items),
        len(recommended_projects),
    )
    return result
