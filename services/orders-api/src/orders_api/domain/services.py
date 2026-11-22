from datetime import UTC, datetime
from uuid import UUID, uuid4

from orders_api.domain.exceptions import EmailAlreadyRegisteredError, UserNotFoundError
from orders_api.domain.models import User, UserCreate
from orders_api.repositories.users import UserRepository


class UserService:
    """Regras de negócio relacionadas a usuários."""

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def create_user(self, data: UserCreate) -> User:
        if self._repository.get_by_email(data.email) is not None:
            raise EmailAlreadyRegisteredError(data.email)

        user = User(
            user_id=uuid4(),
            name=data.name,
            email=data.email,
            created_at=datetime.now(UTC),
        )
        self._repository.add(user)
        return user

    def get_user(self, user_id: UUID) -> User:
        user = self._repository.get(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return user
