from enum import StrEnum

from pydantic import BaseModel, Field


class OperatingSystem(StrEnum):
    windows = "windows"
    linux = "linux"


class CloudProvider(StrEnum):
    azure = "azure"
    huawei = "huawei"
    aws = "aws"


class WorkloadCriticality(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    mission_critical = "mission_critical"


class MigrationAssessmentRequest(BaseModel):
    vm_name: str = Field(..., examples=["ad-dc-01"])
    application_name: str | None = None
    environment: str | None = None
    business_owner: str | None = None
    technical_owner: str | None = None
    operating_system: OperatingSystem
    os_version: str | None = None
    current_platform: str | None = None
    datacenter_location: str | None = None
    target_region: str | None = None
    cpu_cores: int = Field(..., ge=1, le=128)
    memory_gb: int = Field(..., ge=1, le=2048)
    storage_gb: int = Field(..., ge=10, le=65536)
    disk_count: int | None = Field(default=None, ge=1, le=128)
    average_cpu_percent: float = Field(..., ge=0, le=100)
    peak_cpu_percent: float | None = Field(default=None, ge=0, le=100)
    average_memory_percent: float = Field(..., ge=0, le=100)
    peak_memory_percent: float | None = Field(default=None, ge=0, le=100)
    average_disk_iops: int | None = Field(default=None, ge=0)
    average_disk_throughput_mbps: float | None = Field(default=None, ge=0)
    network_in_mbps: float | None = Field(default=None, ge=0)
    network_out_mbps: float | None = Field(default=None, ge=0)
    criticality: WorkloadCriticality = WorkloadCriticality.medium
    target_cloud: CloudProvider = CloudProvider.azure
    uptime_requirement: str | None = None
    rpo_minutes: int | None = Field(default=None, ge=0)
    rto_minutes: int | None = Field(default=None, ge=0)
    backup_policy: str | None = None
    maintenance_window: str | None = None
    uses_active_directory: bool = False
    domain_joined: bool = False
    requires_static_ip: bool = False
    requires_vpn_connectivity: bool = False
    internet_access_required: bool = False
    listening_ports: list[int] = Field(default_factory=list)
    dependency_flows: list[str] = Field(default_factory=list)
    compliance_requirements: str | None = None
    migration_notes: str | None = None


class SizingRecommendation(BaseModel):
    cpu_cores: int
    memory_gb: int
    storage_gb: int
    rationale: str


class CloudRecommendation(BaseModel):
    provider: CloudProvider
    compute_sku: str
    disk_type: str
    network_design: str
    identity_design: str
    backup_design: str
    terraform_resources: list[str]
    notes: list[str]


class MigrationAssessmentResponse(BaseModel):
    vm_name: str
    application_name: str | None = None
    target_cloud: CloudProvider
    target_region: str | None = None
    migration_strategy: str
    risk_level: str
    readiness_score: int
    recommended_sizing: SizingRecommendation
    cloud_recommendation: CloudRecommendation
    recommendations: list[str]
    next_steps: list[str]


class InventoryUploadItem(BaseModel):
    row_number: int
    assessment: MigrationAssessmentResponse | None = None
    errors: list[str] = Field(default_factory=list)


class InventoryUploadResponse(BaseModel):
    total_rows: int
    valid_rows: int
    invalid_rows: int
    results: list[InventoryUploadItem]
