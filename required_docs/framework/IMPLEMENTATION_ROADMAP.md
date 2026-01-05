# Framework Implementation Roadmap

## Overview

This document provides a detailed, step-by-step implementation roadmap for building the web automation testing framework. It is based on the complete system design and acceptance criteria.

**Roadmap Date:** 2025-01-XX  
**Status:** Ready for Implementation  
**Purpose:** Step-by-step implementation guide

---

## Implementation Strategy

### Approach

1. **Foundation First:** Build utilities and core components
2. **Incremental:** Build and test each component
3. **Integration:** Integrate components as they're built
4. **Validation:** Verify against acceptance criteria

### Principles

- ✅ Build one component at a time
- ✅ Test each component before moving to next
- ✅ Verify against acceptance criteria
- ✅ Document as you build

---

## Phase 0: Foundation Setup

### Step 0.1: Project Structure

**Create folder structure:**
```
project/
├── config/
│   ├── user_pool.json          # User credentials (user provides)
│   └── user_state.json         # Runtime state (auto-created)
├── utils/
├── lib/
│   ├── builders/
│   └── pages/
├── fixtures/
├── tests/
│   ├── plugins/
│   ├── ui/
│   └── verification/
├── state/                       # Auto-created
├── requirements.txt
├── pytest.ini
└── .env                         # Already exists
```

**Action Items:**
- [ ] Create all folders
- [ ] Add `__init__.py` files to make packages
- [ ] Create `.gitignore` file

**Acceptance:** Folder structure matches blueprint

---

### Step 0.2: Dependencies

**Create `requirements.txt`:**
```
pytest>=8.0.0
playwright>=1.41.0
requests>=2.31.0
filelock>=3.13.1
pytest-playwright>=0.4.4
pymongo>=4.6.1
pytest-xdist>=3.5.0
python-dotenv>=1.0.0
```

**Create `pytest.ini`:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

**Action Items:**
- [ ] Create `requirements.txt`
- [ ] Create `pytest.ini`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Install Playwright browsers: `playwright install`

**Acceptance:** All dependencies installed, pytest works

---

### Step 0.3: Configuration Management

**Create `utils/config.py`:**
- Read environment variables from `.env`
- Provide Config class with all settings
- Support default values
- Use `python-dotenv` for `.env` loading

**Key Configuration:**
- `API_BASE_URL`
- `FRONTEND_BASE_URL`
- `MONGODB_URI`
- `MONGODB_DB_NAME`
- `ENABLE_SEED_SETUP`
- `INTERNAL_AUTOMATION_KEY`

**Action Items:**
- [ ] Create `utils/config.py`
- [ ] Implement Config class
- [ ] Test configuration loading
- [ ] Verify environment variables read correctly

**Acceptance:** Config loads from `.env`, all variables accessible

---

### Step 0.4: User Pool Configuration

**Create `config/user_pool.json`:**
- Use provided user pool configuration
- Remove `reserved_by` field (runtime only)
- Validate structure

**Action Items:**
- [ ] Create `config/user_pool.json` with provided data
- [ ] Remove `reserved_by` fields
- [ ] Validate JSON structure
- [ ] Verify user count per role

**Acceptance:** User pool config valid, structure correct

---

## Phase 1: Core Utilities

### Step 1.1: File Locking Utility

**Create `utils/file_lock.py`:**
- Wrap `filelock` library
- Implement AtomicLock class
- Context manager pattern
- Fail-fast timeout (10 seconds)

**Key Features:**
- Cross-platform compatibility
- Automatic cleanup
- Clear error messages

**Action Items:**
- [ ] Create `utils/file_lock.py`
- [ ] Implement AtomicLock class
- [ ] Test lock acquisition/release
- [ ] Test timeout handling
- [ ] Test cross-platform compatibility

**Acceptance:** Lock works correctly, timeout handled, cleanup automatic

---

### Step 1.2: API Client Wrapper

**Create `utils/api_client.py`:**
- Wrap `requests` library
- Handle authentication headers
- URL normalization
- Error handling
- Response parsing

**Key Features:**
- Token header management
- Error response parsing
- Clear error messages

**Action Items:**
- [ ] Create `utils/api_client.py`
- [ ] Implement APIClient class
- [ ] Test HTTP methods (GET, POST, PUT, DELETE)
- [ ] Test authentication headers
- [ ] Test error handling

**Acceptance:** API client works, handles errors, manages auth headers

