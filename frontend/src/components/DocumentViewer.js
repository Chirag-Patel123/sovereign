import React, { useState } from 'react';
import { uploadDocument } from '../api/client';

export default function DocumentViewer({ onDocumentReady }) {
  const [preview, setPreview] = useState(null);
  const [fileName, setFileName] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  async function handleChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;

    setError(null);
    setFileName(file.name);
    if (file.type.startsWith('image/')) {
      setPreview(URL.createObjectURL(file));
    } else {
      setPreview(null);
    }

    setUploading(true);
    try {
      const result = await uploadDocument(file);
      onDocumentReady?.(result?.doc_id ?? null);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="panel">
      <div className="panel-header">
        <span>02 · DOCUMENT</span>
        <label className="upload-label">
          Upload
          <input type="file" accept="image/*,application/pdf" style={{ display: 'none' }} onChange={handleChange} />
        </label>
      </div>

      <div className="doc-body">
        {!fileName && (
          <div className="doc-empty">
            <p>No document loaded.<br />Upload a scanned drawing or standard to begin.</p>
          </div>
        )}

        {fileName && (
          <div className="fade-in">
            <div className="doc-status-row">
              <span>{fileName}</span>
              {uploading ? <span className="processing">processing…</span> : <span className="ready">ready</span>}
            </div>

            {preview ? (
              <img src={preview} alt={fileName} className="doc-preview" />
            ) : (
              <div className="doc-pdf-placeholder">PDF loaded — inline preview not rendered</div>
            )}

            {error && <p className="doc-error">{error}</p>}
          </div>
        )}
      </div>
    </div>
  );
}
