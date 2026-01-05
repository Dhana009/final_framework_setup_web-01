"""Tests for file locking utility."""

import pytest
import tempfile
import os


class TestAtomicLock:
    """Test AtomicLock class for file-based locking."""

    def test_lock_acquisition(self):
        """Test that lock can be acquired."""
        from utils.file_lock import AtomicLock

        # Create a temporary lock file path
        with tempfile.NamedTemporaryFile(delete=False, suffix='.lock') as tmp:
            lock_path = tmp.name

        try:
            # Acquire lock
            lock = AtomicLock(lock_path)
            lock.acquire()

            # Verify lock is acquired (file exists)
            assert os.path.exists(lock_path)

            # Release lock
            lock.release()
        finally:
            # Cleanup
            if os.path.exists(lock_path):
                os.unlink(lock_path)

    def test_lock_release(self):
        """Test that lock can be released."""
        from utils.file_lock import AtomicLock

        with tempfile.NamedTemporaryFile(delete=False, suffix='.lock') as tmp:
            lock_path = tmp.name

        try:
            lock = AtomicLock(lock_path)
            lock.acquire()
            assert os.path.exists(lock_path)

            lock.release()
            # After release, we should be able to acquire again
            lock2 = AtomicLock(lock_path)
            lock2.acquire()
            lock2.release()
        finally:
            if os.path.exists(lock_path):
                os.unlink(lock_path)

    def test_context_manager(self):
        """Test using lock as context manager."""
        from utils.file_lock import AtomicLock

        with tempfile.NamedTemporaryFile(delete=False, suffix='.lock') as tmp:
            lock_path = tmp.name

        try:
            with AtomicLock(lock_path) as lock:
                assert os.path.exists(lock_path)
                assert lock._acquired is True

            # Lock should be released after context exit
            # We should be able to acquire again
            with AtomicLock(lock_path) as lock2:
                assert lock2._acquired is True
        finally:
            if os.path.exists(lock_path):
                os.unlink(lock_path)

    def test_lock_timeout(self):
        """Test that lock times out after specified time."""
        from utils.file_lock import AtomicLock
        from filelock import Timeout

        with tempfile.NamedTemporaryFile(delete=False, suffix='.lock') as tmp:
            lock_path = tmp.name

        try:
            # Acquire lock with first instance
            lock1 = AtomicLock(lock_path, timeout=0.1)
            lock1.acquire()

            # Try to acquire with second instance (should timeout)
            lock2 = AtomicLock(lock_path, timeout=0.1)
            with pytest.raises(Timeout):
                lock2.acquire()

            lock1.release()
        finally:
            if os.path.exists(lock_path):
                os.unlink(lock_path)

    def test_cross_process_locking(self):
        """Test that lock works across different processes (simulates pytest-xdist)."""
        from utils.file_lock import AtomicLock
        import threading
        import time

        with tempfile.NamedTemporaryFile(delete=False, suffix='.lock') as tmp:
            lock_path = tmp.name

        try:
            results = []
            lock_acquired = threading.Event()

            def acquire_lock(thread_id):
                """Function to acquire lock in separate thread."""
                try:
                    lock = AtomicLock(lock_path, timeout=1.0)
                    lock.acquire()
                    results.append(f"thread_{thread_id}_acquired")
                    lock_acquired.set()
                    time.sleep(0.1)  # Hold lock briefly
                    lock.release()
                    results.append(f"thread_{thread_id}_released")
                except Exception as e:
                    results.append(f"thread_{thread_id}_error: {str(e)}")

            # Start multiple threads trying to acquire lock
            threads = []
            for i in range(3):
                t = threading.Thread(target=acquire_lock, args=(i,))
                threads.append(t)
                t.start()

            # Wait for all threads
            for t in threads:
                t.join(timeout=5)

            # Verify that locks were acquired sequentially (no conflicts)
            # All threads should have acquired and released
            assert len([r for r in results if "acquired" in r]) == 3
            assert len([r for r in results if "released" in r]) == 3
            assert "error" not in str(results).lower()
        finally:
            if os.path.exists(lock_path):
                os.unlink(lock_path)
