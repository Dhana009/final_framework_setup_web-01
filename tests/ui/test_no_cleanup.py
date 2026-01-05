"""UI tests for no-cleanup scenario.

This test verifies that data persists when cleanup is not performed.
This is useful for debugging and verifying data creation without cleanup overhead.

Note: This test intentionally does NOT clean up created data.
"""

import pytest
import uuid
from lib.pages.search_page import SearchPage
from fixtures.seed_factory import SeedFactory
from lib.builders.item_builder import ItemBuilder


@pytest.mark.no_cleanup
class TestNoCleanup:
    """Test scenarios where data is created but not cleaned up."""

    def test_data_persists_without_cleanup(self, admin_ui_actor, admin_actor, create_test_item, global_seed):
        """Test that data persists when cleanup is not performed.
        
        Flow:
        1. Verify global seed is set up
        2. Create data via API
        3. Verify data exists via UI
        4. NO CLEANUP - Data persists for verification
        
        This test is marked with @pytest.mark.no_cleanup to indicate
        that cleanup should not be performed.
        """
        # Verify global seed is set up
        assert global_seed is not None, "Global seed should be set up before tests"
        
        # Create data via API with unique identifier
        test_suffix = str(uuid.uuid4())[:8]
        item_name = f"PersistentTestItem_NoCleanup_{test_suffix}"
        
        item_data = SeedFactory.generate_physical_item()
        item_data['name'] = item_name
        api_data = ItemBuilder.to_api_format(item_data)
        created_item = create_test_item(api_data)
        
        # Verify item was created
        assert created_item is not None, "Item should be created via API"
        item_id = created_item.get('_id') or created_item.get('id')
        assert item_id is not None, "Created item should have an ID"
        
        # Verify via UI
        page = admin_ui_actor["page"]
        search_page = SearchPage(page)
        search_page.navigate()
        search_page.wait_for_ready()
        
        # Search for the created item
        search_page.search(item_name)
        
        # Verify item exists in search results
        items_count = search_page.get_items_count()
        assert items_count > 0, f"Should find item with name '{item_name}'"
        
        # NO CLEANUP - Data persists for verification
        # This allows manual inspection or subsequent tests to verify the data exists
        print(f"\n[NO CLEANUP] Created item '{item_name}' with ID '{item_id}' - data persists for verification")
