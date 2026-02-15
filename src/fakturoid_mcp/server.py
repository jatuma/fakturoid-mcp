"""FastMCP server instance and lifespan management."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from fakturoid import Fakturoid
from mcp.server.fastmcp import FastMCP

from fakturoid_mcp.config import Settings


@dataclass
class AppContext:
    client: Fakturoid
    settings: Settings


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    settings = Settings()
    client = Fakturoid(
        settings.slug,
        settings.email,
        settings.client_id,
        settings.client_secret.get_secret_value(),
        settings.user_agent,
    )
    yield AppContext(client=client, settings=settings)


mcp = FastMCP(
    "Fakturoid",
    instructions="MCP server for Fakturoid.cz accounting service (API v3)",
    lifespan=app_lifespan,
)

from fakturoid_mcp.tools import register_all_tools  # noqa: E402

register_all_tools(mcp)
