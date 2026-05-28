from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.api.router import api_router
from src.core.config import settings
from src.core.exceptions import register_exception_handlers
from src.core.logging import configure_logging


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    configure_logging()

    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        version="0.1.0",
        description="Inventory control API with authentication, stock movements and reports.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from pathlib import Path

    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    (uploads_dir / "products").mkdir(exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

    register_exception_handlers(app)
    app.include_router(api_router)

    @app.get("/health", tags=["health"])
    def health_check() -> dict[str, str]:
        """Return application health status."""

        return {"status": "ok"}

    return app


app = create_app()
