"""Test parallel UI execution capabilities."""

import pytest
from lib.users import UserLease


class TestParallelUI:
    """Test that UI tests can run in parallel."""

    def test_multiple_ui_actors_parallel(self, admin_ui_actor, editor_ui_actor):
        """Test that multiple UI actors can be used in parallel."""
        # Both actors should have their own browser contexts
        assert admin_ui_actor["page"] is not None
        assert editor_ui_actor["page"] is not None
        assert admin_ui_actor["user"]["email"] != editor_ui_actor["user"]["email"]

    def test_ui_actor_has_page(self, admin_ui_actor):
        """Test that UI actor provides page object."""
        assert "page" in admin_ui_actor
        assert "context" in admin_ui_actor
        assert "user" in admin_ui_actor
        assert "token" in admin_ui_actor
        assert "api" in admin_ui_actor
