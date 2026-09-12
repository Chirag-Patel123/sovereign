// ---------------------------------------------------------------------------
// Sovereign AI Workbench — API client
//
// This is the ONLY file that should need edits once Person 1 / Person 2
// confirm the real FastAPI route names and payload shapes from their
// `app/main.py` and `app/models.py`. Everything above this layer (the React
// components) talks to the functions below, not to fetch() directly.
//
// Expected (assumed) response shape for sendQuery():
// {
//   steps: [
//     { label: "Searching internal standards...", status: "done" },
//     { label: "Running calculation...", status: "done" },
//     { label: "Drafting Word note...", status: "done" }
//   ],
//   generatedFile: { filename: "Approval_Note_Draft.docx", downloadUrl: "https://..." } | null
// }
//
// TODO once confirmed with backend:
// - Update ROUTES below to match app/main.py exactly.
// - If the backend streams progress (SSE / chunked response) instead of
//   returning one JSON blob, replace the body of sendQuery() with the
//   EventSource/fetch-stream variant — see the commented alternative below.
// ---------------------------------------------------------------------------

const BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const ROUTES = {
  chat: '/agent/query', // guess based on app/agent/ folder — confirm with Person 1
  upload: '/documents/upload', // confirm with Person 2
  file: (fileId) => `/files/${fileId}`,
};

async function handleResponse(res) {
  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`Request failed (${res.status}): ${text || res.statusText}`);
  }
  return res.json();
}

/**
 * Sends a user query (optionally referencing an already-uploaded document)
 * to the agent backend and returns the agent's steps + any generated file.
 *
 * @param {string} message
 * @param {{ documentId?: string } } [context]
 */
export async function sendQuery(message, context = {}) {
  const res = await fetch(`${BASE_URL}${ROUTES.chat}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: message, ...context }),
  });
  return handleResponse(res);

  // --- Streaming alternative (uncomment if backend uses SSE) ---
  // return new Promise((resolve, reject) => {
  //   const steps = [];
  //   const evtSource = new EventSource(`${BASE_URL}${ROUTES.chat}?query=${encodeURIComponent(message)}`);
  //   evtSource.onmessage = (e) => {
  //     const data = JSON.parse(e.data);
  //     if (data.type === 'step') steps.push(data.step);
  //     if (data.type === 'done') {
  //       evtSource.close();
  //       resolve({ steps, generatedFile: data.generatedFile || null });
  //     }
  //   };
  //   evtSource.onerror = (err) => { evtSource.close(); reject(err); };
  // });
}

/**
 * Uploads a document (image or PDF) to the backend for OCR/ingestion.
 * Returns an identifier the caller can pass back in sendQuery's context.
 *
 * @param {File} file
 */
export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${BASE_URL}${ROUTES.upload}`, {
    method: 'POST',
    body: formData,
  });
  return handleResponse(res);
}

/**
 * Resolves a generated file's direct download URL, if the backend returns
 * an ID rather than a full URL from sendQuery().
 *
 * @param {string} fileId
 */
export async function getGeneratedFile(fileId) {
  const res = await fetch(`${BASE_URL}${ROUTES.file(fileId)}`);
  return handleResponse(res);
}
