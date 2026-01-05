"""API fixtures for CRUD operations."""

import pytest
from typing import Dict, Any, Optional


@pytest.fixture
def create_test_item(admin_actor):
    """Fixture to create a test item via API.

    Args:
        admin_actor: Admin actor fixture

    Returns:
        Function that creates an item and returns created item data
    """
    def _create_item(item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an item via API.

        Args:
            item_data: Item data dictionary

        Returns:
            Created item data from API response
        """
        api = admin_actor["api"]
        response = api.post("/items", json=item_data)
        
        # Handle response (could be dict or Response object)
        if hasattr(response, 'json'):
            result = response.json()
        else:
            result = response
            
        return result.get("data", result)

    return _create_item


@pytest.fixture
def update_test_item(admin_actor):
    """Fixture to update a test item via API.

    Args:
        admin_actor: Admin actor fixture

    Returns:
        Function that updates an item
    """
    def _update_item(item_id: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an item via API.

        Args:
            item_id: Item ID
            item_data: Updated item data (must include 'version' field)

        Returns:
            Updated item data from API response
        """
        api = admin_actor["api"]
        response = api.put(f"/items/{item_id}", json=item_data)
        
        # Handle response
        if hasattr(response, 'json'):
            result = response.json()
        else:
            result = response
            
        return result.get("data", result)

    return _update_item


@pytest.fixture
def delete_test_item(admin_actor):
    """Fixture to delete (soft delete) a test item via API.

    Args:
        admin_actor: Admin actor fixture

    Returns:
        Function that deletes an item
    """
    def _delete_item(item_id: str):
        """Delete an item via API (soft delete).

        Args:
            item_id: Item ID to delete
        """
        api = admin_actor["api"]
        api.delete(f"/items/{item_id}")

    return _delete_item


@pytest.fixture
def hard_delete_test_item(admin_actor):
    """Fixture to hard delete a test item via internal API.

    Args:
        admin_actor: Admin actor fixture

    Returns:
        Function that hard deletes an item
    """
    from utils.config import Config

    def _hard_delete_item(item_id: str):
        """Hard delete an item via internal API.

        Args:
            item_id: Item ID to hard delete
        """
        api = admin_actor["api"]
        headers = {
            "x-internal-key": Config.INTERNAL_AUTOMATION_KEY
        }
        api.delete(f"/internal/items/{item_id}/permanent", headers=headers)

    return _hard_delete_item


@pytest.fixture
def hard_delete_user_items(admin_actor):
    """Fixture to hard delete all items for a user via internal API.

    Args:
        admin_actor: Admin actor fixture

    Returns:
        Function that hard deletes all user items
    """
    from utils.config import Config

    def _hard_delete_user_items(user_id: str):
        """Hard delete all items for a user via internal API.

        Args:
            user_id: User ID whose items should be deleted
        """
        api = admin_actor["api"]
        headers = {
            "x-internal-key": Config.INTERNAL_AUTOMATION_KEY
        }
        api.delete(f"/internal/users/{user_id}/items", headers=headers)

    return _hard_delete_user_items


@pytest.fixture
def hard_delete_user_data(admin_actor):
    """Fixture to hard delete all data for a user via internal API.

    Args:
        admin_actor: Admin actor fixture

    Returns:
        Function that hard deletes all user data
    """
    from utils.config import Config

    def _hard_delete_user_data(user_id: str):
        """Hard delete all data for a user via internal API.

        This deletes items, files, bulk jobs, activity logs, OTPs.
        The user record itself is preserved.

        Args:
            user_id: User ID whose data should be deleted
        """
        api = admin_actor["api"]
        headers = {
            "x-internal-key": Config.INTERNAL_AUTOMATION_KEY
        }
        api.delete(f"/internal/users/{user_id}/data", headers=headers)

    return _hard_delete_user_data
