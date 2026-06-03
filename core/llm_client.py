import json
import logging
import os
import re
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)


class OllamaClient:
    DEFAULT_API_BASE = "http://127.0.0.1:11434"
    DEFAULT_MODEL = "llama-3"

    def __init__(self, model: Optional[str] = None, api_base: Optional[str] = None, timeout: int = 30):
        self.model = model or os.environ.get("OLLAMA_MODEL", self.DEFAULT_MODEL)
        self.api_base = (api_base or os.environ.get("OLLAMA_API_BASE", self.DEFAULT_API_BASE)).rstrip("/")
        self.timeout = timeout
        logger.info("OllamaClient configured for model=%s api_base=%s", self.model, self.api_base)

    def query(self, messages: List[Dict[str, str]]) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
        }
        try:
            response = self._request(payload)
            return self._parse_response(response)
        except Exception as exc:
            logger.exception("Ollama query failed: %s", exc)
            return self._fallback_response(messages)

    def _request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = urljoin(self.api_base + "/", "v1/chat/completions")
        data = json.dumps(payload).encode("utf-8")
        request = Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            logger.error("Ollama HTTP error %s: %s", exc.code, exc.reason)
            raise
        except URLError as exc:
            logger.error("Ollama connection failed: %s", exc.reason)
            raise

    def _parse_response(self, response: Dict[str, Any]) -> str:
        if not isinstance(response, dict):
            return str(response)

        choices = response.get("choices")
        if isinstance(choices, list) and choices:
            choice = choices[0]
            if isinstance(choice, dict):
                message = choice.get("message")
                if isinstance(message, dict) and isinstance(message.get("content"), str):
                    return message["content"].strip()
                if isinstance(choice.get("content"), str):
                    return choice["content"].strip()
                if isinstance(choice.get("output"), list) and choice["output"]:
                    first_output = choice["output"][0]
                    if isinstance(first_output, dict) and isinstance(first_output.get("content"), str):
                        return first_output["content"].strip()
        if isinstance(response.get("output"), list) and response["output"]:
            first_output = response["output"][0]
            if isinstance(first_output, dict) and isinstance(first_output.get("content"), str):
                return first_output["content"].strip()

        raw = json.dumps(response)
        text_match = re.search(r"\{.*\}", raw, re.DOTALL)
        return text_match.group(0) if text_match else raw

    def _fallback_response(self, messages: List[Dict[str, str]]) -> str:
        last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        fallback = (
            "I could not reach the Ollama model. "
            "Please ensure Ollama is running and the OLLAMA_API_BASE is configured. "
            f"You asked: {last_user}"
        )
        logger.debug("Using fallback response for user request.")
        return fallback
