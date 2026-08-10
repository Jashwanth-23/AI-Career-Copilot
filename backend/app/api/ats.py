"""ATS Score Engine Router Module

This module defines FastAPI endpoints for calculating ATS scores and feedback for uploaded resumes.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.ats import ATSAnalysisResponse
from app.services.resume_analysis_service import (
    ResumeAnalysisFailedError,
    ResumeFileNotFoundError,
    ResumeNotFoundError,
    ResumeQuotaExhaustedError,
    analyze_resume_ats,
)

# Logger configuration for ATS API router
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume", tags=["ATS Score Engine"])


@router.post(
    "/ats/{resume_id}",
    response_model=ATSAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate ATS Score and Feedback",
    description="Loads the user's resume, parses structured fields, and evaluates overall ATS scores, strengths, weaknesses, and improvement suggestions.",
)
async def get_ats_score_endpoint(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ATSAnalysisResponse:
    """Calculate and return ATS score analysis for an uploaded resume.

    - Authenticates user via JWT.
    - Verifies the requested resume belongs to current_user.
    - Calls analyze_resume_ats to run text extraction, Gemini parsing, and ATS scoring.
    - Returns full ATS analysis payload.
    """
    logger.info(
        "Received request for ATS analysis on resume_id=%s from user_id=%s",
        resume_id,
        current_user.id,
    )

    try:
        result = analyze_resume_ats(
            db=db,
            resume_id=resume_id,
            user_id=current_user.id,
        )
        return ATSAnalysisResponse(**result)

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
            "Gemini quota exhausted during ATS analysis for resume_id=%s: %s",
            resume_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Gemini API quota is temporarily exhausted. Please wait and try again.",
        ) from exc

    except ResumeAnalysisFailedError as exc:
        logger.error(
            "ATS analysis failed for resume_id=%s: %s",
            resume_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ATS analysis failed: {exc}",
        ) from exc

    except Exception as exc:
        logger.error(
            "Unexpected error during ATS analysis for resume_id=%s: %s",
            resume_id,
            exc,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while calculating the ATS score.",
        ) from exc
