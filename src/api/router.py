from fastapi import APIRouter

from src.api.routes import auth, movements, products, reports, users

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(products.router)
api_router.include_router(movements.router)
api_router.include_router(reports.router)
