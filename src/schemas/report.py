from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class LowStockProduct(BaseModel):
    id: UUID
    name: str = Field(alias="nome")
    sku: str
    stock_quantity: int = Field(alias="quantidade_estoque")
    minimum_stock: int = Field(alias="estoque_minimo")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class InventoryTotals(BaseModel):
    total_stock_value: Decimal = Field(alias="valor_total_estoque")
    total_items: int = Field(alias="quantidade_total_itens")

    model_config = ConfigDict(populate_by_name=True)
