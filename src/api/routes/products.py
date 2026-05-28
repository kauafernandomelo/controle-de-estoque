from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from src.api.deps import get_auth_user, get_db
from src.models.user import User
from src.schemas.product import ProductCreate, ProductRead, ProductUpdate
from src.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductRead, status_code=201)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_auth_user),
) -> ProductRead:
    return ProductService(db).create(data)


@router.get("", response_model=list[ProductRead])
def list_products(
    nome: str | None = Query(None),
    categoria: str | None = Query(None),
    estoque_baixo: bool | None = Query(None),
    ativo: bool | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    response: Response = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_auth_user),
) -> list[ProductRead]:
    service = ProductService(db)
    products = service.list(
        name=nome,
        category=categoria,
        low_stock=estoque_baixo,
        active=ativo,
        limit=limit,
        offset=offset,
    )
    response.headers["X-Total-Count"] = str(service.repo.count(
        name=nome, category=categoria,
        low_stock=estoque_baixo, active=ativo,
    ))
    return products


@router.get("/sku/{sku}", response_model=ProductRead)
def get_product_by_sku(
    sku: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_auth_user),
) -> ProductRead:
    return ProductService(db).get_by_sku(sku)


@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(get_auth_user),
) -> ProductRead:
    return ProductService(db).get_by_id(product_id)


@router.patch("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: UUID,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_auth_user),
) -> ProductRead:
    return ProductService(db).update(product_id, data)


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(get_auth_user),
) -> None:
    ProductService(db).delete(product_id)
