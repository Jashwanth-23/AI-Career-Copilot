"""
Password Hashing and Verification Module

This module provides password hashing and verification utilities
using Passlib with the bcrypt hashing algorithm.
"""

import bcrypt
from passlib.context import CryptContext

# ------------------------------------------------------------------
# Passlib 1.7.4 & Bcrypt 4.0+ Compatibility Patch
# ------------------------------------------------------------------
# Ensures smooth operation between Passlib and Bcrypt >= 4.0
if not hasattr(bcrypt, "__about__"):
    setattr(bcrypt, "__about__", type("about", (), {"__version__": getattr(bcrypt, "__version__", "4.0.0")}))

# Prevent recursive monkey-patching loop on module reloads
if not getattr(bcrypt.hashpw, "__is_patched__", False):
    _original_hashpw = bcrypt.hashpw

    def _patched_hashpw(password: bytes, salt: bytes) -> bytes:
        if isinstance(password, str):
            password = password.encode("utf-8")
        if len(password) > 72:
            password = password[:72]
        return _original_hashpw(password, salt)

    _patched_hashpw.__is_patched__ = True
    bcrypt.hashpw = _patched_hashpw

# ------------------------------------------------------------------
# CryptContext Configuration
# ------------------------------------------------------------------
# Reusable CryptContext instance configured for bcrypt hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hashes a plain text password using the bcrypt algorithm.

    Args:
        password (str): Plain text password to hash.

    Returns:
        str: Securely hashed password string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a stored hashed password.

    Args:
        plain_password (str): Plain text password submitted by user.
        hashed_password (str): Stored hashed password to verify against.

    Returns:
        bool: True if password matches the hash, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)
