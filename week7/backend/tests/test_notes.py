from fastapi.testclient import TestClient
from backend.tests.conftest import create_test_notes


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


class TestPaginationSkip:
    def test_skip_zero(self, client):
        """Test skip=0 returns all results from the beginning."""
        notes = create_test_notes(client, 10)
        response = client.get("/notes/", params={"skip": 0, "limit": 50, "sort": "id"})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 10
        assert result[0]["id"] == notes[0]["id"]

    def test_skip_five(self, client):
        """Test skip=5 skips first 5 results."""
        notes = create_test_notes(client, 10)
        response = client.get("/notes/", params={"skip": 5, "limit": 50, "sort": "id"})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 5
        assert result[0]["id"] == notes[5]["id"]
        assert result[1]["id"] == notes[6]["id"]

    def test_skip_beyond_range(self, client):
        """Test skip beyond available results returns empty list."""
        create_test_notes(client, 10)
        response = client.get("/notes/", params={"skip": 100, "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 0

    def test_skip_at_boundary(self, client):
        """Test skip at exact boundary returns last item."""
        notes = create_test_notes(client, 10)
        response = client.get("/notes/", params={"skip": 9, "limit": 50, "sort": "id"})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert result[0]["id"] == notes[9]["id"]


class TestPaginationLimit:
    def test_limit_one(self, client):
        """Test limit=1 returns single result."""
        notes = create_test_notes(client, 10)
        response = client.get("/notes/", params={"limit": 1})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1

    def test_limit_fifty(self, client):
        """Test limit=50 with various data sizes."""
        notes = create_test_notes(client, 30)
        response = client.get("/notes/", params={"limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 30
        assert len(result) <= 50

    def test_limit_max_boundary(self, client):
        """Test limit=200 (maximum allowed)."""
        notes = create_test_notes(client, 100)
        response = client.get("/notes/", params={"limit": 200})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 100
        assert len(result) <= 200

    def test_limit_exceeds_max(self, client):
        """Test that limit > 200 is rejected by validation."""
        response = client.get("/notes/", params={"limit": 201})
        assert response.status_code == 422

    def test_limit_actual_less_than_limit_param(self, client):
        """Test that actual results are never more than limit parameter."""
        create_test_notes(client, 5)
        for limit_val in [1, 3, 10, 50]:
            response = client.get("/notes/", params={"limit": limit_val})
            assert response.status_code == 200
            result = response.json()
            assert len(result) <= limit_val


class TestSortCreatedAt:
    def test_sort_created_at_descending(self, client):
        """Test sort=-created_at returns newest first."""
        notes = create_test_notes(client, 5)
        response = client.get("/notes/", params={"sort": "-created_at", "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 5
        for i in range(len(result) - 1):
            assert result[i]["created_at"] >= result[i + 1]["created_at"]

    def test_sort_created_at_ascending(self, client):
        """Test sort=created_at returns oldest first."""
        notes = create_test_notes(client, 5)
        response = client.get("/notes/", params={"sort": "created_at", "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 5
        for i in range(len(result) - 1):
            assert result[i]["created_at"] <= result[i + 1]["created_at"]

    def test_sort_created_at_default(self, client):
        """Test default sort is -created_at (descending)."""
        notes = create_test_notes(client, 5)
        response_default = client.get("/notes/", params={"limit": 50})
        response_explicit = client.get("/notes/", params={"sort": "-created_at", "limit": 50})
        assert response_default.status_code == 200
        assert response_explicit.status_code == 200
        result_default = response_default.json()
        result_explicit = response_explicit.json()
        assert [r["id"] for r in result_default] == [r["id"] for r in result_explicit]


class TestSortAlternativeFields:
    def test_sort_title_ascending(self, client):
        """Test sort=title returns alphabetical order."""
        notes = create_test_notes(client, 5)
        response = client.get("/notes/", params={"sort": "title", "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 5
        for i in range(len(result) - 1):
            assert result[i]["title"] <= result[i + 1]["title"]

    def test_sort_title_descending(self, client):
        """Test sort=-title returns reverse alphabetical order."""
        notes = create_test_notes(client, 5)
        response = client.get("/notes/", params={"sort": "-title", "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 5
        for i in range(len(result) - 1):
            assert result[i]["title"] >= result[i + 1]["title"]

    def test_sort_id_ascending(self, client):
        """Test sort=id returns ascending ID order."""
        notes = create_test_notes(client, 5)
        response = client.get("/notes/", params={"sort": "id", "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 5
        for i in range(len(result) - 1):
            assert result[i]["id"] <= result[i + 1]["id"]

    def test_sort_id_descending(self, client):
        """Test sort=-id returns descending ID order."""
        notes = create_test_notes(client, 5)
        response = client.get("/notes/", params={"sort": "-id", "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 5
        for i in range(len(result) - 1):
            assert result[i]["id"] >= result[i + 1]["id"]

    def test_sort_invalid_field_fallback(self, client):
        """Test that invalid sort field falls back to default sorting."""
        notes = create_test_notes(client, 5)
        response = client.get("/notes/", params={"sort": "invalid_field", "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 5
        for i in range(len(result) - 1):
            assert result[i]["created_at"] >= result[i + 1]["created_at"]


class TestPaginationWithSort:
    def test_skip_limit_sort_together(self, client):
        """Test skip, limit, and sort parameters work together."""
        notes = create_test_notes(client, 20)
        response = client.get("/notes/", params={"skip": 5, "limit": 10, "sort": "created_at"})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 10
        for i in range(len(result) - 1):
            assert result[i]["created_at"] <= result[i + 1]["created_at"]

    def test_skip_limit_sort_title_desc(self, client):
        """Test skip, limit with sort=-title."""
        notes = create_test_notes(client, 20)
        response = client.get("/notes/", params={"skip": 2, "limit": 5, "sort": "-title"})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 5
        for i in range(len(result) - 1):
            assert result[i]["title"] >= result[i + 1]["title"]

    def test_pagination_preserves_sort_across_pages(self, client):
        """Test that sorting is consistent across paginated requests."""
        notes = create_test_notes(client, 15)
        response1 = client.get("/notes/", params={"skip": 0, "limit": 5, "sort": "id"})
        result1 = response1.json()
        response2 = client.get("/notes/", params={"skip": 5, "limit": 5, "sort": "id"})
        result2 = response2.json()
        for i in range(len(result1) - 1):
            assert result1[i]["id"] <= result1[i + 1]["id"]
        for i in range(len(result2) - 1):
            assert result2[i]["id"] <= result2[i + 1]["id"]
        if result1 and result2:
            assert result1[-1]["id"] < result2[0]["id"]


class TestSearchWithPagination:
    def test_search_with_pagination(self, client):
        """Test search parameter combined with pagination."""
        create_test_notes(client, 10)
        payload = {"title": "SPECIAL", "content": "unique content"}
        special = client.post("/notes/", json=payload).json()
        response = client.get("/notes/", params={"q": "SPECIAL", "skip": 0, "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) >= 1
        titles = [r["title"] for r in result]
        assert "SPECIAL" in titles

    def test_search_with_skip_skip_all_results(self, client):
        """Test search with skip that exceeds search results."""
        create_test_notes(client, 5)
        for i in range(3):
            client.post("/notes/", json={"title": f"FINDME_{i}", "content": "content"})
        response = client.get("/notes/", params={"q": "FINDME", "skip": 10, "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 0

    def test_search_with_sort_pagination(self, client):
        """Test search with pagination and custom sorting."""
        create_test_notes(client, 5)
        for i in range(3):
            client.post("/notes/", json={"title": f"TARGET_{i}", "content": f"content {i}"})
        response = client.get("/notes/", params={"q": "TARGET", "skip": 0, "limit": 50, "sort": "-id"})
        assert response.status_code == 200
        result = response.json()
        assert len(result) >= 1
        for i in range(len(result) - 1):
            assert result[i]["id"] >= result[i + 1]["id"]


class TestEdgeCases:
    def test_empty_results_with_pagination(self, client):
        """Test pagination on empty result set."""
        response = client.get("/notes/", params={"skip": 0, "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 0

    def test_single_note_pagination(self, client):
        """Test pagination with only one note."""
        notes = create_test_notes(client, 1)
        response = client.get("/notes/", params={"skip": 0, "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert result[0]["id"] == notes[0]["id"]

    def test_large_skip_with_small_limit(self, client):
        """Test large skip with small limit."""
        notes = create_test_notes(client, 5)
        response = client.get("/notes/", params={"skip": 3, "limit": 1, "sort": "id"})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert result[0]["id"] == notes[3]["id"]

    def test_zero_limit_default_behavior(self, client):
        """Test default limit when not specified."""
        notes = create_test_notes(client, 30)
        response = client.get("/notes/")
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 30

    def test_negative_skip_treated_as_zero(self, client):
        """Test that negative skip might be handled (depends on validation)."""
        notes = create_test_notes(client, 5)
        response = client.get("/notes/", params={"skip": -1, "limit": 50})
        if response.status_code != 422:
            result = response.json()
            assert len(result) > 0

    def test_sorting_with_equal_values(self, client):
        """Test sorting stability when multiple items have same sort value."""
        payload1 = {"title": "Note A", "content": "content"}
        payload2 = {"title": "Note B", "content": "content"}
        note1 = client.post("/notes/", json=payload1).json()
        note2 = client.post("/notes/", json=payload2).json()
        response = client.get("/notes/", params={"sort": "created_at", "limit": 50})
        assert response.status_code == 200
        result = response.json()
        ids = [r["id"] for r in result]
        assert note1["id"] in ids
        assert note2["id"] in ids