---

### Step 1.3: Config Loader

**Already created in Step 0.3, verify:**
- [ ] Config loading works
- [ ] Default values work
- [ ] Environment variable override works

**Acceptance:** Config loading verified

---

## Phase 2: User Pool Management

### Step 2.1: UserLease Class

**Create `lib/users.py`:**
- Implement UserLease class
- Config caching (session-level)
- User acquisition algorithm
- User release mechanism
- Fail-fast on capacity

**Key Algorithm:**
```
1. Load config from cache (O(1))
2. Check candidates exist (early exit)
3. Acquire lock (O(1))
4. Load state file (O(1) read)
5. Find first free user (O(n))
6. Update state file (O(1) write)
7. Release lock (O(1))
```

**Action Items:**
- [ ] Create `lib/users.py`
- [ ] Implement UserLease class
- [ ] Implement config caching
- [ ] Implement acquisition algorithm
- [ ] Implement release mechanism
- [ ] Test user acquisition
- [ ] Test user release
- [ ] Test fail-fast on capacity

**Acceptance:** 
- AC-2.1: User acquired before test
- AC-2.2: Thread-safe acquisition
- AC-2.3: User released after test
- AC-6.2: Simultaneous acquisition works
- AC-6.3: No race conditions
- AC-8.1: < 5ms acquisition time

---

### Step 2.2: Morning Roll Call

**Create `tests/plugins/hooks.py`:**
- Implement `pytest_sessionstart` hook
- Reset `user_state.json` to `{}`
- Use lock for thread-safety
- Validate reset success

**Action Items:**
- [ ] Create `tests/plugins/hooks.py`
- [ ] Implement `pytest_sessionstart` hook
- [ ] Implement state reset
- [ ] Test reset works
- [ ] Test lock usage

**Acceptance:**
- AC-1.7: Runs once per session
- State reset works correctly

---

## Phase 3: Authentication

### Step 3.1: SmartAuth (API Authentication)

**Create `lib/auth.py`:**
- Implement SmartAuth class
- Token validation caching (5-minute TTL)
- File-based state persistence
- Automatic token refresh
- Self-healing authentication

**Key Algorithm:**
```
1. Load state from file (once per instance)
2. Check validation cache (O(1))
3. If cached and valid: Return token (O(1))
4. If not cached: Validate via API (O(1) API call)
5. Update cache
6. If invalid: Login and save new token
```

**Action Items:**
- [ ] Create `lib/auth.py`
- [ ] Implement SmartAuth class
- [ ] Implement validation caching
- [ ] Implement state persistence
- [ ] Implement automatic refresh
- [ ] Test token validation
- [ ] Test token refresh
- [ ] Test caching

**Acceptance:**
- AC-2.4: Authentication validated before test
- AC-2.5: Automatic token refresh
- AC-2.6: Authenticated API client available
- AC-7.2: Automatic refresh on errors
- AC-8.2: < 10ms token reuse (cached)
- AC-8.5: 99% reduction in API calls

---

### Step 3.2: SmartUIAuth (Browser Authentication)

**Create `lib/ui_auth.py`:**
- Implement SmartUIAuth class
- Browser storage state reuse
- Validation via browser context
- Automatic state refresh
- Self-healing authentication

**Key Algorithm:**
```
1. Check if state file exists (O(1))
2. Check validation cache (O(1))
3. If cached and valid: Return state path (O(1))
4. If not cached: Validate via browser
5. Update cache
6. If invalid: Login and save new state
```

**Action Items:**
- [ ] Create `lib/ui_auth.py`
- [ ] Implement SmartUIAuth class
- [ ] Implement validation caching
- [ ] Implement browser validation
- [ ] Implement state persistence
- [ ] Test storage state reuse
- [ ] Test validation
- [ ] Test automatic refresh

**Acceptance:**
- AC-2.4: Authentication validated before test
- AC-2.5: Automatic state refresh
- AC-2.6: Authenticated browser page available
- AC-8.2: < 10ms state reuse (cached)

---

## Phase 4: Data Management

### Step 4.1: Seed Factory

**Create `fixtures/seed_factory.py`:**
- Implement SeedDataFactory class
- Item generation methods
- Role-based data generation (configurable)
- Category-item type compatibility

**Key Features:**
- Basic item creation
- Type-specific fields (PHYSICAL, DIGITAL, SERVICE)
- Category compatibility rules

