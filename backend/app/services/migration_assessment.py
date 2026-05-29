from app.models.migration import (
    MigrationAssessmentRequest,
    MigrationAssessmentResponse,
    SizingRecommendation,
    WorkloadCriticality,
)


def assess_migration_candidate(
    request: MigrationAssessmentRequest,
) -> MigrationAssessmentResponse:
    cpu_reference = max(request.average_cpu_percent, request.peak_cpu_percent or 0)
    memory_reference = max(request.average_memory_percent, request.peak_memory_percent or 0)

    cpu_headroom = 1.25 if cpu_reference >= 70 else 1.0
    memory_headroom = 1.25 if memory_reference >= 70 else 1.0

    recommended_cpu = max(request.cpu_cores, round(request.cpu_cores * cpu_headroom))
    recommended_memory = max(request.memory_gb, round(request.memory_gb * memory_headroom))
    recommended_storage = round(request.storage_gb * 1.2)

    risk_level = _calculate_risk_level(request)
    readiness_score = _calculate_readiness_score(request, risk_level)

    return MigrationAssessmentResponse(
        vm_name=request.vm_name,
        application_name=request.application_name,
        target_cloud=request.target_cloud,
        target_region=request.target_region,
        migration_strategy="rehost",
        risk_level=risk_level,
        readiness_score=readiness_score,
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
            *_identity_recommendations(request),
            *_network_recommendations(request),
        ],
        next_steps=[
            "Collect 30-day CPU, memory, disk, and network metrics.",
            "Classify workload dependencies and identity requirements.",
            "Create target cloud landing zone and connectivity baseline.",
            *_continuity_next_steps(request),
        ],
    )


def _calculate_risk_level(request: MigrationAssessmentRequest) -> str:
    if request.criticality == WorkloadCriticality.mission_critical:
        return "high"
    if (request.peak_cpu_percent or request.average_cpu_percent) >= 85:
        return "medium"
    if (request.peak_memory_percent or request.average_memory_percent) >= 85:
        return "medium"
    if request.storage_gb >= 4096:
        return "medium"
    if request.requires_vpn_connectivity and request.requires_static_ip:
        return "medium"
    return "low"


def _calculate_readiness_score(
    request: MigrationAssessmentRequest,
    risk_level: str,
) -> int:
    score = 100
    if risk_level == "high":
        score -= 30
    elif risk_level == "medium":
        score -= 15

    if request.rpo_minutes is None or request.rto_minutes is None:
        score -= 10
    if not request.maintenance_window:
        score -= 10
    if not request.dependency_flows:
        score -= 10
    if request.uses_active_directory or request.domain_joined:
        score -= 5
    if request.requires_vpn_connectivity:
        score -= 5
    if request.compliance_requirements and request.compliance_requirements.lower() != "none":
        score -= 5

    return max(score, 0)


def _identity_recommendations(request: MigrationAssessmentRequest) -> list[str]:
    if not request.uses_active_directory and not request.domain_joined:
        return []
    return [
        "Validate Active Directory, DNS, LDAP/Kerberos, and domain join dependencies before cutover."
    ]


def _network_recommendations(request: MigrationAssessmentRequest) -> list[str]:
    recommendations: list[str] = []
    if request.requires_vpn_connectivity:
        recommendations.append(
            "Validate VPN routing, firewall rules, and asymmetric routing risks for the target cloud."
        )
    if request.requires_static_ip:
        recommendations.append(
            "Reserve target private IP addressing and update DNS records during migration planning."
        )
    if request.listening_ports:
        ports = ", ".join(str(port) for port in request.listening_ports)
        recommendations.append(f"Confirm security rules for required listening ports: {ports}.")
    return recommendations


def _continuity_next_steps(request: MigrationAssessmentRequest) -> list[str]:
    if request.rpo_minutes is None or request.rto_minutes is None:
        return ["Define RPO and RTO before approving migration execution."]
    return [
        f"Validate backup and recovery design against RPO {request.rpo_minutes} minutes and RTO {request.rto_minutes} minutes."
    ]
