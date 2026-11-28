from uuid import UUID

from fastapi import APIRouter, status

from orders_api.api.dependencies import CurrentUserId, OrderServiceDep
from orders_api.domain.models import Order, OrderCreate

router = APIRouter(prefix="/v1/orders", tags=["orders"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_order(
    data: OrderCreate, service: OrderServiceDep, current_user_id: CurrentUserId
) -> Order:
    """Cria um pedido para um usuário existente."""
    return service.create_order(data)


@router.get("/{order_id}")
def get_order(
    order_id: UUID, service: OrderServiceDep, current_user_id: CurrentUserId
) -> Order:
    """Consulta um pedido pelo ID."""
    return service.get_order(order_id)
