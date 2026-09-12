import React from 'react';

export default function StatusBadge({ online, onToggle }) {
  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-2 border border-line px-3 py-1.5 rounded-sharp">
        <span
          className={[
            'inline-block h-2 w-2 rounded-sharp',
            online ? 'bg-patina animate-blink' : 'bg-danger animate-blink',
          ].join(' ')}
          aria-hidden="true"
        />
        <span className="font-mono text-xs tracking-wide text-ink-muted">
          {online ? 'CONNECTED' : 'AIR-GAPPED · LOCAL ONLY'}
        </span>
      </div>
      <button
        onClick={onToggle}
        className="font-mono text-xs text-ink-muted border border-line px-3 py-1.5 rounded-sharp hover:border-signal-dim hover:text-ink transition-colors"
      >
        {online ? 'Disconnect network' : 'Restore connection'}
      </button>
    </div>
  );
}
