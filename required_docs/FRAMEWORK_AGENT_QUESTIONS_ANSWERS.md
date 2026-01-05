# Framework Implementation - Questions & Answers

## For the Agent Building the Framework

This document answers common questions that arise when starting to build the framework from scratch. These answers provide practical guidance to help you get started quickly.

---

## Q1: What are the actual environment variable values?

**Answer:**

The actual values will be **provided by the user** when you start building. However, here are the **example/default values** you can use for development:

### Environment Variables Structure

```bash
# Database Connection
MONGODB_URI=mongodb://localhost:27017
# OR for cloud: mongodb+srv://user:pass@cluster.mongodb.net/dbname

MONGODB_DB_NAME=test

# API & Frontend URLs
API_BASE_URL=http://localhost:8000/api/v1
# OR production: https://testing-box.onrender.com/api/v1

FRONTEND_BASE_URL=http://localhost:3000
# OR production: https://testing-box.vercel.app

# Feature Flags
ENABLE_SEED_SETUP=true

# Internal Automation Key
INTERNAL_AUTOMATION_KEY=flowhub-secret-automation-key-2025
```

### Important Notes:

1. **Ask the user** for actual values before starting
2. **Use environment variables** - don't hardcode values
3. **Support both local and production** - use a config class pattern (see `utils/config.py` structure)
4. **Default to production** if no environment specified

### Implementation Pattern:

Create a `utils/config.py` that:
- Reads from environment variables
- Provides default values for development
- Supports multiple environments (local, production)
- Uses `python-dotenv` for `.env` file support

**Example structure:**
```python
# utils/config.py pattern
class Config:
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
    FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")
    MONGODB_URI = os.getenv("MONGODB_URI")
    MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "test")
    ENABLE_SEED_SETUP = os.getenv("ENABLE_SEED_SETUP", "false").lower() == "true"
    INTERNAL_AUTOMATION_KEY = os.getenv("INTERNAL_AUTOMATION_KEY", "flowhub-secret-automation-key-2025")
```

---

## Q2: What's the user pool configuration? (How many users per role, actual credentials?)

**Answer:**

### User Pool Structure

The user pool is configured in `config/user_pool.json`. The **structure** is:

```json
{
  "ADMIN": [
    {"email": "admin1@test.com", "password": "actual_password_here"},
    {"email": "admin2@test.com", "password": "actual_password_here"}
  ],
  "EDITOR": [
    {"email": "editor1@test.com", "password": "actual_password_here"},
    {"email": "editor2@test.com", "password": "actual_password_here"}
  ],
  "VIEWER": [
    {"email": "viewer1@test.com", "password": "actual_password_here"}
  ]
}
```

### Important Notes:

1. **Actual credentials will be provided by the user** - don't hardcode passwords
2. **Minimum requirements:**
   - At least **2 ADMIN** users (for parallel testing)
   - At least **2 EDITOR** users (for parallel testing)
   - At least **1 VIEWER** user (read-only testing)
3. **Capacity rule:** Number of users per role should be **>= number of parallel workers**
4. **The `reserved_by` field** is NOT in the config file - it's only in the runtime state file

### What to Do:

1. **Create `config/user_pool.json.example`** with placeholder values
2. **Ask the user** for actual credentials
3. **Validate** that there are enough users for parallel execution
4. **Document** the capacity requirements clearly

### Capacity Planning:

- If running with `-n 4` (4 parallel workers), you need:
  - At least 4 ADMIN users (if all tests use admin)
  - At least 4 EDITOR users (if all tests use editor)
  - Or a mix based on test distribution

**Rule:** `Number of users per role >= Number of parallel workers`

---

## Q3: What Python version and library versions should we use?

**Answer:**

### Python Version

**Use Python 3.9 or higher** (3.9, 3.10, 3.11, 3.12 are all fine)

Recommended: **Python 3.10 or 3.11** for best compatibility

### Library Versions

Use these **exact versions** from `requirements.txt`:

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

