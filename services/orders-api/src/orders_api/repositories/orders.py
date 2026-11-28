from typing import Any, Protocol
from uuid import UUID

from boto3.dynamodb.conditions import Key

from orders_api.domain.models import Order


class OrderRepository(Protocol):
    """O que qualquer repositório de pedidos deve implementar."""

    def add(self, order: Order) -> None:
        """Guarda um pedido ao repositório."""

    def get(self, order_id: UUID) -> Order | None:
        """Consulta um pedido pelo ID. Devolve None se não existir."""

    def list_by_user(self, user_id: UUID) -> list[Order]:
        """Lista os pedidos de um usuário, do mais recente para o mais antigo."""


class InMemoryOrderRepository:
    """Repositório de pedidos em memória, para testes e desenvolvimento."""

    def __init__(self) -> None:
        self._orders: dict[UUID, Order] = {}

    def add(self, order: Order) -> None:
        self._orders[order.order_id] = order

    def get(self, order_id: UUID) -> Order | None:
        return self._orders.get(order_id)

    def list_by_user(self, user_id: UUID) -> list[Order]:
        orders = [order for order in self._orders.values() if order.user_id == user_id]
        return sorted(orders, key=lambda order: order.created_at, reverse=True)


class DynamoOrderRepository:
    """Guarda os pedidos na tabela orders do DynamoDB."""

    def __init__(self, table: Any) -> None:
        self._table = table

    def add(self, order: Order) -> None:
        self._table.put_item(Item=order.model_dump(mode="json"))

    def get(self, order_id: UUID) -> Order | None:
        response = self._table.get_item(Key={"order_id": str(order_id)})
        item = response.get("Item")
        if item is None:
            return None
        return Order.model_validate(item)

    def list_by_user(self, user_id: UUID) -> list[Order]:
        response = self._table.query(
            IndexName="user-orders-index",
            KeyConditionExpression=Key("user_id").eq(str(user_id)),
            ScanIndexForward=False,
        )
        return [Order.model_validate(item) for item in response["Items"]]
