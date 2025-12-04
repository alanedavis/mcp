"""
Tests for Configuration
=======================
"""

import os
from unittest.mock import patch

import pytest


class TestSettings:
    """Tests for Settings class."""

    def test_default_values(self) -> None:
        from marketing_connect_mcp_services.config import Settings

        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()

        assert settings.server_name == "marketing-connect-mcp-services"
        assert settings.debug is False
        assert settings.port == 8000
        assert settings.base_url == ""
        assert settings.region == ""

    def test_env_override(self) -> None:
        from marketing_connect_mcp_services.config import Settings

        with patch.dict(os.environ, {
            "MCP_SERVER_NAME": "custom-server",
            "MCP_DEBUG": "true",
            "MCP_PORT": "3000",
            "MCP_BASE_URL": "http://example.com",
            "MCP_REGION": "us-east-1",
        }, clear=True):
            settings = Settings()

        assert settings.server_name == "custom-server"
        assert settings.debug is True
        assert settings.port == 3000
        assert settings.base_url == "http://example.com"
        assert settings.region == "us-east-1"


class TestGetSettings:
    """Tests for get_settings function."""

    def test_singleton(self) -> None:
        from marketing_connect_mcp_services.config import get_settings

        get_settings.cache_clear()

        s1 = get_settings()
        s2 = get_settings()

        assert s1 is s2

    def test_cache_clear(self) -> None:
        from marketing_connect_mcp_services.config import get_settings

        get_settings.cache_clear()
        s1 = get_settings()

        get_settings.cache_clear()
        s2 = get_settings()

        assert s1 is not s2
