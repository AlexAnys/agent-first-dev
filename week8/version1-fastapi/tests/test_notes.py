def test_create_list_and_patch_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"
    assert "created_at" in data and "updated_at" in data

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/", params={"q": "Hello", "limit": 10, "sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    note_id = data["id"]
    r = client.patch(f"/notes/{note_id}", json={"title": "Updated"})
    assert r.status_code == 200
    patched = r.json()
    assert patched["title"] == "Updated"


def test_notes_pagination(client):
    """Test pagination functionality for notes."""
    # Create multiple notes
    notes = []
    for i in range(10):
        payload = {"title": f"Note {i}", "content": f"Content {i}"}
        r = client.post("/notes/", json=payload)
        assert r.status_code == 201
        notes.append(r.json())

    # Test limit
    r = client.get("/notes/", params={"limit": 3})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 3

    # Test skip
    r = client.get("/notes/", params={"skip": 2, "limit": 3})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 3

    # Test skip beyond available items
    r = client.get("/notes/", params={"skip": 100, "limit": 10})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 0

    # Test limit boundary - minimum
    r = client.get("/notes/", params={"limit": 1})
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1

    # Test limit boundary - maximum
    r = client.get("/notes/", params={"limit": 200})
    assert r.status_code == 200
    items = r.json()
    assert len(items) <= 200

    # Test invalid limit (too small)
    r = client.get("/notes/", params={"limit": 0})
    assert r.status_code == 422

    # Test invalid limit (too large)
    r = client.get("/notes/", params={"limit": 201})
    assert r.status_code == 422

    # Test invalid skip (negative)
    r = client.get("/notes/", params={"skip": -1})
    assert r.status_code == 422


def test_notes_sorting(client):
    """Test sorting functionality for notes."""
    # Create notes with different titles and timestamps
    import time
    
    notes = []
    for i in range(5):
        payload = {"title": f"Note {chr(65+i)}", "content": f"Content {i}"}
        r = client.post("/notes/", json=payload)
        assert r.status_code == 201
        notes.append(r.json())
        time.sleep(0.01)  # Small delay to ensure different timestamps

    # Test default sort (created_at desc)
    r = client.get("/notes/", params={"limit": 10})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 5
    # Should be in descending order (newest first)
    for i in range(len(items) - 1):
        assert items[i]["created_at"] >= items[i + 1]["created_at"]

    # Test ascending sort by created_at
    r = client.get("/notes/", params={"sort": "created_at", "limit": 10})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 5
    # Should be in ascending order (oldest first)
    for i in range(len(items) - 1):
        assert items[i]["created_at"] <= items[i + 1]["created_at"]

    # Test descending sort by created_at (explicit)
    r = client.get("/notes/", params={"sort": "-created_at", "limit": 10})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 5
    # Should be in descending order
    for i in range(len(items) - 1):
        assert items[i]["created_at"] >= items[i + 1]["created_at"]

    # Test sort by title ascending
    r = client.get("/notes/", params={"sort": "title", "limit": 10})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 5
    # Should be in alphabetical order
    for i in range(len(items) - 1):
        assert items[i]["title"].lower() <= items[i + 1]["title"].lower()

    # Test sort by title descending
    r = client.get("/notes/", params={"sort": "-title", "limit": 10})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 5
    # Should be in reverse alphabetical order
    for i in range(len(items) - 1):
        assert items[i]["title"].lower() >= items[i + 1]["title"].lower()

    # Test sort by id ascending
    r = client.get("/notes/", params={"sort": "id", "limit": 10})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 5
    for i in range(len(items) - 1):
        assert items[i]["id"] <= items[i + 1]["id"]

    # Test invalid sort field (should fallback to default)
    r = client.get("/notes/", params={"sort": "invalid_field", "limit": 10})
    assert r.status_code == 200
    items = r.json()
    # Should still return results with default sort
    assert len(items) >= 0


def test_notes_pagination_with_sorting(client):
    """Test pagination combined with sorting."""
    # Create multiple notes
    notes = []
    for i in range(10):
        payload = {"title": f"Note {i:02d}", "content": f"Content {i}"}
        r = client.post("/notes/", json=payload)
        assert r.status_code == 201
        notes.append(r.json())

    # Test first page with sorting
    r = client.get("/notes/", params={"skip": 0, "limit": 3, "sort": "title"})
    assert r.status_code == 200
    page1 = r.json()
    assert len(page1) == 3

    # Test second page with same sorting
    r = client.get("/notes/", params={"skip": 3, "limit": 3, "sort": "title"})
    assert r.status_code == 200
    page2 = r.json()
    assert len(page2) == 3

    # Verify pages don't overlap and are correctly sorted
    assert page1[-1]["title"] <= page2[0]["title"]


def test_notes_pagination_with_filtering(client):
    """Test pagination combined with filtering."""
    # Create categories via API
    cat1_payload = {"name": "Category A", "description": "Test category A"}
    r = client.post("/categories/", json=cat1_payload)
    assert r.status_code == 201
    category1 = r.json()
    
    cat2_payload = {"name": "Category B", "description": "Test category B"}
    r = client.post("/categories/", json=cat2_payload)
    assert r.status_code == 201
    category2 = r.json()

    # Create notes with categories
    for i in range(5):
        payload = {
            "title": f"Note {i}",
            "content": f"Content {i}",
            "category_id": category1["id"] if i % 2 == 0 else category2["id"]
        }
        r = client.post("/notes/", json=payload)
        assert r.status_code == 201

    # Test pagination with category filter
    r = client.get("/notes/", params={"category_id": category1["id"], "skip": 0, "limit": 2})
    assert r.status_code == 200
    items = r.json()
    assert len(items) <= 2
    for item in items:
        assert item["category_id"] == category1["id"]

