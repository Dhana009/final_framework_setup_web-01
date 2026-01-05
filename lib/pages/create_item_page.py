"""Create Item page object model."""

from typing import Dict, Any, Optional
from playwright.sync_api import Page
from lib.pages.base_page import BasePage
from utils.config import Config


class CreateItemPage(BasePage):
    """Page object for the create item page.

    Provides methods for:
    - Navigating to create item page
    - Filling common fields (name, description, price, category)
    - Selecting item type
    - Filling conditional fields (PHYSICAL, DIGITAL, SERVICE)
    - Submitting form
    - Verifying success
    """

    def __init__(self, page: Page):
        """Initialize CreateItemPage.

        Args:
            page: Playwright Page instance
        """
        super().__init__(page)
        self.create_url = f"{self.base_url}/items/create"

    def navigate(self):
        """Navigate to create item page."""
        self.page.goto(self.create_url, wait_until="networkidle")

    def fill_name(self, name: str):
        """Fill item name field.

        Args:
            name: Item name
        """
        self.page.get_by_test_id("item-name").fill(name)

    def fill_description(self, description: str):
        """Fill item description field.

        Args:
            description: Item description
        """
        self.page.get_by_test_id("item-description").fill(description)

    def fill_price(self, price: float):
        """Fill item price field.

        Args:
            price: Item price
        """
        self.page.get_by_test_id("item-price").fill(str(price))

    def fill_category(self, category: str):
        """Fill item category field.

        Args:
            category: Item category
        """
        self.page.get_by_test_id("item-category").fill(category)

    def select_item_type(self, item_type: str):
        """Select item type.

        Args:
            item_type: Item type (PHYSICAL, DIGITAL, SERVICE)
        """
        self.page.get_by_test_id("item-type").select_option(item_type)

    def fill_common_fields(self, name: str, description: str, price: float, category: str):
        """Fill common fields for all item types.

        Args:
            name: Item name
            description: Item description
            price: Item price
            category: Item category
        """
        self.fill_name(name)
        self.fill_description(description)
        self.fill_price(price)
        self.fill_category(category)

    def fill_physical_fields(self, weight: float, length: float, width: float, height: float):
        """Fill PHYSICAL item specific fields.

        Args:
            weight: Item weight
            length: Item length
            width: Item width
            height: Item height
        """
        self.page.get_by_test_id("item-weight").fill(str(weight))
        self.page.get_by_test_id("item-dimension-length").fill(str(length))
        self.page.get_by_test_id("item-dimension-width").fill(str(width))
        self.page.get_by_test_id("item-dimension-height").fill(str(height))

    def fill_digital_fields(self, download_url: str, file_size: int):
        """Fill DIGITAL item specific fields.

        Args:
            download_url: Download URL
            file_size: File size in bytes
        """
        self.page.get_by_test_id("item-download-url").fill(download_url)
        self.page.get_by_test_id("item-file-size").fill(str(file_size))

    def fill_service_fields(self, duration_hours: float):
        """Fill SERVICE item specific fields.

        Args:
            duration_hours: Duration in hours
        """
        self.page.get_by_test_id("item-duration-hours").fill(str(duration_hours))

    def fill_item_data(self, item_data: Dict[str, Any]):
        """Fill form with complete item data.

        Args:
            item_data: Item data dictionary from SeedFactory
        """
        # Fill common fields
        self.fill_common_fields(
            item_data["name"],
            item_data["description"],
            item_data["price"],
            item_data["category"]
        )

        # Select item type
        self.select_item_type(item_data["item_type"])

        # Wait for conditional fields to appear based on item type
        if item_data["item_type"] == "PHYSICAL":
            # Wait for physical fields container to be visible
            self.page.wait_for_selector('[data-testid="physical-fields"]', state="visible", timeout=5000)
            dimensions = item_data.get("dimensions", {})
            self.fill_physical_fields(
                item_data.get("weight", 1.0),
                dimensions.get("length", 10.0),
                dimensions.get("width", 5.0),
                dimensions.get("height", 3.0)
            )
        elif item_data["item_type"] == "DIGITAL":
            # Wait for digital fields container to be visible
            self.page.wait_for_selector('[data-testid="digital-fields"]', state="visible", timeout=5000)
            self.fill_digital_fields(
                item_data.get("download_url", ""),
                item_data.get("file_size", 0)
            )
        elif item_data["item_type"] == "SERVICE":
            # Wait for service fields container to be visible
            self.page.wait_for_selector('[data-testid="service-fields"]', state="visible", timeout=5000)
            self.fill_service_fields(
                item_data.get("duration_hours", 1.0)
            )

    def submit(self):
        """Submit create item form."""
        self.page.get_by_test_id("create-item-submit").click()

    def wait_for_success(self, timeout: int = 10000):
        """Wait for success message or redirect.

        Args:
            timeout: Maximum time to wait in milliseconds
        """
        # Wait for redirect to items page (success is shown via toast)
        self.page.wait_for_url(
            lambda url: "/items" in url and "/create" not in url,
            timeout=timeout
        )

    def create_item(self, item_data: Dict[str, Any]):
        """Complete item creation flow.

        Args:
            item_data: Item data dictionary from SeedFactory
        """
        self.fill_item_data(item_data)
        self.submit()
        self.wait_for_success()
