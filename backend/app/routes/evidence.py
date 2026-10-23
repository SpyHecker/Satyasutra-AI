"""
Evidence routes — handles evidence file upload, retrieval, deletion,
and the full analysis pipeline (graph, timeline, contradictions, report).

Includes multi-user scoping: all evidence records, graphs, timelines,
and reports are isolated per authenticated investigator/admin.
"""

import os
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel

from app.services.ocr import extract_text, get_file_type, is_supported
from app.services.nlp_extraction import extract_entities, get_entity_summary
from app.services.evidence_store import store, EvidenceRecord, EntityRecord
from app.services.graph_builder import (
    add_evidence_to_graph,
    rebuild_case_graph,
    graph_to_json,
    get_case_graph,
    reset_case_graph,
)
from app.services.timeline import build_timeline, detect_gaps
from app.services.contradiction_detector import detect_contradictions
from app.services.report_generator import generate_report
from app.routes.auth import get_current_user
from app.services.auth_service import UserRecord

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


# ═══════════════════════════════════════════════════════════════════════════
# ANALYSIS ROUTES (must be BEFORE /{evidence_id} to avoid path-param clash)
# ═══════════════════════════════════════════════════════════════════════════

# ---------------------------------------------------------------------------
# GET /analysis/stats — dashboard statistics
# ---------------------------------------------------------------------------
@router.get("/analysis/stats")
async def get_stats(current_user: UserRecord = Depends(get_current_user)):
    """Return aggregated statistics for the dashboard scoped to the current investigator."""
    records = store.list_all(user_id=current_user.id)

    total_entities = sum(len(r.entities) for r in records)

    # Get category breakdown
    category_counts: dict[str, int] = {}
    for r in records:
        for e in r.entities:
            cat = e.category
            category_counts[cat] = category_counts.get(cat, 0) + 1

    # Count contradictions
    contradictions = detect_contradictions(records) if len(records) >= 2 else []

    return {
        "evidence_count": len(records),
        "total_entities": total_entities,
        "entity_categories": category_counts,
        "contradiction_count": len(contradictions),
        "processed_count": sum(1 for r in records if r.status == "processed"),
        "failed_count": sum(1 for r in records if r.status == "extraction_failed"),
    }


# ---------------------------------------------------------------------------
# GET /analysis/graph — full case knowledge graph
# ---------------------------------------------------------------------------
@router.get("/analysis/graph")
async def get_graph(current_user: UserRecord = Depends(get_current_user)):
    """Return the user's case knowledge graph as JSON for visualization."""
    records = store.list_all(user_id=current_user.id)
    if not records:
        return {
            "nodes": [],
            "links": [],
            "stats": {"total_nodes": 0, "total_edges": 0, "categories": {}},
        }
    graph_json = rebuild_case_graph(records)
    return graph_json


# ---------------------------------------------------------------------------
# GET /analysis/timeline — reconstructed timeline
# ---------------------------------------------------------------------------
@router.get("/analysis/timeline")
async def get_timeline(current_user: UserRecord = Depends(get_current_user)):
    """Return the reconstructed timeline with gap detection for the investigator's evidence."""
    records = store.list_all(user_id=current_user.id)
    if not records:
        return {"events": [], "gaps": [], "total_events": 0, "total_gaps": 0}

    timeline = build_timeline(records)
    gaps = detect_gaps(timeline, max_gap_hours=6.0)

    return {
        "events": timeline,
        "gaps": gaps,
        "total_events": len(timeline),
        "total_gaps": len(gaps),
    }


# ---------------------------------------------------------------------------
# GET /analysis/contradictions — contradiction detection
# ---------------------------------------------------------------------------
@router.get("/analysis/contradictions")
async def get_contradictions(current_user: UserRecord = Depends(get_current_user)):
    """Detect and return contradictions found across current investigator's evidence sources."""
    records = store.list_all(user_id=current_user.id)
    if len(records) < 2:
        return {"contradictions": [], "total": 0}

    contradictions = detect_contradictions(records)

    return {
        "contradictions": contradictions,
        "total": len(contradictions),
    }


