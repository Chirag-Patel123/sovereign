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
      setPreview(null); // PDFs: no inline preview, just show the filename card
    }

    setUploading(true);
    try {
      const result = await uploadDocument(file);
      onDocumentReady?.(result?.documentId ?? result?.id ?? null);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="flex flex-col h-full border border-line rounded-sharp bg-panel">
      <div className="border-b border-line px-4 py-2.5 flex items-center justify-between">
        <span className="font-mono text-xs tracking-wide text-ink-muted">02 · DOCUMENT</span>
        <label className="font-mono text-xs text-signal border border-signal-dim/50 px-2.5 py-1 rounded-sharp cursor-pointer hover:bg-signal/10 transition-colors">
          Upload
          <input
            type="file"
            accept="image/*,application/pdf"
            className="hidden"
            onChange={handleChange}
          />
        </label>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {!fileName && (
          <div className="h-full flex items-center justify-center text-center px-6">
            <p className="text-sm text-ink-faint font-mono leading-relaxed">
              No document loaded.
              <br />
              Upload a scanned drawing or standard to begin.
            </p>
          </div>
        )}

        {fileName && (
          <div className="space-y-3 animate-fade-in-up">
            <div className="flex items-center justify-between font-mono text-xs text-ink-muted">
              <span>{fileName}</span>
              {uploading ? <span className="text-signal">processing…</span> : <span className="text-patina">ready</span>}
            </div>

            {preview ? (
              <img
                src={preview}
                alt={fileName}
                className="w-full rounded-sharp border border-line2 object-contain max-h-[420px]"
              />
            ) : (
              <div className="border border-line2 rounded-sharp p-6 text-center text-ink-faint text-sm font-mono">
                PDF loaded — inline preview not rendered
              </div>
            )}

            {error && (
              <p className="text-danger text-xs font-mono">{error}</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
