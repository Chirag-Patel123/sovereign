"""
Ingestion/Retrieval service — Person 2
Exposes the PRD Section 1.6 contract on localhost:8001:

    POST /ingest   -> { doc_id, status, page_count }
    GET  /search   -> { chunks: [{ chunk_id, text, page, score }] }

This wraps the existing CLI logic in ingestion.py (extract_text, chunk_text,
embedding + similarity search) so Person 1's agent can call it over HTTP
instead of shelling out to the script.

ASSUMPTIONS — adjust these imports/calls to match the real ingestion.py:
  - extract_text(image_path) -> str
  - chunk_text(text, chunk_size=200) -> list[str]
  - There is (or needs to be) a function that embeds a list of chunks and
    returns vectors, e.g. embed_chunks(chunks) -> list[vector]
  - There is (or needs to be) a function that embeds a query and scores it
    against stored chunk embeddings, e.g. search_chunks(query, doc_id, top_k)
      -> list[{text, page, score}]

If ingestion.py only exposes a single "do everything and print the best
match" entrypoint today, it will need to be split into these two halves
(embed+store at ingest time, embed-query+compare at search time) so that
/ingest and /search can be separate calls, since a document is uploaded
once but searched many times.
"""

import os
import uuid
import shutil
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from pydantic import BaseModel

# Real functions confirmed from ingestion.py:
#   extract_text(file_path) -> str
#   chunk_text(text, chunk_size=50) -> list[str]        (default is 50, not 200)
#   embed_chunks(chunks) -> (model, vectors)             (all chunks at once)
#   search(query, model, chunks, chunk_vectors) -> str   (best chunk TEXT only,
#                                                          raw dot-product, no ranking)
try:
    from ingestion import extract_text, chunk_text, embed_chunks
except ImportError:
    extract_text = None
    chunk_text = None
    embed_chunks = None
# -----------------------------------------------------------------

app = FastAPI(title="Sovereign Workbench — Ingestion/Retrieval (Person 2)")

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory store — matches PRD's "SQLite or even a JSON file" guidance,
# swap for real persistence only if time allows.
DOCUMENTS = {}   # doc_id -> {filename, page_count, status}
CHUNKS = {}      # doc_id -> {"records": [{chunk_id, text, page}], "vectors": ndarray}


class IngestResponse(BaseModel):
    doc_id: str
    status: str
    page_count: int


class SearchResult(BaseModel):
    chunk_id: str
    text: str
    page: int
    score: float


class SearchResponse(BaseModel):
    chunks: list[SearchResult]


# One shared model instance across requests (embed_chunks() in ingestion.py
# loads a fresh SentenceTransformer every call — fine for the CLI's one-shot
# use, too slow to repeat on every /search request here).
_MODEL = None


def _get_model():
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _MODEL


def _score_all(query: str, chunk_vectors) -> list:
    """
    Reimplements ingestion.py's search() dot-product logic, but returns
    scores for every chunk (for top_k ranking) instead of just the argmax.
    NOTE: this is a raw dot product, matching the original script exactly —
    not normalized cosine similarity, since chunk_vectors aren't normalized
    there either. Scores are therefore only comparable within one doc_id,
    not across documents.
    """
    model = _get_model()
    query_vector = model.encode([query])[0]
    similarities = chunk_vectors @ query_vector
    return similarities.tolist()


@app.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...)):
    if extract_text is None or chunk_text is None:
        raise HTTPException(
            status_code=500,
            detail="ingestion.py not importable — check it's on PYTHONPATH "
                   "and exposes extract_text() / chunk_text().",
        )

    doc_id = str(uuid.uuid4())[:8]
    save_path = os.path.join(UPLOAD_DIR, f"{doc_id}_{file.filename}")
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        text = extract_text(save_path)
        # Real default in ingestion.py is chunk_size=50 (README says 200 —
        # the README is stale). Using the real default here.
        chunk_list = chunk_text(text)
        _, chunk_vectors = embed_chunks(chunk_list)  # embeds all chunks in one batch
    except Exception as e:
        DOCUMENTS[doc_id] = {"filename": file.filename, "page_count": 0, "status": "error"}
        raise HTTPException(status_code=500, detail=f"OCR/chunking failed: {e}")

    chunk_records = []
    for i, chunk in enumerate(chunk_list):
        chunk_records.append({
            "chunk_id": f"{doc_id}-{i}",
            "text": chunk,
            "page": 1,  # TODO: real page tracking — extract_text() returns one flat string, no page breaks
        })

    CHUNKS[doc_id] = {"records": chunk_records, "vectors": chunk_vectors}
    DOCUMENTS[doc_id] = {
        "filename": file.filename,
        "page_count": 1,  # TODO: real page count from extract_text if available
        "status": "ready",
    }

    return IngestResponse(
        doc_id=doc_id,
        status=DOCUMENTS[doc_id]["status"],
        page_count=DOCUMENTS[doc_id]["page_count"],
    )


@app.get("/search", response_model=SearchResponse)
async def search(doc_id: str, query: str, top_k: int = Query(5)):
    if doc_id not in DOCUMENTS:
        raise HTTPException(status_code=404, detail=f"Unknown doc_id: {doc_id}")
    if DOCUMENTS[doc_id]["status"] != "ready":
        raise HTTPException(status_code=409, detail=f"doc_id {doc_id} not ready yet")

    doc_chunks = CHUNKS.get(doc_id, {"records": [], "vectors": None})
    records = doc_chunks["records"]
    vectors = doc_chunks["vectors"]

    if not records or vectors is None:
        return SearchResponse(chunks=[])

    scores = _score_all(query, vectors)
    scored = [
        {**rec, "score": scores[i]}
        for i, rec in enumerate(records)
    ]
    scored.sort(key=lambda x: x["score"], reverse=True)
    return SearchResponse(chunks=[SearchResult(**s) for s in scored[:top_k]])


@app.get("/health")
async def health():
    return {"status": "ok", "documents_loaded": len(DOCUMENTS)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)