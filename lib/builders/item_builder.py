"""Item builder for transforming factory data to MongoDB/API format."""

import re
from typing import Dict, Any, Union
from datetime import datetime, timezone
from bson import ObjectId
from fixtures.seed_factory import SeedFactory


class ItemBuilder:
    """Builder for transforming factory data to different formats.

    This class transforms data from SeedFactory into formats suitable for:
    - MongoDB direct insertion
    - API requests
    """

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize item name for MongoDB (trim + lowercase).

        Args:
            name: Item name

        Returns:
            Normalized name (trimmed and lowercased)
        """
        return name.strip().lower()

    @staticmethod
    def _normalize_category(category: str) -> str:
        """Normalize category to Title Case for MongoDB.

        Args:
            category: Category string

        Returns:
            Normalized category in Title Case (first letter uppercase, rest lowercase per word)
        """
        # Title Case: First letter of each word uppercase, rest lowercase
        # Match the JavaScript regex: /\w\S*/g
        def title_case_word(match):
            word = match.group(0)
            return word[0].upper() + word[1:].lower() if len(word) > 1 else word.upper()
        
        # Apply Title Case to each word
        return re.sub(r'\w\S*', title_case_word, category.strip())

    @staticmethod
    def to_mongodb_format(item_data: Dict[str, Any], user_id: Union[str, ObjectId]) -> Dict[str, Any]:
        """Convert factory item data to MongoDB document format.

        Args:
            item_data: Item data from SeedFactory
            user_id: MongoDB user ID (ObjectId or ObjectId string)

        Returns:
            Dictionary in MongoDB document format with all required fields including
            normalizedName and normalizedCategory
        """
        # Convert user_id to ObjectId if it's a string
        if isinstance(user_id, str):
            created_by = ObjectId(user_id)
        else:
            created_by = user_id

        # Compute normalized fields
        name = item_data.get("name", "")
        category = item_data.get("category", "")
        normalized_name = ItemBuilder._normalize_name(name)
        normalized_category = ItemBuilder._normalize_category(category)

        # Create MongoDB document
        doc = {
            **item_data,
            "created_by": created_by,  # ObjectId type
            "is_active": item_data.get("is_active", True),
            "version": 1,
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc),
            "normalizedName": normalized_name,
            "normalizedCategory": normalized_category,
        }

        # Ensure dimensions is properly structured for PHYSICAL items
        if item_data.get("item_type") == "PHYSICAL" and "dimensions" in doc:
            if isinstance(doc["dimensions"], dict):
                # Already in correct format
                pass
            else:
                # Convert if needed
                doc["dimensions"] = {
                    "length": doc.get("length", 10.0),
                    "width": doc.get("width", 5.0),
                    "height": doc.get("height", 3.0)
                }

        return doc

    @staticmethod
    def to_api_format(item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert factory item data to API request format.

        Args:
            item_data: Item data from SeedFactory

        Returns:
            Dictionary in API request format
        """
        # API format is similar to factory format, but may need adjustments
        api_data = {**item_data}

        # Remove fields that API doesn't accept
        api_data.pop("created_by", None)
        api_data.pop("createdAt", None)
        api_data.pop("updatedAt", None)
        api_data.pop("version", None)

        return api_data
