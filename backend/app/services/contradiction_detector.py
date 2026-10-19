"""
Contradiction Detector — finds conflicting facts across evidence sources.

Week 1: stub implementation. Full integration in Week 6.
"""

import networkx as nx


def detect_contradictions(graph: nx.Graph) -> list[dict]:
    """
    Scan the case knowledge graph for contradictory statements or facts.

    Uses rule-based comparison (and optionally NLI) to identify pairs of
    statements/facts from different sources that conflict.

    Parameters
    ----------
    graph : nx.Graph
        The case knowledge graph.

    Returns
    -------
    list[dict]
        List of contradiction dicts, each with:
        - statement_a (str): first statement
        - statement_b (str): conflicting statement
        - source_a (str): evidence ID for statement A
        - source_b (str): evidence ID for statement B
        - explanation (str): why these contradict
        - confidence (float): 0.0 – 1.0
    """
    # TODO (Week 6): implement rule-based and/or NLI contradiction detection
    return []
