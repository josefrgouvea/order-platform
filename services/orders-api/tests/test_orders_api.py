from typing import Any
from uuid import UUID

from fastapi.testclient import TestClient


def test_cria_pedido_para_usuario_existente(
    client: TestClient, user: dict[str, Any]
) -> None:
    response = client.post(
        "/v1/orders",
        json={
            "user_id": user["user_id"],
            "items": [
                {"sku": "AAA", "quantity": 2, "unit_price": "10.00"},
                {"sku": "BBB", "quantity": 1, "unit_price": "15.00"},
            ],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["user_id"] == user["user_id"]
    assert body["total"] == "35.00"
    assert body["status"] == "PENDING"
    assert body["created_at"] == body["updated_at"]


def test_consulta_pedido_existente(client: TestClient, order: dict[str, Any]) -> None:
    response = client.get(f"/v1/orders/{order['order_id']}")

    assert response.status_code == 200
    assert response.json() == order


def test_recusa_pedido_inexistente(client: TestClient) -> None:
    response = client.get(f"/v1/orders/{UUID(int=0)}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "order_not_found"


def test_recusa_pedido_para_usuario_inexistente(client: TestClient) -> None:
    response = client.post(
        "/v1/orders",
        json={
            "user_id": str(UUID(int=0)),
            "items": [{"sku": "AAA", "quantity": 2, "unit_price": "10.00"}],
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "order_user_not_found"


def test_recusa_pedido_com_dados_invalidos(
    client: TestClient, user: dict[str, Any]
) -> None:
    response = client.post(
        "/v1/orders",
        json={
            "user_id": user["user_id"],
            "items": [{"sku": "", "quantity": 0, "unit_price": "0.00"}],
        },
    )

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    fields = {detail["field"] for detail in error["details"]}
    assert fields == {
        "body.items.0.sku",
        "body.items.0.quantity",
        "body.items.0.unit_price",
    }


def test_recusa_pedido_sem_itens(client: TestClient, user: dict[str, Any]) -> None:
    response = client.post(
        "/v1/orders",
        json={"user_id": user["user_id"], "items": []},
    )

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    fields = {detail["field"] for detail in error["details"]}
    assert fields == {"body.items"}
