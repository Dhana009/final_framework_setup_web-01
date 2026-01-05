"""Tests for pytest hooks."""

import pytest
import json
import os
from pathlib import Path


class TestSessionHooks:
    """Test pytest session hooks."""

    def test_session_start_hook_exists(self):
        """Test that pytest_sessionstart hook exists."""
        from tests.plugins import hooks
        
        assert hasattr(hooks, 'pytest_sessionstart')
        assert callable(hooks.pytest_sessionstart)

    def test_state_file_reset(self):
        """Test that state file is reset to empty dict."""
        from tests.plugins.hooks import pytest_sessionstart
        from unittest.mock import Mock

        # Create a mock session
        session = Mock()

        # Create state file with some data
        state_path = Path("config/user_state.json")
        state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(state_path, 'w') as f:
            json.dump({"user1@test.com": {"role": "ADMIN", "status": "BUSY"}}, f)

        # Run hook
        pytest_sessionstart(session)

        # Verify state file is empty
        assert state_path.exists()
        with open(state_path, 'r') as f:
            state = json.load(f)
            assert state == {}

        # Cleanup
        if state_path.exists():
            os.remove(state_path)
