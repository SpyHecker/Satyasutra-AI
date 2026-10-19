"""
Evidence routes — handles evidence file upload, retrieval, and deletion.

Week 2: Full pipeline — upload → save → OCR → NLP → persist → return entities.
"""

import os
import logging
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from app.services.ocr import extract_text, get_file_type, is_supported
from app.services.nlp_extraction import extract_entities, get_entity_summary
from app.services.evidence_store import store, EvidenceRecord, EntityRecord

logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = Path("uploads")


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------
class EntityResponse(BaseModel):
    text: str
    label: str
    category: str
    start: int
    end: int


class UploadResponse(BaseModel):
    id: str
    message: str
    filename: str
    file_type: str
    status: str
    text_preview: str
    entity_count: int
    entity_summary: dict[str, int]
    entities: list[EntityResponse]


class EvidenceListItem(BaseModel):
    id: str
    filename: str
    file_type: str
    upload_date: str
    status: str
    entity_count: int


class EvidenceDetail(BaseModel):
    id: str
    filename: str
    file_type: str
    upload_date: str
    status: str
    raw_text: str
    entity_count: int
    entity_summary: dict[str, int]
    entities: list[EntityResponse]


# ---------------------------------------------------------------------------
# POST /upload — full evidence processing pipeline
# ---------------------------------------------------------------------------
@router.post("/upload", response_model=UploadResponse)
async def upload_evidence(file: UploadFile = File(...)):
    """
    Upload evidence file → save → OCR/read → NLP extraction → persist.

    Supported formats: .txt, .pdf, .png, .jpg, .jpeg, .tiff, .bmp
    """
    filename = file.filename or "unknown"
    file_type = get_file_type(filename)

    # Validate file type
    if not is_supported(filename):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: .{file_type}. "
                   f"Supported: txt, pdf, png, jpg, jpeg, tiff, bmp",
        )

    # Save file to uploads/
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    save_path = UPLOAD_DIR / filename

    # Handle duplicate filenames by appending a counter
    counter = 1
    original_stem = save_path.stem
    while save_path.exists():
        save_path = UPLOAD_DIR / f"{original_stem}_{counter}{save_path.suffix}"
        counter += 1

    content = await file.read()
    save_path.write_bytes(content)
    logger.info(f"Saved file: {save_path} ({len(content)} bytes)")

    # Extract text (OCR / direct read / PDF)
    try:
        raw_text = extract_text(str(save_path))
    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
        # Save the record even if extraction fails
        record = EvidenceRecord(
            filename=filename,
            file_path=str(save_path),
            file_type=file_type,
            raw_text="",
            entities=[],
            status="extraction_failed",
        )
        store.save(record)
        return UploadResponse(
            id=record.id,
            message=f"File saved but text extraction failed: {e}",
            filename=filename,
            file_type=file_type,
            status="extraction_failed",
            text_preview="",
            entity_count=0,
            entity_summary={},
            entities=[],
        )

    # Extract entities via NLP
    try:
        entities_raw = extract_entities(raw_text)
    except Exception as e:
        logger.error(f"NLP extraction failed: {e}")
        entities_raw = []

    # Convert to EntityRecord models
    entity_records = [EntityRecord(**ent) for ent in entities_raw]
    entity_summary = get_entity_summary(entities_raw)

    # Create and persist evidence record
    record = EvidenceRecord(
        filename=filename,
        file_path=str(save_path),
        file_type=file_type,
        raw_text=raw_text,
        entities=entity_records,
        status="processed",
    )
    store.save(record)

    # Build response
    text_preview = raw_text[:500] + ("..." if len(raw_text) > 500 else "")

    return UploadResponse(
        id=record.id,
        message=f"Successfully processed {filename}",
        filename=filename,
        file_type=file_type,
        status="processed",
        text_preview=text_preview,
        entity_count=len(entity_records),
        entity_summary=entity_summary,
        entities=[EntityResponse(**e.model_dump()) for e in entity_records],
    )


# ---------------------------------------------------------------------------
# GET / — list all evidence
# ---------------------------------------------------------------------------
@router.get("/")
async def list_evidence():
    """List all uploaded evidence items (without full text/entities for brevity)."""
    records = store.list_all()
    items = [
        EvidenceListItem(
            id=r.id,
            filename=r.filename,
            file_type=r.file_type,
            upload_date=r.upload_date,
            status=r.status,
            entity_count=len(r.entities),
        )
        for r in records
    ]
    return {"evidence": items, "total": len(items)}


# ---------------------------------------------------------------------------
# GET /{evidence_id} — get single evidence with full detail
# ---------------------------------------------------------------------------
@router.get("/{evidence_id}", response_model=EvidenceDetail)
async def get_evidence(evidence_id: str):
    """Retrieve a single evidence record with full text and entities."""
    record = store.get(evidence_id)
    if not record:
        raise HTTPException(status_code=404, detail="Evidence not found")

    entities_raw = [e.model_dump() for e in record.entities]

    return EvidenceDetail(
        id=record.id,
        filename=record.filename,
        file_type=record.file_type,
        upload_date=record.upload_date,
        status=record.status,
        raw_text=record.raw_text,
        entity_count=len(record.entities),
        entity_summary=get_entity_summary(entities_raw),
        entities=[EntityResponse(**e) for e in entities_raw],
    )


# ---------------------------------------------------------------------------
# DELETE /{evidence_id} — delete evidence
# ---------------------------------------------------------------------------
@router.delete("/{evidence_id}")
async def delete_evidence(evidence_id: str):
    """Delete an evidence record and its uploaded file."""
    record = store.get(evidence_id)
    if not record:
        raise HTTPException(status_code=404, detail="Evidence not found")

    # Delete the file from disk
    try:
        file_path = Path(record.file_path)
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted file: {file_path}")
    except Exception as e:
        logger.warning(f"Could not delete file {record.file_path}: {e}")

    # Delete from store
    store.delete(evidence_id)
    return {"message": f"Evidence '{record.filename}' deleted", "id": evidence_id}
