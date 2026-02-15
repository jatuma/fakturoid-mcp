"""Generator (invoice template) tools for Fakturoid MCP server."""

from fakturoid import Generator, InvoiceLine
from mcp.server.fastmcp import Context, FastMCP

from fakturoid_mcp.tools._helpers import (
    error_response,
    get_client,
    json_response,
    model_to_dict,
    parse_date,
)


def register(mcp: FastMCP) -> None:
    """Register generator tools."""

    @mcp.tool()
    def list_generators(
        ctx: Context,
        recurring: bool | None = None,
        subject_id: int | None = None,
        since: str | None = None,
    ) -> str:
        """List invoice generators (templates).

        Args:
            recurring: True for recurring generators, False for simple templates
            subject_id: Filter by subject (client) ID
            since: Return generators created since this date (YYYY-MM-DD)
        """
        try:
            fa = get_client(ctx)
            kwargs = {}
            if recurring is not None:
                kwargs["recurring"] = recurring
            if subject_id is not None:
                kwargs["subject_id"] = subject_id
            if since:
                kwargs["since"] = parse_date(since)
            generators = list(fa.generators(**kwargs))
            return json_response([model_to_dict(g) for g in generators])
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def get_generator(ctx: Context, generator_id: int) -> str:
        """Get a single invoice generator (template) by ID.

        Args:
            generator_id: The generator ID
        """
        try:
            fa = get_client(ctx)
            generator = fa.generator(generator_id)
            return json_response(model_to_dict(generator))
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def create_generator(
        ctx: Context,
        name: str,
        subject_id: int,
        lines: list[dict],
        recurring: bool = False,
        due: int | None = None,
        currency: str | None = None,
        payment_method: str | None = None,
        note: str | None = None,
        tags: list[str] | None = None,
    ) -> str:
        """Create a new invoice generator (template).

        Args:
            name: Generator name (required)
            subject_id: Client subject ID (required)
            lines: List of line items, each with keys: name (str), quantity (number),
                   unit_name (str), unit_price (number), vat_rate (number)
            recurring: Whether this is a recurring generator
            due: Number of days until due
            currency: Currency code (e.g. CZK, EUR)
            payment_method: Payment method (bank, cash, cod, card, paypal, custom)
            note: Note on generated invoices
            tags: List of tags
        """
        try:
            fa = get_client(ctx)
            generator_lines = [InvoiceLine(**line) for line in lines]
            kwargs: dict = {
                "name": name,
                "subject_id": subject_id,
                "lines": generator_lines,
                "recurring": recurring,
            }
            if due is not None:
                kwargs["due"] = due
            if currency:
                kwargs["currency"] = currency
            if payment_method:
                kwargs["payment_method"] = payment_method
            if note:
                kwargs["note"] = note
            if tags:
                kwargs["tags"] = tags
            generator = Generator(**kwargs)
            fa.save(generator)
            return json_response(model_to_dict(generator))
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def update_generator(
        ctx: Context,
        generator_id: int,
        name: str | None = None,
        due: int | None = None,
        currency: str | None = None,
        payment_method: str | None = None,
        note: str | None = None,
        lines: list[dict] | None = None,
    ) -> str:
        """Update an existing invoice generator (template).

        Args:
            generator_id: The generator ID to update
            name: Generator name
            due: Number of days until due
            currency: Currency code (e.g. CZK, EUR)
            payment_method: Payment method
            note: Note on generated invoices
            lines: Replacement line items (replaces all existing lines)
        """
        try:
            fa = get_client(ctx)
            generator = fa.generator(generator_id)
            if name is not None:
                generator.name = name
            if due is not None:
                generator.due = due
            if currency is not None:
                generator.currency = currency
            if payment_method is not None:
                generator.payment_method = payment_method
            if note is not None:
                generator.note = note
            if lines is not None:
                generator.lines = [InvoiceLine(**line) for line in lines]
            fa.save(generator)
            return json_response(model_to_dict(generator))
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def delete_generator(ctx: Context, generator_id: int) -> str:
        """Delete an invoice generator (template) by ID.

        Args:
            generator_id: The generator ID to delete
        """
        try:
            fa = get_client(ctx)
            fa.delete(Generator(id=generator_id))
            return json_response({"success": True, "deleted_id": generator_id})
        except Exception as e:
            return error_response(e)
