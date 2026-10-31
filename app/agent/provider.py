from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from app.agent.errors import LlmProviderError, classify_llm_http_error
from app.config import Settings


@dataclass
class ToolCallRequest:
    id: str
    name: str
    arguments_json: str


@dataclass
class ProviderResponse:
    content: str | None
    tool_calls: list[ToolCallRequest]
    raw_message: dict[str, Any]


class OpenAiCompatibleProvider:
    """Thin adapter over an OpenAI-compatible Chat Completions API."""

    def __init__(self, settings: Settings) -> None:
        if not settings.llm_api_key:
            raise LlmProviderError(
                "LLM_API_KEY is not configured. Add it to your .env file and restart the API.",
                code="llm_not_configured",
            )
        self._api_key = settings.llm_api_key
        self._base_url = (settings.llm_base_url or "https://api.openai.com/v1").rstrip(
            "/"
        )
        self._model = settings.llm_model
        self._timeout = settings.llm_timeout_seconds

    @property
    def model_name(self) -> str:
        return self._model

    def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> ProviderResponse:
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self._base_url}/chat/completions"

        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(url, headers=headers, json=payload)
        except httpx.TimeoutException as exc:
            raise LlmProviderError(
                "The LLM request timed out. Try again, or increase LLM_TIMEOUT_SECONDS.",
                code="llm_timeout",
            ) from exc
        except httpx.HTTPError as exc:
            raise LlmProviderError(
                "Could not reach the LLM provider. Check your network and LLM_BASE_URL.",
                code="llm_unreachable",
            ) from exc

        if response.status_code >= 400:
            raise classify_llm_http_error(response.status_code, response.text)

        data = response.json()
        try:
            message = data["choices"][0]["message"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LlmProviderError(
                "LLM API response was missing choices/message.",
                code="llm_bad_response",
            ) from exc

        tool_calls: list[ToolCallRequest] = []
        for call in message.get("tool_calls") or []:
            function = call.get("function") or {}
            tool_calls.append(
                ToolCallRequest(
                    id=str(call.get("id") or ""),
                    name=str(function.get("name") or ""),
                    arguments_json=str(function.get("arguments") or "{}"),
                )
            )

        content = message.get("content")
        return ProviderResponse(
            content=content if isinstance(content, str) else None,
            tool_calls=tool_calls,
            raw_message=message,
        )
