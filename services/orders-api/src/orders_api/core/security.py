from pwdlib import PasswordHash

_password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Gera o hash de uma senha, com SAL, usando o Argon2."""
    return _password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Confere se a senha corresponde ao hash guardado."""
    return _password_hash.verify(password, hashed)
