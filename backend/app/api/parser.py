"""Resume Parser Router Module

This module defines FastAPI endpoints for extracting and cleaning text
from uploaded PDF/DOCX resumes.
"""

import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.database import get_db
from app.models.resume import Resume
from app.models.user import User
from app.services.parser_service import parse_uploaded_resume
from app.ai.text_extractor import (
    EmptyFileError,
    ExtractionFailedError,
    MissingFileError,
    TextExtractorError,
    UnsupportedFileTypeError,
)

# Logger configuration
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume", tags=["Resume Parser"])

# Path where uploaded resumes are stored on disk
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BACKEND_DIR / "uploads" / "resumes"


class ResumeParseRequest(BaseModel):
    """Request schema for resume parsing endpoint."""

    resume_id: int = Field(
        ..., description="ID of the uploaded resume to parse", json_schema_extra={"example": 1}
    )


class ResumeParseResponse(BaseModel):
    """Response schema returned after parsing a resume document."""

    resume_id: int = Field(..., description="Unique ID of the resume")
    original_filename: str = Field(
        ..., description="Original filename of the document"
    )
    extracted_text: str = Field(
        ..., description="Cleaned and extracted plain text content"
    )
    message: str = Field(
        default="Resume parsed successfully",
        description="Status message confirming successful parsing",
    )


@router.post(
    "/parse",
    response_model=ResumeParseResponse,
    status_code=status.HTTP_200_OK,
    summary="Parse uploaded resume text",
    description="Loads an uploaded resume by ID, extracts and cleans text content using parser_service.",
)
async def parse_resume(
    payload: Optional[ResumeParseRequest] = Body(None),
    resume_id: Optional[int] = Query(
        None, description="Resume ID if sent via query parameter"
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeParseResponse:
    """Parses an uploaded resume and returns its extracted plain text.

    - Validates JWT authorization for current_user.
    - Accepts resume_id via JSON request body or query parameter.
    - Loads resume metadata record from the database.
    - Ensures current_user owns the requested resume.
    - Calls parser_service.parse_uploaded_resume to process the document.
    - Returns cleaned plain text content.
    """
    # Determine resume_id from JSON payload or query parameter
    target_resume_id = payload.resume_id if payload else resume_id

    if target_resume_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required parameter 'resume_id'.",
        )

    logger.info(
        "User (id=%s) requested parsing for resume_id=%s",
        current_user.id,
        target_resume_id,
    )

    # Load resume record from database for the current authenticated user
    db_resume = (
        db.query(Resume)
        .filter(Resume.id == target_resume_id, Resume.user_id == current_user.id)
        .first()
    )

    if not db_resume:
        logger.warning(
            "Resume not found or unauthorized: resume_id=%s for user_id=%s",
            target_resume_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {target_resume_id} was not found.",
        )

    # Locate uploaded file on disk
    file_path = UPLOAD_DIR / db_resume.stored_filename

    if not file_path.exists():
        logger.error("Resume file missing on disk: %s", file_path)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume file '{db_resume.original_filename}' was not found on the server.",
        )

    # Call parser_service to extract and clean text
    try:
        extracted_text = parse_uploaded_resume(file_path)
    except MissingFileError as exc:
        logger.error("Missing file during resume parse: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except EmptyFileError as exc:
        logger.error("Empty file during resume parse: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resume document '{db_resume.original_filename}' contains no extractable text.",
        ) from exc
    except UnsupportedFileTypeError as exc:
        logger.error("Unsupported file type during resume parse: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except (ExtractionFailedError, TextExtractorError) as exc:
        logger.error(
            "Text extraction failure for resume_id=%s: %s", target_resume_id, exc
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract text from resume '{db_resume.original_filename}'.",
        ) from exc
    except Exception as exc:
        logger.error(
            "Unexpected error parsing resume_id=%s: %s",
            target_resume_id,
            exc,
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while parsing the resume.",
        ) from exc

    return ResumeParseResponse(
        resume_id=db_resume.id,
        original_filename=db_resume.original_filename,
        extracted_text=extracted_text,
        message="Resume text parsed and extracted successfully.",
    )
