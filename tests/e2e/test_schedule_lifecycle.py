# tests/e2e/test_schedule_lifecycle.py

def test_full_schedule_lifecycle(test_client):
    """
    E2E test for a full schedule workflow:
      1. Add a schedule.
      2. Update it.
      3. Confirm it's the latest.
      4. Remove it.
      5. Verify nothing remains.
    This simulates a real usage path from start to finish.
    """
    # 1. Add
    add = test_client.post("/schedule/add", json={"days": ["wed"]})
    assert add.status_code == 201
    sid = add.get_json()["id"]
    print(f"Schedule ID: {sid}")
    # 2. Update
    upd = test_client.put(f"/schedule/update/{sid}", json={"days": ["thu"]})
    assert upd.status_code == 200
    assert upd.get_json()["message"] == "Schedule updated successfully"

    # 3. Latest should match our ID
    latest = test_client.get("/schedule/latest")
    assert latest.status_code == 200
    assert latest.get_json()["_id"] == sid

    # 4. Remove
    rem = test_client.delete(f"/schedule/remove/{sid}")
    assert rem.status_code == 201

    # 5. Now no schedules remain
    latest2 = test_client.get("/schedule/latest")
    assert latest2.status_code == 404
    assert latest2.get_json().get("message", "").lower().startswith("no schedules")
