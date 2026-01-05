"""On-demand seed data insertion fixtures."""

import pytest
from typing import List, Dict, Any, Set
from fixtures.seed_factory import SeedFactory
from utils.api_client import APIClient
from utils.config import Config


def _collect_unique_names(items: List[Dict[str, Any]]) -> Set[str]:
    """Collect unique item names from list.

    Args:
        items: List of item dictionaries

    Returns:
        Set of unique item names
    """
    return {item["name"] for item in items}


def _check_duplicates_via_api(api: APIClient, names: Set[str]) -> Set[str]:
    """Check which items already exist via API.

    Uses indexed search queries to efficiently check for duplicates.

    Args:
        api: APIClient instance
        names: Set of item names to check

    Returns:
        Set of names that already exist
    """
    existing_names = set()

    for name in names:
        try:
            # Use indexed search query with limit=1 for efficiency
            response = api.get("/items", params={
                "search": name,
                "limit": 1
            })

            data = response.json() if hasattr(response, 'json') else response
            
            # Check if item with this name exists
            items = data.get("items", [])
            if items and any(item.get("name") == name for item in items):
                existing_names.add(name)
        except Exception:
            # If API call fails, assume item doesn't exist (safer for tests)
            pass

    return existing_names


def _filter_existing_items(
    items: List[Dict[str, Any]],
    existing_names: Set[str]
) -> List[Dict[str, Any]]:
    """Filter out items that already exist.

    Args:
        items: List of item dictionaries
        existing_names: Set of names that already exist

    Returns:
        List of items that don't exist yet
    """
    return [item for item in items if item["name"] not in existing_names]


@pytest.fixture
def insert_data_if_not_exists(admin_actor):
    """Fixture for inserting test data if it doesn't already exist.

    This fixture provides a function that:
    1. Collects unique item names
    2. Checks for duplicates via API
    3. Filters out existing items
    4. Inserts only new items
    5. Returns all created items

    Args:
        admin_actor: Admin actor fixture with authenticated API client

    Returns:
        Function that inserts items and returns created items
    """
    def _insert_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Insert items if they don't already exist.

        Args:
            items: List of item data dictionaries

        Returns:
            List of created items (from API responses)
        """
        if not items:
            return []

        api = admin_actor["api"]

        # Step 1: Collect unique names - O(n) where n = items
        unique_names = _collect_unique_names(items)

        # Step 2: Check for duplicates via API - O(k) where k = unique names
        existing_names = _check_duplicates_via_api(api, unique_names)

        # Step 3: Filter out existing items - O(n)
        items_to_insert = _filter_existing_items(items, existing_names)

        if not items_to_insert:
            # All items already exist, return empty list
            return []

        # Step 4: Insert new items - O(m) where m = new items
        created_items = []
        for item in items_to_insert:
            try:
                response = api.post("/items", json=item)
                data = response.json() if hasattr(response, 'json') else response
                created_item = data.get("data", data)
                created_items.append(created_item)
            except Exception as e:
                # Log error but continue with other items
                print(f"Failed to insert item {item.get('name', 'unknown')}: {e}")

        return created_items

    return _insert_items
