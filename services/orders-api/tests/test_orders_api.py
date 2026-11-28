from typing import Any
from uuid import UUID

from fastapi.testclient import TestClient
from orders_api.core.security import create_access_token

ITEMS = [
    {"sku": "AAA", "quantity": 2, "unit_price": "10.00"},
    {"sku": "BBB", "quantity": 1, "unit_price": "15.00"},
]


def test_cria_pedido_para_o_usuario_do_token(
    client: TestClient, user: dict[str, Any], auth_headers: dict[str, str]
) -> None:
    response = client.post("/v1/orders", json={"items": ITEMS}, headers=auth_headers)

    assert response.status_code == 201
    body = response.json()
    assert body["user_id"] == user["user_id"]
    assert body["total"] == "35.00"
    assert body["status"] == "PENDING"
    assert body["created_at"] == body["updated_at"]


def test_dono_do_pedido_vem_do_token_e_nao_do_corpo(
    client: TestClient,
    user: dict[str, Any],
    other_user: dict[str, Any],
    auth_headers: dict[str, str],
) -> None:
    # A Ana tenta criar um pedido em nome do Bruno
    response = client.post(
        "/v1/orders",
        json={"user_id": other_user["user_id"], "items": ITEMS},
        headers=auth_headers,
    )

    assert response.status_code == 201
    assert response.json()["user_id"] == user["user_id"]


def test_consulta_pedido_existente(
    client: TestClient, order: dict[str, Any], auth_headers: dict[str, str]
) -> None:
    response = client.get(f"/v1/orders/{order['order_id']}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == order


def test_recusa_consulta_de_pedido_de_outro_usuario(
    client: TestClient, order: dict[str, Any], other_auth_headers: dict[str, str]
) -> None:
    response = client.get(f"/v1/orders/{order['order_id']}", headers=other_auth_headers)

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "forbidden"


def test_recusa_pedido_inexistente(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.get(f"/v1/orders/{UUID(int=0)}", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "order_not_found"


def test_recusa_pedido_de_usuario_do_token_inexistente(client: TestClient) -> None:
    headers = {"Authorization": f"Bearer {create_access_token(UUID(int=0))}"}

    response = client.post("/v1/orders", json={"items": ITEMS}, headers=headers)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "user_not_found"


def test_recusa_pedido_com_dados_invalidos(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post(
        "/v1/orders",
        json={"items": [{"sku": "", "quantity": 0, "unit_price": "0.00"}]},
        headers=auth_headers,
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


def test_recusa_pedido_sem_itens(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post("/v1/orders", json={"items": []}, headers=auth_headers)

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    fields = {detail["field"] for detail in error["details"]}
    assert fields == {"body.items"}


def test_recusa_id_de_pedido_invalido(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.get("/v1/orders/invalid-uuid", headers=auth_headers)

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    fields = {detail["field"] for detail in error["details"]}
    assert fields == {"path.order_id"}


def test_lista_pedidos_de_usuario(
    client: TestClient, user: dict[str, Any], auth_headers: dict[str, str]
) -> None:
    first = client.post("/v1/orders", json={"items": ITEMS}, headers=auth_headers)
    second = client.post("/v1/orders", json={"items": ITEMS}, headers=auth_headers)

    response = client.get(f"/v1/users/{user['user_id']}/orders", headers=auth_headers)

    assert response.status_code == 200
    ids = [order["order_id"] for order in response.json()]
    assert ids == [second.json()["order_id"], first.json()["order_id"]]


def test_lista_apenas_os_pedidos_do_proprio_usuario(
    client: TestClient,
    user: dict[str, Any],
    other_user: dict[str, Any],
    auth_headers: dict[str, str],
    other_auth_headers: dict[str, str],
) -> None:
    pedido_da_ana = client.post(
        "/v1/orders", json={"items": ITEMS}, headers=auth_headers
    )
    pedido_do_bruno = client.post(
        "/v1/orders", json={"items": ITEMS}, headers=other_auth_headers
    )

    response = client.get(f"/v1/users/{user['user_id']}/orders", headers=auth_headers)
    assert response.status_code == 200
    ids = [order["order_id"] for order in response.json()]
    assert ids == [pedido_da_ana.json()["order_id"]]

    response = client.get(
        f"/v1/users/{other_user['user_id']}/orders", headers=other_auth_headers
    )
    assert response.status_code == 200
    ids = [order["order_id"] for order in response.json()]
    assert ids == [pedido_do_bruno.json()["order_id"]]


def test_recusa_listar_pedidos_de_outro_usuario(
    client: TestClient, other_user: dict[str, Any], auth_headers: dict[str, str]
) -> None:
    response = client.get(
        f"/v1/users/{other_user['user_id']}/orders", headers=auth_headers
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "forbidden"


def test_lista_vazia_para_usuario_sem_pedidos(
    client: TestClient, user: dict[str, Any], auth_headers: dict[str, str]
) -> None:
    response = client.get(f"/v1/users/{user['user_id']}/orders", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_lista_de_pedidos_de_usuario_do_token_inexistente(
    client: TestClient,
) -> None:
    user_id = UUID(int=0)
    headers = {"Authorization": f"Bearer {create_access_token(user_id)}"}

    response = client.get(f"/v1/users/{user_id}/orders", headers=headers)

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "user_not_found"
