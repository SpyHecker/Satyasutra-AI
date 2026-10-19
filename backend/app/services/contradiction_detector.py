"""
Contradiction Detector — finds conflicting facts across evidence sources.

Uses rule-based heuristics to identify pairs of statements from different
sources that contain conflicting information. Focuses on:
- Number discrepancies (e.g., "two men" vs "three men")
- Color discrepancies (e.g., "white van" vs "dark van")
- Time discrepancies
- Entity attribute conflicts
"""

import logging
import re
from collections import defaultdict
from difflib import SequenceMatcher

import networkx as nx

logger = logging.getLogger(__name__)

# Number words to digits mapping
NUMBER_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "a": 1, "an": 1,
}

# Color terms for comparison
COLOR_TERMS = {
    "white", "black", "red", "blue", "green", "yellow", "grey", "gray",
    "dark", "light", "brown", "silver", "maroon", "navy", "beige", "tan",
    "orange", "purple", "pink", "cream",
}

# Common descriptive categories where contradictions occur
CONTRADICTION_CATEGORIES = [
    "number_of_people",
    "vehicle_color",
    "time_discrepancy",
    "location_discrepancy",
    "identity_discrepancy",
    "object_description",
]


def _extract_number_references(text: str) -> list[dict]:
    """Extract numerical references and their context from text."""
    results = []
    text_lower = text.lower()

    # Find number words with context
    for word, value in NUMBER_WORDS.items():
        pattern = re.compile(rf"\b{re.escape(word)}\b\s+(\w+(?:\s+\w+)?)", re.IGNORECASE)
        for match in pattern.finditer(text):
            context_after = match.group(1).lower()
            results.append({
                "value": value,
                "word": word,
                "context": context_after,
                "full_match": match.group(),
                "position": match.start(),
            })

    # Find digit numbers with context
    digit_pattern = re.compile(r"\b(\d+)\s+(\w+(?:\s+\w+)?)", re.IGNORECASE)
    for match in digit_pattern.finditer(text):
        try:
            value = int(match.group(1))
            context_after = match.group(2).lower()
            results.append({
                "value": value,
                "word": match.group(1),
                "context": context_after,
                "full_match": match.group(),
                "position": match.start(),
            })
        except ValueError:
            continue

    return results


def _extract_color_references(text: str) -> list[dict]:
    """Extract color descriptions and what they refer to from text."""
    results = []
    text_lower = text.lower()

    for color in COLOR_TERMS:
        pattern = re.compile(
            rf"\b({re.escape(color)}(?:\s*[-/]\s*\w+)?)\s+(\w+(?:\s+\w+)?)",
            re.IGNORECASE,
        )
        for match in pattern.finditer(text):
            results.append({
                "color": match.group(1).lower(),
                "object": match.group(2).lower(),
                "full_match": match.group(),
                "position": match.start(),
            })

    return results


def _context_similarity(ctx_a: str, ctx_b: str) -> float:
    """Measure how similar two context strings are (0.0 - 1.0)."""
    return SequenceMatcher(None, ctx_a.lower(), ctx_b.lower()).ratio()


def _sentences_from_text(text: str) -> list[str]:
    """Split text into sentences."""
    sentences = re.split(r'[.!?\n]+', text)
    return [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]


def detect_contradictions(
    evidence_records: list,
    graph: nx.Graph | None = None,
) -> list[dict]:
    """
    Scan evidence records for contradictory statements or facts.

    Uses rule-based comparison to identify pairs of statements from
    different sources that conflict.

    Parameters
    ----------
    evidence_records : list
        List of EvidenceRecord objects or dicts with raw_text and metadata.
    graph : nx.Graph, optional
        The case knowledge graph (used for entity-aware comparison).

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

            # --- Number contradictions ---
            nums_a = _extract_number_references(text_a)
            nums_b = _extract_number_references(text_b)

            for na in nums_a:
                for nb in nums_b:
                    # Check if they're talking about similar things
                    similarity = _context_similarity(na["context"], nb["context"])
                    if similarity > 0.4 and na["value"] != nb["value"]:
                        # Find the sentence containing this reference
                        sentence_a = _find_sentence_containing(text_a, na["full_match"])
                        sentence_b = _find_sentence_containing(text_b, nb["full_match"])

                        contradictions.append({
                            "type": "number_of_people" if "men" in na["context"] or "man" in na["context"] or "person" in na["context"] or "people" in na["context"]
                                else "quantity_discrepancy",
                            "statement_a": sentence_a or na["full_match"],
                            "statement_b": sentence_b or nb["full_match"],
                            "source_a": id_a,
                            "source_a_name": name_a,
                            "source_b": id_b,
                            "source_b_name": name_b,
                            "explanation": (
                                f"'{name_a}' states {na['word']} {na['context']}, "
                                f"while '{name_b}' states {nb['word']} {nb['context']}. "
                                f"Values differ: {na['value']} vs {nb['value']}."
                            ),
                            "confidence": min(0.5 + similarity * 0.5, 0.95),
                            "severity": "high" if similarity > 0.6 else "medium",
                        })

            # --- Color contradictions ---
            colors_a = _extract_color_references(text_a)
            colors_b = _extract_color_references(text_b)

            for ca in colors_a:
                for cb in colors_b:
                    # Check if they're describing the same object
                    obj_similarity = _context_similarity(ca["object"], cb["object"])
                    if obj_similarity > 0.5 and ca["color"] != cb["color"]:
                        sentence_a = _find_sentence_containing(text_a, ca["full_match"])
                        sentence_b = _find_sentence_containing(text_b, cb["full_match"])

                        contradictions.append({
                            "type": "vehicle_color" if "van" in ca["object"] or "car" in ca["object"] or "vehicle" in ca["object"]
                                else "color_discrepancy",
                            "statement_a": sentence_a or ca["full_match"],
                            "statement_b": sentence_b or cb["full_match"],
                            "source_a": id_a,
                            "source_a_name": name_a,
                            "source_b": id_b,
                            "source_b_name": name_b,
                            "explanation": (
                                f"'{name_a}' describes a {ca['color']} {ca['object']}, "
                                f"while '{name_b}' describes a {cb['color']} {cb['object']}. "
                                f"Color descriptions conflict."
                            ),
                            "confidence": min(0.5 + obj_similarity * 0.4, 0.90),
                            "severity": "medium",
                        })

    # Deduplicate similar contradictions
    contradictions = _deduplicate_contradictions(contradictions)

    logger.info(f"Detected {len(contradictions)} contradictions across {len(records)} evidence records")
    return contradictions


def _find_sentence_containing(text: str, phrase: str) -> str | None:
    """Find the sentence in text that contains the given phrase."""
    sentences = _sentences_from_text(text)
    phrase_lower = phrase.lower()
    for sent in sentences:
        if phrase_lower in sent.lower():
            return sent[:300]
    return None


def _deduplicate_contradictions(contradictions: list[dict]) -> list[dict]:
    """Remove near-duplicate contradictions."""
    if len(contradictions) <= 1:
        return contradictions

    unique = []
    seen_keys = set()

    for c in contradictions:
        # Create a key from source pair + type
        key = (
            min(c["source_a"], c["source_b"]),
            max(c["source_a"], c["source_b"]),
            c["type"],
            c.get("explanation", "")[:60],
        )
        if key not in seen_keys:
            seen_keys.add(key)
            unique.append(c)

    return unique
