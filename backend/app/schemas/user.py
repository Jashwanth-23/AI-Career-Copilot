"""
User Schemas Module

This module defines Pydantic v2 data validation schemas for User registration,
login authentication, and API response serialization.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """
    Base schema containing common user fields.
    """
    email: EmailStr = Field(
        ...,
        description="User valid email address"
    )


class UserCreate(UserBase):
    """
    Schema required for creating a new user account.
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Full name of the user (1 to 100 characters)"
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=255,
        description="User plain text password (minimum 6 characters)"
    )


class UserLogin(BaseModel):
    """
    Schema required for user authentication / login.
    """
    email: EmailStr = Field(
        ...,
        description="User registered email address"
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="User plain text password"
    )


class UserResponse(UserBase):
    """
    Schema returned in API responses representing a User entity.
    Excludes sensitive fields such as password.
    """
    id: int = Field(
        ...,
        description="Unique primary key identifier for the user"
    )
    name: str = Field(
        ...,
        description="Full name of the user"
    )
    created_at: datetime = Field(
        ...,
        description="Account creation timestamp in UTC"
    )

    # Enable ORM attribute extraction for FastAPI response model conversion
    model_config = ConfigDict(from_attributes=True)
