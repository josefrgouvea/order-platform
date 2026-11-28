from uuid import UUID

from fastapi import APIRouter, status

from orders_api.api.dependencies import CurrentUserId, OrderServiceDep, UserServiceDep
from orders_api.domain.models import Order, User, UserCreate

router = APIRouter(prefix="/v1/users", tags=["users"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, service: UserServiceDep) -> User:
    """Cadastra um usuário."""
    return service.create_user(data)


@router.get("/{user_id}")
def get_user(
    user_id: UUID, service: UserServiceDep, current_user_id: CurrentUserId
) -> User:
    """Consulta os dados do próprio usuário."""
    return service.get_user(user_id, requester_id=current_user_id)


@router.get("/{user_id}/orders")
def list_user_orders(
    user_id: UUID, service: OrderServiceDep, current_user_id: CurrentUserId
) -> list[Order]:
    """Lista os pedidos do próprio usuário, mais recentes primeiro."""
    return service.list_user_orders(user_id, requester_id=current_user_id)
