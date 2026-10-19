"""
Timeline Service — reconstructs chronological event sequences and detects gaps.

Extracts time-related entities from evidence, normalizes them into ISO 8601
timestamps, sorts chronologically, and detects temporal gaps that may indicate
missing evidence or unaccounted time periods.
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# Mapping of month names/abbreviations to numbers
MONTH_MAP = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "september": 9, "sept": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}

# Regex patterns for common date/time formats
DATE_PATTERNS = [
    # DD-Month-YYYY (e.g., 15-July-2026)
    re.compile(
        r"(\d{1,2})[/-](\w+)[/-](\d{4})",
        re.IGNORECASE,
    ),
    # Month DD, YYYY (e.g., July 15, 2026)
    re.compile(
        r"(\w+)\s+(\d{1,2}),?\s+(\d{4})",
        re.IGNORECASE,
    ),
    # DD/MM/YYYY or DD-MM-YYYY
    re.compile(
        r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})",
    ),
    # YYYY-MM-DD
    re.compile(
        r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})",
    ),
]

TIME_PATTERNS = [
    # HH:MM AM/PM (e.g., 11:45 PM, 9:30 AM)
    re.compile(
        r"(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)",
        re.IGNORECASE,
    ),
    # HH:MM (24-hour)
    re.compile(
        r"(\d{1,2}):(\d{2})(?:\s*(?:hours?|hrs?))?",
    ),
    # Approximate times like "approximately 11:45 PM"
    re.compile(
        r"approximately\s+(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)",
        re.IGNORECASE,
    ),
    # "midnight" keyword
    re.compile(
        r"\b(midnight)\b",
        re.IGNORECASE,
    ),
    # "noon" keyword
    re.compile(
        r"\b(noon)\b",
        re.IGNORECASE,
    ),
]


def _parse_month(month_str: str) -> Optional[int]:
    """Convert a month name or number to its integer value."""
    month_str = month_str.strip().lower()
    if month_str in MONTH_MAP:
        return MONTH_MAP[month_str]
    try:
        val = int(month_str)
        if 1 <= val <= 12:
            return val
    except ValueError:
        pass
    return None


def _parse_time_string(time_str: str) -> Optional[tuple[int, int]]:
    """Extract hour and minute from a time string."""
    time_str = time_str.strip().lower()

    if "midnight" in time_str:
        return (0, 0)
    if "noon" in time_str:
        return (12, 0)

    for pattern in TIME_PATTERNS:
        match = pattern.search(time_str)
        if match:
            groups = match.groups()
            if len(groups) >= 2:
                try:
                    hour = int(groups[0])
                    minute = int(groups[1])
                    if len(groups) >= 3 and groups[2]:
                        meridiem = groups[2].upper()
                        if meridiem == "PM" and hour != 12:
                            hour += 12
                        elif meridiem == "AM" and hour == 12:
                            hour = 0
                    if 0 <= hour <= 23 and 0 <= minute <= 59:
                        return (hour, minute)
                except (ValueError, IndexError):
                    continue
    return None


def _extract_dates_from_text(text: str) -> list[dict]:
    """
    Extract date references from raw text content.

    Returns a list of dicts with parsed datetime objects and their
    surrounding context.
    """
    results = []

    if not text:
        return results

    lines = text.split("\n")

    for line_idx, line in enumerate(lines):
        line_stripped = line.strip()
        if not line_stripped:
            continue

        for pattern in DATE_PATTERNS:
            for match in pattern.finditer(line_stripped):
                groups = match.groups()
                parsed_date = None

                try:
                    if len(groups) == 3:
                        g0, g1, g2 = groups

                        # Try DD-Month-YYYY
                        month = _parse_month(g1)
                        if month and g0.isdigit() and g2.isdigit():
                            day = int(g0)
                            year = int(g2)
                            if 1 <= day <= 31 and 1900 <= year <= 2100:
                                parsed_date = datetime(year, month, day)

                        # Try Month DD, YYYY
                        if not parsed_date:
                            month = _parse_month(g0)
                            if month and g1.isdigit() and g2.isdigit():
                                day = int(g1)
                                year = int(g2)
                                if 1 <= day <= 31 and 1900 <= year <= 2100:
                                    parsed_date = datetime(year, month, day)

                        # Try YYYY-MM-DD
                        if not parsed_date and g0.isdigit() and len(g0) == 4:
                            year = int(g0)
                            month_val = int(g1) if g1.isdigit() else None
                            day_val = int(g2) if g2.isdigit() else None
                            if month_val and day_val:
                                if 1 <= month_val <= 12 and 1 <= day_val <= 31 and 1900 <= year <= 2100:
                                    parsed_date = datetime(year, month_val, day_val)

                        # Try DD/MM/YYYY
                        if not parsed_date and all(g.isdigit() for g in groups):
                            day = int(g0)
                            month_val = int(g1)
                            year = int(g2)
                            if 1 <= day <= 31 and 1 <= month_val <= 12 and 1900 <= year <= 2100:
                                parsed_date = datetime(year, month_val, day)

                except (ValueError, OverflowError):
                    continue

                if parsed_date:
                    # Try to find a time in the same line
                    time_tuple = _parse_time_string(line_stripped)
                    if time_tuple:
                        parsed_date = parsed_date.replace(
                            hour=time_tuple[0], minute=time_tuple[1]
                        )

                    # Get context (the line itself, trimmed)
                    context = line_stripped[:200]

                    results.append({
                        "datetime": parsed_date,
                        "context": context,
                        "line_index": line_idx,
                        "match_text": match.group(),
                    })

    return results


def build_timeline(
    evidence_records: list,
    raw_texts: Optional[dict[str, str]] = None,
) -> list[dict]:
    """
    Build a chronological timeline from evidence records.

    Extracts timestamps from entity text and raw document text,
    sorts chronologically, and returns structured timeline events.

    Parameters
    ----------
    evidence_records : list
        List of evidence records (EvidenceRecord objects or dicts).
    raw_texts : dict[str, str], optional
        Mapping of evidence_id → raw text for deeper date extraction.

    Returns
    -------
    list[dict]
        Sorted list of timeline events, each with:
        - timestamp (str): ISO 8601 datetime
        - description (str): event summary / context
        - source_id (str): evidence ID
        - source_name (str): evidence filename
        - type (str): event type category
        - is_approximate (bool): whether the time is approximate
    """
    events = []

    for record in evidence_records:
        # Handle both EvidenceRecord objects and dicts
        if hasattr(record, "model_dump"):
            rec = record.model_dump()
        elif isinstance(record, dict):
            rec = record
        else:
            continue

        evidence_id = rec.get("id", "")
        filename = rec.get("filename", "unknown")
        raw_text = rec.get("raw_text", "")
        entities = rec.get("entities", [])

        # If raw_texts provided, use that
        if raw_texts and evidence_id in raw_texts:
            raw_text = raw_texts[evidence_id]

        # Strategy 1: Extract from Time-category entities
        for ent in entities:
            ent_data = ent if isinstance(ent, dict) else (ent.model_dump() if hasattr(ent, "model_dump") else {})
            category = ent_data.get("category", "")
            if category != "Time":
                continue

            text = ent_data.get("text", "").strip()
            if not text:
                continue

            # Try to parse the entity text as a date
            date_results = _extract_dates_from_text(text)
            for dr in date_results:
                events.append({
                    "timestamp": dr["datetime"].isoformat(),
                    "datetime_obj": dr["datetime"],
                    "description": f"Date reference: {text}",
                    "context": dr.get("context", text),
                    "source_id": evidence_id,
                    "source_name": filename,
                    "type": "date_reference",
                    "is_approximate": False,
                })

        # Strategy 2: Extract timestamps from raw text
        if raw_text:
            text_dates = _extract_dates_from_text(raw_text)
            for dr in text_dates:
                # Check for "approximately" marker
                is_approx = "approximately" in dr.get("context", "").lower()

                events.append({
                    "timestamp": dr["datetime"].isoformat(),
                    "datetime_obj": dr["datetime"],
                    "description": dr.get("context", ""),
                    "context": dr.get("context", ""),
                    "source_id": evidence_id,
                    "source_name": filename,
                    "type": "extracted_event",
                    "is_approximate": is_approx,
                })

    # Deduplicate events with same timestamp + same source
    seen = set()
    unique_events = []
    for evt in events:
        key = (evt["timestamp"], evt["source_id"], evt["description"][:80])
        if key not in seen:
            seen.add(key)
            unique_events.append(evt)

    # Sort by datetime
    unique_events.sort(key=lambda e: e.get("datetime_obj", datetime.min))

    # Remove internal datetime object before returning
    for evt in unique_events:
        evt.pop("datetime_obj", None)

    logger.info(f"Built timeline with {len(unique_events)} events")
    return unique_events


def detect_gaps(
    timeline: list[dict],
    max_gap_hours: float = 24.0,
) -> list[dict]:
    """
    Detect temporal gaps in the timeline that exceed a threshold.

    Parameters
    ----------
    timeline : list[dict]
        Sorted timeline events from build_timeline().
    max_gap_hours : float
        Gaps larger than this (in hours) are flagged.

    Returns
    -------
    list[dict]
        List of gap dicts with: start, end, duration_hours, description.
    """
    gaps = []

    if len(timeline) < 2:
        return gaps

    for i in range(len(timeline) - 1):
        try:
            ts_a = datetime.fromisoformat(timeline[i]["timestamp"])
            ts_b = datetime.fromisoformat(timeline[i + 1]["timestamp"])
            delta = ts_b - ts_a
            hours = delta.total_seconds() / 3600

            if hours > max_gap_hours:
                gaps.append({
                    "start": timeline[i]["timestamp"],
                    "end": timeline[i + 1]["timestamp"],
                    "duration_hours": round(hours, 2),
                    "description": (
                        f"Gap of {round(hours, 1)} hours detected between "
                        f"'{timeline[i].get('source_name', 'unknown')}' "
                        f"and '{timeline[i+1].get('source_name', 'unknown')}'"
                    ),
                    "before_event": timeline[i].get("description", ""),
                    "after_event": timeline[i + 1].get("description", ""),
                })
        except (ValueError, KeyError):
            continue

    logger.info(f"Detected {len(gaps)} temporal gaps (threshold: {max_gap_hours}h)")
    return gaps
