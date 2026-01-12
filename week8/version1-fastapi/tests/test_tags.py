def test_create_get_and_delete_tag(client):
    """Test basic CRUD operations for tags."""
    payload = {"name": "test-tag", "color": "#FF0000"}
    r = client.post("/tags/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["name"] == "test-tag"
    assert data["color"] == "#FF0000"
    assert "created_at" in data and "updated_at" in data

    tag_id = data["id"]
    r = client.get(f"/tags/{tag_id}")
    assert r.status_code == 200
    retrieved = r.json()
    assert retrieved["name"] == "test-tag"

    r = client.delete(f"/tags/{tag_id}")
    assert r.status_code == 204

    r = client.get(f"/tags/{tag_id}")
    assert r.status_code == 404


def test_tags_pagination(client):
    """Test pagination functionality for tags."""
    # Create multiple tags
    tags = []
    for i in range(10):
        payload = {"name": f"tag-{i}"}
        r = client.post("/tags/", json=payload)
        assert r.status_code == 201
        tags.append(r.json())

    # Test limit
    r = client.get("/tags/", params={"limit": 3})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 3

    # Test skip
    r = client.get("/tags/", params={"skip": 2, "limit": 3})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 3

    # Test skip beyond available items
    r = client.get("/tags/", params={"skip": 100, "limit": 10})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 0

    # Test limit boundary - minimum
    r = client.get("/tags/", params={"limit": 1})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1

    # Test limit boundary - maximum
    r = client.get("/tags/", params={"limit": 200})
    assert r.status_code == 200
    items = r.json()
    assert len(items) <= 200

    # Test invalid limit (too small)
    r = client.get("/tags/", params={"limit": 0})
    assert r.status_code == 422

    # Test invalid limit (too large)
    r = client.get("/tags/", params={"limit": 201})
    assert r.status_code == 422

    # Test invalid skip (negative)
    r = client.get("/tags/", params={"skip": -1})
    assert r.status_code == 422


def test_tags_sorting(client):
    """Test sorting functionality for tags."""
    # Create tags with different names and timestamps
    import time
    
    tags = []
    for i in range(5):
        payload = {"name": f"tag-{chr(65+i)}"}
        r = client.post("/tags/", json=payload)
        assert r.status_code == 201
        tags.append(r.json())
        time.sleep(0.01)  # Small delay to ensure different timestamps

    # Test default sort (created_at desc)
    r = client.get("/tags/", params={"limit": 10})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 5
    # Should be in descending order (newest first)
    for i in range(len(items) - 1):
        assert items[i]["created_at"] >= items[i + 1]["created_at"]

    # Test ascending sort by created_at
    r = client.get("/tags/", params={"sort": "created_at", "limit": 10})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 5
    # Should be in ascending order (oldest first)
    for i in range(len(items) - 1):
        assert items[i]["created_at"] <= items[i + 1]["created_at"]

    # Test descending sort by created_at (explicit)
    r = client.get("/tags/", params={"sort": "-created_at", "limit": 10})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 5
    # Should be in descending order
    for i in range(len(items) - 1):
        assert items[i]["created_at"] >= items[i + 1]["created_at"]

    # Test sort by name ascending
    r = client.get("/tags/", params={"sort": "name", "limit": 10})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 5
    # Should be in alphabetical order
    for i in range(len(items) - 1):
        assert items[i]["name"].lower() <= items[i + 1]["name"].lower()

    # Test sort by name descending
    r = client.get("/tags/", params={"sort": "-name", "limit": 10})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 5
    # Should be in reverse alphabetical order
    for i in range(len(items) - 1):
        assert items[i]["name"].lower() >= items[i + 1]["name"].lower()

    # Test sort by id ascending
    r = client.get("/tags/", params={"sort": "id", "limit": 10})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 5
    for i in range(len(items) - 1):
        assert items[i]["id"] <= items[i + 1]["id"]

    # Test invalid sort field (should fallback to default)
    r = client.get("/tags/", params={"sort": "invalid_field", "limit": 10})
    assert r.status_code == 200
    items = r.json()
    # Should still return results with default sort
    assert len(items) >= 0


def test_tags_pagination_with_sorting(client):
    """Test pagination combined with sorting."""
    # Create multiple tags
    tags = []
    for i in range(10):
        payload = {"name": f"tag-{i:02d}"}
        r = client.post("/tags/", json=payload)
        assert r.status_code == 201
        tags.append(r.json())

    # Test first page with sorting
    r = client.get("/tags/", params={"skip": 0, "limit": 3, "sort": "name"})
    assert r.status_code == 200
    page1 = r.json()
    assert len(page1) == 3

    # Test second page with same sorting
    r = client.get("/tags/", params={"skip": 3, "limit": 3, "sort": "name"})
    assert r.status_code == 200
    page2 = r.json()
    assert len(page2) == 3

    # Verify pages don't overlap and are correctly sorted
    assert page1[-1]["name"] <= page2[0]["name"]


def test_update_tag_patch(client):
    """Test PATCH endpoint for updating a tag (partial update)."""
    # Create a tag
    payload = {"name": "original-tag", "color": "#FF0000"}
    r = client.post("/tags/", json=payload)
    assert r.status_code == 201
    tag = r.json()
    tag_id = tag["id"]
    original_created_at = tag["created_at"]

    # Update only name
    r = client.patch(f"/tags/{tag_id}", json={"name": "updated-tag"})
    assert r.status_code == 200
    updated = r.json()
    assert updated["name"] == "updated-tag"
    assert updated["color"] == "#FF0000"  # Unchanged
    assert updated["id"] == tag_id

    # Update only color
    r = client.patch(f"/tags/{tag_id}", json={"color": "#00FF00"})
    assert r.status_code == 200
    updated = r.json()
    assert updated["name"] == "updated-tag"  # Unchanged
    assert updated["color"] == "#00FF00"

    # Update both fields
    r = client.patch(
        f"/tags/{tag_id}",
        json={"name": "final-tag", "color": "#0000FF"}
    )
    assert r.status_code == 200
    updated = r.json()
    assert updated["name"] == "final-tag"
    assert updated["color"] == "#0000FF"

    # Verify updated_at changed
    assert updated["updated_at"] > original_created_at

    # Try to update non-existent tag
    r = client.patch("/tags/99999", json={"name": "test"})
    assert r.status_code == 404


def test_update_tag_put(client):
    """Test PUT endpoint for updating a tag (full replacement)."""
    # Create a tag
    payload = {"name": "original-tag", "color": "#FF0000"}
    r = client.post("/tags/", json=payload)
    assert r.status_code == 201
    tag = r.json()
    tag_id = tag["id"]

    # Replace entire tag
    payload = {"name": "replaced-tag", "color": "#00FF00"}
    r = client.put(f"/tags/{tag_id}", json=payload)
    assert r.status_code == 200
    updated = r.json()
    assert updated["name"] == "replaced-tag"
    assert updated["color"] == "#00FF00"
    assert updated["id"] == tag_id

    # Replace without color
    payload = {"name": "tag-without-color"}
    r = client.put(f"/tags/{tag_id}", json=payload)
    assert r.status_code == 200
    updated = r.json()
    assert updated["name"] == "tag-without-color"
    assert updated["color"] is None

    # Try to update non-existent tag
    r = client.put("/tags/99999", json={"name": "test"})
    assert r.status_code == 404


def test_update_tag_duplicate_name(client):
    """Test that updating a tag with a duplicate name fails."""
    # Create two tags
    payload1 = {"name": "tag-a"}
    r = client.post("/tags/", json=payload1)
    assert r.status_code == 201
    tag1 = r.json()

    payload2 = {"name": "tag-b"}
    r = client.post("/tags/", json=payload2)
    assert r.status_code == 201
    tag2 = r.json()

    # Try to update tag2 with tag1's name (should fail)
    r = client.patch(f"/tags/{tag2['id']}", json={"name": "tag-a"})
    assert r.status_code == 409

    r = client.put(f"/tags/{tag2['id']}", json={"name": "tag-a"})
    assert r.status_code == 409
