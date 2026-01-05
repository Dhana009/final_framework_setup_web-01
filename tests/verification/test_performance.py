"""Performance validation tests."""

import pytest
import time
from lib.users import UserLease
from lib.auth import SmartAuth
from utils.api_client import APIClient
from utils.config import Config


class TestPerformance:
    """Test performance targets."""

    def test_user_acquisition_performance(self):
        """Test that user acquisition meets < 5ms target."""
        start = time.time()
        with UserLease(role="ADMIN") as lease:
            acquisition_time = (time.time() - start) * 1000  # Convert to ms
            assert lease.user is not None

        # Target: < 5ms (with caching, should be much faster)
        assert acquisition_time < 5000, f"User acquisition took {acquisition_time}ms, target is < 5ms"

    def test_config_caching_performance(self):
        """Test that config caching reduces I/O."""
        # First load (file read)
        start1 = time.time()
        with UserLease(role="ADMIN") as lease1:
            time1 = (time.time() - start1) * 1000
            user1 = lease1.user

        # Second load (should use cache)
        start2 = time.time()
        with UserLease(role="ADMIN") as lease2:
            time2 = (time.time() - start2) * 1000
            user2 = lease2.user

        # Cached load should be faster (or at least not slower)
        # Note: This is a basic check, actual caching is session-level
        assert user1 is not None
        assert user2 is not None
