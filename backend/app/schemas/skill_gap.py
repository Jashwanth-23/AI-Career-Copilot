"""Skill Gap Schemas Module

This module defines Pydantic v2 data schemas for the Skill Gap Analysis feature.
"""

from typing import List
from pydantic import BaseModel, ConfigDict, Field


class SkillGapRequest(BaseModel):
    """Request schema for Skill Gap Analysis endpoint."""

    target_role: str = Field(
        ...,
        description="Target job role (e.g. Backend Developer, AI Engineer)",
        json_schema_extra={"example": "Backend Developer"},
    )


class SkillGapResultSchema(BaseModel):
    """Detailed Skill Gap Analysis result payload matching module specifications."""

    target_role: str = Field(..., description="Target job role title")
    matched_skills: List[str] = Field(
        default_factory=list,
        description="List of skills matched from candidate resume",
    )
    missing_skills: List[str] = Field(
        default_factory=list,
        description="List of core required skills missing from candidate resume",
    )
    recommended_skills: List[str] = Field(
        default_factory=list,
        description="List of recommended secondary skills for career advancement",
    )
    match_percentage: int = Field(
        ..., description="Skill match percentage (0-100)"
    )
    priority_learning_order: List[str] = Field(
        default_factory=list,
        description="Prioritized list of missing skills recommended to learn first",
    )


class SkillGapResponse(BaseModel):
    """API response schema returned by POST /api/v1/resume/skill-gap/{resume_id}."""

    status: str = Field(
        default="success", description="Status of the operation"
    )
    resume_id: int = Field(..., description="ID of the analyzed resume")
    user_id: int = Field(..., description="ID of the user owning the resume")
    original_filename: str = Field(..., description="Original uploaded filename")
    skill_gap: SkillGapResultSchema = Field(
        ..., description="Calculated Skill Gap Analysis result"
    )

    model_config = ConfigDict(from_attributes=True)
