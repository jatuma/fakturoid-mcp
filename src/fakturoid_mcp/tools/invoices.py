"""Invoice tools for Fakturoid MCP server."""

from fakturoid import Invoice, InvoiceLine, InvoiceMessage, InvoicePayment
from mcp.server.fastmcp import Context, FastMCP

from fakturoid_mcp.tools._helpers import (
    error_response,
    get_client,
    json_response,
    model_to_dict,
    parse_date,
)


def register(mcp: FastMCP) -> None:
    """Register invoice tools."""

    @mcp.tool()
    def list_invoices(
        ctx: Context,
        subject_id: int | None = None,
        since: str | None = None,
        updated_since: str | None = None,
        number: str | None = None,
        status: str | None = None,
        custom_id: str | None = None,
        proforma: bool | None = None,
    ) -> str:
        """List invoices with optional filters.

        Args:
            subject_id: Filter by subject (client) ID
            since: Return invoices created since this date (YYYY-MM-DD)
            updated_since: Return invoices updated since this date (YYYY-MM-DD)
            number: Filter by invoice number
            status: Filter by status (open, sent, overdue, paid, cancelled)
            custom_id: Filter by custom identifier
            proforma: True for proforma invoices, False for regular
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
            if proforma is not None:
                kwargs["proforma"] = proforma
            invoices = list(fa.invoices(**kwargs))
            return json_response([model_to_dict(i) for i in invoices])
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def get_invoice(ctx: Context, invoice_id: int) -> str:
        """Get a single invoice by ID.

        Args:
            invoice_id: The invoice ID
        """
        try:
            fa = get_client(ctx)
            invoice = fa.invoice(invoice_id)
            return json_response(model_to_dict(invoice))
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def create_invoice(
        ctx: Context,
        subject_id: int,
        lines: list[dict],
        due: int | None = None,
        issued_on: str | None = None,
        taxable_fulfillment_due: str | None = None,
        currency: str | None = None,
        payment_method: str | None = None,
        note: str | None = None,
        proforma: bool = False,
        custom_id: str | None = None,
        order_number: str | None = None,
        tags: list[str] | None = None,
    ) -> str:
        """Create a new invoice.

        Args:
            subject_id: Client subject ID (required)
            lines: List of line items, each with keys: name (str), quantity (number),
                   unit_name (str), unit_price (number), vat_rate (number)
            due: Number of days until due
            issued_on: Issue date (YYYY-MM-DD)
            taxable_fulfillment_due: Taxable fulfillment date (YYYY-MM-DD)
            currency: Currency code (e.g. CZK, EUR)
            payment_method: Payment method (bank, cash, cod, card, paypal, custom)
            note: Note on the invoice
            proforma: Whether this is a proforma invoice
            custom_id: Custom identifier
            order_number: Order number
            tags: List of tags
        """
        try:
            fa = get_client(ctx)
            invoice_lines = [InvoiceLine(**line) for line in lines]
            kwargs: dict = {
                "subject_id": subject_id,
                "lines": invoice_lines,
            }
            if due is not None:
                kwargs["due"] = due
            if issued_on:
                kwargs["issued_on"] = parse_date(issued_on)
            if taxable_fulfillment_due:
                kwargs["taxable_fulfillment_due"] = parse_date(taxable_fulfillment_due)
            if currency:
                kwargs["currency"] = currency
            if payment_method:
                kwargs["payment_method"] = payment_method
            if note:
                kwargs["note"] = note
            if proforma:
                kwargs["proforma"] = proforma
            if custom_id:
                kwargs["custom_id"] = custom_id
            if order_number:
                kwargs["order_number"] = order_number
            if tags:
                kwargs["tags"] = tags
            invoice = Invoice(**kwargs)
            fa.save(invoice)
            return json_response(model_to_dict(invoice))
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def update_invoice(
        ctx: Context,
        invoice_id: int,
        due: int | None = None,
        currency: str | None = None,
        payment_method: str | None = None,
        note: str | None = None,
        custom_id: str | None = None,
        order_number: str | None = None,
        lines: list[dict] | None = None,
    ) -> str:
        """Update an existing invoice.

        Args:
            invoice_id: The invoice ID to update
            due: Number of days until due
            currency: Currency code (e.g. CZK, EUR)
            payment_method: Payment method
            note: Note on the invoice
            custom_id: Custom identifier
            order_number: Order number
            lines: Replacement line items (replaces all existing lines)
        """
        try:
            fa = get_client(ctx)
            invoice = fa.invoice(invoice_id)
            if due is not None:
                invoice.due = due
            if currency is not None:
                invoice.currency = currency
            if payment_method is not None:
                invoice.payment_method = payment_method
            if note is not None:
                invoice.note = note
            if custom_id is not None:
                invoice.custom_id = custom_id
            if order_number is not None:
                invoice.order_number = order_number
            if lines is not None:
                invoice.lines = [InvoiceLine(**line) for line in lines]
            fa.save(invoice)
            return json_response(model_to_dict(invoice))
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def delete_invoice(ctx: Context, invoice_id: int) -> str:
        """Delete an invoice by ID.

        Args:
            invoice_id: The invoice ID to delete
        """
        try:
            fa = get_client(ctx)
            fa.delete(Invoice(id=invoice_id))
            return json_response({"success": True, "deleted_id": invoice_id})
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def fire_invoice_event(
        ctx: Context,
        invoice_id: int,
        event: str,
        paid_on: str | None = None,
        paid_amount: float | None = None,
    ) -> str:
        """Fire an event on an invoice to change its state.

        Args:
            invoice_id: The invoice ID
            event: Event name: mark_as_sent, deliver, pay, pay_proforma,
                   pay_partial_proforma, remove_payment, deliver_reminder,
                   cancel, undo_cancel
            paid_on: Payment date (YYYY-MM-DD), required for pay event
            paid_amount: Payment amount, required for pay event
        """
        try:
            fa = get_client(ctx)
            kwargs = {}
            if paid_on:
                kwargs["paid_on"] = parse_date(paid_on)
            if paid_amount is not None:
                kwargs["paid_amount"] = paid_amount
            fa.fire_invoice_event(invoice_id, event, **kwargs)
            return json_response({"success": True, "invoice_id": invoice_id, "event": event})
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def create_invoice_payment(
        ctx: Context,
        invoice_id: int,
        paid_on: str,
        amount: float,
        currency: str | None = None,
        mark_document_as_paid: bool = True,
    ) -> str:
        """Record a payment on an invoice.

        Args:
            invoice_id: The invoice ID
            paid_on: Payment date (YYYY-MM-DD)
            amount: Payment amount
            currency: Currency code
            mark_document_as_paid: Whether to mark the invoice as fully paid
        """
        try:
            fa = get_client(ctx)
            kwargs: dict = {
                "paid_on": parse_date(paid_on),
                "amount": amount,
            }
            if currency:
                kwargs["currency"] = currency
            if not mark_document_as_paid:
                kwargs["mark_document_as_paid"] = False
            payment = InvoicePayment(**kwargs)
            fa.save(payment, invoice_id=invoice_id)
            return json_response(model_to_dict(payment))
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def delete_invoice_payment(ctx: Context, invoice_id: int, payment_id: int) -> str:
        """Delete a payment from an invoice.

        Args:
            invoice_id: The invoice ID
            payment_id: The payment ID to delete
        """
        try:
            fa = get_client(ctx)
            fa.delete(InvoicePayment(id=payment_id), invoice_id=invoice_id)
            return json_response({"success": True, "invoice_id": invoice_id, "payment_id": payment_id})
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def send_invoice_message(
        ctx: Context,
        invoice_id: int,
        email: str,
        email_subject: str | None = None,
        email_body: str | None = None,
    ) -> str:
        """Send an invoice via email.

        Args:
            invoice_id: The invoice ID to send
            email: Recipient email address
            email_subject: Custom email subject line
            email_body: Custom email body text
        """
        try:
            fa = get_client(ctx)
            kwargs: dict = {"email": email}
            if email_subject:
                kwargs["subject"] = email_subject
            if email_body:
                kwargs["body"] = email_body
            message = InvoiceMessage(**kwargs)
            fa.save(message, invoice_id=invoice_id)
            return json_response({"success": True, "invoice_id": invoice_id, "email": email})
        except Exception as e:
            return error_response(e)
