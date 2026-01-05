"""Pytest hooks for session management."""

import json
import os
from pathlib import Path
from utils.file_lock import AtomicLock


def pytest_sessionstart(session):
    """Reset user state file at the start of each test session.

    This hook runs once at the beginning of the test session (before any
    tests run). It resets the user_state.json file to an empty state,
    ensuring a clean slate for user acquisition.

    This is the "morning roll call" - it recovers from any crashes or
    incomplete test runs by clearing the state file.

    Args:
        session: Pytest session object
    """
    state_path = Path("config/user_state.json")
    lock_path = str(state_path) + ".lock"

    # Use file lock to ensure atomic reset
    with AtomicLock(lock_path):
        # Reset state file to empty
        state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(state_path, 'w') as f:
            json.dump({}, f)
