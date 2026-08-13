"""
Interview Model Module

This module defines SQLAlchemy 2.0 ORM models for `interview_sessions`
and `interview_questions` tables for the AI Mock Interview feature.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class InterviewSession(Base):
    """
    SQLAlchemy 2.0 ORM Model for `interview_sessions` table.

    Tracks full lifecycle of an AI mock interview session.
    """

    __tablename__ = "interview_sessions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        doc="Unique primary key identifier for interview session"
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key referencing users.id"
    )

    resume_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key referencing resumes.id"
    )

    target_role: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Target job role position for the interview"
    )

    interview_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Type of interview (technical, behavioral, hr, system_design, mixed, resume_based)"
    )

    difficulty: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Difficulty level (easy, medium, hard)"
    )

    total_questions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
        doc="Total target number of questions for session"
    )

    current_question_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        doc="Current active question index (1-based)"
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
        doc="Session state (active, completed, cancelled)"
    )

    overall_score: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Final overall interview score (0-100)"
    )

    performance_rating: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        doc="Qualitative performance rating (e.g. Excellent, Strong, Satisfactory, Needs Improvement)"
    )

    final_report: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        doc="Structured JSON payload containing comprehensive final performance breakdown"
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Timestamp when interview started"
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when interview was completed"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Record creation timestamp"
    )

    # ORM relationship to generated questions
    questions: Mapped[List["InterviewQuestion"]] = relationship(
        "InterviewQuestion",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="InterviewQuestion.question_number",
        doc="ORM relationship to questions asked during this session"
    )

    def __repr__(self) -> str:
        return (
            f"<InterviewSession(id={self.id}, user_id={self.user_id}, "
            f"target_role='{self.target_role}', status='{self.status}')>"
        )


class InterviewQuestion(Base):
    """
    SQLAlchemy 2.0 ORM Model for `interview_questions` table.

    Stores individual AI generated question, candidate answer, and AI evaluation.
    """

    __tablename__ = "interview_questions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        doc="Unique primary key identifier for interview question"
    )

    session_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("interview_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key referencing interview_sessions.id"
    )

    question_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Sequence number of the question in the session (1-based)"
    )

    question_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Type of question (technical, behavioral, hr, system_design, resume_based)"
    )

    difficulty: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Difficulty level of question (easy, medium, hard)"
    )

    topic: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Topic or technical focus area of question"
    )

    question_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Exact wording of the interview question generated by AI"
    )

    resume_reference: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Reference to candidate's resume element (e.g. project name, skill, company)"
    )

    user_answer: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Text answer submitted by candidate"
    )

    score: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Evaluation overall score for this answer (0-100)"
    )

    evaluation: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        doc="Structured JSON evaluation payload from Gemini AI"
    )

    feedback: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Summary feedback for the candidate's answer"
    )

    missing_key_points: Mapped[Optional[List[str]]] = mapped_column(
        JSON,
        nullable=True,
        doc="JSON list of missing concepts or key points"
    )

    ideal_answer: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Guidance/sample ideal answer direction"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Record creation timestamp"
    )

    session: Mapped["InterviewSession"] = relationship(
        "InterviewSession",
        back_populates="questions",
        doc="ORM relationship back to parent InterviewSession"
    )

    def __repr__(self) -> str:
        return (
            f"<InterviewQuestion(id={self.id}, session_id={self.session_id}, "
            f"number={self.question_number}, score={self.score})>"
        )
