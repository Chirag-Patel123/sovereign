# SIH26117 — PRD & Execution Plan
### Sovereign On-Premise Agentic AI Workbench (MRPL) — 3-Person Build Track

Built on top of the Battle Plan's locked scope: **one flawless end-to-end journey** — upload a scanned document → agent reads it, retrieves the relevant internal standard, runs a calculation, returns a formatted Word file — demoed with the network physically disconnected. 24-hour internal round.

This split works because the three tracks have a clean boundary: **Person 2 produces retrievable chunks, Person 1 consumes them and produces a file, Person 3 never touches a model or a vector store directly.** Freezing the interface between them in the first two hours is the single highest-leverage thing this team can do — it's what lets three people build in parallel instead of waiting on each other.

---

## PART 1 — PRODUCT REQUIREMENTS DOCUMENT

### 1.1 Problem Statement (recap)
Confidential industrial knowledge work — approval notes, calculations, reviewing scanned drawings — cannot go near cloud AI tools, so it's done manually or leaked into public chatbots anyway. Build a self-hosted, air-gapped assistant that reads documents/drawings, grounds answers in internal standards, and outputs real files.

### 1.2 Goals (this build)
- G1: Ingest one scanned document and make its content retrievable.
- G2: An agent plans and executes a small tool sequence (search → calculate → write file) rather than answering in one shot.
- G3: Output is a real, downloadable, formatted `.docx` file — not chat text.
- G4: The full flow runs with zero network calls at demo time.

### 1.3 Non-Goals (explicitly out of scope for this build)
- Multiple concurrent users, auth, or audit logging.
- Training or fine-tuning any model.
- General-purpose P&ID symbol recognition (attempt only if G1–G4 are done early).
- More than one input document type in the demo path.
- A production-grade model router — a visibly working dispatcher between two models is enough if time allows; it is a Should, not a Must.

### 1.4 Primary User & Core Use Case
A refinery process engineer uploads a scanned document (a standard, a note, or a simple P&ID) and asks a question that requires: finding the relevant passage, doing a calculation referencing it, and producing a shareable approval-note draft.

### 1.5 System Architecture

Three independently runnable services, integrated only through HTTP calls:

```
┌─────────────┐      ┌──────────────────┐      ┌───────────────────────┐
│  UI (P3)    │ ───► │ Backend/Agent (P1)│ ───► │ Ingestion/Retrieval    │
│  React/     │ ◄─── │ Ollama + agent    │ ◄─── │ (P2)                  │
│  Streamlit  │      │ loop + tools      │      │ OCR + chunk + vector   │
└─────────────┘      └──────────────────┘      └───────────────────────┘
                              │
                              ▼
                      docx/xlsx file writer
                      (local tool, in-process)
```

- **UI (Person 3)** never calls Ingestion directly for querying — only for the upload step. All querying goes through the Agent, which is the single orchestrator. This keeps the UI dumb and the integration surface small.
- **Backend/Agent (Person 1)** treats retrieval as *one tool among several* it can call — this is what makes it an agent loop rather than a RAG pipeline with a wrapper.
- **Ingestion/Retrieval (Person 2)** is a self-contained service with no knowledge of the agent or UI — it only knows documents and chunks.

### 1.6 API Contracts (freeze these in Hour 1 — do not renegotiate mid-build)

**Ingestion/Retrieval service (owned by Person 2), exposed on `localhost:8001`**

```
POST /ingest
  body: multipart file (PDF or image)
  returns: { "doc_id": "string", "status": "ready|processing|error", "page_count": int }

GET /search?doc_id={id}&query={text}&top_k=5
  returns: {
    "chunks": [
      { "chunk_id": "string", "text": "string", "page": int, "score": float }
    ]
  }
```

**Backend/Agent service (owned by Person 1), exposed on `localhost:8000`**

```
POST /agent/query
  body: { "doc_id": "string", "query": "string" }
  returns: {
    "answer": "string",
    "tool_trace": [ { "tool": "search|calculate|write_file", "input": {}, "output": {} } ],
    "file_url": "string | null"   // set when write_file tool ran
  }

GET /files/{filename}
  returns: the generated .docx/.xlsx file for download
```

**UI (Person 3)** only ever calls `POST /ingest` (on upload) and `POST /agent/query` (on every user message), then renders `answer`, optionally the `tool_trace` for a "show its work" panel, and a download button pointed at `file_url`.

**Why this shape matters:** Person 3 can build the entire UI today against a hardcoded mock JSON matching these exact response shapes, without either backend existing yet. Person 1 can build and test the agent loop against a mock `/search` response before Person 2's OCR pipeline is real. This is what makes 3-way parallel work possible in 24 hours.

### 1.7 Data Model

```
Document
  doc_id: string
  filename: string
  page_count: int
  status: enum(processing, ready, error)

Chunk
  chunk_id: string
  doc_id: string (FK)
  page: int
  text: string
  embedding: vector

ToolCall (for tool_trace, not persisted — in-memory per request)
  tool: string
  input: object
  output: object

GeneratedFile
  filename: string
  doc_id: string (FK)
  file_path: string
  created_at: timestamp
```

Keep storage dead simple: SQLite or even a JSON file for `Document`/`Chunk` metadata, a local FAISS or Chroma index for embeddings, and generated files just written to a local `/outputs` folder served statically. No need for Postgres or anything heavier in 24 hours.

