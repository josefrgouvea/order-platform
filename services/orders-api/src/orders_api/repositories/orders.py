from typing import Any, Protocol
from uuid import UUID

from orders_api.domain.models import Order


class OrderRepository(Protocol):
    """O que qualquer repositório de pedidos deve implementar."""

    def add(self, order: Order) -> None:
        """Guarda um pedido ao repositório."""

    def get(self, order_id: UUID) -> Order | None:
        """Consulta um pedido pelo ID. Devolve None se não existir."""


class InMemoryOrderRepository:
    """Repositório de pedidos em memória, para testes e desenvolvimento."""

    def __init__(self) -> None:
        self._orders: dict[UUID, Order] = {}

    def add(self, order: Order) -> None:
        self._orders[order.order_id] = order

    def get(self, order_id: UUID) -> Order | None:
        return self._orders.get(order_id)


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
