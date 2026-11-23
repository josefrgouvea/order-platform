from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from orders_api.domain.exceptions import (
    DomainError,
    EmailAlreadyRegisteredError,
    OrderNotFoundError,
    OrderUserNotFoundError,
    UserNotFoundError,
)

# Qual status HTTP cada erro de negócio vira.
STATUS_BY_ERROR: dict[type[DomainError], int] = {
    UserNotFoundError: status.HTTP_404_NOT_FOUND,
    OrderNotFoundError: status.HTTP_404_NOT_FOUND,
    EmailAlreadyRegisteredError: status.HTTP_409_CONFLICT,
    OrderUserNotFoundError: status.HTTP_422_UNPROCESSABLE_CONTENT,
}


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: list[dict[str, str]] | None = None,
) -> JSONResponse:
    """Monta uma resposta de erro no formato padrão da API."""
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "details": details or []}},
    )


async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
    status_code = STATUS_BY_ERROR.get(type(exc), status.HTTP_400_BAD_REQUEST)
    return error_response(status_code, exc.code, str(exc))


async def handle_validation_error(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    details = [
        {
            "field": ".".join(str(part) for part in error["loc"]),
            "type": error["type"],
            "message": error["msg"],
        }
        for error in exc.errors()
    ]
    return error_response(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "validation_error",
        "Os dados enviados são inválidos.",
        details,
    )


async def handle_http_error(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    return error_response(exc.status_code, "http_error", str(exc.detail))


async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    return error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "internal_error",
        "Erro interno. Tente novamente mais tarde.",
    )


def register_error_handlers(app: FastAPI) -> None:
    """Registra todos os tratadores de erro na aplicação."""
    app.add_exception_handler(DomainError, handle_domain_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(StarletteHTTPException, handle_http_error)
    app.add_exception_handler(Exception, handle_unexpected_error)
