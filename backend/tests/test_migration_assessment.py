from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_assess_migration_candidate() -> None:
    payload = {
        "vm_name": "vpn-gw-01",
        "operating_system": "linux",
        "cpu_cores": 4,
        "memory_gb": 16,
        "storage_gb": 200,
        "average_cpu_percent": 72,
        "average_memory_percent": 64,
        "criticality": "high",
        "target_cloud": "azure",
    }

    response = client.post("/api/v1/migrations/assess", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["vm_name"] == "vpn-gw-01"
    assert body["migration_strategy"] == "rehost"
    assert body["readiness_score"] == 70
    assert body["recommended_sizing"]["cpu_cores"] == 5
    assert body["recommended_sizing"]["memory_gb"] == 16
    assert body["recommended_sizing"]["storage_gb"] == 240


def test_upload_inventory_csv() -> None:
    csv_content = "\n".join(
        [
            "vm_name,application_name,environment,operating_system,target_cloud,cpu_cores,memory_gb,storage_gb,average_cpu_percent,peak_cpu_percent,average_memory_percent,peak_memory_percent,criticality,rpo_minutes,rto_minutes,maintenance_window,requires_vpn_connectivity,requires_static_ip,listening_ports,dependency_flows",
            'erp-app-01,ERP,prod,windows,azure,8,32,500,55,82,68,91,high,60,240,"Sunday 01:00-04:00",true,true,"443;3389","erp-app-01->sql-prod-01:1433"',
            "bad-row,ERP,prod,windows,azure,0,32,500,55,82,68,91,high,60,240,Sunday,false,false,443,",
        ]
    )

    response = client.post(
        "/api/v1/inventory/upload",
        files={"file": ("inventory.csv", csv_content, "text/csv")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total_rows"] == 2
    assert body["valid_rows"] == 1
    assert body["invalid_rows"] == 1
    assert body["results"][0]["assessment"]["vm_name"] == "erp-app-01"
    assert body["results"][0]["assessment"]["readiness_score"] == 80
    assert "cpu_cores" in body["results"][1]["errors"][0]