### Installation Steps:

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate (Windows)
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers
playwright install
```

### Important Notes:

1. **Use `>=` for versions** - allows minor updates
2. **Test with the minimum versions** to ensure compatibility
3. **Playwright browsers** must be installed separately (`playwright install`)
4. **pytest-xdist** is required for parallel execution

---

## Q4: What's the expected parallel worker count for pytest-xdist?

**Answer:**

### Default Recommendation

**Start with 2-4 workers** for initial development and testing:

```bash
# Run with 2 workers
pytest -n 2

# Run with 4 workers
pytest -n 4
```

### Capacity Planning

The worker count depends on:

1. **Number of users available** per role
2. **Test execution time** (more workers = faster, but need more users)
3. **System resources** (CPU, memory)

### Rule of Thumb:

- **Minimum:** 2 workers (for parallel testing validation)
- **Recommended:** 4 workers (good balance)
- **Maximum:** Limited by user pool size

### Important:

**The framework uses a "Capacity Guarantee" model:**
- If you request a user and none are available → **FAIL FAST** (infrastructure error)
- This means: **Number of users per role MUST be >= number of workers**

### Example:

If you have:
- 2 ADMIN users
- 2 EDITOR users
- 1 VIEWER user

Then you can run:
- `pytest -n 2` (2 workers) ✅ Works
- `pytest -n 4` (4 workers) ❌ Fails (not enough users)

### What to Do:

1. **Start with 2 workers** during development
2. **Ask the user** what worker count they want to support
3. **Ensure** user pool has enough users for that count
4. **Document** the capacity requirements

---

## Q5: Should we use the Test Data Factory pattern from the guide, or build a simpler version?

**Answer:**

### Use the Test Data Factory Pattern

**Yes, implement the factory pattern** as described in the blueprint. Here's why:

1. **Flexibility:** Tester can configure data generation per user/role
2. **Maintainability:** Centralized data generation logic
3. **Scalability:** Easy to add new data types
4. **Framework principle:** Framework provides mechanism, tester configures

### Implementation Approach:

**Start with a simple factory, then extend:**

#### Phase 1: Basic Factory (Start Here)

```python
# fixtures/seed_factory.py
class SeedDataFactory:
    def create_item(self, name, category, item_type, price, **kwargs):
        # Basic item creation
        # Add type-specific fields based on item_type
        pass
    
    def create_items_for_user(self, user_email, role, count=10):
        # Generate items based on role
        # Return list of item dictionaries
        pass
