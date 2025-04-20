# tests/unit/test_weekly_schedule_model.py

import pytest
from pymongo import MongoClient
from configs.envconfig import MONGO_URI
from models.weekly_schedule_model import WeeklyScheduleModel

def test_add_and_prune_schedules():
    """
    Unit test for WeeklyScheduleModel.add_schedule.
    Inserts MAX_DOCUMENTS+1 schedules and verifies that the oldest
    is dropped so only MAX_DOCUMENTS remain.
    """
    client = MongoClient(MONGO_URI)
    db = client["tests"]
    coll = db["weekly_schedule"]

    # Insert one more than the max
    for _ in range(WeeklyScheduleModel.MAX_DOCUMENTS + 1):
        resp = WeeklyScheduleModel.add_schedule({"days": []})
        assert resp["message"] == "Schedule added successfully"

    # After pruning, count should equal MAX_DOCUMENTS
    assert coll.count_documents({}) == WeeklyScheduleModel.MAX_DOCUMENTS

def test_remove_nonexistent():
    """
    Unit test for WeeklyScheduleModel.remove_schedule.
    Attempting to remove an ID that doesn't exist should return an error dict.
    """
    fake_id = "000000000000000000000000"
    result = WeeklyScheduleModel.remove_schedule(fake_id)
 # We expect a tuple: (error_dict, status_code)
    assert isinstance(result, tuple), "Expected remove_schedule to return (payload, status)"
    error_payload, status_code = result

    # First element must be a dict with an 'error' key
    assert isinstance(error_payload, dict)
    assert "error" in error_payload

    # Second element must be the 404 status
    assert status_code == 404