import { useState, useEffect, useRef, useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import api from '../api/client';

const CATEGORY_COLORS = {
  Person: '#6366f1',
  Location: '#22c55e',
  Time: '#eab308',
  Object: '#f97316',
  Organization: '#3b82f6',
  Event: '#ef4444',
  Legal: '#8b5cf6',
  Quantity: '#06b6d4',
  Language: '#ec4899',
  Other: '#64748b',
};

export default function GraphView() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [stats, setStats] = useState(null);
  const [contradictions, setContradictions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [filterCategory, setFilterCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showContradictions, setShowContradictions] = useState(true);
  const graphRef = useRef();
  const containerRef = useRef();
  const [dimensions, setDimensions] = useState({ width: 800, height: 500 });

  useEffect(() => {
    loadGraph();
    loadContradictions();
  }, []);

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.offsetWidth,
          height: Math.max(500, window.innerHeight - 380),
        });
      }
    };
    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  const loadGraph = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.analysis.graph();
      setGraphData({
        nodes: data.nodes || [],
        links: data.links || [],
      });
      setStats(data.stats || null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadContradictions = async () => {
    try {
      const data = await api.analysis.contradictions();
      setContradictions(data.contradictions || []);
    } catch {
      // Silently fail — contradictions are supplementary
    }
  };

  // Filter nodes
  const filteredData = useCallback(() => {
    let nodes = graphData.nodes;
    let links = graphData.links;

    if (filterCategory !== 'all') {
      const filteredNodeIds = new Set(
        nodes.filter((n) => n.category === filterCategory).map((n) => n.id)
      );
      nodes = nodes.filter((n) => filteredNodeIds.has(n.id));
      links = links.filter(
        (l) => filteredNodeIds.has(l.source?.id || l.source) && filteredNodeIds.has(l.target?.id || l.target)
      );
    }

    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      const matchedIds = new Set(
        nodes.filter((n) => n.label?.toLowerCase().includes(term)).map((n) => n.id)
      );
      nodes = nodes.filter((n) => matchedIds.has(n.id));
      links = links.filter(
        (l) => matchedIds.has(l.source?.id || l.source) && matchedIds.has(l.target?.id || l.target)
      );
    }

    return { nodes, links };
  }, [graphData, filterCategory, searchTerm]);

  const categories = [...new Set(graphData.nodes.map((n) => n.category))].sort();

  const handleNodeClick = useCallback((node) => {
    setSelectedNode(node);
    // Zoom to node
    if (graphRef.current) {
      graphRef.current.centerAt(node.x, node.y, 600);
      graphRef.current.zoom(3, 600);
    }
  }, []);

  const nodeCanvasObject = useCallback((node, ctx, globalScale) => {
    const label = node.label || '';
    const fontSize = Math.max(10 / globalScale, 3);
    const nodeRadius = Math.max(node.val || 4, 3);
    const color = node.color || CATEGORY_COLORS.Other;

    // Node glow
    ctx.beginPath();
    ctx.arc(node.x, node.y, nodeRadius + 2, 0, 2 * Math.PI);
    ctx.fillStyle = color + '33';
    ctx.fill();

    // Node circle
    ctx.beginPath();
    ctx.arc(node.x, node.y, nodeRadius, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.fill();

    // Border
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 0.5;
    ctx.stroke();

    // Label
    if (globalScale > 0.8) {
      ctx.font = `${fontSize}px Inter, sans-serif`;
      ctx.fillStyle = '#e8ecf4';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      ctx.fillText(label, node.x, node.y + nodeRadius + 2);
    }
  }, []);

  const linkCanvasObject = useCallback((link, ctx) => {
    const start = link.source;
    const end = link.target;
    if (!start || !end || typeof start.x === 'undefined') return;

    ctx.beginPath();
    ctx.moveTo(start.x, start.y);
    ctx.lineTo(end.x, end.y);
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
    ctx.lineWidth = Math.max(0.5, (link.weight || 1) * 0.5);
    ctx.stroke();
  }, []);

  if (loading) {
    return (
      <div className="stub-page anim-fade">
        <div className="stub-icon" style={{ animation: 'pulse 1.5s ease infinite' }}>🕸️</div>
        <h1>Loading Knowledge Graph...</h1>
        <p className="stub-desc">Building connections from evidence entities</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="stub-page anim-fade">
        <div className="stub-icon">⚠️</div>
        <h1>Could Not Load Graph</h1>
        <p className="stub-desc">{error}</p>
        <button className="btn btn-primary" onClick={loadGraph}>🔄 Retry</button>
      </div>
    );
  }

  if (graphData.nodes.length === 0) {
    return (
      <div className="stub-page anim-fade">
        <div className="stub-icon">🕸️</div>
        <h1>Knowledge Graph</h1>
        <p className="stub-desc">
          No evidence has been processed yet. Upload evidence files to build the knowledge graph.
        </p>
        <a href="/evidence" className="btn btn-primary">📁 Upload Evidence</a>
      </div>
    );
  }

  const filtered = filteredData();

  return (
    <div className="anim-fade">
      <div className="page-header">
        <h1>🕸️ Knowledge Graph</h1>
        <p>
          Interactive visualization of entities and their relationships. Click nodes for details.
          Every edge is traceable to its source evidence.
        </p>
      </div>

      {/* Controls */}
      <div className="graph-controls">
        <div className="graph-control-group">
          <label className="control-label">Filter by Category</label>
          <select
            className="control-select"
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
          >
            <option value="all">All Categories</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>
        <div className="graph-control-group">
          <label className="control-label">Search Entities</label>
          <input
            className="control-input"
            type="text"
            placeholder="Search nodes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="graph-control-group">
          <button className="btn btn-ghost btn-sm" onClick={() => graphRef.current?.zoomToFit(400)}>
            🔍 Fit View
          </button>
        </div>
      </div>

      {/* Stats Bar */}
      {stats && (
        <div className="graph-stats-bar">
          <span className="graph-stat">
            <strong>{stats.total_nodes}</strong> Nodes
          </span>
          <span className="graph-stat">
            <strong>{stats.total_edges}</strong> Edges
          </span>
          {Object.entries(stats.categories || {}).map(([cat, count]) => (
            <span key={cat} className="graph-stat" style={{ color: CATEGORY_COLORS[cat] || CATEGORY_COLORS.Other }}>
              <span className="entity-chip-dot" style={{ background: CATEGORY_COLORS[cat] || CATEGORY_COLORS.Other, display: 'inline-block', width: 8, height: 8, borderRadius: '50%', marginRight: 4 }} />
              {cat}: {count}
            </span>
          ))}
        </div>
      )}

      {/* Graph Canvas */}
      <div className="graph-container" ref={containerRef}>
        <ForceGraph2D
          ref={graphRef}
          graphData={filtered}
          width={dimensions.width}
          height={dimensions.height}
          backgroundColor="#06080f"
          nodeCanvasObject={nodeCanvasObject}
          linkCanvasObjectMode={() => 'replace'}
          linkCanvasObject={linkCanvasObject}
          onNodeClick={handleNodeClick}
          nodePointerAreaPaint={(node, color, ctx) => {
            const r = node.val || 4;
            ctx.beginPath();
            ctx.arc(node.x, node.y, r + 3, 0, 2 * Math.PI);
            ctx.fillStyle = color;
            ctx.fill();
          }}
          cooldownTicks={80}
          d3AlphaDecay={0.02}
          d3VelocityDecay={0.3}
        />
      </div>

      {/* Selected Node Detail */}
      {selectedNode && (
        <div className="result-card anim-slide-down" style={{ marginTop: 'var(--sp-4)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3>
              <span className="entity-chip-dot" style={{ background: selectedNode.color, display: 'inline-block', width: 12, height: 12, borderRadius: '50%', marginRight: 8 }} />
              {selectedNode.label}
            </h3>
            <button className="btn-sm btn-ghost" onClick={() => setSelectedNode(null)}>✕</button>
          </div>
          <div className="result-field">
            <span className="result-label">Category</span>
            <span className="badge badge-info">{selectedNode.category}</span>
          </div>
          <div className="result-field">
            <span className="result-label">NER Label</span>
            <span className="result-value">{selectedNode.ner_label}</span>
          </div>
          <div className="result-field">
            <span className="result-label">Mentions</span>
            <span className="result-value">{selectedNode.mention_count}×</span>
          </div>
          <div className="result-field">
            <span className="result-label">Sources</span>
            <span className="result-value">
              {selectedNode.sources?.length > 0
                ? selectedNode.sources.map((s) => `[${s}]`).join(', ')
                : 'N/A'}
            </span>
          </div>
        </div>
      )}

      {/* Contradictions Panel */}
      {contradictions.length > 0 && (
        <div style={{ marginTop: 'var(--sp-6)' }}>
          <button
            className="btn btn-ghost"
            onClick={() => setShowContradictions(!showContradictions)}
            style={{ marginBottom: 'var(--sp-3)' }}
          >
            ⚡ {contradictions.length} Contradiction{contradictions.length !== 1 ? 's' : ''} Detected
            {showContradictions ? ' ▼' : ' ▶'}
          </button>

          {showContradictions && (
            <div className="contradictions-list">
              {contradictions.map((c, i) => (
                <div key={i} className="contradiction-card anim-fade-up" style={{ animationDelay: `${i * 0.05}s` }}>
                  <div className="contradiction-header">
                    <span className={`badge ${c.severity === 'high' ? 'badge-danger' : 'badge-warning'}`}>
                      {c.severity}
                    </span>
                    <span className="contradiction-type">
                      {c.type?.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <p className="contradiction-explanation">{c.explanation}</p>
                  <div className="contradiction-sources">
                    <span className="format-tag">📄 {c.source_a_name}</span>
                    <span style={{ color: 'var(--text-muted)' }}>vs</span>
                    <span className="format-tag">📄 {c.source_b_name}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Legend */}
      <div className="graph-legend">
        <h4 style={{ marginBottom: 'var(--sp-3)', fontSize: 'var(--text-sm)', color: 'var(--text-muted)' }}>
          Entity Legend
        </h4>
        <div className="legend-items">
          {Object.entries(CATEGORY_COLORS).map(([cat, color]) => (
            <span key={cat} className="legend-item" onClick={() => setFilterCategory(cat === filterCategory ? 'all' : cat)}>
              <span className="legend-dot" style={{ background: color }} />
              {cat}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
