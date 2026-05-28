from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.database.session import get_db
from src.models.enums import MovementType
from src.models.user import User
from src.schemas.report import (
    InventoryTotals,
    LowStockProduct,
    MostMovedProduct,
    PeriodMovementTotal,
)
from src.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/low-stock", response_model=list[LowStockProduct])
def low_stock_products(
    _: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> list[LowStockProduct]:
    """Report products below or equal to minimum stock."""

    return ReportService(db).low_stock_products()


@router.get("/most-moved", response_model=list[MostMovedProduct])
def most_moved_products(
    limit: int = Query(default=10, ge=1, le=100),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MostMovedProduct]:
    """Report products with highest movement volume."""

    return ReportService(db).most_moved_products(limit=limit)


@router.get("/entries", response_model=PeriodMovementTotal)
def entries_by_period(
    start_at: datetime,
    end_at: datetime,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PeriodMovementTotal:
    """Report stock entries by period."""

    return ReportService(db).movement_total_by_period(MovementType.IN, start_at, end_at)


@router.get("/exits", response_model=PeriodMovementTotal)
def exits_by_period(
    start_at: datetime,
    end_at: datetime,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PeriodMovementTotal:
    """Report stock exits by period."""

    return ReportService(db).movement_total_by_period(MovementType.OUT, start_at, end_at)


@router.get("/inventory-totals", response_model=InventoryTotals)
def inventory_totals(
    _: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> InventoryTotals:
    """Report total stock value and total quantity of items."""

    return ReportService(db).inventory_totals()
