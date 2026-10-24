/**
 * Client-side Secure Knowledge Model & Fallback Engine for SatyaSutra
 * 
 * SECURITY RULES:
 * 1. Never reveal login credentials, passwords, or admin tokens.
 * 2. Never reveal tech stack, database, or server infrastructure that could endanger the site.
 * 3. Apologize with "I am sorry..." when asked about internal detective operations, active cases,
 *    or post-login tools.
 * 4. Only provide high-level answers based on public landing page information.
 */

// Regex patterns to intercept sensitive inquiries
const CREDENTIAL_REGEX = /\b(password|passcode|credentials?|login cred|admin cred|admin login|admin email|admin user|secret|token|jwt|api[ _-]?key|bypass|hack)\b/i;
const TECH_STACK_REGEX = /\b(tech[ _-]?stack|technolog|backend|fastapi|uvicorn|sqlite|mongodb|database|server port|vulnerabilit|source code|package\.json|requirements\.txt|dependencies)\b/i;
const INTERNAL_OP_REGEX = /\b(detective operations?|detectives?|internal operations?|internal investigative|active cases?|case dossiers?|suspect lists?|suspects?|case files?|uploaded evidences?|evidence files?|who is (?:the )?suspect|interrogations?|wiretaps?|post[ _-]logins?|after logins?|internal data|internal tools?|investigator workspace|confidential|classified|search evidences?|view databases?|case #?cr-|state vs|vikramaditya)\b/i;

export const PUBLIC_KNOWLEDGE = [
  {
    id: "landing_overview",
    title: "What is SatyaSutra?",
    keywords: ["what is satyasutra", "about satyasutra", "overview", "introduction", "purpose", "mission"],
    answer: `**SatyaSutra** (*AI-Assisted Forensic Intelligence*) is designed to connect fragmented investigative evidence — such as documents, crime-scene photographs, financial records, and witness statements — into one unified, auditable case view.

Key highlights from our landing page:
- 🔒 **100% Evidence Traceable**: Connects fragmented clues with direct references.
- ⚡ **Zero AI Hallucination**: Employs verified inline citations.
- ⏱️ **Automated Timeline Gap & Alibi Spotting**: Identifies unverified intervals in event chronologies.
- 🍃 **Unified Case Vault**: Secure, auditable storage for investigative materials.`,
  },
  {
    id: "landing_pipeline",
    title: "4-Stage Investigation Pipeline",
    keywords: ["how it works", "pipeline", "workflow", "4 stages", "four stages", "steps", "process"],
    answer: `SatyaSutra features an automated **4-Stage Intelligence Pipeline** (as shown on our landing page):

1. **Stage 01 — Ingest & Transcribe**: Accepts case documents, crime-scene photographs, and typed statements for automated transcription.
2. **Stage 02 — Extract & Cross-Reference**: Automatically identifies key entities (persons, locations, time markers) and cross-links them.
3. **Stage 03 — Audit Graph & Timeline**: Assembles an interconnected relationship view, highlights flagged contradictions, and identifies timeline gaps.
4. **Stage 04 — Generate Traceable Dossier**: Prepares an investigator draft summary with inline evidence citations.`,
  },
  {
    id: "landing_capabilities",
    title: "Core Capabilities (Landing Page Pillars)",
    keywords: ["capabilities", "features", "pillars", "what can it do", "ocr", "entity extraction", "knowledge graph", "timeline", "contradiction"],
    answer: `According to the SatyaSutra landing page, the platform is built on **6 Core Pillars**:

- 📄 **Multimodal Ingestion & OCR**: Processes scanned FIRs, affidavits, and scene photos.
- 🧠 **NLP Entity Extraction**: Identifies persons, places, organizations, and time markers.
- 🕸️ **Interactive Knowledge Graph**: Visually networks connected entities with explainable links.
- ⏱️ **Timeline Reconstruction & Gaps**: Chronologically sequences events and flags unverified alibi intervals.
- ⚡ **Cross-Source Contradiction Spotter**: Detects conflicting statements and discrepancies across records.
- 🍃 **Secure Case Vault**: Enterprise-grade storage for case dossiers.`,
  },
  {
    id: "landing_use_cases",
    title: "Public Use Cases & Applications",
    keywords: ["use cases", "who uses this", "applications", "target audience", "police", "law enforcement", "lawyers", "journalists", "fraud"],
    answer: `SatyaSutra is designed for four major public domains:

- 🚓 **Law Enforcement**: Consolidating FIRs, surveillance logs, and statements to speed up investigation reviews.
- ⚖️ **Legal Counsel**: Pinpointing contradictions in witness testimonies and verifying timeline alibis.
- 📰 **Investigative Journalism**: Connecting leaks, corporate registries, and public interest records.
- 💼 **Corporate Forensics & Compliance**: Evaluating internal audits, whistleblower claims, and AML reviews.`,
  },
  {
    id: "landing_ethics",
    title: "Ethical Constraints & Guardrails",
    keywords: ["ethics", "guardrails", "guilt score", "criminal probability", "human in the loop", "constraints"],
    answer: `SatyaSutra strictly enforces **Three Ethical Principles**:

1. 🚫 **No Guilt Scoring**: The platform NEVER calculates a guilt percentage or criminal probability score.
2. 🤝 **Human-in-the-Loop Confirmation**: Every AI-suggested link requires human investigator verification.
3. ⚖️ **Investigator-Review Draft Only**: All generated summaries are labeled strictly as review drafts, not court verdicts.`,
  },
  {
    id: "landing_team",
    title: "Creators & Affiliation",
    keywords: ["who created", "who made", "creators", "team", "college", "pes", "pune", "mcoe"],
    answer: `**SatyaSutra** was created by **Team SatyaSutra** from **PES's Modern College of Engineering, Pune**.

- **Team**: Team SatyaSutra (Pune, India)
- **Institution**: Progressive Education Society's Modern College of Engineering (MCOE)
- **Mission**: Providing transparent, explainable forensic intelligence for justice.`,
  },
  {
    id: "landing_portal",
    title: "Portal Access",
    keywords: ["how to login", "where to login", "sign in", "portal", "access portal"],
    answer: `Authorized investigators can sign in at the [Portal Sign In Page](/login).

Please use your officially issued departmental credentials to access the workspace. For account setup or password assistance, please contact your system administrator.`,
  },
];

export const PUBLIC_SUGGESTIONS = [
  "What is SatyaSutra?",
  "How does the 4-stage pipeline work?",
  "What are the core capabilities on the landing page?",
  "Who are the target users and use cases?",
  "What ethical guidelines does SatyaSutra follow?",
  "Who created SatyaSutra?",
];

export function queryClientKnowledge(userQuery) {
  const query = (userQuery || "").toLowerCase().trim();
  if (!query) {
    return {
      answer: "Hello! I am the SatyaSutra Public Assistant. I can answer basic operational questions about our platform and capabilities as outlined on the landing page.",
      sources: ["Landing Page Guide"],
      suggestedFollowups: PUBLIC_SUGGESTIONS.slice(0, 3),
    };
  }

  // 1. Security Shield: Credentials
  if (CREDENTIAL_REGEX.test(query)) {
    return {
      answer: `🔒 **I am sorry, but for security and privacy reasons, I cannot disclose login credentials, passwords, or authentication keys.**

If you are an authorized investigator, please sign in at the [Portal Sign In Page](/login) using your departmentally issued credentials. If you require access, please contact your system administrator.`,
      sources: ["Security Policy"],
      suggestedFollowups: PUBLIC_SUGGESTIONS.slice(0, 3),
    };
  }

  // 2. Security Shield: Tech stack
  if (TECH_STACK_REGEX.test(query)) {
    return {
      answer: `🛡️ **I am sorry, but to ensure platform security and protect investigative systems from external risks, internal technical stack details, database architectures, and server configurations are confidential and cannot be disclosed.**

SatyaSutra is an AI-assisted forensic intelligence platform designed to connect fragmented evidence into auditable case dossiers as described on our landing page.`,
      sources: ["Platform Security Policy"],
      suggestedFollowups: PUBLIC_SUGGESTIONS.slice(0, 3),
    };
  }

  // 3. Security Shield: Internal or Detective Operations
  if (INTERNAL_OP_REGEX.test(query)) {
    return {
      answer: `⚠️ **I am sorry, but I can only answer general questions based on public landing page information.**

Internal detective operations, active investigation files, uploaded evidence records, and case dossiers are strictly confidential. They are restricted exclusively to authorized personnel within the authenticated forensic workspace after secure login.`,
      sources: ["Confidentiality Policy"],
      suggestedFollowups: PUBLIC_SUGGESTIONS.slice(0, 3),
    };
  }

  // 4. Greetings
  if (["hi", "hello", "hey", "namaste", "good morning"].some(g => query === g || query.startsWith(g + " "))) {
    return {
      answer: `👋 **Hello! Welcome to the SatyaSutra Platform Guide.**

I can provide basic operational answers based on our public landing page data, including:
- *What is SatyaSutra?*
- *The 4-Stage Investigation Pipeline*
- *Core capabilities and public use cases*
- *Ethical guardrails and project information*

How can I help you today?`,
      sources: ["Landing Page Guide"],
      suggestedFollowups: PUBLIC_SUGGESTIONS.slice(0, 3),
    };
  }

  // 5. Landing knowledge matching
  let bestItem = null;
  let bestScore = 0;

  for (const item of PUBLIC_KNOWLEDGE) {
    let score = 0;
    for (const kw of item.keywords) {
      if (query.includes(kw)) score += 10;
      else if (kw.includes(query)) score += 5;
    }
    if (score > bestScore) {
      bestScore = score;
      bestItem = item;
    }
  }

  if (bestItem && bestScore >= 4) {
    const followups = PUBLIC_KNOWLEDGE.filter(k => k.id !== bestItem.id).slice(0, 3).map(k => k.title);
    return {
      answer: bestItem.answer,
      sources: [bestItem.title],
      suggestedFollowups: followups,
    };
  }

  return {
    answer: `I can only provide general, public information based on the SatyaSutra landing page.

- **Overview**: Learn what SatyaSutra is and its mission.
- **Pipeline**: Understand the 4-stage intelligence pipeline.
- **Capabilities**: Explore the 6 core platform capabilities.
- **Use Cases**: Discover who uses SatyaSutra.
- **Ethics**: Learn about our zero-guilt-score and human-in-the-loop policies.

Please choose a topic above or ask a general question about our landing page.`,
    sources: ["Landing Page Directory"],
    suggestedFollowups: PUBLIC_SUGGESTIONS.slice(0, 3),
  };
}
