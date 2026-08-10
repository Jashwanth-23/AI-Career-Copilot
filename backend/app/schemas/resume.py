"""
Resume Schemas Module

This module defines Pydantic v2 data schemas for Resume file operations:
- ResumeUploadResponse: Returned upon successful file upload
- ResumeDetails: Detailed representation of a stored Resume entity
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ResumeBase(BaseModel):
    """
    Base schema sharing core metadata attributes of a resume file.
    """
    original_filename: str = Field(
        ...,
        description="Original name of the uploaded document file"
    )
    file_type: str = Field(
        ...,
        description="MIME content type of the file (e.g., application/pdf)"
    )
    file_size: int = Field(
        ...,
        description="File size in bytes"
    )


class ResumeUploadResponse(ResumeBase):
    """
    Response schema returned after successfully uploading a resume file.
    """
    id: int = Field(
        ...,
        description="Unique primary key identifier for the stored resume"
    )
    stored_filename: str = Field(
        ...,
        description="Unique internal stored filename on disk"
    )
    uploaded_at: datetime = Field(
        ...,
        description="Upload timestamp in UTC"
    )
    message: str = Field(
        default="Resume uploaded successfully",
        description="Status message confirming upload success"
    )

    # Enable ORM attribute extraction for Pydantic v2
    model_config = ConfigDict(from_attributes=True)


class ResumeDetails(ResumeBase):
    """
    Schema representing full details of a stored Resume entity.
    """
    id: int = Field(
        ...,
        description="Unique primary key identifier for the resume"
    )
    user_id: int = Field(
        ...,
        description="Foreign key ID of the user who owns this resume"
    )
    stored_filename: str = Field(
        ...,
        description="Unique internal stored filename on disk"
    )
    uploaded_at: datetime = Field(
        ...,
        description="Upload timestamp in UTC"
    )

    # Enable ORM attribute extraction for Pydantic v2
    model_config = ConfigDict(from_attributes=True)
