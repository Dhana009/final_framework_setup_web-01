"""Search & Discovery page object model."""

from typing import List, Optional, Dict
from playwright.sync_api import Page, Locator
from lib.pages.base_page import BasePage
from utils.config import Config


class SearchPage(BasePage):
    """Page object for the search & discovery page.

    Provides methods for:
    - Navigating to items page
    - Waiting for page ready state
    - Searching items
    - Filtering by status and category
    - Sorting items
    - Pagination
    - Getting item data
    """

    def __init__(self, page: Page):
        """Initialize SearchPage.

        Args:
            page: Playwright Page instance
        """
        super().__init__(page)
        self.items_url = f"{self.base_url}/items"

    def navigate(self):
        """Navigate to items/search page."""
        self.page.goto(self.items_url, wait_until="networkidle")

    def wait_for_ready(self, timeout: int = 30000):
        """Wait for page to be ready (data loaded).

        Waits for data-test-ready="true" attribute.

        Args:
            timeout: Maximum time to wait in milliseconds
        """
        self.wait_for_element('[data-test-ready="true"]', timeout=timeout)

    def search(self, search_term: str):
        """Search for items by name or description.

        Handles debounce automatically by waiting for search state to become 'ready'.

        Args:
            search_term: Search term
        """
        search_input = self.page.get_by_test_id("item-search")
        search_input.fill(search_term)

        # Wait for debounce and search to complete
        # Search state should become 'ready' after debounce + API call
        self.page.wait_for_selector(
            '[data-testid="item-search"][data-test-search-state="ready"]',
            timeout=10000
        )

    def clear_search(self):
        """Clear search input."""
        self.page.get_by_test_id("search-clear").click()
        # Wait for search to reset
        self.page.wait_for_selector(
            '[data-testid="item-search"][data-test-search-state="ready"]',
            timeout=5000
        )

    def filter_by_status(self, status: str):
        """Filter items by status.

        Args:
            status: Status filter (active, inactive, all)
        """
        self.page.get_by_test_id("filter-status").select_option(status)
        # Wait for filter to apply
        self.wait_for_ready()

    def filter_by_category(self, category: str):
        """Filter items by category.

        Args:
            category: Category filter
        """
        self.page.get_by_test_id("filter-category").select_option(category)
        # Wait for filter to apply
        self.wait_for_ready()

    def sort_by(self, column: str, order: str = "asc"):
        """Sort items by column.

        Args:
            column: Column to sort by (name, category, price, created)
            order: Sort order (asc, desc)
        """
        # Click sort button for column
        sort_button = self.page.get_by_test_id(f"sort-{column}")
        sort_button.click()

        # If order is desc, click again to toggle (no data-sort-order attribute exists)
        if order == "desc":
            # Check aria-sort attribute to determine current order
            aria_sort = sort_button.get_attribute("aria-sort")
            if aria_sort != "descending":
                sort_button.click()  # Toggle to descending

        # Wait for sort to apply
        self.wait_for_ready()

    def get_items_count(self) -> int:
        """Get number of items currently displayed.

        Returns:
            Number of items
        """
        count_attr = self.page.get_attribute('[data-test-items-count]', 'data-test-items-count')
        return int(count_attr) if count_attr else 0

    def get_item_rows(self) -> List[Locator]:
        """Get all item row locators.

        Returns:
            List of item row locators (using pattern item-row-{itemId})
        """
        return self.page.locator('[data-testid^="item-row-"]').all()

    def get_item_data(self, row_index: int = 0) -> Optional[Dict[str, str]]:
        """Get data from a specific item row.

        Args:
            row_index: Index of the item row (0-based)

        Returns:
            Dictionary with item data (name, category, price, etc.) or None
        """
        rows = self.get_item_rows()
        if row_index >= len(rows):
            return None

        row = rows[row_index]
        
        # Extract item ID from row's data-testid (item-row-{itemId})
        row_testid = row.get_attribute("data-testid") or ""
        item_id = row_testid.replace("item-row-", "") if row_testid.startswith("item-row-") else ""
        
        if not item_id:
            return None
        
        # Use dynamic locators with item ID
        return {
            "item_id": item_id,
            "name": row.locator(f'[data-testid="item-name-{item_id}"]').text_content() or "",
            "category": row.locator(f'[data-testid="item-category-{item_id}"]').text_content() or "",
            "price": row.locator(f'[data-testid="item-price-{item_id}"]').text_content() or "",
            "status": row.locator(f'[data-testid="item-status-{item_id}"]').text_content() or "",
        }

    def click_next_page(self):
        """Click next page button."""
        self.page.get_by_test_id("pagination-next").click()
        self.wait_for_ready()

    def click_previous_page(self):
        """Click previous page button."""
        self.page.get_by_test_id("pagination-prev").click()
        self.wait_for_ready()

    def go_to_page(self, page_number: int):
        """Navigate to specific page.

        Args:
            page_number: Page number (1-based)
        """
        page_button = self.page.get_by_test_id(f"pagination-page-{page_number}")
        if page_button.is_visible():
            page_button.click()
            self.wait_for_ready()
