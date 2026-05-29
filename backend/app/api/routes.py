from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models.migration import (
    CloudProvider,
    InventoryUploadResponse,
    MigrationAssessmentRequest,
    MigrationAssessmentResponse,
)
from app.services.inventory_import import assess_inventory_csv
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


@router.post(
    "/api/v1/inventory/upload",
    response_model=InventoryUploadResponse,
    tags=["inventory"],
)
async def upload_inventory(
    file: UploadFile = File(...),
    target_cloud: CloudProvider | None = Form(default=None),
    target_region: str | None = Form(default=None),
) -> InventoryUploadResponse:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV inventory files are supported.")

    content = await file.read()
    try:
        csv_content = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV file must be UTF-8 encoded.") from exc

    return assess_inventory_csv(
        csv_content,
        target_cloud=target_cloud,
        target_region=target_region or None,
    )
