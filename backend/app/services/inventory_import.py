import csv
from io import StringIO
from typing import Any

from pydantic import ValidationError

from app.models.migration import (
    CloudProvider,
    InventoryUploadItem,
    InventoryUploadResponse,
    MigrationAssessmentRequest,
)
from app.services.migration_assessment import assess_migration_candidate


def assess_inventory_csv(
    csv_content: str,
    target_cloud: CloudProvider | None = None,
    target_region: str | None = None,
) -> InventoryUploadResponse:
    reader = csv.DictReader(StringIO(csv_content))
    results: list[InventoryUploadItem] = []

    for row_number, row in enumerate(reader, start=2):
        try:
            normalized_row = _normalize_row(row)
            if target_cloud is not None:
                normalized_row["target_cloud"] = target_cloud.value
            if target_region:
                normalized_row["target_region"] = target_region
            request = MigrationAssessmentRequest.model_validate(normalized_row)
        except ValidationError as exc:
            results.append(
                InventoryUploadItem(
                    row_number=row_number,
                    errors=[f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}" for error in exc.errors()],
                )
            )
            continue

        results.append(
            InventoryUploadItem(
                row_number=row_number,
                assessment=assess_migration_candidate(request),
            )
        )

    valid_rows = sum(1 for item in results if item.assessment is not None)
    invalid_rows = len(results) - valid_rows

    return InventoryUploadResponse(
        total_rows=len(results),
        valid_rows=valid_rows,
        invalid_rows=invalid_rows,
        results=results,
    )


def _normalize_row(row: dict[str, str | None]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in row.items():
        if key is None:
            continue
        normalized[key] = _normalize_value(key.strip(), value)
    return normalized


def _normalize_value(key: str, value: str | None) -> Any:
    if value is None:
        return None

    value = value.strip()
    if value == "":
        return None

    if key in {
        "uses_active_directory",
        "domain_joined",
        "requires_static_ip",
        "requires_vpn_connectivity",
        "internet_access_required",
    }:
        return value.lower() in {"true", "yes", "y", "1", "si", "sí"}

    if key == "listening_ports":
        return [int(port.strip()) for port in value.split(";") if port.strip()]

    if key == "dependency_flows":
        return [flow.strip() for flow in value.split(";") if flow.strip()]

    return value
