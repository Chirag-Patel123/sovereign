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
    <div className="min-h-screen bg-base text-ink flex flex-col">
      <header className="border-b border-line px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold tracking-tight">Sovereign Workbench</h1>
          <p className="font-mono text-[11px] text-ink-faint mt-0.5">
            on-premise · agentic · confidential document processing
          </p>
        </div>
        <StatusBadge online={online} onToggle={() => setOnline((v) => !v)} />
      </header>

      <main className="flex-1 grid grid-cols-1 lg:grid-cols-[1fr_1.4fr_1fr] gap-4 p-4 lg:p-6 min-h-0">
        <div className="min-h-[420px] lg:min-h-0">
          <ChatPanel documentId={documentId} onFileGenerated={setGeneratedFile} />
        </div>
        <div className="min-h-[420px] lg:min-h-0">
          <DocumentViewer onDocumentReady={setDocumentId} />
        </div>
        <div className="min-h-[240px] lg:min-h-0">
          <FilePanel file={generatedFile} />
        </div>
      </main>
    </div>
  );
}
