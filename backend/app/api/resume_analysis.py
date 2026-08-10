"""Resume Analysis Router Module

This module defines FastAPI endpoints for analyzing uploaded resumes using Gemini AI
and checking Gemini API integration health.
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.gemini_client import check_gemini_health
from app.database.database import get_db
from app.models.user import User
from app.schemas.resume_analysis import ResumeAnalysisResponse
from app.services.resume_analysis_service import (
    ResumeAnalysisFailedError,
    ResumeFileNotFoundError,
    ResumeNotFoundError,
    ResumeQuotaExhaustedError,
    analyze_resume,
)

# Logger configuration for resume analysis router
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume", tags=["Resume Analysis"])


@router.get(
    "/gemini-health",
    status_code=status.HTTP_200_OK,
    summary="Check Gemini API Integration Health",
    description="Diagnostic endpoint to verify API key configuration, client initialization, configured model, and minimal text generation test without exposing secrets.",
)
async def get_gemini_health_endpoint() -> Dict[str, Any]:
    """Return diagnostic status of Google Gemini API connection."""
    logger.info("Executing Gemini API health check diagnostic endpoint")
    return check_gemini_health()


@router.post(
    "/analyze/{resume_id}",
    response_model=ResumeAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze uploaded resume with Gemini AI",
    description="Loads user's uploaded resume document, extracts text, and invokes Gemini AI to parse structured resume fields.",
)
async def analyze_resume_endpoint(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeAnalysisResponse:
    """Analyze an uploaded resume and return structured JSON details.

    - Authenticates the current user via JWT.
    - Verifies resume exists and belongs to the current authenticated user.
    - Extracts text and executes Gemini AI structured parsing.
    - Returns structured JSON payload without persisting analysis to DB.
    """
    logger.info(
        "Received request to analyze resume_id=%s from user_id=%s",
        resume_id,
        current_user.id,
    )

    try:
        result = analyze_resume(
            db=db,
            resume_id=resume_id,
            user_id=current_user.id,
        )
        return ResumeAnalysisResponse(**result)

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
            "Gemini quota exhausted for resume_id=%s: %s",
            resume_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Gemini API quota is temporarily exhausted. Please wait and try again.",
        ) from exc

    except ResumeAnalysisFailedError as exc:
        logger.error(
            "Resume analysis pipeline failed for resume_id=%s: %s",
            resume_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze resume: {exc}",
        ) from exc

    except Exception as exc:
        err_str = str(exc)
        logger.error(
            "Unexpected error analyzing resume_id=%s: %s",
            resume_id,
            err_str,
            exc_info=True,
        )
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Gemini API quota is temporarily exhausted. Please wait and try again.",
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while analyzing the resume.",
        ) from exc
