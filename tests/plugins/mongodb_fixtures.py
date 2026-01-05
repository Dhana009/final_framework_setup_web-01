"""MongoDB fixtures for direct database operations."""

import pytest
from pymongo import MongoClient
from pymongo.database import Database
from utils.config import Config


@pytest.fixture(scope="session")
def mongodb_connection():
    """Session-scoped MongoDB connection fixture.

    Provides a MongoDB client connection for the entire test session.
    The connection is reused across all tests for performance.

    Yields:
        MongoClient: MongoDB client instance

    Raises:
        Exception: If connection fails
    """
    if not Config.MONGODB_URI:
        pytest.skip("MONGODB_URI not configured")

    client = MongoClient(Config.MONGODB_URI)
    
    try:
        # Verify connection
        client.admin.command('ping')
        yield client
    finally:
        client.close()


@pytest.fixture(scope="session")
def mongodb_database(mongodb_connection):
    """Session-scoped MongoDB database fixture.

    Provides access to the test database for the entire session.

    Args:
        mongodb_connection: MongoDB client fixture

    Yields:
        Database: MongoDB database instance
    """
    db = mongodb_connection[Config.MONGODB_DB_NAME]
    yield db
