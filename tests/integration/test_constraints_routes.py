# tests/integration/test_constraints_routes.py

from pymongo import MongoClient
from configs.envconfig import MONGO_URI

def test_constraints_crud_flow(test_client):
    """
    Full CRUD on /constraints/ endpoints:
      1. Seed a user so the model can look up first_name/last_name/jobs.
      2. POST to create/update constraints.
      3. GET them back.
      4. DELETE them.
      5. Confirm GET now returns 404.
    """
    # 1. Seed the 'users' collection in the same 'tests' DB
    client = MongoClient(MONGO_URI)
    tests_db = client["tests"]
    tests_db["users"].insert_one({
        "uid": "u123",
        "first_name": "Alice",
        "last_name": "Smith",
        "jobs": "Waiter,Bartender"
    })

    tests_db["manager_settings"].insert_one({
        "activeVersion": "v1"
    })

    # 2. Create/update
    payload = {"uid": "u123", "constraints": "", "availability": []}
    post_resp = test_client.post("/constraints/", json=payload)
    assert post_resp.status_code == 200
    assert post_resp.get_json()["message"].startswith("Constraint created")

    # 3. Retrieve
    get_resp = test_client.get("/constraints/u123")
    assert get_resp.status_code == 200
    assert get_resp.get_json()["uid"] == "u123"

    # 4. Delete
    del_resp = test_client.delete("/constraints/remove/u123")
    assert del_resp.status_code == 200

    # 5. Now GET should 404
    notfound = test_client.get("/constraints/u123")
    assert notfound.status_code == 404
