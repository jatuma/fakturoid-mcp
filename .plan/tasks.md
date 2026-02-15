# Implementation Tasks

Created: 2026-02-15
Plan: Fakturoid MCP Server

## Phase 1: Project Foundation & Shared Utilities
**Goal**: Set up project structure, dependencies, configuration, and shared helper functions.
**Verification**: `uv sync` installs dependencies; `uv run fakturoid-mcp` starts without tools (exits cleanly or shows MCP server ready).

### Core Setup (Sequential)
- [ ] Create `pyproject.toml` with project metadata, dependencies (mcp[cli], fakturoid from git, pydantic-settings), and entry point configuration
- [ ] Create `.env.example` template with all `FAKTUROID_*` environment variables
- [ ] Create `src/fakturoid_mcp/__init__.py` with package version string

### Configuration & Server Infrastructure (Sequential - depends on Core Setup)
- [ ] Implement `src/fakturoid_mcp/config.py` with pydantic-settings based Settings class
- [ ] Implement `src/fakturoid_mcp/server.py` with FastMCP instance and lifespan context manager for client initialization
- [ ] Implement `src/fakturoid_mcp/__main__.py` with transport selection logic and entry point

### Shared Utilities (Parallel - can start after Core Setup)
- [ ] Create `src/fakturoid_mcp/tools/_helpers.py` with shared utility functions (get_client, model_to_dict, parse_date, json_response, error_response)
- [ ] Create `src/fakturoid_mcp/tools/__init__.py` with register_all_tools function (initially empty)

### Phase 1 Verification
- [ ] Run `uv sync` to verify dependency installation
- [ ] Run `uv run fakturoid-mcp` to verify server starts successfully

## Phase 2: Account and Subject Tools
**Goal**: Implement first set of domain tools (account info and subjects CRUD).
**Verification**: With valid `.env`, `uv run fakturoid-mcp` exposes 8 tools. Test `get_account` via MCP inspector.
**Parallelism**: Account and Subject tools can be implemented in parallel by different agents.

### Account Tools (Parallel Track A)
- [ ] Implement `src/fakturoid_mcp/tools/account.py` with 2 tools: get_account, list_bank_accounts
- [ ] Update `src/fakturoid_mcp/tools/__init__.py` to register account tools

### Subject Tools (Parallel Track B)
- [ ] Implement `src/fakturoid_mcp/tools/subjects.py` with 6 tools: list_subjects, search_subjects, get_subject, create_subject, update_subject, delete_subject
- [ ] Update `src/fakturoid_mcp/tools/__init__.py` to register subject tools

### Phase 2 Verification
- [ ] Run `uv run fakturoid-mcp` and verify 8 tools are exposed
- [ ] Test get_account and list_subjects with valid credentials via MCP inspector

## Phase 3: Invoice Tools
**Goal**: Implement complete invoice management toolset (CRUD, events, payments, messages).
**Verification**: 18 tools exposed. Test `list_invoices`, `create_invoice` with line items, `fire_invoice_event`.

### Invoice Core CRUD (Sequential)
- [ ] Implement `src/fakturoid_mcp/tools/invoices.py` with basic CRUD tools: list_invoices (with all filters), get_invoice, create_invoice (with InvoiceLine handling), update_invoice, delete_invoice

### Invoice Events & Payments (Parallel - depends on Invoice Core CRUD)
- [ ] Add fire_invoice_event tool to invoices.py with event type handling and date parsing
- [ ] Add create_invoice_payment and delete_invoice_payment tools with proper payment model handling
- [ ] Add send_invoice_message tool for creating and sending invoice messages

### Phase 3 Integration
- [ ] Update `src/fakturoid_mcp/tools/__init__.py` to register invoice tools

### Phase 3 Verification
- [ ] Run `uv run fakturoid-mcp` and verify 18 tools are exposed (8 from Phase 2 + 10 from Phase 3)
- [ ] Test invoice creation with line items, fire an event, and create a payment

## Phase 4: Expense and Generator Tools
**Goal**: Complete all remaining domain tools (expenses and generators).
**Verification**: 29 tools exposed. Test CRUD cycle on expenses and generators.
**Parallelism**: Expense and Generator tools can be implemented in parallel by different agents.

### Expense Tools (Parallel Track A)
- [ ] Implement `src/fakturoid_mcp/tools/expenses.py` with 8 tools: list_expenses (with filters), get_expense, create_expense, update_expense, delete_expense, fire_expense_event, create_expense_payment, delete_expense_payment
- [ ] Update `src/fakturoid_mcp/tools/__init__.py` to register expense tools

