import { Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import api from '../api/client';

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
      value: stats?.evidence_count ?? '—',
      label: 'Evidence',
      color: stats?.evidence_count > 0 ? 'var(--accent-light)' : 'var(--text-muted)',
    },
    {
      value: stats?.total_entities ?? '—',
      label: 'Entities',
      color: stats?.total_entities > 0 ? 'var(--success)' : 'var(--text-muted)',
    },
    {
      value: stats?.contradiction_count ?? '—',
      label: 'Contradictions',
      color: stats?.contradiction_count > 0 ? 'var(--danger)' : 'var(--text-muted)',
    },
    {
      value: backendOnline === true ? '●' : backendOnline === false ? '○' : '…',
      label: 'Backend',
      color: backendOnline ? 'var(--success)' : 'var(--danger)',
    },
  ];

  return (
    <div className="anim-fade">
      {/* Hero */}
      <section className="hero" id="dashboard-hero">
        <div className="hero-badge anim-fade-up">
          🚀 AI-Powered Investigation
        </div>

        <h1 className="anim-fade-up delay-1">
          Connect the <span className="accent">Evidence</span>
        </h1>

        <p className="hero-desc anim-fade-up delay-2">
          Turn fragmented documents, images, and statements into one auditable case view —
          knowledge graph, timeline, and source-cited report.
        </p>

        <div className="hero-actions anim-fade-up delay-3">
          <Link to="/evidence" className="btn btn-primary">
            📁 Upload Evidence
          </Link>
          <Link to="/graph" className="btn btn-ghost">
            🔗 View Graph
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

      {/* Feature Grid */}
      <section id="features-section" style={{ marginTop: 'var(--sp-12)' }}>
        <h2 style={{ textAlign: 'center', marginBottom: 'var(--sp-8)', fontSize: 'var(--text-2xl)' }}
            className="anim-fade-up delay-4"
        >
          Core Capabilities
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
