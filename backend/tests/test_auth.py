from app.seed import DEV_PASSWORD


def test_login_success(client):
    response = client.post("/api/auth/login", json={"username": "alice", "password": DEV_PASSWORD})
    assert response.status_code == 200
    assert response.json()["username"] == "alice"


def test_login_wrong_password(client):
    response = client.post("/api/auth/login", json={"username": "alice", "password": "wrong"})
    assert response.status_code == 401


def test_login_unknown_user(client):
    response = client.post("/api/auth/login", json={"username": "nobody", "password": "x"})
    assert response.status_code == 401


def test_me_requires_authentication(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_after_login(logged_in_client):
    response = logged_in_client.get("/api/auth/me")
    assert response.status_code == 200
    assert response.json()["username"] == "alice"


def test_logout_clears_session(logged_in_client):
    response = logged_in_client.post("/api/auth/logout")
    assert response.status_code == 204
    response = logged_in_client.get("/api/auth/me")
    assert response.status_code == 401
