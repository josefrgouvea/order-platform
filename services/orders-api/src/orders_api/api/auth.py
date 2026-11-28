from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from orders_api.api.dependencies import AuthServiceDep
from orders_api.domain.models import TokenResponse

router = APIRouter(prefix="/v1/auth", tags=["auth"])


@router.post("/login")
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: AuthServiceDep,
) -> TokenResponse:
    """Confere e-mail e senha e devolve um token de acesso."""
    token = service.login(form.username, form.password)
    return TokenResponse(access_token=token)
