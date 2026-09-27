from tests.conftest import login, signup


def create_post(client, headers, title="제목", tag="AI"):
    return client.post("/api/post/create", headers=headers, json={"title": title, "content": "내용", "tag": tag})


def test_create_requires_auth(client):
    assert create_post(client, {}).status_code == 401


def test_create_and_read(client, auth_headers):
    post = create_post(client, auth_headers).json()
    assert post["writer_name"] == "tester"

    assert client.get(f"/api/post/read/{post['post_id']}").json()["title"] == "제목"
    assert client.get("/api/post/read/999").status_code == 404


def test_read_all_newest_first(client, auth_headers):
    create_post(client, auth_headers, title="첫 글")
    create_post(client, auth_headers, title="둘째 글")
    titles = [p["title"] for p in client.get("/api/post/read/all").json()]
    assert titles == ["둘째 글", "첫 글"]


def test_read_by_tag_ignores_spaces(client, auth_headers):
    create_post(client, auth_headers, tag="인공 지능")
    create_post(client, auth_headers, tag="경제")
    posts = client.get("/api/post/read/tag/인공지능").json()
    assert [p["tag"] for p in posts] == ["인공 지능"]


def test_only_writer_can_update_or_delete(client, auth_headers):
    post_id = create_post(client, auth_headers).json()["post_id"]

    signup(client, username="other", email="other@example.com")
    other = {"Authorization": f"Bearer {login(client, email='other@example.com').json()['access_token']}"}

    update = {"title": "수정", "content": "수정"}
    assert client.patch(f"/api/post/update/{post_id}", headers=other, json=update).status_code == 403
    assert client.delete(f"/api/post/delete/{post_id}", headers=other).status_code == 403

    assert client.patch(f"/api/post/update/{post_id}", headers=auth_headers, json=update).json()["title"] == "수정"
    assert client.delete(f"/api/post/delete/{post_id}", headers=auth_headers).status_code == 200
    assert client.get(f"/api/post/read/{post_id}").status_code == 404
