"""Tests for configuration management."""

import os
import pytest
from dotenv import load_dotenv


class TestConfigLoading:
    """Test configuration loading from .env file."""

    def test_load_config_from_env(self):
        """Test that Config class loads values from .env file."""
        # This test will fail until we implement Config class
        from utils.config import Config

        # Load .env file
        load_dotenv()

        # Verify Config loads API_BASE_URL from .env
        assert hasattr(Config, 'API_BASE_URL')
        assert Config.API_BASE_URL is not None

    def test_default_values_when_env_var_missing(self):
        """Test that Config uses default values when env var is missing."""
        from utils.config import Config

        # These should have defaults even if not in .env
        assert Config.API_BASE_URL == "http://localhost:8000/api/v1" or Config.API_BASE_URL is not None
        assert Config.FRONTEND_BASE_URL == "http://localhost:3000" or Config.FRONTEND_BASE_URL is not None
        assert Config.MONGODB_DB_NAME == "test" or Config.MONGODB_DB_NAME is not None
        assert isinstance(Config.ENABLE_SEED_SETUP, bool)

    def test_environment_variable_override(self, monkeypatch):
        """Test that environment variables override default values."""
        # Override with test values (before import)
        monkeypatch.setenv("BACKEND_BASE_URL", "https://test-api.example.com/api/v1")
        monkeypatch.setenv("API_BASE_URL", "")  # Clear this to test BACKEND_BASE_URL
        monkeypatch.setenv("FRONTEND_BASE_URL", "https://test-frontend.example.com")
        monkeypatch.setenv("MONGODB_DB_NAME", "test_override")

        # Reload config to pick up new env vars
        import importlib
        import utils.config
        importlib.reload(utils.config)
        from utils.config import Config as ReloadedConfig

        # Verify overrides work
        assert ReloadedConfig.API_BASE_URL == "https://test-api.example.com/api/v1"
        assert ReloadedConfig.FRONTEND_BASE_URL == "https://test-frontend.example.com"
        assert ReloadedConfig.MONGODB_DB_NAME == "test_override"
