// ---------------------------------------------------------------------------
// Sovereign AI Workbench — API client
//
// Confirmed against the real backend/app/main.py + models.py and the real
// ingestion/app.py (as of Hour ~7). Two separate services:
//   - Backend/Agent (Person 1): localhost:8000 — chat queries + file download
//   - Ingestion (Person 2): localhost:8001 — document upload/OCR directly,
//     NOT proxied through the backend.
//
// Confirmed response shape for sendQuery() -> POST /agent/query:
// {
//   answer: "string",
//   tool_trace: [ { tool: "search|calculate|write_file", input: {}, output: {} } ],
//   file_url: "string | null"
// }
//
// Confirmed response shape for uploadDocument() -> POST /ingest (port 8001):
// {
//   doc_id: "string",
//   status: "ready|processing|error",
//   page_count: number
// }
// ---------------------------------------------------------------------------

const BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
const INGESTION_URL = process.env.REACT_APP_INGESTION_BASE_URL || 'http://localhost:8001';

const ROUTES = {
  chat: '/agent/query',       // backend, confirmed against app/main.py
  upload: '/ingest',          // ingestion service, confirmed against ingestion/app.py — NOT the backend
  file: (filename) => `/files/${filename}`, // backend, confirmed against app/main.py
};

async function handleResponse(res) {
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Request failed (${res.status}): ${text || res.statusText}`);
  }
  return res.json();
}

/**
 * Sends a user query against an already-ingested document to the agent
 * backend and returns its answer, tool trace, and any generated file URL.
 *
 * @param {string} message
 * @param {{ docId?: string }} [context]
 */
export async function sendQuery(message, context = {}) {
  const res = await fetch(`${BASE_URL}${ROUTES.chat}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: message, doc_id: context.docId ?? '' }),
  });
  return handleResponse(res);
}

/**
 * Uploads a document (image or PDF) directly to the Ingestion service
 * (port 8001) for OCR/chunking. Returns { doc_id, status, page_count }.
 * The returned doc_id is what gets passed back into sendQuery's context.
 *
 * @param {File} file
 */
export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${INGESTION_URL}${ROUTES.upload}`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse(res);
}

/**
 * Resolves a generated file's direct download URL on the backend.
 *
 * @param {string} filename
 */
export function getFileDownloadUrl(filename) {
  return `${BASE_URL}${ROUTES.file(filename)}`;
}
