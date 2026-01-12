def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"

    # Basic list endpoint should still return a plain list
    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list)
    assert len(items) >= 1

    # Default search response shape and defaults
    r = client.get("/notes/search")
    assert r.status_code == 200
    search = r.json()
    assert set(search.keys()) == {"items", "total", "page", "page_size"}
    assert search["page"] == 1
    assert search["page_size"] == 10
    assert search["total"] >= 1
    assert len(search["items"]) >= 1

    # Case-insensitive search by content
    r = client.get("/notes/search", params={"q": "hello"})
    assert r.status_code == 200
    search = r.json()
    assert search["total"] >= 1
    titles = [item["title"] for item in search["items"]]
    assert "Test" in titles


def test_search_case_insensitive(client):
    payload = {"title": "Hello World", "content": "Foo BAR"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    note_id = r.json()["id"]

    for q in ["hello", "HELLO", "bar", "BAR"]:
        r = client.get("/notes/search", params={"q": q})
        assert r.status_code == 200
        data = r.json()
        ids = [item["id"] for item in data["items"]]
        assert note_id in ids


def test_search_pagination(client):
    # create more than one page of notes
    for i in range(15):
        r = client.post("/notes/", json={"title": f"Note {i}", "content": "x"})
        assert r.status_code == 201

    # page 1
    r = client.get("/notes/search", params={"page": 1, "page_size": 10})
    assert r.status_code == 200
    page1 = r.json()
    assert page1["page"] == 1
    assert page1["page_size"] == 10
    assert page1["total"] >= 15
    assert len(page1["items"]) == 10

    # page 2
    r = client.get("/notes/search", params={"page": 2, "page_size": 10})
    assert r.status_code == 200
    page2 = r.json()
    assert page2["page"] == 2
    assert page2["page_size"] == 10
    assert page2["total"] == page1["total"]
    assert 1 <= len(page2["items"]) <= 10

    # out-of-range page
    r = client.get("/notes/search", params={"page": 3, "page_size": 10})
    assert r.status_code == 200
    page3 = r.json()
    assert page3["page"] == 3
    assert page3["total"] == page1["total"]
    assert page3["items"] == []


def test_search_sort_title_asc(client):
    titles = ["zeta", "alpha", "mango"]
    for title in titles:
        r = client.post("/notes/", json={"title": title, "content": "x"})
        assert r.status_code == 201

    r = client.get("/notes/search", params={"sort": "title_asc", "page_size": 10})
    assert r.status_code == 200
    data = r.json()
    returned_titles = [item["title"] for item in data["items"]]
    # Filter to the ones we created in this test
    present = [t for t in returned_titles if t in titles]
    assert present == sorted(present)


def test_search_sort_invalid_defaults_to_created_desc(client):
    created_ids = []
    for i in range(3):
        r = client.post("/notes/", json={"title": f"Note {i}", "content": "x"})
        assert r.status_code == 201
        created_ids.append(r.json()["id"])

    max_id = max(created_ids)

    r = client.get("/notes/search", params={"sort": "unknown", "page_size": 10})
    assert r.status_code == 200
    data = r.json()
    returned_ids = [item["id"] for item in data["items"]]
    assert returned_ids[0] == max_id
    assert returned_ids == sorted(returned_ids, reverse=True)
