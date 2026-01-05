"""Core pytest fixtures for the framework."""

import pytest
from lib.users import UserLease
from utils.config import Config


@pytest.fixture(scope="function")
def user_lease(request):
    """Fixture to acquire and release a user for a test.

    This fixture automatically acquires a user from the pool at test start
    and releases it at test end.

    Args:
        request: Pytest request object (used to get role from marker)

    Yields:
        UserLease instance with acquired user
    """
    # Get role from marker or default to ADMIN
    role = "ADMIN"
    if hasattr(request, 'param') and isinstance(request.param, dict):
        role = request.param.get('role', 'ADMIN')
    elif hasattr(request.node, 'get_closest_marker'):
        marker = request.node.get_closest_marker('user_role')
        if marker:
            role = marker.args[0] if marker.args else 'ADMIN'

    # Acquire user
    lease = UserLease(role=role)
    lease.acquire()

    yield lease

    # Release user
    lease.release()


@pytest.fixture(scope="session")
def env_config():
    """Session-scoped fixture providing environment configuration.

    Yields:
        Config object with all environment variables
    """
    yield Config
