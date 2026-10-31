from __future__ import annotations

import json
from typing import Any, Protocol

from app.agent.errors import LlmProviderError
from app.agent.prompts import build_system_prompt
from app.agent.provider import OpenAiCompatibleProvider, ProviderResponse
from app.config import Settings, get_settings
from app.schemas.chat import ChatResponse, ToolActivity
from app.tools.registry import (
    execute_allowlisted_tool,
    openai_tool_schemas,
    parse_tool_arguments,
)

EMPTY_ANSWER_FALLBACK = (
    "I could not produce an answer from the model. "
    "Try a concrete sales question such as total revenue for last month."
)

MAX_STEPS_FALLBACK = (
    "I reached the maximum number of tool steps without a final answer. "
    "Please ask a simpler analytics question for a single date range."
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
        cleaned = user_message.strip()
        if not cleaned:
            return ChatResponse(
                answer="Please ask a non-empty analytics question about the demo sales data.",
                tool_activity=[],
                model=self.llm.model_name,
                iterations=0,
                is_demo_dataset=None,
            )

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": cleaned},
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

                    # Reinforce empty-data honesty for the next model turn.
                    content = dict(result)
                    if status == "ok" and result.get("has_data") is False:
                        content["_instruction"] = (
                            "Tool returned no data. Tell the user clearly that the demo "
                            "dataset has no sales for this period. Do not invent numbers."
                        )

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": json.dumps(content),
                        }
                    )
                continue

            answer = (provider_response.content or "").strip() or EMPTY_ANSWER_FALLBACK
            return ChatResponse(
                answer=answer,
                tool_activity=activity,
                model=self.llm.model_name,
                iterations=iterations,
                is_demo_dataset=is_demo_dataset,
            )

        return ChatResponse(
            answer=MAX_STEPS_FALLBACK,
            tool_activity=activity,
            model=self.llm.model_name,
            iterations=iterations,
            is_demo_dataset=is_demo_dataset,
        )
