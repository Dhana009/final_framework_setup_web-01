"""Test that all .env configuration values are loaded and used correctly."""

import pytest
from utils.config import Config


class TestEnvConfigComplete:
    """Test complete .env configuration loading."""

    def test_urls_from_env(self):
        """Test that URLs are loaded from .env."""
        assert Config.FRONTEND_BASE_URL == "https://testing-box.vercel.app"
        assert Config.API_BASE_URL == "https://testing-box.onrender.com/api/v1"
        assert "localhost" not in Config.FRONTEND_BASE_URL
        assert "localhost" not in Config.API_BASE_URL

    def test_flags_from_env(self):
        """Test that feature flags are loaded from .env."""
        assert Config.ENABLE_SEED_SETUP is True
        assert Config.CLEANUP_SEED_ON_START is False

    def test_mongodb_config_from_env(self):
        """Test that MongoDB config is loaded from .env."""
        assert Config.MONGODB_URI is not None
        assert "mongodb+srv://" in Config.MONGODB_URI
        assert Config.MONGODB_DB_NAME == "test"
        assert Config.MONGODB_ITEMS_COLLECTION == "items"

    def test_internal_key_from_env(self):
        """Test that internal automation key is loaded from .env."""
        assert Config.INTERNAL_AUTOMATION_KEY == "flowhub-secret-automation-key-2025"

    def test_all_components_use_config(self):
        """Test that all components use Config values."""
        from utils.api_client import APIClient
        from lib.pages.base_page import BasePage
        from unittest.mock import Mock

        # APIClient should use Config.API_BASE_URL
        api_client = APIClient()
        assert api_client.base_url == Config.API_BASE_URL
        assert api_client.base_url is not None
        assert api_client.base_url.startswith("http://") or api_client.base_url.startswith("https://")

        # BasePage should use Config.FRONTEND_BASE_URL
        base_page = BasePage(Mock())
        assert base_page.base_url == Config.FRONTEND_BASE_URL
        assert base_page.base_url is not None
        assert len(base_page.base_url) > 0
        assert base_page.base_url.startswith("http://") or base_page.base_url.startswith("https://")