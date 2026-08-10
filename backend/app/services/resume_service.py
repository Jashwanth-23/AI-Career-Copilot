"""
Resume Service Module

This module provides data access layer helper functions for Resume database operations
using SQLAlchemy 2.0.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.resume import Resume


def save_resume(
    db: Session,
    user_id: int,
    original_filename: str,
    stored_filename: str,
    file_type: str,
    file_size: int,
) -> Resume:
    """
    Creates and persists a new Resume entity in the database.

    Args:
        db (Session): Active SQLAlchemy database session.
        user_id (int): ID of the user owning the resume.
        original_filename (str): Original name of the uploaded file.
        stored_filename (str): Internal stored filename on disk.
        file_type (str): MIME content type of the file.
        file_size (int): Size of the file in bytes.

    Returns:
        Resume: The newly created and refreshed Resume model instance.
    """
    resume = Resume(
        user_id=user_id,
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_type=file_type,
        file_size=file_size,
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    return resume


def get_resume_by_user(db: Session, user_id: int) -> Optional[Resume]:
    """
    Retrieves the most recent Resume record for a specified user ID.

    Args:
        db (Session): Active SQLAlchemy database session.
        user_id (int): User ID to look up.

    Returns:
        Optional[Resume]: The latest Resume instance if found, None otherwise.
    """
    statement = (
        select(Resume)
        .where(Resume.user_id == user_id)
        .order_by(Resume.uploaded_at.desc())
    )
    return db.scalar(statement)


def get_user_resumes(db: Session, user_id: int) -> list[Resume]:
    """
    Retrieves all Resume records for a specified user ID ordered by uploaded_at descending.

    Args:
        db (Session): Active SQLAlchemy database session.
        user_id (int): User ID to look up.

    Returns:
        list[Resume]: List of Resume instances.
    """
    statement = (
        select(Resume)
        .where(Resume.user_id == user_id)
        .order_by(Resume.uploaded_at.desc())
    )
    return list(db.scalars(statement).all())


def get_resume_by_id(db: Session, resume_id: int, user_id: Optional[int] = None) -> Optional[Resume]:
    """
    Retrieves a Resume record by ID, optionally enforcing user ownership.

    Args:
        db (Session): Active SQLAlchemy database session.
        resume_id (int): Resume ID to retrieve.
        user_id (Optional[int]): Optional user ID to enforce authorization.

    Returns:
        Optional[Resume]: Resume instance if found, None otherwise.
    """
    statement = select(Resume).where(Resume.id == resume_id)
    if user_id is not None:
        statement = statement.where(Resume.user_id == user_id)
    return db.scalar(statement)


def delete_resume(db: Session, resume_id: int, user_id: int) -> bool:
    """
    Deletes a Resume record from the database if owned by the specified user.

    Args:
        db (Session): Active SQLAlchemy database session.
        resume_id (int): Resume ID to delete.
        user_id (int): User ID of owner.

    Returns:
        bool: True if deleted, False if record was not found or unauthorized.
    """
    resume = get_resume_by_id(db, resume_id=resume_id, user_id=user_id)
    if not resume:
        return False

    db.delete(resume)
    db.commit()
    return True

