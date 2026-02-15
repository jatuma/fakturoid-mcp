# Implementation Plan: Fakturoid MCP Server

Created: 2026-02-15
Status: draft

## Overview

Build an MCP (Model Context Protocol) server that wraps the Fakturoid.cz accounting API, exposing it as a set of tools for LLMs. The server uses the jan-tomek/python-fakturoid fork (v2.9.1, API v3 with OAuth 2.0 client credentials flow), FastMCP from the `mcp` Python SDK for the server framework, and pydantic-settings for configuration. The architecture is modular with tools organized by domain (account, subjects, invoices, expenses, generators). Both stdio and HTTP transports are supported, with Docker for production deployment.

## Current State

The repository contains only a `.gitignore` and a placeholder `README.md` on the `main` branch. There is no source code, no configuration, and no dependency management yet. The design plan at `~/.claude/plans/refactored-percolating-planet.md` is complete and specifies the full target architecture, project structure, all 31 tools, and the implementation patterns.

## Desired State

A fully working MCP server with 31 tools covering: account info (2), subjects CRUD + search (6), invoices CRUD + events + payments + messages (10), expenses CRUD + events + payments (8), and generators CRUD (5). Runnable via `uv run fakturoid-mcp` (stdio) or Docker (HTTP). All tools return JSON strings and handle errors gracefully.

## Library API Notes (Critical for Implementation)

Analysis of the `jan-tomek/python-fakturoid` fork reveals the following API surface that tools must map to:

- **Client init**: `Fakturoid(slug, email, client_id, client_secret, user_agent)` -- triggers `refresh_access_token()` immediately
- **Account**: `fa.account()` returns `Account`, `fa.bank_accounts()` returns list of `BankAccount`
- **Subjects**: `fa.subject(id)`, `fa.subjects(since?, updated_since?, custom_id?)` returns `ModelList`, `fa.subjects.search(query)` returns list
- **Invoices**: `fa.invoice(id)`, `fa.invoices(proforma?, subject_id?, since?, until?, updated_since?, updated_until?, number?, status?, custom_id?)` returns `ModelList`, `fa.fire_invoice_event(id, event, **kwargs)`
- **Expenses**: `fa.expense(id)`, `fa.expenses(subject_id?, since?, updated_since?, number?, status?, custom_id?, variable_symbol?)` returns `ModelList`, `fa.fire_expense_event(id, event, **kwargs)`
- **Generators**: `fa.generator(id)`, `fa.generators(recurring?, subject_id?, since?)` returns list
- **CRUD**: `fa.save(model_instance)` for create/update (checks `model.id`), `fa.delete(model_instance)`
- **Payments**: `fa.save(InvoicePayment(...), invoice_id=N)`, `fa.delete(InvoicePayment(id=M), invoice_id=N)`, same pattern for `ExpensePayment` with `expense_id`
- **Messages**: `fa.save(InvoiceMessage(...), invoice_id=N)`
- **No search for invoices/expenses** -- the library only supports `subjects.search()`. The design plan lists `search_invoices` and `search_expenses` tools, but these cannot be implemented with this library. We will skip them (29 tools instead of 31) or implement them as filtered list queries.
- **ModelList is lazy** -- `fa.subjects()`, `fa.invoices()`, `fa.expenses()` return `ModelList` which loads pages on access. Tools must iterate to collect results (e.g., `list(fa.subjects())`).
- **Model serialization** -- Models have `__dict__` with all fields. Use `model.__dict__` for JSON serialization, filtering internal fields (`_loaded_lines`). `model.get_fields()` only returns writable fields (for save), not all fields.
- **Date parameters** -- The library expects `datetime.date` or `datetime.datetime` objects for filter params like `since`, `paid_at`. Tools must parse ISO strings from LLM input into date objects.

## Files to Change

- `README.md` -- Replace placeholder with full documentation: project description, prerequisites, setup with uv, Claude Desktop configuration (stdio), Docker deployment (HTTP), available tools reference, environment variable reference.

## New Files

