from tests.conftest import login, signup


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_signup(client):
    response = signup(client)
    assert response.status_code == 201
    assert response.json() == {"detail": "회원가입이 완료되었습니다."}


def test_signup_duplicate_email(client):
    signup(client)
    response = signup(client, username="other")
    assert response.status_code == 409


def test_signup_duplicate_username(client):
    signup(client)
    response = signup(client, email="other@example.com")
    assert response.status_code == 409
    assert response.json()["detail"] == "이미 사용 중인 이름입니다."


def test_signup_password_mismatch(client):
    response = client.post("/api/user/signup", json={
        "username": "tester", "email": "tester@example.com",
        "password": "pw123456", "confirm_password": "different",
    })
    assert response.status_code == 422


def test_login(client):
    signup(client)
    response = login(client)
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["username"] == "tester"


def test_login_wrong_password(client):
    signup(client)
    assert login(client, password="wrong").status_code == 400


def test_me_requires_token(client):
    assert client.get("/api/user/me").status_code == 401


def test_me_rejects_invalid_token(client):
    response = client.get("/api/user/me", headers={"Authorization": "Bearer not-a-jwt"})
    assert response.status_code == 401


def test_me_hides_password_hash(client, auth_headers):
    response = client.get("/api/user/me", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["user_email"] == "tester@example.com"
    assert "user_password" not in body


def test_update_password_does_not_echo_passwords(client, auth_headers):
    response = client.patch("/api/user/update/password", headers=auth_headers, json={
        "current_password": "pw123456", "new_password": "newpw123", "confirm_new_password": "newpw123",
    })
    assert response.status_code == 200
    assert "newpw123" not in response.text
    assert login(client, password="newpw123").status_code == 200
