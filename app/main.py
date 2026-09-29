from fastapi import FastAPI

from app.core.config import settings
from app.routers.customer_router import router as customer_router


def create_app() -> FastAPI:
    """Application factory initializing FastAPI with routes and metadata."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="RESTful API for searching and managing customer records using local JSON persistence.",
    )

    app.include_router(customer_router)

    @app.get("/health", tags=["Health"])
    def health_check() -> dict[str, str]:
        return {"status": "healthy", "version": settings.app_version}

    return app


app = create_app()
