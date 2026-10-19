const planned = [
  'Vertical timeline with event cards',
  'Highlighted temporal gaps between events',
  'Click any event to see source evidence',
  'Filter timeline by person or location',
  'Zoom and pan across time ranges',
  'Color-coded events by entity type',
];

export default function Timeline() {
  return (
    <div className="stub-page anim-fade">
      <div className="stub-icon">📅</div>
      <h1>Timeline Reconstruction</h1>
      <p className="stub-desc">
        Chronological view of events extracted from evidence, with automatic gap detection
        and flagging of missing time periods.
      </p>
      <span className="badge badge-warning">Coming in Week 5</span>

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
