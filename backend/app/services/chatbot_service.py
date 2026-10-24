"""
SatyaSutra AI Public Assistant — Secure Landing-Page Knowledge Model

SECURITY POLICY & CONSTRAINTS:
1. NO CREDENTIALS: Never reveal login credentials, passwords, admin accounts, or secret keys.
2. NO TECH STACK / VULNERABILITY EXPOSURE: Do not disclose internal frameworks, database details,
   server ports, file paths, or dependencies that could endanger the web application.
3. NO INTERNAL OR DETECTIVE OPERATIONS: If asked about internal operations, active cases, uploaded
   evidence, suspect dossiers, or post-login actions, respond with the polite "sorry" refusal.
4. PUBLIC LANDING PAGE ONLY: Provides high-level operational answers strictly derived from public
   landing page content.
"""

import re
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ============================================================================
# SECURITY PATTERN DETECTION
# ============================================================================

# Patterns requesting credentials, passwords, keys, or authentication bypass
CREDENTIAL_PATTERNS = [
    r"\bpass(?:word|code)?s?\b",
    r"\blogin cred(?:ential)?s?\b",
    r"\bcredentials?\b",
    r"\badmin cred(?:ential)?s?\b",
    r"\badmin login\b",
    r"\badmin email\b",
    r"\badmin user\b",
    r"\bsecret(?:s| key)?\b",
    r"\bjwt\b",
    r"\btoken\b",
    r"\bapi[ _-]?key\b",
    r"\bbypass\b",
    r"\bhack\b",
    r"\bauth(?:entication)? key\b",
    r"\bwhat is (?:the )?(?:admin )?pass(?:word)?\b",
    r"\bgive me (?:the )?(?:admin )?login\b",
    r"\bhow to login as admin\b",
]

# Patterns requesting internal technical stack, database details, or server infrastructure
TECH_STACK_PATTERNS = [
    r"\btech[ _-]?stack\b",
    r"\btechnolog(?:y|ies)\b",
    r"\bbackend framework\b",
    r"\bdatabase (?:type|name|url|conn|string)\b",
    r"\bsqlite\b",
    r"\bmongodb\b",
    r"\bfastapi\b",
    r"\buvicorn\b",
    r"\bpackage\.json\b",
    r"\brequirements\.txt\b",
    r"\bserver port\b",
    r"\bfile path\b",
    r"\bserver config\b",
    r"\bvulnerabilit(?:y|ies)\b",
    r"\bsource code\b",
    r"\binternal architecture\b",
    r"\bwhat stack\b",
    r"\blibraries used\b",
    r"\bdependencies\b",
]

# Patterns requesting internal detective operations, active case evidence, or post-login tools
INTERNAL_OPERATION_PATTERNS = [
    r"\bdetective operations?\b",
    r"\bdetectives?\b",
    r"\binternal operations?\b",
    r"\binternal investigative?\b",
    r"\bactive cases?\b",
    r"\bcase dossiers?\b",
    r"\bview cases?\b",
    r"\bsuspect lists?\b",
    r"\bsuspects?\b",
    r"\bcase files?\b",
    r"\buploaded evidences?\b",
    r"\bevidence files?\b",
    r"\bwho is (?:the )?suspect\b",
    r"\binterrogations?\b",
    r"\bwiretaps?\b",
    r"\bpost[ _-]logins?\b",
    r"\bafter logins?\b",
    r"\binternal data\b",
    r"\binternal tools?\b",
    r"\binvestigator workspace\b",
    r"\bconfidential\b",
    r"\bclassified\b",
    r"\bsearch evidences?\b",
    r"\bview databases?\b",
    r"\bcase #?cr-",
    r"\bstate vs\b",
    r"\bvikramaditya\b",
]


# ============================================================================
# PUBLIC LANDING PAGE KNOWLEDGE CORPUS
# Strictly limited to public-facing landing page information
# ============================================================================

