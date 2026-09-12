import logging
import requests
from typing import Dict, Any, Optional
from ..config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for local, air-gapped Ollama instance."""

    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = OLLAMA_MODEL):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = OLLAMA_TIMEOUT

    def is_available(self) -> bool:
        """Check if local Ollama daemon is reachable."""
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return res.status_code == 200
        except Exception:
            return False

    def get_installed_models(self) -> list:
        """Return list of available local models."""
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=3)
            if res.status_code == 200:
                data = res.json()
                return [m.get("name") for m in data.get("models", [])]
        except Exception as e:
            logger.debug(f"[OllamaClient] Could not fetch models: {e}")
        return []

    def generate(self, prompt: str, system: Optional[str] = None, temperature: float = 0.1) -> Optional[str]:
        """Generate a response using Ollama's /api/generate endpoint."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": 0.9
            }
        }
        if system:
            payload["system"] = system

        try:
            logger.info(f"[OllamaClient] Sending request to {url} with model {self.model}")
            res = requests.post(url, json=payload, timeout=self.timeout)
            if res.status_code == 200:
                data = res.json()
                return data.get("response", "")
            else:
                logger.warning(f"[OllamaClient] Ollama returned status {res.status_code}")
        except requests.exceptions.Timeout:
            logger.warning(f"[OllamaClient] Ollama request timed out after {self.timeout}s.")
        except Exception as e:
            logger.warning(f"[OllamaClient] Ollama error: {e}")

        return None
