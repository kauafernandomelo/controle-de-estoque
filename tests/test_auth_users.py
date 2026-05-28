from fastapi.testclient import TestClient


def test_register_first_user_as_admin_and_refresh_token(client: TestClient) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={"nome": "Admin User", "email": "admin@example.com", "senha": "strongpass123"},
    )
    assert register_response.status_code == 201
    assert register_response.json()["perfil"] == "ADMINISTRADOR"

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@example.com", "password": "strongpass123"},
    )
    assert login_response.status_code == 200
    refresh_token = login_response.json()["refresh_token"]

    refresh_response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_response.status_code == 200
    assert refresh_response.json()["token_type"] == "bearer"


def test_invalid_login_returns_401(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "missing@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 401


def test_admin_can_create_user_and_operator_cannot_list_users(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    create_response = client.post(
        "/api/v1/users",
        headers=admin_headers,
        json={
            "nome": "Operator User",
            "email": "operator@example.com",
            "senha": "strongpass123",
            "perfil": "OPERADOR",
        },
    )
    assert create_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "operator@example.com", "password": "strongpass123"},
    )
    operator_token = login_response.json()["access_token"]

    list_response = client.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {operator_token}"}
    )
    assert list_response.status_code == 403


def test_duplicate_registration_returns_conflict(client: TestClient) -> None:
    payload = {"nome": "Admin User", "email": "admin@example.com", "senha": "strongpass123"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
