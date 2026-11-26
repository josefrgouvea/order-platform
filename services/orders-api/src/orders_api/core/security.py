from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from pwdlib import PasswordHash

from orders_api.core.config import settings

_password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Gera o hash de uma senha, com SAL, usando o Argon2."""
    return _password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Confere se a senha corresponde ao hash guardado."""
    return _password_hash.verify(password, hashed)


def create_access_token(user_id: UUID) -> str:
    """Cria um JWT de acesso para o usuário, com expiração."""
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )
