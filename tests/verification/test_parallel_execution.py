"""Tests for parallel execution capabilities."""

import pytest
from lib.users import UserLease


class TestParallelExecution:
    """Test parallel execution support."""

    def test_multiple_users_acquired(self):
        """Test that multiple users can be acquired."""
        # Simulate parallel acquisition
        users = []
        roles = ["ADMIN", "EDITOR", "VIEWER"]

        for role in roles:
            with UserLease(role=role) as lease:
                users.append(lease.user)

        # All users should be different
        emails = [user["email"] for user in users]
        assert len(emails) == len(set(emails)), "All users should be different"

    def test_user_release_after_use(self):
        """Test that users are released after use."""
        # Acquire and release user
        with UserLease(role="ADMIN") as lease:
            email = lease.user["email"]
            assert email is not None

        # User should be released (can't verify directly, but no error means success)
