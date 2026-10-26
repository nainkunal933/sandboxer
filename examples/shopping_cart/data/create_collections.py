# /// script
# requires-python = ">=3.12"
# dependencies = ["pymongo>=4.15,<5"]
# ///
"""Create shopping cart collections with JSON Schema validators from external files.

Run with: uv run examples/shopping_cart/data/create_collections.py
Set MONGODB_URI to override the default mongodb://127.0.0.1:27017 connection.
"""

import json
import os
from pathlib import Path

from pymongo import MongoClient
from pymongo.errors import CollectionInvalid


def main() -> None:
    """Create collections or update their validators without deleting existing data."""
    schema_directory = Path(__file__).resolve().parent / "schemas"
    collection_schemas = {
        name: json.loads((schema_directory / f"{name}.schema.json").read_text(encoding="utf-8"))
        for name in ("carts", "orders", "products")
    }
    uri = os.environ.get("MONGODB_URI", "mongodb://127.0.0.1:27017")
    with MongoClient(uri, serverSelectionTimeoutMS=5000) as client:
        database = client["shopping_cart"]
        for name, schema in collection_schemas.items():
            validation_options = {
                "validator": {"$jsonSchema": schema},
                "validationLevel": "strict",
                "validationAction": "error",
            }
            try:
                database.create_collection(name, **validation_options)
            except CollectionInvalid:
                database.command("collMod", name, **validation_options)
                print(f"Updated validator for existing collection: {name}")
            else:
                print(f"Created collection: {name}")


if __name__ == "__main__":
    main()
