import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = os.getenv("OUTPUTS_DIR", str(BASE_DIR / "outputs"))

# Ensure outputs directory exists
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# Server settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Person 2 (Ingestion / Retrieval Service)
INGESTION_SERVICE_URL = os.getenv("INGESTION_SERVICE_URL", "http://localhost:8001")
# In Hour 2-8, default to True so P1 works without P2 being up yet
MOCK_INGESTION = os.getenv("MOCK_INGESTION", "true").lower() in ("1", "true", "yes")

# Ollama local LLM settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
# Default model: small/fast model preferred on CPU, fallback to llama2:latest
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "45"))

# Base URL used for downloadable generated files
BASE_FILE_URL = os.getenv("BASE_FILE_URL", f"http://localhost:{PORT}/files")

# Deterministic demo fallback (per NFR4 - guaranteed consistency on rehearsed queries)
ENABLE_DEMO_DETERMINISTIC_PATH = os.getenv("ENABLE_DEMO_DETERMINISTIC_PATH", "true").lower() in ("1", "true", "yes")
