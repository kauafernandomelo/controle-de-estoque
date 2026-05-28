from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.enums import MovementType


class LowStockProduct(BaseModel):
    """Product below minimum stock report item."""

    id: UUID
    name: str = Field(alias="nome")
    sku: str
    stock_quantity: int = Field(alias="quantidade_estoque")
    minimum_stock: int = Field(alias="estoque_minimo")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class MostMovedProduct(BaseModel):
    """Most moved product report item."""

    product_id: UUID = Field(alias="produto_id")
    name: str = Field(alias="nome")
    sku: str
    total_quantity: int = Field(alias="quantidade_total")

    model_config = ConfigDict(populate_by_name=True)


class PeriodMovementTotal(BaseModel):
    """Movement total grouped by type in a given period."""

    movement_type: MovementType = Field(alias="tipo_movimentacao")
    total_quantity: int = Field(alias="quantidade_total")

    model_config = ConfigDict(populate_by_name=True)


class InventoryTotals(BaseModel):
    """Financial and quantitative inventory totals."""

    total_stock_value: Decimal = Field(alias="valor_total_estoque")
    total_items: int = Field(alias="quantidade_total_itens")

    model_config = ConfigDict(populate_by_name=True)