### Phase 1: Project Foundation
- `pyproject.toml` -- Project metadata (Python >=3.11), dependencies (mcp[cli], fakturoid from git, pydantic-settings), entry point `fakturoid-mcp = "fakturoid_mcp.__main__:main"`, hatchling build system, ruff config.
- `.env.example` -- Template showing all `FAKTUROID_*` variables: SLUG, EMAIL, CLIENT_ID, CLIENT_SECRET, USER_AGENT (optional), TRANSPORT (default: stdio), HOST, PORT.
- `src/fakturoid_mcp/__init__.py` -- Package version string (`__version__ = "0.1.0"`).
- `src/fakturoid_mcp/config.py` -- `Settings` class using `pydantic_settings.BaseSettings` with `env_prefix="FAKTUROID_"`. Fields: `slug: str`, `email: str`, `client_id: str`, `client_secret: SecretStr`, `user_agent: str` (with default), `transport: str` (default "stdio"), `host: str` (default "0.0.0.0"), `port: int` (default 8000).
- `src/fakturoid_mcp/server.py` -- Create `FastMCP("Fakturoid")` instance with lifespan context manager that loads Settings, creates Fakturoid client, yields context dict with `{"client": fa}`. Import and call `register_all_tools(mcp)`.
- `src/fakturoid_mcp/__main__.py` -- Load settings, call `mcp.run(transport=settings.transport)` with host/port kwargs for HTTP transport. Guard with `if __name__ == "__main__"`.
- `src/fakturoid_mcp/tools/__init__.py` -- `register_all_tools(mcp)` function that imports and calls `register(mcp)` from each tool module.

### Phase 2: Account and Subject Tools
- `src/fakturoid_mcp/tools/account.py` -- `register(mcp)` defining 2 tools: `get_account` (calls `fa.account()`, returns serialized dict), `list_bank_accounts` (calls `fa.bank_accounts()`, returns serialized list). Both access client via `ctx.request_context.lifespan_context["client"]`.
- `src/fakturoid_mcp/tools/subjects.py` -- `register(mcp)` defining 6 tools: `list_subjects` (with optional `since`, `updated_since`, `custom_id` string params; parses dates, calls `fa.subjects()`, iterates ModelList), `search_subjects` (calls `fa.subjects.search(query)`), `get_subject`, `create_subject` (creates `Subject(**fields)`, calls `fa.save()`), `update_subject` (loads then updates fields, saves), `delete_subject` (calls `fa.delete(Subject(id=...))`).

### Phase 3: Invoice Tools
- `src/fakturoid_mcp/tools/invoices.py` -- `register(mcp)` defining 8-10 tools: `list_invoices` (with filters: subject_id, since, updated_since, number, status, custom_id, proforma; parses dates), `get_invoice`, `create_invoice` (creates `Invoice` with `InvoiceLine` objects from lines list), `update_invoice`, `delete_invoice`, `fire_invoice_event` (calls `fa.fire_invoice_event(id, event, **kwargs)`; parses `paid_at` to date), `create_invoice_payment` (creates `InvoicePayment`, calls `fa.save(payment, invoice_id=...)`), `delete_invoice_payment`, `send_invoice_message` (creates `InvoiceMessage`, calls `fa.save(msg, invoice_id=...)`). Note: `search_invoices` is not supported by the library -- either skip or implement as a note in the tool's error response.

### Phase 4: Expense and Generator Tools
- `src/fakturoid_mcp/tools/expenses.py` -- `register(mcp)` defining 7-8 tools: `list_expenses` (with filters), `get_expense`, `create_expense`, `update_expense`, `delete_expense`, `fire_expense_event`, `create_expense_payment`. Note: `search_expenses` not supported by library -- same approach as invoices.
- `src/fakturoid_mcp/tools/generators.py` -- `register(mcp)` defining 5 tools: `list_generators` (with `recurring`, `subject_id`, `since` params), `get_generator`, `create_generator`, `update_generator`, `delete_generator`.

### Phase 5: Docker and Deployment
- `Dockerfile` -- Multi-stage build: builder stage with uv installing dependencies, runtime stage with slim Python copying `.venv` and `src/`. Default command runs with `streamable-http` transport on port 8000.
- `docker-compose.yml` -- Service definition with build context, port 8000 mapping, `env_file: .env`, `restart: unless-stopped`.

## Implementation Phases (Commit Boundaries)

### Phase 1: Project Foundation
**Files**: `pyproject.toml`, `.env.example`, `src/fakturoid_mcp/__init__.py`, `src/fakturoid_mcp/config.py`, `src/fakturoid_mcp/server.py`, `src/fakturoid_mcp/__main__.py`, `src/fakturoid_mcp/tools/__init__.py`
**Verification**: `uv sync` installs dependencies; `uv run fakturoid-mcp` starts without tools (exits cleanly or shows MCP server ready).

