"""
Resume Model Module

This module defines the SQLAlchemy 2.0 ORM model for the `resumes` table.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class Resume(Base):
    """
    SQLAlchemy 2.0 ORM Model for the `resumes` table.

    Represents uploaded resume documents linked to users.
    """

    __tablename__ = "resumes"

    # Unique primary key identifier for the resume
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        doc="Unique primary key identifier"
    )

    # Foreign key referencing the user who owns this resume
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Foreign key referencing users.id"
    )

    # Original filename as uploaded by the user
    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Original filename of uploaded document"
    )

    # Unique stored filename on filesystem/storage
    stored_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        doc="Unique internal stored filename"
    )

    # MIME file type (e.g. application/pdf, application/vnd.openxmlformats-officedocument.wordprocessingml.document)
    file_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="MIME content type of the file"
    )

    # File size in bytes
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="File size in bytes"
    )

    # Timestamp recording when the resume was uploaded (UTC)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Upload timestamp in UTC"
    )

    # Relationship linking back to the User model
    user: Mapped["User"] = relationship(
        "User",
        back_populates="resumes",
        doc="ORM relationship to the User model"
    )

    def __repr__(self) -> str:
        return (
            f"<Resume(id={self.id}, user_id={self.user_id}, "
            f"original_filename='{self.original_filename}')>"
        )
