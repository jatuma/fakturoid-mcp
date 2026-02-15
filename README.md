# fakturoid-mcp

MCP server for [Fakturoid.cz](https://www.fakturoid.cz) accounting service. Exposes the Fakturoid API v3 as 30 MCP tools for use with Claude Desktop, Claude Code, and other MCP clients.

Uses the [jan-tomek/python-fakturoid](https://github.com/jan-tomek/python-fakturoid) library for API access with OAuth 2.0 authentication.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Fakturoid account with API credentials (Client ID + Client Secret)

## Setup

1. Clone the repository and install dependencies:

```bash
git clone https://github.com/your-org/fakturoid-mcp.git
cd fakturoid-mcp
uv sync
```

2. Create a `.env` file with your Fakturoid credentials:

```bash
cp .env.example .env
# Edit .env with your credentials
```

Get your OAuth credentials from: **Fakturoid > Settings > User account > API credentials**

## Usage

### Claude Desktop (stdio)

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "fakturoid": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/fakturoid-mcp", "run", "fakturoid-mcp"],
      "env": {
        "FAKTUROID_SLUG": "your-slug",
        "FAKTUROID_EMAIL": "your@email.com",
        "FAKTUROID_CLIENT_ID": "your-client-id",
        "FAKTUROID_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

### Claude Code (stdio)

Add to your Claude Code MCP config:

```json
{
  "mcpServers": {
    "fakturoid": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/fakturoid-mcp", "run", "fakturoid-mcp"],
      "env": {
        "FAKTUROID_SLUG": "your-slug",
        "FAKTUROID_EMAIL": "your@email.com",
        "FAKTUROID_CLIENT_ID": "your-client-id",
        "FAKTUROID_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

### Docker (HTTP transport)

```bash
docker compose up --build
```

The server will be available at `http://localhost:8000/mcp`.

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FAKTUROID_SLUG` | Yes | — | Fakturoid account slug |
| `FAKTUROID_EMAIL` | Yes | — | Account email |
| `FAKTUROID_CLIENT_ID` | Yes | — | OAuth Client ID |
| `FAKTUROID_CLIENT_SECRET` | Yes | — | OAuth Client Secret |
| `FAKTUROID_USER_AGENT` | No | `FakturoidMCP (mcp@example.com)` | User-Agent header |
| `FAKTUROID_TRANSPORT` | No | `stdio` | Transport: `stdio` or `streamable-http` |
| `FAKTUROID_HOST` | No | `0.0.0.0` | HTTP server host |
| `FAKTUROID_PORT` | No | `8000` | HTTP server port |

## Available Tools (30)

### Account (2)

- `get_account` — Get account information
- `list_bank_accounts` — List bank accounts

### Subjects (6)

- `list_subjects` — List contacts/clients with filters
- `search_subjects` — Full-text search subjects
- `get_subject` — Get subject by ID
- `create_subject` — Create new contact
- `update_subject` — Update contact
- `delete_subject` — Delete contact

### Invoices (9)

- `list_invoices` — List invoices with filters (status, date, subject, etc.)
- `get_invoice` — Get invoice by ID
- `create_invoice` — Create invoice with line items
- `update_invoice` — Update invoice
- `delete_invoice` — Delete invoice
- `fire_invoice_event` — Change state (mark_as_sent, deliver, pay, cancel, etc.)
- `create_invoice_payment` — Record a payment
- `delete_invoice_payment` — Delete a payment
- `send_invoice_message` — Send invoice via email

### Expenses (8)

- `list_expenses` — List expenses with filters
- `get_expense` — Get expense by ID
- `create_expense` — Create expense with line items
- `update_expense` — Update expense
- `delete_expense` — Delete expense
- `fire_expense_event` — Change state (pay, lock, unlock, etc.)
- `create_expense_payment` — Record a payment
- `delete_expense_payment` — Delete a payment

### Generators (5)

- `list_generators` — List invoice templates
- `get_generator` — Get generator by ID
- `create_generator` — Create invoice template
- `update_generator` — Update template
- `delete_generator` — Delete template

## Limitations

- **No invoice/expense search** — The python-fakturoid library only supports full-text search on subjects. Invoice and expense listing supports filters (status, date, subject) but not free-text search.
- **Synchronous API** — The Fakturoid client library uses synchronous HTTP calls. FastMCP wraps these in a thread pool automatically.

## License

MIT
