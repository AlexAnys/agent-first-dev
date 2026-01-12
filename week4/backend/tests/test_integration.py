"""Integration tests for full CRUD lifecycle scenarios."""

from fastapi.testclient import TestClient


class TestNotesCRUDLifecycle:
    """Integration tests for complete Note CRUD lifecycle."""

    def test_full_note_lifecycle(self, client: TestClient):
        """Test complete CRUD lifecycle for notes: Create -> Read -> Update -> Delete."""
        # CREATE: Create a new note
        create_payload = {"title": "My First Note", "content": "This is the initial content"}
        create_response = client.post("/notes/", json=create_payload)
        assert create_response.status_code == 201
        created_note = create_response.json()
        note_id = created_note["id"]
        assert created_note["title"] == "My First Note"
        assert created_note["content"] == "This is the initial content"

        # READ: Retrieve the created note by ID
        get_response = client.get(f"/notes/{note_id}")
        assert get_response.status_code == 200
        retrieved_note = get_response.json()
        assert retrieved_note["id"] == note_id
        assert retrieved_note["title"] == "My First Note"

        # READ: Verify note appears in list
        list_response = client.get("/notes/")
        assert list_response.status_code == 200
        notes_list = list_response.json()
        assert any(note["id"] == note_id for note in notes_list)

        # READ: Verify note appears in search
        search_response = client.get("/notes/search/", params={"search_query": "First"})
        assert search_response.status_code == 200
        search_results = search_response.json()
        assert any(note["id"] == note_id for note in search_results)

        # UPDATE: Update the note (full update)
        update_payload = {"title": "Updated Title", "content": "Updated content"}
        update_response = client.put(f"/notes/{note_id}", json=update_payload)
        assert update_response.status_code == 200
        updated_note = update_response.json()
        assert updated_note["id"] == note_id
        assert updated_note["title"] == "Updated Title"
        assert updated_note["content"] == "Updated content"

        # UPDATE: Partial update (only title)
        partial_update_payload = {"title": "Partially Updated"}
        partial_response = client.put(f"/notes/{note_id}", json=partial_update_payload)
        assert partial_response.status_code == 200
        partially_updated = partial_response.json()
        assert partially_updated["title"] == "Partially Updated"
        assert partially_updated["content"] == "Updated content"

        # DELETE: Delete the note
        delete_response = client.delete(f"/notes/{note_id}")
        assert delete_response.status_code == 204

        # VERIFY DELETION: Attempting to retrieve deleted note returns 404
        get_deleted_response = client.get(f"/notes/{note_id}")
        assert get_deleted_response.status_code == 404

        # VERIFY DELETION: Note no longer appears in list
        final_list_response = client.get("/notes/")
        final_notes_list = final_list_response.json()
        assert not any(note["id"] == note_id for note in final_notes_list)

    def test_multiple_notes_with_pagination(self, client: TestClient):
        """Test creating multiple notes and using pagination."""
        # Create 15 notes
        note_ids = []
        for i in range(15):
            payload = {"title": f"Note {i}", "content": f"Content for note {i}"}
            response = client.post("/notes/", json=payload)
            assert response.status_code == 201
            note_ids.append(response.json()["id"])

        # Test pagination - first page
        page1_response = client.get("/notes/", params={"skip": 0, "limit": 10})
        assert page1_response.status_code == 200
        page1_notes = page1_response.json()
        assert len(page1_notes) == 10

        # Test pagination - second page
        page2_response = client.get("/notes/", params={"skip": 10, "limit": 10})
        assert page2_response.status_code == 200
        page2_notes = page2_response.json()
        assert len(page2_notes) == 5

        # Test search with pagination
        search_response = client.get(
            "/notes/search/", params={"search_query": "Note", "skip": 5, "limit": 5}
        )
        assert search_response.status_code == 200
        search_results = search_response.json()
        assert len(search_results) == 5

    def test_notes_search_lifecycle(self, client: TestClient):
        """Test creating notes and searching with various queries."""
        # Create notes with different content
        client.post("/notes/", json={"title": "Python Tutorial", "content": "Learn Python basics"})
        client.post("/notes/", json={"title": "JavaScript Guide", "content": "Learn JavaScript"})
        client.post(
            "/notes/", json={"title": "Python Advanced", "content": "Advanced Python concepts"}
        )
        client.post("/notes/", json={"title": "Java Basics", "content": "Introduction to Java"})

        # Search by title keyword
        python_search = client.get("/notes/search/", params={"search_query": "Python"})
        assert python_search.status_code == 200
        python_results = python_search.json()
        assert len(python_results) == 2
        assert all("Python" in note["title"] for note in python_results)

        # Search by content keyword
        learn_search = client.get("/notes/search/", params={"search_query": "Learn"})
        assert learn_search.status_code == 200
        learn_results = learn_search.json()
        assert len(learn_results) == 2

        # Search with no results
        no_results_search = client.get(
            "/notes/search/", params={"search_query": "NonExistentKeyword"}
        )
        assert no_results_search.status_code == 200
        assert no_results_search.json() == []


