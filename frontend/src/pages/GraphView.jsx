const planned = [
  'Force-directed graph layout (react-force-graph)',
  'Click any edge to see its source evidence',
  'Filter nodes by entity type (Person, Location, Event, Object)',
  'Highlight contradictions with red edges',
  'Search and zoom to specific nodes',
  'Export graph as image or JSON',
];

export default function GraphView() {
  return (
    <div className="stub-page anim-fade">
      <div className="stub-icon">🕸️</div>
      <h1>Knowledge Graph</h1>
      <p className="stub-desc">
        Interactive visualization of entities and their relationships extracted from case evidence.
        Every edge is traceable to its source document.
      </p>
      <span className="badge badge-warning">Coming in Week 3–4</span>

      <div className="feature-list">
        {planned.map((item) => (
          <div className="feature-list-item" key={item}>
            <span className="dot">→</span>
            <span>{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
