"""Tests for API client wrapper."""

import pytest
from unittest.mock import Mock, patch


class TestAPIClient:
    """Test APIClient class for HTTP requests."""

    def test_get_request(self):
        """Test that GET request works."""
        from utils.api_client import APIClient

        with patch('requests.request') as mock_request:
            # Mock response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": "test"}
            mock_response.raise_for_status = Mock()  # Don't raise on success
            mock_request.return_value = mock_response

            # Create client and make GET request
            client = APIClient(base_url="http://test.com/api")
            response = client.get("/endpoint")

            # Verify request was made correctly
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1]['method'] == 'GET'
            assert response.status_code == 200
            assert response.json() == {"data": "test"}

    def test_post_request(self):
        """Test that POST request works."""
        from utils.api_client import APIClient

        with patch('requests.request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 201
            mock_response.json.return_value = {"id": 1, "name": "test"}
            mock_response.raise_for_status = Mock()
            mock_request.return_value = mock_response

            client = APIClient(base_url="http://test.com/api")
            response = client.post("/items", json={"name": "test"})

            mock_request.assert_called_once()
            call_kwargs = mock_request.call_args[1]
            assert call_kwargs['method'] == 'POST'
            assert call_kwargs['json'] == {"name": "test"}
            assert response.status_code == 201

    def test_put_request(self):
        """Test that PUT request works."""
        from utils.api_client import APIClient

        with patch('requests.request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": 1, "name": "updated"}
            mock_response.raise_for_status = Mock()
            mock_request.return_value = mock_response

            client = APIClient(base_url="http://test.com/api")
            response = client.put("/items/1", json={"name": "updated"})

            mock_request.assert_called_once()
            call_kwargs = mock_request.call_args[1]
            assert call_kwargs['method'] == 'PUT'
            assert call_kwargs['json'] == {"name": "updated"}

    def test_delete_request(self):
        """Test that DELETE request works."""
        from utils.api_client import APIClient

        with patch('requests.request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 204
            mock_response.raise_for_status = Mock()
            mock_request.return_value = mock_response

            client = APIClient(base_url="http://test.com/api")
            response = client.delete("/items/1")

            mock_request.assert_called_once()
            call_kwargs = mock_request.call_args[1]
            assert call_kwargs['method'] == 'DELETE'
            assert response.status_code == 204

    def test_authentication_header(self):
        """Test that Authorization header is added when token is provided."""
        from utils.api_client import APIClient

        with patch('requests.request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status = Mock()
            mock_request.return_value = mock_response

            client = APIClient(base_url="http://test.com/api", token="test-token")
            client.get("/endpoint")

            call_kwargs = mock_request.call_args[1]
            assert 'headers' in call_kwargs
            assert call_kwargs['headers']['Authorization'] == 'Bearer test-token'

    def test_url_normalization(self):
        """Test that URLs are normalized correctly."""
        from utils.api_client import APIClient

        with patch('requests.request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status = Mock()
            mock_request.return_value = mock_response

            client = APIClient(base_url="http://test.com/api/v1")
            
            # Test with leading slash
            client.get("/items")
            call_args = mock_request.call_args
            assert call_args[1]['url'] == "http://test.com/api/v1/items"

            # Test without leading slash
            client.get("items")
            call_args = mock_request.call_args
            assert call_args[1]['url'] == "http://test.com/api/v1/items"

    def test_error_handling(self):
        """Test that API errors are handled correctly."""
        from utils.api_client import APIClient
        import requests

        with patch('requests.request') as mock_request:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = requests.HTTPError("Not Found")
            mock_request.return_value = mock_response

            client = APIClient(base_url="http://test.com/api")
            
            with pytest.raises(requests.HTTPError):
                client.get("/nonexistent")
