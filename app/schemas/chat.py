from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    # Reserved for later conversation persistence; ignored in this milestone.
    session_id: str | None = None


class ToolActivity(BaseModel):
    tool_name: str
    status: Literal["ok", "error", "rejected"]
    detail: str | None = None
    arguments: dict[str, Any] | None = None
    result: dict[str, Any] | None = None


class ChatResponse(BaseModel):
    answer: str
    tool_activity: list[ToolActivity] = Field(default_factory=list)
    model: str
    iterations: int
    llm_calls: int = Field(
        default=0,
        description="How many hosted LLM requests this turn used (0 when rule-routed).",
    )
    answer_source: Literal["router", "template", "llm"] = Field(
        default="llm",
        description="router=no LLM; template=LLM chose tool then Python answered; llm=model wrote text",
    )
    is_demo_dataset: bool | None = None
