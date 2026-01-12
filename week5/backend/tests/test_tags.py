from week5.backend.app.models import Note, Tag


def test_tags_crud(client):
    # Initially empty
    r = client.get("/tags")
    assert r.status_code == 200
    assert r.json() == []

    # Create a tag
    r = client.post("/tags", json={"name": "work"})
    assert r.status_code == 201, r.text
    tag = r.json()
    assert tag["name"] == "work"
    tag_id = tag["id"]

    # List should include the tag
    r = client.get("/tags")
    assert r.status_code == 200
    tags = r.json()
    names = [t["name"] for t in tags]
    assert "work" in names

    # Creating a duplicate tag should fail
    r = client.post("/tags", json={"name": "work"})
    assert r.status_code == 400

    # Delete the tag
    r = client.delete(f"/tags/{tag_id}")
    assert r.status_code == 204

    # It should no longer appear in the list
    r = client.get("/tags")
    assert r.status_code == 200
    names = [t["name"] for t in r.json()]
    assert "work" not in names

    # Deleting again should return 404
    r = client.delete(f"/tags/{tag_id}")
    assert r.status_code == 404


def test_note_tag_attach_detach(client):
    # Create a note and a tag
    note_r = client.post("/notes/", json={"title": "Test Note", "content": "Content"})
    assert note_r.status_code == 201
    note = note_r.json()
    note_id = note["id"]
    assert note["tags"] == []

    tag_r = client.post("/tags", json={"name": "test-tag"})
    assert tag_r.status_code == 201
    tag = tag_r.json()
    tag_id = tag["id"]

    # Attach tag to note
    r = client.post(f"/notes/{note_id}/tags", json={"tag_id": tag_id})
    assert r.status_code == 200
    note_updated = r.json()
    assert len(note_updated["tags"]) == 1
    assert note_updated["tags"][0]["id"] == tag_id
    assert note_updated["tags"][0]["name"] == "test-tag"

    # Try to attach the same tag again (should fail)
    r = client.post(f"/notes/{note_id}/tags", json={"tag_id": tag_id})
    assert r.status_code == 400

    # Detach tag from note
    r = client.delete(f"/notes/{note_id}/tags/{tag_id}")
    assert r.status_code == 200
    note_updated = r.json()
    assert len(note_updated["tags"]) == 0

    # Try to detach again (should fail)
    r = client.delete(f"/notes/{note_id}/tags/{tag_id}")
    assert r.status_code == 400

    # Attach non-existent tag (should fail)
    r = client.post(f"/notes/{note_id}/tags", json={"tag_id": 99999})
    assert r.status_code == 404

    # Attach tag to non-existent note (should fail)
    r = client.post("/notes/99999/tags", json={"tag_id": tag_id})
    assert r.status_code == 404


def test_search_notes_by_tag(client):
    # Create notes and tags
    note1_r = client.post("/notes/", json={"title": "Note 1", "content": "Content 1"})
    note2_r = client.post("/notes/", json={"title": "Note 2", "content": "Content 2"})
    assert note1_r.status_code == 201
    assert note2_r.status_code == 201
    note1_id = note1_r.json()["id"]
    note2_id = note2_r.json()["id"]

    tag_r = client.post("/tags", json={"name": "important"})
    assert tag_r.status_code == 201
    tag_id = tag_r.json()["id"]

    # Attach tag only to note1
    r = client.post(f"/notes/{note1_id}/tags", json={"tag_id": tag_id})
    assert r.status_code == 200

    # Search without tag filter - should return both notes
    r = client.get("/notes/search", params={"page_size": 10})
    assert r.status_code == 200
    data = r.json()
    note_ids = [n["id"] for n in data["items"]]
    assert note1_id in note_ids
    assert note2_id in note_ids

    # Search with tag filter - should return only note1
    r = client.get("/notes/search", params={"tag_id": tag_id, "page_size": 10})
    assert r.status_code == 200
    data = r.json()
    note_ids = [n["id"] for n in data["items"]]
    assert note1_id in note_ids
    assert note2_id not in note_ids

    # Search with non-existent tag (should fail)
    r = client.get("/notes/search", params={"tag_id": 99999})
    assert r.status_code == 404
