"""Tests for ItemBuilder."""

import pytest
from bson import ObjectId
from lib.builders.item_builder import ItemBuilder
from fixtures.seed_factory import SeedFactory


class TestItemBuilder:
    """Test ItemBuilder for data transformation."""

    def test_data_transformation(self):
        """Test transforming factory data."""
        # Generate item from factory
        item_data = SeedFactory.generate_physical_item()
        
        # Transform to MongoDB format
        user_id = "507f1f77bcf86cd799439011"
        mongo_doc = ItemBuilder.to_mongodb_format(item_data, user_id)
        
        assert mongo_doc is not None
        assert "created_by" in mongo_doc
        assert isinstance(mongo_doc["created_by"], ObjectId)
        assert "createdAt" in mongo_doc
        assert "updatedAt" in mongo_doc
        assert "normalizedName" in mongo_doc
        assert "normalizedCategory" in mongo_doc

    def test_mongodb_format(self):
        """Test converting to MongoDB format."""
        item_data = SeedFactory.generate_digital_item()
        user_id = "507f1f77bcf86cd799439011"
        
        mongo_doc = ItemBuilder.to_mongodb_format(item_data, user_id)
        
        assert mongo_doc["item_type"] == "DIGITAL"
        assert "created_by" in mongo_doc
        assert isinstance(mongo_doc["created_by"], ObjectId)
        assert "version" in mongo_doc
        assert mongo_doc["version"] == 1
        assert "normalizedName" in mongo_doc
        assert "normalizedCategory" in mongo_doc

    def test_normalization(self):
        """Test name and category normalization."""
        # Test name normalization (lowercase + trim)
        assert ItemBuilder._normalize_name("  Test Item  ") == "test item"
        assert ItemBuilder._normalize_name("TEST ITEM") == "test item"
        assert ItemBuilder._normalize_name("Test Item") == "test item"
        
        # Test category normalization (Title Case)
        assert ItemBuilder._normalize_category("electronics") == "Electronics"
        assert ItemBuilder._normalize_category("ELECTRONICS") == "Electronics"
        assert ItemBuilder._normalize_category("  electronics  ") == "Electronics"
        assert ItemBuilder._normalize_category("software") == "Software"

    def test_api_format(self):
        """Test converting to API format."""
        item_data = SeedFactory.generate_service_item()
        
        api_data = ItemBuilder.to_api_format(item_data)
        
        assert api_data["item_type"] == "SERVICE"
        assert "created_by" not in api_data
        assert "createdAt" not in api_data
        assert "version" not in api_data
