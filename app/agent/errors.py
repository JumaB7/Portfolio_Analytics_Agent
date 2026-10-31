from __future__ import annotations

import json
from typing import Any


class LlmProviderError(Exception):
    """Raised when the hosted LLM API fails or returns an unexpected payload."""

    def __init__(self, message: str, *, code: str = "llm_error") -> None:
        super().__init__(message)
        self.code = code
        self.message = message

    def as_http_detail(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


def classify_llm_http_error(status_code: int, body_text: str) -> LlmProviderError:
    """Map provider HTTP failures to stable codes and user-safe messages."""
    lowered = body_text.lower()
    payload: dict[str, Any] = {}
    try:
        payload = json.loads(body_text)
    except json.JSONDecodeError:
        payload = {}

    error_obj = payload.get("error") if isinstance(payload, dict) else None
    provider_code = ""
    provider_message = ""
    if isinstance(error_obj, dict):
        provider_code = str(error_obj.get("code") or "")
        provider_message = str(error_obj.get("message") or "")

    if status_code in {401, 403}:
        return LlmProviderError(
            "The LLM API rejected the API key. Check LLM_API_KEY in .env and restart the API.",
            code="llm_auth_failed",
        )

    if status_code == 429 or "insufficient_quota" in lowered or "credit_balance" in lowered:
        return LlmProviderError(
            "The LLM provider reports no credits remaining (or rate limit exceeded). "
            "Add billing credits or wait, then retry.",
            code="llm_quota_exhausted",
        )

    if status_code == 404:
        return LlmProviderError(
            "The LLM endpoint or model was not found. Check LLM_BASE_URL and LLM_MODEL.",
            code="llm_not_found",
        )

    if status_code >= 500:
        return LlmProviderError(
            "The LLM provider is temporarily unavailable. Try again shortly.",
            code="llm_unavailable",
        )

    snippet = (provider_message or body_text or "Unknown provider error")[:300]
    code = provider_code or "llm_http_error"
    return LlmProviderError(
        f"LLM API returned HTTP {status_code}: {snippet}",
        code=code if code.isidentifier() or "_" in code else "llm_http_error",
    )
