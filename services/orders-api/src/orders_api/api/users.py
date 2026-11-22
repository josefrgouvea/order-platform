from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from orders_api.api.dependencies import UserServiceDep
from orders_api.domain.exceptions import EmailAlreadyRegisteredError, UserNotFoundError
from orders_api.domain.models import User, UserCreate

router = APIRouter(prefix="/v1/users", tags=["users"])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, service: UserServiceDep) -> User:
    """Cadastra um usuário."""
    try:
        return service.create_user(data)
    except EmailAlreadyRegisteredError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(error)
        ) from error


@router.get("/{user_id}")
def get_user(user_id: UUID, service: UserServiceDep) -> User:
    """Consulta um usuário pelo ID."""
    try:
        return service.get_user(user_id)
    except UserNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
        ) from error
