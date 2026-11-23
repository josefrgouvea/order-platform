from typing import Annotated

from fastapi import Depends

from orders_api.domain.services import OrderService, UserService
from orders_api.repositories.orders import InMemoryOrderRepository, OrderRepository
from orders_api.repositories.users import InMemoryUserRepository, UserRepository

# Uma única instância, criada quando a API sobe: todas as requisições
# usam o mesmo "banco de dados".
_user_repository = InMemoryUserRepository()
_order_repository = InMemoryOrderRepository()


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


OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]
