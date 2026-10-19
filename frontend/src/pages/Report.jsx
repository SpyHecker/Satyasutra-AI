import { useState, useEffect } from 'react';
import { marked } from 'marked';
import api from '../api/client';

export default function Report() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('preview');

  useEffect(() => {
    loadReport();
  }, []);

  const loadReport = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.analysis.report();
      setReport(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleExportMarkdown = () => {
    if (!report?.markdown) return;
    const blob = new Blob([report.markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `satyasutra_report_${new Date().toISOString().split('T')[0]}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="stub-page anim-fade">
        <div className="stub-icon" style={{ animation: 'pulse 1.5s ease infinite' }}>📄</div>
        <h1>Generating Report...</h1>
        <p className="stub-desc">Aggregating evidence analysis into a comprehensive case report</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="stub-page anim-fade">
        <div className="stub-icon">⚠️</div>
        <h1>Could Not Generate Report</h1>
        <p className="stub-desc">{error}</p>
        <button className="btn btn-primary" onClick={loadReport}>🔄 Retry</button>
      </div>
    );
  }

  if (!report || !report.markdown) {
    return (
      <div className="stub-page anim-fade">
        <div className="stub-icon">📄</div>
        <h1>Case Report</h1>
        <p className="stub-desc">
          No evidence to analyze. Upload evidence files to generate a case report.
        </p>
        <a href="/evidence" className="btn btn-primary">📁 Upload Evidence</a>
      </div>
    );
  }

  const renderedHtml = marked(report.markdown, {
    gfm: true,
    breaks: true,
  });

  return (
    <div className="anim-fade">
      <div className="page-header">
        <h1>📄 Case Report</h1>
        <p>
          Auto-generated investigator-review draft with inline evidence citations.
          Generated at {report.generated_at}.
        </p>
      </div>

      {/* Report Stats */}
      <div className="report-stats-bar">
        <div className="report-stat">
          <span className="report-stat-value">{report.stats?.evidence_count ?? 0}</span>
          <span className="report-stat-label">Evidence</span>
        </div>
        <div className="report-stat">
          <span className="report-stat-value">{report.stats?.entity_count ?? 0}</span>
          <span className="report-stat-label">Entities</span>
        </div>
        <div className="report-stat">
          <span className="report-stat-value">{report.stats?.timeline_events ?? 0}</span>
          <span className="report-stat-label">Timeline Events</span>
        </div>
        <div className="report-stat">
          <span className="report-stat-value" style={{
            color: (report.stats?.contradictions ?? 0) > 0 ? 'var(--danger)' : 'var(--success)'
          }}>
            {report.stats?.contradictions ?? 0}
          </span>
          <span className="report-stat-label">Contradictions</span>
        </div>
        <div className="report-stat">
          <span className="report-stat-value" style={{
            color: (report.stats?.timeline_gaps ?? 0) > 0 ? 'var(--warning)' : 'var(--success)'
          }}>
            {report.stats?.timeline_gaps ?? 0}
          </span>
          <span className="report-stat-label">Time Gaps</span>
        </div>
      </div>

      {/* Tab Controls */}
      <div className="report-tabs">
        <button
          className={`report-tab ${activeTab === 'preview' ? 'active' : ''}`}
          onClick={() => setActiveTab('preview')}
        >
          📖 Preview
        </button>
        <button
          className={`report-tab ${activeTab === 'markdown' ? 'active' : ''}`}
          onClick={() => setActiveTab('markdown')}
        >
          ✏️ Markdown
        </button>
        <div className="report-tab-spacer" />
        <button className="btn btn-ghost btn-sm" onClick={handleExportMarkdown}>
          💾 Export .md
        </button>
        <button className="btn btn-ghost btn-sm" onClick={handlePrint}>
          🖨️ Print
        </button>
        <button className="btn btn-primary btn-sm" onClick={loadReport}>
          🔄 Regenerate
        </button>
      </div>

      {/* Report Content */}
      {activeTab === 'preview' ? (
        <div className="report-content report-preview">
          <div
            className="markdown-body"
            dangerouslySetInnerHTML={{ __html: renderedHtml }}
          />
        </div>
      ) : (
        <div className="report-content">
          <pre className="report-markdown-source">{report.markdown}</pre>
        </div>
      )}
    </div>
  );
}
