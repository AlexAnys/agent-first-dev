def test_create_complete_list_and_patch_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["completed"] is False
    assert "created_at" in item and "updated_at" in item

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["completed"] is True

    r = client.get("/action-items/", params={"completed": True, "limit": 5, "sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.patch(f"/action-items/{item['id']}", json={"description": "Updated"})
    assert r.status_code == 200
    patched = r.json()
    assert patched["description"] == "Updated"


def test_get_action_item(client):
    payload = {"description": "Get Test Item"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201
    item_id = r.json()["id"]

    r = client.get(f"/action-items/{item_id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == item_id
    assert data["description"] == "Get Test Item"
    assert data["completed"] is False


def test_get_action_item_not_found(client):
    r = client.get("/action-items/99999")
    assert r.status_code == 404
    assert "Action item not found" in r.json()["detail"]


def test_delete_action_item(client):
    payload = {"description": "Delete Test Item"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201
    item_id = r.json()["id"]

    r = client.delete(f"/action-items/{item_id}")
    assert r.status_code == 204
    assert r.text == ""

    r = client.get(f"/action-items/{item_id}")
    assert r.status_code == 404


def test_delete_action_item_not_found(client):
    r = client.delete("/action-items/99999")
    assert r.status_code == 404
    assert "Action item not found" in r.json()["detail"]


def test_action_item_description_validation(client):
    # Description min_length=1
    r = client.post("/action-items/", json={"description": ""})
    assert r.status_code == 422

    # Description max_length=500
    r = client.post("/action-items/", json={"description": "a" * 501})
    assert r.status_code == 422

    # Valid payload
    r = client.post("/action-items/", json={"description": "Valid description"})
    assert r.status_code == 201

