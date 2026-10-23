"""
Authentication routes for SatyaSutra.

Provides endpoints for investigator registration, login, current session lookup,
and database status checks.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Header, status

from app.services.auth_service import (
    user_store,
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    UserRegister,
    UserLogin,
    UserOut,
    TokenOut,
    UserRecord,
)
from app.db.mongodb import is_mongodb_ready, get_mongodb_db_name

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Dependency: Extract Current User from Bearer Token
# ---------------------------------------------------------------------------
async def get_current_user(authorization: Optional[str] = Header(None)) -> UserRecord:
    """Validate Bearer JWT token and return authenticated user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ", 1)[1].strip()
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid credentials. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    user = user_store.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_optional_current_user(authorization: Optional[str] = Header(None)) -> Optional[UserRecord]:
    """Optionally validate token without raising 401 if missing."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ", 1)[1].strip()
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    return user_store.get_by_id(payload.get("sub"))


# ---------------------------------------------------------------------------
# Auth Endpoints
# ---------------------------------------------------------------------------
@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister):
    """
    Register a new investigator account.
    Returns access token and user profile on success.
    """
    if len(payload.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long.",
        )

    try:
        user = user_store.create_user(
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
            role=payload.role or "Investigator",
            badge_number=payload.badge_number,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})

    return TokenOut(
        access_token=token,
        token_type="bearer",
        user=UserOut(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            badge_number=user.badge_number,
            created_at=user.created_at,
        ),
    )


@router.post("/login", response_model=TokenOut)
async def login(payload: UserLogin):
    """
    Sign in to an existing investigator or administrator account with email and password.
    Returns access token and user profile.
    """
    user = user_store.get_by_email(payload.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = create_access_token({"sub": user.id, "email": user.email, "role": user.role})

    return TokenOut(
        access_token=token,
        token_type="bearer",
        user=UserOut(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            badge_number=user.badge_number,
            created_at=user.created_at,
        ),
    )


@router.get("/me", response_model=UserOut)
async def get_my_profile(current_user: UserRecord = Depends(get_current_user)):
    """Retrieve currently authenticated investigator's profile."""
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        badge_number=current_user.badge_number,
        created_at=current_user.created_at,
    )


@router.get("/status")
async def get_auth_and_db_status():
    """Return status of authentication provider and MongoDB database connection."""
    mongo_ready = is_mongodb_ready()
    return {
        "auth_enabled": True,
        "database": {
            "type": "mongodb" if mongo_ready else "local_fallback",
            "mongodb_connected": mongo_ready,
            "database_name": get_mongodb_db_name() if mongo_ready else "data/json_store",
        },
    }
