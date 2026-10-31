from fastapi import APIRouter, HTTPException

from app.agent.errors import LlmProviderError
from app.agent.orchestrator import AgentOrchestrator
from app.config import get_settings
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Run one bounded agent turn: optional tool calls, then a grounded answer.

    Common demo prompts can be answered by the rule router with zero LLM calls
    (no API key required). Ambiguous prompts still need LLM_API_KEY.
    """
    settings = get_settings()
    try:
        return AgentOrchestrator(settings=settings).run(request.message)
    except LlmProviderError as exc:
        status = 503 if exc.code in {
            "llm_not_configured",
            "llm_quota_exhausted",
        } else 502
        raise HTTPException(status_code=status, detail=exc.as_http_detail()) from exc
