from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from src.api.deps import get_current_user, require_admin
from src.database.session import get_db
from src.models.user import User
from src.schemas.product import ProductCreate, ProductRead, ProductUpdate
from src.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProductRead:
    """Create a product with unique SKU."""

    return ProductService(db).create(payload)


@router.get("", response_model=list[ProductRead])
def list_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    nome: str | None = Query(default=None, min_length=2),
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ProductRead]:
    """List products and optionally search by name."""

    return ProductService(db).list(skip=skip, limit=limit, name=nome)


@router.get("/sku/{sku}", response_model=ProductRead)
def get_product_by_sku(
    sku: str,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProductRead:
    """Find a product by SKU."""

    return ProductService(db).get_by_sku(sku)


@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    product_id: UUID,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProductRead:
    """Find a product by id."""

    return ProductService(db).get(product_id)


@router.patch("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: UUID,
    payload: ProductUpdate,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProductRead:
    """Update product data."""

    return ProductService(db).update(product_id, payload)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: UUID,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> Response:
    """Delete a product without movement history. Administrator only."""

    ProductService(db).delete(product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
