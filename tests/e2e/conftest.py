# tests/e2e/conftest.py
import os, sys
from pymongo import MongoClient
import pytest



# Ensure tests point at your local test DB
os.environ["FLASK_ENV"] = "testing"
os.environ["MONGO_URI"]  = "mongodb://localhost:27017"

@pytest.fixture(autouse=True)
def clear_weekly_schedule_collection():
    """Runs before EACH E2E test to start with zero schedules."""
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["tests"]
    db["weekly_schedule"].delete_many({})
    yield
    db["weekly_schedule"].delete_many({})
