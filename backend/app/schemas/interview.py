"""
Interview Schemas Module

This module defines Pydantic v2 validation schemas for the AI Mock Interview endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class InterviewStartRequest(BaseModel):
    """Payload to create and launch a new mock interview session."""

    resume_id: int = Field(..., description="ID of active uploaded resume to personalize interview")
    target_role: str = Field(..., min_length=2, max_length=255, description="Target job position")
    interview_type: str = Field(
        default="technical",
        description="Category of interview: technical, behavioral, hr, system_design, mixed, resume_based"
    )
    difficulty: str = Field(
        default="medium",
        description="Difficulty level: easy, medium, hard"
    )
    total_questions: int = Field(
        default=3,
        description="Number of questions in session (3, 5, 10, or 15)"
    )

    @field_validator("interview_type")
    @classmethod
    def validate_interview_type(cls, v: str) -> str:
        valid_types = {"technical", "behavioral", "hr", "system_design", "mixed", "resume_based"}
        v_clean = v.strip().lower()
        if v_clean not in valid_types:
            raise ValueError(f"Invalid interview_type. Must be one of: {', '.join(sorted(valid_types))}")
        return v_clean

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        valid_diffs = {"easy", "medium", "hard"}
        v_clean = v.strip().lower()
        if v_clean not in valid_diffs:
            raise ValueError(f"Invalid difficulty. Must be one of: {', '.join(sorted(valid_diffs))}")
        return v_clean

    @field_validator("total_questions")
    @classmethod
    def validate_total_questions(cls, v: int) -> int:
        if v not in {3, 5, 10, 15}:
            raise ValueError("total_questions must be 3, 5, 10, or 15")
        return v


class InterviewAnswerRequest(BaseModel):
    """Payload to submit candidate's answer for the active question."""

    answer: str = Field(..., min_length=1, description="Candidate's text response")

    @field_validator("answer")
    @classmethod
    def validate_answer(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Answer cannot be empty or blank space.")
        return v.strip()


class QuestionSchema(BaseModel):
    """Schema representing an individual interview question and evaluation state."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    question_number: int
    question_type: str
    difficulty: str
    topic: Optional[str] = None
    question_text: str
    resume_reference: Optional[str] = None
    user_answer: Optional[str] = None
    score: Optional[int] = None
    evaluation: Optional[Dict[str, Any]] = None
    feedback: Optional[str] = None
    missing_key_points: Optional[List[str]] = None
    ideal_answer: Optional[str] = None


class InterviewSessionResponse(BaseModel):
    """Comprehensive state response for an interview session."""

    model_config = ConfigDict(from_attributes=True)

    session_id: int
    user_id: int
    resume_id: int
    target_role: str
    interview_type: str
    difficulty: str
    total_questions: int
    current_question_number: int
    status: str
    overall_score: Optional[int] = None
    performance_rating: Optional[str] = None
    current_question: Optional[QuestionSchema] = None
    questions: List[QuestionSchema] = []
    final_report: Optional[Dict[str, Any]] = None
    started_at: datetime
    completed_at: Optional[datetime] = None


class InterviewAnswerResponse(BaseModel):
    """Response payload returned immediately after evaluating an answer."""

    evaluation: Dict[str, Any]
    next_question: Optional[QuestionSchema] = None
    question_number: int
    total_questions: int
    completed: bool


class InterviewSummaryResponse(BaseModel):
    """Summary item schema for history listing."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    resume_id: int
    target_role: str
    interview_type: str
    difficulty: str
    total_questions: int
    status: str
    overall_score: Optional[int] = None
    performance_rating: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    created_at: datetime
