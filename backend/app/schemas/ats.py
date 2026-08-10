"""ATS Schemas Module

This module defines Pydantic v2 data schemas for the ATS Score Engine feature.
"""

from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict, Field


class ATSScoreBreakdownSchema(BaseModel):
    """Schema for ATS score breakdown and qualitative feedback."""

    overall_score: int = Field(..., description="Overall ATS score (0-100)")
    skills_score: int = Field(..., description="Skills evaluation score (0-100)")
    experience_score: int = Field(
        ..., description="Experience evaluation score (0-100)"
    )
    education_score: int = Field(
        ..., description="Education evaluation score (0-100)"
    )
    projects_score: int = Field(
        ..., description="Projects evaluation score (0-100)"
    )
    completeness_score: int = Field(
        ..., description="Profile completeness score (0-100)"
    )
    strengths: List[str] = Field(
        default_factory=list, description="Identified resume strengths"
    )
    weaknesses: List[str] = Field(
        default_factory=list, description="Identified resume weaknesses"
    )
    improvement_suggestions: List[str] = Field(
        default_factory=list, description="Actionable improvement recommendations"
    )


class ATSAnalysisResponse(BaseModel):
    """Full API response schema returned by POST /api/v1/resume/ats/{resume_id}."""

    status: str = Field(
        default="success", description="Status of the operation"
    )
    resume_id: int = Field(..., description="ID of the analyzed resume")
    user_id: int = Field(..., description="ID of the user owning the resume")
    original_filename: str = Field(..., description="Original uploaded filename")
    ats_score: ATSScoreBreakdownSchema = Field(
        ..., description="Calculated ATS score breakdown"
    )
    structured_data: Dict[str, Any] = Field(
        ..., description="Structured JSON extracted by Gemini AI"
    )

    model_config = ConfigDict(from_attributes=True)
