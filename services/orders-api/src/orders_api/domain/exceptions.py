from uuid import UUID


class DomainError(Exception):
    """Erro genérico de domínio."""

    code = "domain_error"


class UserNotFoundError(DomainError):
    """Erro quando um usuário não é encontrado."""

    code = "user_not_found"

    def __init__(self, user_id: UUID) -> None:
        super().__init__(f"Usuário {user_id} não encontrado.")
        self.user_id = user_id


class EmailAlreadyRegisteredError(DomainError):
    """Erro quando um e-mail já está cadastrado."""

    code = "email_already_registered"

    def __init__(self, email: str) -> None:
        super().__init__(f"E-mail {email} já está cadastrado.")
        self.email = email


class OrderNotFoundError(DomainError):
    """Erro quando um pedido não é encontrado."""

    code = "order_not_found"

    def __init__(self, order_id: UUID) -> None:
        super().__init__(f"Pedido {order_id} não encontrado.")
        self.order_id = order_id


class OrderUserNotFoundError(DomainError):
    """Erro quando um pedido é criado para um usuário que não existe."""

    code = "order_user_not_found"

    def __init__(self, user_id: UUID) -> None:
        super().__init__(f"Usuário {user_id} informado no pedido não foi encontrado.")
        self.user_id = user_id


class InvalidCredentialsError(DomainError):
    """Erro quando o e-mail ou a senha do login estão errados."""

    code = "invalid_credentials"

    def __init__(self) -> None:
        super().__init__("E-mail ou senha incorretos.")


class NotAuthenticatedError(DomainError):
    """Erro quando a requisição não traz um token."""

    code = "not_authenticated"

    def __init__(self) -> None:
        super().__init__("É preciso estar autenticado para acessar este recurso.")


class InvalidAccessTokenError(DomainError):
    """Erro quando o token é inválido ou está expirado."""

    code = "invalid_token"

    def __init__(self) -> None:
        super().__init__("Token inválido ou expirado.")
