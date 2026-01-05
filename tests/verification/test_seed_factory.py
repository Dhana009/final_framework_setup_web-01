"""Tests for seed factory."""

import pytest
from fixtures.seed_factory import SeedFactory, ItemType, Category


class TestSeedFactory:
    """Test SeedFactory for generating test data."""

    def test_basic_item_generation(self):
        """Test generating a basic item."""
        item = SeedFactory.generate_item(ItemType.PHYSICAL)
        
        assert item is not None
        assert "name" in item
        assert "description" in item
        assert "item_type" in item
        assert item["item_type"] == "PHYSICAL"

    def test_physical_item_generation(self):
        """Test generating PHYSICAL item with required fields."""
        item = SeedFactory.generate_physical_item()
        
        assert item["item_type"] == "PHYSICAL"
        assert "weight" in item
        assert "dimensions" in item
        assert "length" in item["dimensions"]
        assert "width" in item["dimensions"]
        assert "height" in item["dimensions"]

    def test_digital_item_generation(self):
        """Test generating DIGITAL item."""
        item = SeedFactory.generate_digital_item()
        
        assert item["item_type"] == "DIGITAL"
        assert "download_url" in item
        assert "file_size" in item

    def test_service_item_generation(self):
        """Test generating SERVICE item."""
        item = SeedFactory.generate_service_item()
        
        assert item["item_type"] == "SERVICE"
        assert "duration_hours" in item

    def test_category_item_type_compatibility(self):
        """Test category-item type compatibility rules."""
        # Electronics should be PHYSICAL
        item = SeedFactory.generate_item(ItemType.PHYSICAL, category=Category.ELECTRONICS.value)
        assert item["category"] == Category.ELECTRONICS.value
        assert item["item_type"] == "PHYSICAL"
        
        # Software should be DIGITAL
        item = SeedFactory.generate_item(ItemType.DIGITAL, category=Category.SOFTWARE.value)
        assert item["category"] == Category.SOFTWARE.value
        assert item["item_type"] == "DIGITAL"
        
        # Services should be SERVICE
        item = SeedFactory.generate_item(ItemType.SERVICE, category=Category.SERVICES.value)
        assert item["category"] == Category.SERVICES.value
        assert item["item_type"] == "SERVICE"
