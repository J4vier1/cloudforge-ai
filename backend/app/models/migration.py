from enum import StrEnum

from pydantic import BaseModel, Field


class OperatingSystem(StrEnum):
    windows = "windows"
    linux = "linux"


class CloudProvider(StrEnum):
    azure = "azure"
    huawei = "huawei"


class WorkloadCriticality(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    mission_critical = "mission_critical"


class MigrationAssessmentRequest(BaseModel):
    vm_name: str = Field(..., examples=["ad-dc-01"])
    operating_system: OperatingSystem
    cpu_cores: int = Field(..., ge=1, le=128)
    memory_gb: int = Field(..., ge=1, le=2048)
    storage_gb: int = Field(..., ge=10, le=65536)
    average_cpu_percent: float = Field(..., ge=0, le=100)
    average_memory_percent: float = Field(..., ge=0, le=100)
    criticality: WorkloadCriticality = WorkloadCriticality.medium
    target_cloud: CloudProvider = CloudProvider.azure


class SizingRecommendation(BaseModel):
    cpu_cores: int
    memory_gb: int
    storage_gb: int
    rationale: str


class MigrationAssessmentResponse(BaseModel):
    vm_name: str
    target_cloud: CloudProvider
    migration_strategy: str
    risk_level: str
    recommended_sizing: SizingRecommendation
    recommendations: list[str]
    next_steps: list[str]
