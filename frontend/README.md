# Sovereign AI Workbench — Frontend

Frontend for the SIH26117 practice project. Built with Create React App + CRACO + Tailwind CSS. Talks to a real FastAPI backend (owned by Person 1 & 2 — model serving via Groq, agent loop, OCR pipeline).

## Design

Instrument-panel / blueprint aesthetic rather than a generic SaaS look: near-black base, amber signal accent for active states, muted teal for "connected", sharp 2px corners, IBM Plex Sans for headers and IBM Plex Mono for all data/labels/filenames.

## Getting Started

```bash
npm install
cp .env.example .env   # set REACT_APP_API_BASE_URL to your backend
npm start
```

Runs at `http://localhost:3000`.

## Project Structure

```
src/
  App.js                    # three-panel layout
  api/client.js             # ALL backend calls live here — edit this file
                             # once Person 1/2 confirm the real route names
                             # and response shape in app/main.py
  components/
    ChatPanel.js             # chat + renders agent steps as they return
    DocumentViewer.js         # file upload + preview
    FilePanel.js               # generated file card + download
    StatusBadge.js             # connected/air-gapped indicator + toggle
```

## Backend Contract (assumed — confirm and update `src/api/client.js`)

`sendQuery(message, context)` expects:

```json
{
  "steps": [{ "label": "Searching internal standards...", "status": "done" }],
  "generatedFile": { "filename": "Approval_Note_Draft.docx", "downloadUrl": "https://..." }
}
```

If the backend streams progress instead of returning one blob, swap in the
commented SSE variant inside `client.js`.

## Build

```bash
npm run build
```

## Deploy

Push to GitHub, connect to Vercel, set `REACT_APP_API_BASE_URL` as an environment variable in the Vercel project settings.