```

#### Phase 2: Extend as Needed

- Add role-specific methods (`create_admin_items`, `create_editor_items`)
- Add category-item type compatibility logic
- Add randomization for variety

### Key Points:

1. **Don't over-engineer** - start simple
2. **Follow the blueprint** - it has the right level of detail
3. **Make it configurable** - tester should control what data is generated
4. **Handle category-item type rules:**
   - "Electronics" → Must be PHYSICAL
   - "Software" → Must be DIGITAL
   - "Services" → Must be SERVICE

### What NOT to Do:

- Don't hardcode specific test data
- Don't make role-based decisions in the factory (tester configures)
- Don't skip the factory (it's needed for global seed setup)

---

## Q6: What's the exact folder structure preference? (root level, nested, etc.)

**Answer:**

### Use the Structure from the Blueprint

Follow the **exact structure** documented in Part 7 of the blueprint:

```
project/
├── config/
│   ├── user_pool.json          # User credentials (user provides)
│   └── user_state.json         # Runtime state (auto-created, don't create manually)
├── utils/
│   ├── file_lock.py
│   ├── api_client.py
│   └── config.py
├── lib/
│   ├── users.py
│   ├── auth.py
│   ├── ui_auth.py
│   ├── builders/
│   │   └── item_builder.py
│   └── pages/
│       ├── base_page.py
│       ├── login_page.py
│       ├── create_item_page.py
│       └── search_page.py
├── fixtures/
│   └── seed_factory.py
├── tests/
│   ├── conftest.py
│   ├── plugins/
│   │   ├── core.py
│   │   ├── hooks.py
│   │   ├── actors_api.py
│   │   ├── actors_ui.py
│   │   ├── data.py
│   │   ├── mongodb_fixtures.py
│   │   ├── seed_fixtures.py
│   │   └── api_fixtures.py
│   ├── ui/
│   │   ├── test_create_item.py
│   │   └── test_search_discovery.py
│   └── verification/
│       └── test_data_management_complete.py
├── requirements.txt
├── pytest.ini
└── .env (optional, for environment variables)
```

### Important Notes:

1. **Root level** - Keep it flat, don't nest too deep
2. **`config/`** - Configuration files
3. **`utils/`** - Utility modules (reusable across framework)
4. **`lib/`** - Core library code (framework logic)
5. **`fixtures/`** - Data generation (not pytest fixtures)
6. **`tests/`** - All test code and pytest fixtures
7. **`tests/plugins/`** - Pytest plugin modules (fixtures)

### File Naming:

- Use **snake_case** for Python files
- Use **descriptive names** that indicate purpose
- **`conftest.py`** - Special pytest file (auto-discovered)

### What to Create First:

1. **Create folder structure** first
2. **Add `__init__.py`** files to make packages
3. **Start with `utils/`** and `lib/` (foundation)
4. **Then `tests/plugins/`** (fixtures)
5. **Finally `tests/ui/`** (test cases)

---

## Q7: Should we start with simple print() logging or implement structured logging from day 1?

**Answer:**

### Start with Simple print() Logging

**Use `print()` statements for now.** Here's why:

1. **Faster to implement** - no setup overhead
2. **Sufficient for initial development** - you can see what's happening
3. **Easy to debug** - immediate output
4. **Can upgrade later** - structured logging is a "nice to have"

### Recommended Approach:

#### Phase 1: Simple print() (Start Here)

```python
# Use descriptive print statements
print(f"[UserLease] Acquiring {role} user...")
print(f"[SmartAuth] Token for {email} is VALID (cached)")
print(f"[SeedSetup] Created {count} items for {email}")
```

**Format:** `[Component] Message`

#### Phase 2: Consider Structured Logging Later

After the framework is working, you can:
- Replace `print()` with `logging` module
- Add log levels (DEBUG, INFO, WARNING, ERROR)
- Add structured format (JSON, etc.)
- Add file output

### What to Do:

1. **Use `print()`** with consistent format: `[Component] Message`
2. **Include context** in messages (user email, item ID, etc.)
3. **Use clear prefixes** to identify components:
   - `[UserLease]` - User pool management
   - `[SmartAuth]` - API authentication
   - `[SmartUIAuth]` - UI authentication
   - `[SeedSetup]` - Seed data setup
   - `[API]` - API operations
   - `[Insert]` - Data insertion

### Example Pattern:

```python
# Good
print(f"[UserLease] Acquired user: {user['email']}")
print(f"[SmartAuth] Token validation for {email}: {'VALID' if is_valid else 'EXPIRED'}")

# Avoid
print("User acquired")  # Too vague
print(f"Token: {token}")  # Too verbose, might expose sensitive data
```

### Important:

- **Don't log sensitive data** (passwords, full tokens)
- **Use consistent format** across all components
- **Include enough context** to debug issues
- **Can upgrade to structured logging later** (it's in recommendations, not requirements)

---

## Q8: What test scenarios should we implement first as examples?

**Answer:**

### Implementation Order (Priority)

Implement tests in this order to validate the framework incrementally:

#### Phase 1: Foundation Tests (Start Here)

**1. User Pool Management Test**
```python
# tests/verification/test_user_pool.py
def test_user_acquisition_works():
    # Verify user can be acquired
    # Verify user is released after test
    pass

def test_parallel_user_acquisition():
    # Verify multiple workers can acquire different users
    # Verify no race conditions
    pass
```

**2. Authentication Test**
```python
# tests/verification/test_authentication.py
def test_api_auth_works():
    # Verify SmartAuth can login
    # Verify token is cached
    # Verify token validation works
    pass

