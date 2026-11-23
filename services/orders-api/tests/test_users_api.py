from typing import Any
from uuid import uuid4

from fastapi.testclient import TestClient


def test_cria_usuario(client: TestClient) -> None:
    response = client.post(
        "/v1/users", json={"name": "Jose", "email": "jose@exemplo.com"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Jose"
    assert body["email"] == "jose@exemplo.com"
    assert "user_id" in body


def test_consulta_usuario(client: TestClient, user: dict[str, Any]) -> None:
    response = client.get(f"/v1/users/{user['user_id']}")

    assert response.status_code == 200
    assert response.json() == user


def test_recusa_email_repetido(client: TestClient, user: dict[str, Any]) -> None:
    response = client.post("/v1/users", json={"name": "Joao", "email": user["email"]})

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "email_already_registered"


def test_usuario_inexistente(client: TestClient) -> None:
    response = client.get(f"/v1/users/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "user_not_found"


def test_recusa_dados_invalidos(client: TestClient) -> None:
    response = client.post("/v1/users", json={"name": "", "email": "abc"})

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    fields = {detail["field"] for detail in error["details"]}
    assert fields == {"body.name", "body.email"}


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "version" in body
    assert "environment" in body


def test_handle_error(client: TestClient) -> None:
    response = client.get("/v1/nada")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "http_error"
