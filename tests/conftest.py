"""Pytest configuration and plugin registration."""

# Register all pytest plugins
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
