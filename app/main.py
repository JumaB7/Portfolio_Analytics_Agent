from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.tools import router as tools_router
from app.config import get_settings
from app.schemas.health import HealthResponse

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "Bounded AI data analyst agent over the portfolio showcase analytics dataset "
        "shared with the Highcharts dashboard. Demo data only — not production client data."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tools_router, prefix=settings.api_prefix)
app.include_router(chat_router, prefix=settings.api_prefix)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    """Liveness check for local development and deployment probes."""
    return HealthResponse(
        status="ok",
        app=settings.app_name,
        environment=settings.app_env,
    )


@app.get(f"{settings.api_prefix}/health", response_model=HealthResponse, tags=["system"])
def api_health() -> HealthResponse:
    """Same health payload under the API prefix used by the frontend."""
    return health()
