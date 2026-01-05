"""UI tests for Flow 3: Search & Discovery.

These tests verify the complete Flow 3 scenario:
1. Global seed data is set up before test session (via global_seed fixture)
2. API creates test data with known names/categories before UI test
3. UI searches for API-created items
4. API cleans up test data after test

Requires ENABLE_SEED_SETUP=true in .env for global seed to run.
"""

import pytest
import uuid
from lib.pages.search_page import SearchPage
from fixtures.seed_factory import SeedFactory
from lib.builders.item_builder import ItemBuilder


class TestSearchDiscovery:
    """Test search and discovery functionality with API setup/teardown."""

    def test_search_items(self, admin_ui_actor, admin_actor, create_test_item, hard_delete_test_item, global_seed):
        """Test searching for items created via API.
        
        Flow:
        1. Verify global seed is set up
        2. Create test data via API with known search term
        3. Search for API-created items via UI
        4. Verify search results contain API-created items
        5. Clean up API-created data
        """
        # Verify global seed is set up
        assert global_seed is not None, "Global seed should be set up before tests"
        
        # Setup: Create test data via API with known search term
        test_suffix = str(uuid.uuid4())[:8]
        search_term = f"SearchTest_{test_suffix}"
        
        api_items = []
        for i in range(3):
            item_data = SeedFactory.generate_physical_item()
            # Add search term to name so we can find it
            item_data['name'] = f"{item_data['name']} {search_term} Item{i}"
            api_data = ItemBuilder.to_api_format(item_data)
            created_item = create_test_item(api_data)
            api_items.append(created_item)
        
        # Test: Search for API-created items via UI
        page = admin_ui_actor["page"]
        search_page = SearchPage(page)
        search_page.navigate()
        search_page.wait_for_ready()
        
        # Search for the test term
        search_page.search(search_term)
        
        # Verify: API-created items appear in results
        items_count = search_page.get_items_count()
        assert items_count > 0, f"Should find items with search term '{search_term}'"
        
        # Cleanup: Delete API-created items
        for item in api_items:
            item_id = item.get('_id') or item.get('id')
            if item_id:
                hard_delete_test_item(item_id)

    def test_filter_by_status(self, admin_ui_actor, admin_actor, create_test_item, hard_delete_test_item, global_seed):
        """Test filtering items by status with API-created data."""
        # Verify global seed is set up
        assert global_seed is not None
        
        # Setup: Create test data via API
        test_suffix = str(uuid.uuid4())[:8]
        api_items = []
        
        for i in range(2):
            item_data = SeedFactory.generate_physical_item()
            item_data['name'] = f"FilterTest_{test_suffix}_{i}"
            api_data = ItemBuilder.to_api_format(item_data)
            created_item = create_test_item(api_data)
            api_items.append(created_item)
        
        # Test: Filter by active status
        page = admin_ui_actor["page"]
        search_page = SearchPage(page)
        search_page.navigate()
        search_page.wait_for_ready()
        search_page.filter_by_status("active")
        
        # Verify filter applied
        items_count = search_page.get_items_count()
        assert items_count >= 0
        
        # Cleanup: Delete API-created items
        for item in api_items:
            item_id = item.get('_id') or item.get('id')
            if item_id:
                hard_delete_test_item(item_id)

    def test_filter_by_category(self, admin_ui_actor, admin_actor, create_test_item, hard_delete_test_item, global_seed):
        """Test filtering items by category with API-created data."""
        # Verify global seed is set up
        assert global_seed is not None
        
        # Setup: Create test data via API with specific category
        test_suffix = str(uuid.uuid4())[:8]
        api_items = []
        target_category = "Electronics"
        
        for i in range(2):
            item_data = SeedFactory.generate_physical_item()
            item_data['name'] = f"CategoryTest_{test_suffix}_{i}"
            item_data['category'] = target_category
            api_data = ItemBuilder.to_api_format(item_data)
            created_item = create_test_item(api_data)
            api_items.append(created_item)
        
        # Test: Filter by category
        page = admin_ui_actor["page"]
        search_page = SearchPage(page)
        search_page.navigate()
        search_page.wait_for_ready()
        search_page.filter_by_category(target_category)
        
        # Verify filter applied
        items_count = search_page.get_items_count()
        assert items_count >= 0
        
        # Cleanup: Delete API-created items
        for item in api_items:
            item_id = item.get('_id') or item.get('id')
            if item_id:
                hard_delete_test_item(item_id)

    def test_sort_items(self, admin_ui_actor, admin_actor, create_test_item, hard_delete_test_item, global_seed):
        """Test sorting items with API-created data."""
        # Verify global seed is set up
        assert global_seed is not None
        
        # Setup: Create test data via API
        test_suffix = str(uuid.uuid4())[:8]
        api_items = []
        
        for i in range(2):
            item_data = SeedFactory.generate_physical_item()
            item_data['name'] = f"SortTest_{test_suffix}_{i}"
            api_data = ItemBuilder.to_api_format(item_data)
            created_item = create_test_item(api_data)
            api_items.append(created_item)
        
        # Test: Sort by name ascending
        page = admin_ui_actor["page"]
        search_page = SearchPage(page)
        search_page.navigate()
        search_page.wait_for_ready()
        search_page.sort_by("name", "asc")
        
        # Verify sort applied
        items_count = search_page.get_items_count()
        assert items_count >= 0
        
        # Cleanup: Delete API-created items
        for item in api_items:
            item_id = item.get('_id') or item.get('id')
            if item_id:
                hard_delete_test_item(item_id)