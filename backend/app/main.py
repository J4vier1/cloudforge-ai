from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.project_name,
        version=settings.version,
        description="AI-native API for cloud migration assessment and automation.",
    )
    app.include_router(router)
    return app


app = create_app()
