"""
Tests for Example Tools
=======================
"""

import json

import pytest


class TestEchoTool:
    """Tests for echo tool."""

    @pytest.mark.asyncio
    async def test_echo_returns_message(self) -> None:
        from marketing_connect_mcp_services.tools.example import echo

        result = await echo("Hello, World!")
        assert result == "Echo: Hello, World!"


class TestFormatTextTool:
    """Tests for format_text tool."""

    @pytest.mark.asyncio
    async def test_format_default(self) -> None:
        from marketing_connect_mcp_services.tools.example import format_text

        result = await format_text("hello")
        assert result == "hello"

    @pytest.mark.asyncio
    async def test_format_uppercase(self) -> None:
        from marketing_connect_mcp_services.tools.example import format_text

        result = await format_text("hello", uppercase=True)
        assert result == "HELLO"

    @pytest.mark.asyncio
    async def test_format_with_prefix_suffix(self) -> None:
        from marketing_connect_mcp_services.tools.example import format_text

        result = await format_text("hello", prefix=">>> ", suffix=" <<<")
        assert result == ">>> hello <<<"


class TestProcessItemsTool:
    """Tests for process_items tool."""

    @pytest.mark.asyncio
    async def test_process_basic(self) -> None:
        from marketing_connect_mcp_services.tools.example import process_items

        result = await process_items(["a", "b", "c"])
        data = json.loads(result)

        assert data["processed"] == ["a", "b", "c"]
        assert data["count"] == 3

    @pytest.mark.asyncio
    async def test_process_with_reverse(self) -> None:
        from marketing_connect_mcp_services.tools.example import process_items

        result = await process_items(["a", "b", "c"], {"reverse": True})
        data = json.loads(result)

        assert data["processed"] == ["c", "b", "a"]

    @pytest.mark.asyncio
    async def test_process_with_limit(self) -> None:
        from marketing_connect_mcp_services.tools.example import process_items

        result = await process_items(["a", "b", "c", "d"], {"limit": 2})
        data = json.loads(result)

        assert data["processed"] == ["a", "b"]
        assert data["count"] == 2


class TestDivideTool:
    """Tests for divide tool."""

    @pytest.mark.asyncio
    async def test_divide_success(self) -> None:
        from marketing_connect_mcp_services.tools.example import divide

        result = await divide(10, 2)
        data = json.loads(result)

        assert data["success"] is True
        assert data["result"] == 5.0

    @pytest.mark.asyncio
    async def test_divide_by_zero(self) -> None:
        from marketing_connect_mcp_services.tools.example import divide

        result = await divide(10, 0)
        data = json.loads(result)

        assert data["success"] is False
        assert "zero" in data["error"].lower()


class TestCalculateTool:
    """Tests for calculate tool."""

    @pytest.mark.asyncio
    async def test_calculate_simple(self) -> None:
        from marketing_connect_mcp_services.tools.example import calculate

        result = await calculate("2 + 3")
        data = json.loads(result)

        assert data["success"] is True
        assert data["result"] == 5

    @pytest.mark.asyncio
    async def test_calculate_complex(self) -> None:
        from marketing_connect_mcp_services.tools.example import calculate

        result = await calculate("(10 - 3) * 2")
        data = json.loads(result)

        assert data["success"] is True
        assert data["result"] == 14

    @pytest.mark.asyncio
    async def test_calculate_invalid_chars(self) -> None:
        from marketing_connect_mcp_services.tools.example import calculate

        result = await calculate("import os")
        data = json.loads(result)

        assert data["success"] is False
        assert "invalid" in data["error"].lower()
