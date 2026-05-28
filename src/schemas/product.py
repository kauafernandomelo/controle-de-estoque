from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductBase(BaseModel):
    name: str = Field(min_length=2, max_length=160, alias="nome")
    sku: str = Field(min_length=2, max_length=64)
    description: str | None = Field(default=None, alias="descricao")
    category: str = Field(min_length=2, max_length=120, alias="categoria")
    ean: str | None = Field(default=None, max_length=13)
    cost_price: Decimal = Field(ge=0, decimal_places=2, alias="preco_custo")
    sale_price: Decimal = Field(ge=0, decimal_places=2, alias="preco_venda")
    stock_quantity: int = Field(default=0, ge=0, alias="quantidade_estoque")
    minimum_stock: int = Field(default=0, ge=0, alias="estoque_minimo")
    active: bool = Field(default=True, alias="ativo")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, value: str) -> str:
        return value.strip().upper()


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160, alias="nome")
    sku: str | None = Field(default=None, min_length=2, max_length=64)
    description: str | None = Field(default=None, alias="descricao")
    category: str | None = Field(default=None, min_length=2, max_length=120, alias="categoria")
    ean: str | None = Field(default=None, max_length=13)
    cost_price: Decimal | None = Field(default=None, ge=0, decimal_places=2, alias="preco_custo")
    sale_price: Decimal | None = Field(default=None, ge=0, decimal_places=2, alias="preco_venda")
    stock_quantity: int | None = Field(default=None, ge=0, alias="quantidade_estoque")
    minimum_stock: int | None = Field(default=None, ge=0, alias="estoque_minimo")
    active: bool | None = Field(default=None, alias="ativo")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, value: str | None) -> str | None:
        return value.strip().upper() if value else value


class ProductRead(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
