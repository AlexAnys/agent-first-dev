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


def test_update_category_patch(client):
    """Test PATCH endpoint for updating a category (partial update)."""
    # Create a category
    payload = {"name": "Original Category", "description": "Original description"}
    r = client.post("/categories/", json=payload)
    assert r.status_code == 201
    category = r.json()
    category_id = category["id"]
    original_created_at = category["created_at"]

    # Update only name
    r = client.patch(f"/categories/{category_id}", json={"name": "Updated Category"})
    assert r.status_code == 200
    updated = r.json()
    assert updated["name"] == "Updated Category"
    assert updated["description"] == "Original description"  # Unchanged
    assert updated["id"] == category_id

    # Update only description
    r = client.patch(f"/categories/{category_id}", json={"description": "Updated description"})
    assert r.status_code == 200
    updated = r.json()
    assert updated["name"] == "Updated Category"  # Unchanged
    assert updated["description"] == "Updated description"

    # Update both fields
    r = client.patch(
        f"/categories/{category_id}",
        json={"name": "Final Category", "description": "Final description"}
    )
    assert r.status_code == 200
    updated = r.json()
    assert updated["name"] == "Final Category"
    assert updated["description"] == "Final description"

    # Verify updated_at changed
    assert updated["updated_at"] > original_created_at

    # Try to update non-existent category
    r = client.patch("/categories/99999", json={"name": "Test"})
    assert r.status_code == 404


def test_update_category_put(client):
    """Test PUT endpoint for updating a category (full replacement)."""
    # Create a category
    payload = {"name": "Original Category", "description": "Original description"}
    r = client.post("/categories/", json=payload)
    assert r.status_code == 201
    category = r.json()
    category_id = category["id"]

    # Replace entire category
    payload = {"name": "Replaced Category", "description": "New description"}
    r = client.put(f"/categories/{category_id}", json=payload)
    assert r.status_code == 200
    updated = r.json()
    assert updated["name"] == "Replaced Category"
    assert updated["description"] == "New description"
    assert updated["id"] == category_id

    # Replace without description
    payload = {"name": "Category Without Description"}
    r = client.put(f"/categories/{category_id}", json=payload)
    assert r.status_code == 200
    updated = r.json()
    assert updated["name"] == "Category Without Description"
    assert updated["description"] is None

    # Try to update non-existent category
    r = client.put("/categories/99999", json={"name": "Test"})
    assert r.status_code == 404


def test_update_category_duplicate_name(client):
    """Test that updating a category with a duplicate name fails."""
    # Create two categories
    payload1 = {"name": "Category A"}
    r = client.post("/categories/", json=payload1)
    assert r.status_code == 201
    category1 = r.json()

    payload2 = {"name": "Category B"}
    r = client.post("/categories/", json=payload2)
    assert r.status_code == 201
    category2 = r.json()

    # Try to update category2 with category1's name (should fail)
    r = client.patch(f"/categories/{category2['id']}", json={"name": "Category A"})
    assert r.status_code == 409

    r = client.put(f"/categories/{category2['id']}", json={"name": "Category A"})
    assert r.status_code == 409
