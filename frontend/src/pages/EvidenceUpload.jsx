import { useState, useCallback, useEffect } from 'react';
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

export default function EvidenceUpload() {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [evidenceList, setEvidenceList] = useState([]);
  const [selectedEvidence, setSelectedEvidence] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  // Load evidence list on mount
  useEffect(() => {
    loadEvidenceList();
  }, []);

  const loadEvidenceList = async () => {
    try {
      const data = await api.evidence.list();
      setEvidenceList(data.evidence || []);
    } catch {
      // Backend might not be running
    }
  };

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  }, []);

  const handleUpload = useCallback(async (file) => {
    setUploading(true);
    setError(null);
    setResult(null);
    setSelectedEvidence(null);
    try {
      const response = await api.evidence.upload(file);
      setResult(response);
      loadEvidenceList(); // Refresh list
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) handleUpload(e.dataTransfer.files[0]);
  }, [handleUpload]);

  const handleFileInput = useCallback((e) => {
    if (e.target.files?.[0]) handleUpload(e.target.files[0]);
  }, [handleUpload]);

  const handleViewDetail = async (id) => {
    setLoadingDetail(true);
    setSelectedEvidence(null);
    try {
      const detail = await api.evidence.get(id);
      setSelectedEvidence(detail);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingDetail(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.evidence.delete(id);
      setSelectedEvidence(null);
      setResult(null);
      loadEvidenceList();
    } catch (err) {
      setError(err.message);
    }
  };

  const formats = ['PDF', 'PNG', 'JPG', 'TIFF', 'TXT', 'BMP'];

  return (
    <div className="anim-fade">
      <div className="page-header">
        <h1>📁 Evidence Upload</h1>
        <p>
          Upload documents, images, or text files. The pipeline will extract text via OCR
          and identify entities using NLP.
        </p>
      </div>

      {/* Drop Zone */}
      <div
        id="evidence-dropzone"
        className={`upload-zone ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => document.getElementById('file-input').click()}
      >
        <div className="upload-zone-icon">{uploading ? '⏳' : '📤'}</div>
        <h3>{uploading ? 'Processing...' : 'Drop evidence file here'}</h3>
        <p>or click to browse your files</p>
        <div className="upload-formats">
          {formats.map((f) => (
            <span className="format-tag" key={f}>{f}</span>
          ))}
        </div>
        <input
          id="file-input"
          type="file"
          onChange={handleFileInput}
          style={{ display: 'none' }}
          accept=".txt,.pdf,.png,.jpg,.jpeg,.tiff,.bmp"
        />
      </div>

      {/* Upload Result */}
      {result && (
        <div className="result-card anim-slide-down">
          <h3 style={{ marginBottom: 'var(--sp-4)' }}>✅ Upload Successful</h3>
          <div className="result-field">
            <span className="result-label">File</span>
            <span className="result-value">{result.filename}</span>
          </div>
          <div className="result-field">
            <span className="result-label">Status</span>
            <span className="badge badge-success">{result.status}</span>
          </div>
          <div className="result-field">
            <span className="result-label">Entities</span>
            <span className="result-value">{result.entity_count} found</span>
          </div>
          {result.entity_summary && Object.keys(result.entity_summary).length > 0 && (
            <div style={{ marginTop: 'var(--sp-4)' }}>
              <span className="result-label" style={{ display: 'block', marginBottom: 'var(--sp-2)' }}>
                Entity Breakdown
              </span>
              <div className="entity-tags">
                {Object.entries(result.entity_summary).map(([cat, count]) => (
                  <span
                    key={cat}
                    className="entity-tag"
                    style={{ '--tag-color': CATEGORY_COLORS[cat] || CATEGORY_COLORS.Other }}
                  >
                    {cat}: {count}
                  </span>
                ))}
              </div>
            </div>
          )}
          {result.entities && result.entities.length > 0 && (
            <div style={{ marginTop: 'var(--sp-4)' }}>
              <span className="result-label" style={{ display: 'block', marginBottom: 'var(--sp-2)' }}>
                Extracted Entities
              </span>
              <div className="entity-chips">
                {result.entities.slice(0, 30).map((ent, i) => (
                  <span
                    key={`${ent.text}-${i}`}
                    className="entity-chip"
                    style={{ borderColor: CATEGORY_COLORS[ent.category] || CATEGORY_COLORS.Other }}
                    title={`${ent.label} → ${ent.category}`}
                  >
                    <span className="entity-chip-dot" style={{ background: CATEGORY_COLORS[ent.category] || CATEGORY_COLORS.Other }} />
                    {ent.text}
                  </span>
                ))}
                {result.entities.length > 30 && (
                  <span className="entity-chip" style={{ borderColor: 'var(--border)' }}>
                    +{result.entities.length - 30} more
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="result-card error anim-slide-down">
          <h3 style={{ color: 'var(--danger)', marginBottom: 'var(--sp-3)' }}>❌ Upload Failed</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-sm)' }}>{error}</p>
        </div>
      )}

      {/* Evidence List */}
      {evidenceList.length > 0 ? (
        <div style={{ marginTop: 'var(--sp-8)' }} className="anim-fade-up delay-2">
          <h2 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--sp-4)' }}>
            📂 Uploaded Evidence ({evidenceList.length})
          </h2>
          <div className="evidence-table">
            <div className="evidence-table-header">
              <span>File</span>
              <span>Type</span>
              <span>Status</span>
              <span>Entities</span>
              <span>Actions</span>
            </div>
            {evidenceList.map((ev) => (
              <div className="evidence-table-row" key={ev.id}>
                <span className="evidence-filename">{ev.filename}</span>
                <span><span className="format-tag">{ev.file_type.toUpperCase()}</span></span>
                <span>
                  <span className={`badge ${ev.status === 'processed' ? 'badge-success' : 'badge-danger'}`}>
                    {ev.status}
                  </span>
                </span>
                <span className="result-value">{ev.entity_count}</span>
                <span className="evidence-actions">
                  <button
                    className="btn-sm btn-ghost"
                    onClick={() => handleViewDetail(ev.id)}
                  >
                    👁️ View
                  </button>
                  <button
                    className="btn-sm btn-danger-ghost"
                    onClick={() => handleDelete(ev.id)}
                  >
                    🗑️
                  </button>
                </span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        !uploading && (
          <div className="empty-evidence-prompt anim-fade-up delay-2">
            <div className="empty-prompt-icon">📂</div>
            <h3>No Evidence Files Ingested Yet</h3>
            <p>
              Your investigator workspace is currently blank. Drag and drop case documents,
              FIRs, PDFs, or CCTV stills into the upload zone above to begin automated extraction.
            </p>
          </div>
        )
      )}

      {/* Evidence Detail Modal */}
      {loadingDetail && (
        <div className="result-card anim-slide-down" style={{ marginTop: 'var(--sp-4)' }}>
          <p style={{ textAlign: 'center', color: 'var(--text-muted)' }}>Loading evidence details...</p>
        </div>
      )}

      {selectedEvidence && (
        <div className="result-card anim-slide-down" style={{ marginTop: 'var(--sp-4)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--sp-4)' }}>
            <h3>📄 {selectedEvidence.filename}</h3>
            <button className="btn-sm btn-ghost" onClick={() => setSelectedEvidence(null)}>✕ Close</button>
          </div>

          <div className="result-field">
            <span className="result-label">ID</span>
            <code className="result-value" style={{ fontSize: 'var(--text-xs)', background: 'var(--bg-glass)', padding: '2px 8px', borderRadius: '4px' }}>
              {selectedEvidence.id}
            </code>
          </div>
          <div className="result-field">
            <span className="result-label">Uploaded</span>
            <span className="result-value">{new Date(selectedEvidence.upload_date).toLocaleString()}</span>
          </div>
          <div className="result-field">
            <span className="result-label">Entities</span>
            <span className="result-value">{selectedEvidence.entity_count}</span>
          </div>

          {selectedEvidence.entities && selectedEvidence.entities.length > 0 && (
            <div style={{ marginTop: 'var(--sp-4)' }}>
              <span className="result-label" style={{ display: 'block', marginBottom: 'var(--sp-2)' }}>
                All Entities
              </span>
              <div className="entity-chips">
                {selectedEvidence.entities.map((ent, i) => (
                  <span
                    key={`${ent.text}-${i}`}
                    className="entity-chip"
                    style={{ borderColor: CATEGORY_COLORS[ent.category] || CATEGORY_COLORS.Other }}
                    title={`${ent.label} → ${ent.category}`}
                  >
                    <span className="entity-chip-dot" style={{ background: CATEGORY_COLORS[ent.category] || CATEGORY_COLORS.Other }} />
                    {ent.text}
                  </span>
                ))}
              </div>
            </div>
          )}

          {selectedEvidence.raw_text && (
            <div style={{ marginTop: 'var(--sp-4)' }}>
              <span className="result-label" style={{ display: 'block', marginBottom: 'var(--sp-2)' }}>
                Extracted Text
              </span>
              <pre className="text-preview">{selectedEvidence.raw_text}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
