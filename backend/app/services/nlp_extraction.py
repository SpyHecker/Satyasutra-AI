"""
NLP Extraction Service — extracts named entities from text using spaCy.

Maps spaCy NER labels to the SatyaSutra graph schema categories:
  Person, Location, Time, Object, Organization, Quantity
"""

import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# Mapping from spaCy NER labels → SatyaSutra schema categories
LABEL_MAP: dict[str, str] = {
    # Person
    "PERSON": "Person",
    # Location
    "GPE": "Location",       # Countries, cities, states
    "LOC": "Location",       # Mountains, rivers, etc.
    "FAC": "Location",       # Buildings, airports, etc.
    # Time
    "DATE": "Time",
    "TIME": "Time",
    # Object
    "PRODUCT": "Object",
    "WORK_OF_ART": "Object",
    # Organization
    "ORG": "Organization",
    "NORP": "Organization",  # Nationalities, religious/political groups
    # Quantity
    "MONEY": "Quantity",
    "QUANTITY": "Quantity",
    "CARDINAL": "Quantity",
    "ORDINAL": "Quantity",
    "PERCENT": "Quantity",
    # Event
    "EVENT": "Event",
    # Legal
    "LAW": "Legal",
    # Language
    "LANGUAGE": "Language",
}


@lru_cache(maxsize=1)
def _load_model():
    """
    Load the spaCy NER model (singleton).

    Uses en_core_web_sm by default. Falls back to a blank model
    if the model is not installed.
    """
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        logger.info("Loaded spaCy model: en_core_web_sm")
        return nlp
    except OSError:
        logger.warning(
            "spaCy model 'en_core_web_sm' not found. "
            "Run: python -m spacy download en_core_web_sm"
        )
        raise RuntimeError(
            "spaCy model 'en_core_web_sm' is not installed. "
            "Run: python -m spacy download en_core_web_sm"
        )


def extract_entities(text: str) -> list[dict]:
    """
    Extract named entities from text using spaCy NER.

    Parameters
    ----------
    text : str
        Plain text content (e.g., from OCR output).

    Returns
    -------
    list[dict]
        List of entity dicts with keys:
        - text (str): the entity text
        - label (str): spaCy NER label (e.g., PERSON, GPE)
        - category (str): mapped SatyaSutra category (e.g., Person, Location)
        - start (int): character offset start
        - end (int): character offset end
    """
    if not text or not text.strip():
        return []

    nlp = _load_model()

    # Process the text (limit to first 100,000 chars to avoid memory issues)
    doc = nlp(text[:100_000])

    # Extract entities
    raw_entities = []
    for ent in doc.ents:
        category = LABEL_MAP.get(ent.label_, "Other")
        raw_entities.append({
            "text": ent.text.strip(),
            "label": ent.label_,
            "category": category,
            "start": ent.start_char,
            "end": ent.end_char,
        })

    # Deduplicate by (normalized_text, category)
    seen = set()
    unique_entities = []
    for ent in raw_entities:
        key = (ent["text"].lower().strip(), ent["category"])
        if key not in seen:
            seen.add(key)
            unique_entities.append(ent)

    logger.info(f"Extracted {len(unique_entities)} unique entities from {len(text)} chars")
    return unique_entities


def get_entity_summary(entities: list[dict]) -> dict[str, int]:
    """
    Get a count summary of entities by category.

    Parameters
    ----------
    entities : list[dict]
        Entity list from extract_entities().

    Returns
    -------
    dict[str, int]
        Mapping of category → count. E.g., {"Person": 5, "Location": 3}
    """
    summary: dict[str, int] = {}
    for ent in entities:
        cat = ent.get("category", "Other")
        summary[cat] = summary.get(cat, 0) + 1
    return summary
