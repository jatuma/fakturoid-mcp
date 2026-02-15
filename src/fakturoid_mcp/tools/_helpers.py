"""Shared utility functions for MCP tools."""

import json
from datetime import date, datetime
from decimal import Decimal

from mcp.server.fastmcp import Context


def get_client(ctx: Context):
    """Extract Fakturoid client from MCP context."""
    return ctx.request_context.lifespan_context.client


def model_to_dict(model) -> dict:
    """Serialize a Fakturoid model to a JSON-safe dict.

    Handles Decimal, date, datetime types and filters internal fields.
    Recursively processes nested models and lists.
    """
    result = {}
    for key, value in model.__dict__.items():
        if key.startswith("_"):
            continue
        result[key] = _convert_value(value)
    return result


def _convert_value(value):
    """Convert a value to a JSON-safe type."""
    if value is None:
        return None
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, list):
        return [_convert_value(item) for item in value]
    if hasattr(value, "__dict__") and not isinstance(value, (str, int, float, bool)):
        return model_to_dict(value)
    return value


def parse_date(value: str | None) -> date | None:
    """Parse an ISO date string (YYYY-MM-DD) to a date object."""
    if value is None:
        return None
    return date.fromisoformat(value)


def json_response(data) -> str:
    """Serialize data to a JSON string with fallback for special types."""
    return json.dumps(data, default=str, ensure_ascii=False)


def error_response(e: Exception) -> str:
    """Create a standardized error response."""
    return json_response({"error": str(e)})
