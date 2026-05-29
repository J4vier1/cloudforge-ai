from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models.migration import (
    CloudProvider,
    InventoryUploadResponse,
    MigrationAssessmentRequest,
    MigrationAssessmentResponse,
    MigrationPlanCreateRequest,
    MigrationPlanResponse,
    MigrationTaskStatus,
)
from app.services.inventory_import import assess_inventory_csv
from app.services.migration_assessment import assess_migration_candidate
from app.services.migration_planner import (
    add_tasks_to_plan,
    create_migration_plan,
    delete_migration_plan,
    get_migration_plan,
    list_migration_plans,
    update_task_status,
)

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


@router.post(
    "/api/v1/migration-plans",
    response_model=MigrationPlanResponse,
    tags=["migration-plans"],
)
def create_plan(request: MigrationPlanCreateRequest) -> MigrationPlanResponse:
    """Create a new migration plan."""
    return create_migration_plan(request)


@router.get(
    "/api/v1/migration-plans",
    response_model=list[MigrationPlanResponse],
    tags=["migration-plans"],
)
def list_plans() -> list[MigrationPlanResponse]:
    """List all migration plans."""
    return list_migration_plans()


@router.get(
    "/api/v1/migration-plans/{plan_id}",
    response_model=MigrationPlanResponse,
    tags=["migration-plans"],
)
def get_plan(plan_id: str) -> MigrationPlanResponse:
    """Get a specific migration plan."""
    plan = get_migration_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Migration plan not found.")
    return plan


@router.patch(
    "/api/v1/migration-plans/{plan_id}/tasks/{vm_name}",
    response_model=MigrationPlanResponse,
    tags=["migration-plans"],
)
def update_task(
    plan_id: str,
    vm_name: str,
    status: MigrationTaskStatus,
) -> MigrationPlanResponse:
    """Update the status of a migration task."""
    plan = update_task_status(plan_id, vm_name, status)
    if not plan:
        raise HTTPException(status_code=404, detail="Migration plan not found.")
    return plan


@router.delete(
    "/api/v1/migration-plans/{plan_id}",
    tags=["migration-plans"],
)
def delete_plan(plan_id: str) -> dict[str, str]:
    """Delete a migration plan."""
    if not delete_migration_plan(plan_id):
        raise HTTPException(status_code=404, detail="Migration plan not found.")
    return {"message": "Migration plan deleted."}