class TestActionItemsCRUDLifecycle:
    """Integration tests for complete ActionItem CRUD lifecycle."""

    def test_full_action_item_lifecycle(self, client: TestClient):
        """Test complete CRUD lifecycle for action items."""
        # CREATE: Create a new action item
        create_payload = {"description": "Complete project documentation"}
        create_response = client.post("/action-items/", json=create_payload)
        assert create_response.status_code == 201
        created_item = create_response.json()
        item_id = created_item["id"]
        assert created_item["description"] == "Complete project documentation"
        assert created_item["completed"] is False

        # READ: Retrieve the created action item by ID
        get_response = client.get(f"/action-items/{item_id}")
        assert get_response.status_code == 200
        retrieved_item = get_response.json()
        assert retrieved_item["id"] == item_id
        assert retrieved_item["description"] == "Complete project documentation"

        # READ: Verify item appears in list
        list_response = client.get("/action-items/")
        assert list_response.status_code == 200
        items_list = list_response.json()
        assert any(item["id"] == item_id for item in items_list)

        # UPDATE: Update the action item (description)
        update_payload = {"description": "Complete project documentation and tests"}
        update_response = client.put(f"/action-items/{item_id}", json=update_payload)
        assert update_response.status_code == 200
        updated_item = update_response.json()
        assert updated_item["description"] == "Complete project documentation and tests"
        assert updated_item["completed"] is False

        # UPDATE: Mark as completed using the complete endpoint
        complete_response = client.put(f"/action-items/{item_id}/complete")
        assert complete_response.status_code == 200
        completed_item = complete_response.json()
        assert completed_item["completed"] is True

        # UPDATE: Update using PUT with completed status
        reopen_payload = {"completed": False}
        reopen_response = client.put(f"/action-items/{item_id}", json=reopen_payload)
        assert reopen_response.status_code == 200
        reopened_item = reopen_response.json()
        assert reopened_item["completed"] is False

        # DELETE: Delete the action item
        delete_response = client.delete(f"/action-items/{item_id}")
        assert delete_response.status_code == 204

        # VERIFY DELETION: Attempting to retrieve deleted item returns 404
        get_deleted_response = client.get(f"/action-items/{item_id}")
        assert get_deleted_response.status_code == 404

    def test_action_items_status_filtering(self, client: TestClient):
        """Test creating action items and filtering by status."""
        # Create multiple action items
        item1_response = client.post("/action-items/", json={"description": "Task 1"})
        item2_response = client.post("/action-items/", json={"description": "Task 2"})
        client.post("/action-items/", json={"description": "Task 3"})
        client.post("/action-items/", json={"description": "Task 4"})

        item1_id = item1_response.json()["id"]
        item2_id = item2_response.json()["id"]

        # Mark some as completed
        client.put(f"/action-items/{item1_id}/complete")
        client.put(f"/action-items/{item2_id}/complete")

        # Filter for pending items
        pending_response = client.get("/action-items/", params={"status": "pending"})
        assert pending_response.status_code == 200
        pending_items = pending_response.json()
        assert len(pending_items) == 2
        assert all(not item["completed"] for item in pending_items)

        # Filter for completed items
        completed_response = client.get("/action-items/", params={"status": "completed"})
        assert completed_response.status_code == 200
        completed_items = completed_response.json()
        assert len(completed_items) == 2
        assert all(item["completed"] for item in completed_items)

        # Get all items (no filter)
        all_response = client.get("/action-items/")
        assert all_response.status_code == 200
        all_items = all_response.json()
        assert len(all_items) == 4

    def test_multiple_action_items_with_pagination(self, client: TestClient):
        """Test creating multiple action items and using pagination."""
        # Create 20 action items
        item_ids = []
        for i in range(20):
            payload = {"description": f"Task {i}"}
            response = client.post("/action-items/", json=payload)
            assert response.status_code == 201
            item_ids.append(response.json()["id"])

        # Mark every other item as completed
        for i in range(0, 20, 2):
            client.put(f"/action-items/{item_ids[i]}/complete")

        # Test pagination with status filter - pending items
        pending_page1 = client.get(
            "/action-items/", params={"status": "pending", "skip": 0, "limit": 5}
        )
        assert pending_page1.status_code == 200
        assert len(pending_page1.json()) == 5

        # Test pagination with status filter - completed items
        completed_page1 = client.get(
            "/action-items/", params={"status": "completed", "skip": 0, "limit": 5}
        )
        assert completed_page1.status_code == 200
        assert len(completed_page1.json()) == 5


