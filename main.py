"""FastAPI application entry point."""

from fastapi import FastAPI

from routes import router

app = FastAPI(title="LegalEase API", version="1.0.0")
app.include_router(router)


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "LegalEase API"}
