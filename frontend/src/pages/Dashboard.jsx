import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import api from '../api/client';
import { useAuth } from '../context/useAuth';

const features = [
  {
    icon: '🔍',
    title: 'Evidence Analysis',
    desc: 'OCR + NLP pipeline extracts people, places, times, and objects from documents and images.',
    scope: 'MVP',
    to: '/evidence',
  },
  {
    icon: '🕸️',
    title: 'Knowledge Graph',
    desc: 'Auto-linked entity graph where every edge is traceable back to its source evidence.',
    scope: 'MVP',
    to: '/graph',
  },
  {
    icon: '⏱️',
    title: 'Timeline Reconstruction',
    desc: 'Chronological event ordering with automatic gap detection and flagging.',
    scope: 'MVP',
    to: '/timeline',
  },
  {
    icon: '⚡',
    title: 'Contradiction Detection',
    desc: 'Automatically flags conflicting facts discovered across multiple evidence sources.',
    scope: 'MVP',
    to: '/graph',
  },
  {
    icon: '📋',
    title: 'Report Generator',
    desc: 'Draft case report with inline evidence-ID citations for every single claim.',
    scope: 'MVP',
    to: '/report',
  },
  {
    icon: '💬',
    title: 'Case Q&A Chatbot',
    desc: 'RAG-powered question answering directly over the case knowledge graph.',
    scope: 'Stretch',
    to: '#',
  },
];

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [backendOnline, setBackendOnline] = useState(null);

  useEffect(() => {
    // Check backend health
    api.health()
      .then(() => setBackendOnline(true))
      .catch(() => setBackendOnline(false));

    // Fetch stats
    api.analysis.stats()
      .then((data) => setStats(data))
      .catch(() => setStats(null));
  }, []);

  const liveStats = [
    {
      value: stats?.evidence_count ?? 0,
      label: 'Evidence Files',
      color: stats?.evidence_count > 0 ? 'var(--accent-light)' : 'var(--text-muted)',
    },
    {
      value: stats?.total_entities ?? 0,
      label: 'Extracted Entities',
      color: stats?.total_entities > 0 ? 'var(--success)' : 'var(--text-muted)',
    },
    {
      value: stats?.contradiction_count ?? 0,
      label: 'Contradictions',
      color: stats?.contradiction_count > 0 ? 'var(--danger)' : 'var(--text-muted)',
    },
    {
      value: backendOnline === true ? '● Online' : backendOnline === false ? '○ Offline' : '…',
      label: 'System Status',
      color: backendOnline ? 'var(--success)' : 'var(--danger)',
    },
  ];

  const isBlankCase = stats && stats.evidence_count === 0;

  return (
    <div className="anim-fade">
      {/* Hero */}
      <section className="hero" id="dashboard-hero">
        <div className="hero-badge anim-fade-up">
          🛡️ Case Clearance Level: {user?.role || 'Lead Investigator'}
        </div>

        <h1 className="anim-fade-up delay-1">
          Welcome, <span className="accent">{user?.full_name || 'Investigator'}</span>
        </h1>

        <p className="hero-desc anim-fade-up delay-2">
          {isBlankCase
            ? 'Your personal case vault is ready and waiting for initial evidence intake.'
            : 'Active multi-source investigation workspace with linked graph, timeline, and audit-ready reporting.'}
        </p>

        <div className="hero-actions anim-fade-up delay-3">
          <Link to="/evidence" className="btn btn-primary">
            📁 Ingest Evidence
          </Link>
          <Link to="/graph" className="btn btn-ghost">
            🕸️ View Graph
          </Link>
        </div>

        {/* Live Stats */}
        <div className="stats-bar anim-fade-up delay-4">
          {liveStats.map((s) => (
            <div className="stat-item" key={s.label}>
              <span className="stat-value" style={{ color: s.color }}>{s.value}</span>
              <span className="stat-label">{s.label}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Blank Workspace Welcome Card for New Users */}
      {isBlankCase && (
        <section className="blank-workspace-card anim-fade-up delay-4">
          <div className="blank-card-glow"></div>
          <div className="blank-card-icon">🗂️</div>
          <div className="blank-card-body">
            <h3>Fresh Case Workspace Initialized</h3>
            <p>
              All evidence vaults, entity graphs, and timeline sequences are blank for your new account.
              Begin by uploading police FIRs, witness testimonies, or CCTV stills to start automatic OCR
              and entity linkage.
            </p>
            <div className="blank-card-actions">
              <Link to="/evidence" className="btn btn-primary">
                Upload Your First Evidence Document →
              </Link>
            </div>
          </div>
        </section>
      )}

      {/* Feature Grid */}
      <section id="features-section" style={{ marginTop: 'var(--sp-12)' }}>
        <h2 style={{ textAlign: 'center', marginBottom: 'var(--sp-8)', fontSize: 'var(--text-2xl)' }}
            className="anim-fade-up delay-4"
        >
          Forensic Investigation Modules
        </h2>
        <div className="grid grid-3">
          {features.map((f, i) => (
            <Link to={f.to} className="card card-link anim-fade-up" key={f.title}
                  style={{ animationDelay: `${0.07 * (i + 5)}s`, opacity: 0 }}
            >
              <div className="card-icon">{f.icon}</div>
              <h3 className="card-title">{f.title}</h3>
              <p className="card-desc">{f.desc}</p>
              <span className={`badge ${f.scope === 'MVP' ? 'badge-success' : 'badge-warning'}`}>
                {f.scope}
              </span>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
