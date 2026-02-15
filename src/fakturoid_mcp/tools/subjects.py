"""Subject tools for Fakturoid MCP server."""

from fakturoid import Subject
from mcp.server.fastmcp import Context, FastMCP

from fakturoid_mcp.tools._helpers import (
    error_response,
    get_client,
    json_response,
    model_to_dict,
    parse_date,
)


def register(mcp: FastMCP) -> None:
    """Register subject tools."""

    @mcp.tool()
    def list_subjects(
        ctx: Context,
        since: str | None = None,
        updated_since: str | None = None,
        custom_id: str | None = None,
    ) -> str:
        """List all subjects (contacts/clients) in Fakturoid.

        Args:
            since: Return subjects created since this date (YYYY-MM-DD)
            updated_since: Return subjects updated since this date (YYYY-MM-DD)
            custom_id: Filter by custom identifier
        """
        try:
            fa = get_client(ctx)
            kwargs = {}
            if since:
                kwargs["since"] = parse_date(since)
            if updated_since:
                kwargs["updated_since"] = parse_date(updated_since)
            if custom_id:
                kwargs["custom_id"] = custom_id
            subjects = list(fa.subjects(**kwargs))
            return json_response([model_to_dict(s) for s in subjects])
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def search_subjects(ctx: Context, query: str) -> str:
        """Full-text search for subjects (contacts/clients).

        Args:
            query: Search query string
        """
        try:
            fa = get_client(ctx)
            subjects = fa.subjects.search(query)
            return json_response([model_to_dict(s) for s in subjects])
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def get_subject(ctx: Context, subject_id: int) -> str:
        """Get a single subject (contact/client) by ID.

        Args:
            subject_id: The subject ID
        """
        try:
            fa = get_client(ctx)
            subject = fa.subject(subject_id)
            return json_response(model_to_dict(subject))
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def create_subject(
        ctx: Context,
        name: str,
        street: str | None = None,
        city: str | None = None,
        zip_code: str | None = None,
        country: str | None = None,
        registration_no: str | None = None,
        vat_no: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        web: str | None = None,
        full_name: str | None = None,
        custom_id: str | None = None,
    ) -> str:
        """Create a new subject (contact/client).

        Args:
            name: Company or person name (required)
            street: Street address
            city: City
            zip_code: ZIP/postal code
            country: Country code (e.g. CZ, SK)
            registration_no: Company registration number (ICO)
            vat_no: VAT number (DIC)
            email: Email address
            phone: Phone number
            web: Website URL
            full_name: Full name of contact person
            custom_id: Custom identifier
        """
        try:
            fa = get_client(ctx)
            kwargs = {"name": name}
            if street:
                kwargs["street"] = street
            if city:
                kwargs["city"] = city
            if zip_code:
                kwargs["zip"] = zip_code
            if country:
                kwargs["country"] = country
            if registration_no:
                kwargs["registration_no"] = registration_no
            if vat_no:
                kwargs["vat_no"] = vat_no
            if email:
                kwargs["email"] = email
            if phone:
                kwargs["phone"] = phone
            if web:
                kwargs["web"] = web
            if full_name:
                kwargs["full_name"] = full_name
            if custom_id:
                kwargs["custom_id"] = custom_id
            subject = Subject(**kwargs)
            fa.save(subject)
            return json_response(model_to_dict(subject))
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def update_subject(
        ctx: Context,
        subject_id: int,
        name: str | None = None,
        street: str | None = None,
        city: str | None = None,
        zip_code: str | None = None,
        country: str | None = None,
        registration_no: str | None = None,
        vat_no: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        web: str | None = None,
        full_name: str | None = None,
    ) -> str:
        """Update an existing subject (contact/client).

        Args:
            subject_id: The subject ID to update
            name: Company or person name
            street: Street address
            city: City
            zip_code: ZIP/postal code
            country: Country code (e.g. CZ, SK)
            registration_no: Company registration number (ICO)
            vat_no: VAT number (DIC)
            email: Email address
            phone: Phone number
            web: Website URL
            full_name: Full name of contact person
        """
        try:
            fa = get_client(ctx)
            subject = fa.subject(subject_id)
            fields = {
                "name": name,
                "street": street,
                "city": city,
                "zip": zip_code,
                "country": country,
                "registration_no": registration_no,
                "vat_no": vat_no,
                "email": email,
                "phone": phone,
                "web": web,
                "full_name": full_name,
            }
            for key, value in fields.items():
                if value is not None:
                    setattr(subject, key, value)
            fa.save(subject)
            return json_response(model_to_dict(subject))
        except Exception as e:
            return error_response(e)

    @mcp.tool()
    def delete_subject(ctx: Context, subject_id: int) -> str:
        """Delete a subject (contact/client) by ID.

        Args:
            subject_id: The subject ID to delete
        """
        try:
            fa = get_client(ctx)
            fa.delete(Subject(id=subject_id))
            return json_response({"success": True, "deleted_id": subject_id})
        except Exception as e:
            return error_response(e)
