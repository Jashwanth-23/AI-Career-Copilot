"""Job Recommendation Router Module

This module defines FastAPI endpoints for generating AI job recommendations for candidate resumes.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.job_recommendation import (
    JobRecommendationRequest,
    JobRecommendationResponse,
)
from app.services.resume_analysis_service import (
    ResumeAnalysisFailedError,
    ResumeFileNotFoundError,
    ResumeNotFoundError,
    ResumeQuotaExhaustedError,
    analyze_resume_job_recommendations,
)

# Logger configuration for Job Recommendation API router
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume", tags=["Job Recommendation Engine"])


@router.post(
    "/job-recommendations/{resume_id}",
    response_model=JobRecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate AI Job Recommendations",
    description="Evaluates candidate resume skills, ATS metrics, and experience against 10 tech roles to return ranked job recommendations and salary estimates.",
)
async def get_job_recommendations_endpoint(
    resume_id: int,
    payload: JobRecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> JobRecommendationResponse:
    """Generate and return AI Job Recommendations for an uploaded resume.

    - Authenticates user via JWT.
    - Verifies requested resume belongs to current_user.
    - Calls analyze_resume_job_recommendations to evaluate 10 tech job suitabilities.
    - Returns full Job Recommendations payload.
    """
    location = payload.preferred_location or "Remote"
    experience = payload.experience_level or "Fresher"

    logger.info(
        "Received request for Job Recommendations on resume_id=%s (location='%s', experience='%s') from user_id=%s",
        resume_id,
        location,
        experience,
        current_user.id,
    )

    try:
        result = analyze_resume_job_recommendations(
            db=db,
            resume_id=resume_id,
            preferred_location=location,
            experience_level=experience,
            user_id=current_user.id,
        )
        return JobRecommendationResponse(**result)

    except ResumeNotFoundError as exc:
        logger.warning(
            "Resume not found or access denied for resume_id=%s (user_id=%s): %s",
            resume_id,
            current_user.id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} was not found or access is denied.",
        ) from exc

    except ResumeFileNotFoundError as exc:
        logger.error(
            "Resume document file missing or empty for resume_id=%s: %s",
            resume_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ResumeQuotaExhaustedError as exc:
        logger.error(
            "Gemini quota exhausted during Job Recommendation evaluation for resume_id=%s: %s",
            resume_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Gemini API quota is temporarily exhausted. Please wait and try again.",
        ) from exc

    except ResumeAnalysisFailedError as exc:
        logger.error(
            "Job Recommendation evaluation failed for resume_id=%s: %s",
            resume_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job Recommendation evaluation failed: {exc}",
        ) from exc

    except Exception as exc:
        logger.error(
            "Unexpected error during Job Recommendation evaluation for resume_id=%s: %s",
            resume_id,
            exc,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing Job Recommendations.",
        ) from exc