PUBLIC_LANDING_KNOWLEDGE = [
    {
        "id": "landing_overview",
        "title": "What is SatyaSutra?",
        "category": "Platform Overview",
        "keywords": [
            "what is satyasutra", "about satyasutra", "overview", "introduction",
            "purpose", "mission", "platform", "what does it do", "meaning"
        ],
        "summary": "AI-assisted forensic intelligence platform that connects fragmented evidence into an auditable case view.",
        "content": (
            "**SatyaSutra** (*AI-Assisted Forensic Intelligence*) is designed to connect fragmented "
            "investigative evidence — such as documents, crime-scene photographs, financial records, "
            "and witness statements — into one unified, auditable case view.\n\n"
            "As highlighted on our landing page, SatyaSutra provides:\n"
            "- **100% Evidence Traceability**: Connecting disparate clues with source-linked references.\n"
            "- **Zero AI Hallucination**: Every assertion includes verifiable inline citations.\n"
            "- **Automated Timeline Gap & Alibi Spotting**: Surfacing unverified intervals in event chronologies.\n"
            "- **Unified Case Vault**: Secure, auditable storage for investigative materials."
        ),
        "related_links": ["/"],
    },
    {
        "id": "landing_pipeline",
        "title": "4-Stage Investigation Pipeline",
        "category": "Workflow",
        "keywords": [
            "how it works", "pipeline", "workflow", "4 stages", "four stages",
            "steps", "process", "investigation pipeline"
        ],
        "summary": "Ingest & Transcribe -> Extract & Cross-Reference -> Audit Graph & Timeline -> Generate Traceable Dossier.",
        "content": (
            "SatyaSutra's public workflow follows an automated **4-Stage Intelligence Pipeline**:\n\n"
            "1. **Stage 01 — Ingest & Transcribe**: Accepts case documents, crime-scene photographs, and typed statements for automated transcription.\n"
            "2. **Stage 02 — Extract & Cross-Reference**: Automatically identifies key entities (persons, locations, time markers) and cross-links them.\n"
            "3. **Stage 03 — Audit Graph & Timeline**: Assembles an interconnected relationship view, highlights flagged contradictions, and identifies timeline gaps.\n"
            "4. **Stage 04 — Generate Traceable Dossier**: Prepares an investigator draft summary with inline evidence citations."
        ),
        "related_links": ["/"],
    },
    {
        "id": "landing_capabilities",
        "title": "Core Capabilities (Landing Page Pillars)",
        "category": "Capabilities",
        "keywords": [
            "capabilities", "features", "pillars", "what can it do", "ocr",
            "entity extraction", "knowledge graph", "timeline", "contradiction"
        ],
        "summary": "Multimodal Ingestion, NLP Extraction, Knowledge Graph, Timeline Gaps, Contradiction Spotter, and Case Vault.",
        "content": (
            "According to the SatyaSutra landing page, the platform is built on **6 Core Pillars**:\n\n"
            "- 📄 **Multimodal Ingestion & OCR**: Processes scanned FIRs, affidavits, and scene photos.\n"
            "- 🧠 **NLP Entity Extraction**: Identifies persons, places, organizations, and time markers.\n"
            "- 🕸️ **Interactive Knowledge Graph**: Visually networks connected entities with explainable links.\n"
            "- ⏱️ **Timeline Reconstruction & Gaps**: Chronologically sequences events and flags unverified alibi intervals.\n"
            "- ⚡ **Cross-Source Contradiction Spotter**: Detects conflicting statements and discrepancies across records.\n"
            "- 🍃 **Secure Case Vault**: Enterprise-grade storage for case dossiers."
        ),
        "related_links": ["/"],
    },
    {
        "id": "landing_use_cases",
        "title": "Public Use Cases & Applications",
        "category": "Use Cases",
        "keywords": [
            "use cases", "who uses this", "applications", "target audience",
            "police", "law enforcement", "lawyers", "journalists", "fraud"
        ],
        "summary": "Built for Law Enforcement, Legal Counsel, Investigative Journalists, and Corporate Fraud audits.",
        "content": (
            "SatyaSutra is designed for four major public domains:\n\n"
            "- 🚓 **Law Enforcement**: Consolidating FIRs, surveillance logs, and statements to speed up investigation reviews.\n"
            "- ⚖️ **Legal Counsel**: Pinpointing contradictions in witness testimonies and verifying timeline alibis.\n"
            "- 📰 **Investigative Journalism**: Connecting leaks, corporate registries, and public interest records.\n"
            "- 💼 **Corporate Forensics & Compliance**: Evaluating internal audits, whistleblower claims, and AML reviews."
        ),
        "related_links": ["/"],
    },
    {
        "id": "landing_ethics",
        "title": "Ethical Constraints & Guardrails",
        "category": "Governance",
        "keywords": [
            "ethics", "guardrails", "guilt score", "criminal probability",
            "human in the loop", "hallucination", "constraints"
        ],
        "summary": "No guilt scoring, human-in-the-loop confirmation required, and reports labeled as investigator drafts.",
        "content": (
            "SatyaSutra strictly enforces **Three Ethical Principles**:\n\n"
            "1. 🚫 **No Guilt Scoring**: The platform NEVER calculates a guilt percentage or criminal probability score.\n"
            "2. 🤝 **Human-in-the-Loop Confirmation**: Every AI-suggested link requires human investigator verification.\n"
            "3. ⚖️ **Investigator-Review Draft Only**: All generated summaries are labeled strictly as review drafts, not court verdicts."
        ),
        "related_links": ["/"],
    },
    {
        "id": "landing_team",
        "title": "Creators & Affiliation",
        "category": "About",
        "keywords": [
            "who created", "who made", "creators", "team", "college",
            "pes", "pune", "authors", "developers", "mcoe"
        ],
        "summary": "Developed by Team SatyaSutra from PES's Modern College of Engineering, Pune.",
        "content": (
            "**SatyaSutra** was created by **Team SatyaSutra** from **PES's Modern College of Engineering, Pune**.\n\n"
            "- **Team**: Team SatyaSutra (Pune, India)\n"
            "- **Institution**: Progressive Education Society's Modern College of Engineering (MCOE)\n"
            "- **Purpose**: Building transparent, explainable forensic intelligence for justice."
        ),
        "related_links": ["/"],
    },
    {
        "id": "landing_portal",
        "title": "How to Access the Investigation Portal",
        "category": "Access",
        "keywords": [
            "how to login", "where to login", "access portal", "sign in page", "portal"
        ],
        "summary": "Access the secure portal using departmentally issued credentials at the login page.",
        "content": (
            "Authorized investigators can sign in at the [Portal Sign In Page](/login).\n\n"
            "Please use your officially issued departmental credentials to access the workspace. "
            "For account setup or password assistance, please contact your system administrator."
        ),
        "related_links": ["/login"],
    },
]

