"""
Tests for Health Check Endpoints
================================
"""

import pytest
from starlette.testclient import TestClient


class TestHealthEndpoints:
    """Tests for the health check endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client for the application."""
        from marketing_connect_mcp_services.cli import create_health_app

        app = create_health_app()
        return TestClient(app)

    def test_root_endpoint(self, client) -> None:
        """Test the root endpoint returns service info."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "endpoints" in data
        assert data["status"] == "running"

    def test_health_endpoint(self, client) -> None:
        """Test the health endpoint returns UP status."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "UP"
        assert "timestamp" in data

    def test_info_endpoint(self, client) -> None:
        """Test the info endpoint returns server metadata."""
        response = client.get("/info")
        assert response.status_code == 200

        data = response.json()
        assert "app" in data
        assert "server" in data
        assert "config" in data
        assert "runtime" in data

        # Check app section
        assert data["app"]["name"] == "test-server"  # From conftest mock
        assert "version" in data["app"]

        # Check server section
        assert "host" in data["server"]
        assert "port" in data["server"]
        assert "debug" in data["server"]

        # Check runtime section
        assert "start_time" in data["runtime"]
        assert "uptime_seconds" in data["runtime"]
