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


def test_action_items_pagination(client):
    """Test pagination functionality for action items."""
    # Create multiple action items
    items = []
    for i in range(10):
        payload = {"description": f"Action item {i}"}
        r = client.post("/action-items/", json=payload)
        assert r.status_code == 201
        items.append(r.json())

    # Test limit
    r = client.get("/action-items/", params={"limit": 3})
    assert r.status_code == 200
    result = r.json()
    assert len(result) == 3

    # Test skip
    r = client.get("/action-items/", params={"skip": 2, "limit": 3})
    assert r.status_code == 200
    result = r.json()
    assert len(result) == 3

    # Test skip beyond available items
    r = client.get("/action-items/", params={"skip": 100, "limit": 10})
    assert r.status_code == 200
    result = r.json()
    assert len(result) == 0

    # Test limit boundary - minimum
    r = client.get("/action-items/", params={"limit": 1})
    assert r.status_code == 200
    result = r.json()
    assert len(result) == 1

    # Test limit boundary - maximum
    r = client.get("/action-items/", params={"limit": 200})
    assert r.status_code == 200
    result = r.json()
    assert len(result) <= 200

    # Test invalid limit (too small)
    r = client.get("/action-items/", params={"limit": 0})
    assert r.status_code == 422

    # Test invalid limit (too large)
    r = client.get("/action-items/", params={"limit": 201})
    assert r.status_code == 422

    # Test invalid skip (negative)
    r = client.get("/action-items/", params={"skip": -1})
    assert r.status_code == 422


def test_action_items_sorting(client):
    """Test sorting functionality for action items."""
    # Create action items with different descriptions
    import time
    
    items = []
    for i in range(5):
        payload = {"description": f"Action {chr(65+i)}"}
        r = client.post("/action-items/", json=payload)
        assert r.status_code == 201
        items.append(r.json())
        time.sleep(0.01)  # Small delay to ensure different timestamps

    # Test default sort (created_at desc)
    r = client.get("/action-items/", params={"limit": 10})
    assert r.status_code == 200
    result = r.json()
    assert len(result) >= 5
    # Should be in descending order (newest first)
    for i in range(len(result) - 1):
        assert result[i]["created_at"] >= result[i + 1]["created_at"]

    # Test ascending sort by created_at
    r = client.get("/action-items/", params={"sort": "created_at", "limit": 10})
    assert r.status_code == 200
    result = r.json()
    assert len(result) >= 5
    # Should be in ascending order (oldest first)
    for i in range(len(result) - 1):
        assert result[i]["created_at"] <= result[i + 1]["created_at"]

    # Test descending sort by created_at (explicit)
    r = client.get("/action-items/", params={"sort": "-created_at", "limit": 10})
    assert r.status_code == 200
    result = r.json()
    assert len(result) >= 5
    # Should be in descending order
    for i in range(len(result) - 1):
        assert result[i]["created_at"] >= result[i + 1]["created_at"]

    # Test sort by description ascending
    r = client.get("/action-items/", params={"sort": "description", "limit": 10})
    assert r.status_code == 200
    result = r.json()
    assert len(result) >= 5
    # Should be in alphabetical order
    for i in range(len(result) - 1):
        assert result[i]["description"].lower() <= result[i + 1]["description"].lower()

    # Test sort by description descending
    r = client.get("/action-items/", params={"sort": "-description", "limit": 10})
    assert r.status_code == 200
    result = r.json()
    assert len(result) >= 5
    # Should be in reverse alphabetical order
    for i in range(len(result) - 1):
        assert result[i]["description"].lower() >= result[i + 1]["description"].lower()

    # Test sort by completed status
    r = client.get("/action-items/", params={"sort": "completed", "limit": 10})
    assert r.status_code == 200
    result = r.json()
    assert len(result) >= 5
    # False should come before True
    for i in range(len(result) - 1):
        assert result[i]["completed"] <= result[i + 1]["completed"]

    # Test invalid sort field (should fallback to default)
    r = client.get("/action-items/", params={"sort": "invalid_field", "limit": 10})
    assert r.status_code == 200
    result = r.json()
    # Should still return results with default sort
    assert len(result) >= 0


def test_action_items_pagination_with_sorting(client):
    """Test pagination combined with sorting."""
    # Create multiple action items
    items = []
    for i in range(10):
        payload = {"description": f"Action {i:02d}"}
        r = client.post("/action-items/", json=payload)
        assert r.status_code == 201
        items.append(r.json())

    # Test first page with sorting
    r = client.get("/action-items/", params={"skip": 0, "limit": 3, "sort": "description"})
    assert r.status_code == 200
    page1 = r.json()
    assert len(page1) == 3

    # Test second page with same sorting
    r = client.get("/action-items/", params={"skip": 3, "limit": 3, "sort": "description"})
    assert r.status_code == 200
    page2 = r.json()
    assert len(page2) == 3

    # Verify pages don't overlap and are correctly sorted
    assert page1[-1]["description"] <= page2[0]["description"]


def test_action_items_pagination_with_filtering(client):
    """Test pagination combined with filtering."""
    # Create action items with different completion statuses
    completed_items = []
    incomplete_items = []
    
    for i in range(5):
        payload = {"description": f"Complete {i}"}
        r = client.post("/action-items/", json=payload)
        assert r.status_code == 201
        item = r.json()
        # Complete some items
        if i % 2 == 0:
            r = client.put(f"/action-items/{item['id']}/complete")
            assert r.status_code == 200
            completed_items.append(r.json())
        else:
            incomplete_items.append(item)

    # Test pagination with completed filter
    r = client.get("/action-items/", params={"completed": True, "skip": 0, "limit": 2})
    assert r.status_code == 200
    items = r.json()
    assert len(items) <= 2
    for item in items:
        assert item["completed"] is True

    # Test pagination with incomplete filter
    r = client.get("/action-items/", params={"completed": False, "skip": 0, "limit": 2})
    assert r.status_code == 200
    items = r.json()
    assert len(items) <= 2
    for item in items:
        assert item["completed"] is False

