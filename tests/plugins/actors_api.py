"""API actor fixtures for different user roles."""

import pytest
from lib.users import UserLease
from lib.auth import SmartAuth
from utils.api_client import APIClient
from utils.config import Config


def _create_actor(role: str):
    """Create an API actor for a given role.

    Args:
        role: User role (ADMIN, EDITOR, VIEWER)

    Returns:
        Dictionary with user, token, and api client
    """
    # Acquire user
    lease = UserLease(role=role)
    user = lease.acquire()

    # Authenticate
    api = APIClient(base_url=Config.API_BASE_URL)
    auth = SmartAuth(user, api)
    token = auth.get_token()

    # Update API client with token
    api.token = token

    return {
        "user": user,
        "token": token,
        "api": api,
        "_lease": lease  # Keep reference for cleanup
    }


@pytest.fixture(scope="function")
def admin_actor():
    """Fixture providing an authenticated ADMIN user for API tests.

    Yields:
        Dictionary with:
        - user: User credentials (email, password)
        - token: Authentication token
        - api: APIClient instance with token set
    """
    actor = _create_actor("ADMIN")
    yield {
        "user": actor["user"],
        "token": actor["token"],
        "api": actor["api"]
    }
    # Cleanup: release user
    actor["_lease"].release()


@pytest.fixture(scope="function")
def editor_actor():
    """Fixture providing an authenticated EDITOR user for API tests.

    Yields:
        Dictionary with:
        - user: User credentials (email, password)
        - token: Authentication token
        - api: APIClient instance with token set
    """
    actor = _create_actor("EDITOR")
    yield {
        "user": actor["user"],
        "token": actor["token"],
        "api": actor["api"]
    }
    # Cleanup: release user
    actor["_lease"].release()


@pytest.fixture(scope="function")
def viewer_actor():
    """Fixture providing an authenticated VIEWER user for API tests.

    Yields:
        Dictionary with:
        - user: User credentials (email, password)
        - token: Authentication token
        - api: APIClient instance with token set
    """
    actor = _create_actor("VIEWER")
    yield {
        "user": actor["user"],
        "token": actor["token"],
        "api": actor["api"]
    }
    # Cleanup: release user
    actor["_lease"].release()