**Action Items:**
- [ ] Create `fixtures/seed_factory.py`
- [ ] Implement SeedDataFactory class
- [ ] Implement item generation
- [ ] Implement type-specific fields
- [ ] Test item generation
- [ ] Test category compatibility

**Acceptance:** Factory generates valid items, handles all types

---

### Step 4.2: Item Builder

**Create `lib/builders/item_builder.py`:**
- Transform factory data to MongoDB format
- Handle all item types
- Add required fields
- Validate data

**Action Items:**
- [ ] Create `lib/builders/item_builder.py`
- [ ] Implement ItemBuilder class
- [ ] Implement transformation logic
- [ ] Test transformation
- [ ] Test validation

**Acceptance:** Builder transforms data correctly, validates properly

---

### Step 4.3: MongoDB Fixtures

**Create `tests/plugins/mongodb_fixtures.py`:**
- MongoDB connection fixture (session-scoped)
- Direct database insertion
- Duplicate checking
- Bulk operations

**Key Features:**
- Session-scoped connection
- Efficient duplicate checking
- Bulk insert for performance

**Action Items:**
- [ ] Create `tests/plugins/mongodb_fixtures.py`
- [ ] Implement MongoDB connection fixture
- [ ] Implement direct insertion
- [ ] Implement duplicate checking
- [ ] Test MongoDB connection
- [ ] Test direct insertion
- [ ] Test duplicate checking

**Acceptance:**
- AC-1.5: MongoDB direct insertion works
- AC-1.2: Duplicate checking works
- AC-1.3: Skip creation if exists

---

### Step 4.4: Global Seed Setup

**Create `tests/plugins/data.py`:**
- Global seed setup fixture (session-scoped)
- ENABLE_SEED_SETUP flag check
- Calls MongoDB seeding
- Error handling

**Action Items:**
- [ ] Create `tests/plugins/data.py`
- [ ] Implement global seed setup fixture
- [ ] Implement ENABLE_SEED_SETUP check
- [ ] Integrate with MongoDB fixtures
- [ ] Test global seed setup
- [ ] Test flag handling

**Acceptance:**
- AC-1.1: Global seed setup runs before tests
- AC-1.2: Checks if data exists
- AC-1.3: Skips if exists
- AC-1.4: Creates if missing
- AC-1.5: Uses MongoDB direct
- AC-1.6: Handles failures gracefully
- AC-1.7: Runs once per session
- AC-8.3: < 30s for 5 users

---

### Step 4.5: On-Demand Insertion

**Create `tests/plugins/seed_fixtures.py`:**
- `insert_data_if_not_exists` fixture
- Duplicate checking via API
- Only insert new items
- Return created items

**Key Algorithm:**
```
1. Collect unique names
2. For each unique name: Check via API
3. Filter out existing items
4. Insert only new items
5. Return created items
```

**Action Items:**
- [ ] Create `tests/plugins/seed_fixtures.py`
- [ ] Implement `insert_data_if_not_exists` fixture
- [ ] Implement duplicate checking
- [ ] Test duplicate checking
- [ ] Test insertion
- [ ] Test return value

**Acceptance:**
- AC-3.1: Test can call API for data setup
- AC-3.2: Duplicate checking works
- AC-3.3: Uses indexed queries
- AC-3.4: Only new items inserted
- AC-3.5: Returns created items
- AC-3.6: Handles API errors gracefully

---

### Step 4.6: CRUD Operations

**Create `tests/plugins/api_fixtures.py`:**
- `create_test_item` fixture
- `update_test_item` fixture
- `delete_test_item` fixture
- `hard_delete_test_item` fixture
- `hard_delete_user_items` fixture
- `hard_delete_user_data` fixture

**Action Items:**
- [ ] Create `tests/plugins/api_fixtures.py`
- [ ] Implement all CRUD fixtures
- [ ] Test create operation
- [ ] Test update operation
- [ ] Test delete operation
- [ ] Test hard delete operations

**Acceptance:** All CRUD operations work correctly

---

## Phase 5: Fixtures and Actors

### Step 5.1: Core Fixtures

**Create `tests/plugins/core.py`:**
- `user_lease` fixture (function scope)
- `env_config` fixture (session scope)
- `worker_id` fixture (pytest-xdist)
- `mongodb_connection` fixture (session scope)

