"""Base Page Object Model class for all page objects."""

from typing import Optional
from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
from utils.config import Config


class BasePage:
    """Base class for all page objects.

    Provides common functionality for all pages:
    - Navigation
    - Element waiting strategies
    - Common interactions
    - Error handling

    Attributes:
        page: Playwright Page instance
        base_url: Base URL for the application
    """

    def __init__(self, page: Page, base_url: Optional[str] = None):
        """Initialize BasePage.

        Args:
            page: Playwright Page instance
            base_url: Base URL (defaults to Config.FRONTEND_BASE_URL)
        """
        self.page = page
        self.base_url = base_url or Config.FRONTEND_BASE_URL

    def navigate(self, path: str = ""):
        """Navigate to a page.

        Args:
            path: Path to navigate to (relative to base_url)
        """
        url = f"{self.base_url}/{path.lstrip('/')}" if path else self.base_url
        self.page.goto(url, wait_until="networkidle")

    def wait_for_element(
        self,
        selector: str,
        timeout: int = 30000,
        state: str = "visible"
    ) -> Locator:
        """Wait for an element to be in a specific state.

        Args:
            selector: CSS selector or data-testid
            timeout: Maximum time to wait in milliseconds
            state: Element state (visible, hidden, attached, detached)

        Returns:
            Locator for the element

        Raises:
            TimeoutError: If element doesn't reach state within timeout
        """
        locator = self.page.locator(selector)
        locator.wait_for(state=state, timeout=timeout)
        return locator

    def wait_for_url(
        self,
        url_pattern: str,
        timeout: int = 30000
    ):
        """Wait for URL to match pattern.

        Args:
            url_pattern: URL pattern to wait for
            timeout: Maximum time to wait in milliseconds
        """
        self.page.wait_for_url(url_pattern, timeout=timeout)

    def click(self, selector: str, timeout: int = 30000):
        """Click an element.

        Args:
            selector: CSS selector or data-testid
            timeout: Maximum time to wait in milliseconds
        """
        self.page.click(selector, timeout=timeout)

    def fill(self, selector: str, value: str, timeout: int = 30000):
        """Fill an input field.

        Args:
            selector: CSS selector or data-testid
            value: Value to fill
            timeout: Maximum time to wait in milliseconds
        """
        self.page.fill(selector, value, timeout=timeout)

    def select_option(self, selector: str, value: str, timeout: int = 30000):
        """Select an option from a dropdown.

        Args:
            selector: CSS selector or data-testid
            value: Option value to select
            timeout: Maximum time to wait in milliseconds
        """
        self.page.select_option(selector, value, timeout=timeout)

    def get_text(self, selector: str, timeout: int = 30000) -> str:
        """Get text content of an element.

        Args:
            selector: CSS selector or data-testid
            timeout: Maximum time to wait in milliseconds

        Returns:
            Text content of the element
        """
        return self.page.locator(selector).text_content(timeout=timeout) or ""

    def is_visible(self, selector: str, timeout: int = 5000) -> bool:
        """Check if an element is visible.

        Args:
            selector: CSS selector or data-testid
            timeout: Maximum time to wait in milliseconds

        Returns:
            True if element is visible, False otherwise
        """
        try:
            self.page.locator(selector).wait_for(state="visible", timeout=timeout)
            return True
        except PlaywrightTimeoutError:
            return False
