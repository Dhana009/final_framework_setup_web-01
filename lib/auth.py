"""Smart authentication for API requests with token caching and validation."""

import json
import time
from typing import Optional, Dict, Any
from pathlib import Path
from utils.api_client import APIClient
from utils.config import Config
from utils.file_lock import AtomicLock


# Session-level validation cache: {email: {valid: bool, timestamp: float}}
_validation_cache: Dict[str, Dict[str, Any]] = {}


def _get_state_path() -> Path:
    """Get path to user state file.

    Returns:
        Path to user_state.json
    """
    return Path("config/user_state.json")


def _load_state() -> Dict[str, Dict[str, Any]]:
    """Load user state file.

    Returns:
        Dictionary mapping user emails to their state
    """
    state_path = _get_state_path()
    if not state_path.exists():
        return {}

    with open(state_path, 'r') as f:
        return json.load(f)


def _save_state(state: Dict[str, Dict[str, Any]]):
    """Save user state file.

    Args:
        state: Dictionary mapping user emails to their state
    """
    state_path = _get_state_path()
    state_path.parent.mkdir(parents=True, exist_ok=True)

    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)


class SmartAuth:
    """Smart authentication manager with token validation and caching.

    This class provides intelligent token management:
    - Validates tokens with 5-minute TTL cache
    - Automatically logs in if token is invalid
    - Refreshes tokens when expired
    - Persists tokens to state file

    Attributes:
        user: User credentials (email, password)
        token: Current authentication token
        api: APIClient instance for API calls
    """

    def __init__(self, user: Dict[str, str], api: Optional[APIClient] = None):
        """Initialize SmartAuth.

        Args:
            user: User credentials with 'email' and 'password'
            api: Optional APIClient instance (creates new if not provided)
        """
        self.user = user
        self.email = user['email']
        self.password = user['password']
        self.api = api or APIClient(base_url=Config.API_BASE_URL)
        self.token: Optional[str] = None

    def get_token(self) -> str:
        """Get valid authentication token.

        This method:
        1. Checks session cache for recent validation (O(1))
        2. Loads token from state file once (O(1))
        3. Validates token via API if needed (O(1) API call)
        4. Auto-login if token is invalid (O(1) API call)
        5. Returns valid token

        Time Complexity: O(1) - all operations are constant time
        Space Complexity: O(1) - minimal state

        Returns:
            Valid authentication token

        Raises:
            Exception: If login fails
        """
        # Check validation cache (5-minute TTL) - O(1) lookup
        if self.email in _validation_cache:
            cache_entry = _validation_cache[self.email]
            age = time.time() - cache_entry['timestamp']
            if age < 300 and cache_entry['valid']:  # 5 minutes = 300 seconds
                # Use cached token - load state once
                state = _load_state()
                auth_state = state.get("auth", {})
                if self.email in auth_state and 'token' in auth_state[self.email]:
                    self.token = auth_state[self.email]['token']
                    self.api.token = self.token
                    return self.token

        # Load state once - O(1) file read
        state = _load_state()
        auth_state = state.get("auth", {})
        
        # Check if token exists in state
        if self.email in auth_state and 'token' in auth_state[self.email]:
            self.token = auth_state[self.email]['token']
            self.api.token = self.token

            # Validate token via API - O(1) API call
            if self._validate_token():
                # Update cache - O(1) dictionary update
                _validation_cache[self.email] = {
                    'valid': True,
                    'timestamp': time.time()
                }
                return self.token

        # Token invalid or missing - login - O(1) API call
        return self._login()

    def _validate_token(self) -> bool:
        """Validate token via GET /auth/me endpoint.

        Returns:
            True if token is valid, False otherwise
        """
        try:
            response = self.api.get("/auth/me")
            return response.status_code == 200
        except Exception:
            return False

    def _login(self) -> str:
        """Login and get new token.

        Time Complexity: O(1) - single API call + single file write
        Space Complexity: O(1) - minimal state

        Returns:
            New authentication token

        Raises:
            Exception: If login fails
        """
        # Login via API - O(1) API call
        response = self.api.post("/auth/login", json={
            "email": self.email,
            "password": self.password
        })

        data = response.json()
        self.token = data['token']
        self.api.token = self.token

        # Save to state file - O(1) file write
        # Use file lock to prevent race conditions with users.py and parallel auth calls
        lock_path = str(_get_state_path()) + ".lock"
        with AtomicLock(lock_path):
            state = _load_state()
            if "auth" not in state:
                state["auth"] = {}
            state["auth"][self.email] = {
                **state["auth"].get(self.email, {}),
                "token": self.token
            }
            _save_state(state)

        # Update cache - O(1) dictionary update
        _validation_cache[self.email] = {
            'valid': True,
            'timestamp': time.time()
        }

        return self.token

    def refresh_token(self) -> str:
        """Refresh authentication token.

        Returns:
            New authentication token

        Raises:
            Exception: If refresh fails
        """
        # Note: Refresh endpoint uses httpOnly cookie, so we need to handle
        # cookies. For now, we'll just re-login if refresh fails.
        try:
            # Try refresh (this may not work without cookie handling)
            response = self.api.post("/auth/refresh")
            data = response.json()
            self.token = data['token']
            self.api.token = self.token

            # Save to state
            # Use file lock to prevent race conditions with users.py and parallel auth calls
            lock_path = str(_get_state_path()) + ".lock"
            with AtomicLock(lock_path):
                state = _load_state()
                if "auth" not in state:
                    state["auth"] = {}
                state["auth"][self.email] = {
                    **state["auth"].get(self.email, {}),
                    "token": self.token
                }
                _save_state(state)

            # Update cache
            _validation_cache[self.email] = {
                'valid': True,
                'timestamp': time.time()
            }

            return self.token
        except Exception:
            # Fallback to login
            return self._login()
