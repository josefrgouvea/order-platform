from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from orders_api.core.config import settings
from orders_api.core.dynamodb import get_dynamodb_resource
from orders_api.core.security import decode_access_token
from orders_api.domain.exceptions import NotAuthenticatedError
from orders_api.domain.services import AuthService, OrderService, UserService
from orders_api.repositories.orders import DynamoOrderRepository, OrderRepository
from orders_api.repositories.users import DynamoUserRepository, UserRepository

# A conexão com o DynamoDB e os repositórios, criados uma vez só, quando a API sobe.
_dynamodb = get_dynamodb_resource()
_user_repository = DynamoUserRepository(_dynamodb.Table(settings.users_table))
_order_repository = DynamoOrderRepository(_dynamodb.Table(settings.orders_table))


def get_user_repository() -> UserRepository:
    return _user_repository


def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(repository)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_order_repository() -> OrderRepository:
    return _order_repository


def get_order_service(
    orders: Annotated[OrderRepository, Depends(get_order_repository)],
    users: Annotated[UserRepository, Depends(get_user_repository)],
) -> OrderService:
    return OrderService(orders, users)


def get_auth_service(
    users: Annotated[UserRepository, Depends(get_user_repository)],
) -> AuthService:
    return AuthService(users)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login", auto_error=False)


def get_current_user_id(
    token: Annotated[str | None, Depends(oauth2_scheme)],
) -> UUID:
    """Identifica o usuário da requisição, pelo token."""
    if token is None:
        raise NotAuthenticatedError()
    return decode_access_token(token)


CurrentUserId = Annotated[UUID, Depends(get_current_user_id)]
