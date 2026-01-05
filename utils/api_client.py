"""API client wrapper for HTTP requests.

This module provides a convenient HTTP client wrapper that handles:
- URL normalization (base URL + endpoint)
- Automatic authentication header injection
- Consistent error handling
- Support for all HTTP methods (GET, POST, PUT, DELETE)
"""

import requests
from typing import Optional, Dict, Any
from urllib.parse import urljoin
from utils.config import Config


class APIClient:
    """HTTP client wrapper for API requests.

    This class provides a convenient interface for making HTTP requests
    to the backend API with automatic URL normalization, authentication
    header injection, and error handling.

    The client automatically:
    - Combines base URL with endpoint paths
    - Adds Authorization header when token is provided
    - Raises exceptions for HTTP error status codes
    - Supports JSON payloads for POST/PUT requests

    Attributes:
        base_url: Base URL for the API (e.g., "http://localhost:8000/api/v1")
        token: Authentication token (optional, added as Bearer token)
        headers: Default headers for all requests

    Example:
        >>> client = APIClient(base_url="http://api.example.com", token="abc123")
        >>> response = client.get("/items")
        >>> data = response.json()
    """

    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        """Initialize APIClient.

        Args:
            base_url: Base URL for the API (defaults to Config.API_BASE_URL from .env)
            token: Optional authentication token
        """
        self.base_url = (base_url or Config.API_BASE_URL).rstrip('/')
        self.headers = {}
        # Use property setter to ensure headers are updated
        self.token = token

    @property
    def token(self) -> Optional[str]:
        """Get the current authentication token.

        Returns:
            Current authentication token or None
        """
        return getattr(self, '_token', None)

    @token.setter
    def token(self, value: Optional[str]):
        """Set the authentication token and update Authorization header.

        Args:
            value: Authentication token (or None to remove)
        """
        self._token = value
        if value:
            self.headers['Authorization'] = f'Bearer {value}'
        elif 'Authorization' in self.headers:
            # Remove Authorization header if token is None
            del self.headers['Authorization']

    def _normalize_url(self, endpoint: str) -> str:
        """Normalize URL by combining base URL with endpoint.

        Args:
            endpoint: API endpoint (e.g., "/items" or "items")

        Returns:
            Full URL combining base URL and endpoint
        """
        # Remove leading slash from endpoint if present
        endpoint = endpoint.lstrip('/')
        return urljoin(f"{self.base_url}/", endpoint)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> requests.Response:
        """Make HTTP request with common logic.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            **kwargs: Additional arguments to pass to requests method

        Returns:
            Response object

        Raises:
            requests.RequestException: If request fails
        """
        url = self._normalize_url(endpoint)

        # Merge headers
        headers = {**self.headers, **kwargs.pop('headers', {})}

        # Make request
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            **kwargs
        )

        # Raise exception for bad status codes
        response.raise_for_status()

        return response

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """Make GET request.

        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments to pass to requests.get

        Returns:
            Response object
        """
        return self._make_request('GET', endpoint, **kwargs)

    def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """Make POST request.

        Args:
            endpoint: API endpoint
            json: JSON payload (optional)
            **kwargs: Additional arguments to pass to requests.post

        Returns:
            Response object
        """
        return self._make_request('POST', endpoint, json=json, **kwargs)

    def put(self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """Make PUT request.

        Args:
            endpoint: API endpoint
            json: JSON payload (optional)
            **kwargs: Additional arguments to pass to requests.put

        Returns:
            Response object
        """
        return self._make_request('PUT', endpoint, json=json, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """Make DELETE request.

        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments to pass to requests.delete

        Returns:
            Response object
        """
        return self._make_request('DELETE', endpoint, **kwargs)
