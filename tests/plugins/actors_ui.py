"""UI actor fixtures for browser-based testing."""

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright
from lib.users import UserLease
from lib.ui_auth import SmartUIAuth
from lib.auth import SmartAuth
from utils.api_client import APIClient
from utils.config import Config


def _create_ui_actor(role: str, browser: Browser):
    """Create a UI actor for a given role.

    Args:
        role: User role (ADMIN, EDITOR, VIEWER)
        browser: Playwright Browser instance

    Returns:
        Dictionary with user, token, api, page, and context
    """
    # Acquire user
    lease = UserLease(role=role)
    user = lease.acquire()

    # Set up API authentication
    api = APIClient(base_url=Config.API_BASE_URL)
    auth = SmartAuth(user, api)
    token = auth.get_token()
    api.token = token

    # Set up UI authentication
    ui_auth = SmartUIAuth(user)
    storage_state_path = ui_auth.get_storage_state(browser)
    
    # Ensure path is string (Playwright expects string)
    storage_state_str = str(storage_state_path) if storage_state_path else None

    # Create browser context with storage state
    context = browser.new_context(storage_state=storage_state_str) if storage_state_str else browser.new_context()
    page = context.new_page()

    return {
        "user": user,
        "token": token,
        "api": api,
        "page": page,
        "context": context,
        "_lease": lease  # Keep reference for cleanup
    }


@pytest.fixture(scope="function")
def browser():
    """Function-scoped Playwright browser fixture.

    Launches browser in headed mode so tests are visible.

    Yields:
        Browser: Playwright Browser instance
    """
    with sync_playwright() as p:
        # Launch in headed mode (visible browser) for debugging
        browser = p.chromium.launch(headless=False)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def admin_ui_actor(browser):
    """Fixture providing an authenticated ADMIN user for UI tests.

    This fixture:
    1. Acquires an ADMIN user from the pool
    2. Authenticates via API (gets token)
    3. Authenticates via browser (gets storage state)
    4. Creates browser context with storage state
    5. Returns page and context for UI testing

    Yields:
        Dictionary with:
        - user: User credentials (email, password)
        - token: Authentication token
        - api: APIClient instance with token set
        - page: Playwright Page instance (authenticated)
        - context: Playwright BrowserContext instance

    Cleanup:
        Automatically releases user and closes browser context
    """
    actor = _create_ui_actor("ADMIN", browser)
    yield {
        "user": actor["user"],
        "token": actor["token"],
        "api": actor["api"],
        "page": actor["page"],
        "context": actor["context"]
    }
    # Cleanup
    actor["page"].close()
    actor["context"].close()
    actor["_lease"].release()


@pytest.fixture(scope="function")
def editor_ui_actor(browser):
    """Fixture providing an authenticated EDITOR user for UI tests.

    Yields:
        Dictionary with user, token, api, page, and context
    """
    actor = _create_ui_actor("EDITOR", browser)
    yield {
        "user": actor["user"],
        "token": actor["token"],
        "api": actor["api"],
        "page": actor["page"],
        "context": actor["context"]
    }
    # Cleanup
    actor["page"].close()
    actor["context"].close()
    actor["_lease"].release()


@pytest.fixture(scope="function")
def viewer_ui_actor(browser):
    """Fixture providing an authenticated VIEWER user for UI tests.

    Yields:
        Dictionary with user, token, api, page, and context
    """
    actor = _create_ui_actor("VIEWER", browser)
    yield {
        "user": actor["user"],
        "token": actor["token"],
        "api": actor["api"],
        "page": actor["page"],
        "context": actor["context"]
    }
    # Cleanup
    actor["page"].close()
    actor["context"].close()
    actor["_lease"].release()
