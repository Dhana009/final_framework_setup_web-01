"""File-based locking utility for thread-safe operations.

This module provides a simple wrapper around the filelock library to enable
cross-process and cross-thread synchronization. It's used for coordinating
access to shared resources like user pool state files.
"""

from filelock import FileLock, Timeout


class AtomicLock:
    """Thread-safe file-based lock wrapper.

    This class provides a simple interface for file-based locking using
    the filelock library. It ensures atomic operations across processes
    and threads, which is essential for parallel test execution with pytest-xdist.

    The lock uses a file-based mechanism that works across:
    - Multiple threads in the same process
    - Multiple processes (e.g., pytest-xdist workers)
    - Multiple machines (if using shared filesystem)

    Attributes:
        lock_path: Path to the lock file
        timeout: Maximum time to wait for lock acquisition (default: 10 seconds)
        _lock: Internal FileLock instance
        _acquired: Boolean flag indicating if lock is currently acquired

    Example:
        >>> lock = AtomicLock("/path/to/lock.file")
        >>> with lock:
        ...     # Critical section
        ...     pass
    """

    def __init__(self, lock_path: str, timeout: float = 10.0):
        """Initialize AtomicLock.

        Args:
            lock_path: Path to the lock file. The file will be created
                automatically if it doesn't exist.
            timeout: Maximum time to wait for lock acquisition in seconds.
                Default is 10 seconds. If lock cannot be acquired within
                this time, a Timeout exception is raised.

        Raises:
            ValueError: If lock_path is empty or invalid
        """
        if not lock_path:
            raise ValueError("lock_path cannot be empty")

        self.lock_path = lock_path
        self.timeout = timeout
        self._lock = FileLock(lock_path, timeout=timeout)
        self._acquired = False

    def acquire(self):
        """Acquire the lock.

        This method blocks until the lock is acquired or the timeout period
        expires. If the lock is already acquired by this instance, calling
        acquire() again will raise an error.

        Raises:
            Timeout: If lock cannot be acquired within timeout period.
                This typically happens when another process/thread is holding
                the lock.
        """
        if self._acquired:
            raise RuntimeError("Lock already acquired by this instance")

        self._lock.acquire()
        self._acquired = True

    def release(self):
        """Release the lock.

        This method releases the lock, allowing other processes/threads to
        acquire it. It's safe to call release() even if the lock wasn't
        acquired (it will be a no-op).

        Note:
            The lock must be released by the same instance that acquired it.
        """
        if self._acquired:
            self._lock.release()
            self._acquired = False

    def __enter__(self):
        """Context manager entry.

        Allows using AtomicLock as a context manager:
        >>> with AtomicLock("/path/to/lock") as lock:
        ...     # Critical section
        ...     pass

        Returns:
            self: The lock instance
        """
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit.

        Automatically releases the lock when exiting the context, even if
        an exception occurred.

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)

        Returns:
            False: Always returns False to allow exceptions to propagate
        """
        self.release()
        return False
