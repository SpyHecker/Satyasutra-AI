"""
SQLite Database Manager for SatyaSutra.

Provides lightweight, zero-configuration local relational persistence for the
authentication and user system using Python's built-in sqlite3 standard library.
"""

import os
import sqlite3
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from contextlib import contextmanager

logger = logging.getLogger(__name__)

DB_PATH = Path(os.getenv("SQLITE_DB_PATH", "data/satyasutra.db"))


def get_db_path() -> Path:
    """Return the absolute Path to the SQLite database file."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return DB_PATH


@contextmanager
def get_db_connection():
    """Context manager for obtaining a SQLite connection with row-factory."""
    db_file = get_db_path()
    conn = sqlite3.connect(str(db_file), timeout=10.0)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_sqlite_db():
    """Create essential tables for users and authentication if not already present."""
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'Investigator',
                badge_number TEXT,
                hashed_password TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)
        # Index for fast email lookups during login
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        """)
    logger.info(f"✅ SQLite auth database initialized at {get_db_path().resolve()}")


def save_user_sqlite(user_dict: Dict[str, Any]) -> None:
    """Insert or update a user record in SQLite."""
    with get_db_connection() as conn:
        conn.execute("""
            INSERT INTO users (id, email, full_name, role, badge_number, hashed_password, created_at)
            VALUES (:id, :email, :full_name, :role, :badge_number, :hashed_password, :created_at)
            ON CONFLICT(email) DO UPDATE SET
                full_name = excluded.full_name,
                role = excluded.role,
                badge_number = excluded.badge_number,
                hashed_password = excluded.hashed_password;
        """, user_dict)


def get_user_by_email_sqlite(email: str) -> Optional[Dict[str, Any]]:
    """Look up a user in SQLite by email (case-insensitive)."""
    email_clean = email.strip().lower()
    with get_db_connection() as conn:
        cursor = conn.execute(
            "SELECT * FROM users WHERE LOWER(email) = LOWER(?) LIMIT 1;",
            (email_clean,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
    return None


def get_user_by_id_sqlite(user_id: str) -> Optional[Dict[str, Any]]:
    """Look up a user in SQLite by primary key ID."""
    with get_db_connection() as conn:
        cursor = conn.execute(
            "SELECT * FROM users WHERE id = ? LIMIT 1;",
            (user_id,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
    return None


def get_all_users_sqlite() -> List[Dict[str, Any]]:
    """List all registered users from SQLite."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM users ORDER BY created_at ASC;")
        return [dict(row) for row in cursor.fetchall()]
