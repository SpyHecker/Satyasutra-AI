"""
Graph Builder Service — constructs a knowledge graph from extracted entities.

Converts NLP-extracted entities into a NetworkX knowledge graph where:
- Each unique entity becomes a node (deduplicated by normalized text + category)
- Co-occurrence within the same document creates edges
- Every edge stores the source evidence ID for traceability
- Provides serialization to JSON for the frontend graph viewer
"""

import logging
from collections import defaultdict
from itertools import combinations

import networkx as nx

logger = logging.getLogger(__name__)

# Category → color mapping for frontend visualization
CATEGORY_COLORS = {
    "Person": "#6366f1",      # Indigo
    "Location": "#22c55e",    # Green
    "Time": "#eab308",        # Yellow
    "Object": "#f97316",      # Orange
    "Organization": "#3b82f6",# Blue
    "Event": "#ef4444",       # Red
    "Legal": "#8b5cf6",       # Purple
    "Quantity": "#06b6d4",    # Cyan
    "Language": "#ec4899",    # Pink
    "Other": "#64748b",       # Slate
}


def _normalize_key(text: str, category: str) -> str:
    """Create a unique node key from entity text + category."""
    return f"{category}::{text.strip().lower()}"


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
    graph = nx.Graph()

    if not entities:
        return graph

    # Deduplicate entities and build nodes
    node_keys = []
    for ent in entities:
        text = ent.get("text", "").strip()
        category = ent.get("category", "Other")
        label = ent.get("label", "")

        if not text:
            continue

        key = _normalize_key(text, category)

        if not graph.has_node(key):
            graph.add_node(
                key,
                label=text,
                display_name=text,
                category=category,
                ner_label=label,
                color=CATEGORY_COLORS.get(category, CATEGORY_COLORS["Other"]),
                sources=[source_document_id] if source_document_id else [],
                mention_count=1,
            )
        else:
            # Update existing node
            node = graph.nodes[key]
            node["mention_count"] = node.get("mention_count", 0) + 1
            if source_document_id and source_document_id not in node.get("sources", []):
                node["sources"].append(source_document_id)

        node_keys.append(key)

    # Deduplicate node_keys for edge creation
    unique_keys = list(dict.fromkeys(node_keys))

    # Create co-occurrence edges between all entity pairs in the same document
    for key_a, key_b in combinations(unique_keys, 2):
        if graph.has_edge(key_a, key_b):
            edge = graph.edges[key_a, key_b]
            edge["weight"] = edge.get("weight", 1) + 1
            if source_document_id and source_document_id not in edge.get("evidence_ids", []):
                edge["evidence_ids"].append(source_document_id)
        else:
            graph.add_edge(
                key_a,
                key_b,
                weight=1,
                relation="co_occurrence",
                evidence_ids=[source_document_id] if source_document_id else [],
            )

    logger.info(
        f"Built graph: {graph.number_of_nodes()} nodes, "
        f"{graph.number_of_edges()} edges from {len(entities)} entities"
    )
    return graph


def merge_graphs(base: nx.Graph, new: nx.Graph) -> nx.Graph:
    """
    Merge a new evidence graph into the existing case graph.

    Handles node deduplication (same key = merge attributes)
    and edge weight accumulation.

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
    for node_id, attrs in new.nodes(data=True):
        if base.has_node(node_id):
            existing = base.nodes[node_id]
            # Merge sources
            existing_sources = existing.get("sources", [])
            new_sources = attrs.get("sources", [])
            for src in new_sources:
                if src and src not in existing_sources:
                    existing_sources.append(src)
            existing["sources"] = existing_sources
            # Accumulate mention counts
            existing["mention_count"] = (
                existing.get("mention_count", 1) + attrs.get("mention_count", 1)
            )
        else:
            base.add_node(node_id, **attrs)

    for u, v, attrs in new.edges(data=True):
        if base.has_edge(u, v):
            existing = base.edges[u, v]
            existing["weight"] = existing.get("weight", 1) + attrs.get("weight", 1)
            # Merge evidence IDs
            existing_eids = existing.get("evidence_ids", [])
            for eid in attrs.get("evidence_ids", []):
                if eid and eid not in existing_eids:
                    existing_eids.append(eid)
            existing["evidence_ids"] = existing_eids
        else:
            base.add_edge(u, v, **attrs)

    logger.info(
        f"Merged graph now has {base.number_of_nodes()} nodes, "
        f"{base.number_of_edges()} edges"
    )
    return base


def graph_to_json(graph: nx.Graph) -> dict:
    """
    Serialize a NetworkX graph to a JSON-friendly format for
    the frontend react-force-graph visualization.

    Returns
    -------
    dict
        {"nodes": [...], "links": [...], "stats": {...}}
    """
    nodes = []
    for node_id, attrs in graph.nodes(data=True):
        nodes.append({
            "id": node_id,
            "label": attrs.get("display_name", attrs.get("label", node_id)),
            "category": attrs.get("category", "Other"),
            "color": attrs.get("color", CATEGORY_COLORS["Other"]),
            "ner_label": attrs.get("ner_label", ""),
            "sources": attrs.get("sources", []),
            "mention_count": attrs.get("mention_count", 1),
            "val": max(2, min(attrs.get("mention_count", 1) * 2, 12)),  # node size
        })

    links = []
    for u, v, attrs in graph.edges(data=True):
        links.append({
            "source": u,
            "target": v,
            "weight": attrs.get("weight", 1),
            "relation": attrs.get("relation", "co_occurrence"),
            "evidence_ids": attrs.get("evidence_ids", []),
        })

    # Category breakdown
    category_counts = defaultdict(int)
    for n in nodes:
        category_counts[n["category"]] += 1

    return {
        "nodes": nodes,
        "links": links,
        "stats": {
            "total_nodes": len(nodes),
            "total_edges": len(links),
            "categories": dict(category_counts),
        },
    }


# ---------------------------------------------------------------------------
# Module-level case graph (singleton for this prototype)
# ---------------------------------------------------------------------------
_case_graph = nx.Graph()


def get_case_graph() -> nx.Graph:
    """Return the case-level graph singleton."""
    global _case_graph
    return _case_graph


def add_evidence_to_graph(entities: list[dict], evidence_id: str) -> dict:
    """
    Build a graph from new evidence entities and merge into the case graph.

    Returns the serialized full graph JSON.
    """
    global _case_graph
    new_graph = build_graph(entities, source_document_id=evidence_id)
    _case_graph = merge_graphs(_case_graph, new_graph)
    return graph_to_json(_case_graph)


def reset_case_graph():
    """Reset the case graph (used for testing or new case)."""
    global _case_graph
    _case_graph = nx.Graph()


def rebuild_case_graph(evidence_records: list) -> dict:
    """
    Rebuild the entire case graph from all evidence records.

    Parameters
    ----------
    evidence_records : list
        List of EvidenceRecord objects from the evidence store.

    Returns
    -------
    dict
        Serialized graph JSON.
    """
    global _case_graph
    _case_graph = nx.Graph()

    for record in evidence_records:
        entities = [e.model_dump() if hasattr(e, "model_dump") else e for e in record.entities]
        if entities:
            new_graph = build_graph(entities, source_document_id=record.id)
            _case_graph = merge_graphs(_case_graph, new_graph)

    return graph_to_json(_case_graph)