def test_ui_auth_works():
    # Verify SmartUIAuth can login
    # Verify storage state is saved
    # Verify state reuse works
    pass
```

#### Phase 2: Data Management Tests

**3. Seed Data Setup Test**
```python
# tests/verification/test_seed_data.py
def test_global_seed_setup():
    # Verify global seed data is created
    # Verify ENABLE_SEED_SETUP flag works
    pass

def test_on_demand_insertion():
    # Verify insert_data_if_not_exists works
    # Verify duplicate checking works
    pass
```

#### Phase 3: UI Integration Tests

**4. Flow 2: Create Item Test**
```python
# tests/ui/test_create_item.py
def test_create_digital_item():
    # Verify can create DIGITAL item via UI
    # Verify POM works
    # Verify success message appears
    pass
```

**5. Flow 3: Search Test**
```python
# tests/ui/test_search_discovery.py
def test_search_by_name():
    # Verify search functionality works
    # Verify results are filtered correctly
    pass
```

### Recommended First Test (Simplest)

**Start with this simple test to verify the foundation:**

```python
# tests/smoke/test_basic_flow.py
def test_admin_can_login_and_view_items(admin_ui_actor, env_config):
    """Simplest test: Login and view items list"""
    actor = admin_ui_actor
    page = actor['page']
    
    # Navigate to items page
    page.goto(f"{env_config.FRONTEND_BASE_URL}/items")
    
    # Verify page loads (not redirected to login)
    assert "/login" not in page.url
    
    # Verify items page loaded
    assert "/items" in page.url or page.url.endswith("/items")
    
    print("[Smoke] Basic flow works: Login → View Items")
```

### Test Implementation Strategy:

1. **Start with smoke tests** - verify basic functionality
2. **Add verification tests** - test each component
3. **Add UI tests** - test full flows
4. **Add integration tests** - test component interactions

### What to Test First:

**Priority 1 (Must Have):**
- ✅ User pool acquisition/release
- ✅ API authentication
- ✅ UI authentication
- ✅ Basic UI navigation

**Priority 2 (Important):**
- ✅ Seed data setup
- ✅ Data insertion
- ✅ Flow 2: Create item
- ✅ Flow 3: Search

**Priority 3 (Nice to Have):**
- ✅ Update operations
- ✅ Delete operations
- ✅ Filter/Sort/Pagination
- ✅ RBAC verification

### Test File Structure:

```
tests/
├── smoke/
│   └── test_basic_flow.py          # Start here
├── verification/
│   ├── test_user_pool.py           # Foundation
│   ├── test_authentication.py      # Foundation
│   └── test_seed_data.py           # Data management
└── ui/
    ├── test_create_item.py         # Flow 2
    └── test_search_discovery.py    # Flow 3
```

---

## Summary: Getting Started Checklist

Before you start building, make sure you have:

1. ✅ **Environment variables** - Ask user for actual values
2. ✅ **User pool configuration** - Ask user for credentials and count
3. ✅ **Python version** - 3.10 or 3.11 recommended
4. ✅ **Dependencies** - Install from requirements.txt
5. ✅ **Worker count** - Start with 2-4 workers
6. ✅ **Factory pattern** - Implement as described in blueprint
7. ✅ **Folder structure** - Follow blueprint exactly
8. ✅ **Logging** - Start with print() statements
9. ✅ **Test scenarios** - Start with smoke test, then verification tests

---

## Questions to Ask the User

Before starting, ask the user:

1. **"What are the actual environment variable values?"**
   - API_BASE_URL, FRONTEND_BASE_URL, MONGODB_URI, etc.

2. **"What's the user pool configuration?"**
   - How many users per role?
   - What are the actual credentials?

3. **"What parallel worker count should we support?"**
   - This determines minimum user pool size

4. **"What environment are we targeting?"**
   - Local development?
   - Production/staging?

5. **"Are there any specific test scenarios you want prioritized?"**
   - Any critical flows to test first?

---

**Remember:** The blueprint has all the technical details. These answers help you get started practically. When in doubt, refer to the blueprint and ask the user for clarification.