# ---------------------------------------------------------------------------
# GET /analysis/report — full case report
# ---------------------------------------------------------------------------
@router.get("/analysis/report")
async def get_report(current_user: UserRecord = Depends(get_current_user)):
    """Generate and return a full case investigation report for the active user."""
    records = store.list_all(user_id=current_user.id)

    if not records:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        return {
            "title": "SatyaSutra Investigation Report",
            "generated_at": now,
            "markdown": "",
            "sections": [],
            "stats": {
                "evidence_count": 0,
                "entity_count": 0,
                "timeline_events": 0,
                "gaps_detected": 0,
                "contradictions": 0,
            },
        }

    # Build all analysis components
    graph_json = rebuild_case_graph(records)
    timeline = build_timeline(records)
    gaps = detect_gaps(timeline, max_gap_hours=6.0) if timeline else []
    contradictions = detect_contradictions(records) if len(records) >= 2 else []

    # Prepare evidence metadata for the report
    evidence_meta = [
        {
            "id": r.id,
            "filename": r.filename,
            "file_type": r.file_type,
            "status": r.status,
            "entity_count": len(r.entities),
        }
        for r in records
    ]

    case_data = {
        "evidence": evidence_meta,
        "graph": graph_json,
        "timeline": timeline,
        "timeline_gaps": gaps,
        "contradictions": contradictions,
    }

    report = generate_report(case_data)
    return report


# ═══════════════════════════════════════════════════════════════════════════
# EVIDENCE CRUD ROUTES
# ═══════════════════════════════════════════════════════════════════════════

# ---------------------------------------------------------------------------
# POST /upload — full evidence processing pipeline
# ---------------------------------------------------------------------------
@router.post("/upload", response_model=UploadResponse)
async def upload_evidence(
    file: UploadFile = File(...),
    current_user: UserRecord = Depends(get_current_user),
):
    """
    Upload evidence file → save → OCR/read → NLP extraction → persist.
    Attaches the file to the current investigator's account.
    """
    user_id = current_user.id
    uploaded_by = current_user.email

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
    logger.info(f"Saved file: {save_path} ({len(content)} bytes) for user {user_id}")

    # Extract text (OCR / direct read / PDF)
    try:
        raw_text = extract_text(str(save_path))
    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
        record = EvidenceRecord(
            filename=filename,
            file_path=str(save_path),
            file_type=file_type,
            raw_text="",
            entities=[],
            status="extraction_failed",
            user_id=user_id,
            uploaded_by=uploaded_by,
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

    # Create and persist evidence record scoped to user
    record = EvidenceRecord(
        filename=filename,
        file_path=str(save_path),
        file_type=file_type,
        raw_text=raw_text,
        entities=entity_records,
        status="processed",
        user_id=user_id,
        uploaded_by=uploaded_by,
    )
    store.save(record)

    # Add to case graph
    try:
        add_evidence_to_graph(entities_raw, record.id)
    except Exception as e:
        logger.warning(f"Graph update failed: {e}")

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
# GET / — list evidence for current investigator
# ---------------------------------------------------------------------------
@router.get("/")
async def list_evidence(current_user: UserRecord = Depends(get_current_user)):
    """List all uploaded evidence items belonging to the active investigator."""
    records = store.list_all(user_id=current_user.id)
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
async def get_evidence(
    evidence_id: str,
    current_user: UserRecord = Depends(get_current_user),
):
    """Retrieve a single evidence record with full text and entities."""
    record = store.get(evidence_id, user_id=current_user.id)
    if not record:
        raise HTTPException(status_code=404, detail="Evidence not found in active case workspace.")

    return EvidenceDetail(
        id=record.id,
        filename=record.filename,
        file_type=record.file_type,
        upload_date=record.upload_date,
        status=record.status,
        raw_text=record.raw_text,
        entity_count=len(record.entities),
        entity_summary=get_entity_summary([e.model_dump() for e in record.entities]),
        entities=[EntityResponse(**e.model_dump()) for e in record.entities],
    )


# ---------------------------------------------------------------------------
# DELETE /{evidence_id} — delete single evidence
# ---------------------------------------------------------------------------
@router.delete("/{evidence_id}")
async def delete_evidence(
    evidence_id: str,
    current_user: UserRecord = Depends(get_current_user),
):
    """Delete an evidence record from the active investigator's workspace."""
    deleted = store.delete(evidence_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Evidence record not found or unauthorized.")

    return {"message": f"Deleted evidence {evidence_id}", "id": evidence_id}