**Action Items:**
- [ ] Create `tests/plugins/core.py`
- [ ] Implement all core fixtures
- [ ] Test fixture dependencies
- [ ] Test fixture scoping

**Acceptance:** All core fixtures work, proper scoping

---

### Step 5.2: API Actors

**Create `tests/plugins/actors_api.py`:**
- `admin_actor` fixture
- `editor_actor` fixture
- `viewer_actor` fixture
- Each returns: `{user, token, api}`

**Action Items:**
- [ ] Create `tests/plugins/actors_api.py`
- [ ] Implement admin_actor
- [ ] Implement editor_actor
- [ ] Implement viewer_actor
- [ ] Test actor creation
- [ ] Test authentication
- [ ] Test resource cleanup

**Acceptance:**
- AC-2.6: Authenticated API client available
- AC-9.4: All roles supported

---

### Step 5.3: UI Actors

**Create `tests/plugins/actors_ui.py`:**
- `admin_ui_actor` fixture
- `editor_ui_actor` fixture
- `viewer_ui_actor` fixture
- Each returns: `{user, token, api, page, context}`

**Action Items:**
- [ ] Create `tests/plugins/actors_ui.py`
- [ ] Implement admin_ui_actor
- [ ] Implement editor_ui_actor
- [ ] Implement viewer_ui_actor
- [ ] Test actor creation
- [ ] Test browser authentication
- [ ] Test resource cleanup

**Acceptance:**
- AC-2.6: Authenticated browser page available
- AC-9.4: All roles supported

---

### Step 5.4: Plugin Registration

**Create `tests/conftest.py`:**
- Register all plugins
- Environment setup
- Pytest configuration

**Action Items:**
- [ ] Create `tests/conftest.py`
- [ ] Register all plugins
- [ ] Test plugin registration
- [ ] Test fixture availability

**Acceptance:** All plugins registered, fixtures available

---

## Phase 6: UI Layer

### Step 6.1: Base Page Object

**Create `lib/pages/base_page.py`:**
- Base page class
- Common methods
- Wait strategies
- Error handling

**Action Items:**
- [ ] Create `lib/pages/base_page.py`
- [ ] Implement BasePage class
- [ ] Implement common methods
- [ ] Test base functionality

**Acceptance:** Base page works, common methods available

---

### Step 6.2: Login Page

**Create `lib/pages/login_page.py`:**
- Login form interaction
- Form filling
- Submit handling
- Success verification

**Action Items:**
- [ ] Create `lib/pages/login_page.py`
- [ ] Implement LoginPage class
- [ ] Test login functionality
- [ ] Test error handling

**Acceptance:** Login page works, can login successfully

---

### Step 6.3: Create Item Page

**Create `lib/pages/create_item_page.py`:**
- Form filling
- Conditional fields handling
- Type selection
- Success verification

**Key Features:**
- Handle PHYSICAL, DIGITAL, SERVICE types
- Conditional fields based on type
- Success message verification

**Action Items:**
- [ ] Create `lib/pages/create_item_page.py`
- [ ] Implement CreateItemPage class
- [ ] Implement form filling
- [ ] Implement conditional fields
- [ ] Test create item functionality
- [ ] Test all item types

**Acceptance:**
- AC-9.2: Uses correct UI selectors
- Can create all item types

---

### Step 6.4: Search Page

**Create `lib/pages/search_page.py`:**
- Search functionality
- Filter handling
- Sort handling
- Pagination handling
- Wait for ready state

**Key Features:**
- Wait for `data-test-ready="true"`
- Search with debounce
- Filter by status/category
- Sort by columns

**Action Items:**
- [ ] Create `lib/pages/search_page.py`
- [ ] Implement SearchPage class
- [ ] Implement search functionality
- [ ] Implement filters
- [ ] Implement sorting
- [ ] Implement pagination
- [ ] Test search functionality
- [ ] Test all features

**Acceptance:**
- AC-9.2: Uses correct UI selectors
- All search features work

---

## Phase 7: Test Examples

### Step 7.1: Smoke Test

**Create `tests/smoke/test_basic_flow.py`:**
- Simplest test: Login → View Items
- Verify basic flow works
- Verify authentication works

**Action Items:**
- [ ] Create `tests/smoke/test_basic_flow.py`
- [ ] Implement basic flow test
- [ ] Test authentication
- [ ] Test navigation

**Acceptance:**
- AC-10.1: End-to-end flow works
- Basic functionality verified

---

### Step 7.2: Verification Tests

