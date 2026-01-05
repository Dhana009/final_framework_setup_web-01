# Real-World Test Scenarios Guide

**Date:** 2025-01-05  
**Status:** ✅ Complete

---

## Overview

This document describes the real-world test scenarios implemented for Flow 2 (Create Item) and Flow 3 (Search & Discovery) with comprehensive API setup/teardown, global seed verification, and parallel execution support.

---

## Test Flow Architecture

### Complete Test Flow

```
Test Session Start
    ↓
Global Seed Setup (if ENABLE_SEED_SETUP=true)
    ↓
Test Execution
    ├── Flow 2: Create Item
    │   ├── API: Create test data
    │   ├── UI: Create item
    │   └── API: Cleanup test data
    │
    ├── Flow 3: Search & Discovery
    │   ├── API: Create test data with known names
    │   ├── UI: Search for API-created items
    │   └── API: Cleanup test data
    │
    └── No Cleanup Test
        ├── API: Create test data
        ├── UI: Verify data exists
        └── NO CLEANUP (data persists)
```

---

## Test Scenarios

### 1. Flow 2: Create Item Tests

**File:** `tests/ui/test_create_item.py`

**Scenarios:**
- `test_create_physical_item` - Create PHYSICAL item via UI with API setup/teardown
- `test_create_digital_item` - Create DIGITAL item via UI with API setup/teardown
- `test_create_service_item` - Create SERVICE item via UI with API setup/teardown

**Flow:**
1. ✅ Verify global seed is set up
2. ✅ Create 2 test items via API (for setup verification)
3. ✅ Create item via UI (main test)
4. ✅ Clean up API-created items

**Example:**
```python
def test_create_physical_item(self, admin_ui_actor, admin_actor, create_test_item, hard_delete_test_item, global_seed):
    # Setup: Create test data via API
    api_items = []
    for i in range(2):
        item_data = SeedFactory.generate_physical_item()
        item_data['name'] = f"{item_data['name']} API_{test_suffix}_{i}"
        api_data = ItemBuilder.to_api_format(item_data)
        created_item = create_test_item(api_data)
        api_items.append(created_item)
    
    # Test: Create item via UI
    create_page.create_item(item_data)
    
    # Cleanup: Delete API-created items
    for item in api_items:
        hard_delete_test_item(item['_id'])
```

---

### 2. Flow 3: Search & Discovery Tests

**File:** `tests/ui/test_search_discovery.py`

**Scenarios:**
- `test_search_items` - Search for API-created items
- `test_filter_by_status` - Filter items by status with API-created data
- `test_filter_by_category` - Filter items by category with API-created data
- `test_sort_items` - Sort items with API-created data

**Flow:**
1. ✅ Verify global seed is set up
2. ✅ Create test items via API with known names/categories
3. ✅ Search/filter/sort for API-created items via UI
4. ✅ Verify API-created items appear in results
5. ✅ Clean up API-created items

**Example:**
```python
def test_search_items(self, admin_ui_actor, admin_actor, create_test_item, hard_delete_test_item, global_seed):
    # Setup: Create test data with known search term
    search_term = f"SearchTest_{test_suffix}"
    item_data['name'] = f"{item_data['name']} {search_term} Item{i}"
    created_item = create_test_item(api_data)
    
    # Test: Search for API-created items
    search_page.search(search_term)
    
    # Verify: Items appear in results
    assert items_count > 0
    
    # Cleanup: Delete API-created items
    hard_delete_test_item(created_item['_id'])
```

---

### 3. No Cleanup Test

**File:** `tests/ui/test_no_cleanup.py`

**Purpose:** Verify that data persists when cleanup is not performed.

**Scenario:**
- `test_data_persists_without_cleanup` - Create data via API, verify via UI, but don't cleanup

**Flow:**
1. ✅ Verify global seed is set up
2. ✅ Create data via API with unique identifier
3. ✅ Verify data exists via UI
4. ✅ **NO CLEANUP** - Data persists for verification

**Use Cases:**
- Debugging test data creation
- Verifying data persistence
- Manual inspection of created data

**Note:** This test is marked with `@pytest.mark.no_cleanup` to indicate intentional no cleanup.

---

### 4. Parallel Execution Verification

**File:** `tests/ui/test_parallel_real_world.py`

**Purpose:** Verify all scenarios work correctly in parallel execution.

**Scenarios:**
- `test_parallel_flow2_create_item` - Flow 2 in parallel
- `test_parallel_flow3_search_discovery` - Flow 3 in parallel
- `test_parallel_multiple_workers_no_conflicts` - Multiple workers without conflicts