class TestCrossResourceIntegration:
    """Integration tests involving both Notes and Action Items."""

    def test_creating_and_managing_both_resources(self, client: TestClient):
        """Test creating and managing both notes and action items in a workflow."""
        # Create a note
        note_response = client.post(
            "/notes/",
            json={"title": "Project Plan", "content": "TODO: Create tasks\nShip it!"},
        )
        assert note_response.status_code == 201
        note_id = note_response.json()["id"]

        # Create related action items
        task1 = client.post("/action-items/", json={"description": "Create tasks"})
        task2 = client.post("/action-items/", json={"description": "Ship it!"})
        assert task1.status_code == 201
        assert task2.status_code == 201
        task1_id = task1.json()["id"]

        # Complete first task
        client.put(f"/action-items/{task1_id}/complete")

        # Update note to reflect progress
        client.put(f"/notes/{note_id}", json={"content": "Task 1 done! Ship it!"})

        # Verify states
        updated_note = client.get(f"/notes/{note_id}").json()
        assert "Task 1 done" in updated_note["content"]

        completed_tasks = client.get("/action-items/", params={"status": "completed"}).json()
        assert len(completed_tasks) == 1

        pending_tasks = client.get("/action-items/", params={"status": "pending"}).json()
        assert len(pending_tasks) == 1

    def test_bulk_operations_on_multiple_resources(self, client: TestClient):
        """Test bulk creation and cleanup of both resource types."""
        # Bulk create notes
        note_ids = []
        for i in range(5):
            response = client.post("/notes/", json={"title": f"Note {i}", "content": f"C{i}"})
            note_ids.append(response.json()["id"])

        # Bulk create action items
        item_ids = []
        for i in range(5):
            response = client.post("/action-items/", json={"description": f"Task {i}"})
            item_ids.append(response.json()["id"])

        # Verify counts
        assert len(client.get("/notes/").json()) == 5
        assert len(client.get("/action-items/").json()) == 5

        # Bulk delete notes
        for note_id in note_ids:
            response = client.delete(f"/notes/{note_id}")
            assert response.status_code == 204

        # Bulk delete action items
        for item_id in item_ids:
            response = client.delete(f"/action-items/{item_id}")
            assert response.status_code == 204

        # Verify all deleted
        assert len(client.get("/notes/").json()) == 0
        assert len(client.get("/action-items/").json()) == 0
