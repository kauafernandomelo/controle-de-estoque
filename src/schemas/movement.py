from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.models.enums import MovementType


class MovementCreate(BaseModel):
    """Payload for stock movement creation."""

    product_id: UUID = Field(alias="produto_id")
    movement_type: MovementType = Field(alias="tipo_movimentacao")
    quantity: int = Field(alias="quantidade")
    observation: str | None = Field(default=None, max_length=500, alias="observacao")

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="after")
    def validate_quantity(self) -> "MovementCreate":
        """Ensure movement quantity follows the expected business semantics."""

        if self.movement_type in {MovementType.IN, MovementType.OUT} and self.quantity <= 0:
            raise ValueError("Quantidade deve ser positiva para entrada e saida")
        if self.movement_type == MovementType.ADJUST and self.quantity == 0:
            raise ValueError("Quantidade de ajuste nao pode ser zero")
        return self


class MovementRead(BaseModel):
    """Stock movement response schema."""

    id: UUID
    product_id: UUID = Field(alias="produto_id")
    user_id: UUID = Field(alias="usuario_id")
    movement_type: MovementType = Field(alias="tipo_movimentacao")
    quantity: int = Field(alias="quantidade")
    observation: str | None = Field(alias="observacao")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
