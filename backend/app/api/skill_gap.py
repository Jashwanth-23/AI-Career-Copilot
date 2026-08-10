"""Skill Gap Router Module

This module defines FastAPI endpoints for analyzing candidate skill gaps against target job roles.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai.skill_gap_engine import InvalidTargetRoleError
from app.api.auth import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.skill_gap import SkillGapRequest, SkillGapResponse
from app.services.resume_analysis_service import (
    ResumeAnalysisFailedError,
    ResumeFileNotFoundError,
    ResumeNotFoundError,
    ResumeQuotaExhaustedError,
    analyze_resume_skill_gap,
)

# Logger configuration for Skill Gap API router
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume", tags=["Skill Gap Analysis"])


@router.post(
    "/skill-gap/{resume_id}",
    response_model=SkillGapResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Candidate Skill Gap against Target Role",
    description="Loads the user's resume, extracts parsed skills, and compares them against target job role skill taxonomies to identify matched, missing, and recommended skills.",
)
async def get_skill_gap_endpoint(
    resume_id: int,
    payload: SkillGapRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SkillGapResponse:
    """Analyze and return Skill Gap Analysis for an uploaded resume.

    - Authenticates user via JWT.
    - Verifies requested resume belongs to current_user.
    - Calls analyze_resume_skill_gap to compare candidate skills against target_role requirements.
    - Returns full Skill Gap payload.
    """
    logger.info(
        "Received request for Skill Gap Analysis on resume_id=%s (target_role='%s') from user_id=%s",
        resume_id,
        payload.target_role,
        current_user.id,
    )

    try:
        result = analyze_resume_skill_gap(
            db=db,
            resume_id=resume_id,
            target_role=payload.target_role,
            user_id=current_user.id,
        )
        return SkillGapResponse(**result)

    except InvalidTargetRoleError as exc:
        logger.warning(
            "Invalid target role '%s' requested for resume_id=%s: %s",
            payload.target_role,
            resume_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

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
            "Gemini quota exhausted during Skill Gap analysis for resume_id=%s: %s",
            resume_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Gemini API quota is temporarily exhausted. Please wait and try again.",
        ) from exc

    except ResumeAnalysisFailedError as exc:
        logger.error(
            "Skill Gap analysis failed for resume_id=%s: %s",
            resume_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Skill Gap analysis failed: {exc}",
        ) from exc

    except Exception as exc:
        logger.error(
            "Unexpected error during Skill Gap analysis for resume_id=%s: %s",
            resume_id,
            exc,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while processing Skill Gap Analysis.",
        ) from exc
