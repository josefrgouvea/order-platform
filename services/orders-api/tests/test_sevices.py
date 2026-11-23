from decimal import Decimal

from orders_api.domain.models import OrderItem
from orders_api.domain.services import calculate_total


def test_calcula_total_soma() -> None:
    items = [
        OrderItem(sku="AAA-001", quantity=2, unit_price=Decimal("27.90")),
        OrderItem(sku="BBB-002", quantity=1, unit_price=Decimal("150.30")),
    ]

    total = calculate_total(items)

    assert total == Decimal("206.10")


def test_calcula_total_sem_erro_de_float() -> None:
    items = [
        OrderItem(sku="A", quantity=1, unit_price=Decimal("0.10")),
        OrderItem(sku="B", quantity=1, unit_price=Decimal("0.20")),
    ]

    assert calculate_total(items) == Decimal("0.30")


def test_calcula_total_de_lista_vazia() -> None:
    assert calculate_total([]) == Decimal("0")
