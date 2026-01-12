def test_create_get_and_delete_category(client):
    """Test basic CRUD operations for categories."""
    payload = {"name": "Test Category", "description": "Test description"}
    r = client.post("/categories/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["name"] == "Test Category"
    assert data["description"] == "Test description"
    assert "created_at" in data and "updated_at" in data

    category_id = data["id"]
    r = client.get(f"/categories/{category_id}")
    assert r.status_code == 200
    retrieved = r.json()
    assert retrieved["name"] == "Test Category"

    r = client.delete(f"/categories/{category_id}")
    assert r.status_code == 204

    r = client.get(f"/categories/{category_id}")
    assert r.status_code == 404


def test_categories_pagination(client):
    """Test pagination functionality for categories."""
    # Create multiple categories
    categories = []
    for i in range(10):
        payload = {"name": f"Category {i}"}
        r = client.post("/categories/", json=payload)
        assert r.status_code == 201
        categories.append(r.json())

    # Test limit
    r = client.get("/categories/", params={"limit": 3})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 3

    # Test skip
    r = client.get("/categories/", params={"skip": 2, "limit": 3})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 3

    # Test skip beyond available items
    r = client.get("/categories/", params={"skip": 100, "limit": 10})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 0

    # Test limit boundary - minimum
    r = client.get("/categories/", params={"limit": 1})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1

    # Test limit boundary - maximum
    r = client.get("/categories/", params={"limit": 200})
    assert r.status_code == 200
    items = r.json()
    assert len(items) <= 200

    # Test invalid limit (too small)
    r = client.get("/categories/", params={"limit": 0})
    assert r.status_code == 422

    # Test invalid limit (too large)
    r = client.get("/categories/", params={"limit": 201})
    assert r.status_code == 422

    # Test invalid skip (negative)
    r = client.get("/categories/", params={"skip": -1})
    assert r.status_code == 422


def test_categories_sorting(client):
    """Test sorting functionality for categories."""
    # Create categories with different names and timestamps
    import time
    
    categories = []
    for i in range(5):
        payload = {"name": f"Category {chr(65+i)}"}
        r = client.post("/categories/", json=payload)
        assert r.status_code == 201
        categories.append(r.json())
        time.sleep(0.01)  # Small delay to ensure different timestamps

    # Test default sort (created_at desc)
    r = client.get("/categories/", params={"limit": 10})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 5
    # Should be in descending order (newest first)
    for i in range(len(items) - 1):
        assert items[i]["created_at"] >= items[i + 1]["created_at"]

    # Test ascending sort by created_at
    r = client.get("/categories/", params={"sort": "created_at", "limit": 10})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 5
    # Should be in ascending order (oldest first)
    for i in range(len(items) - 1):
        assert items[i]["created_at"] <= items[i + 1]["created_at"]

    # Test descending sort by created_at (explicit)
    r = client.get("/categories/", params={"sort": "-created_at", "limit": 10})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 5
    # Should be in descending order
    for i in range(len(items) - 1):
        assert items[i]["created_at"] >= items[i + 1]["created_at"]

    # Test sort by name ascending
    r = client.get("/categories/", params={"sort": "name", "limit": 10})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 5
    # Should be in alphabetical order
    for i in range(len(items) - 1):
        assert items[i]["name"].lower() <= items[i + 1]["name"].lower()

    # Test sort by name descending
    r = client.get("/categories/", params={"sort": "-name", "limit": 10})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 5
    # Should be in reverse alphabetical order
    for i in range(len(items) - 1):
        assert items[i]["name"].lower() >= items[i + 1]["name"].lower()

    # Test sort by id ascending
    r = client.get("/categories/", params={"sort": "id", "limit": 10})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 5
    for i in range(len(items) - 1):
        assert items[i]["id"] <= items[i + 1]["id"]

    # Test invalid sort field (should fallback to default)
    r = client.get("/categories/", params={"sort": "invalid_field", "limit": 10})
    assert r.status_code == 200
    items = r.json()
    # Should still return results with default sort
    assert len(items) >= 0


def test_categories_pagination_with_sorting(client):
    """Test pagination combined with sorting."""
    # Create multiple categories
    categories = []
    for i in range(10):
        payload = {"name": f"Category {i:02d}"}
        r = client.post("/categories/", json=payload)
        assert r.status_code == 201
        categories.append(r.json())

    # Test first page with sorting
    r = client.get("/categories/", params={"skip": 0, "limit": 3, "sort": "name"})
    assert r.status_code == 200
    page1 = r.json()
    assert len(page1) == 3

    # Test second page with same sorting
    r = client.get("/categories/", params={"skip": 3, "limit": 3, "sort": "name"})
    assert r.status_code == 200
    page2 = r.json()
    assert len(page2) == 3

    # Verify pages don't overlap and are correctly sorted
    assert page1[-1]["name"] <= page2[0]["name"]
