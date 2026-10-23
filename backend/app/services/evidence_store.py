"""
Evidence Store — MongoDB + JSON fallback persistence for evidence records.

Supports multi-user isolation by scoping all evidence records and queries
to the authenticated user's ID. Automatically falls back to a thread-safe
local JSON file if MongoDB is offline or unconfigured.
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Optional

from pydantic import BaseModel, Field

from app.db.mongodb import (
    is_mongodb_ready,
    get_evidence_collection,
)

logger = logging.getLogger(__name__)


class EntityRecord(BaseModel):
    """A single named entity extracted from evidence text."""
    text: str
    label: str          # spaCy label (PERSON, GPE, DATE, etc.)
    category: str       # Mapped schema category (Person, Location, Time, etc.)
    start: int          # Character offset start
    end: int            # Character offset end


class EvidenceRecord(BaseModel):
    """A complete evidence record with extracted data."""
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    filename: str
    file_path: str
    upload_date: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    file_type: str      # txt, pdf, png, jpg, etc.
    raw_text: str = ""
    entities: list[EntityRecord] = []
    status: str = "processed"
    user_id: Optional[str] = "inv-demo-001"  # Scopes evidence to specific investigator
    uploaded_by: Optional[str] = None        # User email or name for provenance


class EvidenceStore:
    """
    Evidence store supporting MongoDB primary storage with JSON-file fallback,
    with multi-user case workspace isolation.
    """

    def __init__(self, store_path: str = "data/evidence_store.json"):
        self._path = Path(store_path)
        self._lock = Lock()
        self._ensure_file()
        self._synced_to_mongo = False

    def _ensure_file(self):
        """Create the store file and parent directories if they don't exist."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.write_text("[]", encoding="utf-8")

    def _read_local(self) -> list[dict]:
        """Read all records from the fallback JSON file."""
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                # Ensure legacy records have user_id assigned to demo user
                for r in data:
                    if "user_id" not in r or not r["user_id"]:
                        r["user_id"] = "inv-demo-001"
                return data
            return []
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_local(self, records: list[dict]):
        """Write records to the local backup JSON file."""
        self._path.write_text(
            json.dumps(records, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _sync_existing_to_mongo(self):
        """Seed MongoDB with existing JSON records if MongoDB is empty."""
        if self._synced_to_mongo:
            return
        if not is_mongodb_ready():
            return
        try:
            col = get_evidence_collection()
            if col is not None and col.count_documents({}) == 0:
                local_records = self._read_local()
                if local_records:
                    col.insert_many(local_records)
                    logger.info(f"Synchronized {len(local_records)} local evidence records into MongoDB.")
            self._synced_to_mongo = True
        except Exception as exc:
            logger.warning(f"Failed to sync local evidence to MongoDB: {exc}")

    def save(self, record: EvidenceRecord) -> EvidenceRecord:
        """Save or update an evidence record in MongoDB and local fallback."""
        doc = record.model_dump()

        # Save to local file backup
        with self._lock:
            records = self._read_local()
            # Replace existing or append
            records = [r for r in records if r.get("id") != record.id]
            records.append(doc)
            self._write_local(records)

        # Save to MongoDB if available
        if is_mongodb_ready():
            try:
                col = get_evidence_collection()
                if col is not None:
                    col.replace_one({"id": record.id}, doc, upsert=True)
                    logger.debug(f"Saved evidence record {record.id} for user {record.user_id} to MongoDB.")
            except Exception as exc:
                logger.warning(f"Could not persist evidence {record.id} to MongoDB: {exc}")

        return record

    def get(self, evidence_id: str, user_id: Optional[str] = None) -> EvidenceRecord | None:
        """Retrieve a single evidence record by ID, optionally validating user ownership."""
        if is_mongodb_ready():
            try:
                col = get_evidence_collection()
                if col is not None:
                    query = {"id": evidence_id}
                    if user_id:
                        query["user_id"] = user_id
                    doc = col.find_one(query, {"_id": 0})
                    if doc:
                        return EvidenceRecord(**doc)
            except Exception as exc:
                logger.warning(f"MongoDB read error for {evidence_id}: {exc}. Checking local fallback.")

        # Fallback to local
        with self._lock:
            records = self._read_local()
        for r in records:
            if r.get("id") == evidence_id:
                if user_id and r.get("user_id") != user_id:
                    return None
                return EvidenceRecord(**r)
        return None

    def list_all(self, user_id: Optional[str] = None) -> list[EvidenceRecord]:
        """
        Return evidence records sorted chronologically.
        If user_id is provided, only records owned by that user are returned.
        """
        self._sync_existing_to_mongo()

        if is_mongodb_ready():
            try:
                col = get_evidence_collection()
                if col is not None:
                    query = {"user_id": user_id} if user_id else {}
                    cursor = col.find(query, {"_id": 0}).sort("upload_date", -1)
                    return [EvidenceRecord(**doc) for doc in cursor]
            except Exception as exc:
                logger.warning(f"MongoDB list_all error: {exc}. Reading from local fallback.")

        # Fallback to local
        with self._lock:
            records = self._read_local()

        if user_id:
            records = [r for r in records if r.get("user_id") == user_id]

        records_sorted = sorted(
            records,
            key=lambda x: x.get("upload_date", ""),
            reverse=True,
        )
        return [EvidenceRecord(**r) for r in records_sorted]

    def delete(self, evidence_id: str, user_id: Optional[str] = None) -> bool:
        """Delete an evidence record by ID. Returns True if found and deleted."""
        deleted_from_local = False
        with self._lock:
            records = self._read_local()
            matching = [
                r for r in records
                if r.get("id") == evidence_id and (not user_id or r.get("user_id") == user_id)
            ]
            if matching:
                filtered = [r for r in records if r.get("id") != evidence_id]
                self._write_local(filtered)
                deleted_from_local = True

        deleted_from_mongo = False
        if is_mongodb_ready():
            try:
                col = get_evidence_collection()
                if col is not None:
                    query = {"id": evidence_id}
                    if user_id:
                        query["user_id"] = user_id
                    result = col.delete_one(query)
                    deleted_from_mongo = result.deleted_count > 0
            except Exception as exc:
                logger.warning(f"MongoDB delete error for {evidence_id}: {exc}")

        return deleted_from_local or deleted_from_mongo


# Module-level singleton
store = EvidenceStore()
