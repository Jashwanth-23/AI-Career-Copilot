"""
User Model Module

This module defines the SQLAlchemy 2.0 ORM model for the `users` table.
"""

from datetime import datetime, timezone
from typing import List, TYPE_CHECKING
from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base

if TYPE_CHECKING:
    from app.models.resume import Resume


class User(Base):
    """
    SQLAlchemy 2.0 ORM Model for the `users` table.

    Represents registered users within the application.
    """

    __tablename__ = "users"

    # Primary key identifier for the user
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        doc="Unique primary key identifier for the user"
    )

    # User's full name (maximum length 100 characters)
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Full name of the user (max 100 characters)"
    )

    # User's unique email address (indexed for fast query lookups)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        doc="Unique user email address (indexed for lookups)"
    )

    # Hashed password string (maximum length 255 characters)
    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Hashed user password string (max 255 characters)"
    )

    # Account creation timestamp (automatically set to current UTC time)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Account creation timestamp set to current UTC time"
    )

    # ORM relationship to user's uploaded resumes
    resumes: Mapped[List["Resume"]] = relationship(
        "Resume",
        back_populates="user",
        cascade="all, delete-orphan",
        doc="ORM relationship to user's uploaded resumes"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"

