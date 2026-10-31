from fastapi import APIRouter, HTTPException

from app.agent.orchestrator import AgentOrchestrator
from app.agent.provider import LlmProviderError
from app.config import get_settings
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Run one bounded agent turn: optional tool calls, then a grounded answer."""
    settings = get_settings()
    if not settings.llm_api_key:
        raise HTTPException(
            status_code=503,
            detail=(
                "LLM_API_KEY is not set. Add your provider key to .env, "
                "restart the API, then retry."
            ),
        )

    try:
        return AgentOrchestrator(settings=settings).run(request.message)
    except LlmProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
