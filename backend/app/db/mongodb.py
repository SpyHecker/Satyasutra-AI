"""
MongoDB Connection Manager for SatyaSutra.

Connects to MongoDB using the configured MONGODB_URL environment variable.
Supports both local MongoDB instances and cloud-hosted MongoDB Atlas clusters.
Provides graceful fallback indicators if MongoDB is offline or unconfigured.
"""

import os
import re
import logging
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

# Module-level connection state
_client: Optional[MongoClient] = None
_db: Optional[Database] = None
_is_connected: bool = False
_connection_attempted: bool = False


def _mask_mongo_url(url: str) -> str:
    """Mask credentials in MongoDB connection string for safe logging."""
    if not url:
        return ""
    return re.sub(r"://([^:]+):([^@]+)@", r"://\1:****@", url)


def get_mongodb_url() -> str:
    """Retrieve MongoDB connection URL from environment."""
    return os.getenv("MONGODB_URL") or os.getenv("MONGO_URI") or ""


def get_mongodb_db_name() -> str:
    """Retrieve MongoDB database name from environment (defaults to 'satyasutra')."""
    return os.getenv("MONGODB_DB_NAME", "satyasutra")


def connect_to_mongodb() -> bool:
    """
    Establish connection to MongoDB and test liveness with a ping.
    Returns True if connection succeeded, False otherwise.
    """
    global _client, _db, _is_connected, _connection_attempted

    _connection_attempted = True
    url = get_mongodb_url()

    if not url:
        logger.info("ℹ️ MONGODB_URL not specified in environment. Using local file store fallback.")
        _is_connected = False
        return False

    db_name = get_mongodb_db_name()
    safe_url = _mask_mongo_url(url)
    logger.info(f"Connecting to MongoDB at {safe_url} (db: {db_name})...")

    try:
        # 2.5 second timeout for server selection to keep startup fast
        try:
            import certifi
            ca_file = certifi.where()
        except Exception:
            ca_file = None

        kwargs = {"serverSelectionTimeoutMS": 2500}
        if ca_file:
            kwargs["tlsCAFile"] = ca_file

        _client = MongoClient(url, **kwargs)
        # Verify connection
        _client.admin.command("ping")
        _db = _client[db_name]
        _is_connected = True
        logger.info(f"✅ Successfully connected to MongoDB database '{db_name}'.")

        # Initialize collections & indexes
        _init_indexes(_db)
        return True

    except (ServerSelectionTimeoutError, PyMongoError) as exc:
        logger.warning(
            f"⚠️ Could not reach MongoDB at {safe_url}: {exc}. "
            "Falling back to local file store."
        )
        _is_connected = False
        return False
    except Exception as exc:
        logger.error(f"❌ Unexpected error connecting to MongoDB: {exc}")
        _is_connected = False
        return False


def _init_indexes(db: Database):
    """Ensure essential indexes exist for performance and constraints."""
    try:
        # Users collection: unique email
        db["users"].create_index("email", unique=True)
        # Evidence collection: unique ID, sorted upload_date
        db["evidence"].create_index("id", unique=True)
        db["evidence"].create_index([("upload_date", -1)])
        logger.info("MongoDB indexes verified.")
    except Exception as exc:
        logger.warning(f"Could not initialize MongoDB indexes: {exc}")


def is_mongodb_ready() -> bool:
    """Check if MongoDB is currently connected and operational."""
    global _is_connected, _connection_attempted
    if not _connection_attempted:
        connect_to_mongodb()
    return _is_connected


def get_mongodb_client() -> Optional[MongoClient]:
    """Return the active MongoClient, connecting if not already attempted."""
    if not _connection_attempted:
        connect_to_mongodb()
    return _client if _is_connected else None


def get_database() -> Optional[Database]:
    """Return the active Database object, or None if MongoDB is offline."""
    if not _connection_attempted:
        connect_to_mongodb()
    return _db if _is_connected else None


def get_evidence_collection() -> Optional[Collection]:
    """Return the evidence collection, or None if MongoDB is offline."""
    db = get_database()
    return db["evidence"] if db is not None else None


def get_users_collection() -> Optional[Collection]:
    """Return the users collection, or None if MongoDB is offline."""
    db = get_database()
    return db["users"] if db is not None else None


def close_mongodb_connection():
    """Close MongoDB client connection on shutdown."""
    global _client, _db, _is_connected, _connection_attempted
    if _client is not None:
        try:
            _client.close()
            logger.info("MongoDB connection closed.")
        except Exception as exc:
            logger.warning(f"Error closing MongoDB connection: {exc}")
    _client = None
    _db = None
    _is_connected = False
    _connection_attempted = False
