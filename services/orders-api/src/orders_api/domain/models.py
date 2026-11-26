from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

# ---------- Usuários ----------


class UserCreate(BaseModel):
    """Dados que o cliente envia para cadastrar um usuário."""

    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class User(BaseModel):
    """Um usuário como a API o devolve."""

    user_id: UUID
    name: str
    email: EmailStr
    created_at: datetime


class UserInDB(User):
    """Um usuário como fica guardado no banco, com o hash da senha."""

    password_hash: str


# ---------- Pedidos ----------


class OrderStatus(StrEnum):
    PENDING = "PENDING"
    PAID = "PAID"
    PAYMENT_FAILED = "PAYMENT_FAILED"


class OrderItem(BaseModel):
    sku: str = Field(min_length=1)
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(gt=0, decimal_places=2)


class OrderCreate(BaseModel):
    """Dados que o cliente envia para criar um pedido."""

    user_id: UUID
    items: list[OrderItem] = Field(min_length=1)


class Order(BaseModel):
    """Um pedido como a API o devolve."""

    order_id: UUID
    user_id: UUID
    items: list[OrderItem]
    total: Decimal
    status: OrderStatus
    created_at: datetime
    updated_at: datetime


# ---------- Autenticação ----------


class TokenResponse(BaseModel):
    """A resposta do login."""

    access_token: str
    token_type: str = "bearer"
