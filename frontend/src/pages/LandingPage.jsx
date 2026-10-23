import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/useAuth';

export default function LandingPage() {
  const { isAuthenticated, user, dbStatus } = useAuth();
  const [activeTab, setActiveTab] = useState('graph');

  return (
    <div className="landing-page" id="landing-container">
      {/* ============================================================
          HERO SECTION
          ============================================================ */}
      <section className="landing-hero" id="hero">
        <div className="hero-glow-sphere"></div>
        <div className="hero-glow-secondary"></div>

        <div className="hero-badge">
          <span className="pulse-indicator"></span>
          <span>SATYASUTRA 2.0 • AI-ASSISTED FORENSIC INTELLIGENCE</span>
        </div>

        <h1 className="hero-headline">
          Connect Fragmented Evidence Into <span className="text-gradient">Auditable Case Truth</span>
        </h1>

        <p className="hero-subhead">
          SatyaSutra bridges disconnected documents, crime-scene photographs, financial transactions,
          and witness statements into one unified investigation view: an interconnected knowledge graph,
          a chronological timeline with automated gap detection, and court-ready cited case reports.
        </p>

        {/* CTA Button Group */}
        <div className="hero-cta-group">
          {isAuthenticated ? (
            <Link to="/dashboard" className="btn btn-primary btn-hero-primary" id="cta-dashboard">
              🚀 Enter Investigation Workspace ({user?.full_name?.split(' ')[0] || 'Investigator'}) →
            </Link>
          ) : (
            <Link to="/login" className="btn btn-primary btn-hero-primary" id="cta-login">
              🔐 Sign In to Investigation Vault →
            </Link>
          )}
        </div>

        {/* Trust & Spec Ribbon */}
        <div className="hero-metrics-ribbon">
          <div className="metric-pill">
            <span className="metric-icon">🔒</span>
            <span className="metric-text"><strong>100%</strong> Evidence Traceable</span>
          </div>
          <div className="metric-pill">
            <span className="metric-icon">⚡</span>
            <span className="metric-text"><strong>Zero</strong> AI Hallucination with Inline Citations</span>
          </div>
          <div className="metric-pill">
            <span className="metric-icon">⏱️</span>
            <span className="metric-text"><strong>Automated</strong> Timeline Gap & Alibi Detection</span>
          </div>
          <div className="metric-pill">
            <span className="metric-icon">🍃</span>
            <span className="metric-text">
              <strong>MongoDB</strong> {dbStatus?.mongodb_connected ? 'Connected' : 'Ready'} Case Vault
            </span>
          </div>
        </div>

        {/* ============================================================
            HERO VISUAL SHOWCASE: INTERACTIVE CASE SIMULATION
            ============================================================ */}
        <div className="hero-preview-container">
          <div className="terminal-header">
            <div className="terminal-controls">
              <span className="ctrl-dot red"></span>
              <span className="ctrl-dot yellow"></span>
              <span className="ctrl-dot green"></span>
            </div>
            <div className="terminal-title">
              CASE DOSSIER #CR-2026-094 • STATE vs. VIKRAMADITYA & ASSOCIATES
            </div>
            <div className="terminal-status-badge">
              <span className="status-live-dot"></span>
              <span>AUDIT ACTIVE</span>
            </div>
          </div>

          {/* Interactive Simulation Nav Tabs */}
          <div className="interactive-tabs">
            <button
              onClick={() => setActiveTab('graph')}
              className={`interactive-tab-btn ${activeTab === 'graph' ? 'active' : ''}`}
            >
              🕸️ Knowledge Graph View
            </button>
            <button
              onClick={() => setActiveTab('timeline')}
              className={`interactive-tab-btn ${activeTab === 'timeline' ? 'active' : ''}`}
            >
              ⏱️ Timeline & Gap Flag
            </button>
            <button
              onClick={() => setActiveTab('contradictions')}
              className={`interactive-tab-btn ${activeTab === 'contradictions' ? 'active' : ''}`}
            >
              ⚡ Contradiction Alerts (2)
            </button>
            <button
              onClick={() => setActiveTab('report')}
              className={`interactive-tab-btn ${activeTab === 'report' ? 'active' : ''}`}
            >
              📄 Cited Case Report
            </button>
          </div>

          {/* Tab Content Display */}
          <div className="tab-stage">
            {activeTab === 'graph' && (
              <div className="showcase-graph-preview">
                <div className="mock-graph-nodes">
                  <div className="node-item node-person">
                    <span className="node-badge">PERSON</span>
                    <span className="node-label">Vikramaditya (Suspect)</span>
                  </div>
                  <div className="graph-edge edge-1">
                    <span className="edge-text">owns vehicle [EVD-01]</span>
                  </div>
                  <div className="node-item node-object">
                    <span className="node-badge">OBJECT</span>
                    <span className="node-label">Black SUV (DL-4C-9902)</span>
                  </div>
                  <div className="graph-edge edge-2">
                    <span className="edge-text">captured at [EVD-04]</span>
                  </div>
                  <div className="node-item node-location">
                    <span className="node-badge">LOCATION</span>
                    <span className="node-label">Harbor Warehouse 4B</span>
                  </div>
                  <div className="graph-edge edge-3">
                    <span className="edge-text">transacted with [EVD-07]</span>
                  </div>
                  <div className="node-item node-org">
                    <span className="node-badge">ORGANIZATION</span>
                    <span className="node-label">Apex Shell Logistics</span>
                  </div>
                </div>
                <div className="graph-hint">
                  <span>💡 Every graph edge links directly to source evidence with verified page & timestamp citations.</span>
                </div>
              </div>
            )}

            {activeTab === 'timeline' && (
              <div className="showcase-timeline-preview">
                <div className="timeline-sequence">
                  <div className="timeline-item">
                    <div className="time-badge">20:15 IST</div>
                    <div className="time-content">
                      <strong>Suspect Seen Leaving Office</strong>
                      <p>Access card swipe recorded at Headquarters Gate B. Verified against CCTV.</p>
                      <span className="evd-tag">[EVD-01]</span>
                    </div>
                  </div>

                  <div className="timeline-gap-alert">
                    <div className="gap-icon">⚠️</div>
                    <div className="gap-info">
                      <strong>DETECTED TIMELINE GAP: 2 HOURS 45 MINUTES</strong>
                      <span>Missing alibi or surveillance coverage between 21:15 IST and 00:00 IST.</span>
                    </div>
                  </div>

                  <div className="timeline-item">
                    <div className="time-badge">00:00 IST</div>
                    <div className="time-content">
                      <strong>ATM Withdrawal & Cell Tower Ping</strong>
                      <p>Credit card transaction at Sector 14 ATM; phone connected to cell tower ID #884.</p>
                      <span className="evd-tag">[EVD-05]</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'contradictions' && (
              <div className="showcase-contradictions-preview">
                <div className="contradiction-card">
                  <div className="contradiction-header">
                    <span className="conflict-badge">ALIBI DISCREPANCY</span>
                    <span className="confidence-pill">High Severity</span>
                  </div>
                  <div className="conflict-sources">
                    <div className="source-box">
                      <span className="source-label">Source 1: Witness Statement [EVD-02]</span>
                      <p>&quot;The suspect claimed he was having dinner at the Grand Hotel in South Bombay between 21:00 and 23:00.&quot;</p>
                    </div>
                    <div className="source-vs">VS</div>
                    <div className="source-box highlight-conflict">
                      <span className="source-label">Source 2: Tollway FASTag Log [EVD-06]</span>
                      <p>&quot;Black SUV DL-4C-9902 passed through Navi Mumbai Expressway Tollgate at 21:42.&quot;</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'report' && (
              <div className="showcase-report-preview">
                <div className="report-snippet">
                  <h3>INVESTIGATION SUMMARY: INCIDENT OF 14 OCTOBER</h3>
                  <p>
                    Initial inquiry reveals that the subject departed the headquarters premises at approximately 20:15 IST <span className="evd-citation">[EVD-01]</span> in a black SUV bearing registration DL-4C-9902. Contrary to initial claims of dining in South Bombay <span className="evd-citation">[EVD-02]</span>, electronic toll records confirm the vehicle traversed the Navi Mumbai Tollway at 21:42 IST <span className="evd-citation">[EVD-06]</span>. The 2h 45m unverified gap remains unaccounted for prior to the midnight transaction <span className="evd-citation">[EVD-05]</span>.
                  </p>
                  <div className="report-footer-tag">
                    <span>Generated by SatyaSutra • Cryptographic Hash: SHA256:d892ef...</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* ============================================================
          CORE CAPABILITIES GRID (6 PILLARS)
          ============================================================ */}
      <section className="landing-section" id="capabilities">
        <div className="section-header">
          <span className="section-tag">COMPREHENSIVE CAPABILITIES</span>
          <h2 className="section-title">Designed for Modern Forensic Workflows</h2>
          <p className="section-subtitle">
            An end-to-end investigative engine that turns raw, heterogeneous clues into auditable evidence.
          </p>
        </div>

        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon-wrapper">📄</div>
            <h3 className="feature-card-title">Multimodal Ingestion & OCR</h3>
            <p className="feature-card-desc">
              Process scanned FIRs, affidavits, bank statements, and CCTV frame screenshots using
              high-accuracy Tesseract OCR and PDF parsing.
            </p>
            <span className="feature-badge">PyMuPDF + Tesseract</span>
          </div>

          <div className="feature-card">
            <div className="feature-icon-wrapper">🧠</div>
            <h3 className="feature-card-title">NLP Entity Extraction</h3>
            <p className="feature-card-desc">
              Automatically identify Persons, Locations, Organizations, Time markers, and Objects
              from unstructured text using pre-trained neural language models.
            </p>
            <span className="feature-badge">spaCy Pipeline</span>
          </div>

          <div className="feature-card">
            <div className="feature-icon-wrapper">🕸️</div>
            <h3 className="feature-card-title">Interactive Knowledge Graph</h3>
            <p className="feature-card-desc">
              Connect entities across separate documents. Explore relationships visually in an interactive
              force-directed graph where every connection traces to source files.
            </p>
            <span className="feature-badge">NetworkX + ForceGraph</span>
          </div>

          <div className="feature-card">
            <div className="feature-icon-wrapper">⏱️</div>
            <h3 className="feature-card-title">Timeline Reconstruction & Gaps</h3>
            <p className="feature-card-desc">
              Chronologically sequence statements, surveillance pings, and events while automatically
              highlighting unverified time intervals and missing alibi periods.
            </p>
            <span className="feature-badge">Chronological Engine</span>
          </div>

          <div className="feature-card">
            <div className="feature-icon-wrapper">⚡</div>
            <h3 className="feature-card-title">Cross-Source Contradiction Spotter</h3>
            <p className="feature-card-desc">
              Detect discrepancies between witness statements, alibis, digital logs, and forensic reports
              to immediately surface conflicting testimony.
            </p>
            <span className="feature-badge">Contradiction Detector</span>
          </div>

          <div className="feature-card">
            <div className="feature-icon-wrapper">🍃</div>
            <h3 className="feature-card-title">MongoDB Unified Case Vault</h3>
            <p className="feature-card-desc">
              Enterprise-grade document storage connecting directly via MONGODB_URL with role-based investigator
              credentials and offline fallback security.
            </p>
            <span className="feature-badge">MongoDB + JWT Auth</span>
          </div>
        </div>
      </section>

      {/* ============================================================
          HOW IT WORKS PIPELINE
          ============================================================ */}
      <section className="landing-section pipeline-section" id="workflow">
        <div className="section-header">
          <span className="section-tag">INVESTIGATION PIPELINE</span>
          <h2 className="section-title">From Unstructured Data to Court-Ready Dossier</h2>
          <p className="section-subtitle">
            Follow the automated four-stage intelligence pipeline built into SatyaSutra.
          </p>
        </div>

        <div className="pipeline-steps">
          <div className="pipeline-step">
            <div className="step-number">01</div>
            <div className="step-content">
              <h4>Ingest & Transcribe</h4>
              <p>Upload PDFs, crime scene photos, typed affidavits, or plain text notes to the secure case store.</p>
            </div>
          </div>

          <div className="pipeline-divider"></div>

          <div className="pipeline-step">
            <div className="step-number">02</div>
            <div className="step-content">
              <h4>Extract & Cross-Reference</h4>
              <p>spaCy NLP identifies key suspects, locations, and timestamps, cross-linking entities across documents.</p>
            </div>
          </div>

          <div className="pipeline-divider"></div>

          <div className="pipeline-step">
            <div className="step-number">03</div>
            <div className="step-content">
              <h4>Audit Graph & Timeline</h4>
              <p>Investigate the auto-assembled network graph, audit flagged contradictions, and inspect timeline gaps.</p>
            </div>
          </div>

          <div className="pipeline-divider"></div>

          <div className="pipeline-step">
            <div className="step-number">04</div>
            <div className="step-content">
              <h4>Generate Traceable Dossier</h4>
              <p>Export a formatted case report with inline evidence citations, ready for courtroom presentation.</p>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================
          USE CASES
          ============================================================ */}
      <section className="landing-section" id="use-cases">
        <div className="section-header">
          <span className="section-tag">MISSION-CRITICAL APPLICATIONS</span>
          <h2 className="section-title">Built for High-Stakes Truth Finding</h2>
        </div>

        <div className="use-cases-grid">
          <div className="use-case-card">
            <div className="use-case-badge">LAW ENFORCEMENT</div>
            <h3>Police & Detective Agencies</h3>
            <p>
              Consolidate FIRs, CDR phone logs, CCTV capture timestamps, and interrogations into a single
              auditable case dossier that speeds up charge-sheet preparation.
            </p>
          </div>

          <div className="use-case-card">
            <div className="use-case-badge">LEGAL COUNSEL</div>
            <h3>Defense & Prosecution Attorneys</h3>
            <p>
              Instantly pinpoint contradictions in opposing witness statements and verify every piece of
              evidence against chronological time logs with zero hallucination.
            </p>
          </div>

          <div className="use-case-card">
            <div className="use-case-badge">JOURNALISM</div>
            <h3>Investigative Journalists</h3>
            <p>
              Process leaked documents, financial disclosures, and corporate registries to build linked
              money trails and verify complex public-interest investigations.
            </p>
          </div>

          <div className="use-case-card">
            <div className="use-case-badge">COMPLIANCE</div>
            <h3>Corporate Fraud & Forensics</h3>
            <p>
              Perform internal audits, whistle-blower report evaluations, and anti-money laundering (AML)
              investigations backed by complete chain-of-custody tracking.
            </p>
          </div>
        </div>
      </section>

      {/* ============================================================
          CALL TO ACTION (CTA)
          ============================================================ */}
      <section className="landing-cta-banner">
        <div className="cta-glow"></div>
        <div className="cta-content">
          <h2 className="cta-title">Ready to Accelerate Your Investigation?</h2>
          <p className="cta-desc">
            Experience the clarity of AI-assisted evidence linkage. Launch your case dossier in seconds.
          </p>
          <div className="cta-buttons">
            <Link to={isAuthenticated ? '/dashboard' : '/login'} className="btn btn-primary btn-cta">
              {isAuthenticated ? 'Open Investigation Dashboard →' : 'Sign In to Investigation Vault →'}
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
