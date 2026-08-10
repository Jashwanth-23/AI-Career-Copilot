"""Learning Roadmap Router Module

This module defines FastAPI endpoints for generating personalized AI learning roadmaps for resumes.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.ai.skill_gap_engine import InvalidTargetRoleError
from app.api.auth import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.learning_roadmap import (
    LearningRoadmapRequest,
    LearningRoadmapResponse,
)
from app.services.resume_analysis_service import (
    ResumeAnalysisFailedError,
    ResumeFileNotFoundError,
    ResumeNotFoundError,
    ResumeQuotaExhaustedError,
    analyze_resume_learning_roadmap,
)

# Logger configuration for Learning Roadmap API router
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume", tags=["Learning Roadmap Engine"])


@router.post(
    "/learning-roadmap/{resume_id}",
    response_model=LearningRoadmapResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Personalized AI Learning Roadmap",
    description="Generates a multi-week personalized learning roadmap based on candidate resume analysis, ATS scores, skill gaps, and target job role.",
)
async def get_learning_roadmap_endpoint(
    resume_id: int,
    payload: LearningRoadmapRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LearningRoadmapResponse:
    """Generate and return a personalized Learning Roadmap for an uploaded resume.

    - Authenticates user via JWT.
    - Verifies requested resume belongs to current_user.
    - Calls analyze_resume_learning_roadmap to build a tailored weekly roadmap.
    - Returns full Learning Roadmap payload.
    """
    logger.info(
        "Received request for Learning Roadmap on resume_id=%s (target_role='%s') from user_id=%s",
        resume_id,
        payload.target_role,
        current_user.id,
    )

    try:
        result = analyze_resume_learning_roadmap(
            db=db,
            resume_id=resume_id,
            target_role=payload.target_role,
            user_id=current_user.id,
        )
        return LearningRoadmapResponse(**result)

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
            "Gemini quota exhausted during Learning Roadmap generation for resume_id=%s: %s",
            resume_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Gemini API quota is temporarily exhausted. Please wait and try again.",
        ) from exc

    except ResumeAnalysisFailedError as exc:
        logger.error(
            "Learning Roadmap generation failed for resume_id=%s: %s",
            resume_id,
            exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Learning Roadmap generation failed: {exc}",
        ) from exc

    except Exception as exc:
        logger.error(
            "Unexpected error during Learning Roadmap generation for resume_id=%s: %s",
            resume_id,
            exc,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating the Learning Roadmap.",
        ) from exc
