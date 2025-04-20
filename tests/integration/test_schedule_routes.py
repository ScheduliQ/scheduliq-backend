def test_add_list_and_delete_schedule(test_client):
    """
    Walks through:
      1. POST /schedule/add
      2. GET /schedule/all
      3. DELETE /schedule/remove/<id>
    Verifies each status code and payload.
    """
    # 1. Add a schedule
    add_resp = test_client.post("/schedule/add", json={"days": ["mon", "tue"]})
    assert add_resp.status_code == 201
    data = add_resp.get_json()
    sched_id = data["id"]
    assert data["message"] == "Schedule added successfully"

    # 2. It should appear in /schedule/all
    list_resp = test_client.get("/schedule/all")
    schedules = list_resp.get_json()
    assert any(s["_id"] == sched_id for s in schedules)

    # 3. Remove it
    del_resp = test_client.delete(f"/schedule/remove/{sched_id}")
    assert del_resp.status_code == 201
    response = test_client.get("/schedule/all")
    list2=response.get_json()
    assert not any(s["_id"] == sched_id for s in list2)
