import os
import pytest
from docx import Document
from app.tools.search_tool import SearchTool
from app.tools.calculate_tool import CalculateTool
from app.tools.file_tool import WriteFileTool

def test_search_tool_mock():
    tool = SearchTool()
    result = tool.run(doc_id="MRPL-STD-PIPE-2024", query="wall thickness criteria")
    assert "chunks" in result
    chunks = result["chunks"]
    assert len(chunks) > 0
    first_chunk = chunks[0]
    assert "chunk_id" in first_chunk
    assert "text" in first_chunk
    assert "page" in first_chunk
    assert first_chunk["page"] >= 1
    assert "MRPL" in first_chunk["text"]

def test_calculate_tool_pipe_thickness():
    tool = CalculateTool()
    res = tool.run(
        calculation_type="pipe_wall_thickness",
        parameters={
            "P": 15.0,
            "D": 219.1,
            "S": 120.0,
            "E": 1.0,
            "Y": 0.4,
            "c": 3.0
        }
    )
    assert res["status"] == "success"
    assert "formula" in res
    assert "results" in res
    results = res["results"]
    assert results["minimum_required_thickness_tm_mm"] > 10.0
    assert results["recommended_commercial_schedule"] in ("Sch 120", "Sch 160", "Schedule 120")
    assert results["safety_margin_percent"] > 0

def test_write_file_tool():
    tool = WriteFileTool()
    res = tool.run(
        title="Test Technical Approval Note",
        summary="Automated verification test for docx generator",
        calculation_data={
            "formula": "t_m = [P * D] / [2 * (S * E + P * Y)] + c",
            "inputs": {"P": 15.0, "D": 219.1, "S": 120.0},
            "results": {
                "minimum_required_thickness_tm_mm": 15.82,
                "nominal_thickness_with_tolerance_mm": 18.08,
                "recommended_commercial_schedule": "Schedule 120",
                "schedule_nominal_thickness_mm": 18.26,
                "safety_margin_percent": 14.2
            }
        },
        grounded_sources=[
            {"chunk_id": "chk-001", "page": 1, "text": "MRPL Engineering Standard ES-401 Rev 4"}
        ],
        doc_id="MRPL-TEST-001"
    )
    assert res["status"] == "success"
    assert "file_path" in res
    assert os.path.exists(res["file_path"])
    assert res["file_url"].startswith("http")
    assert res["filename"].endswith(".docx")

    # Verify docx file integrity
    doc = Document(res["file_path"])
    text_content = " ".join([p.text for p in doc.paragraphs])
    assert "MANGALORE REFINERY AND PETROCHEMICALS LIMITED" in text_content
