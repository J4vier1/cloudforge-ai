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
    assert body["recommended_sizing"]["cpu_cores"] == 5
    assert body["recommended_sizing"]["memory_gb"] == 16
    assert body["recommended_sizing"]["storage_gb"] == 240
