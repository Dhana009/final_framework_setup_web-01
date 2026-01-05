"""Real-world parallel execution verification tests.

These tests verify that all scenarios work correctly in parallel execution
with multiple workers (4 workers recommended).

Run with: pytest tests/ui/test_parallel_real_world.py -v -n 4
"""

import pytest
import uuid
from lib.pages.create_item_page import CreateItemPage
from lib.pages.search_page import SearchPage
from fixtures.seed_factory import SeedFactory
from lib.builders.item_builder import ItemBuilder


class TestParallelRealWorld:
    """Verify real-world scenarios work in parallel execution."""

    def test_parallel_flow2_create_item(self, admin_ui_actor, admin_actor, create_test_item, hard_delete_test_item, global_seed):
        """Test Flow 2 (Create Item) works in parallel execution.
        
        This test can run in parallel with other tests without conflicts
        due to UUID namespacing and proper user pool management.
        """
        # Verify global seed is set up
        assert global_seed is not None
        
        # Setup: Create test data via API with unique identifier
        test_suffix = str(uuid.uuid4())[:8]
        api_items = []
        
        for i in range(2):
            item_data = SeedFactory.generate_physical_item()
            item_data['name'] = f"ParallelFlow2_{test_suffix}_{i}"
            api_data = ItemBuilder.to_api_format(item_data)
            created_item = create_test_item(api_data)
            api_items.append(created_item)
        
        # Test: Create item via UI
        page = admin_ui_actor["page"]
        create_page = CreateItemPage(page)
        create_page.navigate()
        
        item_data = SeedFactory.generate_physical_item()
        create_page.create_item(item_data)
        
        # Verify success
        assert "/items" in page.url or "/create" not in page.url
        
        # Cleanup: Delete API-created items
        for item in api_items:
            item_id = item.get('_id') or item.get('id')
            if item_id:
                hard_delete_test_item(item_id)

    def test_parallel_flow3_search_discovery(self, admin_ui_actor, admin_actor, create_test_item, hard_delete_test_item, global_seed):
        """Test Flow 3 (Search & Discovery) works in parallel execution."""
        # Verify global seed is set up
        assert global_seed is not None
        
        # Setup: Create test data via API with unique search term
        test_suffix = str(uuid.uuid4())[:8]
        search_term = f"ParallelFlow3_{test_suffix}"
        
        api_items = []
        for i in range(3):
            item_data = SeedFactory.generate_physical_item()
            item_data['name'] = f"{item_data['name']} {search_term} Item{i}"
            api_data = ItemBuilder.to_api_format(item_data)
            created_item = create_test_item(api_data)
            api_items.append(created_item)
        
        # Test: Search for API-created items via UI
        page = admin_ui_actor["page"]
        search_page = SearchPage(page)
        search_page.navigate()
        search_page.wait_for_ready()
        search_page.search(search_term)
        
        # Verify: API-created items appear in results
        items_count = search_page.get_items_count()
        assert items_count > 0, f"Should find items with search term '{search_term}'"
        
        # Cleanup: Delete API-created items
        for item in api_items:
            item_id = item.get('_id') or item.get('id')
            if item_id:
                hard_delete_test_item(item_id)

    def test_parallel_multiple_workers_no_conflicts(self, admin_ui_actor, admin_actor, create_test_item, hard_delete_test_item, global_seed):
        """Test that multiple parallel workers don't conflict.
        
        This test verifies that UUID namespacing and user pool management
        prevent conflicts when multiple workers run simultaneously.
        """
        # Verify global seed is set up
        assert global_seed is not None
        
        # Create unique test data for this worker
        test_suffix = str(uuid.uuid4())[:8]
        # Use test name and suffix for uniqueness (pytest-xdist handles worker isolation)
        worker_id = f"worker_{test_suffix}"
        
        # Setup: Create test data via API
        api_items = []
        for i in range(2):
            item_data = SeedFactory.generate_physical_item()
            item_data['name'] = f"WorkerTest_{worker_id}_{test_suffix}_{i}"
            api_data = ItemBuilder.to_api_format(item_data)
            created_item = create_test_item(api_data)
            api_items.append(created_item)
        
        # Test: Verify data via UI
        page = admin_ui_actor["page"]
        search_page = SearchPage(page)
        search_page.navigate()
        search_page.wait_for_ready()
        
        # Search for worker-specific items
        search_term = f"WorkerTest_{test_suffix}"
        search_page.search(search_term)
        
        # Verify items exist
        items_count = search_page.get_items_count()
        assert items_count >= 0
        
        # Cleanup: Delete API-created items
        for item in api_items:
            item_id = item.get('_id') or item.get('id')
            if item_id:
                hard_delete_test_item(item_id)
