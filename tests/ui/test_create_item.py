"""UI tests for Flow 2: Create Item.

These tests verify the complete Flow 2 scenario:
1. Global seed data is set up before test session (via global_seed fixture)
2. API creates test data before UI test
3. UI creates additional item
4. API cleans up test data after test

Requires ENABLE_SEED_SETUP=true in .env for global seed to run.
"""

import pytest
import uuid
from lib.pages.create_item_page import CreateItemPage
from fixtures.seed_factory import SeedFactory
from lib.builders.item_builder import ItemBuilder


class TestCreateItem:
    """Test creating items via UI with API setup/teardown."""

    def test_create_physical_item(self, admin_ui_actor, admin_actor, create_test_item, hard_delete_test_item, global_seed):
        """Test creating a PHYSICAL item via UI with API setup/teardown.
        
        Flow:
        1. Verify global seed is set up
        2. Create test data via API
        3. Create item via UI
        4. Clean up API-created data
        """
        # Verify global seed is set up
        assert global_seed is not None, "Global seed should be set up before tests"
        
        # Setup: Create test data via API
        api_items = []
        test_suffix = str(uuid.uuid4())[:8]
        
        for i in range(2):
            item_data = SeedFactory.generate_physical_item()
            # Add unique suffix to avoid conflicts
            item_data['name'] = f"{item_data['name']} API_{test_suffix}_{i}"
            # Convert to API format
            api_data = ItemBuilder.to_api_format(item_data)
            created_item = create_test_item(api_data)
            api_items.append(created_item)
        
        # Test: Create item via UI
        page = admin_ui_actor["page"]
        create_page = CreateItemPage(page)
        create_page.navigate()
        
        item_data = SeedFactory.generate_physical_item()
        create_page.create_item(item_data)
        
        # Verify success (redirected to items page)
        assert "/items" in page.url or "/create" not in page.url
        
        # Cleanup: Delete API-created items
        for item in api_items:
            item_id = item.get('_id') or item.get('id')
            if item_id:
                hard_delete_test_item(item_id)

    def test_create_digital_item(self, admin_ui_actor, admin_actor, create_test_item, hard_delete_test_item, global_seed):
        """Test creating a DIGITAL item via UI with API setup/teardown."""
        # Verify global seed is set up
        assert global_seed is not None
        
        # Setup: Create test data via API
        api_items = []
        test_suffix = str(uuid.uuid4())[:8]
        
        for i in range(2):
            item_data = SeedFactory.generate_digital_item()
            item_data['name'] = f"{item_data['name']} API_{test_suffix}_{i}"
            api_data = ItemBuilder.to_api_format(item_data)
            created_item = create_test_item(api_data)
            api_items.append(created_item)
        
        # Test: Create item via UI
        page = admin_ui_actor["page"]
        create_page = CreateItemPage(page)
        create_page.navigate()
        
        item_data = SeedFactory.generate_digital_item()
        create_page.create_item(item_data)
        
        assert "/items" in page.url or "/create" not in page.url
        
        # Cleanup: Delete API-created items
        for item in api_items:
            item_id = item.get('_id') or item.get('id')
            if item_id:
                hard_delete_test_item(item_id)

    def test_create_service_item(self, admin_ui_actor, admin_actor, create_test_item, hard_delete_test_item, global_seed):
        """Test creating a SERVICE item via UI with API setup/teardown."""
        # Verify global seed is set up
        assert global_seed is not None
        
        # Setup: Create test data via API
        api_items = []
        test_suffix = str(uuid.uuid4())[:8]
        
        for i in range(2):
            item_data = SeedFactory.generate_service_item()
            item_data['name'] = f"{item_data['name']} API_{test_suffix}_{i}"
            api_data = ItemBuilder.to_api_format(item_data)
            created_item = create_test_item(api_data)
            api_items.append(created_item)
        
        # Test: Create item via UI
        page = admin_ui_actor["page"]
        create_page = CreateItemPage(page)
        create_page.navigate()
        
        item_data = SeedFactory.generate_service_item()
        create_page.create_item(item_data)
        
        assert "/items" in page.url or "/create" not in page.url
        
        # Cleanup: Delete API-created items
        for item in api_items:
            item_id = item.get('_id') or item.get('id')
            if item_id:
                hard_delete_test_item(item_id)