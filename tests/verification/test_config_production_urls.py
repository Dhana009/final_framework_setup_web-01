"""Test that framework uses production URLs from .env."""

import pytest
from utils.config import Config


class TestProductionURLs:
    """Test that framework uses production URLs from .env file."""

    def test_backend_url_from_env(self):
        """Test that BACKEND_BASE_URL is loaded from .env."""
        # Should use production URL from .env, not localhost
        assert Config.API_BASE_URL is not None
        assert "localhost" not in Config.API_BASE_URL or Config.API_BASE_URL.startswith("https://")
        # Should be the production URL
        assert Config.API_BASE_URL == "https://testing-box.onrender.com/api/v1"

    def test_frontend_url_from_env(self):
        """Test that FRONTEND_BASE_URL is loaded from .env."""
        # Should use production URL from .env, not localhost
        assert Config.FRONTEND_BASE_URL is not None
        assert "localhost" not in Config.FRONTEND_BASE_URL or Config.FRONTEND_BASE_URL.startswith("https://")
        # Should be the production URL
        assert Config.FRONTEND_BASE_URL == "https://testing-box.vercel.app"

    def test_cleanup_seed_flag_from_env(self):
        """Test that CLEANUP_SEED_ON_START is loaded from .env."""
        # Should be False from .env
        assert Config.CLEANUP_SEED_ON_START is False

    def test_api_client_uses_config_url(self):
        """Test that APIClient uses Config.API_BASE_URL by default."""
        from utils.api_client import APIClient

        # APIClient should default to Config.API_BASE_URL
        client = APIClient()
        assert client.base_url == Config.API_BASE_URL
        assert client.base_url == "https://testing-box.onrender.com/api/v1"
        
        # Verify it uses the production URL, not localhost
        assert "localhost" not in client.base_url

    def test_base_page_uses_config_url(self):
        """Test that BasePage uses Config.FRONTEND_BASE_URL."""
        from lib.pages.base_page import BasePage
        from unittest.mock import Mock

        mock_page = Mock()
        base_page = BasePage(mock_page)
        
        # BasePage should use Config.FRONTEND_BASE_URL
        # Verify integration: BasePage gets URL from Config, not hardcoded
        assert base_page.base_url == Config.FRONTEND_BASE_URL
        # Verify it's not using a hardcoded default
        assert base_page.base_url is not None
        assert len(base_page.base_url) > 0
        # Verify it's a valid URL format
        assert base_page.base_url.startswith("http://") or base_page.base_url.startswith("https://")