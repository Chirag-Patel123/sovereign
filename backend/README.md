# Sovereign AI Workbench — Backend & Agent Service (Person 1)

This service serves as the central brain and orchestrator of the **Sovereign On-Premise Agentic AI Workbench (MRPL)**. It is owned by **Person 1** and runs completely air-gapped on `localhost:8000`.

---

## 🎯 Architecture & Responsibilities

- **Single Orchestrator:** Person 3 (UI) sends inquiries to `POST /agent/query`. The Agent plans and executes a 3-tool chain:
  1. `search`: Retrieves grounded internal standard passages from Person 2 (`localhost:8001/search`) or local mock data.
  2. `calculate`: Executes ASME B31.3 Barlow wall thickness formulas and commercial schedule recommendations.
  3. `write_file`: Generates an official, corporate-grade `.docx` Technical Approval Note saved to `./outputs`.
- **API Contracts (PRD Section 1.6 Compliant):**
  - `POST /agent/query` → `{ "answer": "...", "tool_trace": [...], "file_url": "..." }`
  - `GET /files/{filename}` → Downloads generated `.docx` / `.xlsx` files
  - `GET /health` → Service status, Groq API availability, mock ingestion flag

---

## 🚀 Quickstart

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Start the Backend Service
```bash
python backend/run.py
```
The server will start on **http://localhost:8000** with interactive Swagger API docs available at **http://localhost:8000/docs**.

---

## 🧪 Running Tests

Run the automated unit and integration tests:
```bash
pytest backend/tests/ -v
```

---

## 🔄 Integration with Other Tracks

### For Person 2 (Ingestion / Retrieval — `localhost:8001`):
- During Hour 2–8: Person 1 operates with `MOCK_INGESTION=true` (default).
- At Hour 8 Sync: Set environment variable `MOCK_INGESTION=false` to route searches to `http://localhost:8001/search?doc_id={id}&query={text}&top_k=5`.
- If the Ingestion service is temporarily unavailable, the search tool gracefully falls back to cached standards to ensure demo stability.

### For Person 3 (UI — React / Vite / Streamlit):
- Point your chat input to: `POST http://localhost:8000/agent/query`
- JSON Body:
  ```json
  {
    "doc_id": "MRPL-STD-PIPE-2024",
    "query": "Review pipe standard, calculate minimum wall thickness, and generate approval note."
  }
  ```
- Render the `answer`, render the `tool_trace` in the "Show Work" drawer, and provide a download button pointing to `file_url`.
