from typing import Protocol
from uuid import UUID

from orders_api.domain.models import User


class UserRepository(Protocol):
    """O que qualquer repositório de usuários deve implementar."""

    def add(self, user: User) -> None:
        """Guarda um usuário ao repositório."""

    def get(self, user_id: UUID) -> User | None:
        """Consulta um usuário pelo ID. Devolve None se não existir."""

    def get_by_email(self, email: str) -> User | None:
        """Consulta um usuário pelo e-mail. Devolve None se não existir."""


class InMemoryUserRepository:
    """Repositório de usuários em memória, para testes e desenvolvimento."""

    def __init__(self) -> None:
        self._users: dict[UUID, User] = {}

    def add(self, user: User) -> None:
        self._users[user.user_id] = user

    def get(self, user_id: UUID) -> User | None:
        return self._users.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        for user in self._users.values():
            if user.email == email:
                return user
        return None
