"""Smoke tests for critical functionality."""

import pytest


class TestSmoke:
    """Smoke tests to verify basic framework functionality."""

    def test_user_pool_available(self):
        """Test that user pool is available."""
        from lib.users import UserLease

        # Should be able to acquire a user
        with UserLease(role="ADMIN") as lease:
            assert lease.user is not None
            assert "email" in lease.user
            assert "password" in lease.user

    def test_api_authentication(self, admin_actor):
        """Test that API authentication works."""
        assert admin_actor["token"] is not None
        assert len(admin_actor["token"]) > 0
        assert admin_actor["api"] is not None

    def test_seed_factory(self):
        """Test that seed factory generates valid data."""
        from fixtures.seed_factory import SeedFactory, ItemType

        item = SeedFactory.generate_item(ItemType.PHYSICAL)
        assert item is not None
        assert "name" in item
        assert "item_type" in item
        assert item["item_type"] == "PHYSICAL"

    def test_config_loading(self):
        """Test that config loads correctly."""
        from utils.config import Config

        assert Config.API_BASE_URL is not None
        assert Config.FRONTEND_BASE_URL is not None
