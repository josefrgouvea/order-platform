from fastapi import FastAPI

from orders_api.core.config import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)


@app.get("/health")
def health() -> dict[str, str]:
    """Indica se a API está funcionando."""
    return {
        "status": "ok",
        "version": settings.app_version,
        "environment": settings.environment,
    }
