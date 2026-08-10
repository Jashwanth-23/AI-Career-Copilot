"""
Authentication Router Module

This module defines FastAPI authentication endpoints with diagnostic logging:
- POST /register : User registration with execution time tracking
- POST /login    : User authentication and JWT access token issuance
- GET /me        : Authenticated user profile retrieval
"""

import logging
import time
import traceback
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.jwt_handler import create_access_token, verify_access_token
from app.auth.password import verify_password
from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.user_service import create_user, get_user_by_email

# Logger configuration for Auth API router
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


# ------------------------------------------------------------------
# Dependency: Current User Extractor
# ------------------------------------------------------------------
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency that validates the Bearer JWT token and retrieves the current User entity.
    """
    token = credentials.credentials
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email: str = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new user account after validating that the email address is unique."
)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Registers a new user account with step-by-step diagnostic timing logs.
    """
    t_req_start = time.perf_counter()
    logger.info(f"=== [API /register START] Request received for email: '{user_in.email}' ===")

    try:
        # Step 1: Request Validation (Pydantic completed upon function entry)
        t_val = time.perf_counter()
        logger.info(f"[STEP 1/7 SUCCESS] Request validation passed: name='{user_in.name}', email='{user_in.email}' (Time: {(t_val - t_req_start)*1000:.2f}ms)")

        # Step 2: DB Session Availability
        logger.info(f"[STEP 2/7 SUCCESS] Database session established via Depends(get_db)")

        # Step 3: Check if Email Exists
        t_check_start = time.perf_counter()
        logger.info(f"[STEP 3/7 START] Checking database for existing user email: '{user_in.email}'")
        existing_user = get_user_by_email(db, user_in.email)
        t_check_duration = (time.perf_counter() - t_check_start) * 1000
        logger.info(f"[STEP 3/7 END] Check email exists finished in {t_check_duration:.2f}ms")

        if existing_user:
            logger.warning(f"[STEP 3/7 REJECT] Email '{user_in.email}' is already registered in DB.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered"
            )

        # Step 4-6: Create User (Hash password, add user to session, commit transaction, refresh)
        t_create_start = time.perf_counter()
        logger.info("[STEP 4-6 START] Invoking create_user service...")
        new_user = create_user(db, user_in)
        t_create_duration = (time.perf_counter() - t_create_start) * 1000
        logger.info(f"[STEP 4-6 END] User creation service finished in {t_create_duration:.2f}ms (Created User ID: #{new_user.id})")

        # Step 7: Return Response
        t_total_duration = (time.perf_counter() - t_req_start) * 1000
        logger.info(f"=== [API /register SUCCESS] User #{new_user.id} registered successfully in {t_total_duration:.2f}ms ===")
        return new_user

    except HTTPException:
        # Re-raise HTTP exceptions cleanly
        raise
    except Exception as exc:
        t_err_duration = (time.perf_counter() - t_req_start) * 1000
        tb_str = traceback.format_exc()
        logger.error(f"=== [API /register ERROR] Registration exception after {t_err_duration:.2f}ms: {exc} ===\n{tb_str}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed due to a server error: {str(exc)}"
        ) from exc


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticates user credentials and returns a JWT access token."
)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
) -> dict:
    """
    Authenticates a user and issues a signed JWT access token.
    """
    t_login_start = time.perf_counter()
    logger.info(f"[API /login START] Authenticating email: '{credentials.email}'")

    try:
        user = get_user_by_email(db, credentials.email)
        if not user or not verify_password(credentials.password, user.password):
            logger.warning(f"[API /login REJECT] Invalid credentials for email: '{credentials.email}'")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(data={"sub": user.email})
        t_duration = (time.perf_counter() - t_login_start) * 1000
        logger.info(f"[API /login SUCCESS] Issued JWT token for user #{user.id} in {t_duration:.2f}ms")
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[API /login ERROR] Login exception: {exc}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login."
        ) from exc


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Retrieves the profile of the currently authenticated user using JWT token."
)
def get_me(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Retrieves current authenticated user details.
    """
    return current_user