### Phase 2: Account and Subject Tools
**Files**: `src/fakturoid_mcp/tools/account.py`, `src/fakturoid_mcp/tools/subjects.py`, update `tools/__init__.py`
**Verification**: With valid `.env`, `uv run fakturoid-mcp` exposes 8 tools. Test `get_account` via MCP inspector.

### Phase 3: Invoice Tools
**Files**: `src/fakturoid_mcp/tools/invoices.py`, update `tools/__init__.py`
**Verification**: 18 tools exposed. Test `list_invoices`, `create_invoice` with line items, `fire_invoice_event`.

### Phase 4: Expense and Generator Tools
**Files**: `src/fakturoid_mcp/tools/expenses.py`, `src/fakturoid_mcp/tools/generators.py`, update `tools/__init__.py`
**Verification**: 29 tools exposed. Test CRUD cycle on expenses and generators.

### Phase 5: Docker and Deployment
**Files**: `Dockerfile`, `docker-compose.yml`
**Verification**: `docker compose up --build` starts HTTP server on port 8000. Test with MCP client connecting via HTTP.

### Phase 6: Documentation
**Files**: `README.md`
**Verification**: README covers setup, usage, tool reference, deployment.

## Dependencies

- `mcp[cli]>=1.0` -- MCP Python SDK with FastMCP and CLI tools
- `fakturoid @ git+https://github.com/jan-tomek/python-fakturoid.git` -- Fakturoid API v3 client (v2.9.1); depends on `requests` and `python-dateutil`
- `pydantic-settings>=2.0` -- Configuration management from env vars and .env files
- Python >= 3.11
- uv for package management
- Docker + docker-compose for HTTP deployment (optional)

## Risks

- **OAuth token refresh under load**: The library refreshes the access token synchronously and stores it on the `Fakturoid` instance. If multiple MCP tool calls arrive concurrently, there could be a race condition on token refresh. FastMCP runs sync tools in a thread pool, so this is a real concern. Mitigation: The library already checks expiration with a 900-second buffer, and in practice MCP calls are sequential from a single LLM. Monitor and add a lock if needed.
- **ModelList iteration cost**: `fa.subjects()`, `fa.invoices()`, etc. return lazy `ModelList` that loads all pages when iterated. For accounts with thousands of invoices, `list(fa.invoices())` could be very slow and return huge payloads. Mitigation: Add pagination parameters to list tools (page number/size) or limit results. Consider adding a `page` parameter to list tools and loading only one page at a time.
- **No invoice/expense search**: The library only implements `subjects.search()`. The design plan assumed `search_invoices` and `search_expenses` exist, but the fork does not have them. This reduces the tool count from 31 to 29. The Fakturoid API v3 does support search endpoints -- we could implement raw HTTP calls, but that breaks the library abstraction. Decision: Skip search tools for invoices/expenses in the initial implementation; note in README.
- **Library stability**: The jan-tomek fork is pinned by git URL without a tag/commit hash. If the fork changes, builds could break. Mitigation: Consider pinning to a specific commit hash in `pyproject.toml`.
- **Decimal serialization**: The library uses Python `Decimal` for monetary values. `json.dumps` does not handle `Decimal` natively. Tools must use a custom serializer (e.g., `default=str`) or convert decimals before serialization.
- **Date parsing from LLM input**: Tools receive dates as ISO strings from the LLM. These must be parsed to `datetime.date` objects for the library. Invalid date strings from the LLM will cause errors. Mitigation: Add clear docstrings specifying expected format (YYYY-MM-DD) and wrap parsing in try/except.
- **Model-to-dict serialization**: The library models use `__dict__` which includes internal fields like `_loaded_lines`. Need a helper function to cleanly serialize models to dicts, filtering private attributes and handling Decimal/date/datetime types.

## Shared Utilities (Consider Adding)

A small `src/fakturoid_mcp/tools/_helpers.py` module could reduce code duplication across tool modules:
- `get_client(ctx)` -- Extract Fakturoid client from MCP context
- `model_to_dict(model)` -- Serialize any Model to a JSON-safe dict, handling Decimal, date, datetime, filtering `_` prefixed attributes, and recursing into nested models/lists
- `parse_date(value: str | None) -> date | None` -- Parse ISO date string from LLM input
- `json_response(data)` -- `json.dumps` with `default=str` fallback
- `error_response(e: Exception)` -- Standardized error dict `{"error": str(e)}`
