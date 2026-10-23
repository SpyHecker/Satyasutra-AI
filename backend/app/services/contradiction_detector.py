"""
Contradiction Detector — finds conflicting facts across evidence sources.

Uses rule-based heuristics to identify pairs of statements from different
sources that contain conflicting information. Focuses on:
- Number of people/suspects discrepancies
- Vehicle color discrepancies
- Vehicle description conflicts
- Key factual disagreements
"""

import logging
import re
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Targeted extraction patterns — focused on investigative contradictions
# ---------------------------------------------------------------------------

# Pattern: "two men", "three suspects", "a man", etc.
PEOPLE_COUNT_PATTERN = re.compile(
    r"\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+)\s+"
    r"(men|man|people|persons?|suspects?|individuals?|males?|females?|guys?|figures?)\b",
    re.IGNORECASE,
)

# Pattern: color + vehicle ("white van", "dark car", etc.)
VEHICLE_COLOR_PATTERN = re.compile(
    r"\b(white|black|dark|light|red|blue|green|grey|gray|silver|brown|maroon|cream)\s*"
    r"[-]?\s*(van|car|vehicle|truck|suv|auto|maruti|eeco|swift|alto|sedan|hatchback)\b",
    re.IGNORECASE,
)

# Pattern: time of activity ("at 11:45 PM", "around 12:30 AM")
EVENT_TIME_PATTERN = re.compile(
    r"(?:at|around|approximately|about)\s+(\d{1,2}[:.]\d{2})\s*(AM|PM|am|pm)\b",
    re.IGNORECASE,
)

# Number word to digit
NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "a": 1, "an": 1,
}


def _word_to_number(word: str) -> int | None:
    """Convert a number word or digit string to int."""
    word = word.strip().lower()
    if word in NUMBER_WORDS:
        return NUMBER_WORDS[word]
    try:
        return int(word)
    except ValueError:
        return None


def _sentences_from_text(text: str) -> list[str]:
    """Split text into sentences."""
    sentences = re.split(r'[.!?\n]+', text)
    return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 15]


def _find_sentence_containing(text: str, phrase: str) -> str:
    """Find the sentence in text that contains the given phrase."""
    sentences = _sentences_from_text(text)
    phrase_lower = phrase.lower()
    for sent in sentences:
        if phrase_lower in sent.lower():
            return sent[:300]
    return phrase


def _extract_people_counts(text: str) -> list[dict]:
    """Extract references to the number of people/suspects."""
    results = []
    for match in PEOPLE_COUNT_PATTERN.finditer(text):
        num = _word_to_number(match.group(1))
        if num is not None and num <= 20:  # Reasonable people count
            results.append({
                "count": num,
                "subject": match.group(2).lower(),
                "full_match": match.group(),
                "position": match.start(),
            })
    return results


def _extract_vehicle_colors(text: str) -> list[dict]:
    """Extract vehicle color descriptions."""
    results = []
    for match in VEHICLE_COLOR_PATTERN.finditer(text):
        results.append({
            "color": match.group(1).lower(),
            "vehicle": match.group(2).lower(),
            "full_match": match.group(),
            "position": match.start(),
        })
    return results


