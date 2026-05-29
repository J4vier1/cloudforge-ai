# CloudForge AI

AI Cloud Engineering Lab for building cloud-native and AI-native engineering platforms.

## First Project: Cloud Migration Assistant

The initial service is a FastAPI backend that assesses virtual machines and returns a first-pass lift-and-shift recommendation for Azure or Huawei Cloud.

## Run Locally

```powershell
cd backend
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

API docs:

```text
http://localhost:8000/docs
```

Web app:

```text
http://localhost:8000/dashboard/
```

## Run With Docker

```powershell
docker compose up --build
```

## Test

```powershell
cd backend
pytest
```

## Upload A Client Inventory CSV

Start the API and open Swagger:

```text
http://localhost:8000/docs
```

Use:

```text
POST /api/v1/inventory/upload
```

Upload the sample file:

```text
docs/sample-inventory.csv
```

The API validates each row and returns:

- Total rows processed.
- Valid and invalid row counts.
- Assessment output per valid VM.
- Validation errors per invalid VM.

## Kubernetes

```powershell
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/backend-deployment.yaml
kubectl apply -f kubernetes/backend-service.yaml
```

## Roadmap

- Add PostgreSQL persistence for assessments.
- Add OpenAI-generated cloud migration recommendations.
- Generate Terraform from approved migration plans.
- Package Kubernetes manifests with Helm.
- Deploy to AKS with CI/CD.
