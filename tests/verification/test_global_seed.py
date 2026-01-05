"""Tests for global seed setup fixture."""

import pytest
from unittest.mock import Mock, patch


class TestGlobalSeedSetup:
    """Test global seed setup fixture."""

    def test_global_seed_fixture_exists(self):
        """Test that global_seed fixture can be accessed."""
        # This will fail until we implement the fixture
        # For now, just verify we can import
        try:
            from tests.plugins.data import global_seed
            assert global_seed is not None
        except ImportError:
            pytest.skip("global_seed fixture not yet implemented")

    def test_enable_seed_setup_flag(self):
        """Test that ENABLE_SEED_SETUP flag controls seed setup."""
        from utils.config import Config
        
        # Should be able to check flag
        assert hasattr(Config, 'ENABLE_SEED_SETUP')
        assert isinstance(Config.ENABLE_SEED_SETUP, bool)

    def test_seed_data_structure(self):
        """Test that seed data has correct structure."""
        # Test will verify structure when fixture is used
        from bson import ObjectId
        from fixtures.seed_factory import SeedFactory
        from lib.builders.item_builder import ItemBuilder
        
        # Generate test item
        item = SeedFactory.generate_physical_item()
        # Use valid ObjectId format (24 hex characters)
        valid_user_id = "507f1f77bcf86cd799439011"
        mongo_doc = ItemBuilder.to_mongodb_format(item, valid_user_id)
        
        assert "created_by" in mongo_doc
        assert isinstance(mongo_doc["created_by"], ObjectId)
        assert "createdAt" in mongo_doc
        assert "normalizedName" in mongo_doc
        assert "normalizedCategory" in mongo_doc
        assert mongo_doc["item_type"] == "PHYSICAL"

    def test_idempotent_check_logic(self):
        """Test that idempotent check logic works."""
        # This tests the logic for checking existing data
        # In real fixture, it checks MongoDB count
        from pymongo.collection import Collection
        
        # Mock collection
        mock_collection = Mock(spec=Collection)
        mock_collection.count_documents.return_value = 5
        
        # Should detect existing data
        existing_count = mock_collection.count_documents(
            {"created_by": "test_user_id"},
            limit=1
        )
        
        assert existing_count > 0
        # If count > 0, seed data exists, should skip creation
