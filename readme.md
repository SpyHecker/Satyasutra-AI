# SatyaSutra

**An AI-assisted investigation tool that connects fragmented evidence — documents, images, and statements — into one auditable case view: a linked knowledge graph, a chronological timeline with gaps flagged, and a source-cited case report.**

![Status](https://img.shields.io/badge/status-in%20development-yellow)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Node](https://img.shields.io/badge/node-18%2B-green)

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Weekly Project Plan](#weekly-project-plan)
- [Design Constraints](#design-constraints)
- [Team](#team)
- [License](#license)

---

## Features

| Feature | Scope |
|---|---|
| Evidence Analysis Engine — OCR + NLP entity extraction (person, location, time, object) | MVP |
| Knowledge Graph — auto-linked nodes, every edge traceable to source evidence | MVP |
| Timeline Reconstruction — chronological ordering + automatic gap detection | MVP |
| Contradiction Detection — flags conflicting facts across sources | MVP |
| Evidence-Traceable Report Generator — draft report with inline citations | MVP |
| Case Q&A Chatbot — RAG over the case graph | Stretch |
| CCTV/video analytics, facial recognition, witness intake, scenario simulation, RBAC, multilingual OCR | Future scope |

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React |
| Backend / API | Flask / FastAPI |
| OCR + NLP Pipeline | Tesseract OCR, spaCy |
| Graph Database | Neo4j / NetworkX |
| Deployment | Render / AWS |

## Project Structure

```
satyasutra/
├── frontend/                # React app
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── App.jsx
│   └── package.json
├── backend/                  # Flask / FastAPI service
│   ├── app/
│   │   ├── routes/
│   │   ├── services/
│   │   │   ├── ocr.py
│   │   │   ├── nlp_extraction.py
│   │   │   ├── graph_builder.py
│   │   │   ├── timeline.py
│   │   │   ├── contradiction_detector.py
│   │   │   └── report_generator.py
│   │   └── main.py
│   └── requirements.txt
├── data/
│   ├── sample_evidence/      # sample docs/images for demo
│   └── schema/                # graph node/edge schema definitions
├── docs/
├── SatyaSutra_Pitch_Deck.pptx
├── .env.example
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Neo4j (local instance or Aura free tier) — or NetworkX for a no-DB local prototype
- Tesseract OCR installed locally

### Installation

```bash
git clone https://github.com/SpyHecker/satyasutra.git
cd satyasutra

# backend
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

# frontend
cd ../frontend
npm install
```

### Running Locally

```bash
# backend
cd backend
python -m app.main

# frontend (separate terminal)
cd frontend
npm run dev
```

## Weekly Project Plan

| Week | Focus | Key Tasks | Deliverable |
|---|---|---|---|
| 1 | Setup & Planning | Finalize tech stack; scaffold backend (Flask/FastAPI) and frontend (React); set up Neo4j/NetworkX; define graph schema (node/edge types); collect sample evidence dataset (sample docs, images, FIR-style text) | Working dev environment, repo scaffold, sample dataset |
| 2 | Evidence Analysis Engine | Integrate Tesseract OCR for document/image text extraction; integrate spaCy NER for person/location/time/object extraction; build evidence upload API | Upload → extracted entities pipeline |
| 3 | Knowledge Graph Construction | Build graph builder service converting entities into nodes/edges; implement co-occurrence-based auto-linking; persist graph in Neo4j/NetworkX | Evidence auto-converted into a queryable graph |
| 4 | Explainable Links + Graph UI | Track source-evidence metadata per edge; build frontend graph visualization (e.g. react-force-graph); implement click-an-edge-to-explain interaction | Interactive graph UI with evidence-backed links |
| 5 | Timeline Reconstruction | Extract and normalize timestamps from evidence; build chronological ordering service; implement gap-detection logic; build frontend timeline component | Timeline view with flagged gaps |
| 6 | Contradiction Detection | Design fact-comparison logic (rule-based or NLI-based) across sources; flag conflicting statements/records; build contradiction UI | System flags conflicting facts across evidence |
| 7 | Report Generator + Integration | Build report generator aggregating graph + timeline + contradictions; implement inline evidence-ID citations; wire all modules into one end-to-end flow | End-to-end pipeline: upload → cited draft report |
| 8 | Stretch Goal, Testing & Demo Prep | Build Case Q&A chatbot if time allows (RAG over case graph); fix bugs; polish UI; prepare sample case walkthrough and demo script | Demo-ready product + presentation |

*Timeline assumes an 8-week build; compress or extend per your actual schedule.*

## Design Constraints

- No individual guilt/criminal-probability scores — only evidence strength and contradictions are surfaced
- Every AI-suggested link requires human confirmation before being accepted into the case graph
- All generated reports are labeled "investigator-review draft," never "court-ready"

## Team

**Team SatyaSutra**
PES's Modern College of Engineering, Pune

| Name | Role |
|---|---|
| Yash [Last Name] | [Role] |
| [Team Member] | [Role] |
| [Team Member] | [Role] |

*Guided by [Faculty Mentor Name]*

## License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.