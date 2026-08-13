"""
Mock Interview Router Module

Defines FastAPI REST API endpoints for the AI Mock Interview feature.
Enforces strict JWT authorization and user data isolation.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.gemini_client import GeminiQuotaExhaustedError, GeminiServiceError
from app.database.database import get_db
from app.models.user import User
from app.schemas.interview import (
    InterviewAnswerRequest,
    InterviewAnswerResponse,
    InterviewSessionResponse,
    InterviewStartRequest,
    InterviewSummaryResponse,
    QuestionSchema,
)
from app.services.mock_interview_service import (
    MockInterviewServiceError,
    SessionAlreadyCompletedError,
    SessionNotFoundError,
    delete_interview,
    finalize_session_report,
    get_report,
    get_session,
    get_user_history,
    start_interview,
    submit_answer,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/interview", tags=["AI Mock Interview"])


@router.post(
    "/start",
    response_model=InterviewSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new personalized AI mock interview session",
)
def api_start_interview(
    payload: InterviewStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start a new AI-powered mock interview initialized with candidate's active resume."""
    try:
        session, q1 = start_interview(
            db=db,
            user_id=current_user.id,
            resume_id=payload.resume_id,
            target_role=payload.target_role,
            interview_type=payload.interview_type,
            difficulty=payload.difficulty,
            total_questions=payload.total_questions,
        )
        return {
            "session_id": session.id,
            "user_id": session.user_id,
            "resume_id": session.resume_id,
            "target_role": session.target_role,
            "interview_type": session.interview_type,
            "difficulty": session.difficulty,
            "total_questions": session.total_questions,
            "current_question_number": session.current_question_number,
            "status": session.status,
            "overall_score": session.overall_score,
            "performance_rating": session.performance_rating,
            "current_question": q1,
            "questions": [q1],
            "final_report": session.final_report,
            "started_at": session.started_at,
            "completed_at": session.completed_at,
        }
    except GeminiQuotaExhaustedError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI interview service is temporarily unavailable due to quota limits. Please try again later.",
        )
    except MockInterviewServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.error("Error starting interview session: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize AI interview session.",
        )


@router.get(
    "/session/{session_id}",
    response_model=InterviewSessionResponse,
    summary="Get active interview session state (Browser refresh safe)",
)
def api_get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve state of an interview session belonging to the authenticated user."""
    try:
        session, active_question = get_session(db, user_id=current_user.id, session_id=session_id)
        return {
            "session_id": session.id,
            "user_id": session.user_id,
            "resume_id": session.resume_id,
            "target_role": session.target_role,
            "interview_type": session.interview_type,
            "difficulty": session.difficulty,
            "total_questions": session.total_questions,
            "current_question_number": session.current_question_number,
            "status": session.status,
            "overall_score": session.overall_score,
            "performance_rating": session.performance_rating,
            "current_question": active_question,
            "questions": session.questions,
            "final_report": session.final_report,
            "started_at": session.started_at,
            "completed_at": session.completed_at,
        }
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception as exc:
        logger.error("Error fetching session state: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve interview session.",
        )


@router.post(
    "/session/{session_id}/answer",
    response_model=InterviewAnswerResponse,
    summary="Submit candidate's answer and get AI evaluation",
)
def api_submit_answer(
    session_id: int,
    payload: InterviewAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit text answer for current question, receive live AI evaluation, and obtain next question."""
    try:
        result = submit_answer(
            db=db,
            user_id=current_user.id,
            session_id=session_id,
            user_answer=payload.answer,
        )
        return result
    except GeminiQuotaExhaustedError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI interview service is temporarily unavailable due to quota limits. Please try again later.",
        )
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except SessionAlreadyCompletedError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except MockInterviewServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.error("Error submitting interview answer: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process and evaluate interview answer.",
        )


@router.post(
    "/session/{session_id}/finish",
    summary="Finalize interview session and generate performance report",
)
def api_finish_interview(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Finalize an active interview session early or after all questions are complete."""
    try:
        session, _ = get_session(db, user_id=current_user.id, session_id=session_id)
        updated_session = finalize_session_report(db, session)
        return {
            "session_id": updated_session.id,
            "status": updated_session.status,
            "overall_score": updated_session.overall_score,
            "performance_rating": updated_session.performance_rating,
            "final_report": updated_session.final_report,
            "completed_at": updated_session.completed_at,
        }
    except GeminiQuotaExhaustedError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI interview service is temporarily unavailable due to quota limits. Please try again later.",
        )
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception as exc:
        logger.error("Error finishing interview session: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to finalize interview session report.",
        )


@router.get(
    "/session/{session_id}/report",
    summary="Get final performance report for completed interview",
)
def api_get_report(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch final performance report for a completed session."""
    try:
        return get_report(db, user_id=current_user.id, session_id=session_id)
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception as exc:
        logger.error("Error retrieving interview report: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve final interview report.",
        )


@router.get(
    "/history",
    response_model=List[InterviewSummaryResponse],
    summary="Get history of past interview sessions for authenticated user",
)
def api_get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve history of user's mock interview practice sessions."""
    try:
        return get_user_history(db, user_id=current_user.id)
    except Exception as exc:
        logger.error("Error fetching interview history: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve interview history.",
        )


@router.delete(
    "/session/{session_id}",
    summary="Delete an interview session",
)
def api_delete_interview(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an interview session from user history."""
    try:
        delete_interview(db, user_id=current_user.id, session_id=session_id)
        return {
            "status": "success",
            "message": "Interview session deleted successfully.",
        }
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except Exception as exc:
        logger.error("Error deleting interview session: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete interview session.",
        )
