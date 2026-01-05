"""Tests for API actor fixtures."""

import pytest


class TestAPIActors:
    """Test API actor fixtures."""

    def test_admin_actor_structure(self, admin_actor):
        """Test that admin_actor has correct structure."""
        assert "user" in admin_actor
        assert "token" in admin_actor
        assert "api" in admin_actor
        
        assert "email" in admin_actor["user"]
        assert admin_actor["token"] is not None
        assert admin_actor["api"] is not None

    def test_editor_actor_structure(self, editor_actor):
        """Test that editor_actor has correct structure."""
        assert "user" in editor_actor
        assert "token" in editor_actor
        assert "api" in editor_actor

    def test_viewer_actor_structure(self, viewer_actor):
        """Test that viewer_actor has correct structure."""
        assert "user" in viewer_actor
        assert "token" in viewer_actor
        assert "api" in viewer_actor

    def test_automatic_authentication(self, admin_actor):
        """Test that actors authenticate automatically."""
        # Actor should have token
        assert admin_actor["token"] is not None
        assert len(admin_actor["token"]) > 0
        
        # API client should have token set
        assert admin_actor["api"].token == admin_actor["token"]