# Preset public suggestions displayed on the landing page assistant
PUBLIC_SUGGESTED_QUESTIONS = [
    "What is SatyaSutra?",
    "How does the 4-stage pipeline work?",
    "What are the core capabilities on the landing page?",
    "Who are the target users and use cases?",
    "What ethical guidelines does SatyaSutra follow?",
    "Who created SatyaSutra?",
]


# ============================================================================
# SECURITY SHIELD & QUERY EVALUATOR
# ============================================================================

def _matches_any_pattern(text: str, patterns: list[str]) -> bool:
    """Check if query matches any regex in the security pattern list."""
    for pat in patterns:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return False


def _tokenize(text: str) -> list[str]:
    """Clean and tokenize text into lowercase words."""
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    return [word for word in cleaned.split() if len(word) > 1]


class SecureSatyaSutraChatbotModel:
    """
    Secure public assistant model trained strictly on landing page information.
    Enforces security shields against credential requests, technical stack exposure,
    and internal detective operations.
    """

    def __init__(self):
        self.knowledge_base = PUBLIC_LANDING_KNOWLEDGE
        self.suggested_questions = PUBLIC_SUGGESTED_QUESTIONS
        logger.info("Initialized SecureSatyaSutraChatbotModel with public landing page knowledge.")

    def get_suggested_questions(self) -> list[str]:
        return self.suggested_questions

    def answer_query(self, query: str, conversation_history: Optional[list[dict[str, str]]] = None) -> dict[str, Any]:
        raw_query = (query or "").strip()
        if not raw_query:
            return {
                "answer": (
                    "Hello! I am the SatyaSutra Public Assistant. "
                    "I can answer basic questions about our platform, 4-stage pipeline, and capabilities as outlined on the landing page."
                ),
                "sources": ["SatyaSutra Landing Page"],
                "suggested_followups": self.suggested_questions[:3],
                "confidence": 1.0,
            }

        query_lower = raw_query.lower()

        # ====================================================================
        # SECURITY SHIELD 1: CREDENTIALS & SENSITIVE KEYS
        # ====================================================================
        if _matches_any_pattern(query_lower, CREDENTIAL_PATTERNS):
            return {
                "answer": (
                    "🔒 **I am sorry, but for security and privacy reasons, I cannot disclose "
                    "login credentials, passwords, or authentication keys.**\n\n"
                    "If you are an authorized investigator, please sign in at the [Portal Sign In Page](/login) "
                    "using your departmentally issued credentials. If you require access, please reach out to your system administrator."
                ),
                "sources": ["Security Policy"],
                "suggested_followups": [
                    "What is SatyaSutra?",
                    "How does the 4-stage pipeline work?",
                    "What are the core capabilities on the landing page?",
                ],
                "confidence": 1.0,
            }

        # ====================================================================
        # SECURITY SHIELD 2: TECH STACK & INFRASTRUCTURE EXPOSURE
        # ====================================================================
        if _matches_any_pattern(query_lower, TECH_STACK_PATTERNS):
            return {
                "answer": (
                    "🛡️ **I am sorry, but to ensure platform security and protect investigative systems from external risks, "
                    "internal technical stack details, database architectures, and server configurations are confidential and cannot be disclosed.**\n\n"
                    "SatyaSutra is an AI-assisted forensic intelligence platform designed to connect fragmented evidence into auditable case dossiers. "
                    "You can read more about its public capabilities and workflow on our landing page."
                ),
                "sources": ["Platform Security Policy"],
                "suggested_followups": [
                    "What is SatyaSutra?",
                    "What are the core capabilities on the landing page?",
                    "How does the 4-stage pipeline work?",
                ],
                "confidence": 1.0,
            }

        # ====================================================================
        # SECURITY SHIELD 3: INTERNAL OR DETECTIVE OPERATIONS (AFTER LOGIN)
        # ====================================================================
        if _matches_any_pattern(query_lower, INTERNAL_OPERATION_PATTERNS):
            return {
                "answer": (
                    "⚠️ **I am sorry, but I can only answer general questions based on public landing page information.**\n\n"
                    "Internal detective operations, active investigation files, uploaded evidence records, and case dossiers "
                    "are strictly confidential. They are restricted exclusively to authorized personnel within the authenticated "
                    "forensic workspace after secure login."
                ),
                "sources": ["Confidentiality Policy"],
                "suggested_followups": [
                    "What is SatyaSutra?",
                    "How does the 4-stage pipeline work?",
                    "Who are the target users and use cases?",
                ],
                "confidence": 1.0,
            }

        # ====================================================================
        # GREETINGS
        # ====================================================================
        greetings = ["hi", "hello", "hey", "namaste", "good morning", "good evening"]
        if query_lower in greetings or any(query_lower.startswith(g + " ") for g in greetings if len(query_lower) < 15):
            return {
                "answer": (
                    "👋 **Hello! Welcome to the SatyaSutra Platform Guide.**\n\n"
                    "I can provide basic operational answers based on our public landing page data, including:\n"
                    "- *What is SatyaSutra?*\n"
                    "- *The 4-Stage Investigation Pipeline*\n"
                    "- *Core capabilities and public use cases*\n"
                    "- *Ethical guardrails and project information*\n\n"
                    "How can I help you today?"
                ),
                "sources": ["Landing Page Guide"],
                "suggested_followups": self.suggested_questions[:3],
                "confidence": 1.0,
            }

        if any(term in query_lower for term in ["thank you", "thanks", "bye", "goodbye"]):
            return {
                "answer": "You're welcome! Feel free to ask if you have any more questions about the SatyaSutra platform. Have a great day!",
                "sources": [],
                "suggested_followups": ["What is SatyaSutra?", "How does the 4-stage pipeline work?"],
                "confidence": 1.0,
            }

        # ====================================================================
        # LANDING PAGE KNOWLEDGE MATCHING
        # ====================================================================
        query_tokens = set(_tokenize(raw_query))
        ranked_items = []

        for item in self.knowledge_base:
            score = 0.0
            # Keyword matching
            for kw in item["keywords"]:
                if kw in query_lower:
                    score += 10.0
                elif query_lower in kw:
                    score += 5.0
                else:
                    overlap = query_tokens.intersection(set(_tokenize(kw)))
                    if overlap:
                        score += len(overlap) * 2.0

            # Title matching
            title_overlap = query_tokens.intersection(set(_tokenize(item["title"])))
            score += len(title_overlap) * 3.0

            if score > 2.0:
                ranked_items.append((score, item))

        ranked_items.sort(key=lambda x: x[0], reverse=True)

        if ranked_items:
            best_score, top_item = ranked_items[0]
            followups = [k["title"] for k in self.knowledge_base if k["id"] != top_item["id"]][:3]

            return {
                "answer": top_item["content"],
                "sources": [top_item["title"]],
                "related_links": top_item.get("related_links", ["/"]),
                "suggested_followups": followups,
                "confidence": min(1.0, round(best_score / 15.0, 2)),
            }

        # Fallback for questions outside public landing page scope
        return {
            "answer": (
                "I can only provide general, public information based on the SatyaSutra landing page. "
                "Here is what I can assist you with:\n\n"
                "- **Overview**: Learn what SatyaSutra is and its mission.\n"
                "- **Pipeline**: Understand the 4-stage intelligence pipeline.\n"
                "- **Capabilities**: Explore the core platform capabilities.\n"
                "- **Use Cases**: Discover how law enforcement and legal teams use SatyaSutra.\n"
                "- **Ethics**: Learn about our zero-guilt-score and human-in-the-loop policies.\n\n"
                "Please choose a topic above or ask a general question about the website."
            ),
            "sources": ["Landing Page Directory"],
            "suggested_followups": self.suggested_questions[:4],
            "confidence": 0.4,
        }


# Singleton instance
chatbot_service = SecureSatyaSutraChatbotModel()
