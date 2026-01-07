# Framework Structure Guide

**Purpose:** Complete guide to understanding the framework architecture, folder structure, and organization patterns. Use this to learn the framework structure independently.

**Last Updated:** 2025-01-27  
**Status:** Production-ready framework

---

## Table of Contents

1. [Framework Overview](#framework-overview)
2. [Folder Structure](#folder-structure)
3. [Core Components](#core-components)
4. [Configuration Files](#configuration-files)
5. [Test Organization](#test-organization)
6. [Key Patterns & Concepts](#key-patterns--concepts)
7. [Entry Points](#entry-points)
8. [Data Flow](#data-flow)

---

## Framework Overview

### What This Framework Does

A **parallel web automation testing framework** that:
- Runs tests in parallel using `pytest-xdist`
- Manages shared user accounts across test workers
- Handles authentication (API tokens + browser sessions)
- Manages test data (seed data + on-demand insertion)
- Provides reusable fixtures for API and UI testing

### Core Principle

> **"Framework provides mechanisms, tester configures data"**

- Framework provides: User leasing, authentication, seed data setup mechanisms
- Tester is responsible: Configuring correct data for each user, setting up test scenarios
- Framework does NOT make: Role-based decisions, business logic decisions

---

## Folder Structure

```
final_framework_setup_web/
│
├── config/                          # Configuration files
│   ├── user_pool.json              # User credentials pool (static)
│   ├── user_state.json             # Runtime state (auto-created)
│   └── seed_users.json             # Users for seed data setup
│
├── state/                           # Browser storage state files
│   ├── admin1_test_com_storage.json
│   └── ...                         # Per-user Playwright storage state
│
├── utils/                           # Core utilities (foundation layer)
│   ├── config.py                   # Environment configuration
│   ├── file_lock.py                # Cross-process file locking
│   └── api_client.py               # HTTP client wrapper
│
├── lib/                            # Core library (business logic)
│   ├── users.py                    # User pool management
│   ├── auth.py                     # API authentication
│   ├── ui_auth.py                  # Browser authentication
│   ├── builders/                   # Data transformation
│   │   └── item_builder.py        # MongoDB ↔ API format conversion
│   └── pages/                      # Page Object Model (POM)
│       ├── base_page.py
│       ├── login_page.py
│       ├── create_item_page.py
│       └── search_page.py
│
├── fixtures/                        # Test data generation
│   └── seed_factory.py             # Generates test items
│
├── tests/                           # Test code
│   ├── conftest.py                 # Plugin registration (entry point)
│   ├── plugins/                    # Pytest plugins (fixtures)
│   │   ├── core.py                 # Core fixtures (user_lease, env_config)
│   │   ├── hooks.py                 # Session hooks (morning roll call)
│   │   ├── mongodb_fixtures.py     # MongoDB connection fixtures
│   │   ├── actors_api.py           # API actor fixtures (admin_actor, etc.)
│   │   ├── actors_ui.py             # UI actor fixtures (browser actors)
│   │   ├── api_fixtures.py         # CRUD operation fixtures
│   │   ├── data.py                 # Global seed data fixture
│   │   └── seed_fixtures.py        # On-demand data insertion
│   ├── verification/               # Framework verification tests
│   ├── smoke/                      # Smoke tests
│   ├── ui/                         # UI test examples
│   └── integration/                # Integration tests
│
├── docs/                           # Documentation
├── required_docs/                  # Requirements & specifications
│
├── pytest.ini                      # Pytest configuration
├── requirements.txt                # Python dependencies
└── verify_seed_data.py            # Utility script
```

---

## Core Components

### 1. Foundation Layer (`utils/`)

**Purpose:** Basic utilities used by everything else.

#### `utils/config.py`
- Loads environment variables from `.env`
- Provides `Config` class with all settings
- Default values for development

#### `utils/file_lock.py`
- `AtomicLock` class for cross-process synchronization
- Uses `filelock` library
- Context manager support (`with AtomicLock(...)`)

#### `utils/api_client.py`
- `APIClient` class wrapping `requests`
- Handles authentication headers
- GET, POST, PUT, DELETE methods

---

### 2. Core Library (`lib/`)

**Purpose:** Business logic for user management and authentication.

#### `lib/users.py`
- `UserLease` class for thread-safe user acquisition
- Manages user pool state file
- Uses file locking for parallel execution
- **Key concept:** User leasing (acquire → use → release)

#### `lib/auth.py`
- `SmartAuth` class for API token management
- Token validation with 5-minute TTL cache
- Auto-login on token expiration
- Persists tokens to state file

#### `lib/ui_auth.py`
- `SmartUIAuth` class for browser authentication
- Reuses Playwright storage state files
- Validates state before reuse
- Saves storage state after login

#### `lib/builders/item_builder.py`
- Converts data between formats:
  - API format ↔ MongoDB format
- Handles field mapping and transformations

#### `lib/pages/` (Page Object Model)
- Base classes for UI testing
- Encapsulates page interactions
- Reusable across tests

---

### 3. Test Infrastructure (`tests/plugins/`)

**Purpose:** Pytest fixtures that provide test capabilities.

#### `tests/plugins/core.py`
- `user_lease` fixture - Acquires/releases users
- `env_config` fixture - Environment configuration

#### `tests/plugins/hooks.py`
- `pytest_sessionstart` hook - Resets state at session start
- "Morning roll call" for crash recovery

#### `tests/plugins/mongodb_fixtures.py`
- `mongodb_connection` fixture - Session-scoped DB connection
- `mongodb_database` fixture - Database access

#### `tests/plugins/actors_api.py`
- `admin_actor` fixture - Authenticated admin user
- `editor_actor` fixture - Authenticated editor user
- `viewer_actor` fixture - Authenticated viewer user
- **Returns:** `{user, token, api}` dictionary

#### `tests/plugins/actors_ui.py`
- Browser-based actors for UI tests
- Uses `SmartUIAuth` for authentication
- Provides Playwright page objects

#### `tests/plugins/api_fixtures.py`
- `create_test_item` - Create items via API
- `update_test_item` - Update items
- `delete_test_item` - Soft delete
- `hard_delete_test_item` - Hard delete (internal API)

#### `tests/plugins/data.py`
- `global_seed` fixture - Session-scoped seed data
- Creates baseline data via MongoDB direct insertion
- Idempotent (checks before creating)

#### `tests/plugins/seed_fixtures.py`
- `insert_data_if_not_exists` fixture - On-demand data insertion
- Checks duplicates via API before inserting
- Returns created items

---

### 4. Test Data Generation (`fixtures/`)

#### `fixtures/seed_factory.py`
- `SeedFactory` class for generating test data
- Generates items: PHYSICAL, DIGITAL, SERVICE
- Uses UUIDs in names for isolation
- Ensures category-item type compatibility

---

## Configuration Files

### `config/user_pool.json`
**Purpose:** Static user credentials pool

**Structure:**
```json
{
  "ADMIN": [
    {"email": "admin1@test.com", "password": "pass123"},
    ...
  ],
  "EDITOR": [...],
  "VIEWER": [...]
}
```

**Key Points:**
- Static file (not modified at runtime)
- Organized by role
- Used by `lib/users.py` for user acquisition

---

### `config/user_state.json`
**Purpose:** Runtime state tracking (auto-created)

**Structure:**
```json
{
  "auth": {
    "admin1@test.com": {
      "token": "eyJhbGciOiJIUzI1NiIs..."
    }
  },
  "lease": {
    "admin1@test.com": {
      "role": "ADMIN",
      "status": "BUSY"
    }
  }
}
```

**Key Points:**
- Auto-created at runtime
- Two namespaces: `auth` (tokens) and `lease` (user reservations)
- Reset to `{}` at session start (morning roll call)
- Protected by file locking

---

### `config/seed_users.json`
**Purpose:** Users for global seed data setup

**Structure:**
```json
{
  "seed_users": [
    "admin1@test.com",
    "admin2@test.com"
  ]
}
```

**Key Points:**
- Used by `global_seed` fixture
- Defines which users get seed data
- Separate from `user_pool.json`

---

### `state/` directory
**Purpose:** Browser storage state files (Playwright)

**Files:**
- `{email}_storage.json` - Per-user browser authentication state
- Created by `SmartUIAuth` after login
- Reused across tests to avoid re-login

---

## Test Organization

### `tests/conftest.py`
**Purpose:** Plugin registration (entry point for pytest)

**Key Code:**
```python
pytest_plugins = [
    "tests.plugins.core",
    "tests.plugins.hooks",
    "tests.plugins.mongodb_fixtures",
    "tests.plugins.actors_api",
    "tests.plugins.actors_ui",
    "tests.plugins.api_fixtures",
    "tests.plugins.data",
    "tests.plugins.seed_fixtures",
]
```

**What it does:**
- Registers all plugin modules
- Makes all fixtures available to tests
- Runs automatically when pytest starts

---

### Test Categories

#### `tests/verification/`
- Tests that verify framework components work
- Examples: `test_user_pool.py`, `test_auth.py`, `test_file_lock.py`
- **Purpose:** Ensure framework is correct

#### `tests/smoke/`
- Quick smoke tests
- Verify basic functionality
- **Purpose:** Fast feedback

#### `tests/ui/`
- UI test examples
- Uses Page Object Model
- **Purpose:** Demonstrate UI testing patterns

#### `tests/integration/`
- End-to-end integration tests
- Full flows
- **Purpose:** Verify complete scenarios

---

## Key Patterns & Concepts

### 1. Fixture Scoping

**Session Scope:**
- Created once per test session
- Shared across all tests
- Examples: `mongodb_connection`, `global_seed`, `env_config`

**Function Scope:**
- Created fresh for each test
- Examples: `user_lease`, `admin_actor`, `create_test_item`

**Why it matters:**
- Session scope = expensive resources (DB connections)
- Function scope = test isolation (users, actors)

---

### 2. Actor Pattern

**Concept:** Encapsulate user + authentication + API client

**Example:**
```python
@pytest.fixture
def admin_actor():
    # Acquires user, authenticates, returns ready-to-use actor
    yield {"user": user, "token": token, "api": api}
    # Cleanup: releases user
```

**Benefits:**
- Tests get authenticated users easily
- Clean separation of concerns
- Automatic cleanup

---

### 3. File-Based Locking

**Concept:** Use file locks for cross-process coordination

**How it works:**
1. Multiple test workers (pytest-xdist) need to coordinate
2. File lock ensures only one worker modifies state at a time
3. Lock file: `config/user_state.json.lock`

**Used in:**
- `lib/users.py` - User acquisition/release
- `lib/auth.py` - Token saving
- `tests/plugins/hooks.py` - State reset

---

### 4. State Management

**Two namespaces in `user_state.json`:**

**`auth` namespace:**
- Owned by `lib/auth.py`
- Stores: `{email: {token: "..."}}`
- Purpose: Token persistence

**`lease` namespace:**
- Owned by `lib/users.py`
- Stores: `{email: {role: "...", status: "BUSY"}}`
- Purpose: User reservation tracking

**Why separate:**
- Prevents semantic collisions
- Clear ownership
- No interference between auth and leasing

---

### 5. Validation Caching

**Concept:** Cache validation results to avoid repeated API calls

**How it works:**
- In-memory cache: `{email: {valid: bool, timestamp: float}}`
- TTL: 5 minutes
- Reduces API calls by ~98%

**Used in:**
- `lib/auth.py` - Token validation
- `lib/ui_auth.py` - Storage state validation

---

### 6. Idempotent Operations

**Concept:** Operations that can be run multiple times safely

**Examples:**
- `global_seed` - Checks if data exists before creating
- `insert_data_if_not_exists` - Checks duplicates before inserting

**Why it matters:**
- Tests can be re-run safely
- No duplicate data
- Self-healing

---

## Entry Points

### Running Tests

**Basic:**
```bash
pytest
```

**Parallel:**
```bash
pytest -n auto  # Auto-detect CPU count
pytest -n 4     # Use 4 workers
```

**Specific:**
```bash
pytest tests/ui/              # Run UI tests
pytest tests/verification/    # Run verification tests
pytest tests/smoke/          # Run smoke tests
```

---

### Configuration

**Environment Variables (`.env`):**
```
API_BASE_URL=http://localhost:3000/api
FRONTEND_BASE_URL=http://localhost:3000
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=test_db
ENABLE_SEED_SETUP=true
```

**Pytest Configuration (`pytest.ini`):**
- Test discovery patterns
- Default options
- Test paths

---

## Data Flow

### User Acquisition Flow

```
Test starts
    ↓
Requests user_lease fixture
    ↓
UserLease.acquire() called
    ↓
Acquire file lock
    ↓
Read user_state.json (lease namespace)
    ↓
Find first free user
    ↓
Mark user as BUSY in lease namespace
    ↓
Save state file
    ↓
Release lock
    ↓
Return user to test
```

### Authentication Flow (API)

```
Test requests admin_actor fixture
    ↓
UserLease.acquire() - Get user
    ↓
SmartAuth.get_token() called
    ↓
Check validation cache (5-min TTL)
    ├─→ Cache hit? → Return token (fast path)
    └─→ Cache miss? → Continue...
    ↓
Load state file (auth namespace)
    ↓
Token exists?
    ├─→ Yes → Validate via API
    │   ├─→ Valid? → Update cache → Return token
    │   └─→ Invalid? → Login → Save token → Return token
    └─→ No → Login → Save token → Return token
```

### Seed Data Flow

```
Session starts
    ↓
global_seed fixture runs (session scope)
    ↓
For each user in seed_users.json:
    ↓
Check MongoDB: Does user have items?
    ├─→ Yes → Skip (idempotent)
    └─→ No → Generate items → Insert via MongoDB
    ↓
Yield seed info
    ↓
Available for all tests in session
```

---

## Key Files to Understand

### Must Understand (Core):
1. `lib/users.py` - User pool management
2. `lib/auth.py` - API authentication
3. `utils/file_lock.py` - Locking mechanism
4. `tests/conftest.py` - Plugin registration

### Should Understand (Infrastructure):
5. `tests/plugins/core.py` - Core fixtures
6. `tests/plugins/actors_api.py` - Actor pattern
7. `tests/plugins/mongodb_fixtures.py` - DB connections
8. `tests/plugins/data.py` - Seed data

### Nice to Understand (Utilities):
9. `lib/ui_auth.py` - Browser auth
10. `fixtures/seed_factory.py` - Data generation
11. `lib/pages/` - Page Object Model

---

## Common Questions

### Q: Where do I add new fixtures?
**A:** `tests/plugins/` - Create new file or add to existing one, register in `conftest.py`

### Q: How do I add a new user role?
**A:** Add to `config/user_pool.json`, create actor fixture in `tests/plugins/actors_api.py`

### Q: Where is test data generated?
**A:** `fixtures/seed_factory.py` - Modify or extend for new data types

### Q: How do I add a new page object?
**A:** `lib/pages/` - Create new file, inherit from `BasePage`

### Q: Where is configuration loaded?
**A:** `utils/config.py` - Uses `.env` file, provides `Config` class

---

## Next Steps for Learning

1. **Start with:** `tests/conftest.py` → Understand plugin registration
2. **Then:** `lib/users.py` → Understand user leasing
3. **Then:** `lib/auth.py` → Understand authentication
4. **Then:** `tests/plugins/actors_api.py` → Understand actor pattern
5. **Then:** Explore test examples in `tests/ui/` or `tests/integration/`

---

## Summary

**Framework Architecture:**
- **Foundation:** `utils/` - Basic utilities
- **Core:** `lib/` - Business logic (users, auth, pages)
- **Infrastructure:** `tests/plugins/` - Pytest fixtures
- **Data:** `fixtures/` - Test data generation
- **Config:** `config/` - Configuration files
- **Tests:** `tests/` - Test code organized by category

**Key Concepts:**
- File-based locking for parallel execution
- Namespaced state management (auth vs lease)
- Validation caching for performance
- Actor pattern for authenticated users
- Fixture scoping (session vs function)
- Idempotent operations

**Entry Point:**
- `tests/conftest.py` - Registers all plugins
- `pytest.ini` - Pytest configuration
- `requirements.txt` - Dependencies

---

**This guide provides enough information to understand the framework structure. Use it with another agent to explore specific components in detail.**
