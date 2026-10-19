"""
Evidence Store — JSON-file-based persistence for evidence records.

Stores evidence metadata and extracted entities in a local JSON file.
Thread-safe with file locking. Designed to be replaced by a database
(e.g., SQLite, PostgreSQL) in later weeks.
"""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from pydantic import BaseModel, Field


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


class EvidenceStore:
    """
    JSON-file-based evidence store.

    All evidence records are stored in a single JSON file.
    Thread-safe via a reentrant lock.
    """

    def __init__(self, store_path: str = "data/evidence_store.json"):
        self._path = Path(store_path)
        self._lock = Lock()
        self._ensure_file()

    def _ensure_file(self):
        """Create the store file and parent directories if they don't exist."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.write_text("[]", encoding="utf-8")

    def _read(self) -> list[dict]:
        """Read all records from the JSON file."""
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write(self, records: list[dict]):
        """Write all records to the JSON file."""
        self._path.write_text(
            json.dumps(records, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def save(self, record: EvidenceRecord) -> EvidenceRecord:
        """Save a new evidence record."""
        with self._lock:
            records = self._read()
            records.append(record.model_dump())
            self._write(records)
        return record

    def get(self, evidence_id: str) -> EvidenceRecord | None:
        """Retrieve a single evidence record by ID."""
        with self._lock:
            records = self._read()
        for r in records:
            if r.get("id") == evidence_id:
                return EvidenceRecord(**r)
        return None

    def list_all(self) -> list[EvidenceRecord]:
        """Return all evidence records."""
        with self._lock:
            records = self._read()
        return [EvidenceRecord(**r) for r in records]

    def delete(self, evidence_id: str) -> bool:
        """Delete an evidence record by ID. Returns True if found and deleted."""
        with self._lock:
            records = self._read()
            filtered = [r for r in records if r.get("id") != evidence_id]
            if len(filtered) == len(records):
                return False
            self._write(filtered)
        return True


# Module-level singleton
store = EvidenceStore()
