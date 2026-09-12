import os
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from .config import HOST, PORT, OUTPUTS_DIR, MOCK_INGESTION
from .models import AgentQueryRequest, AgentQueryResponse, HealthResponse
from .agent.orchestrator import AgentOrchestrator
from .agent.llm_client import GroqClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("sovereign_backend")

app = FastAPI(
    title="Sovereign AI Workbench — Backend & Agent Service",
    description="Person 1 Backend/Agent service providing offline multi-step reasoning, retrieval, and .docx generation for MRPL industrial engineering workflows.",
    version="1.0.0"
)

# Enable CORS for UI integration (Person 3)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent orchestrator and Groq LLM client
orchestrator = AgentOrchestrator()
llm_client = GroqClient()

@app.get("/", summary="Root index")
def index():
    return {
        "service": "Sovereign AI Workbench — Backend & Agent API",
        "owner": "Person 1 (Backend/Agent)",
        "status": "operational",
        "endpoints": {
            "query": "POST /agent/query",
            "files": "GET /files/{filename}",
            "health": "GET /health",
            "docs": "GET /docs"
        }
    }

@app.get("/health", response_model=HealthResponse, summary="System Health & Integration Status")
def health_check():
    groq_ok = llm_client.is_available()
    return HealthResponse(
        status="healthy",
        groq_connected=groq_ok,
        mock_ingestion=MOCK_INGESTION,
        service="Sovereign Backend / Agent (Person 1)"
    )

@app.post("/agent/query", response_model=AgentQueryResponse, summary="Execute multi-step Agent query")
def query_agent(request: AgentQueryRequest):
    """
    Contract:
    body: { "doc_id": "string", "query": "string" }
    returns: {
      "answer": "string",
      "tool_trace": [ { "tool": "search|calculate|write_file", "input": {}, "output": {} } ],
      "file_url": "string | null"
    }
    """
    logger.info(f"[POST /agent/query] Received query for doc_id='{request.doc_id}': '{request.query}'")
    try:
        response = orchestrator.run(doc_id=request.doc_id, query=request.query)
        return response
    except Exception as e:
        logger.error(f"[POST /agent/query] Error during agent execution: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failure: {str(e)}"
        )

@app.get("/files/{filename}", summary="Download generated engineering reports")
def download_file(filename: str):
    """
    Contract:
    GET /files/{filename}
    returns: the generated .docx/.xlsx file for download
    """
    # Prevent directory traversal attacks
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(OUTPUTS_DIR, safe_filename)

    if not os.path.exists(file_path):
        logger.warning(f"[GET /files/{filename}] File not found at path: {file_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{safe_filename}' not found."
        )

    # Determine media type based on extension
    media_type = "application/octet-stream"
    if safe_filename.endswith(".docx"):
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif safe_filename.endswith(".xlsx"):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif safe_filename.endswith(".pdf"):
        media_type = "application/pdf"

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=safe_filename,
        headers={"Content-Disposition": f'attachment; filename="{safe_filename}"'}
    )
