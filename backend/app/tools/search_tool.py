import logging
import requests
from typing import Dict, Any, List
from .base import BaseTool
from ..config import INGESTION_SERVICE_URL, MOCK_INGESTION
from ..mocks.mock_chunks import get_mock_chunks

logger = logging.getLogger(__name__)

class SearchTool(BaseTool):
    """
    Search / Retrieval tool.
    In Hour 2-8 (or when MOCK_INGESTION is True), uses realistic pre-configured
    MRPL refinery standard chunks.
    In Hour 8+ (when Person 2's service is running), queries localhost:8001/search.
    """
    
    @property
    def name(self) -> str:
        return "search"

    @property
    def description(self) -> str:
        return (
            "Searches and retrieves relevant grounded chunks from an ingested document "
            "using semantic retrieval. Arguments: doc_id (str), query (str), top_k (int, optional)."
        )

    def run(self, doc_id: str, query: str = "", top_k: int = 5, **kwargs) -> Dict[str, Any]:
        """Execute search against mock or live Ingestion service."""
        # 1. If mock ingestion is explicitly enabled, return mock data immediately
        if MOCK_INGESTION:
            logger.info(f"[SearchTool] Running in MOCK mode for doc_id='{doc_id}'")
            chunks = get_mock_chunks(doc_id, query, top_k)
            return {"chunks": chunks, "mode": "mock"}

        # 2. Live HTTP call to Person 2 (localhost:8001/search)
        url = f"{INGESTION_SERVICE_URL}/search"
        params = {"doc_id": doc_id, "query": query, "top_k": top_k}
        try:
            logger.info(f"[SearchTool] Querying live Ingestion service at {url}")
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                chunks = data.get("chunks", [])
                return {"chunks": chunks, "mode": "live"}
            else:
                logger.warning(f"[SearchTool] Ingestion service returned {response.status_code}. Falling back to mock chunks.")
        except Exception as e:
            logger.warning(f"[SearchTool] Could not connect to live Ingestion service ({e}). Falling back to mock chunks.")

        # Graceful fallback to guarantee demo resilience
        chunks = get_mock_chunks(doc_id, query, top_k)
        return {"chunks": chunks, "mode": "fallback"}
