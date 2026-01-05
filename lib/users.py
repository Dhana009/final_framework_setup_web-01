"""User pool management for parallel test execution.

This module provides thread-safe user pool management for parallel test
execution. It uses file-based locking to coordinate user acquisition
across multiple test workers (pytest-xdist).

Key Features:
- Session-level config caching for performance
- File-based locking for cross-process coordination
- Fail-fast when no users available
- Automatic user release via context manager
"""

import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from utils.file_lock import AtomicLock


# Session-level config cache (loaded once per test session)
_config_cache: Optional[Dict[str, List[Dict[str, str]]]] = None


def _load_config() -> Dict[str, List[Dict[str, str]]]:
    """Load user pool configuration with session-level caching.

    Returns:
        Dictionary mapping roles to lists of user credentials
    """
    global _config_cache

    if _config_cache is not None:
        return _config_cache

    config_path = Path("config/user_pool.json")
    if not config_path.exists():
        raise FileNotFoundError(f"User pool config not found: {config_path}")

    with open(config_path, 'r') as f:
        _config_cache = json.load(f)

    return _config_cache


def _get_state_path() -> Path:
    """Get path to user state file.

    Returns:
        Path to user_state.json
    """
    return Path("config/user_state.json")


def _load_state() -> Dict[str, Dict[str, str]]:
    """Load user state file.

    Returns:
        Dictionary mapping user emails to their state
    """
    state_path = _get_state_path()
    if not state_path.exists():
        return {}

    with open(state_path, 'r') as f:
        return json.load(f)


def _save_state(state: Dict[str, Dict[str, str]]):
    """Save user state file.

    Args:
        state: Dictionary mapping user emails to their state
    """
    state_path = _get_state_path()
    state_path.parent.mkdir(parents=True, exist_ok=True)

    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)


class InfrastructureError(Exception):
    """Raised when infrastructure issues prevent test execution."""
    pass


class UserLease:
    """Manages user acquisition and release for parallel test execution.

    This class provides thread-safe user pool management using file-based
    locking. It ensures that users are not double-allocated across parallel
    test workers.

    Attributes:
        role: User role (ADMIN, EDITOR, VIEWER)
        user: Acquired user credentials (email, password)
        _acquired: Whether a user has been acquired
    """

    def __init__(self, role: str):
        """Initialize UserLease.

        Args:
            role: User role (ADMIN, EDITOR, VIEWER)
        """
        self.role = role.upper()
        self.user: Optional[Dict[str, str]] = None
        self._acquired = False

    def acquire(self) -> Dict[str, str]:
        """Acquire a free user from the pool.

        This method uses file-based locking to ensure thread-safe user
        acquisition. It finds the first available user for the specified
        role and marks it as BUSY in the state file.

        Time Complexity: O(1) config lookup (cached) + O(n) user search
        - Config lookup: O(1) - dictionary lookup from cache
        - Lock acquisition: O(1) - single file operation
        - State file read: O(1) - single file read
        - User search: O(n) where n = users for role (optimal, cannot be better)
        - State file write: O(1) - single file write
        - Total: O(n) where n = users for role

        Space Complexity: O(1) - minimal state, config cached at session level

        Optimizations:
        - Config caching: O(1) lookup instead of O(1) file read
        - Early exit: Check candidates before acquiring lock
        - Minimized lock hold time: Only during critical section

        Returns:
            Dictionary with user credentials (email, password)

        Raises:
            InfrastructureError: If no users are available
            FileNotFoundError: If config file doesn't exist
        """
        if self._acquired:
            raise RuntimeError("User already acquired by this instance")

        # Load config (cached)
        config = _load_config()

        # Check if role exists
        if self.role not in config:
            raise ValueError(f"Unknown role: {self.role}")

        candidates = config[self.role]

        # Early exit: check if any candidates exist
        if not candidates:
            raise InfrastructureError(f"No users available for role: {self.role}")

        # Acquire lock and find free user
        lock_path = str(_get_state_path()) + ".lock"
        with AtomicLock(lock_path):
            # Load state
            state = _load_state()

            # Find first free user
            free_user = None
            for user in candidates:
                email = user['email']
                if email not in state:
                    # User is free
                    free_user = user
                    break

            if free_user is None:
                raise InfrastructureError(
                    f"No free users available for role: {self.role}. "
                    f"All {len(candidates)} users are currently in use."
                )

            # Mark user as BUSY
            email = free_user['email']
            state[email] = {
                "role": self.role,
                "status": "BUSY"
            }

            # Save state
            _save_state(state)

            # Store user
            self.user = free_user
            self._acquired = True

            return free_user

    def release(self):
        """Release the acquired user back to the pool.

        This method removes the user from the state file, making it
        available for other tests.
        """
        if not self._acquired or self.user is None:
            return

        lock_path = str(_get_state_path()) + ".lock"
        with AtomicLock(lock_path):
            # Load state
            state = _load_state()

            # Remove user from state
            email = self.user['email']
            if email in state:
                del state[email]

            # Save state
            _save_state(state)

            # Reset
            self.user = None
            self._acquired = False

    def __enter__(self):
        """Context manager entry."""
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
        return False