### 1.8 Non-Functional Requirements
- **NFR1 — Offline at demo time.** No component may make an external network call once the demo begins. Ollama, OCR models, and embeddings must all be pre-downloaded before the network is cut.
- **NFR2 — Runs on the actual demo laptop.** Whatever GPU/CPU the presenting machine has is the real constraint — test on it by Hour 8, not Hour 22.
- **NFR3 — Response latency under ~20 seconds** for the full agent flow on the demo query — long enough to allow real work, short enough not to lose the judges' attention. If the honest latency is higher, script a short verbal bridge ("it's reading the drawing now") rather than silence.
- **NFR4 — Deterministic on the demo query.** The three rehearsed demo queries (Section 1.9) must return consistent results across runs — pin temperature low, and consider caching the demo's exact retrieval + agent trace as a fallback path.

### 1.9 Acceptance Criteria (Definition of Done for the MVP)
- [ ] A scanned sample document can be uploaded and shows `status: ready` within a reasonable time.
- [ ] A natural-language query against that document returns an answer grounded in retrieved text (not hallucinated) — verify by checking `tool_trace` shows a real `search` call with matching chunk text.
- [ ] The agent calls at least two distinct tools in sequence for the demo query (e.g., `search` then `write_file`).
- [ ] A `.docx` file is generated, downloadable, and readably formatted (headings, not a text dump).
- [ ] The entire flow above completes with Wi-Fi/Ethernet disabled on the demo machine.
- [ ] The same three rehearsed queries produce consistent, correct results on three consecutive runs.

---

## PART 2 — EXECUTION PLAN (24 HOURS, 3 TECHNICAL TRACKS)

### Hour 0–2 — Contract Freeze (all three, together)
- Agree and write down the API contracts in Section 1.6 exactly as above, or amend them now — never after.
- Person 2 picks and pre-downloads the OCR/embedding models. Person 1 picks and pre-downloads the LLM via Ollama. Person 3 scaffolds the UI project and hardcodes a mock response matching the contract shapes.
- **Sync point:** everyone can state the other two people's API shapes from memory before moving on.

### Hour 2–8 — Independent Build, Track 1
| Person | Task | Done condition |
|---|---|---|
| P1 (Backend/Agent) | Stand up Ollama; build the agent loop skeleton with a mock `search` tool (returns hardcoded chunks) and a real `write_file` tool | Agent responds to a test query end-to-end using the mock, produces a real .docx |
| P2 (Ingestion/Retrieval) | Build `/ingest` (OCR via PaddleOCR/docling → text) and `/search` (chunk + embed + similarity search) against one real sample PDF | `/search` returns correct, relevant chunks for 3 test queries on the real document |
| P3 (UI) | Build upload screen, chat screen, and generated-file panel entirely against the mocked JSON from Hour 0 | UI is fully clickable and renders realistic-looking (fake) responses |

**Sync point at Hour 8:** Person 1 swaps the mock `search` tool for a real HTTP call to Person 2's `/search` endpoint. This should be a 15-minute change if the contract was respected — if it isn't, that's the signal something drifted and needs fixing now, not at Hour 20.

### Hour 8–14 — Independent Build, Track 2
| Person | Task | Done condition |
|---|---|---|
| P1 | Add the `calculate` tool (hardcode the demo's specific formula, don't build a general math engine); wire multi-step planning so the agent chains search → calculate → write_file | The full three-tool chain runs correctly on the real demo query |
| P2 | Extend ingestion to the second demo document (e.g., the P&ID or handwritten note) if Track 1 finished early; otherwise, harden OCR accuracy on the primary document | `/search` quality holds up on messier/lower-quality scans |
| P3 | Wire the UI to Person 1's real `/agent/query` endpoint instead of the mock; add the download button pointed at `file_url` | End user can go upload → ask → download a real file through the actual UI |

**Sync point at Hour 14:** Full three-service integration test, live, on the actual demo laptop. This is the most important checkpoint in the whole 24 hours — if it slips past here, cut scope immediately per the Battle Plan's contingency list rather than pushing it to Hour 20.

### Hour 14–20 — Integration & Polish
- P1: Improve prompt/agent reliability on the exact rehearsed queries; add the second model + a visible routing indicator in `tool_trace` if time allows (Should, not Must).
- P2: Pre-embed and cache all demo documents so ingestion latency isn't a live risk during the demo itself.
- P3: Polish formatting of the `.docx` output template (headings, logo, consistent spacing) and the UI's "show its work" trace panel — this is the highest perceived-value-per-hour work left.
- All three: disable network on the demo machine and run the full flow twice, back to back.

### Hour 20–24 — Freeze & Rehearse
- Hour 20: code freeze. No new features, no new tools, no new documents.
- Hour 20–22: three consecutive full run-throughs on the actual presentation setup, timed.
- Hour 22: record a screen-capture fallback of a clean successful run, in case live demo fails.
- Hour 22–24: pitch rehearsal, slide polish, and a final dry run of the physical "pull the cable" moment specifically — practice this exact motion, it's the demo's signature beat.

### Cross-Track Risks & Mitigations
| Risk | Owner most exposed | Mitigation |
|---|---|---|
| OCR misreads the sample document badly | P2 | Pick the cleanest, highest-contrast sample document for the demo path; keep a messier one only as a stretch goal |
| Agent loop doesn't reliably call tools in the right order | P1 | Constrain the demo to one scripted query pattern rather than open-ended chat; the agent's *flexibility* is explained verbally, not proven live |
| Model too slow on demo hardware | P1 | Test on real hardware by Hour 8 (not later); have a smaller quantized model as fallback |
| Integration surprises at Hour 14 | All | This is exactly why the contract is frozen at Hour 2 and why P3 builds against a mock from the start — if contracts are respected, integration is a wiring exercise, not a redesign |
| Generated file looks unpolished | P3 | Budget real time for this in Hours 14–20 — a scruffy Word doc undercuts the "real deliverable" USP more than any other single flaw |