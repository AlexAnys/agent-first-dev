"""Edge case tests for API endpoints."""

from backend.app.constants import MAX_TITLE_LENGTH
from fastapi.testclient import TestClient


class TestNoteEdgeCases:
    """Edge case tests for Note endpoints."""

    def test_create_note_with_empty_title(self, client: TestClient):
        """Test creating a note with empty title fails validation."""
        payload = {"title": "", "content": "Valid content"}
        response = client.post("/notes/", json=payload)
        assert response.status_code == 422
        error_detail = response.json()["detail"][0]
        assert "title" in error_detail["loc"]
        assert "empty" in error_detail["msg"].lower()

    def test_create_note_with_whitespace_only_title(self, client: TestClient):
        """Test creating a note with whitespace-only title fails."""
        payload = {"title": "   ", "content": "Valid content"}
        response = client.post("/notes/", json=payload)
        assert response.status_code == 422

    def test_create_note_with_empty_content(self, client: TestClient):
        """Test creating a note with empty content fails validation."""
        payload = {"title": "Valid title", "content": ""}
        response = client.post("/notes/", json=payload)
        assert response.status_code == 422
        error_detail = response.json()["detail"][0]
        assert "content" in error_detail["loc"]

    def test_create_note_with_whitespace_only_content(self, client: TestClient):
        """Test creating a note with whitespace-only content fails."""
        payload = {"title": "Valid title", "content": "   "}
        response = client.post("/notes/", json=payload)
        assert response.status_code == 422

    def test_create_note_with_very_long_title(self, client: TestClient):
        """Test creating a note with title exceeding max length fails."""
        long_title = "a" * (MAX_TITLE_LENGTH + 1)
        payload = {"title": long_title, "content": "Valid content"}
        response = client.post("/notes/", json=payload)
        assert response.status_code == 422
        error_detail = response.json()["detail"][0]
        assert "title" in error_detail["loc"]

    def test_create_note_with_max_length_title(self, client: TestClient):
        """Test creating a note with max length title succeeds."""
        max_length_title = "a" * MAX_TITLE_LENGTH
        payload = {"title": max_length_title, "content": "Valid content"}
        response = client.post("/notes/", json=payload)
        assert response.status_code == 201
        assert response.json()["title"] == max_length_title

    def test_create_note_with_special_characters(self, client: TestClient):
        """Test creating a note with special characters in title and content."""
        payload = {
            "title": "Special chars: @#$%^&*()[]{}|<>?",
            "content": "Unicode: 你好 🚀 émoji",
        }
        response = client.post("/notes/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == payload["title"]
        assert data["content"] == payload["content"]

    def test_create_note_trims_whitespace(self, client: TestClient):
        """Test that leading/trailing whitespace is trimmed."""
        payload = {"title": "  Title with spaces  ", "content": "  Content with spaces  "}
        response = client.post("/notes/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Title with spaces"
        assert data["content"] == "Content with spaces"

    def test_get_note_not_found(self, client: TestClient):
        """Test retrieving a non-existent note returns 404."""
        response = client.get("/notes/99999")
        assert response.status_code == 404
        assert "Note" in response.json()["detail"]

    def test_update_note_not_found(self, client: TestClient):
        """Test updating a non-existent note returns 404."""
        payload = {"title": "Updated", "content": "Updated content"}
        response = client.put("/notes/99999", json=payload)
        assert response.status_code == 404

    def test_update_note_with_empty_title(self, client: TestClient):
        """Test updating a note with empty title fails."""
        create_payload = {"title": "Original", "content": "Original content"}
        create_response = client.post("/notes/", json=create_payload)
        note_id = create_response.json()["id"]

        update_payload = {"title": ""}
        response = client.put(f"/notes/{note_id}", json=update_payload)
        assert response.status_code == 422

    def test_update_note_with_no_fields(self, client: TestClient):
        """Test updating a note with no fields returns original note."""
        create_payload = {"title": "Original", "content": "Original content"}
        create_response = client.post("/notes/", json=create_payload)
        note_id = create_response.json()["id"]

        update_payload = {}
        response = client.put(f"/notes/{note_id}", json=update_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Original"
        assert data["content"] == "Original content"

    def test_delete_note_not_found(self, client: TestClient):
        """Test deleting a non-existent note returns 404."""
        response = client.delete("/notes/99999")
        assert response.status_code == 404

    def test_search_notes_with_very_long_query(self, client: TestClient):
        """Test searching with a very long query string."""
        long_query = "a" * 1000
        response = client.get("/notes/search/", params={"search_query": long_query})
        assert response.status_code == 200
        assert response.json() == []

    def test_pagination_with_negative_skip(self, client: TestClient):
        """Test pagination with negative skip fails validation."""
        response = client.get("/notes/", params={"skip": -1, "limit": 10})
        assert response.status_code == 422

    def test_pagination_with_zero_limit(self, client: TestClient):
        """Test pagination with zero limit fails validation."""
        response = client.get("/notes/", params={"skip": 0, "limit": 0})
        assert response.status_code == 422

    def test_pagination_with_excessive_limit(self, client: TestClient):
        """Test pagination with limit exceeding max fails validation."""
        response = client.get("/notes/", params={"skip": 0, "limit": 10000})
        assert response.status_code == 422


class TestActionItemEdgeCases:
    """Edge case tests for ActionItem endpoints."""

    def test_create_action_item_with_empty_description(self, client: TestClient):
        """Test creating an action item with empty description fails."""
        payload = {"description": ""}
        response = client.post("/action-items/", json=payload)
        assert response.status_code == 422
        error_detail = response.json()["detail"][0]
        assert "description" in error_detail["loc"]

    def test_create_action_item_with_whitespace_only_description(self, client: TestClient):
        """Test creating an action item with whitespace-only description fails."""
        payload = {"description": "   "}
        response = client.post("/action-items/", json=payload)
        assert response.status_code == 422

    def test_create_action_item_with_special_characters(self, client: TestClient):
        """Test creating an action item with special characters."""
        payload = {"description": "Special task: @#$% 你好 🎯"}
        response = client.post("/action-items/", json=payload)
        assert response.status_code == 201
        assert response.json()["description"] == payload["description"]

    def test_create_action_item_trims_whitespace(self, client: TestClient):
        """Test that leading/trailing whitespace is trimmed."""
        payload = {"description": "  Task with spaces  "}
        response = client.post("/action-items/", json=payload)
        assert response.status_code == 201
        assert response.json()["description"] == "Task with spaces"

    def test_get_action_item_not_found(self, client: TestClient):
        """Test retrieving a non-existent action item returns 404."""
        response = client.get("/action-items/99999")
        assert response.status_code == 404
        assert "Action item" in response.json()["detail"]

    def test_update_action_item_not_found(self, client: TestClient):
        """Test updating a non-existent action item returns 404."""
        payload = {"description": "Updated"}
        response = client.put("/action-items/99999", json=payload)
        assert response.status_code == 404

    def test_update_action_item_with_empty_description(self, client: TestClient):
        """Test updating an action item with empty description fails."""
        create_payload = {"description": "Original task"}
        create_response = client.post("/action-items/", json=create_payload)
        item_id = create_response.json()["id"]

        update_payload = {"description": ""}
        response = client.put(f"/action-items/{item_id}", json=update_payload)
        assert response.status_code == 422

    def test_update_action_item_with_no_fields(self, client: TestClient):
        """Test updating an action item with no fields returns original."""
        create_payload = {"description": "Original task"}
        create_response = client.post("/action-items/", json=create_payload)
        item_id = create_response.json()["id"]

        update_payload = {}
        response = client.put(f"/action-items/{item_id}", json=update_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Original task"
        assert data["completed"] is False

    def test_delete_action_item_not_found(self, client: TestClient):
        """Test deleting a non-existent action item returns 404."""
        response = client.delete("/action-items/99999")
        assert response.status_code == 404

    def test_complete_action_item_not_found(self, client: TestClient):
        """Test completing a non-existent action item returns 404."""
        response = client.put("/action-items/99999/complete")
        assert response.status_code == 404

    def test_filter_action_items_with_invalid_status(self, client: TestClient):
        """Test filtering with invalid status still works (returns all)."""
        client.post("/action-items/", json={"description": "Task 1"})
        client.post("/action-items/", json={"description": "Task 2"})

        response = client.get("/action-items/", params={"status": "invalid"})
        assert response.status_code == 200
        items = response.json()
        assert len(items) == 2

    def test_pagination_with_negative_skip_action_items(self, client: TestClient):
        """Test pagination with negative skip fails validation."""
        response = client.get("/action-items/", params={"skip": -1, "limit": 10})
        assert response.status_code == 422

    def test_pagination_with_zero_limit_action_items(self, client: TestClient):
        """Test pagination with zero limit fails validation."""
        response = client.get("/action-items/", params={"skip": 0, "limit": 0})
        assert response.status_code == 422

    def test_pagination_with_excessive_limit_action_items(self, client: TestClient):
        """Test pagination with limit exceeding max fails validation."""
        response = client.get("/action-items/", params={"skip": 0, "limit": 10000})
        assert response.status_code == 422
