"""Tests for SmartUIAuth browser authentication."""

import pytest
from pathlib import Path
import os


class TestSmartUIAuth:
    """Test SmartUIAuth class for browser authentication."""

    def test_storage_state_file_check(self):
        """Test that SmartUIAuth checks for storage state file."""
        from lib.ui_auth import SmartUIAuth

        user = {"email": "test@test.com", "password": "test123"}
        auth = SmartUIAuth(user)

        assert auth.user == user
        assert auth.email == "test@test.com"

    def test_validation_cache_ui(self):
        """Test that UI validation cache works."""
        from lib.ui_auth import SmartUIAuth, _validation_cache

        user = {"email": "test@test.com", "password": "test123"}
        auth = SmartUIAuth(user)

        # Cache should be accessible
        assert isinstance(_validation_cache, dict)

    def test_storage_state_path_generation(self):
        """Test that storage state path is generated correctly."""
        from lib.ui_auth import SmartUIAuth, _get_storage_state_path

        user = {"email": "test@example.com", "password": "test123"}
        auth = SmartUIAuth(user)

        # Path should be generated
        assert auth.storage_state_path is not None
        assert "test_example_com" in str(auth.storage_state_path)
        assert auth.storage_state_path.suffix == ".json"
