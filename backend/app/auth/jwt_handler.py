"""
JWT Token Handler Module

This module provides utility functions for creating and verifying JSON Web Tokens (JWT)
for user authentication using `python-jose`.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt

from app.core.config import settings


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generates a signed JWT access token containing the payload data and expiration claim.

    Args:
        data (Dict[str, Any]): Dictionary payload to encode inside the JWT token (e.g. {"sub": email}).
        expires_delta (Optional[timedelta]): Custom expiration duration. If None, defaults to
                                             `settings.ACCESS_TOKEN_EXPIRE_MINUTES`.

    Returns:
        str: Encoded JWT string signed with application SECRET_KEY.
    """
    to_encode = data.copy()

    # Use timezone-aware UTC timestamp
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    # Encode JWT using secret key and configured algorithm
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodes and verifies a JWT access token.

    Args:
        token (str): Encoded JWT string to decode and verify.

    Returns:
        Optional[Dict[str, Any]]: Decoded claims payload if valid; None if expired or invalid signature.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
