"""Expense tools for Fakturoid MCP server."""

from fakturoid import Expense, ExpensePayment, InvoiceLine
from mcp.server.fastmcp import Context, FastMCP

from fakturoid_mcp.tools._helpers import (
    error_response,
    get_client,
    json_response,
    model_to_dict,
    parse_date,
)


def register(mcp: FastMCP) -> None:
    """Register expense tools."""

    @mcp.tool()
    def list_expenses(
        ctx: Context,
        subject_id: int | None = None,
        since: str | None = None,
        updated_since: str | None = None,
        number: str | None = None,
        status: str | None = None,
        custom_id: str | None = None,
        variable_symbol: str | None = None,
    ) -> str:
        """List expenses with optional filters.

        Args:
            subject_id: Filter by subject (supplier) ID
            since: Return expenses created since this date (YYYY-MM-DD)
            updated_since: Return expenses updated since this date (YYYY-MM-DD)
            number: Filter by expense number
            status: Filter by status (open, overdue, paid)
            custom_id: Filter by custom identifier
            variable_symbol: Filter by variable symbol
        """
        try:
            fa = get_client(ctx)
            kwargs = {}
            if subject_id is not None:
                kwargs["subject_id"] = subject_id
            if since:
                kwargs["since"] = parse_date(since)
            if updated_since:
                kwargs["updated_since"] = parse_date(updated_since)
            if number:
                kwargs["number"] = number
            if status:
                kwargs["status"] = status
            if custom_id:
                kwargs["custom_id"] = custom_id
            if variable_symbol:
                kwargs["variable_symbol"] = variable_symbol
            expenses = list(fa.expenses(**kwargs))
            return json_response([model_to_dict(e) for e in expenses])
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def get_expense(ctx: Context, expense_id: int) -> str:
        """Get a single expense by ID.

        Args:
            expense_id: The expense ID
        """
        try:
            fa = get_client(ctx)
            expense = fa.expense(expense_id)
            return json_response(model_to_dict(expense))
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def create_expense(
        ctx: Context,
        subject_id: int,
        lines: list[dict],
        issued_on: str | None = None,
        taxable_fulfillment_due: str | None = None,
        due_on: str | None = None,
        currency: str | None = None,
        payment_method: str | None = None,
        note: str | None = None,
        variable_symbol: str | None = None,
        custom_id: str | None = None,
        tags: list[str] | None = None,
    ) -> str:
        """Create a new expense.

        Args:
            subject_id: Supplier subject ID (required)
            lines: List of line items, each with keys: name (str), quantity (number),
                   unit_name (str), unit_price (number), vat_rate (number)
            issued_on: Issue date (YYYY-MM-DD)
            taxable_fulfillment_due: Taxable fulfillment date (YYYY-MM-DD)
            due_on: Due date (YYYY-MM-DD)
            currency: Currency code (e.g. CZK, EUR)
            payment_method: Payment method (bank, cash, cod, card, paypal, custom)
            note: Note on the expense
            variable_symbol: Variable symbol
            custom_id: Custom identifier
            tags: List of tags
        """
        try:
            fa = get_client(ctx)
            expense_lines = [InvoiceLine(**line) for line in lines]
            kwargs: dict = {
                "subject_id": subject_id,
                "lines": expense_lines,
            }
            if issued_on:
                kwargs["issued_on"] = parse_date(issued_on)
            if taxable_fulfillment_due:
                kwargs["taxable_fulfillment_due"] = parse_date(taxable_fulfillment_due)
            if due_on:
                kwargs["due_on"] = parse_date(due_on)
            if currency:
                kwargs["currency"] = currency
            if payment_method:
                kwargs["payment_method"] = payment_method
            if note:
                kwargs["note"] = note
            if variable_symbol:
                kwargs["variable_symbol"] = variable_symbol
            if custom_id:
                kwargs["custom_id"] = custom_id
            if tags:
                kwargs["tags"] = tags
            expense = Expense(**kwargs)
            fa.save(expense)
            return json_response(model_to_dict(expense))
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def update_expense(
        ctx: Context,
        expense_id: int,
        due_on: str | None = None,
        currency: str | None = None,
        payment_method: str | None = None,
        note: str | None = None,
        variable_symbol: str | None = None,
        custom_id: str | None = None,
        lines: list[dict] | None = None,
    ) -> str:
        """Update an existing expense.

        Args:
            expense_id: The expense ID to update
            due_on: Due date (YYYY-MM-DD)
            currency: Currency code (e.g. CZK, EUR)
            payment_method: Payment method
            note: Note on the expense
            variable_symbol: Variable symbol
            custom_id: Custom identifier
            lines: Replacement line items (replaces all existing lines)
        """
        try:
            fa = get_client(ctx)
            expense = fa.expense(expense_id)
            if due_on is not None:
                expense.due_on = parse_date(due_on)
            if currency is not None:
                expense.currency = currency
            if payment_method is not None:
                expense.payment_method = payment_method
            if note is not None:
                expense.note = note
            if variable_symbol is not None:
                expense.variable_symbol = variable_symbol
            if custom_id is not None:
                expense.custom_id = custom_id
            if lines is not None:
                expense.lines = [InvoiceLine(**line) for line in lines]
            fa.save(expense)
            return json_response(model_to_dict(expense))
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def delete_expense(ctx: Context, expense_id: int) -> str:
        """Delete an expense by ID.

        Args:
            expense_id: The expense ID to delete
        """
        try:
            fa = get_client(ctx)
            fa.delete(Expense(id=expense_id))
            return json_response({"success": True, "deleted_id": expense_id})
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def fire_expense_event(
        ctx: Context,
        expense_id: int,
        event: str,
    ) -> str:
        """Fire an event on an expense to change its state.

        Args:
            expense_id: The expense ID
            event: Event name: remove_payment, deliver, pay, lock, unlock
        """
        try:
            fa = get_client(ctx)
            fa.fire_expense_event(expense_id, event)
            return json_response({"success": True, "expense_id": expense_id, "event": event})
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def create_expense_payment(
        ctx: Context,
        expense_id: int,
        paid_on: str,
        amount: float,
        currency: str | None = None,
    ) -> str:
        """Record a payment on an expense.

        Args:
            expense_id: The expense ID
            paid_on: Payment date (YYYY-MM-DD)
            amount: Payment amount
            currency: Currency code
        """
        try:
            fa = get_client(ctx)
            kwargs: dict = {
                "paid_on": parse_date(paid_on),
                "amount": amount,
            }
            if currency:
                kwargs["currency"] = currency
            payment = ExpensePayment(**kwargs)
            fa.save(payment, expense_id=expense_id)
            return json_response(model_to_dict(payment))
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def delete_expense_payment(ctx: Context, expense_id: int, payment_id: int) -> str:
        """Delete a payment from an expense.

        Args:
            expense_id: The expense ID
            payment_id: The payment ID to delete
        """
        try:
            fa = get_client(ctx)
            fa.delete(ExpensePayment(id=payment_id), expense_id=expense_id)
            return json_response({"success": True, "expense_id": expense_id, "payment_id": payment_id})
        except Exception as e:
            return error_response(e)
