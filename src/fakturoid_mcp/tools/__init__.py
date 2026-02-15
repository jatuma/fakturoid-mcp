"""MCP tool registration."""

from mcp.server.fastmcp import FastMCP


def register_all_tools(mcp: FastMCP) -> None:
    """Import all tool modules to trigger registration."""
    from fakturoid_mcp.tools import account, expenses, generators, invoices, subjects  # noqa: F401

    for module in [account, subjects, invoices, expenses, generators]:
        module.register(mcp)
