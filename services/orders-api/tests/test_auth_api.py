from datetime import UTC, datetime
from typing import Any

import jwt
from fastapi.testclient import TestClient
from orders_api.core.config import settings


def test_login_devolve_token_valido(client: TestClient, user: dict[str, Any]) -> None:
    response = client.post(
        "/v1/auth/login",
        data={"username": user["email"], "password": "senha-do-jose"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"

    payload = jwt.decode(
        body["access_token"],
        settings.jwt_secret_key.get_secret_value(),
        algorithms=[settings.jwt_algorithm],
    )
    assert payload["sub"] == user["user_id"]
    assert payload["exp"] > datetime.now(UTC).timestamp()


def test_login_recusa_senha_incorreta(client: TestClient, user: dict[str, Any]) -> None:
    response = client.post(
        "/v1/auth/login",
        data={"username": user["email"], "password": "senha-errada"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"


def test_login_recusa_email_inexistente(client: TestClient) -> None:
    response = client.post(
        "/v1/auth/login",
        data={"username": "email@inexistente.com", "password": "senha-qualquer"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"


def test_login_nao_revela_se_o_email_existe(
    client: TestClient, user: dict[str, Any]
) -> None:
    response1 = client.post(
        "/v1/auth/login",
        data={"username": user["email"], "password": "senha-qualquer"},
    )

    response2 = client.post(
        "/v1/auth/login",
        data={"username": "email@inexistente.com", "password": "senha-qualquer"},
    )
    assert response1.status_code == 401
    assert response1.json()["error"]["code"] == "invalid_credentials"
    assert response2.status_code == 401
    assert response2.json()["error"]["code"] == "invalid_credentials"
    assert response1.json() == response2.json()
