# Parallel Execution Guide

## Running Tests in Parallel

The framework supports parallel test execution using `pytest-xdist`.

### Basic Parallel Execution

```bash
# Auto-detect number of CPUs
pytest -n auto

# Use specific number of workers
pytest -n 4

# Run specific test directory
pytest tests/ui/ -n auto
```

### UI Tests in Headed Mode

UI tests are configured to run in **headed mode** (visible browser) by default.

**Browser Configuration:**
- Headless: `False` (browser visible)
- Browser: Chromium
- Scope: Function-level (each test gets fresh browser)

### Parallel Execution Benefits

1. **Faster Execution:** Tests run concurrently
2. **User Pool Management:** Thread-safe user acquisition
3. **No Conflicts:** UUID namespacing prevents data conflicts
4. **Resource Efficiency:** Better CPU utilization

### Example Commands

```bash
# Run all tests in parallel (auto workers)
pytest -n auto

# Run UI tests in parallel (4 workers)
pytest tests/ui/ -n 4

# Run verification tests in parallel
pytest tests/verification/ -n auto

# Run with verbose output
pytest -n auto -v

# Run specific test file in parallel
pytest tests/ui/test_create_item.py -n 2
```

### Performance

- **Sequential:** ~5-10 minutes for full suite
- **Parallel (4 workers):** ~2-3 minutes for full suite
- **Speedup:** 2-3x faster with parallel execution

### Notes

- User pool automatically manages parallel user acquisition
- Each worker gets unique users (no conflicts)
- Browser contexts are isolated per test
- Storage state files are per-user (no conflicts)
