"""
Resume Router Module

This module defines FastAPI endpoints for resume file uploading,
file validation, local storage management, and database record persistence.
"""

import logging
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.resume import ResumeDetails, ResumeUploadResponse
from app.services.resume_service import (
    delete_resume as delete_resume_service,
    get_resume_by_id,
    get_resume_by_user,
    get_user_resumes,
    save_resume,
)

# Logger configuration
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume", tags=["Resumes"])

# Constants
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB limit
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}

# Target file storage path: backend/uploads/resumes
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = BACKEND_DIR / "uploads" / "resumes"


@router.post(
    "/upload",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload resume document",
    description="Uploads a PDF or DOCX resume document (max 5MB) for the authenticated user."
)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ResumeUploadResponse:
    """
    Uploads a resume file for the authenticated user.
    """
    original_name = file.filename or "resume"
    file_ext = Path(original_name).suffix.lower()

    if file_ext not in ALLOWED_EXTENSIONS and file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF (.pdf) and DOCX (.docx) files are supported."
        )

    try:
        content = await file.read()
    except Exception as err:
        logger.error(f"Failed to read uploaded file stream: {str(err)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read uploaded file content."
        )

    file_size = len(content)

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds the 5 MB maximum limit (received {file_size / (1024 * 1024):.2f} MB)."
        )

    try:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as err:
        logger.error(f"Failed to create upload directory {UPLOAD_DIR}: {str(err)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Storage directory initialization failed on the server."
        )

    unique_prefix = uuid.uuid4().hex
    safe_filename = Path(original_name).name
    stored_filename = f"{unique_prefix}_{safe_filename}"
    file_path = UPLOAD_DIR / stored_filename

    try:
        with open(file_path, "wb") as f:
            f.write(content)

        content_type = file.content_type or "application/octet-stream"
        db_resume = save_resume(
            db=db,
            user_id=current_user.id,
            original_filename=original_name,
            stored_filename=stored_filename,
            file_type=content_type,
            file_size=file_size,
        )
        return db_resume

    except Exception as err:
        db.rollback()
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as cleanup_err:
                logger.error(f"Failed to clean up orphan file {file_path}: {str(cleanup_err)}")

        logger.error(f"Error during resume upload process: {str(err)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while saving the resume: {str(err)}"
        )


@router.get(
    "/history",
    response_model=List[ResumeDetails],
    status_code=status.HTTP_200_OK,
    summary="Get user's uploaded resume history",
    description="Retrieves all resume records uploaded by the currently authenticated user."
)
def get_resume_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[ResumeDetails]:
    """Retrieves all resume records uploaded by current_user."""
    return get_user_resumes(db, current_user.id)


@router.get(
    "/latest",
    response_model=Optional[ResumeDetails],
    status_code=status.HTTP_200_OK,
    summary="Get user's latest active resume",
    description="Retrieves the most recently uploaded resume for the authenticated user."
)
def get_latest_resume(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Optional[ResumeDetails]:
    """Retrieves current_user's latest uploaded resume."""
    return get_resume_by_user(db, current_user.id)


@router.get(
    "/download/{resume_id}",
    summary="Download original resume document",
    description="Securely streams the requested original resume file for the authenticated owner."
)
def download_resume(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Downloads original resume file by ID."""
    db_resume = get_resume_by_id(db, resume_id=resume_id, user_id=current_user.id)
    if not db_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} was not found."
        )

    file_path = UPLOAD_DIR / db_resume.stored_filename
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume file does not exist on server disk."
        )

    return FileResponse(
        path=str(file_path),
        filename=db_resume.original_filename,
        media_type=db_resume.file_type
    )


@router.delete(
    "/{resume_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete uploaded resume",
    description="Removes a resume record from the database and deletes the physical file from disk."
)
def delete_resume_endpoint(
    resume_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """Deletes resume record and disk file."""
    db_resume = get_resume_by_id(db, resume_id=resume_id, user_id=current_user.id)
    if not db_resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {resume_id} was not found."
        )

    file_path = UPLOAD_DIR / db_resume.stored_filename
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as cleanup_err:
            logger.warning(f"Failed to remove file from disk: {cleanup_err}")

    delete_resume_service(db, resume_id=resume_id, user_id=current_user.id)
    return {"message": f"Resume #{resume_id} deleted successfully."}


@router.post(
    "/replace",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Replace current resume with a new file",
    description="Uploads a new resume file for current user and removes previous active resume."
)
async def replace_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ResumeUploadResponse:
    """Replaces current resume with a new upload."""
    old_resume = get_resume_by_user(db, current_user.id)
    new_resume = await upload_resume(file=file, current_user=current_user, db=db)

    if old_resume:
        old_path = UPLOAD_DIR / old_resume.stored_filename
        if old_path.exists():
            try:
                old_path.unlink()
            except Exception:
                pass
        delete_resume_service(db, resume_id=old_resume.id, user_id=current_user.id)

    return new_resume

