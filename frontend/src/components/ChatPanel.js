import React, { useState, useRef, useEffect } from 'react';
import { sendQuery } from '../api/client';

const STEP_REVEAL_DELAY_MS = 500;
const BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// tool_trace items look like { tool: "search|calculate|write_file", input: {}, output: {} }
// there's no human-readable "label" field from the backend, so build one here.
function describeToolStep(step) {
  switch (step.tool) {
    case 'search':
      return `Searching internal standards for "${step.input?.query ?? ''}"…`;
    case 'calculate':
      return 'Running calculation…';
    case 'write_file':
      return 'Drafting Word note…';
    default:
      return `Running ${step.tool}…`;
  }
}

export default function ChatPanel({ documentId, onFileGenerated }) {
  const [messages, setMessages] = useState([
    { role: 'system', text: 'Upload a document on the right, then ask a question about it.' },
  ]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  async function handleSubmit(e) {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || busy) return;

    setMessages((prev) => [...prev, { role: 'user', text: trimmed }]);
    setInput('');
    setBusy(true);

    try {
      const result = await sendQuery(trimmed, documentId ? { docId: documentId } : {});
      const trace = result?.tool_trace || [];

      for (const step of trace) {
        await sleep(STEP_REVEAL_DELAY_MS);
        setMessages((prev) => [...prev, { role: 'agent', text: describeToolStep(step) }]);
      }

      if (result?.answer) {
        await sleep(STEP_REVEAL_DELAY_MS);
        setMessages((prev) => [...prev, { role: 'agent', text: result.answer }]);
      }

      if (result?.file_url) {
        const filename = result.file_url.split('/').pop();
        onFileGenerated?.({
          filename,
          downloadUrl: `${result.file_url.startsWith('http') ? '' : BASE_URL}${result.file_url}`,
        });
        await sleep(STEP_REVEAL_DELAY_MS);
        setMessages((prev) => [
          ...prev,
          { role: 'agent', text: `Generated ${filename}. See the file panel →` },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'error', text: `Request failed: ${err.message}` }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="panel">
      <div className="panel-header">01 · AGENT CHAT</div>

      <div ref={scrollRef} className="chat-messages">
        {messages.map((m, i) => (
          <Bubble key={i} role={m.role} text={m.text} />
        ))}
        {busy && <div className="chat-busy">agent is working…</div>}
      </div>

      <form onSubmit={handleSubmit} className="chat-form">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about the uploaded document…"
          className="chat-input"
          disabled={busy}
        />
        <button type="submit" disabled={busy || !input.trim()} className="btn-primary">
          Send
        </button>
      </form>
    </div>
  );
}

function Bubble({ role, text }) {
  return (
    <div className={`bubble ${role} fade-in`}>
      {text}
    </div>
  );
}
