from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi.testclient import TestClient
from orders_api.core.config import settings


def make_token(user_id: str, expires_at: datetime, key: str) -> str:
    """Fabrica um token com a expiração e a chave que o teste escolher."""
    return jwt.encode(
        {"sub": user_id, "exp": expires_at}, key, algorithm=settings.jwt_algorithm
    )


def test_recusa_requisicao_sem_token(client: TestClient, user: dict[str, Any]) -> None:
    response = client.get(f"/v1/users/{user['user_id']}")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "not_authenticated"


def test_recusa_token_falso(client: TestClient, user: dict[str, Any]) -> None:
    response = client.get(
        f"/v1/users/{user['user_id']}",
        headers={"Authorization": "Bearer token-falso"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_token"


def test_recusa_token_expirado(client: TestClient, user: dict[str, Any]) -> None:
    token = make_token(
        user["user_id"],
        expires_at=datetime.now(UTC) - timedelta(minutes=1),
        key=settings.jwt_secret_key.get_secret_value(),
    )

    response = client.get(
        f"/v1/users/{user['user_id']}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_token"


def test_recusa_token_assinado_com_outra_chave(
    client: TestClient, user: dict[str, Any]
) -> None:
    token = make_token(
        user["user_id"],
        expires_at=datetime.now(UTC) + timedelta(minutes=30),
        key="chave-de-um-atacante-com-mais-de-32-bytes",
    )

    response = client.get(
        f"/v1/users/{user['user_id']}", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_token"


def test_cadastro_continua_publico(client: TestClient) -> None:
    response = client.post(
        "/v1/users",
        json={"name": "Novo", "email": "novo@exemplo.com", "password": "senha-nova"},
    )

    assert response.status_code == 201
