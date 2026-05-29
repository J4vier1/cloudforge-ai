from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.config import settings

FRONTEND_DIR = next(
    path
    for path in (
        Path(__file__).resolve().parents[2] / "frontend",
        Path(__file__).resolve().parents[1] / "frontend",
        Path.cwd() / "frontend",
        Path.cwd().parent / "frontend",
    )
    if path.exists()
)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.project_name,
        version=settings.version,
        description="AI-native API for cloud migration assessment and automation.",
    )
    app.include_router(router)
    app.mount("/dashboard", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="dashboard")
    return app


app = create_app()
