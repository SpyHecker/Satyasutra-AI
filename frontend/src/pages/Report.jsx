const planned = [
  'Markdown-rendered case report',
  'Inline [Evidence-ID] citations for every claim',
  'Sections: Summary, Timeline, Contradictions, Graph',
  'Export as PDF or Markdown',
  'All reports labeled "investigator-review draft"',
  'Aggregates graph, timeline, and contradiction data',
];

export default function Report() {
  return (
    <div className="stub-page anim-fade">
      <div className="stub-icon">📄</div>
      <h1>Case Report</h1>
      <p className="stub-desc">
        Auto-generated draft investigation report with inline evidence-ID citations.
        Every claim links back to its source document.
      </p>
      <span className="badge badge-warning">Coming in Week 7</span>

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
