import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "endpoints" in data

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "ollama_connected" in data
    assert "mock_ingestion" in data

def test_agent_query_and_download_flow():
    payload = {
        "doc_id": "MRPL-STD-PIPE-2024",
        "query": "Review the high pressure line standard, compute the required wall thickness for 15 MPa, and draft an approval note."
    }
    response = client.post("/agent/query", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Verify API contract keys strictly match PRD Section 1.6
    assert "answer" in data
    assert "tool_trace" in data
    assert "file_url" in data

    assert len(data["answer"]) > 20
    assert len(data["tool_trace"]) >= 2

    # Check tools executed in sequence
    tools_called = [step["tool"] for step in data["tool_trace"]]
    assert "search" in tools_called
    assert "calculate" in tools_called
    assert "write_file" in tools_called

    # Verify file was generated and is downloadable
    file_url = data["file_url"]
    assert file_url is not None
    filename = file_url.split("/")[-1]

    file_res = client.get(f"/files/{filename}")
    assert file_res.status_code == 200
    assert "wordprocessingml" in file_res.headers.get("content-type", "")
    assert len(file_res.content) > 1000 # Valid non-empty binary docx
