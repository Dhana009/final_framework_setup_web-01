"""Test data factory for generating seed data."""

import uuid
from typing import Dict, Any, Optional
from enum import Enum


class ItemType(str, Enum):
    """Item type enumeration."""
    PHYSICAL = "PHYSICAL"
    DIGITAL = "DIGITAL"
    SERVICE = "SERVICE"


class Category(str, Enum):
    """Category enumeration."""
    ELECTRONICS = "Electronics"
    SOFTWARE = "Software"
    SERVICES = "Services"
    BOOKS = "Books"
    CLOTHING = "Clothing"


class SeedFactory:
    """Factory for generating test data items.

    This factory generates valid test data according to the backend schemas.
    It ensures category-item type compatibility and generates all required fields.
    """

    @staticmethod
    def generate_item(
        item_type: ItemType,
        category: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a test item with all required fields.

        Args:
            item_type: Type of item (PHYSICAL, DIGITAL, SERVICE)
            category: Item category (optional, will be auto-selected if not provided)
            name: Item name (optional, will be auto-generated if not provided)
            **kwargs: Additional fields to override

        Returns:
            Dictionary with item data ready for API/MongoDB insertion
        """
        # Auto-select category based on item type if not provided
        if not category:
            category_map = {
                ItemType.PHYSICAL: Category.ELECTRONICS.value,
                ItemType.DIGITAL: Category.SOFTWARE.value,
                ItemType.SERVICE: Category.SERVICES.value,
            }
            category = category_map.get(item_type, Category.ELECTRONICS.value)

        # Generate name if not provided
        if not name:
            name = f"Test {item_type.value} Item {uuid.uuid4().hex[:8]}"

        # Base item structure
        item = {
            "name": name,
            "description": f"Test description for {name}",
            "item_type": item_type.value,
            "price": kwargs.get("price", 99.99),
            "category": category,
            "is_active": kwargs.get("is_active", True),
        }

        # Add conditional fields based on item type
        if item_type == ItemType.PHYSICAL:
            item.update({
                "weight": kwargs.get("weight", 1.5),
                "dimensions": kwargs.get("dimensions", {
                    "length": 10.0,
                    "width": 5.0,
                    "height": 3.0
                })
            })
        elif item_type == ItemType.DIGITAL:
            item.update({
                "download_url": kwargs.get("download_url", "https://example.com/download"),
                "file_size": kwargs.get("file_size", 1024000)  # 1MB in bytes
            })
        elif item_type == ItemType.SERVICE:
            item.update({
                "duration_hours": kwargs.get("duration_hours", 2.0)
            })

        # Add optional fields if provided
        if "tags" in kwargs:
            item["tags"] = kwargs["tags"]
        if "embed_url" in kwargs:
            item["embed_url"] = kwargs["embed_url"]

        return item

    @staticmethod
    def generate_physical_item(**kwargs) -> Dict[str, Any]:
        """Generate a PHYSICAL item.

        Args:
            **kwargs: Override any fields

        Returns:
            Dictionary with PHYSICAL item data
        """
        return SeedFactory.generate_item(ItemType.PHYSICAL, **kwargs)

    @staticmethod
    def generate_digital_item(**kwargs) -> Dict[str, Any]:
        """Generate a DIGITAL item.

        Args:
            **kwargs: Override any fields

        Returns:
            Dictionary with DIGITAL item data
        """
        return SeedFactory.generate_item(ItemType.DIGITAL, **kwargs)

    @staticmethod
    def generate_service_item(**kwargs) -> Dict[str, Any]:
        """Generate a SERVICE item.

        Args:
            **kwargs: Override any fields

        Returns:
            Dictionary with SERVICE item data
        """
        return SeedFactory.generate_item(ItemType.SERVICE, **kwargs)
