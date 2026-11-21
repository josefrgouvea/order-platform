from fastapi import FastAPI

app = FastAPI(title="Orders API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    """Indica se a API está funcionando."""
    return {"status": "ok", "version": "0.1.0"}
