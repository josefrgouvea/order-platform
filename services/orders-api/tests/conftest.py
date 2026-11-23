from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from orders_api.api.dependencies import get_order_repository, get_user_repository
from orders_api.main import app
from orders_api.repositories.orders import InMemoryOrderRepository
from orders_api.repositories.users import InMemoryUserRepository


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Um cliente de testes com repositórios novos, vazios, só para este teste."""
    users = InMemoryUserRepository()
    orders = InMemoryOrderRepository()
    app.dependency_overrides[get_user_repository] = lambda: users
    app.dependency_overrides[get_order_repository] = lambda: orders

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def user(client: TestClient) -> dict[str, Any]:
    """Um usuário já cadastrado, para os testes que precisam de um."""
    response = client.post(
        "/v1/users", json={"name": "Jose", "email": "jose@exemplo.com"}
    )
    return response.json()


@pytest.fixture
def order(client: TestClient, user: dict[str, Any]) -> dict[str, Any]:
    """Um pedido já cadastrado, para os testes que precisam de um."""
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
    return response.json()
