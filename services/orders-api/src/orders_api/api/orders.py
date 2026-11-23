from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from orders_api.api.dependencies import OrderServiceDep
from orders_api.domain.exceptions import OrderNotFoundError, UserNotFoundError
from orders_api.domain.models import Order, OrderCreate

router = APIRouter(prefix="/v1/orders", tags=["orders"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_order(data: OrderCreate, service: OrderServiceDep) -> Order:
    """Cria um pedido para um usuário existente."""
    try:
        return service.create_order(data)
    except UserNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)
        ) from error


@router.get("/{order_id}")
def get_order(order_id: UUID, service: OrderServiceDep) -> Order:
    """Consulta um pedido pelo ID."""
    try:
        return service.get_order(order_id)
    except OrderNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
