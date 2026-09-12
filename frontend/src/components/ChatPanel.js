import React, { useState, useRef, useEffect } from 'react';
import { sendQuery } from '../api/client';

const STEP_REVEAL_DELAY_MS = 500;

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export default function ChatPanel({ documentId, onFileGenerated }) {
  const [messages, setMessages] = useState([
    {
      role: 'system',
      text: 'Upload a document on the right, then ask a question about it.',
    },
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
      const result = await sendQuery(trimmed, documentId ? { documentId } : {});
      const steps = result?.steps || [];

      // Reveal each agent step in sequence rather than dumping them all at once —
      // this is what actually communicates "agent loop" to someone watching.
      for (const step of steps) {
        await sleep(STEP_REVEAL_DELAY_MS);
        setMessages((prev) => [...prev, { role: 'agent', text: step.label }]);
      }

      if (result?.generatedFile) {
        onFileGenerated?.(result.generatedFile);
        await sleep(STEP_REVEAL_DELAY_MS);
        setMessages((prev) => [
          ...prev,
          { role: 'agent', text: `Generated ${result.generatedFile.filename}. See the file panel →` },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'error', text: `Request failed: ${err.message}` },
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex flex-col h-full border border-line rounded-sharp bg-panel">
      <div className="border-b border-line px-4 py-2.5">
        <span className="font-mono text-xs tracking-wide text-ink-muted">01 · AGENT CHAT</span>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        {messages.map((m, i) => (
          <Bubble key={i} role={m.role} text={m.text} />
        ))}
        {busy && (
          <div className="font-mono text-xs text-ink-faint animate-fade-in-up">
            agent is working<span className="animate-blink">…</span>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="border-t border-line p-3 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about the uploaded document…"
          className="flex-1 bg-base border border-line rounded-sharp px-3 py-2 text-sm text-ink placeholder:text-ink-faint focus:outline-none focus:border-signal-dim"
          disabled={busy}
        />
        <button
          type="submit"
          disabled={busy || !input.trim()}
          className="px-4 py-2 rounded-sharp bg-signal text-base font-medium text-sm disabled:opacity-40 disabled:cursor-not-allowed hover:bg-signal/90 transition-colors"
        >
          Send
        </button>
      </form>
    </div>
  );
}

function Bubble({ role, text }) {
  if (role === 'user') {
    return (
      <div className="flex justify-end animate-fade-in-up">
        <div className="max-w-[85%] bg-signal/10 border border-signal-dim/40 text-ink rounded-sharp px-3 py-2 text-sm">
          {text}
        </div>
      </div>
    );
  }
  if (role === 'error') {
    return (
      <div className="animate-fade-in-up">
        <div className="max-w-[85%] border border-danger/50 text-danger rounded-sharp px-3 py-2 text-sm font-mono">
          {text}
        </div>
      </div>
    );
  }
  if (role === 'agent') {
    return (
      <div className="animate-fade-in-up">
        <div className="max-w-[85%] border border-line2 text-ink-muted rounded-sharp px-3 py-2 text-sm font-mono">
          {text}
        </div>
      </div>
    );
  }
  // system
  return (
    <div className="text-xs text-ink-faint font-mono px-1">{text}</div>
  );
}
