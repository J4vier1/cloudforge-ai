from app.models.migration import (
    CloudProvider,
    CloudRecommendation,
    MigrationAssessmentRequest,
    SizingRecommendation,
)


def build_cloud_recommendation(
    request: MigrationAssessmentRequest,
    sizing: SizingRecommendation,
) -> CloudRecommendation:
    if request.target_cloud == CloudProvider.azure:
        return _azure_recommendation(request, sizing)
    if request.target_cloud == CloudProvider.aws:
        return _aws_recommendation(request, sizing)
    return _huawei_recommendation(request, sizing)


def _azure_recommendation(
    request: MigrationAssessmentRequest,
    sizing: SizingRecommendation,
) -> CloudRecommendation:
    return CloudRecommendation(
        provider=CloudProvider.azure,
        compute_sku=_pick_sku(
            sizing,
            balanced=[
                (2, 8, "Standard_D2s_v5"),
                (4, 16, "Standard_D4s_v5"),
                (8, 32, "Standard_D8s_v5"),
                (16, 64, "Standard_D16s_v5"),
                (32, 128, "Standard_D32s_v5"),
            ],
            memory=[
                (2, 16, "Standard_E2s_v5"),
                (4, 32, "Standard_E4s_v5"),
                (8, 64, "Standard_E8s_v5"),
                (16, 128, "Standard_E16s_v5"),
                (32, 256, "Standard_E32s_v5"),
            ],
        ),
        disk_type=_disk_type(request, standard="Standard SSD", performance="Premium SSD v2"),
        network_design="VNet, subnet, NSG rules, private IP reservation, and VPN/ExpressRoute validation.",
        identity_design=_identity_design(
            request,
            active_directory="AD DS connectivity with DNS forwarding and optional Azure Arc onboarding.",
            standalone="Microsoft Entra ID/IAM review and local admin access hardening.",
        ),
        backup_design="Azure Backup with Recovery Services Vault and restore testing aligned to RPO/RTO.",
        terraform_resources=[
            "azurerm_linux_virtual_machine or azurerm_windows_virtual_machine",
            "azurerm_managed_disk",
            "azurerm_network_interface",
            "azurerm_network_security_group",
            "azurerm_recovery_services_vault",
        ],
        notes=_common_notes(request)
        + ["Validate Azure Migrate assessment data before final sizing and cost approval."],
    )


def _aws_recommendation(
    request: MigrationAssessmentRequest,
    sizing: SizingRecommendation,
) -> CloudRecommendation:
    return CloudRecommendation(
        provider=CloudProvider.aws,
        compute_sku=_pick_sku(
            sizing,
            balanced=[
                (2, 8, "m6i.large"),
                (4, 16, "m6i.xlarge"),
                (8, 32, "m6i.2xlarge"),
                (16, 64, "m6i.4xlarge"),
                (32, 128, "m6i.8xlarge"),
            ],
            memory=[
                (2, 16, "r6i.large"),
                (4, 32, "r6i.xlarge"),
                (8, 64, "r6i.2xlarge"),
                (16, 128, "r6i.4xlarge"),
                (32, 256, "r6i.8xlarge"),
            ],
        ),
        disk_type=_disk_type(request, standard="EBS gp3", performance="EBS io2"),
        network_design="VPC, private subnet, security groups, route tables, Elastic IP review, and VPN/Direct Connect validation.",
        identity_design=_identity_design(
            request,
            active_directory="AWS Managed Microsoft AD or AD Connector validation with DNS and Kerberos flows.",
            standalone="IAM roles, Systems Manager access, and least-privilege operational model.",
        ),
        backup_design="AWS Backup policy with restore testing and CloudWatch monitoring baseline.",
        terraform_resources=[
            "aws_instance",
            "aws_ebs_volume",
            "aws_network_interface",
            "aws_security_group",
            "aws_backup_plan",
        ],
        notes=_common_notes(request)
        + ["Validate AWS Application Migration Service compatibility before cutover planning."],
    )


def _huawei_recommendation(
    request: MigrationAssessmentRequest,
    sizing: SizingRecommendation,
) -> CloudRecommendation:
    return CloudRecommendation(
        provider=CloudProvider.huawei,
        compute_sku=_pick_sku(
            sizing,
            balanced=[
                (2, 8, "c7.large.4"),
                (4, 16, "c7.xlarge.4"),
                (8, 32, "c7.2xlarge.4"),
                (16, 64, "c7.4xlarge.4"),
                (32, 128, "c7.8xlarge.4"),
            ],
            memory=[
                (2, 16, "m7.large.8"),
                (4, 32, "m7.xlarge.8"),
                (8, 64, "m7.2xlarge.8"),
                (16, 128, "m7.4xlarge.8"),
                (32, 256, "m7.8xlarge.8"),
            ],
        ),
        disk_type=_disk_type(request, standard="EVS General Purpose SSD", performance="EVS Ultra-high I/O"),
        network_design="VPC, subnet, security group, EIP review, and VPN/Direct Connect validation.",
        identity_design=_identity_design(
            request,
            active_directory="AD connectivity validation over VPN with DNS and domain controller reachability.",
            standalone="IAM agency and least-privilege operational access model.",
        ),
        backup_design="Cloud Backup and Recovery policy with restore validation aligned to RPO/RTO.",
        terraform_resources=[
            "huaweicloud_compute_instance",
            "huaweicloud_evs_volume",
            "huaweicloud_vpc",
            "huaweicloud_networking_secgroup",
            "huaweicloud_cbr_vault",
        ],
        notes=_common_notes(request)
        + ["Validate target region flavor availability before final migration wave planning."],
    )


def _pick_sku(
    sizing: SizingRecommendation,
    balanced: list[tuple[int, int, str]],
    memory: list[tuple[int, int, str]],
) -> str:
    catalog = memory if sizing.memory_gb / sizing.cpu_cores >= 6 else balanced
    for cpu, memory_gb, sku in catalog:
        if cpu >= sizing.cpu_cores and memory_gb >= sizing.memory_gb:
            return sku
    return catalog[-1][2]


def _disk_type(
    request: MigrationAssessmentRequest,
    standard: str,
    performance: str,
) -> str:
    if (request.average_disk_iops or 0) >= 3000:
        return performance
    if (request.average_disk_throughput_mbps or 0) >= 125:
        return performance
    return standard


def _identity_design(
    request: MigrationAssessmentRequest,
    active_directory: str,
    standalone: str,
) -> str:
    if request.uses_active_directory or request.domain_joined:
        return active_directory
    return standalone


def _common_notes(request: MigrationAssessmentRequest) -> list[str]:
    notes: list[str] = []
    if request.requires_vpn_connectivity:
        notes.append("Connectivity must be validated before migration wave approval.")
    if request.requires_static_ip:
        notes.append("Plan private IP reservation and DNS update sequence.")
    if request.compliance_requirements and request.compliance_requirements.lower() != "none":
        notes.append(f"Review compliance requirement: {request.compliance_requirements}.")
    return notes
