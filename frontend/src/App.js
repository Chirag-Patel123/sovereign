import React, { useState } from 'react';
import StatusBadge from './components/StatusBadge';
import ChatPanel from './components/ChatPanel';
import DocumentViewer from './components/DocumentViewer';
import FilePanel from './components/FilePanel';

export default function App() {
  const [online, setOnline] = useState(true);
  const [documentId, setDocumentId] = useState(null);
  const [generatedFile, setGeneratedFile] = useState(null);

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <h1>Sovereign Workbench</h1>
          <p>on-premise · agentic · confidential document processing</p>
        </div>
        <StatusBadge online={online} onToggle={() => setOnline((v) => !v)} />
      </header>

      <main className="app-main">
        <div className="panel-slot">
          <ChatPanel documentId={documentId} onFileGenerated={setGeneratedFile} />
        </div>
        <div className="panel-slot">
          <DocumentViewer onDocumentReady={setDocumentId} />
        </div>
        <div className="panel-slot">
          <FilePanel file={generatedFile} />
        </div>
      </main>
    </div>
  );
}
