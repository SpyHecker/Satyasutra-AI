"""
Authentication & User Service for SatyaSutra.

Handles password hashing (bcrypt), JWT generation/verification, and user persistence
in MongoDB (with local JSON fallback when MongoDB is unconfigured or offline).
Ensures a single legitimate Administrator account on system startup.
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from threading import Lock
from typing import Optional

import bcrypt
import jwt
from pydantic import BaseModel, EmailStr, Field

# --- MongoDB code commented out per instruction (using SQLite for login) ---
# from app.db.mongodb import (
#     is_mongodb_ready,
#     get_users_collection,
# )
from app.db.sqlite import (
    init_sqlite_db,
    save_user_sqlite,
    get_user_by_email_sqlite,
    get_user_by_id_sqlite,
)

logger = logging.getLogger(__name__)

# Security settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "satyasutra-forensic-ai-jwt-secret-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------
class UserRecord(BaseModel):
    """Full user record stored in the database."""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    email: str
    full_name: str
    role: str = "Investigator"
    badge_number: Optional[str] = "ADMIN-001"
    hashed_password: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class UserRegister(BaseModel):
    """Request model for investigator signup."""
    email: EmailStr
    password: str
    full_name: str
    role: Optional[str] = "Investigator"
    badge_number: Optional[str] = None


class UserLogin(BaseModel):
    """Request model for investigator login."""
    email: EmailStr
    password: str


class UserOut(BaseModel):
    """Public user response model without password hash."""
    id: str
    email: str
    full_name: str
    role: str
    badge_number: Optional[str] = None
    created_at: str


class TokenOut(BaseModel):
    """Access token response model."""
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------------------------------------------------------------------------
# Cryptographic Helpers
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    """Hash plaintext password with bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception as exc:
        logger.warning(f"Password verification error: {exc}")
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate signed JWT token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate signed JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError as exc:
        logger.debug(f"JWT decode error: {exc}")
        return None


# ---------------------------------------------------------------------------
# User Store (SQLite primary + JSON backup)
# ---------------------------------------------------------------------------
class UserStore:
    """Store for managing user accounts in SQLite with JSON backup."""

    def __init__(self, store_path: str = "data/users_store.json"):
        self._path = Path(store_path)
        self._lock = Lock()
        init_sqlite_db()
        self._ensure_file()
        self._sync_local_to_sqlite()
        self._ensure_admin_user()

    def _ensure_file(self):
        """Ensure storage directory and local backup file exist."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.write_text("[]", encoding="utf-8")

    def _read_local(self) -> list[dict]:
        """Read users from JSON file."""
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_local(self, records: list[dict]):
        """Write users to JSON file."""
        self._path.write_text(
            json.dumps(records, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _sync_local_to_sqlite(self):
        """Seed SQLite with existing local JSON accounts if SQLite is fresh."""
        try:
            records = self._read_local()
            for r in records:
                if not get_user_by_email_sqlite(r.get("email", "")):
                    save_user_sqlite(r)
        except Exception as exc:
            logger.warning(f"Could not sync JSON to SQLite: {exc}")

    def _ensure_admin_user(self):
        """Ensure a single legitimate administrator account exists."""
        admin_email = os.getenv("ADMIN_EMAIL", "admin@satyasutra.ai").strip().lower()
        admin_password = os.getenv("ADMIN_PASSWORD", "Admin@SatyaSutra2026!")

        # Clean out any old demo accounts
        with self._lock:
            records = self._read_local()
            cleaned = [r for r in records if r.get("email", "").lower() != "detective@satyasutra.ai"]
            if len(cleaned) != len(records):
                self._write_local(cleaned)

        existing = self.get_by_email(admin_email)
        if existing is None:
            admin_user = UserRecord(
                id="admin-001",
                email=admin_email,
                full_name="System Administrator",
                role="Administrator",
                badge_number="ADMIN-001",
                hashed_password=hash_password(admin_password),
            )
            self._save_record(admin_user)
            logger.info(f"Initialized legit administrator account in SQLite: {admin_email}")

    def _save_record(self, record: UserRecord):
        """Persist user record to SQLite and JSON backup."""
        doc = record.model_dump()
        with self._lock:
            records = self._read_local()
            records = [r for r in records if r.get("email", "").lower() != record.email.lower()]
            records.append(doc)
            self._write_local(records)

        # Persist to SQLite
        try:
            save_user_sqlite(doc)
        except Exception as exc:
            logger.warning(f"Could not persist user to SQLite: {exc}")

        # --- MongoDB code commented out per instruction (using SQLite for login) ---
        # if is_mongodb_ready():
        #     try:
        #         col = get_users_collection()
        #         if col is not None:
        #             col.replace_one({"email": record.email.lower()}, doc, upsert=True)
        #     except Exception as exc:
        #         logger.warning(f"Could not persist user to MongoDB: {exc}")

    def create_user(
        self,
        email: str,
        password: str,
        full_name: str,
        role: str = "Investigator",
        badge_number: Optional[str] = None,
    ) -> UserRecord:
        """Create and persist a new user."""
        email_clean = email.strip().lower()
        if self.get_by_email(email_clean):
            raise ValueError("An investigator account with this email already exists.")

        hashed = hash_password(password)
        record = UserRecord(
            email=email_clean,
            full_name=full_name.strip(),
            role=role.strip() if role else "Investigator",
            badge_number=badge_number.strip() if badge_number else f"SS-{uuid.uuid4().hex[:4].upper()}",
            hashed_password=hashed,
        )
        self._save_record(record)
        return record

    def get_by_email(self, email: str) -> Optional[UserRecord]:
        """Look up user by email address from SQLite."""
        email_clean = email.strip().lower()

        # Check SQLite first
        try:
            row = get_user_by_email_sqlite(email_clean)
            if row:
                return UserRecord(**row)
        except Exception as exc:
            logger.warning(f"SQLite user lookup error: {exc}")

        # --- MongoDB code commented out per instruction (using SQLite for login) ---
        # if is_mongodb_ready():
        #     try:
        #         col = get_users_collection()
        #         if col is not None:
        #             doc = col.find_one({"email": email_clean}, {"_id": 0})
        #             if doc:
        #                 return UserRecord(**doc)
        #     except Exception as exc:
        #         logger.warning(f"MongoDB user lookup error: {exc}")

        # Local JSON fallback
        with self._lock:
            records = self._read_local()
        for r in records:
            if r.get("email", "").lower() == email_clean:
                return UserRecord(**r)
        return None

    def get_by_id(self, user_id: str) -> Optional[UserRecord]:
        """Look up user by ID from SQLite."""
        # Check SQLite first
        try:
            row = get_user_by_id_sqlite(user_id)
            if row:
                return UserRecord(**row)
        except Exception as exc:
            logger.warning(f"SQLite user id lookup error: {exc}")

        # --- MongoDB code commented out per instruction (using SQLite for login) ---
        # if is_mongodb_ready():
        #     try:
        #         col = get_users_collection()
        #         if col is not None:
        #             doc = col.find_one({"id": user_id}, {"_id": 0})
        #             if doc:
        #                 return UserRecord(**doc)
        #     except Exception as exc:
        #         logger.warning(f"MongoDB user id lookup error: {exc}")

        with self._lock:
            records = self._read_local()
        for r in records:
            if r.get("id") == user_id:
                return UserRecord(**r)
        return None


# Module-level singleton
user_store = UserStore()
