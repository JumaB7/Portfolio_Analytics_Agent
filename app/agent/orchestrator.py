from __future__ import annotations

import json
from typing import Any, Protocol

from app.agent.prompts import build_system_prompt
from app.agent.provider import LlmProviderError, OpenAiCompatibleProvider, ProviderResponse
from app.config import Settings, get_settings
from app.schemas.chat import ChatResponse, ToolActivity
from app.tools.registry import (
    execute_allowlisted_tool,
    openai_tool_schemas,
    parse_tool_arguments,
)


class LlmClient(Protocol):
    @property
    def model_name(self) -> str: ...

    def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> ProviderResponse: ...


class AgentOrchestrator:
    """Bounded tool-calling loop. Backend validates and executes tools."""

    def __init__(
        self,
        settings: Settings | None = None,
        llm: LlmClient | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.llm = llm or OpenAiCompatibleProvider(self.settings)
        self.max_iterations = self.settings.agent_max_tool_iterations

    def run(self, user_message: str) -> ChatResponse:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": user_message.strip()},
        ]
        tools = openai_tool_schemas()
        activity: list[ToolActivity] = []
        is_demo_dataset: bool | None = None
        iterations = 0

        for _ in range(self.max_iterations):
            iterations += 1
            try:
                provider_response = self.llm.complete(messages, tools)
            except LlmProviderError:
                raise

            if provider_response.tool_calls:
                messages.append(provider_response.raw_message)
                for call in provider_response.tool_calls:
                    args = parse_tool_arguments(call.arguments_json)
                    result, status, detail = execute_allowlisted_tool(
                        call.name, call.arguments_json
                    )
                    activity.append(
                        ToolActivity(
                            tool_name=call.name or "(missing)",
                            status=status,  # type: ignore[arg-type]
                            detail=detail,
                            arguments=args,
                            result=result,
                        )
                    )
                    if status == "ok" and isinstance(result.get("is_demo_dataset"), bool):
                        is_demo_dataset = result["is_demo_dataset"]

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": json.dumps(result),
                        }
                    )
                continue

            answer = (provider_response.content or "").strip()
            if not answer:
                answer = (
                    "I could not produce an answer from the model. "
                    "Try asking about total sales for a specific month."
                )
            return ChatResponse(
                answer=answer,
                tool_activity=activity,
                model=self.llm.model_name,
                iterations=iterations,
                is_demo_dataset=is_demo_dataset,
            )

        return ChatResponse(
            answer=(
                "I reached the maximum number of tool steps without a final answer. "
                "Please ask a simpler sales question for a single date range."
            ),
            tool_activity=activity,
            model=self.llm.model_name,
            iterations=iterations,
            is_demo_dataset=is_demo_dataset,
        )
