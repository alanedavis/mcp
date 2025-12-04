"""
Configuration Management
========================

Centralized settings loaded from environment variables.

USAGE:
------
    from marketing_connect_mcp_services.config import settings

    print(settings.server_name)
    print(settings.base_url)
    print(settings.debug)
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings from environment variables.

    All settings can be overridden via environment variables.
    Prefix: MCP_ (e.g., MCP_DEBUG=true)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="MCP_",
        case_sensitive=False,
        extra="ignore",
    )

    # -------------------------------------------------------------------------
    # Server Identity
    # -------------------------------------------------------------------------
    server_name: str = Field(
        default="marketing-connect-mcp-services",
        description="Name of this MCP server",
    )

    server_version: str = Field(
        default="1.0.0",
        description="Version of this MCP server",
    )

    # -------------------------------------------------------------------------
    # Server Configuration
    # -------------------------------------------------------------------------
    host: str = Field(
        default="0.0.0.0",
        description="Host to bind HTTP server to",
    )

    port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Port for HTTP server",
    )

    # -------------------------------------------------------------------------
    # Development / Logging
    # -------------------------------------------------------------------------
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )

    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)",
    )

    # -------------------------------------------------------------------------
    # Application Settings
    # -------------------------------------------------------------------------
    base_url: str = Field(
        default="",
        description="Base URL for the application",
    )

    region: str = Field(
        default="",
        description="Deployment region",
    )

    # -------------------------------------------------------------------------
    # ADD YOUR SETTINGS HERE
    # -------------------------------------------------------------------------
    # Example: API integration settings
    #
    # api_key: str = Field(
    #     default="",
    #     description="API key for authentication",
    # )


@lru_cache
def get_settings() -> Settings:
    """
    Get settings singleton.

    Cached to avoid re-parsing environment on every access.
    Call get_settings.cache_clear() to reload.
    """
    return Settings()


# Convenience export
settings = get_settings()
