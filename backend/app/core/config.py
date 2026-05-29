from pydantic import BaseModel


class Settings(BaseModel):
    project_name: str = "CloudForge AI"
    version: str = "0.1.0"
    environment: str = "local"


settings = Settings()
