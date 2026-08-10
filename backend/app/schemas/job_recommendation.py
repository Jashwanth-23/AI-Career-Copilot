"""Job Recommendation Schemas Module

This module defines Pydantic v2 data schemas for the AI Job Recommendation Engine feature.
"""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class JobRecommendationRequest(BaseModel):
    """Request schema for Job Recommendation endpoint."""

    preferred_location: Optional[str] = Field(
        default="Remote",
        description="Preferred work location (e.g., Remote, On-site, Hybrid)",
        json_schema_extra={"example": "Remote"},
    )
    experience_level: Optional[str] = Field(
        default="Fresher",
        description="Experience tier (Fresher, Junior, Mid-Level, Senior, Lead)",
        json_schema_extra={"example": "Fresher"},
    )


class RecommendedJobSchema(BaseModel):
    """Schema for an individual recommended job role."""

    role: str = Field(..., description="Job role title")
    match_percentage: int = Field(
        ..., description="Match score percentage (0-100)"
    )
    salary_range: str = Field(
        ..., description="Approximate estimated salary range"
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Candidate strengths aligned with this job role",
    )
    missing_skills: List[str] = Field(
        default_factory=list,
        description="Missing skills required to excel in this role",
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Actionable career recommendations for this role",
    )


class JobRecommendationResponse(BaseModel):
    """API response schema returned by POST /api/v1/resume/job-recommendations/{resume_id}."""

    status: str = Field(
        default="success", description="Status of the operation"
    )
    resume_id: int = Field(..., description="ID of the analyzed resume")
    user_id: int = Field(..., description="ID of the user owning the resume")
    original_filename: str = Field(..., description="Original uploaded filename")
    recommended_jobs: List[RecommendedJobSchema] = Field(
        ..., description="List of recommended job roles matching candidate profile"
    )

    model_config = ConfigDict(from_attributes=True)
