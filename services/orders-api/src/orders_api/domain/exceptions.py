from uuid import UUID


class DomainError(Exception):
    """Erro genérico de domínio."""


class UserNotFoundError(DomainError):
    """Erro quando um usuário não é encontrado."""

    def __init__(self, user_id: UUID) -> None:
        super().__init__(f"Usuário {user_id} não encontrado.")
        self.user_id = user_id


class EmailAlreadyRegisteredError(DomainError):
    """Erro quando um e-mail já está cadastrado."""

    def __init__(self, email: str) -> None:
        super().__init__(f"E-mail {email} já está cadastrado.")
        self.email = email


class OrderNotFoundError(DomainError):
    """Erro quando um pedido não é encontrado."""

    def __init__(self, order_id: UUID) -> None:
        super().__init__(f"Pedido {order_id} não encontrado.")
        self.order_id = order_id
