"""Load the shared portfolio analytics dataset from PortfolioAPI (or local seed)."""

from __future__ import annotations

from typing import Any

import httpx

from app.config import get_settings
from app.data.portfolio_seed import create_portfolio_seed


def load_portfolio_dataset() -> dict[str, Any]:
    """Prefer PortfolioAPI so the agent and dashboard share one source of truth."""
    settings = get_settings()
    base = (settings.portfolio_api_base_url or "").rstrip("/")
    if base:
        url = f"{base}/api/dashboard/analytics"
        try:
            with httpx.Client(timeout=settings.portfolio_api_timeout_seconds) as client:
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                if isinstance(data, dict) and data.get("projects") is not None:
                    data.setdefault("isDemoDataset", True)
                    data["_source"] = "portfolio_api"
                    return data
        except Exception:  # noqa: BLE001 - fall back to seed for local demos
            pass

    seed = create_portfolio_seed()
    seed["isDemoDataset"] = True
    seed["_source"] = "local_seed"
    return seed
