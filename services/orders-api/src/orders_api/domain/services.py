from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from orders_api.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from orders_api.domain.exceptions import (
    EmailAlreadyRegisteredError,
    ForbiddenError,
    InvalidCredentialsError,
    OrderNotFoundError,
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


def ensure_same_user(owner_id: UUID, requester_id: UUID) -> None:
    """Garante que cada usuário só acesse os próprios dados."""
    if owner_id != requester_id:
        raise ForbiddenError()


class UserService:
    """Regras de negócio de usuários."""

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

    def get_user(self, user_id: UUID, requester_id: UUID) -> UserInDB:
        ensure_same_user(user_id, requester_id)
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

    def create_order(self, data: OrderCreate, user_id: UUID) -> Order:
        if self._users.get(user_id) is None:
            raise UserNotFoundError(user_id)

        now = datetime.now(UTC)
        order = Order(
            order_id=uuid4(),
            user_id=user_id,
            items=data.items,
            total=calculate_total(data.items),
            status=OrderStatus.PENDING,
            created_at=now,
            updated_at=now,
        )
        self._orders.add(order)
        return order

    def get_order(self, order_id: UUID, requester_id: UUID) -> Order:
        order = self._orders.get(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        ensure_same_user(order.user_id, requester_id)
        return order

    def list_user_orders(self, user_id: UUID, requester_id: UUID) -> list[Order]:
        ensure_same_user(user_id, requester_id)
        if self._users.get(user_id) is None:
            raise UserNotFoundError(user_id)
        return self._orders.list_by_user(user_id)


class AuthService:
    """Regras de autenticação."""

    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def login(self, email: str, password: str) -> str:
        user = self._users.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        return create_access_token(user.user_id)
