from typing import Annotated

from fastapi import Depends

from orders_api.domain.services import UserService
from orders_api.repositories.users import InMemoryUserRepository, UserRepository

# Uma única instância, criada quando a API sobe: todas as requisições
# usam o mesmo "banco de dados".
_user_repository = InMemoryUserRepository()


def get_user_repository() -> UserRepository:
    return _user_repository


def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(repository)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]