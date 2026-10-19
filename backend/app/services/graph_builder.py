"""
Graph Builder Service — constructs a knowledge graph from extracted entities.

Week 1: stub implementation. Full integration in Week 3.
"""

import networkx as nx


def build_graph(entities: list[dict], source_document_id: str = "") -> nx.Graph:
    """
    Build a NetworkX knowledge graph from a list of extracted entities.

    Each entity becomes a node; co-occurrence within the same document
    creates edges. Every edge stores the source evidence ID for
    traceability.

    Parameters
    ----------
    entities : list[dict]
        Extracted entities from nlp_extraction.extract_entities().
    source_document_id : str
        ID of the source document for edge provenance.

    Returns
    -------
    nx.Graph
        A NetworkX graph with entity nodes and co-occurrence edges.
    """
    # TODO (Week 3): implement entity-to-node conversion and co-occurrence linking
    graph = nx.Graph()
    return graph


def merge_graphs(base: nx.Graph, new: nx.Graph) -> nx.Graph:
    """
    Merge a new evidence graph into the existing case graph.

    Parameters
    ----------
    base : nx.Graph
        The existing case-level graph.
    new : nx.Graph
        A newly extracted evidence graph to merge in.

    Returns
    -------
    nx.Graph
        The merged graph.
    """
    # TODO (Week 3): implement graph merging with deduplication
    return nx.compose(base, new)
