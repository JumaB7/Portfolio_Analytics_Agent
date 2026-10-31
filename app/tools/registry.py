from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ValidationError

from app.schemas.tools import SalesSummaryInput
from app.tools.sales import TOOL_DEFINITIONS, get_sales_summary_tool

ToolHandler = Callable[[BaseModel], BaseModel]

_HANDLERS: dict[str, tuple[type[BaseModel], ToolHandler]] = {
    "get_sales_summary": (SalesSummaryInput, get_sales_summary_tool),
}


def openai_tool_schemas() -> list[dict[str, Any]]:
    """OpenAI-compatible tool definitions derived from allowlisted tools only."""
    schemas: list[dict[str, Any]] = []
    for definition in TOOL_DEFINITIONS:
        name = definition["name"]
        if name not in _HANDLERS:
            continue
        parameters_model: type[BaseModel] = definition["parameters_model"]
        schemas.append(
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": definition["description"],
                    "parameters": parameters_model.model_json_schema(),
                },
            }
        )
    return schemas


def execute_allowlisted_tool(
    name: str, arguments_json: str
) -> tuple[dict[str, Any], str, str]:
    """Validate and execute an allowlisted tool.

    Returns (result_dict, status, detail).
    status is ok | error | rejected.
    """
    if name not in _HANDLERS:
        return (
            {"error": f"Tool '{name}' is not allowlisted."},
            "rejected",
            f"Rejected unknown tool '{name}'",
        )

    parameters_model, handler = _HANDLERS[name]
    try:
        raw_args = json.loads(arguments_json or "{}")
    except json.JSONDecodeError:
        return (
            {"error": "Tool arguments were not valid JSON."},
            "error",
            "Invalid JSON arguments",
        )

    try:
        params = parameters_model.model_validate(raw_args)
    except ValidationError as exc:
        return (
            {"error": "Tool argument validation failed.", "details": exc.errors()},
            "error",
            "Argument validation failed",
        )

    try:
        result = handler(params)
    except Exception as exc:  # noqa: BLE001 - surfaced to model as tool error payload
        return (
            {"error": f"Tool execution failed: {exc}"},
            "error",
            "Tool execution failed",
        )

    return result.model_dump(mode="json"), "ok", "Tool completed successfully"


def parse_tool_arguments(arguments_json: str) -> dict[str, Any] | None:
    try:
        value = json.loads(arguments_json or "{}")
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None
