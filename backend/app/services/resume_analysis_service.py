"""Resume Analysis Service Module for AI Career Copilot.

Acts as the central AI analysis engine that coordinates resume retrieval,
text extraction via parser_service, and structured AI parsing via
gemini_resume_parser.

This service is designed as the core foundational module for downstream
AI features including ATS scoring, Skill Gap Analysis, Learning Roadmaps,
Job Recommendations, and Interview Question Generation.
"""

import threading
from datetime import datetime, timezone
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.gemini_resume_parser import (
    GeminiParserError,
    GeminiQuotaExhaustedError,
    parse_resume_with_gemini,
)
from app.ai.text_extractor import TextExtractorError
from app.core.gemini_client import get_gemini_model
from app.models.resume import Resume
from app.services.parser_service import parse_uploaded_resume

# Logger configuration for resume analysis service
logger = logging.getLogger(__name__)

# Base upload directory for resume storage on disk
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BACKEND_DIR / "uploads" / "resumes"

# In-memory cache for parsed structured resume JSON to prevent duplicate Gemini API requests
_ANALYSIS_CACHE: Dict[int, Dict[str, Any]] = {}
_CACHE_LOCK = threading.Lock()


# ============================================================================
# Custom Exception Hierarchy
# ============================================================================


class ResumeAnalysisError(Exception):
    """Base exception class for resume analysis service operations."""

    pass


class ResumeNotFoundError(ResumeAnalysisError):
    """Raised when a specified resume record is not found in the database."""

    pass


class ResumeFileNotFoundError(ResumeAnalysisError):
    """Raised when the resume document file is missing from disk or empty."""

    pass


class ResumeQuotaExhaustedError(ResumeAnalysisError):
    """Raised when Gemini returns HTTP 429 rate limit / quota exhausted."""

    pass


class ResumeAnalysisFailedError(ResumeAnalysisError):
    """Raised when an unrecoverable failure occurs during text extraction or AI parsing."""

    pass


# ============================================================================
# Helper Functions
# ============================================================================


def validate_resume(
    db: Session,
    resume_id: int,
    user_id: Optional[int] = None,
) -> Tuple[Resume, Path]:
    """Validate database record and underlying disk file for a given resume ID.

    Args:
        db: Active SQLAlchemy database session.
        resume_id: Primary key identifier of the target Resume.
        user_id: Optional user ID to enforce ownership validation.

    Returns:
        Tuple containing the validated Resume model instance and its Path on disk.

    Raises:
        ResumeNotFoundError: If the resume record does not exist or user_id mismatch occurs.
        ResumeFileNotFoundError: If the resume file does not exist on disk or is 0 bytes.
    """
    logger.info(
        "Validating resume ID %s (User ID check: %s)", resume_id, user_id
    )

    statement = select(Resume).where(Resume.id == resume_id)
    if user_id is not None:
        statement = statement.where(Resume.user_id == user_id)

    db_resume = db.scalar(statement)

    if not db_resume:
        logger.error(
            "Resume record not found in database: resume_id=%s, user_id=%s",
            resume_id,
            user_id,
        )
        raise ResumeNotFoundError(
            f"Resume record with ID {resume_id} was not found or access is denied."
        )

    file_path = UPLOAD_DIR / db_resume.stored_filename

    if not file_path.exists():
        logger.error("Resume document file missing from disk: %s", file_path)
        raise ResumeFileNotFoundError(
            f"Resume file '{db_resume.original_filename}' does not exist on the server."
        )

    if not file_path.is_file() or file_path.stat().st_size == 0:
        logger.error(
            "Resume document file is invalid or 0 bytes: %s", file_path
        )
        raise ResumeFileNotFoundError(
            f"Resume file '{db_resume.original_filename}' is empty or invalid."
        )

    logger.debug(
        "Resume validation successful for ID %s (Path: %s)",
        resume_id,
        file_path,
    )
    return db_resume, file_path


