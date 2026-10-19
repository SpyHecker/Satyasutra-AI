import { useState, useCallback } from 'react';
import api from '../api/client';

export default function EvidenceUpload() {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === 'dragenter' || e.type === 'dragover');
  }, []);

  const handleUpload = useCallback(async (file) => {
    setUploading(true);
    setError(null);
    setResult(null);
    try {
      const response = await api.evidence.upload(file);
      setResult(response);
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
            <span className="badge badge-info">{result.status}</span>
          </div>
          <div className="result-field">
            <span className="result-label">Message</span>
            <span style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-sm)' }}>{result.message}</span>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="result-card error anim-slide-down">
          <h3 style={{ color: 'var(--danger)', marginBottom: 'var(--sp-3)' }}>❌ Upload Failed</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: 'var(--text-sm)' }}>{error}</p>
        </div>
      )}
    </div>
  );
}
