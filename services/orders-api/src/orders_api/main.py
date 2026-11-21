from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, status

from orders_api.core.config import settings
from orders_api.domain.models import User, UserCreate

app = FastAPI(title=settings.app_name, version=settings.app_version)

# "Banco de dados" provisório, em memória: some quando a API reinicia.
users_db: dict[UUID, User] = {}


@app.get("/health")
def health() -> dict[str, str]:
    """Indica se a API está funcionando."""
    return {
        "status": "ok",
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.post("/v1/users", status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate) -> User:
    """Cadastra um usuário."""
    for existing in users_db.values():
        if existing.email == data.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um usuário com este e-mail.",
            )

    user = User(
        user_id=uuid4(),
        name=data.name,
        email=data.email,
        created_at=datetime.now(UTC),
    )
    users_db[user.user_id] = user
    return user


@app.get("/v1/users/{user_id}")
def get_user(user_id: UUID) -> User:
    """Consulta um usuário pelo ID."""
    user = users_db.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )
    return user