def build_analysis_result(
    resume: Resume,
    extracted_text: str,
    structured_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Construct a standardized result dictionary combining resume metadata, extracted text, and AI JSON.

    Args:
        resume: The validated Resume database model instance.
        extracted_text: Cleaned plain text extracted from the document.
        structured_data: AI-extracted structured JSON dictionary from Gemini.

    Returns:
        Unified dictionary payload containing resume metadata and structured AI analysis.
    """
    uploaded_at_iso = (
        resume.uploaded_at.isoformat() if resume.uploaded_at else None
    )

    return {
        "status": "success",
        "resume_id": resume.id,
        "user_id": resume.user_id,
        "original_filename": resume.original_filename,
        "file_type": resume.file_type,
        "file_size": resume.file_size,
        "uploaded_at": uploaded_at_iso,
        "extracted_text": extracted_text,
        "structured_data": structured_data,
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }


# ============================================================================
# Core Service Orchestration
# ============================================================================


def analyze_resume(
    db: Session,
    resume_id: int,
    user_id: Optional[int] = None,
    api_key: Optional[str] = None,
    force_refresh: bool = False,
) -> Dict[str, Any]:
    """Orchestrate the end-to-end resume analysis pipeline.

    1. Validates resume DB record and disk file using validate_resume().
    2. Checks in-memory cache (_ANALYSIS_CACHE) to reuse existing parsed structured JSON.
    3. Extracts text using parser_service.parse_uploaded_resume() if cache miss.
    4. Parses structured JSON using gemini_resume_parser.parse_resume_with_gemini().
    5. Caches and returns unified analysis result payload.

    Args:
        db: Active SQLAlchemy database session.
        resume_id: Target resume ID to analyze.
        user_id: Optional user ID for ownership validation.
        api_key: Optional Google Gemini API key override.
        force_refresh: Force bypass of in-memory parsed resume cache.

    Returns:
        Structured dictionary payload containing metadata, extracted text, and AI JSON.

    Raises:
        ResumeNotFoundError: If resume DB record is not found or unauthorized.
        ResumeFileNotFoundError: If resume document file is missing or empty on disk.
        ResumeQuotaExhaustedError: If Gemini returns HTTP 429 quota exhausted.
        ResumeAnalysisFailedError: If text extraction or Gemini AI parsing fails.
    """
    logger.info(
        "Starting resume analysis pipeline for resume_id=%s (user_id=%s)",
        resume_id,
        user_id,
    )

    # 1. Validate database record & disk file
    db_resume, file_path = validate_resume(
        db, resume_id=resume_id, user_id=user_id
    )

    current_mtime = file_path.stat().st_mtime
    target_model = get_gemini_model()

    # 2. Check thread-safe in-memory cache
    if not force_refresh:
        with _CACHE_LOCK:
            cached_entry = _ANALYSIS_CACHE.get(resume_id)
            if cached_entry:
                if (
                    cached_entry.get("mtime") == current_mtime
                    and cached_entry.get("model") == target_model
                    and cached_entry.get("structured_data")
                ):
                    logger.info(
                        "Cache hit for resume_id=%s (model=%s). Reusing parsed structured JSON.",
                        resume_id,
                        target_model,
                    )
                    return build_analysis_result(
                        resume=db_resume,
                        extracted_text=cached_entry["extracted_text"],
                        structured_data=cached_entry["structured_data"],
                    )

    # 3. Extract and clean text using parser_service
    try:
        logger.info(
            "Extracting plain text for resume_id=%s from %s",
            resume_id,
            file_path,
        )
        extracted_text = parse_uploaded_resume(file_path)
    except TextExtractorError as exc:
        logger.error("Text extraction failed for resume_id=%s: %s", resume_id, exc)
        raise ResumeAnalysisFailedError(
            f"Failed to extract text from resume '{db_resume.original_filename}': {exc}"
        ) from exc
    except Exception as exc:
        logger.error(
            "Unexpected text extraction error for resume_id=%s: %s",
            resume_id,
            exc,
            exc_info=True,
        )
        raise ResumeAnalysisFailedError(
            f"Unexpected text extraction failure for resume '{db_resume.original_filename}': {exc}"
        ) from exc

    # 4. Call Gemini AI Resume Parser
    try:
        logger.info("Executing Gemini AI parsing for resume_id=%s (Model: %s)", resume_id, target_model)
        structured_data = parse_resume_with_gemini(
            resume_text=extracted_text,
            api_key=api_key,
        )
    except GeminiQuotaExhaustedError as exc:
        logger.error("Gemini quota exhausted for resume_id=%s: %s", resume_id, exc)
        raise ResumeQuotaExhaustedError(
            "Gemini API quota is temporarily exhausted. Please wait and try again."
        ) from exc
    except GeminiParserError as exc:
        logger.error(
            "Gemini AI parsing failed for resume_id=%s: %s", resume_id, exc
        )
        raise ResumeAnalysisFailedError(
            f"Gemini AI resume parsing failed for '{db_resume.original_filename}': {exc}"
        ) from exc
    except Exception as exc:
        err_str = str(exc)
        logger.error(
            "Unexpected AI parsing error for resume_id=%s: %s",
            resume_id,
            err_str,
            exc_info=True,
        )
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
            raise ResumeQuotaExhaustedError(
                "Gemini API quota is temporarily exhausted. Please wait and try again."
            ) from exc
        raise ResumeAnalysisFailedError(
            f"Unexpected AI parsing error for '{db_resume.original_filename}': {exc}"
        ) from exc

    # Store successful parse in thread-safe in-memory cache
    with _CACHE_LOCK:
        _ANALYSIS_CACHE[resume_id] = {
            "mtime": current_mtime,
            "model": target_model,
            "extracted_text": extracted_text,
            "structured_data": structured_data,
        }

    # 5. Construct and return structured analysis result
    result = build_analysis_result(
        resume=db_resume,
        extracted_text=extracted_text,
        structured_data=structured_data,
    )

    logger.info(
        "Successfully completed resume analysis pipeline for resume_id=%s",
        resume_id,
    )
    return result


def analyze_resume_ats(
    db: Session,
    resume_id: int,
    user_id: Optional[int] = None,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute resume analysis and calculate ATS score breakdown.

    Reuses analyze_resume to obtain structured JSON from Gemini AI and passes
    it to evaluate_ats_score from app.ai.ats_engine.

    Args:
        db: Active SQLAlchemy database session.
        resume_id: Target resume ID.
        user_id: Optional user ID for ownership validation.
        api_key: Optional Google Gemini API key override.

    Returns:
        Structured payload containing metadata, structured JSON, and ATS score breakdown.
    """
    logger.info("Starting ATS analysis pipeline for resume_id=%s", resume_id)

    # 1. Reuse existing analyze_resume service to extract & parse resume
    analysis_result = analyze_resume(
        db=db,
        resume_id=resume_id,
        user_id=user_id,
        api_key=api_key,
    )

    # 2. Evaluate ATS Score using ATS engine
    try:
        from app.ai.ats_engine import evaluate_ats_score

        ats_score = evaluate_ats_score(analysis_result["structured_data"])
    except Exception as exc:
        logger.error(
            "ATS score evaluation failed for resume_id=%s: %s",
            resume_id,
            exc,
            exc_info=True,
        )
        raise ResumeAnalysisFailedError(
            f"ATS score evaluation failed: {exc}"
        ) from exc

    return {
        "status": "success",
        "resume_id": analysis_result["resume_id"],
        "user_id": analysis_result["user_id"],
        "original_filename": analysis_result["original_filename"],
        "ats_score": ats_score,
        "structured_data": analysis_result["structured_data"],
    }


def analyze_resume_skill_gap(
    db: Session,
    resume_id: int,
    target_role: str,
    user_id: Optional[int] = None,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute resume analysis and calculate Skill Gap Analysis against a target job role.

    Reuses analyze_resume to obtain structured JSON from Gemini AI and passes
    it to evaluate_skill_gap from app.ai.skill_gap_engine.

    Args:
        db: Active SQLAlchemy database session.
        resume_id: Target resume ID.
        target_role: Target job role title (e.g., Backend Developer).
        user_id: Optional user ID for ownership validation.
        api_key: Optional Google Gemini API key override.

    Returns:
        Structured payload containing metadata and skill gap result dictionary.
    """
    logger.info(
        "Starting Skill Gap analysis pipeline for resume_id=%s (target_role=%s)",
        resume_id,
        target_role,
    )

    # 1. Reuse existing analyze_resume service to extract & parse resume
    analysis_result = analyze_resume(
        db=db,
        resume_id=resume_id,
        user_id=user_id,
        api_key=api_key,
    )

    # 2. Evaluate Skill Gap using Skill Gap engine
    try:
        from app.ai.skill_gap_engine import (
            InvalidTargetRoleError,
            evaluate_skill_gap,
        )

        skill_gap_data = evaluate_skill_gap(
            analysis_result["structured_data"], target_role=target_role
        )
    except InvalidTargetRoleError:
        raise
    except Exception as exc:
        logger.error(
            "Skill Gap analysis failed for resume_id=%s: %s",
            resume_id,
            exc,
            exc_info=True,
        )
        raise ResumeAnalysisFailedError(
            f"Skill Gap analysis failed: {exc}"
        ) from exc

    return {
        "status": "success",
        "resume_id": analysis_result["resume_id"],
        "user_id": analysis_result["user_id"],
        "original_filename": analysis_result["original_filename"],
        "skill_gap": skill_gap_data,
    }


def analyze_resume_learning_roadmap(
    db: Session,
    resume_id: int,
    target_role: str,
    user_id: Optional[int] = None,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute end-to-end Learning Roadmap generation for a candidate resume.

    Reuses analyze_resume to extract resume JSON, evaluate_ats_score to compute ATS metrics,
    and evaluate_skill_gap to identify missing skills, then passes all datasets to
    generate_learning_roadmap in app.ai.learning_roadmap_engine.

    Args:
        db: Active SQLAlchemy database session.
        resume_id: Target resume ID.
        target_role: Target job role title (e.g. Backend Developer).
        user_id: Optional user ID for ownership validation.
        api_key: Optional Google Gemini API key override.

    Returns:
        Structured payload containing metadata and generated Learning Roadmap result.
    """
    logger.info(
        "Starting Learning Roadmap analysis pipeline for resume_id=%s (target_role='%s')",
        resume_id,
        target_role,
    )

    # 1. Reuse existing analyze_resume service to extract & parse resume
    analysis_result = analyze_resume(
        db=db,
        resume_id=resume_id,
        user_id=user_id,
        api_key=api_key,
    )

    # 2. Evaluate ATS Score & Skill Gap Analysis
    try:
        from app.ai.ats_engine import evaluate_ats_score
        from app.ai.learning_roadmap_engine import generate_learning_roadmap
        from app.ai.skill_gap_engine import (
            InvalidTargetRoleError,
            evaluate_skill_gap,
        )

        ats_score = evaluate_ats_score(analysis_result["structured_data"])
        skill_gap_data = evaluate_skill_gap(
            analysis_result["structured_data"], target_role=target_role
        )
    except InvalidTargetRoleError:
        raise
    except Exception as exc:
        logger.error(
            "Prerequisite evaluation failed during Learning Roadmap generation for resume_id=%s: %s",
            resume_id,
            exc,
            exc_info=True,
        )
        raise ResumeAnalysisFailedError(
            f"Learning Roadmap prerequisite evaluation failed: {exc}"
        ) from exc

    # 3. Generate Learning Roadmap
    try:
        roadmap_data = generate_learning_roadmap(
            structured_data=analysis_result["structured_data"],
            ats_score=ats_score,
            skill_gap=skill_gap_data,
            target_role=skill_gap_data.get("target_role", target_role),
        )
    except Exception as exc:
        logger.error(
            "Learning Roadmap generation failed for resume_id=%s: %s",
            resume_id,
            exc,
            exc_info=True,
        )
        raise ResumeAnalysisFailedError(
            f"Learning Roadmap engine generation failed: {exc}"
        ) from exc

    return {
        "status": "success",
        "resume_id": analysis_result["resume_id"],
        "user_id": analysis_result["user_id"],
        "original_filename": analysis_result["original_filename"],
        "learning_roadmap": roadmap_data,
    }


def analyze_resume_job_recommendations(
    db: Session,
    resume_id: int,
    preferred_location: str = "Remote",
    experience_level: str = "Fresher",
    user_id: Optional[int] = None,
    api_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute end-to-end Job Recommendations evaluation for a candidate resume.

    Reuses analyze_resume to extract structured JSON data, then invokes
    recommend_jobs in app.ai.job_recommendation_engine.

    Args:
        db: Active SQLAlchemy database session.
        resume_id: Target resume ID.
        preferred_location: Preferred location (e.g. Remote, On-site).
        experience_level: Experience tier (Fresher, Junior, Mid-Level, Senior, Lead).
        user_id: Optional user ID for ownership validation.
        api_key: Optional Google Gemini API key override.

    Returns:
        Structured payload containing metadata and recommended_jobs list.
    """
    logger.info(
        "Starting Job Recommendations pipeline for resume_id=%s (location='%s', experience='%s')",
        resume_id,
        preferred_location,
        experience_level,
    )

    # 1. Reuse existing analyze_resume service to extract & parse resume
    analysis_result = analyze_resume(
        db=db,
        resume_id=resume_id,
        user_id=user_id,
        api_key=api_key,
    )

    # 2. Evaluate Job Recommendations
    try:
        from app.ai.job_recommendation_engine import recommend_jobs

        recommendations_data = recommend_jobs(
            structured_data=analysis_result["structured_data"],
            preferred_location=preferred_location,
            experience_level=experience_level,
        )
    except Exception as exc:
        logger.error(
            "Job Recommendation engine evaluation failed for resume_id=%s: %s",
            resume_id,
            exc,
            exc_info=True,
        )
        raise ResumeAnalysisFailedError(
            f"Job Recommendation engine failed: {exc}"
        ) from exc

    return {
        "status": "success",
        "resume_id": analysis_result["resume_id"],
        "user_id": analysis_result["user_id"],
        "original_filename": analysis_result["original_filename"],
        "recommended_jobs": recommendations_data.get("recommended_jobs", []),
    }
