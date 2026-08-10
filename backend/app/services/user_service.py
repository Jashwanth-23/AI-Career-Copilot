"""
User Service Module

This module provides data access layer helper functions for User operations
using SQLAlchemy 2.0 with performance timing diagnostics.
"""

import logging
import time
import traceback
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.password import hash_password
from app.models.user import User
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Retrieves a User record from the database by email address.
    """
    t_start = time.perf_counter()
    logger.info(f"[DB STEP START] Checking if email exists: '{email}'")
    
    try:
        statement = select(User).where(User.email == email)
        result = db.scalar(statement)
        t_duration = (time.perf_counter() - t_start) * 1000
        logger.info(f"[DB STEP SUCCESS] Check email exists completed in {t_duration:.2f}ms. Found: {result is not None}")
        return result
    except Exception as exc:
        t_duration = (time.perf_counter() - t_start) * 1000
        logger.error(f"[DB STEP ERROR] Check email exists failed after {t_duration:.2f}ms: {exc}", exc_info=True)
        raise


def create_user(db: Session, user_in: UserCreate) -> User:
    """
    Hashes the user password and creates a new User record in the database
    with granular diagnostic step timing logs.
    """
    t_create_start = time.perf_counter()

    # Step: Hash Password
    t_hash_start = time.perf_counter()
    logger.info(f"[STEP START] Password Hashing for email: '{user_in.email}'")
    try:
        hashed_pwd = hash_password(user_in.password)
        t_hash_duration = (time.perf_counter() - t_hash_start) * 1000
        logger.info(f"[STEP SUCCESS] Password Hashing completed in {t_hash_duration:.2f}ms")
    except Exception as exc:
        logger.error(f"[STEP ERROR] Password Hashing failed: {exc}", exc_info=True)
        raise

    # Step: Create User Object
    t_obj_start = time.perf_counter()
    logger.info("[STEP START] Creating SQLAlchemy User ORM Object")
    db_user = User(
        name=user_in.name,
        email=user_in.email,
        password=hashed_pwd,
    )
    t_obj_duration = (time.perf_counter() - t_obj_start) * 1000
    logger.info(f"[STEP SUCCESS] User ORM Object instantiated in {t_obj_duration:.2f}ms")

    # Step: Add User to Session
    t_add_start = time.perf_counter()
    logger.info("[STEP START] Adding User to DB Session")
    db.add(db_user)
    t_add_duration = (time.perf_counter() - t_add_start) * 1000
    logger.info(f"[STEP SUCCESS] User added to session in {t_add_duration:.2f}ms")

    # Step: Commit Transaction
    t_commit_start = time.perf_counter()
    logger.info("[STEP START] Executing Session.commit() to persist User")
    try:
        db.commit()
        t_commit_duration = (time.perf_counter() - t_commit_start) * 1000
        logger.info(f"[STEP SUCCESS] Session.commit() completed in {t_commit_duration:.2f}ms")
    except Exception as exc:
        t_commit_duration = (time.perf_counter() - t_commit_start) * 1000
        logger.error(f"[STEP ERROR] Session.commit() failed/blocked after {t_commit_duration:.2f}ms: {exc}", exc_info=True)
        db.rollback()
        raise

    # Step: Refresh User
    t_refresh_start = time.perf_counter()
    logger.info("[STEP START] Executing Session.refresh() for created User")
    try:
        db.refresh(db_user)
        t_refresh_duration = (time.perf_counter() - t_refresh_start) * 1000
        logger.info(f"[STEP SUCCESS] Session.refresh() completed in {t_refresh_duration:.2f}ms. Assigned User ID: #{db_user.id}")
    except Exception as exc:
        t_refresh_duration = (time.perf_counter() - t_refresh_start) * 1000
        logger.error(f"[STEP ERROR] Session.refresh() failed after {t_refresh_duration:.2f}ms: {exc}", exc_info=True)
        raise

    t_total = (time.perf_counter() - t_create_start) * 1000
    logger.info(f"[USER SERVICE SUMMARY] Total user creation service execution time: {t_total:.2f}ms")

    return db_user
