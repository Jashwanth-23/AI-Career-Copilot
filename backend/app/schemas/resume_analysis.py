"""Resume Analysis Schemas Module

This module defines Pydantic v2 data schemas for the AI Resume Analysis feature,
including structured JSON sub-models and API response schemas.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class PersonalInformationSchema(BaseModel):
    """Schema for candidate personal contact details."""

    name: Optional[str] = Field(default="", description="Full Name of candidate")
    email: Optional[str] = Field(default="", description="Email address")
    phone: Optional[str] = Field(default="", description="Phone number")
    location: Optional[str] = Field(
        default="", description="City, State/Country"
    )
    linkedin: Optional[str] = Field(
        default="", description="LinkedIn profile URL"
    )
    github: Optional[str] = Field(default="", description="GitHub profile URL")
    website: Optional[str] = Field(
        default="", description="Portfolio/Personal website URL"
    )


class EducationSchema(BaseModel):
    """Schema for individual education entries."""

    institution: Optional[str] = Field(
        default="", description="School or university name"
    )
    degree: Optional[str] = Field(
        default="", description="Degree earned (e.g. B.S., M.S.)"
    )
    field_of_study: Optional[str] = Field(
        default="", description="Major or field of study"
    )
    start_date: Optional[str] = Field(default="", description="Start date")
    end_date: Optional[str] = Field(
        default="", description="End date or Expected date"
    )
    gpa: Optional[str] = Field(default="", description="Grade point average")


class ExperienceSchema(BaseModel):
    """Schema for work experience entries."""

    company: Optional[str] = Field(
        default="", description="Company or organization name"
    )
    position: Optional[str] = Field(default="", description="Job title or role")
    location: Optional[str] = Field(
        default="", description="Office location or Remote"
    )
    start_date: Optional[str] = Field(
        default="", description="Employment start date"
    )
    end_date: Optional[str] = Field(
        default="", description="Employment end date or Present"
    )
    description: List[str] = Field(
        default_factory=list,
        description="Key accomplishments and responsibilities",
    )
    technologies: List[str] = Field(
        default_factory=list,
        description="Tools, frameworks, and technologies used",
    )


class ProjectSchema(BaseModel):
    """Schema for key project entries."""

    name: Optional[str] = Field(default="", description="Project name")
    description: Optional[str] = Field(
        default="", description="Project summary"
    )
    technologies: List[str] = Field(
        default_factory=list, description="Technologies used in project"
    )
    link: Optional[str] = Field(
        default="", description="Project repository or live URL"
    )


class StructuredResumeSchema(BaseModel):
    """Structured AI JSON format returned by Gemini parser."""

    personal_information: PersonalInformationSchema = Field(
        default_factory=PersonalInformationSchema,
        description="Candidate contact information",
    )
    education: List[EducationSchema] = Field(
        default_factory=list, description="Educational history"
    )
    experience: List[ExperienceSchema] = Field(
        default_factory=list, description="Work experience history"
    )
    skills: List[str] = Field(
        default_factory=list, description="Technical and soft skills"
    )
    projects: List[ProjectSchema] = Field(
        default_factory=list, description="Notable projects"
    )
    certifications: List[str] = Field(
        default_factory=list, description="Professional certifications"
    )
    languages: List[str] = Field(
        default_factory=list, description="Languages spoken"
    )
    summary: Optional[str] = Field(
        default="", description="Professional summary statement"
    )


class ResumeAnalysisResponse(BaseModel):
    """API response schema returned by POST /api/v1/resume/analyze/{resume_id}."""

    status: str = Field(
        default="success", description="Status of the analysis operation"
    )
    resume_id: int = Field(..., description="ID of the analyzed resume")
    user_id: int = Field(..., description="ID of the user owning the resume")
    original_filename: str = Field(..., description="Original uploaded filename")
    file_type: str = Field(..., description="MIME content type")
    file_size: int = Field(..., description="File size in bytes")
    uploaded_at: Optional[str] = Field(None, description="ISO upload timestamp")
    extracted_text: str = Field(
        ..., description="Cleaned plain text extracted from document"
    )
    structured_data: Dict[str, Any] = Field(
        ..., description="Structured JSON extracted by Gemini AI"
    )
    analyzed_at: str = Field(
        ..., description="Analysis completion timestamp in ISO format"
    )

    model_config = ConfigDict(from_attributes=True)
