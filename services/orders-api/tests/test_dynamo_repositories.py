from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import boto3
import pytest
from moto import mock_aws
from orders_api.domain.models import Order, OrderItem, OrderStatus, User
from orders_api.repositories.orders import DynamoOrderRepository
from orders_api.repositories.users import DynamoUserRepository


@pytest.fixture
def dynamodb(monkeypatch: pytest.MonkeyPatch) -> Iterator[Any]:
    """Um DynamoDB falso, do moto, com as tabelas do projeto criadas."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")

    with mock_aws():
        resource = boto3.resource("dynamodb", region_name="us-east-1")
        resource.create_table(
            TableName="users",
            KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "email", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "email-index",
                    "KeySchema": [{"AttributeName": "email", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        resource.create_table(
            TableName="orders",
            KeySchema=[{"AttributeName": "order_id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "order_id", "AttributeType": "S"},
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "created_at", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "user-orders-index",
                    "KeySchema": [
                        {"AttributeName": "user_id", "KeyType": "HASH"},
                        {"AttributeName": "created_at", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                }
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        yield resource


@pytest.fixture
def user_repository(dynamodb: Any) -> DynamoUserRepository:
    return DynamoUserRepository(dynamodb.Table("users"))


@pytest.fixture
def order_repository(dynamodb: Any) -> DynamoOrderRepository:
    return DynamoOrderRepository(dynamodb.Table("orders"))


def make_user(email: str = "ana@exemplo.com") -> User:
    return User(user_id=uuid4(), name="Ana", email=email, created_at=datetime.now(UTC))


def make_order(user_id: UUID, created_at: datetime | None = None) -> Order:
    when = created_at or datetime.now(UTC)
    return Order(
        order_id=uuid4(),
        user_id=user_id,
        items=[OrderItem(sku="BOOK-001", quantity=2, unit_price=Decimal("49.90"))],
        total=Decimal("99.80"),
        status=OrderStatus.PENDING,
        created_at=when,
        updated_at=when,
    )


def test_grava_e_le_usuario(user_repository: DynamoUserRepository) -> None:
    user = make_user()

    user_repository.add(user)

    assert user_repository.get(user.user_id) == user


def test_usuario_inexistente_devolve_none(
    user_repository: DynamoUserRepository,
) -> None:
    assert user_repository.get(uuid4()) is None


def test_encontra_usuario_por_email(user_repository: DynamoUserRepository) -> None:
    user = make_user()

    user_repository.add(user)

    assert user_repository.get_by_email(user.email) == user


def test_usuario_por_email_inexistente_devolve_none(
    user_repository: DynamoUserRepository,
) -> None:
    assert user_repository.get_by_email("inexistente@exemplo.com") is None


def test_grava_e_le_pedido(order_repository: DynamoOrderRepository) -> None:
    user_id = uuid4()
    order = make_order(user_id)

    order_repository.add(order)

    assert order_repository.get(order.order_id) == order


def test_lista_pedidos_do_mais_recente_para_o_mais_antigo(
    order_repository: DynamoOrderRepository,
) -> None:
    user_id = uuid4()
    now = datetime.now(UTC)
    antigo = make_order(user_id, created_at=now - timedelta(days=1))
    recente = make_order(user_id, created_at=now)

    order_repository.add(recente)
    order_repository.add(antigo)

    orders = order_repository.list_by_user(user_id)

    assert orders == [recente, antigo]


def test_lista_apenas_os_pedidos_do_usuario(
    order_repository: DynamoOrderRepository,
) -> None:
    user_id = uuid4()
    outro_user_id = uuid4()
    order1 = make_order(user_id)
    order2 = make_order(outro_user_id)

    order_repository.add(order1)
    order_repository.add(order2)

    orders = order_repository.list_by_user(user_id)

    assert orders == [order1]