### Generator Tools (Parallel Track B)
- [ ] Implement `src/fakturoid_mcp/tools/generators.py` with 5 tools: list_generators (with filters), get_generator, create_generator, update_generator, delete_generator
- [ ] Update `src/fakturoid_mcp/tools/__init__.py` to register generator tools

### Phase 4 Verification
- [ ] Run `uv run fakturoid-mcp` and verify all 29 tools are exposed
- [ ] Test complete CRUD cycle on an expense (create, update, get, delete)
- [ ] Test generator creation and listing with filters

## Phase 5: Docker and Deployment
**Goal**: Enable production deployment via Docker with HTTP transport.
**Verification**: `docker compose up --build` starts HTTP server on port 8000. Test with MCP client connecting via HTTP.

### Docker Configuration (Parallel)
- [ ] Create `Dockerfile` with multi-stage build (builder with uv, runtime with slim Python)
- [ ] Create `docker-compose.yml` with service definition, port mapping, and env file configuration

### Phase 5 Verification
- [ ] Build Docker image and verify successful build
- [ ] Run `docker compose up` and verify HTTP server starts on port 8000
- [ ] Test MCP client connection via HTTP transport

## Phase 6: Documentation
**Goal**: Provide complete documentation for users and developers.
**Verification**: README covers setup, usage, tool reference, deployment.

### Documentation
- [ ] Replace `README.md` with comprehensive documentation: project description, prerequisites, setup with uv, Claude Desktop configuration (stdio), Docker deployment (HTTP), available tools reference (all 29 tools organized by domain), environment variable reference, limitations (no search for invoices/expenses), and example usage

### Phase 6 Verification
- [ ] Review README for completeness and accuracy
- [ ] Verify all commands in README execute successfully

## Parallelism Opportunities Summary

**Phase 1**: Shared Utilities can start as soon as Core Setup completes (parallel with Configuration & Server Infrastructure).

**Phase 2**: Account Tools (Track A) and Subject Tools (Track B) are fully independent and can be implemented simultaneously.

**Phase 3**: After Invoice Core CRUD is complete, the three event/payment/message tool groups can be worked on in parallel.

**Phase 4**: Expense Tools (Track A) and Generator Tools (Track B) are fully independent and can be implemented simultaneously.

**Phase 5**: Both Docker files can be created in parallel.

**Maximum Parallelism**: Up to 2-3 agents can work simultaneously in Phases 2, 3, 4, and 5.

## Dependencies Graph

```
Phase 1: Foundation
├─ Core Setup (seq) → Configuration & Server (seq)
├─ Core Setup (seq) → Shared Utilities (parallel)
└─ Verification (depends on all Phase 1)

Phase 2: Account & Subjects (depends on Phase 1)
├─ Account Tools (parallel track A)
├─ Subject Tools (parallel track B)
└─ Verification (depends on both tracks)

Phase 3: Invoices (depends on Phase 2)
├─ Invoice Core CRUD (seq)
├─ Invoice Events (depends on Core CRUD)
├─ Invoice Payments (depends on Core CRUD)
├─ Invoice Messages (depends on Core CRUD)
└─ Verification (depends on all Phase 3)

Phase 4: Expenses & Generators (depends on Phase 3)
├─ Expense Tools (parallel track A)
├─ Generator Tools (parallel track B)
└─ Verification (depends on both tracks)

Phase 5: Docker (depends on Phase 4)
├─ Dockerfile (parallel)
├─ docker-compose.yml (parallel)
└─ Verification (depends on both)

Phase 6: Documentation (depends on Phase 5)
└─ README.md (single task)
```

## Notes

- **Total Tasks**: 35 actionable tasks across 6 phases
- **Critical Path**: Phase 1 Core/Config → Phase 2 → Phase 3 Core → Phase 3 Events → Phase 4 → Phase 5 → Phase 6
- **Tool Count**: 29 tools total (not 31, due to lack of invoice/expense search in library)
- **Date Handling**: All list/filter tools must parse ISO date strings to date objects
- **Serialization**: All tools must use model_to_dict helper to handle Decimal, dates, and filter internal fields
- **Error Handling**: All tools should wrap operations in try/except and use error_response helper
- **Testing Strategy**: Manual verification after each phase using MCP inspector and valid Fakturoid credentials
