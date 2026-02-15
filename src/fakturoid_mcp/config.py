"""Configuration management for Fakturoid MCP server."""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Fakturoid MCP server configuration.

    Priority (highest to lowest):
    1. Environment variables (FAKTUROID_ prefix)
    2. .env file
    3. Defaults
    """

    slug: str = Field(description="Fakturoid account slug")
    email: str = Field(description="Fakturoid account email")
    client_id: str = Field(description="OAuth Client ID")
    client_secret: SecretStr = Field(description="OAuth Client Secret")
    user_agent: str = Field(
        default="FakturoidMCP (mcp@example.com)",
        description="User-Agent header for Fakturoid API",
    )

    transport: str = Field(default="stdio", description="MCP transport: stdio or streamable-http")
    host: str = Field(default="0.0.0.0", description="HTTP server host")
    port: int = Field(default=8000, description="HTTP server port")

    model_config = SettingsConfigDict(
        env_prefix="FAKTUROID_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
