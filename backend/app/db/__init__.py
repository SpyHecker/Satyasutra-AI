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

__all__ = [
    "get_mongodb_client",
    "get_database",
    "is_mongodb_ready",
    "get_evidence_collection",
    "get_users_collection",
    "close_mongodb_connection",
]
