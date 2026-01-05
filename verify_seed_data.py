"""Quick verification script to check global seed data creation."""

import json
from pathlib import Path
from pymongo import MongoClient
from utils.config import Config

# Load seed users config
seed_config_path = Path("config/seed_users.json")
with open(seed_config_path, 'r') as f:
    seed_config = json.load(f)
seed_users = seed_config.get("seed_users", [])

print(f"Configured seed users: {len(seed_users)}")
for email in seed_users:
    print(f"  - {email}")

# Connect to MongoDB
client = MongoClient(Config.MONGODB_URI)
db = client[Config.MONGODB_DB_NAME]
items_collection = db[Config.MONGODB_ITEMS_COLLECTION]
users_collection = db['users']

print(f"\nChecking MongoDB for seed data...")

# Get user IDs for seed users
seed_user_ids = {}
for email in seed_users:
    user_doc = users_collection.find_one({"email": email})
    if user_doc:
        seed_user_ids[email] = user_doc['_id']
    else:
        print(f"  WARNING: User {email} not found in MongoDB")

print(f"\nSeed users found in MongoDB: {len(seed_user_ids)}")

# Count items per seed user
total_seed_items = 0
for email, user_id in seed_user_ids.items():
    count = items_collection.count_documents({"created_by": user_id})
    total_seed_items += count
    status = "[OK]" if count > 0 else "[MISSING]"
    print(f"  {status} {email}: {count} items")

print(f"\nTotal seed items: {total_seed_items}")
print(f"Expected: {len(seed_user_ids)} users × 15 items = {len(seed_user_ids) * 15} items")

# Count all items (should be seed items + any test items)
total_all_items = items_collection.count_documents({})
print(f"\nTotal items in database: {total_all_items}")
print(f"  - Seed items: {total_seed_items}")
print(f"  - Other items: {total_all_items - total_seed_items}")

client.close()
