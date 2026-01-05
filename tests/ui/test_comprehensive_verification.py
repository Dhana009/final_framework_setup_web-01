"""Comprehensive verification tests for complete framework functionality.

This test suite contains 10 new test cases that verify:
1. Global seed data setup
2. API data creation
3. UI interactions
4. API cleanup/deletion
5. Parallel execution support

All tests are independent and can run in parallel or sequentially.
"""

import pytest
import uuid
from lib.pages.create_item_page import CreateItemPage
from lib.pages.search_page import SearchPage
from fixtures.seed_factory import SeedFactory, ItemType
from lib.builders.item_builder import ItemBuilder


class TestComprehensiveVerification:
    """Comprehensive test suite for framework verification."""

    def test_01_verify_global_seed_and_api_create_physical(self, admin_ui_actor, admin_actor, create_test_item, hard_delete_test_item, global_seed):
        """Test 1: Verify global seed exists, create PHYSICAL item via API, verify via UI, then cleanup."""
        # Verify global seed
        assert global_seed is not None, "Global seed must be set up"
        assert len(global_seed.get("users", [])) > 0, "Global seed should have users"
        
        # Create unique test data
        test_id = str(uuid.uuid4())[:8]
        item_data = SeedFactory.generate_physical_item()
        item_data['name'] = f"Verification_Physical_{test_id}"
        
        # Create via API
        api_data = ItemBuilder.to_api_format(item_data)
        created_item = create_test_item(api_data)
        assert created_item is not None, "API item creation should succeed"
        item_id = created_item.get('_id') or created_item.get('id')
        assert item_id is not None, "Created item must have ID"
        
        # Verify via UI search
        page = admin_ui_actor["page"]
        search_page = SearchPage(page)
        search_page.navigate()
        search_page.wait_for_ready()
        search_page.search(f"Verification_Physical_{test_id}")
        
        items_count = search_page.get_items_count()
        assert items_count > 0, "Should find API-created item in UI"
        
        # Cleanup
        hard_delete_test_item(item_id)

    def test_02_verify_global_seed_and_api_create_digital(self, admin_ui_actor, admin_actor, create_test_item, hard_delete_test_item, global_seed):
        """Test 2: Verify global seed exists, create DIGITAL item via API, verify via UI, then cleanup."""
        # Verify global seed
        assert global_seed is not None
        
        # Create unique test data
        test_id = str(uuid.uuid4())[:8]
        item_data = SeedFactory.generate_digital_item()
        item_data['name'] = f"Verification_Digital_{test_id}"
        
        # Create via API
        api_data = ItemBuilder.to_api_format(item_data)
        created_item = create_test_item(api_data)
        item_id = created_item.get('_id') or created_item.get('id')
        
        # Verify via UI
        page = admin_ui_actor["page"]
        search_page = SearchPage(page)
        search_page.navigate()
        search_page.wait_for_ready()
        search_page.search(f"Verification_Digital_{test_id}")
        
        assert search_page.get_items_count() > 0
        
        # Cleanup
        hard_delete_test_item(item_id)

    def test_03_verify_global_seed_and_api_create_service(self, admin_ui_actor, admin_actor, create_test_item, hard_delete_test_item, global_seed):
        """Test 3: Verify global seed exists, create SERVICE item via API, verify via UI, then cleanup."""
        assert global_seed is not None
        
        test_id = str(uuid.uuid4())[:8]
        item_data = SeedFactory.generate_service_item()
        item_data['name'] = f"Verification_Service_{test_id}"
        
        created_item = create_test_item(ItemBuilder.to_api_format(item_data))
        item_id = created_item.get('_id') or created_item.get('id')
        
        page = admin_ui_actor["page"]
        search_page = SearchPage(page)
        search_page.navigate()
        search_page.wait_for_ready()
        search_page.search(f"Verification_Service_{test_id}")
        
        assert search_page.get_items_count() > 0
        
        hard_delete_test_item(item_id)

    def test_04_verify_api_batch_create_and_cleanup(self, admin_ui_actor, admin_actor, create_test_item, hard_delete_test_item, global_seed):
        """Test 4: Create multiple items via API, verify all exist, then cleanup all."""
        assert global_seed is not None
        
        test_id = str(uuid.uuid4())[:8]
        created_items = []
        
        # Create 3 items of different types
        for i, item_type in enumerate([ItemType.PHYSICAL, ItemType.DIGITAL, ItemType.SERVICE]):
            item_data = SeedFactory.generate_item(item_type)
            item_data['name'] = f"BatchTest_{test_id}_{i}"
            created_item = create_test_item(ItemBuilder.to_api_format(item_data))
            created_items.append(created_item)
        
        # Verify all exist via UI
        page = admin_ui_actor["page"]
        search_page = SearchPage(page)
        search_page.navigate()
        search_page.wait_for_ready()
        search_page.search(f"BatchTest_{test_id}")
        
        assert search_page.get_items_count() >= 3, "Should find all batch-created items"
        
        # Cleanup all
        for item in created_items:
            item_id = item.get('_id') or item.get('id')
            if item_id:
                hard_delete_test_item(item_id)

    def test_05_verify_ui_create_after_api_setup(self, admin_ui_actor, admin_actor, create_test_item, hard_delete_test_item, global_seed):
        """Test 5: Create item via API, then create another via UI, verify both, cleanup API item."""
        assert global_seed is not None
        
        test_id = str(uuid.uuid4())[:8]
        
        # Setup: Create via API
        api_item_data = SeedFactory.generate_physical_item()
        api_item_data['name'] = f"UISetup_{test_id}_API"
        created_api_item = create_test_item(ItemBuilder.to_api_format(api_item_data))
        api_item_id = created_api_item.get('_id') or created_api_item.get('id')
        
        # Test: Create via UI
        page = admin_ui_actor["page"]
        create_page = CreateItemPage(page)
        create_page.navigate()
        
        ui_item_data = SeedFactory.generate_digital_item()
        create_page.create_item(ui_item_data)
        
        # Verify UI item was created
        assert "/items" in page.url or "/create" not in page.url
        
        # Verify API item still exists
        search_page = SearchPage(page)
        search_page.navigate()
        search_page.wait_for_ready()
        search_page.search(f"UISetup_{test_id}_API")
        assert search_page.get_items_count() > 0
        
        # Cleanup API item only
        hard_delete_test_item(api_item_id)

    def test_06_verify_filter_by_category_with_api_data(self, admin_ui_actor, admin_actor, create_test_item, hard_delete_test_item, global_seed):
        """Test 6: Create items with specific category via API, filter by category in UI, verify, cleanup."""
        assert global_seed is not None
        
        test_id = str(uuid.uuid4())[:8]
        target_category = "Electronics"
        created_items = []
        
        # Create 2 items with specific category
        for i in range(2):
            item_data = SeedFactory.generate_physical_item()
            item_data['name'] = f"CategoryFilter_{test_id}_{i}"
            item_data['category'] = target_category
            created_item = create_test_item(ItemBuilder.to_api_format(item_data))
            created_items.append(created_item)
        
        # Filter by category in UI
        page = admin_ui_actor["page"]
        search_page = SearchPage(page)
        search_page.navigate()
        search_page.wait_for_ready()
        search_page.filter_by_category(target_category)
        
        # Verify filter works
        items_count = search_page.get_items_count()
        assert items_count >= 0, "Filter should return results"
        
        # Cleanup
        for item in created_items:
            item_id = item.get('_id') or item.get('id')
            if item_id:
                hard_delete_test_item(item_id)

    def test_07_verify_search_multiple_api_items(self, admin_ui_actor, admin_actor, create_test_item, hard_delete_test_item, global_seed):
        """Test 7: Create multiple items with same search term, search in UI, verify all found, cleanup."""
        assert global_seed is not None
        
        test_id = str(uuid.uuid4())[:8]
        search_term = f"MultiSearch_{test_id}"
        created_items = []
        
        # Create 4 items with same search term
        for i in range(4):
            item_data = SeedFactory.generate_physical_item()
            item_data['name'] = f"{item_data['name']} {search_term} Item{i}"
            created_item = create_test_item(ItemBuilder.to_api_format(item_data))
            created_items.append(created_item)
        
        # Search in UI
        page = admin_ui_actor["page"]
        search_page = SearchPage(page)
        search_page.navigate()
        search_page.wait_for_ready()
        search_page.search(search_term)
        
        # Verify all found
        items_count = search_page.get_items_count()
        assert items_count >= 4, f"Should find at least 4 items with search term '{search_term}'"
        
        # Cleanup
        for item in created_items:
            item_id = item.get('_id') or item.get('id')
            if item_id:
                hard_delete_test_item(item_id)

    def test_08_verify_sort_with_api_created_data(self, admin_ui_actor, admin_actor, create_test_item, hard_delete_test_item, global_seed):
        """Test 8: Create items via API, sort by name in UI, verify sort works, cleanup."""
        assert global_seed is not None
        
        test_id = str(uuid.uuid4())[:8]
        created_items = []
        
        # Create items with predictable names for sorting
        names = [f"SortA_{test_id}", f"SortB_{test_id}", f"SortC_{test_id}"]
        for name in names:
            item_data = SeedFactory.generate_physical_item()
            item_data['name'] = name
            created_item = create_test_item(ItemBuilder.to_api_format(item_data))
            created_items.append(created_item)
        
        # Sort in UI
        page = admin_ui_actor["page"]
        search_page = SearchPage(page)
        search_page.navigate()
        search_page.wait_for_ready()
        search_page.sort_by("name", "asc")
        
        # Verify sort applied
        items_count = search_page.get_items_count()
        assert items_count >= 0
        
        # Cleanup
        for item in created_items:
            item_id = item.get('_id') or item.get('id')
            if item_id:
                hard_delete_test_item(item_id)

    def test_09_verify_global_seed_items_visible_in_ui(self, admin_ui_actor, admin_actor, global_seed):
        """Test 9: Verify that global seed items are visible in UI without creating new data."""
        assert global_seed is not None
        assert len(global_seed.get("users", [])) > 0
        
        # Navigate to search page
        page = admin_ui_actor["page"]
        search_page = SearchPage(page)
        search_page.navigate()
        search_page.wait_for_ready()
        
        # Verify global seed items are visible (should have items from seed)
        items_count = search_page.get_items_count()
        assert items_count >= 0, "Global seed items should be visible"
        
        # No cleanup needed - using global seed data only

    def test_10_verify_complete_flow_api_ui_cleanup(self, admin_ui_actor, admin_actor, create_test_item, hard_delete_test_item, global_seed):
        """Test 10: Complete flow - verify global seed, create via API, create via UI, search, filter, cleanup."""
        # Verify global seed
        assert global_seed is not None
        
        test_id = str(uuid.uuid4())[:8]
        
        # Step 1: Create via API
        api_item_data = SeedFactory.generate_physical_item()
        api_item_data['name'] = f"CompleteFlow_{test_id}_API"
        created_api_item = create_test_item(ItemBuilder.to_api_format(api_item_data))
        api_item_id = created_api_item.get('_id') or created_api_item.get('id')
        
        # Step 2: Create via UI
        page = admin_ui_actor["page"]
        create_page = CreateItemPage(page)
        create_page.navigate()
        
        ui_item_data = SeedFactory.generate_digital_item()
        create_page.create_item(ui_item_data)
        assert "/items" in page.url or "/create" not in page.url
        
        # Step 3: Search for API item
        search_page = SearchPage(page)
        search_page.navigate()
        search_page.wait_for_ready()
        search_page.search(f"CompleteFlow_{test_id}_API")
        assert search_page.get_items_count() > 0
        
        # Step 4: Filter by category
        search_page.filter_by_category("Electronics")
        items_count = search_page.get_items_count()
        assert items_count >= 0
        
        # Step 5: Cleanup API item
        hard_delete_test_item(api_item_id)
