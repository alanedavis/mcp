"""
Pytest Configuration
====================

Shared fixtures for all tests.
"""

import os
from collections.abc import Generator
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def mock_env() -> Generator[None, None, None]:
    """Set test environment variables."""
    test_env = {
        "MCP_SERVER_NAME": "test-server",
        "MCP_DEBUG": "true",
        "MCP_LOG_LEVEL": "DEBUG",
        "MCP_BASE_URL": "http://test.example.com",
        "MCP_REGION": "test-region",
    }

    with patch.dict(os.environ, test_env, clear=False):
        from marketing_connect_mcp_services.config import get_settings
        get_settings.cache_clear()
        yield
        get_settings.cache_clear()
