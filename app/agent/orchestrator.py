from __future__ import annotations

import json
from typing import Any, Literal, Protocol

from app.agent.answers import render_from_activity
from app.agent.errors import LlmProviderError
from app.agent.prompts import build_system_prompt
from app.agent.provider import OpenAiCompatibleProvider, ProviderResponse
from app.agent.router import route_message
from app.config import Settings, get_settings
from app.schemas.chat import ChatResponse, ToolActivity
from app.tools.registry import (
    execute_allowlisted_tool,
    openai_tool_schemas,
    parse_tool_arguments,
)

EMPTY_ANSWER_FALLBACK = (
    "I could not produce an answer from the model. "
    "Try a concrete portfolio question such as how many projects are in the showcase."
)

MAX_STEPS_FALLBACK = (
    "I reached the maximum number of tool steps without a final answer. "
    "Please ask a simpler portfolio analytics question."
)

AnswerSource = Literal["router", "template", "llm"]


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
        self._llm = llm
        self.max_iterations = self.settings.agent_max_tool_iterations

    @property
    def llm(self) -> LlmClient:
        if self._llm is None:
            self._llm = OpenAiCompatibleProvider(self.settings)
        return self._llm

    def run(self, user_message: str) -> ChatResponse:
        cleaned = user_message.strip()
        if not cleaned:
            return ChatResponse(
                answer="Please ask a non-empty analytics question about the portfolio showcase data.",
                tool_activity=[],
                model=self.settings.llm_model,
                iterations=0,
                llm_calls=0,
                answer_source="template",
                is_demo_dataset=None,
            )

        if self.settings.agent_rule_router:
            routed = self._run_router(cleaned)
            if routed is not None:
                return routed

        return self._run_llm_loop(cleaned)

    def _run_router(self, cleaned: str) -> ChatResponse | None:
        decision = route_message(cleaned)
        if decision is None:
            return None

        if decision.kind in {"greeting", "unsupported"}:
            return ChatResponse(
                answer=decision.answer or "",
                tool_activity=[],
                model="rule-router",
                iterations=0,
                llm_calls=0,
                answer_source="router",
                is_demo_dataset=None,
            )

        assert decision.tool_name and decision.arguments is not None
        args_json = json.dumps(decision.arguments)
        result, status, detail = execute_allowlisted_tool(decision.tool_name, args_json)
        activity = [
            ToolActivity(
                tool_name=decision.tool_name,
                status=status,
                detail=detail,
                arguments=decision.arguments,
                result=result,
            )
        ]
        is_demo = (
            result.get("is_demo_dataset")
            if status == "ok" and isinstance(result.get("is_demo_dataset"), bool)
            else None
        )
        answer = render_from_activity(activity) or EMPTY_ANSWER_FALLBACK
        return ChatResponse(
            answer=answer,
            tool_activity=activity,
            model="rule-router",
            iterations=1,
            llm_calls=0,
            answer_source="router",
            is_demo_dataset=is_demo,
        )

    def _run_llm_loop(self, cleaned: str) -> ChatResponse:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": cleaned},
        ]
        tools = openai_tool_schemas()
        activity: list[ToolActivity] = []
        is_demo_dataset: bool | None = None
        iterations = 0
        llm_calls = 0

        for _ in range(self.max_iterations):
            iterations += 1
            try:
                provider_response = self.llm.complete(messages, tools)
            except LlmProviderError:
                raise
            llm_calls += 1

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
                            status=status,
                            detail=detail,
                            arguments=args,
                            result=result,
                        )
                    )
                    if status == "ok" and isinstance(result.get("is_demo_dataset"), bool):
                        is_demo_dataset = result["is_demo_dataset"]

                    content = dict(result)
                    # Only useful when a second LLM turn will read the tool message.
                    if (
                        not self.settings.agent_template_answers
                        and status == "ok"
                        and result.get("has_data") is False
                    ):
                        content["_instruction"] = (
                            "Tool returned no data. Tell the user clearly that the "
                            "showcase dataset has no match. Do not invent numbers."
                        )

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": json.dumps(content),
                        }
                    )

                if self.settings.agent_template_answers:
                    templated = render_from_activity(activity)
                    if templated:
                        return ChatResponse(
                            answer=templated,
                            tool_activity=activity,
                            model=self.llm.model_name,
                            iterations=iterations,
                            llm_calls=llm_calls,
                            answer_source="template",
                            is_demo_dataset=is_demo_dataset,
                        )
                continue

            answer = (provider_response.content or "").strip() or EMPTY_ANSWER_FALLBACK
            return ChatResponse(
                answer=answer,
                tool_activity=activity,
                model=self.llm.model_name,
                iterations=iterations,
                llm_calls=llm_calls,
                answer_source="llm",
                is_demo_dataset=is_demo_dataset,
            )

        if self.settings.agent_template_answers:
            templated = render_from_activity(activity)
            if templated:
                return ChatResponse(
                    answer=templated,
                    tool_activity=activity,
                    model=self.llm.model_name,
                    iterations=iterations,
                    llm_calls=llm_calls,
                    answer_source="template",
                    is_demo_dataset=is_demo_dataset,
                )

        return ChatResponse(
            answer=MAX_STEPS_FALLBACK,
            tool_activity=activity,
            model=self.llm.model_name,
            iterations=iterations,
            llm_calls=llm_calls,
            answer_source="llm",
            is_demo_dataset=is_demo_dataset,
        )
