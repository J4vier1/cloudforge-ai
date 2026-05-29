from app.models.migration import (
    MigrationAssessmentRequest,
    MigrationAssessmentResponse,
    SizingRecommendation,
    WorkloadCriticality,
)


def assess_migration_candidate(
    request: MigrationAssessmentRequest,
) -> MigrationAssessmentResponse:
    cpu_headroom = 1.25 if request.average_cpu_percent >= 70 else 1.0
    memory_headroom = 1.25 if request.average_memory_percent >= 70 else 1.0

    recommended_cpu = max(request.cpu_cores, round(request.cpu_cores * cpu_headroom))
    recommended_memory = max(request.memory_gb, round(request.memory_gb * memory_headroom))
    recommended_storage = round(request.storage_gb * 1.2)

    risk_level = _calculate_risk_level(request)

    return MigrationAssessmentResponse(
        vm_name=request.vm_name,
        target_cloud=request.target_cloud,
        migration_strategy="rehost",
        risk_level=risk_level,
        recommended_sizing=SizingRecommendation(
            cpu_cores=recommended_cpu,
            memory_gb=recommended_memory,
            storage_gb=recommended_storage,
            rationale="Initial lift-and-shift sizing with capacity headroom for observed utilization.",
        ),
        recommendations=[
            "Validate application dependencies before migration.",
            "Confirm backup, rollback, and maintenance window requirements.",
            "Run network latency checks between source, VPN, and target cloud landing zone.",
            "Generate Terraform after target subscription/project and region are selected.",
        ],
        next_steps=[
            "Collect 30-day CPU, memory, disk, and network metrics.",
            "Classify workload dependencies and identity requirements.",
            "Create target cloud landing zone and connectivity baseline.",
        ],
    )


def _calculate_risk_level(request: MigrationAssessmentRequest) -> str:
    if request.criticality == WorkloadCriticality.mission_critical:
        return "high"
    if request.average_cpu_percent >= 85 or request.average_memory_percent >= 85:
        return "medium"
    if request.storage_gb >= 4096:
        return "medium"
    return "low"
