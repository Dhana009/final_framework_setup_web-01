"""Login page object model."""

from playwright.sync_api import Page
from lib.pages.base_page import BasePage
from utils.config import Config


class LoginPage(BasePage):
    """Page object for the login page.

    Provides methods for:
    - Navigating to login page
    - Filling login form
    - Submitting login form
    - Verifying login success
    """

    def __init__(self, page: Page):
        """Initialize LoginPage.

        Args:
            page: Playwright Page instance
        """
        super().__init__(page)
        self.login_url = f"{self.base_url}/login"

    def navigate(self):
        """Navigate to login page."""
        self.page.goto(self.login_url, wait_until="networkidle")

    def fill_email(self, email: str):
        """Fill email field.

        Args:
            email: User email
        """
        self.page.get_by_test_id("login-email").fill(email)

    def fill_password(self, password: str):
        """Fill password field.

        Args:
            password: User password
        """
        self.page.get_by_test_id("login-password").fill(password)

    def fill_form(self, email: str, password: str):
        """Fill entire login form.

        Args:
            email: User email
            password: User password
        """
        self.fill_email(email)
        self.fill_password(password)

    def submit(self):
        """Submit login form."""
        self.page.get_by_test_id("login-submit").click()

    def login(self, email: str, password: str):
        """Complete login flow.

        Args:
            email: User email
            password: User password
        """
        self.fill_form(email, password)
        self.submit()
        # Wait for navigation away from login page
        self.page.wait_for_url(
            lambda url: "/login" not in url,
            timeout=10000
        )

    def is_on_login_page(self) -> bool:
        """Check if currently on login page.

        Returns:
            True if on login page, False otherwise
        """
        return "/login" in self.page.url