def detect_contradictions(
    evidence_records: list,
    graph=None,
) -> list[dict]:
    """
    Scan evidence records for contradictory statements or facts.

    Parameters
    ----------
    evidence_records : list
        List of EvidenceRecord objects or dicts with raw_text and metadata.
    graph : optional
        The case knowledge graph (reserved for future use).

    Returns
    -------
    list[dict]
        List of contradiction dicts, each with:
        - type (str): contradiction category
        - statement_a (str): first statement text
        - statement_b (str): conflicting statement text
        - source_a (str): evidence ID for statement A
        - source_a_name (str): filename of evidence A
        - source_b (str): evidence ID for statement B
        - source_b_name (str): filename of evidence B
        - explanation (str): why these contradict
        - confidence (float): 0.0 – 1.0
        - severity (str): "high", "medium", or "low"
    """
    contradictions = []

    # Normalize records to dicts
    records = []
    for record in evidence_records:
        if hasattr(record, "model_dump"):
            records.append(record.model_dump())
        elif isinstance(record, dict):
            records.append(record)

    if len(records) < 2:
        return contradictions

    # Compare each pair of evidence sources
    for i in range(len(records)):
        for j in range(i + 1, len(records)):
            rec_a = records[i]
            rec_b = records[j]

            text_a = rec_a.get("raw_text", "")
            text_b = rec_b.get("raw_text", "")
            id_a = rec_a.get("id", f"evidence_{i}")
            id_b = rec_b.get("id", f"evidence_{j}")
            name_a = rec_a.get("filename", f"Document {i+1}")
            name_b = rec_b.get("filename", f"Document {j+1}")

            if not text_a or not text_b:
                continue

            # --- 1) People count contradictions ---
            people_a = _extract_people_counts(text_a)
            people_b = _extract_people_counts(text_b)

            # Compare: do they disagree on how many people were seen?
            for pa in people_a:
                for pb in people_b:
                    # Only compare when they're describing the same type of subject
                    subj_a = pa["subject"].rstrip("s")  # normalize plural
                    subj_b = pb["subject"].rstrip("s")
                    if subj_a == subj_b or subj_a == "men" or subj_b == "men" or subj_a == "man" or subj_b == "man":
                        if pa["count"] != pb["count"]:
                            sent_a = _find_sentence_containing(text_a, pa["full_match"])
                            sent_b = _find_sentence_containing(text_b, pb["full_match"])

                            contradictions.append({
                                "type": "number_of_suspects",
                                "statement_a": sent_a,
                                "statement_b": sent_b,
                                "source_a": id_a,
                                "source_a_name": name_a,
                                "source_b": id_b,
                                "source_b_name": name_b,
                                "explanation": (
                                    f"'{name_a}' reports {pa['count']} {pa['subject']}, "
                                    f"but '{name_b}' reports {pb['count']} {pb['subject']}."
                                ),
                                "confidence": 0.85,
                                "severity": "high",
                            })

            # --- 2) Vehicle color contradictions ---
            vehicles_a = _extract_vehicle_colors(text_a)
            vehicles_b = _extract_vehicle_colors(text_b)

            for va in vehicles_a:
                for vb in vehicles_b:
                    # Same vehicle type but different color
                    if va["color"] != vb["color"]:
                        # Check if vehicles are comparable
                        veh_match = (
                            va["vehicle"] == vb["vehicle"]
                            or "van" in va["vehicle"] and "van" in vb["vehicle"]
                            or "maruti" in va["vehicle"] or "maruti" in vb["vehicle"]
                        )
                        if veh_match:
                            sent_a = _find_sentence_containing(text_a, va["full_match"])
                            sent_b = _find_sentence_containing(text_b, vb["full_match"])

                            contradictions.append({
                                "type": "vehicle_description",
                                "statement_a": sent_a,
                                "statement_b": sent_b,
                                "source_a": id_a,
                                "source_a_name": name_a,
                                "source_b": id_b,
                                "source_b_name": name_b,
                                "explanation": (
                                    f"'{name_a}' describes a {va['color']} {va['vehicle']}, "
                                    f"but '{name_b}' describes a {vb['color']} {vb['vehicle']}. "
                                    f"Vehicle color descriptions conflict."
                                ),
                                "confidence": 0.78,
                                "severity": "medium",
                            })

    # Deduplicate
    contradictions = _deduplicate_contradictions(contradictions)

    logger.info(f"Detected {len(contradictions)} contradictions across {len(records)} evidence records")
    return contradictions


def _deduplicate_contradictions(contradictions: list[dict]) -> list[dict]:
    """Remove near-duplicate contradictions."""
    if len(contradictions) <= 1:
        return contradictions

    unique = []
    seen_keys = set()

    for c in contradictions:
        # Create a key from source pair + type + core values
        key = (
            min(c["source_a"], c["source_b"]),
            max(c["source_a"], c["source_b"]),
            c["type"],
            c.get("explanation", "")[:80],
        )
        if key not in seen_keys:
            seen_keys.add(key)
            unique.append(c)

    return unique
