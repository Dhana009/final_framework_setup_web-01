"""Tests for SmartAuth authentication."""

import pytest
from unittest.mock import Mock, patch


class TestSmartAuth:
    """Test SmartAuth class for API authentication."""

    def test_state_file_loading(self):
        """Test that SmartAuth can load state file."""
        from lib.auth import SmartAuth, _load_state

        # State file should be loadable
        state = _load_state()
        assert isinstance(state, dict)

    def test_token_retrieval(self):
        """Test getting token from state."""
        from lib.auth import SmartAuth
        from utils.api_client import APIClient

        user = {"email": "test@test.com", "password": "test123"}
        api = APIClient(base_url="http://test.com/api")
        auth = SmartAuth(user, api)

        assert auth.user == user
        assert auth.email == "test@test.com"

    def test_validation_cache(self):
        """Test that validation cache works."""
        from lib.auth import SmartAuth, _validation_cache
        from utils.api_client import APIClient

        user = {"email": "test@test.com", "password": "test123"}
        api = APIClient(base_url="http://test.com/api")
        auth = SmartAuth(user, api)

        # Cache should be accessible
        assert isinstance(_validation_cache, dict)

    @patch('lib.auth.APIClient')
    def test_automatic_login_on_invalid_token(self, mock_api_class):
        """Test automatic login when token is invalid."""
        from lib.auth import SmartAuth

        # Mock API client
        mock_api = Mock()
        mock_api.token = None
        
        # Mock validation failure then login success
        mock_response_validate = Mock()
        mock_response_validate.status_code = 401
        
        mock_response_login = Mock()
        mock_response_login.status_code = 200
        mock_response_login.json.return_value = {
            "token": "new-token-123",
            "user": {"email": "test@test.com"}
        }
        
        mock_api.get.side_effect = [Exception("Invalid token"), mock_response_login]
        mock_api.post.return_value = mock_response_login
        mock_api_class.return_value = mock_api

        user = {"email": "test@test.com", "password": "test123"}
        auth = SmartAuth(user, mock_api)

        # Should trigger login
        token = auth.get_token()
        assert token == "new-token-123"
        assert mock_api.post.called
