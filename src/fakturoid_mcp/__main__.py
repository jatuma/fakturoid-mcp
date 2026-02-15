"""Entry point for fakturoid-mcp server."""

import os

from fakturoid_mcp.server import mcp


def main():
    transport = os.environ.get("FAKTUROID_TRANSPORT", "stdio")
    if transport == "streamable-http":
        host = os.environ.get("FAKTUROID_HOST", "0.0.0.0")
        port = int(os.environ.get("FAKTUROID_PORT", "8000"))
        mcp.run(transport=transport, host=host, port=port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