**Create verification tests:**
- `tests/verification/test_user_pool.py`
- `tests/verification/test_authentication.py`
- `tests/verification/test_seed_data.py`

**Action Items:**
- [ ] Create user pool verification test
- [ ] Create authentication verification test
- [ ] Create seed data verification test
- [ ] Test all verification scenarios

**Acceptance:** All verification tests pass

---

### Step 7.3: UI Tests

**Create UI tests:**
- `tests/ui/test_create_item.py` (Flow 2)
- `tests/ui/test_search_discovery.py` (Flow 3)

**Action Items:**
- [ ] Create Flow 2 test (Create Item)
- [ ] Create Flow 3 test (Search & Discovery)
- [ ] Test all scenarios
- [ ] Test all item types

**Acceptance:**
- AC-10.1: Complete test flow works
- All UI tests pass

---

## Phase 8: Integration & Validation

### Step 8.1: Parallel Execution Testing

**Test parallel execution:**
- Run tests with pytest-xdist
- Verify no race conditions
- Verify all tests pass
- Verify performance

**Action Items:**
- [ ] Run tests with `-n 2`
- [ ] Run tests with `-n 4`
- [ ] Verify no conflicts
- [ ] Verify all tests pass

**Acceptance:**
- AC-6.1: Parallel execution works
- AC-6.2: Simultaneous acquisition works
- AC-6.3: No race conditions
- AC-6.5: Sequential vs parallel consistency

---

### Step 8.2: Acceptance Criteria Validation

**Validate all acceptance criteria:**
- Go through all 50 acceptance criteria
- Verify each one
- Document results

**Action Items:**
- [ ] Create acceptance criteria checklist
- [ ] Test each criterion
- [ ] Document results
- [ ] Fix any failures

**Acceptance:** All 50 acceptance criteria met

---

### Step 8.3: Performance Validation

**Validate performance targets:**
- Measure user acquisition time
- Measure token reuse time
- Measure global seed setup time
- Verify optimizations

**Action Items:**
- [ ] Measure all performance metrics
- [ ] Verify all targets met
- [ ] Document performance results

**Acceptance:**
- AC-8.1: < 5ms user acquisition
- AC-8.2: < 10ms token reuse
- AC-8.3: < 30s global seed setup
- AC-8.4: 99% reduction in config reads
- AC-8.5: 99% reduction in API calls

---

## Implementation Checklist

### Phase 0: Foundation
- [ ] Project structure created
- [ ] Dependencies installed
- [ ] Configuration management working
- [ ] User pool config created

### Phase 1: Core Utilities
- [ ] File locking utility
- [ ] API client wrapper
- [ ] Config loader verified

### Phase 2: User Pool Management
- [ ] UserLease class
- [ ] Morning roll call
- [ ] All acceptance criteria met

### Phase 3: Authentication
- [ ] SmartAuth (API)
- [ ] SmartUIAuth (Browser)
- [ ] All acceptance criteria met

### Phase 4: Data Management
- [ ] Seed factory
- [ ] Item builder
- [ ] MongoDB fixtures
- [ ] Global seed setup
- [ ] On-demand insertion
- [ ] CRUD operations
- [ ] All acceptance criteria met

### Phase 5: Fixtures and Actors
- [ ] Core fixtures
- [ ] API actors
- [ ] UI actors
- [ ] Plugin registration

### Phase 6: UI Layer
- [ ] Base page object
- [ ] Login page
- [ ] Create item page
- [ ] Search page

### Phase 7: Test Examples
- [ ] Smoke test
- [ ] Verification tests
- [ ] UI tests

### Phase 8: Integration & Validation
- [ ] Parallel execution tested
- [ ] All acceptance criteria validated
- [ ] Performance validated

---

## Success Criteria

### Framework Complete When:

- ✅ All 50 acceptance criteria met
- ✅ All components implemented
- ✅ All tests passing
- ✅ All performance targets met
- ✅ Documentation complete
- ✅ Ready for production use

---

## Next Steps

1. **Start with Phase 0** - Foundation setup
2. **Build incrementally** - One phase at a time
3. **Test continuously** - Test each component
4. **Validate against acceptance criteria** - Verify as you build
5. **Document as you go** - Keep documentation updated

---

**Roadmap Status:** ✅ **COMPLETE**  
**Implementation Readiness:** ✅ **READY**  
**Next Action:** Begin Phase 0 implementation
