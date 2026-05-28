from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.database.session import get_db
from src.models.user import User
from src.schemas.report import InventoryTotals, LowStockProduct
from src.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/low-stock", response_model=list[LowStockProduct])
def low_stock_products(
    _: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[LowStockProduct]:
    return ReportService(db).low_stock_products()


@router.get("/inventory-totals", response_model=InventoryTotals)
def inventory_totals(
    _: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> InventoryTotals:
    return ReportService(db).inventory_totals()