**Key Features:**
- UUID namespacing prevents conflicts
- User pool management ensures proper user allocation
- Each worker gets unique test data

---

## Configuration Requirements

### Environment Variables

**Required:**
- `ENABLE_SEED_SETUP=true` - Enable global seed setup before test session
- `CLEANUP_SEED_ON_START=false` - Don't cleanup seed on start (seed persists)
- `BACKEND_BASE_URL` - Backend API URL
- `FRONTEND_BASE_URL` - Frontend URL
- `MONGODB_URI` - MongoDB connection string

**Example `.env`:**
```env
ENABLE_SEED_SETUP=true
CLEANUP_SEED_ON_START=false
BACKEND_BASE_URL=https://testing-box.onrender.com/api/v1
FRONTEND_BASE_URL=https://testing-box.vercel.app
MONGODB_URI=mongodb+srv://...
```

---

## Running Tests

### Sequential Execution

```bash
# Run Flow 2 tests
pytest tests/ui/test_create_item.py -v

# Run Flow 3 tests
pytest tests/ui/test_search_discovery.py -v

# Run no-cleanup test
pytest tests/ui/test_no_cleanup.py -v

# Run all UI tests
pytest tests/ui/ -v
```

### Parallel Execution (4 workers)

```bash
# Run all UI tests in parallel
pytest tests/ui/ -v -n 4

# Run parallel verification tests
pytest tests/ui/test_parallel_real_world.py -v -n 4

# Run with headed browser (visible)
pytest tests/ui/ -v -n 4 --headed
```

### Verify Global Seed

```bash
# Check if global seed runs (requires ENABLE_SEED_SETUP=true)
pytest tests/ui/ -v --setup-show

# Run with seed verification
pytest tests/ui/test_create_item.py::TestCreateItem::test_create_physical_item -v -s
```

---

## Test Data Management

### UUID Namespacing

All test data uses UUID namespacing to prevent conflicts:
- Each test generates a unique UUID suffix
- Item names include the suffix: `ItemName_API_{uuid}_{index}`
- Prevents conflicts in parallel execution

### Cleanup Strategy

**With Cleanup:**
- API-created items are deleted using `hard_delete_test_item` fixture
- Cleanup happens after test completion
- Ensures clean state for subsequent tests

**Without Cleanup:**
- Data persists for verification
- Useful for debugging and manual inspection
- Marked with `@pytest.mark.no_cleanup`

---

## Success Criteria

✅ **All tests pass sequentially**  
✅ **All tests pass in parallel (4 workers)**  
✅ **Global seed runs before test session**  
✅ **API-created data is used in UI tests**  
✅ **Cleanup works correctly**  
✅ **No race conditions in parallel execution**  
✅ **UUID namespacing prevents conflicts**  

---

## Troubleshooting

### Global Seed Not Running

**Issue:** `global_seed` fixture is None or skipped

**Solution:**
- Ensure `ENABLE_SEED_SETUP=true` in `.env`
- Check MongoDB connection
- Verify user pool config exists

### Cleanup Fails

**Issue:** `hard_delete_test_item` fails to delete items

**Solution:**
- Check item ID format (should be string)
- Verify `INTERNAL_AUTOMATION_KEY` is correct
- Check backend API is accessible

### Parallel Execution Conflicts

**Issue:** Tests conflict when running in parallel

**Solution:**
- Verify UUID namespacing is working
- Check user pool has enough users (8 per role minimum)
- Ensure proper fixture scoping

---

## Best Practices

1. **Always use UUID namespacing** for test data
2. **Verify global seed** before tests
3. **Clean up API-created data** after tests (unless testing no-cleanup)
4. **Use appropriate fixtures** (`admin_actor` for API, `admin_ui_actor` for UI)
5. **Wait for UI elements** before interacting
6. **Verify API responses** before using in UI tests

---

## Related Documentation

- `docs/INFRASTRUCTURE_STATUS_REPORT.md` - Infrastructure status
- `docs/PARALLEL_EXECUTION_GUIDE.md` - Parallel execution guide
- `required_docs/framework/FRAMEWORK_IMPLEMENTATION_BLUEPRINT.md` - Framework architecture

---

## Implementation Status

✅ **All tasks completed:**
- ✅ Global seed verification added to all tests
- ✅ Flow 2 tests updated with API setup/teardown
- ✅ Flow 3 tests updated with API setup/teardown and search verification
- ✅ No-cleanup test created
- ✅ Parallel execution tests created
- ✅ Documentation updated

**Status: ✅ Complete and Ready for Use**
