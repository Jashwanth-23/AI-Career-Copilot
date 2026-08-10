"""Learning Roadmap Schemas Module

This module defines Pydantic v2 data schemas for the AI Learning Roadmap feature
including AI-generated Real-World Portfolio Projects.
"""

from typing import List
from pydantic import BaseModel, ConfigDict, Field


class LearningRoadmapRequest(BaseModel):
    """Request schema for Learning Roadmap endpoint."""

    target_role: str = Field(
        ...,
        description="Target job role (e.g., Backend Developer, AI Engineer)",
        json_schema_extra={"example": "Backend Developer"},
    )


class RoadmapWeekSchema(BaseModel):
    """Schema for individual weekly learning modules."""

    week: int = Field(..., description="Week number (1, 2, 3...)")
    focus: str = Field(..., description="Focus skill or technology for the week")
    topics: List[str] = Field(
        default_factory=list, description="List of key learning topics"
    )
    resources: List[str] = Field(
        default_factory=list,
        description="Free documentation and tutorial resources",
    )
    mini_project: str = Field(
        ..., description="Practical mini project to build during the week"
    )
    milestone: str = Field(
        ..., description="Key milestone achievement for the week"
    )


class RealWorldProjectSchema(BaseModel):
    """Schema for AI-generated real-world portfolio project."""

    title: str = Field(..., description="Project title")
    description: str = Field(..., description="Project summary description")
    difficulty: str = Field(
        default="Intermediate", description="Difficulty tier (Beginner, Intermediate, Advanced)"
    )
    estimated_duration: str = Field(
        default="2-3 Weeks", description="Estimated project build duration"
    )
    why_this_project: str = Field(
        ..., description="Why this project is specifically valuable for candidate"
    )
    technologies: List[str] = Field(
        default_factory=list, description="Technologies and frameworks used"
    )
    key_features: List[str] = Field(
        default_factory=list, description="Key features to implement"
    )
    skills_developed: List[str] = Field(
        default_factory=list, description="Skills developed by building"
    )
    skill_gap_addressed: List[str] = Field(
        default_factory=list, description="Specific missing skills addressed"
    )
    portfolio_value: str = Field(
        ..., description="How this project strengthens candidate's portfolio"
    )
    expected_outcome: str = Field(
        ..., description="What the candidate can demonstrate after completion"
    )


class LearningRoadmapResultSchema(BaseModel):
    """Structured Learning Roadmap result payload."""

    target_role: str = Field(..., description="Target job role title")
    estimated_duration: str = Field(
        ..., description="Estimated roadmap duration (e.g. '8 Weeks')"
    )
    overall_progress: int = Field(
        ..., description="Initial overall progress percentage (0-100)"
    )
    roadmap: List[RoadmapWeekSchema] = Field(
        default_factory=list, description="Ordered list of weekly learning modules"
    )
    recommended_projects: List[RealWorldProjectSchema] = Field(
        default_factory=list, description="2 to 3 AI-generated real-world projects"
    )


class LearningRoadmapResponse(BaseModel):
    """API response schema returned by POST /api/v1/resume/learning-roadmap/{resume_id}."""

    status: str = Field(
        default="success", description="Status of the operation"
    )
    resume_id: int = Field(..., description="ID of the analyzed resume")
    user_id: int = Field(..., description="ID of the user owning the resume")
    original_filename: str = Field(..., description="Original uploaded filename")
    learning_roadmap: LearningRoadmapResultSchema = Field(
        ..., description="Generated Learning Roadmap result"
    )

    model_config = ConfigDict(from_attributes=True)
