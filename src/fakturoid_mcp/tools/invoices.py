"""Invoice tools for Fakturoid MCP server."""

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    """Register invoice tools."""
