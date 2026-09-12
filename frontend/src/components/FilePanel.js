import React from 'react';

export default function FilePanel({ file }) {
  return (
    <div className="panel">
      <div className="panel-header">03 · GENERATED FILE</div>

      <div className="file-body">
        {!file && <p className="file-empty">Output appears here once the agent finishes drafting.</p>}

        {file && (
          <div className="file-card fade-in">
            <div className="file-ready-row">
              <span className="file-ready-dot" aria-hidden="true" />
              <span className="file-ready-label">READY</span>
            </div>
            <p className="file-name">{file.filename}</p>
            <a href={file.downloadUrl} download className="download-btn">Download</a>
          </div>
        )}
      </div>
    </div>
  );
}
