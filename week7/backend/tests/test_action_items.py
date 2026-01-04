from fastapi.testclient import TestClient
from backend.tests.conftest import create_test_action_items


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


# Pagination Tests - Skip Parameter
class TestActionItemPaginationSkip:
    def test_skip_zero(self, client):
        """Test skip=0 returns all results from the beginning."""
        items = create_test_action_items(client, 10)
        response = client.get("/action-items/", params={"skip": 0, "limit": 50, "sort": "id"})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 10
        assert result[0]["id"] == items[0]["id"]

    def test_skip_five(self, client):
        """Test skip=5 skips first 5 results."""
        items = create_test_action_items(client, 10)
        response = client.get("/action-items/", params={"skip": 5, "limit": 50, "sort": "id"})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 5
        assert result[0]["id"] == items[5]["id"]
        assert result[1]["id"] == items[6]["id"]

    def test_skip_beyond_range(self, client):
        """Test skip beyond available results returns empty list."""
        create_test_action_items(client, 10)
        response = client.get("/action-items/", params={"skip": 100, "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 0

    def test_skip_at_boundary(self, client):
        """Test skip at exact boundary returns last item."""
        items = create_test_action_items(client, 10)
        response = client.get("/action-items/", params={"skip": 9, "limit": 50, "sort": "id"})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert result[0]["id"] == items[9]["id"]


# Pagination Tests - Limit Parameter
class TestActionItemPaginationLimit:
    def test_limit_one(self, client):
        """Test limit=1 returns single result."""
        items = create_test_action_items(client, 10)
        response = client.get("/action-items/", params={"limit": 1})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1

    def test_limit_fifty(self, client):
        """Test limit=50 with various data sizes."""
        items = create_test_action_items(client, 30)
        response = client.get("/action-items/", params={"limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 30
        assert len(result) <= 50

    def test_limit_max_boundary(self, client):
        """Test limit=200 (maximum allowed)."""
        items = create_test_action_items(client, 100)
        response = client.get("/action-items/", params={"limit": 200})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 100
        assert len(result) <= 200

    def test_limit_exceeds_max(self, client):
        """Test that limit > 200 is rejected by validation."""
        response = client.get("/action-items/", params={"limit": 201})
        assert response.status_code == 422

    def test_limit_actual_less_than_limit_param(self, client):
        """Test that actual results are never more than limit parameter."""
        create_test_action_items(client, 5)
        for limit_val in [1, 3, 10, 50]:
            response = client.get("/action-items/", params={"limit": limit_val})
            assert response.status_code == 200
            result = response.json()
            assert len(result) <= limit_val


# Sorting Tests - Ascending/Descending on created_at
class TestActionItemSortCreatedAt:
    def test_sort_created_at_descending(self, client):
        """Test sort=-created_at returns newest first."""
        items = create_test_action_items(client, 5)
        response = client.get("/action-items/", params={"sort": "-created_at", "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 5
        for i in range(len(result) - 1):
            assert result[i]["created_at"] >= result[i + 1]["created_at"]

    def test_sort_created_at_ascending(self, client):
        """Test sort=created_at returns oldest first."""
        items = create_test_action_items(client, 5)
        response = client.get("/action-items/", params={"sort": "created_at", "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 5
        for i in range(len(result) - 1):
            assert result[i]["created_at"] <= result[i + 1]["created_at"]

    def test_sort_created_at_default(self, client):
        """Test default sort is -created_at (descending)."""
        items = create_test_action_items(client, 5)
        response_default = client.get("/action-items/", params={"limit": 50})
        response_explicit = client.get("/action-items/", params={"sort": "-created_at", "limit": 50})
        assert response_default.status_code == 200
        assert response_explicit.status_code == 200
        result_default = response_default.json()
        result_explicit = response_explicit.json()
        assert [r["id"] for r in result_default] == [r["id"] for r in result_explicit]


# Sorting Tests - Alternative Sort Fields
class TestActionItemSortAlternativeFields:
    def test_sort_id_ascending(self, client):
        """Test sort=id returns ascending ID order."""
        items = create_test_action_items(client, 5)
        response = client.get("/action-items/", params={"sort": "id", "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 5
        for i in range(len(result) - 1):
            assert result[i]["id"] <= result[i + 1]["id"]

    def test_sort_id_descending(self, client):
        """Test sort=-id returns descending ID order."""
        items = create_test_action_items(client, 5)
        response = client.get("/action-items/", params={"sort": "-id", "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 5
        for i in range(len(result) - 1):
            assert result[i]["id"] >= result[i + 1]["id"]

    def test_sort_description_ascending(self, client):
        """Test sort=description returns alphabetical order."""
        items = create_test_action_items(client, 5)
        response = client.get("/action-items/", params={"sort": "description", "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 5
        for i in range(len(result) - 1):
            assert result[i]["description"] <= result[i + 1]["description"]

    def test_sort_invalid_field_fallback(self, client):
        """Test that invalid sort field falls back to default sorting."""
        items = create_test_action_items(client, 5)
        response = client.get("/action-items/", params={"sort": "invalid_field", "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 5
        for i in range(len(result) - 1):
            assert result[i]["created_at"] >= result[i + 1]["created_at"]


# Filter with Pagination Tests
class TestActionItemFilterWithPagination:
    def test_filter_completed_with_pagination(self, client):
        """Test completed filter combined with pagination."""
        incomplete = create_test_action_items(client, 5, completed=False)
        completed = create_test_action_items(client, 3, completed=True)
        response = client.get("/action-items/", params={"completed": True, "skip": 0, "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 3
        for item in result:
            assert item["completed"] is True

    def test_filter_incomplete_with_skip_limit(self, client):
        """Test incomplete filter with skip and limit."""
        create_test_action_items(client, 5, completed=False)
        create_test_action_items(client, 2, completed=True)
        response = client.get("/action-items/", params={"completed": False, "skip": 1, "limit": 2})
        assert response.status_code == 200
        result = response.json()
        assert len(result) <= 2
        for item in result:
            assert item["completed"] is False

    def test_filter_completed_with_sort(self, client):
        """Test completed filter with custom sorting."""
        create_test_action_items(client, 2, completed=False)
        complete_items = create_test_action_items(client, 3, completed=True)
        response = client.get("/action-items/", params={"completed": True, "sort": "-id", "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 3
        for i in range(len(result) - 1):
            assert result[i]["id"] >= result[i + 1]["id"]


# Sorting Tests - Completed Field
class TestActionItemSortCompleted:
    def test_sort_completed_ascending(self, client):
        """Test sort=completed returns false first then true."""
        create_test_action_items(client, 3, completed=True)
        create_test_action_items(client, 2, completed=False)
        response = client.get("/action-items/", params={"sort": "completed", "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 5
        for i in range(len(result) - 1):
            assert result[i]["completed"] <= result[i + 1]["completed"]

    def test_sort_completed_descending(self, client):
        """Test sort=-completed returns true first then false."""
        create_test_action_items(client, 2, completed=False)
        create_test_action_items(client, 3, completed=True)
        response = client.get("/action-items/", params={"sort": "-completed", "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 5
        for i in range(len(result) - 1):
            assert result[i]["completed"] >= result[i + 1]["completed"]


# Combined Pagination and Sorting Tests
class TestActionItemPaginationWithSort:
    def test_skip_limit_sort_together(self, client):
        """Test skip, limit, and sort parameters work together."""
        items = create_test_action_items(client, 20)
        response = client.get("/action-items/", params={"skip": 5, "limit": 10, "sort": "created_at"})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 10
        for i in range(len(result) - 1):
            assert result[i]["created_at"] <= result[i + 1]["created_at"]

    def test_skip_limit_sort_id_desc(self, client):
        """Test skip, limit with sort=-id."""
        items = create_test_action_items(client, 20)
        response = client.get("/action-items/", params={"skip": 2, "limit": 5, "sort": "-id"})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 5
        for i in range(len(result) - 1):
            assert result[i]["id"] >= result[i + 1]["id"]

    def test_pagination_preserves_sort_across_pages(self, client):
        """Test that sorting is consistent across paginated requests."""
        items = create_test_action_items(client, 15)
        response1 = client.get("/action-items/", params={"skip": 0, "limit": 5, "sort": "id"})
        result1 = response1.json()
        response2 = client.get("/action-items/", params={"skip": 5, "limit": 5, "sort": "id"})
        result2 = response2.json()
        for i in range(len(result1) - 1):
            assert result1[i]["id"] <= result1[i + 1]["id"]
        for i in range(len(result2) - 1):
            assert result2[i]["id"] <= result2[i + 1]["id"]
        if result1 and result2:
            assert result1[-1]["id"] < result2[0]["id"]

    def test_filter_sort_pagination_together(self, client):
        """Test filter, sort, and pagination all together."""
        create_test_action_items(client, 5, completed=False)
        create_test_action_items(client, 20, completed=True)
        response = client.get("/action-items/", params={"completed": True, "skip": 3, "limit": 5, "sort": "-created_at"})
        assert response.status_code == 200
        result = response.json()
        assert len(result) <= 5
        for item in result:
            assert item["completed"] is True
        for i in range(len(result) - 1):
            assert result[i]["created_at"] >= result[i + 1]["created_at"]


# Edge Case Tests
class TestActionItemEdgeCases:
    def test_empty_results_with_pagination(self, client):
        """Test pagination on empty result set."""
        response = client.get("/action-items/", params={"skip": 0, "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 0

    def test_empty_results_with_filter(self, client):
        """Test filter that returns no results."""
        create_test_action_items(client, 5, completed=False)
        response = client.get("/action-items/", params={"completed": True, "skip": 0, "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 0

    def test_single_item_pagination(self, client):
        """Test pagination with only one item."""
        items = create_test_action_items(client, 1)
        response = client.get("/action-items/", params={"skip": 0, "limit": 50})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert result[0]["id"] == items[0]["id"]

    def test_large_skip_with_small_limit(self, client):
        """Test large skip with small limit."""
        items = create_test_action_items(client, 5)
        response = client.get("/action-items/", params={"skip": 3, "limit": 1, "sort": "id"})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 1
        assert result[0]["id"] == items[3]["id"]

    def test_zero_limit_default_behavior(self, client):
        """Test default limit when not specified."""
        items = create_test_action_items(client, 30)
        response = client.get("/action-items/")
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 30

    def test_all_completed_pagination(self, client):
        """Test pagination when all items are completed."""
        create_test_action_items(client, 10, completed=True)
        response = client.get("/action-items/", params={"completed": True, "skip": 0, "limit": 5})
        assert response.status_code == 200
        result = response.json()
        assert len(result) == 5
        for item in result:
            assert item["completed"] is True

    def test_sorting_with_equal_completed_status(self, client):
        """Test sorting when items have equal completed status."""
        items = create_test_action_items(client, 3, completed=True)
        response = client.get("/action-items/", params={"sort": "created_at", "limit": 50})
        assert response.status_code == 200
        result = response.json()
        for item in result:
            assert item["completed"] is True
        assert len(result) == 3
