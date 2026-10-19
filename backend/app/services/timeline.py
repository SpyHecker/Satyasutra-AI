"""
Timeline Service — reconstructs chronological event sequences and detects gaps.

Week 1: stub implementation. Full integration in Week 5.
"""


def build_timeline(entities: list[dict]) -> list[dict]:
    """
    Build a chronological timeline from time-stamped entities/events.

    Parameters
    ----------
    entities : list[dict]
        Entities with optional timestamp fields.

    Returns
    -------
    list[dict]
        Sorted list of timeline events, each with:
        - timestamp (str): ISO 8601 datetime
        - description (str): event summary
        - source_id (str): evidence ID
        - type (str): event type
    """
    # TODO (Week 5): implement timestamp extraction, normalization, and sorting
    return []


def detect_gaps(timeline: list[dict], max_gap_hours: float = 24.0) -> list[dict]:
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
        List of gap dicts with: start, end, duration_hours.
    """
    # TODO (Week 5): implement gap detection logic
    return []
