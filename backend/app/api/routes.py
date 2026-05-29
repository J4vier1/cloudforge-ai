from fastapi import APIRouter

from app.models.migration import MigrationAssessmentRequest, MigrationAssessmentResponse
from app.services.migration_assessment import assess_migration_candidate

router = APIRouter()


@router.get("/", tags=["platform"])
def root() -> dict[str, str]:
    return {
        "project": "CloudForge AI",
        "service": "Cloud Migration Assistant",
        "status": "running",
    }


@router.get("/health", tags=["platform"])
def health() -> dict[str, str]:
    return {"status": "healthy"}


@router.post(
    "/api/v1/migrations/assess",
    response_model=MigrationAssessmentResponse,
    tags=["migration-assessment"],
)
def assess_migration(request: MigrationAssessmentRequest) -> MigrationAssessmentResponse:
    return assess_migration_candidate(request)
