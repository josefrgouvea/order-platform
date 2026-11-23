from fastapi import FastAPI

from orders_api.api import orders, users
from orders_api.core.config import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(users.router)
app.include_router(orders.router)


@app.get("/health")
def health() -> dict[str, str]:
    """Indica se a API está funcionando."""
    return {
        "status": "ok",
        "version": settings.app_version,
        "environment": settings.environment,
    }
