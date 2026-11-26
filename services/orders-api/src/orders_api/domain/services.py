from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from orders_api.core.security import hash_password
from orders_api.domain.exceptions import (
    EmailAlreadyRegisteredError,
    OrderNotFoundError,
    OrderUserNotFoundError,
    UserNotFoundError,
)
from orders_api.domain.models import (
    Order,
    OrderCreate,
    OrderItem,
    OrderStatus,
    UserCreate,
    UserInDB,
)
from orders_api.repositories.orders import OrderRepository
from orders_api.repositories.users import UserRepository


class UserService:
    """Regras de negócio relacionadas a usuários."""

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def create_user(self, data: UserCreate) -> UserInDB:
        if self._repository.get_by_email(data.email) is not None:
            raise EmailAlreadyRegisteredError(data.email)

        user = UserInDB(
            user_id=uuid4(),
            name=data.name,
            email=data.email,
            created_at=datetime.now(UTC),
            password_hash=hash_password(data.password),
        )
        self._repository.add(user)
        return user

    def get_user(self, user_id: UUID) -> UserInDB:
        user = self._repository.get(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return user


def calculate_total(items: list[OrderItem]) -> Decimal:
    """Soma quantidade x preço unitário de cada item."""
    return sum((item.unit_price * item.quantity for item in items), Decimal("0"))


class OrderService:
    """Regras de negócio de pedidos."""

    def __init__(self, orders: OrderRepository, users: UserRepository) -> None:
        self._orders = orders
        self._users = users

    def create_order(self, data: OrderCreate) -> Order:
        if self._users.get(data.user_id) is None:
            raise OrderUserNotFoundError(data.user_id)

        now = datetime.now(UTC)
        order = Order(
            order_id=uuid4(),
            user_id=data.user_id,
            items=data.items,
            total=calculate_total(data.items),
            status=OrderStatus.PENDING,
            created_at=now,
            updated_at=now,
        )
        self._orders.add(order)
        return order

    def get_order(self, order_id: UUID) -> Order:
        order = self._orders.get(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        return order

    def list_user_orders(self, user_id: UUID) -> list[Order]:
        if self._users.get(user_id) is None:
            raise UserNotFoundError(user_id)
        return self._orders.list_by_user(user_id)
