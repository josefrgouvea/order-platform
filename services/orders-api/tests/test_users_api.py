from typing import Any
from uuid import uuid4

from fastapi.testclient import TestClient


def test_cria_usuario(client: TestClient) -> None:
    response = client.post(
        "/v1/users",
        json={"name": "Jose", "email": "jose@exemplo.com", "password": "senha-do-jose"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Jose"
    assert body["email"] == "jose@exemplo.com"
    assert "user_id" in body


def test_consulta_usuario(
    client: TestClient, user: dict[str, Any], auth_headers: dict[str, str]
) -> None:
    response = client.get(f"/v1/users/{user['user_id']}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == user


def test_recusa_email_repetido(client: TestClient, user: dict[str, Any]) -> None:
    response = client.post(
        "/v1/users",
        json={"name": "Joao", "email": user["email"], "password": "outra-senha"},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "email_already_registered"


def test_usuario_inexistente(client: TestClient, auth_headers: dict[str, str]) -> None:
    response = client.get(f"/v1/users/{uuid4()}", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "user_not_found"


def test_recusa_dados_invalidos(client: TestClient) -> None:
    response = client.post(
        "/v1/users", json={"name": "", "email": "abc", "password": "short"}
    )

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    fields = {detail["field"] for detail in error["details"]}
    assert fields == {"body.name", "body.email", "body.password"}


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


def test_recusa_senha_curta(client: TestClient) -> None:
    response = client.post(
        "/v1/users",
        json={"name": "Jose", "email": "jose@exemplo.com", "password": "short"},
    )
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    fields = {detail["field"] for detail in error["details"]}
    assert fields == {"body.password"}


def test_senha_nunca_aparece_na_resposta(
    client: TestClient, user: dict[str, Any], auth_headers: dict[str, str]
) -> None:
    # A resposta do cadastro (a fixture user é ela)
    assert "password" not in user
    assert "password_hash" not in user

    # A resposta da consulta
    response = client.get(f"/v1/users/{user['user_id']}", headers=auth_headers)
    assert response.status_code == 200
    assert "password" not in response.json()
    assert "password_hash" not in response.json()
