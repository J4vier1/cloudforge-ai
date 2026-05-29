import json
from pathlib import Path
from datetime import datetime

from app.models.migration import (
    MigrationPlan,
    MigrationPlanCreateRequest,
    MigrationPlanResponse,
    MigrationTask,
    MigrationTaskStatus,
)

PLANS_FILE = Path(__file__).resolve().parent.parent.parent / ".plans.json"


def _load_plans() -> dict[str, MigrationPlan]:
    """Load all plans from JSON storage."""
    if not PLANS_FILE.exists():
        return {}
    try:
        with open(PLANS_FILE, "r") as f:
            data = json.load(f)
        return {
            plan_id: MigrationPlan(**plan_data)
            for plan_id, plan_data in data.items()
        }
    except (json.JSONDecodeError, ValueError):
        return {}


def _save_plans(plans: dict[str, MigrationPlan]) -> None:
    """Save all plans to JSON storage."""
    with open(PLANS_FILE, "w") as f:
        json.dump(
            {plan_id: plan.model_dump() for plan_id, plan in plans.items()},
            f,
            indent=2,
        )


def create_migration_plan(
    request: MigrationPlanCreateRequest,
) -> MigrationPlanResponse:
    """Create a new migration plan."""
    plans = _load_plans()
    
    # Calculate initial stats
    total_vms = len(request.tasks)
    completed_vms = sum(
        1 for task in request.tasks
        if task.status == MigrationTaskStatus.completed
    )
    
    plan = MigrationPlan(
        name=request.name,
        description=request.description,
        owner=request.owner,
        target_cloud=request.target_cloud,
        target_region=request.target_region,
        tasks=request.tasks,
        total_vms=total_vms,
        completed_vms=completed_vms,
    )
    
    plans[plan.plan_id] = plan
    _save_plans(plans)
    
    return _to_response(plan)


def get_migration_plan(plan_id: str) -> MigrationPlanResponse | None:
    """Get a specific plan by ID."""
    plans = _load_plans()
    plan = plans.get(plan_id)
    return _to_response(plan) if plan else None


def list_migration_plans() -> list[MigrationPlanResponse]:
    """List all migration plans."""
    plans = _load_plans()
    return [_to_response(plan) for plan in plans.values()]


def update_task_status(
    plan_id: str,
    vm_name: str,
    status: MigrationTaskStatus,
    completed_date: str | None = None,
) -> MigrationPlanResponse | None:
    """Update the status of a migration task."""
    plans = _load_plans()
    plan = plans.get(plan_id)
    if not plan:
        return None
    
    # Find and update task
    for task in plan.tasks:
        if task.vm_name == vm_name:
            task.status = status
            if status == MigrationTaskStatus.completed and not completed_date:
                task.completed_date = datetime.now().isoformat()
            elif completed_date:
                task.completed_date = completed_date
            break
    
    # Recalculate stats
    plan.completed_vms = sum(
        1 for task in plan.tasks
        if task.status == MigrationTaskStatus.completed
    )
    
    plans[plan_id] = plan
    _save_plans(plans)
    
    return _to_response(plan)


def add_tasks_to_plan(
    plan_id: str,
    tasks: list[MigrationTask],
) -> MigrationPlanResponse | None:
    """Add more tasks to an existing plan."""
    plans = _load_plans()
    plan = plans.get(plan_id)
    if not plan:
        return None
    
    plan.tasks.extend(tasks)
    plan.total_vms = len(plan.tasks)
    
    plans[plan_id] = plan
    _save_plans(plans)
    
    return _to_response(plan)


def delete_migration_plan(plan_id: str) -> bool:
    """Delete a migration plan."""
    plans = _load_plans()
    if plan_id in plans:
        del plans[plan_id]
        _save_plans(plans)
        return True
    return False


def _to_response(plan: MigrationPlan) -> MigrationPlanResponse:
    """Convert plan to response DTO."""
    progress = (
        int((plan.completed_vms / plan.total_vms) * 100)
        if plan.total_vms > 0
        else 0
    )
    return MigrationPlanResponse(
        plan_id=plan.plan_id,
        name=plan.name,
        description=plan.description,
        created_date=plan.created_date,
        owner=plan.owner,
        target_cloud=plan.target_cloud,
        target_region=plan.target_region,
        tasks=plan.tasks,
        total_vms=plan.total_vms,
        completed_vms=plan.completed_vms,
        progress_percentage=progress,
    )
