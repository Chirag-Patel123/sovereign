"""
Drop-in replacement for the search_documents tool in tools.py.
Calls Person 2's live ingestion/retrieval API (localhost:8001) over HTTP
instead of importing ingestion functions directly in-process.

SETUP REQUIRED (one-time, at agent startup):
  You must first POST each sample document to /ingest and remember its
  doc_id. See `ingest_startup_docs()` below — call this once when your
  agent process starts, before any /search calls.
"""

import requests

INGESTION_API_URL = "http://localhost:8001"

# Populated at startup by ingest_startup_docs() -- maps a friendly name
# to the doc_id the ingestion API returned for it.
_DOC_IDS: dict[str, str] = {}


def ingest_startup_docs(doc_paths: list[str]) -> dict[str, str]:
    """
    Call once when the agent starts up. Uploads each sample document to
    the ingestion API and stores the returned doc_id for later searches.
    Returns the name -> doc_id mapping (also cached in _DOC_IDS).
    """
    global _DOC_IDS
    for path in doc_paths:
        with open(path, "rb") as f:
            response = requests.post(
                f"{INGESTION_API_URL}/ingest",
                files={"file": f},
                timeout=60,
            )
        response.raise_for_status()
        data = response.json()
        _DOC_IDS[path] = data["doc_id"]
        print(f"Ingested {path} -> doc_id={data['doc_id']}")
    return _DOC_IDS


def search_documents(query: str, top_k: int = 3) -> str:
    """
    Tool fn for the agent. Searches ACROSS all ingested documents (loops
    over every doc_id) and returns the combined top matches as a single
    string, since the agent's tool contract expects one string result.

    NOTE: scores are only comparable within one doc_id (see app.py's own
    docstring) -- so when searching across multiple docs, this takes the
    top_k from EACH doc rather than trying to merge scores across docs.
    Good enough for a 3-5 document demo; revisit if you add many more docs.
    """
    if not _DOC_IDS:
        return "ERROR: no documents ingested yet — call ingest_startup_docs() first"

    all_results = []
    for doc_name, doc_id in _DOC_IDS.items():
        try:
            response = requests.get(
                f"{INGESTION_API_URL}/search",
                params={"doc_id": doc_id, "query": query, "top_k": top_k},
                timeout=30,
            )
            response.raise_for_status()
            chunks = response.json()["chunks"]
            for c in chunks:
                all_results.append(f"[{doc_name}] {c['text']}")
        except requests.RequestException as e:
            all_results.append(f"[{doc_name}] ERROR: {e}")

    if not all_results:
        return "No matching chunks found."

    return "\n---\n".join(all_results)


# Same spec shape as the original SEARCH_DOCUMENTS_SPEC in tools.py --
# swap this in place of the old one when registering tools.
SEARCH_DOCUMENTS_SPEC = dict(
    name="search_documents",
    description="Search the organization's internal standards/manuals for relevant passages.",
    parameters={"query": {"type": "string", "description": "What to search for"}},
    required=["query"],
    fn=search_documents,
)


if __name__ == "__main__":
    # Quick manual test -- run this file directly to check the API connection
    ingest_startup_docs([
        "sample_internal_standard.png",
        "sample_inspection_report.png",
        "sample_scanned_note.png",
    ])
    print("\n--- test search ---")
    print(search_documents("what is the max pressure allowed?"))
