"""Account tools for Fakturoid MCP server."""

from mcp.server.fastmcp import Context, FastMCP

from fakturoid_mcp.tools._helpers import error_response, get_client, json_response, model_to_dict


def register(mcp: FastMCP) -> None:
    """Register account tools."""

    @mcp.tool()
    def get_account(ctx: Context) -> str:
        """Get Fakturoid account information (name, plan, etc.)."""
        try:
            fa = get_client(ctx)
            account = fa.account()
            return json_response(model_to_dict(account))
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def list_bank_accounts(ctx: Context) -> str:
        """List all bank accounts configured in Fakturoid."""
        try:
            fa = get_client(ctx)
            accounts = fa.bank_accounts()
            return json_response([model_to_dict(a) for a in accounts])
        except Exception as e:
            return error_response(e)
