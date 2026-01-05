# Framework Quick Start

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Install browsers: `playwright install`
3. Configure `.env` with your URLs and credentials
4. Run tests: `pytest tests/ -v`

## Usage

```python
# API testing with user pool
def test_example(admin_actor):
    response = admin_actor["api"].get("/items")
    assert response.status_code == 200

# User acquisition
with UserLease(role="ADMIN") as lease:
    user = lease.user
    # Use user for testing
```

## Key Features

- ✅ Parallel execution support
- ✅ Automatic user management
- ✅ Token caching
- ✅ Test data generation
