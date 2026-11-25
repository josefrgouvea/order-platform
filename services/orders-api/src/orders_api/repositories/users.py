from typing import Any, Protocol
from uuid import UUID

from boto3.dynamodb.conditions import Key

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


class DynamoUserRepository:
    """Guarda os usuários na tabela users do DynamoDB."""

    def __init__(self, table: Any) -> None:
        self._table = table

    def add(self, user: User) -> None:
        self._table.put_item(Item=user.model_dump(mode="json"))

    def get(self, user_id: UUID) -> User | None:
        response = self._table.get_item(Key={"user_id": str(user_id)})
        item = response.get("Item")
        if item is None:
            return None
        return User.model_validate(item)

    def get_by_email(self, email: str) -> User | None:
        response = self._table.query(
            IndexName="email-index",
            KeyConditionExpression=Key("email").eq(email),
        )
        items = response["Items"]
        if not items:
            return None
        return User.model_validate(items[0])
