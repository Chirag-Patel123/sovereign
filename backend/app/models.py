from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Contract: POST /agent/query request
class AgentQueryRequest(BaseModel):
    doc_id: str = Field(..., description="Document identifier to ground the inquiry")
    query: str = Field(..., description="User question or engineering task")

# Contract: Individual step in tool_trace
class ToolTraceItem(BaseModel):
    tool: str = Field(..., description="Name of the tool: search | calculate | write_file")
    input: Dict[str, Any] = Field(default_factory=dict, description="Arguments passed to the tool")
    output: Dict[str, Any] = Field(default_factory=dict, description="Result returned by the tool")

# Contract: POST /agent/query response
class AgentQueryResponse(BaseModel):
    answer: str = Field(..., description="Final synthesized natural language explanation")
    tool_trace: List[ToolTraceItem] = Field(default_factory=list, description="Ordered trace of executed tools")
    file_url: Optional[str] = Field(default=None, description="Download URL if write_file was executed")

# Contract: P2 Ingestion chunk
class SearchChunk(BaseModel):
    chunk_id: str
    text: str
    page: int
    score: float = 0.0

# Contract: P2 GET /search response
class SearchResponse(BaseModel):
    chunks: List[SearchChunk] = Field(default_factory=list)

# Healthcheck response
class HealthResponse(BaseModel):
    status: str
    ollama_connected: bool
    mock_ingestion: bool
    service: str = "Sovereign Backend / Agent"
