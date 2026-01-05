"""Flow 2: Create Item - Real-world test scenarios with API setup and cleanup."""

import pytest
from lib.pages.create_item_page import CreateItemPage
from fixtures.seed_factory import SeedFactory
from lib.builders.item_builder import ItemBuilder


class TestFlow2WithSetupCleanup:
    """Flow 2 tests with API-based data setup and cleanup."""

    def test_create_physical_item_with_setup_cleanup(self, admin_ui_actor, create_test_item, hard_delete_test_item):
        """Test creating PHYSICAL item with API setup and cleanup.
        
        Scenario:
        1. Setup: Create test data via API
        2. Execute: Create item via UI
        3. Cleanup: Delete test data via API
        """
        page = admin_ui_actor["page"]
        api = admin_ui_actor["api"]
        create_page = CreateItemPage(page)

        # Setup: Create test data via API
        setup_item_data = SeedFactory.generate_physical_item()
        setup_item = create_test_item(setup_item_data)
        setup_item_id = setup_item.get("_id") or setup_item.get("id")
        
        assert setup_item_id is not None, "Setup item should be created"

        try:
            # Navigate to create page
            create_page.navigate()

            # Generate new item data for UI test
            item_data = SeedFactory.generate_physical_item()

            # Create item via UI
            create_page.create_item(item_data)

            # Verify success (redirected to items page)
            assert "/items" in page.url or "/create" not in page.url

        finally:
            # Cleanup: Delete setup data via API
            if setup_item_id:
                hard_delete_test_item(setup_item_id)

    def test_create_digital_item_with_setup_cleanup(self, admin_ui_actor, create_test_item, hard_delete_test_item):
        """Test creating DIGITAL item with API setup and cleanup."""
        page = admin_ui_actor["page"]
        create_page = CreateItemPage(page)

        # Setup: Create test data via API
        setup_item_data = SeedFactory.generate_digital_item()
        setup_item = create_test_item(setup_item_data)
        setup_item_id = setup_item.get("_id") or setup_item.get("id")

        try:
            create_page.navigate()
            item_data = SeedFactory.generate_digital_item()
            create_page.create_item(item_data)
            assert "/items" in page.url or "/create" not in page.url

        finally:
            # Cleanup
            if setup_item_id:
                hard_delete_test_item(setup_item_id)

    def test_create_service_item_with_setup_cleanup(self, admin_ui_actor, create_test_item, hard_delete_test_item):
        """Test creating SERVICE item with API setup and cleanup."""
        page = admin_ui_actor["page"]
        create_page = CreateItemPage(page)

        # Setup: Create test data via API
        setup_item_data = SeedFactory.generate_service_item()
        setup_item = create_test_item(setup_item_data)
        setup_item_id = setup_item.get("_id") or setup_item.get("id")

        try:
            create_page.navigate()
            item_data = SeedFactory.generate_service_item()
            create_page.create_item(item_data)
            assert "/items" in page.url or "/create" not in page.url

        finally:
            # Cleanup
            if setup_item_id:
                hard_delete_test_item(setup_item_id)
