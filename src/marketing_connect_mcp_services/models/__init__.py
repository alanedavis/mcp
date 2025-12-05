"""
Generated Models
================

This directory contains Pydantic models generated from OpenAPI schemas
in the central OpenAPI repository.

IMPORTANT: Do NOT manually edit files in this directory (except this __init__.py).
Generated files will be overwritten when models are updated.

SETUP:
------
    # Place the generated models .tar.gz in the project root, then:
    make fetch-models

    # Or fetch from a URL:
    make fetch-models-url MODELS_URL=https://your-artifact-repo/models.tar.gz

USAGE:
------
    from marketing_connect_mcp_services.models import UserDetails, ProductDetails

    # Use in tools
    @mcp.tool()
    async def greet_user(user: UserDetails) -> str:
        return f"Hello {user.name}"

AVAILABLE MODELS (after fetch-models):
--------------------------------------
    - UserDetails: User information with userSid and name
    - ProductDetails: Product information with productId, name, price, etc.

See the OpenAPI repository for the full schema definitions.
"""

# Try to import generated models
# This will fail gracefully if models haven't been fetched yet
try:
    from .generated import *  # noqa: F401, F403  # type: ignore[import-untyped]
except ImportError:
    import logging

    logger = logging.getLogger(__name__)
    logger.warning(
        "Generated models not found. Run 'make fetch-models' to download them. "
        "Using fallback stub models for development."
    )

    # Fallback stub models for development when generated models aren't available
    # Field names use camelCase to match OpenAPI/JSON conventions
    from pydantic import BaseModel, Field

    class UserDetails(BaseModel):
        """Stub model - replace by running 'make fetch-models'."""

        userSid: str = Field(..., description="User security ID")
        name: str = Field(..., description="User's full name")

    class ProductDetails(BaseModel):
        """Stub model - replace by running 'make fetch-models'."""

        productId: str = Field(..., description="Product ID")
        name: str = Field(..., description="Product name")
        description: str = Field(default="", description="Product description")
        price: float = Field(default=0.0, ge=0, description="Product price")
        category: str = Field(default="", description="Product category")
        inStock: bool = Field(default=True, description="In stock")
        tags: list[str] = Field(default_factory=list, description="Product tags")

    __all__ = ["UserDetails", "ProductDetails"]
