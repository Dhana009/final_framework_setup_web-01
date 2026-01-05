"""Configuration management for the framework.

This module provides centralized configuration management by loading values
from environment variables with sensible defaults.
"""

import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


class Config:
    """Framework configuration loaded from environment variables.

    All configuration values are loaded from environment variables at module
    import time. If an environment variable is not set, default values are used.

    Attributes:
        API_BASE_URL: Base URL for the backend API
        FRONTEND_BASE_URL: Base URL for the frontend application
        MONGODB_URI: MongoDB connection URI
        MONGODB_DB_NAME: MongoDB database name
        ENABLE_SEED_SETUP: Flag to enable/disable global seed setup
        INTERNAL_AUTOMATION_KEY: Key for internal automation endpoints
    """

    # API Configuration
    # Support both BACKEND_BASE_URL and API_BASE_URL for compatibility
    API_BASE_URL: str = os.getenv("BACKEND_BASE_URL") or os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
    """Base URL for the backend API. Reads BACKEND_BASE_URL or API_BASE_URL. Default: http://localhost:8000/api/v1"""

    FRONTEND_BASE_URL: str = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")
    """Base URL for the frontend application. Default: http://localhost:3000"""

    # MongoDB Configuration
    MONGODB_URI: str | None = os.getenv("MONGODB_URI")
    """MongoDB connection URI. Must be set via environment variable."""

    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "test")
    """MongoDB database name. Default: test"""

    MONGODB_ITEMS_COLLECTION: str = os.getenv("MONGODB_ITEMS_COLLECTION", "items")
    """MongoDB items collection name. Default: items"""

    # Feature Flags
    ENABLE_SEED_SETUP: bool = os.getenv("ENABLE_SEED_SETUP", "false").lower() == "true"
    """Enable global seed setup. Default: False"""

    CLEANUP_SEED_ON_START: bool = os.getenv("CLEANUP_SEED_ON_START", "false").lower() == "true"
    """Cleanup seed data on session start. Default: False"""

    # Internal Automation
    INTERNAL_AUTOMATION_KEY: str = os.getenv(
        "INTERNAL_AUTOMATION_KEY", "flowhub-secret-automation-key-2025"
    )
    """Key for internal automation endpoints. Default: flowhub-secret-automation-key-2025"""
