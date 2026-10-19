import { useState, useEffect } from 'react';
import api from '../api/client';

const SOURCE_COLORS = [
  '#6366f1', '#22c55e', '#eab308', '#f97316', '#3b82f6',
  '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899', '#64748b',
];

export default function Timeline() {
  const [timelineData, setTimelineData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterSource, setFilterSource] = useState('all');

  useEffect(() => {
    loadTimeline();
  }, []);

  const loadTimeline = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.analysis.timeline();
      setTimelineData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="stub-page anim-fade">
        <div className="stub-icon" style={{ animation: 'pulse 1.5s ease infinite' }}>📅</div>
        <h1>Loading Timeline...</h1>
        <p className="stub-desc">Reconstructing chronological events from evidence</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="stub-page anim-fade">
        <div className="stub-icon">⚠️</div>
        <h1>Could Not Load Timeline</h1>
        <p className="stub-desc">{error}</p>
        <button className="btn btn-primary" onClick={loadTimeline}>🔄 Retry</button>
      </div>
    );
  }

  const events = timelineData?.events || [];
  const gaps = timelineData?.gaps || [];

  if (events.length === 0) {
    return (
      <div className="stub-page anim-fade">
        <div className="stub-icon">📅</div>
        <h1>Timeline Reconstruction</h1>
        <p className="stub-desc">
          No temporal events extracted yet. Upload evidence files with date/time references
          to build the timeline.
        </p>
        <a href="/evidence" className="btn btn-primary">📁 Upload Evidence</a>
      </div>
    );
  }

  // Build source color map
  const sourceNames = [...new Set(events.map((e) => e.source_name))];
  const sourceColorMap = {};
  sourceNames.forEach((name, i) => {
    sourceColorMap[name] = SOURCE_COLORS[i % SOURCE_COLORS.length];
  });

  // Filter events
  const filteredEvents = filterSource === 'all'
    ? events
    : events.filter((e) => e.source_name === filterSource);

  // Build a combined list of events + gaps sorted by time
  const timelineItems = [];
  let gapIdx = 0;

  for (const evt of filteredEvents) {
    // Insert any gaps that come before this event
    while (gapIdx < gaps.length && gaps[gapIdx].end <= evt.timestamp) {
      timelineItems.push({ type: 'gap', data: gaps[gapIdx] });
      gapIdx++;
    }
    timelineItems.push({ type: 'event', data: evt });
  }
  // Remaining gaps
  while (gapIdx < gaps.length) {
    timelineItems.push({ type: 'gap', data: gaps[gapIdx] });
    gapIdx++;
  }

  return (
    <div className="anim-fade">
      <div className="page-header">
        <h1>📅 Timeline Reconstruction</h1>
        <p>
          Chronological view of events extracted from evidence.
          Gaps exceeding 6 hours are flagged in red.
        </p>
      </div>

      {/* Stats */}
      <div className="timeline-stats">
        <div className="stat-item">
          <span className="stat-value">{events.length}</span>
          <span className="stat-label">Events</span>
        </div>
        <div className="stat-item">
          <span className="stat-value" style={{ color: gaps.length > 0 ? 'var(--danger)' : 'var(--success)' }}>
            {gaps.length}
          </span>
          <span className="stat-label">Gaps Found</span>
        </div>
        <div className="stat-item">
          <span className="stat-value">{sourceNames.length}</span>
          <span className="stat-label">Sources</span>
        </div>
      </div>

      {/* Filters */}
      <div className="graph-controls" style={{ marginTop: 'var(--sp-4)' }}>
        <div className="graph-control-group">
          <label className="control-label">Filter by Source</label>
          <select
            className="control-select"
            value={filterSource}
            onChange={(e) => setFilterSource(e.target.value)}
          >
            <option value="all">All Sources</option>
            {sourceNames.map((name) => (
              <option key={name} value={name}>{name}</option>
            ))}
          </select>
        </div>
        <div className="graph-control-group">
          <div className="source-legend">
            {sourceNames.map((name) => (
              <span
                key={name}
                className="legend-item"
                onClick={() => setFilterSource(name === filterSource ? 'all' : name)}
                style={{ cursor: 'pointer' }}
              >
                <span className="legend-dot" style={{ background: sourceColorMap[name] }} />
                {name}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="timeline-container">
        <div className="timeline-line" />

        {timelineItems.map((item, i) => {
          if (item.type === 'gap') {
            const gap = item.data;
            return (
              <div key={`gap-${i}`} className="timeline-gap anim-fade-up" style={{ animationDelay: `${i * 0.03}s` }}>
                <div className="timeline-gap-marker">⚠️</div>
                <div className="timeline-gap-content">
                  <span className="badge badge-danger">GAP: {gap.duration_hours}h</span>
                  <p>{gap.description}</p>
                  <div className="timeline-gap-range">
                    <span>{formatTimestamp(gap.start)}</span>
                    <span className="timeline-gap-arrow">→</span>
                    <span>{formatTimestamp(gap.end)}</span>
                  </div>
                </div>
              </div>
            );
          }

          const evt = item.data;
          const color = sourceColorMap[evt.source_name] || '#64748b';
          const isLeft = i % 2 === 0;

          return (
            <div
              key={`evt-${i}`}
              className={`timeline-event ${isLeft ? 'left' : 'right'} anim-fade-up`}
              style={{ animationDelay: `${i * 0.03}s` }}
            >
              <div className="timeline-dot" style={{ background: color, boxShadow: `0 0 12px ${color}44` }} />
              <div className="timeline-event-card">
                <div className="timeline-event-time">
                  {formatTimestamp(evt.timestamp)}
                  {evt.is_approximate && <span className="badge badge-warning" style={{ marginLeft: 8, fontSize: '0.65rem' }}>≈ APPROX</span>}
                </div>
                <p className="timeline-event-desc">{evt.description}</p>
                <div className="timeline-event-source">
                  <span className="legend-dot" style={{ background: color }} />
                  <span>{evt.source_name}</span>
                  <code style={{ fontSize: 'var(--text-xs)', color: 'var(--text-muted)', marginLeft: 8 }}>
                    [{evt.source_id}]
                  </code>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function formatTimestamp(ts) {
  if (!ts) return '—';
  try {
    const d = new Date(ts);
    return d.toLocaleString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    });
  } catch {
    return ts;
  }
}
