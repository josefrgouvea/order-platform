from uuid import uuid4

import pytest
from orders_api.domain.models import OrderCreate, OrderItem, UserCreate
from pydantic import ValidationError


def test_aceita_usuario_valido() -> None:
    user = UserCreate(name="Jose", email="Jose@exemplo.com")

    assert user.name == "Jose"
    assert user.email == "Jose@exemplo.com"


def test_recusa_email_invalido() -> None:
    with pytest.raises(ValidationError):
        UserCreate(name="Jose", email="sem-arroba")


@pytest.mark.parametrize(
    ("quantity", "unit_price"),
    [
        (0, "10.00"),  # quantidade zero
        (-1, "10.00"),  # quantidade negativa
        (1, "0"),  # preço zero
        (1, "10.999"),  # mais de duas casas decimais
    ],
)
def test_recusa_item_invalido(quantity: int, unit_price: str) -> None:
    with pytest.raises(ValidationError):
        OrderItem(sku="X", quantity=quantity, unit_price=unit_price)


def test_recusa_pedido_vazio() -> None:
    with pytest.raises(ValidationError):
        OrderCreate(user_id=uuid4(), items=[])


def test_ignora_total_enviado() -> None:
    order = OrderCreate.model_validate(
        {
            "user_id": str(uuid4()),
            "items": [{"sku": "X", "quantity": 1, "unit_price": "10.00"}],
            "total": "1.00",
        }
    )

    assert not hasattr(order, "total")


def test_recusa_nome_vazio() -> None:
    with pytest.raises(ValidationError):
        UserCreate(name="", email="jose@exemplo.com")
