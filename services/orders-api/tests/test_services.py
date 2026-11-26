from decimal import Decimal

from orders_api.core.security import verify_password
from orders_api.domain.models import OrderItem, UserCreate
from orders_api.domain.services import UserService, calculate_total
from orders_api.repositories.users import InMemoryUserRepository


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


def test_guarda_apenas_o_hash_da_senha() -> None:
    repository = InMemoryUserRepository()
    service = UserService(repository)
    senha = "senha-do-jose"

    created = service.create_user(
        UserCreate(name="Jose", email="jose@exemplo.com", password=senha)
    )

    stored = repository.get(created.user_id)
    assert stored is not None
    assert stored.password_hash != senha
    assert verify_password(senha, stored.password_hash)
