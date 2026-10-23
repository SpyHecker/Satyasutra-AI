"""
Database package for SatyaSutra.
"""
from app.db.mongodb import (
    get_mongodb_client,
    get_database,
    is_mongodb_ready,
    get_evidence_collection,
    get_users_collection,
    close_mongodb_connection,
)

from app.db.sqlite import (
    init_sqlite_db,
    save_user_sqlite,
    get_user_by_email_sqlite,
    get_user_by_id_sqlite,
    get_all_users_sqlite,
    get_db_path,
)

__all__ = [
    "get_mongodb_client",
    "get_database",
    "is_mongodb_ready",
    "get_evidence_collection",
    "get_users_collection",
    "close_mongodb_connection",
    "init_sqlite_db",
    "save_user_sqlite",
    "get_user_by_email_sqlite",
    "get_user_by_id_sqlite",
    "get_all_users_sqlite",
    "get_db_path",
]
