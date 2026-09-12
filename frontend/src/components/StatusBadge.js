import React from 'react';

export default function StatusBadge({ online, onToggle }) {
  return (
    <div className="status-group">
      <div className="status-pill">
        <span className={`status-dot ${online ? 'online' : 'offline'}`} aria-hidden="true" />
        <span className="mono">{online ? 'CONNECTED' : 'AIR-GAPPED · LOCAL ONLY'}</span>
      </div>
      <button onClick={onToggle} className="status-btn">
        {online ? 'Disconnect network' : 'Restore connection'}
      </button>
    </div>
  );
}
