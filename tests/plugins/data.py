"""Global seed data fixtures for test session."""

import pytest
from pymongo.database import Database
from bson import ObjectId
from fixtures.seed_factory import SeedFactory, ItemType
from lib.builders.item_builder import ItemBuilder
from utils.config import Config


@pytest.fixture(scope="session")
def global_seed(mongodb_database, mongodb_connection):
    """Session-scoped global seed fixture.

    Creates seed data for configured users (from config/seed_users.json) at the start of the test session.
    This fixture is idempotent - it checks if seed data exists before creating.

    Args:
        mongodb_database: MongoDB database fixture
        mongodb_connection: MongoDB connection fixture

    Yields:
        Dictionary with seed data information:
        - users: List of users with seed data
        - items_per_user: Number of items created per user

    Note:
        Only runs if ENABLE_SEED_SETUP is True in config.
        Reads seed user list from config/seed_users.json (not from user_pool.json).
    """
    if not Config.ENABLE_SEED_SETUP:
        pytest.skip("ENABLE_SEED_SETUP is False, skipping global seed setup")

    # Get seed users from config
    import json
    from pathlib import Path
    
    seed_config_path = Path("config/seed_users.json")
    if not seed_config_path.exists():
        pytest.skip("Seed users config not found (config/seed_users.json)")

    with open(seed_config_path, 'r') as f:
        seed_config = json.load(f)
    
    seed_users = seed_config.get("seed_users", [])
    if not seed_users:
        pytest.skip("No seed users configured in seed_users.json")

    # Collection for items
    items_collection = mongodb_database[Config.MONGODB_ITEMS_COLLECTION]
    users_collection = mongodb_database['users']

    # Track seed data
    seed_info = {
        "users": [],
        "items_per_user": 15  # Default: 15 items per user
    }

    # For each configured seed user, create seed data
    for user_email in seed_users:
        # Get user ID from database (users collection)
        user_doc = users_collection.find_one({"email": user_email})
        
        if not user_doc:
            # User doesn't exist in DB, skip
            continue

        # Get user_id as ObjectId (not string)
        user_id = user_doc['_id']  # Already ObjectId from MongoDB
        
        # Determine user role (for seed_info tracking)
        # Try to find role from user_pool.json for display purposes
        role = "UNKNOWN"
        user_pool_path = Path("config/user_pool.json")
        if user_pool_path.exists():
            with open(user_pool_path, 'r') as f:
                user_pool = json.load(f)
            for r, users in user_pool.items():
                if any(u.get('email') == user_email for u in users):
                    role = r
                    break

        # Check if seed data already exists (idempotent check)
        existing_count = items_collection.count_documents(
            {"created_by": user_id}
        )

        if existing_count > 0:
            # Any data exists, skip creation (idempotent per AC-1.3)
            seed_info["users"].append({
                "email": user_email,
                "role": role,
                "items_count": existing_count,
                "status": "existing"
            })
            continue

        # Create seed items for this user
        items_to_insert = []
        
        # Generate 15 items per user (5 PHYSICAL, 5 DIGITAL, 5 SERVICE)
        for i in range(5):
            # PHYSICAL items
            item_data = SeedFactory.generate_physical_item()
            mongo_doc = ItemBuilder.to_mongodb_format(item_data, user_id)
            items_to_insert.append(mongo_doc)

            # DIGITAL items
            item_data = SeedFactory.generate_digital_item()
            mongo_doc = ItemBuilder.to_mongodb_format(item_data, user_id)
            items_to_insert.append(mongo_doc)

            # SERVICE items
            item_data = SeedFactory.generate_service_item()
            mongo_doc = ItemBuilder.to_mongodb_format(item_data, user_id)
            items_to_insert.append(mongo_doc)

        # Bulk insert items (handle duplicates gracefully)
        if items_to_insert:
            try:
                items_collection.insert_many(items_to_insert, ordered=False)
                seed_info["users"].append({
                    "email": user_email,
                    "role": role,
                    "items_count": len(items_to_insert),
                    "status": "created"
                })
            except Exception as e:
                # Handle bulk write errors (duplicates, etc.)
                # Try inserting one by one to identify which ones succeed
                inserted_count = 0
                for item in items_to_insert:
                    try:
                        items_collection.insert_one(item)
                        inserted_count += 1
                    except Exception:
                        # Item already exists or other error, skip
                        pass
                
                seed_info["users"].append({
                    "email": user_email,
                    "role": role,
                    "items_count": inserted_count,
                    "status": "partial" if inserted_count < len(items_to_insert) else "created"
                })

    yield seed_info

    # Cleanup (if CLEANUP_SEED_ON_START is True, cleanup happens at start)
    # No cleanup needed here - seed data persists across tests
