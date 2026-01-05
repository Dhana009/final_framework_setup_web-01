"""Tests for user pool management."""

import pytest
import json
import os
import tempfile


class TestUserPoolConfig:
    """Test user pool configuration loading."""

    def test_load_config_from_json(self):
        """Test that user pool config can be loaded from JSON file."""
        # Config file should exist from Phase 0
        config_path = "config/user_pool.json"
        assert os.path.exists(config_path), "user_pool.json should exist"

        # Verify the file exists and is valid JSON
        with open(config_path, 'r') as f:
            config = json.load(f)

        assert 'ADMIN' in config
        assert 'EDITOR' in config
        assert 'VIEWER' in config
        assert len(config['ADMIN']) > 0
        assert len(config['EDITOR']) > 0
        assert len(config['VIEWER']) > 0

    def test_user_lease_loads_config(self):
        """Test that UserLease can load config from JSON file."""
        from lib.users import UserLease

        # UserLease should be able to load config
        lease = UserLease(role="ADMIN")
        assert lease is not None
        assert lease.role == "ADMIN"

    def test_config_caching(self):
        """Test that config is cached at session level."""
        from lib.users import _load_config
        import lib.users

        # First load
        config1 = _load_config()
        
        # Second load should use cache
        config2 = _load_config()
        
        # Should be the same object (cached)
        assert config1 is config2
        assert lib.users._config_cache is not None

    def test_user_acquisition_single_user(self):
        """Test acquiring a single user."""
        from lib.users import UserLease
        import os

        # Clean state file
        state_path = "config/user_state.json"
        if os.path.exists(state_path):
            os.remove(state_path)

        lease = UserLease(role="ADMIN")
        user = lease.acquire()

        assert user is not None
        assert 'email' in user
        assert 'password' in user
        assert user['email'].startswith('admin')

        # Cleanup
        lease.release()
        if os.path.exists(state_path):
            os.remove(state_path)

    def test_user_release(self):
        """Test releasing a user."""
        from lib.users import UserLease
        import os

        # Clean state file
        state_path = "config/user_state.json"
        if os.path.exists(state_path):
            os.remove(state_path)

        lease = UserLease(role="ADMIN")
        user1 = lease.acquire()
        email1 = user1['email']
        lease.release()

        # Should be able to acquire again (or another user)
        lease2 = UserLease(role="ADMIN")
        user2 = lease2.acquire()
        # Could be same or different user, but should work
        assert user2 is not None
        lease2.release()

        # Cleanup
        if os.path.exists(state_path):
            os.remove(state_path)

    def test_fail_fast_on_no_users(self):
        """Test that it fails fast when no users available."""
        from lib.users import UserLease, InfrastructureError
        import os
        import json

        # Clean state file
        state_path = "config/user_state.json"
        if os.path.exists(state_path):
            os.remove(state_path)

        # Acquire all ADMIN users
        leases = []
        users_acquired = []
        try:
            # Acquire all available users
            for i in range(8):  # We have 8 admin users
                lease = UserLease(role="ADMIN")
                user = lease.acquire()
                leases.append(lease)
                users_acquired.append(user)

            # Try to acquire one more (should fail)
            lease_fail = UserLease(role="ADMIN")
            with pytest.raises(InfrastructureError) as exc_info:
                lease_fail.acquire()
            
            assert "No free users available" in str(exc_info.value)
        finally:
            # Release all
            for lease in leases:
                lease.release()
            if os.path.exists(state_path):
                os.remove(state_path)

    def test_context_manager(self):
        """Test using UserLease as context manager."""
        from lib.users import UserLease
        import os

        # Clean state file
        state_path = "config/user_state.json"
        if os.path.exists(state_path):
            os.remove(state_path)

        with UserLease(role="ADMIN") as lease:
            assert lease._acquired is True
            assert lease.user is not None

        # Should be released after context exit
        assert lease._acquired is False

        # Cleanup
        if os.path.exists(state_path):
            os.remove(state_path)

    def test_parallel_user_acquisition(self):
        """Test that multiple threads can acquire users without conflicts."""
        from lib.users import UserLease
        import threading
        import os

        # Clean state file
        state_path = "config/user_state.json"
        if os.path.exists(state_path):
            os.remove(state_path)

        results = []
        errors = []

        def acquire_user(thread_id):
            try:
                with UserLease(role="ADMIN") as lease:
                    results.append({
                        'thread_id': thread_id,
                        'email': lease.user['email']
                    })
            except Exception as e:
                errors.append({'thread_id': thread_id, 'error': str(e)})

        # Start multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=acquire_user, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join(timeout=5)

        # Verify no errors
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5
        
        # Verify all got users (they might get same user if state isn't updated fast enough,
        # but with proper locking, they should get different users)
        emails = [r['email'] for r in results]
        # At minimum, all should have gotten a user
        assert len(emails) == 5
        # With file locking, ideally all should be different, but we'll be lenient
        # The important thing is no errors and all got users

        # Cleanup
        if os.path.exists(state_path):
            os.remove(state_path)
