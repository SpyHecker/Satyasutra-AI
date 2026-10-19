# Graph Schema

This directory contains the formal schema for the SatyaSutra knowledge graph.

## `graph_schema.json`

Defines all node and edge types used to model an investigation case.

### Node Types

| Type | Description |
| --- | --- |
| **Person** | An individual mentioned in or relevant to the case |
| **Location** | A physical place referenced in evidence |
| **Event** | A discrete occurrence with a timestamp |
| **Object** | A physical item of evidentiary relevance |
| **Document** | An uploaded evidence file (text, image, scan) |
| **Statement** | A specific claim or account made by a person |

### Edge Types

| Type | From → To | Description |
| --- | --- | --- |
| **PARTICIPATED_IN** | Person → Event | A person participated in an event |
| **LOCATED_AT** | Event → Location | An event took place at a location |
| **MENTIONED_IN** | Person/Object → Document | An entity is mentioned in a document |
| **OWNS** | Person → Object | A person owns or possesses an object |
| **RELATED_TO** | Entity → Entity | A general relationship between entities |
| **CONTRADICTS** | Statement → Statement | Two statements contain conflicting facts |
| **EXTRACTED_FROM** | Entity → Document | An entity was extracted by the NLP pipeline |

### Evidence Traceability

**Every edge** carries an `evidence_id` property that links back to the source document or statement from which the relationship was inferred. This ensures:

- Full audit trail from any graph connection to its source evidence
- Human reviewers can verify AI-suggested links
- Reports can generate inline `[Evidence-ID]` citations
