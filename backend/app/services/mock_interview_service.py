"""
Mock Interview Service Module

Orchestrates database persistence, user ownership validation, structured resume retrieval,
and Gemini AI interview engine interactions for session management.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.ai.mock_interview_engine import (
    evaluate_interview_answer,
    generate_final_interview_report,
    generate_interview_question,
)
from app.models.interview import InterviewQuestion, InterviewSession
from app.models.resume import Resume
from app.services.resume_analysis_service import (
    ResumeAnalysisError,
    analyze_resume,
    validate_resume,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Custom Service Exceptions
# ============================================================================


class MockInterviewServiceError(Exception):
    """Base exception class for Mock Interview service operations."""

    pass


class SessionNotFoundError(MockInterviewServiceError):
    """Raised when an interview session is not found or access is unauthorized."""

    pass


class SessionAlreadyCompletedError(MockInterviewServiceError):
    """Raised when attempting to submit answer to an already completed interview session."""

    pass


# ============================================================================
# Core Business Logic Services
# ============================================================================


def start_interview(
    db: Session,
    user_id: int,
    resume_id: int,
    target_role: str,
    interview_type: str = "technical",
    difficulty: str = "medium",
    total_questions: int = 3,
) -> Tuple[InterviewSession, InterviewQuestion]:
    """Initialize a new interview session and generate the first question.

    Args:
        db: Active SQLAlchemy database session.
        user_id: ID of the authenticated user.
        resume_id: Primary key of user's active uploaded resume.
        target_role: Desired job role position.
        interview_type: Category of interview.
        difficulty: Level of difficulty.
        total_questions: Target total questions count (3, 5, 10, 15).

    Returns:
        Tuple containing the created (InterviewSession, InterviewQuestion).

    Raises:
        MockInterviewServiceError: On validation failure or resume access denied.
    """
    logger.info("Starting new interview session for user_id=%s, resume_id=%s", user_id, resume_id)

    # 1. Enforce resume ownership & disk file existence
    try:
        validate_resume(db, resume_id, user_id=user_id)
    except ResumeAnalysisError as exc:
        logger.error("Resume validation failed for start_interview: %s", exc)
        raise MockInterviewServiceError(str(exc)) from exc

    # 2. Get structured resume analysis data (uses in-memory cache or extracts)
    try:
        analysis_result = analyze_resume(db, resume_id, user_id=user_id)
        structured_resume = analysis_result.get("structured_data", {})
    except Exception as exc:
        logger.warning("Failed to parse detailed structured resume, using fallback: %s", exc)
        structured_resume = {"skills": [], "projects": [], "experience": [], "education": []}

    # 3. Create InterviewSession record
    session = InterviewSession(
        user_id=user_id,
        resume_id=resume_id,
        target_role=target_role.strip(),
        interview_type=interview_type.strip().lower(),
        difficulty=difficulty.strip().lower(),
        total_questions=total_questions,
        current_question_number=1,
        status="active",
        started_at=datetime.now(timezone.utc),
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # 4. Generate Question 1 via Gemini AI
    q1_data = generate_interview_question(
        target_role=session.target_role,
        interview_type=session.interview_type,
        difficulty=session.difficulty,
        question_number=1,
        total_questions=session.total_questions,
        structured_resume=structured_resume,
        previous_questions=None,
    )

    q1 = InterviewQuestion(
        session_id=session.id,
        question_number=1,
        question_type=q1_data.get("question_type", session.interview_type),
        difficulty=q1_data.get("difficulty", session.difficulty),
        topic=q1_data.get("topic"),
        question_text=q1_data.get("question", f"Explain key concepts for {target_role}."),
        resume_reference=q1_data.get("resume_reference"),
    )
    db.add(q1)
    db.commit()
    db.refresh(q1)

    logger.info("Successfully created interview session ID=%s with Question 1 ID=%s", session.id, q1.id)
    return session, q1


def get_session(
    db: Session,
    user_id: int,
    session_id: int,
) -> Tuple[InterviewSession, Optional[InterviewQuestion]]:
    """Retrieve session state enforcing current user ownership (Browser refresh safe).

    Args:
        db: Database session.
        user_id: ID of the authenticated user.
        session_id: Interview session primary key.

    Returns:
        Tuple of (InterviewSession, active_question).

    Raises:
        SessionNotFoundError: If session does not exist or belongs to another user.
    """
    stmt = (
        select(InterviewSession)
        .options(selectinload(InterviewSession.questions))
        .where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == user_id,
        )
    )
    session = db.scalar(stmt)

    if not session:
        raise SessionNotFoundError(f"Interview session with ID {session_id} was not found or access is denied.")

    # Find the current active question matching session.current_question_number
    active_question = None
    for q in session.questions:
        if q.question_number == session.current_question_number:
            active_question = q
            break

    if not active_question and session.questions:
        active_question = session.questions[-1]

    return session, active_question


def submit_answer(
    db: Session,
    user_id: int,
    session_id: int,
    user_answer: str,
) -> Dict[str, Any]:
    """Submit answer for current question, evaluate with Gemini, and advance to next question or complete.

    Args:
        db: Database session.
        user_id: Authenticated user ID.
        session_id: Active session ID.
        user_answer: Submitted text answer.

    Returns:
        Dictionary containing evaluation feedback, next_question (if any), and status flags.

    Raises:
        SessionNotFoundError: If session not found or user unauthorized.
        SessionAlreadyCompletedError: If session is already completed.
    """
    session, active_question = get_session(db, user_id, session_id)

    if session.status == "completed":
        raise SessionAlreadyCompletedError(f"Interview session {session_id} has already been completed.")

    if not active_question:
        raise MockInterviewServiceError(f"No active question found for session {session_id}.")

    logger.info(
        "Evaluating answer for session_id=%s, Q%d/%d",
        session_id,
        active_question.question_number,
        session.total_questions,
    )

    # 1. Evaluate answer using Gemini AI
    eval_result = evaluate_interview_answer(
        question_text=active_question.question_text,
        user_answer=user_answer,
        target_role=session.target_role,
        interview_type=session.interview_type,
        difficulty=session.difficulty,
        topic=active_question.topic,
    )

    # 2. Persist answer & evaluation into active_question record
    active_question.user_answer = user_answer
    active_question.score = eval_result.get("overall_score")
    active_question.evaluation = eval_result
    active_question.feedback = eval_result.get("improvement")
    active_question.missing_key_points = eval_result.get("missing_points")
    active_question.ideal_answer = eval_result.get("ideal_answer")
    db.commit()
    db.refresh(active_question)

    next_q_model: Optional[InterviewQuestion] = None
    is_completed = False

    # 3. Check if session has more questions or needs completion
    if session.current_question_number < session.total_questions:
        next_num = session.current_question_number + 1
        session.current_question_number = next_num
        db.commit()

        # Build previous questions history for context-aware adaptive next question
        prev_questions_data = []
        for q in session.questions:
            if q.user_answer:
                prev_questions_data.append(
                    {
                        "question_number": q.question_number,
                        "question_text": q.question_text,
                        "user_answer": q.user_answer,
                        "score": q.score,
                    }
                )

        # Retrieve structured resume context
        try:
            analysis_result = analyze_resume(db, session.resume_id, user_id=user_id)
            structured_resume = analysis_result.get("structured_data", {})
        except Exception:
            structured_resume = {}

        # Generate next question via Gemini
        next_q_data = generate_interview_question(
            target_role=session.target_role,
            interview_type=session.interview_type,
            difficulty=session.difficulty,
            question_number=next_num,
            total_questions=session.total_questions,
            structured_resume=structured_resume,
            previous_questions=prev_questions_data,
        )

        next_q_model = InterviewQuestion(
            session_id=session.id,
            question_number=next_num,
            question_type=next_q_data.get("question_type", session.interview_type),
            difficulty=next_q_data.get("difficulty", session.difficulty),
            topic=next_q_data.get("topic"),
            question_text=next_q_data.get("question", f"Next question for {session.target_role}"),
            resume_reference=next_q_data.get("resume_reference"),
        )
        db.add(next_q_model)
        db.commit()
        db.refresh(next_q_model)
    else:
        # Final question answered! Finalize interview session.
        is_completed = True
        finalize_session_report(db, session)

    return {
        "evaluation": eval_result,
        "next_question": next_q_model,
        "question_number": session.current_question_number,
        "total_questions": session.total_questions,
        "completed": is_completed,
    }


def finalize_session_report(
    db: Session,
    session: InterviewSession,
) -> InterviewSession:
    """Generate final report and finalize session state.

    Args:
        db: Database session.
        session: Active InterviewSession model instance.

    Returns:
        Updated InterviewSession model instance.
    """
    logger.info("Finalizing session ID=%s", session.id)

    # Collect evaluations from all answered questions
    eval_records = []
    for q in session.questions:
        eval_records.append(
            {
                "question_number": q.question_number,
                "question_text": q.question_text,
                "user_answer": q.user_answer or "",
                "score": q.score or 0,
                "topic": q.topic or "General",
            }
        )

    # Generate report with Gemini AI
    final_report = generate_final_interview_report(
        target_role=session.target_role,
        interview_type=session.interview_type,
        difficulty=session.difficulty,
        questions_evaluations=eval_records,
    )

    session.status = "completed"
    session.overall_score = final_report.get("overall_score", 80)
    session.performance_rating = final_report.get("performance_rating", "Strong")
    session.final_report = final_report
    session.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(session)
    return session


def get_report(
    db: Session,
    user_id: int,
    session_id: int,
) -> Dict[str, Any]:
    """Retrieve final report for a completed session enforcing user ownership.

    Args:
        db: Database session.
        user_id: Authenticated user ID.
        session_id: Target session ID.

    Returns:
        Final report dictionary payload.

    Raises:
        SessionNotFoundError: If session not found or user unauthorized.
    """
    session, _ = get_session(db, user_id, session_id)

    if session.status != "completed" or not session.final_report:
        session = finalize_session_report(db, session)

    return {
        "session_id": session.id,
        "target_role": session.target_role,
        "interview_type": session.interview_type,
        "difficulty": session.difficulty,
        "total_questions": session.total_questions,
        "overall_score": session.overall_score,
        "performance_rating": session.performance_rating,
        "completed_at": session.completed_at,
        "report": session.final_report,
    }


def get_user_history(
    db: Session,
    user_id: int,
) -> List[InterviewSession]:
    """Retrieve history of all interview sessions for authenticated user ordered by created_at desc.

    Args:
        db: Database session.
        user_id: Authenticated user ID.

    Returns:
        List of InterviewSession instances.
    """
    stmt = (
        select(InterviewSession)
        .where(InterviewSession.user_id == user_id)
        .order_by(InterviewSession.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def delete_interview(
    db: Session,
    user_id: int,
    session_id: int,
) -> bool:
    """Delete an interview session enforcing user ownership.

    Args:
        db: Database session.
        user_id: Authenticated user ID.
        session_id: Target session ID to delete.

    Returns:
        True if deleted successfully.

    Raises:
        SessionNotFoundError: If session not found or user unauthorized.
    """
    session, _ = get_session(db, user_id, session_id)
    db.delete(session)
    db.commit()
    logger.info("Deleted interview session ID=%s for user_id=%s", session_id, user_id)
    return True
