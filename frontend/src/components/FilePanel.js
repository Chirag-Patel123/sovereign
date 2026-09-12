import React from 'react';

export default function FilePanel({ file }) {
  return (
    <div className="flex flex-col h-full border border-line rounded-sharp bg-panel">
      <div className="border-b border-line px-4 py-2.5">
        <span className="font-mono text-xs tracking-wide text-ink-muted">03 · GENERATED FILE</span>
      </div>

      <div className="flex-1 flex items-center justify-center p-4">
        {!file && (
          <p className="text-sm text-ink-faint font-mono text-center px-4">
            Output appears here once the agent finishes drafting.
          </p>
        )}

        {file && (
          <div className="w-full border border-patina-dim rounded-sharp p-4 animate-fade-in-up">
            <div className="flex items-center gap-2 mb-3">
              <span className="h-2 w-2 rounded-sharp bg-patina" aria-hidden="true" />
              <span className="font-mono text-xs text-patina">READY</span>
            </div>
            <p className="text-sm text-ink mb-4 break-all font-mono">{file.filename}</p>
            <a
              href={file.downloadUrl}
              download
              className="block text-center bg-signal text-base font-medium text-sm rounded-sharp py-2 hover:bg-signal/90 transition-colors"
            >
              Download
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
