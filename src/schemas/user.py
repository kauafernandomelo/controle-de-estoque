from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.models.enums import UserRole


class UserRegister(BaseModel):
    """Payload for public user registration."""

    name: str = Field(min_length=2, max_length=120, alias="nome")
    email: EmailStr
    password: str = Field(min_length=8, max_length=128, alias="senha")

    model_config = ConfigDict(populate_by_name=True)


class UserCreate(UserRegister):
    """Payload for administrator-created users."""

    role: UserRole = Field(default=UserRole.OPERATOR, alias="perfil")


class UserRead(BaseModel):
    """User response schema."""

    id: UUID
    name: str = Field(alias="nome")
    email: EmailStr
    role: UserRole = Field(alias="perfil")
    active: bool = Field(alias="ativo")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
