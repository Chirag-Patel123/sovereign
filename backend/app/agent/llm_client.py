import logging
from typing import Optional
from ..config import GROQ_API_KEY, GROQ_MODEL, GROQ_TIMEOUT

logger = logging.getLogger(__name__)

# NOTE: switching to Groq means this service is no longer air-gapped —
# it makes a real outbound HTTPS call to api.groq.com on every /agent/query
# that reaches synthesis. PRD NFR1 ("no external network call once the
# demo begins") no longer holds with this client in place. If the
# air-gapped/"pull the cable" demo moment comes back, this needs to be
# swapped back to an Ollama-based client — that swap is intentionally
# trivial since GroqClient exposes the same is_available()/generate()
# interface orchestrator.py already calls.

try:
    from groq import Groq
except ImportError:
    Groq = None


class GroqClient:
    """Client for Groq's hosted LLM API. Same interface as the old
    OllamaClient (is_available(), generate()) so orchestrator.py needs
    no changes."""

    def __init__(self, api_key: str = GROQ_API_KEY, model: str = GROQ_MODEL):
        self.api_key = api_key
        self.model = model
        self.timeout = GROQ_TIMEOUT
        self._client = None
        if Groq is not None and self.api_key:
            self._client = Groq(api_key=self.api_key, timeout=self.timeout)

    def is_available(self) -> bool:
        """Cheap reachability/config check — a real API key is set and the
        SDK is importable. Does not make a network call on every health
        check; generate() will surface actual API failures per-request."""
        if Groq is None:
            logger.warning("[GroqClient] groq package not installed.")
            return False
        if not self.api_key:
            logger.warning("[GroqClient] GROQ_API_KEY is not set.")
            return False
        return True

    def get_installed_models(self) -> list:
        """Kept for interface parity with the old client. Groq has no
        local install step — this just reports the configured model."""
        return [self.model] if self.is_available() else []

    def generate(self, prompt: str, system: Optional[str] = None, temperature: float = 0.1) -> Optional[str]:
        """Generate a response via Groq's chat completions API."""
        if not self.is_available():
            return None

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        try:
            logger.info(f"[GroqClient] Sending request to Groq with model {self.model}")
            completion = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                timeout=self.timeout,
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.warning(f"[GroqClient] Groq API error: {e}")
            return None

