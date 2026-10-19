"""
Report Generator — produces evidence-cited case reports.

Week 1: stub implementation. Full integration in Week 7.
"""


def generate_report(case_data: dict) -> str:
    """
    Generate a draft investigation report with inline evidence citations.

    Parameters
    ----------
    case_data : dict
        Aggregated case data including:
        - graph: serialized knowledge graph
        - timeline: chronological events
        - contradictions: detected conflicts
        - evidence: list of evidence metadata

    Returns
    -------
    str
        Markdown-formatted draft report with [Evidence-ID] citations.
    """
    # TODO (Week 7): implement report template + citation engine
    return "# Case Report\n\n*Report generation not yet implemented.*\n"
