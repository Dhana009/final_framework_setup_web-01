"""Smart browser authentication with Playwright storage state reuse."""

import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright
from utils.config import Config


# Session-level validation cache: {email: {valid: bool, timestamp: float}}
_validation_cache: Dict[str, Dict[str, Any]] = {}


def _get_storage_state_path(email: str) -> Path:
    """Get path to storage state file for a user.

    Args:
        email: User email

    Returns:
        Path to storage state file
    """
    state_dir = Path("state")
    state_dir.mkdir(exist_ok=True)
    # Sanitize email for filename
    safe_email = email.replace("@", "_").replace(".", "_")
    return state_dir / f"{safe_email}_storage.json"


class SmartUIAuth:
    """Smart browser authentication manager with storage state reuse.

    This class provides intelligent browser authentication:
    - Reuses Playwright storage state files when valid
    - Validates state by navigating to protected page
    - Automatically logs in if state is invalid
    - Caches validation results (5-minute TTL)

    Attributes:
        user: User credentials (email, password)
        email: User email
        password: User password
        storage_state_path: Path to storage state file
    """

    def __init__(self, user: Dict[str, str]):
        """Initialize SmartUIAuth.

        Args:
            user: User credentials with 'email' and 'password'
        """
        self.user = user
        self.email = user['email']
        self.password = user['password']
        self.storage_state_path = _get_storage_state_path(self.email)

    def get_storage_state(self, browser: Browser) -> str:
        """Get valid storage state path for browser context.

        This method:
        1. Checks validation cache (5-minute TTL)
        2. Checks if storage state file exists
        3. Validates state via browser context
        4. Auto-login if state is invalid
        5. Returns path to valid storage state file

        Args:
            browser: Playwright Browser instance

        Returns:
            Path to valid storage state file

        Raises:
            Exception: If login fails
        """
        # Check validation cache
        if self.email in _validation_cache:
            cache_entry = _validation_cache[self.email]
            age = time.time() - cache_entry['timestamp']
            if age < 300 and cache_entry['valid']:  # 5 minutes
                if self.storage_state_path.exists():
                    return str(self.storage_state_path)

        # Check if storage state file exists
        if self.storage_state_path.exists():
            # Validate state
            if self._validate_storage_state(browser):
                # Update cache
                _validation_cache[self.email] = {
                    'valid': True,
                    'timestamp': time.time()
                }
                return str(self.storage_state_path)

        # State invalid or missing - login
        return self._login_and_save_state(browser)

    def _validate_storage_state(self, browser: Browser) -> bool:
        """Validate storage state by navigating to protected page.

        Args:
            browser: Playwright Browser instance

        Returns:
            True if state is valid, False otherwise
        """
        try:
            # Create context with storage state
            context = browser.new_context(storage_state=str(self.storage_state_path))
            page = context.new_page()

            # Navigate to protected page (items page requires auth)
            page.goto(f"{Config.FRONTEND_BASE_URL}/items", wait_until="networkidle")
            
            # Check if we're redirected to login (state invalid)
            current_url = page.url
            is_valid = "/login" not in current_url

            # Cleanup
            page.close()
            context.close()

            return is_valid
        except Exception:
            return False

    def _login_and_save_state(self, browser: Browser) -> str:
        """Login via browser and save storage state.

        Args:
            browser: Playwright Browser instance

        Returns:
            Path to saved storage state file

        Raises:
            Exception: If login fails
        """
        # Create new context
        context = browser.new_context()
        page = context.new_page()

        try:
            # Navigate to login page
            page.goto(f"{Config.FRONTEND_BASE_URL}/login", wait_until="networkidle")
            
            # Wait for login form to be visible
            page.wait_for_selector('[data-testid="login-email"]', timeout=10000)

            # Fill login form using data-testid selectors
            page.get_by_test_id("login-email").fill(self.email)
            page.get_by_test_id("login-password").fill(self.password)

            # Submit form
            page.get_by_test_id("login-submit").click()

            # Wait for navigation (should go to items page or dashboard)
            page.wait_for_url(
                lambda url: "/login" not in url,
                timeout=15000
            )

            # Verify we're logged in (not on login page)
            current_url = page.url
            if "/login" in current_url:
                raise Exception("Login failed - still on login page")

            # Save storage state
            context.storage_state(path=str(self.storage_state_path))

            # Update cache
            _validation_cache[self.email] = {
                'valid': True,
                'timestamp': time.time()
            }

            return str(self.storage_state_path)

        finally:
            # Cleanup
            page.close()
            context.close()
