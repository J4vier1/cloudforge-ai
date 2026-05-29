# Cloud Migration Assistant Architecture

## Goal

Cloud Migration Assistant is an API-first platform for assessing virtual machines, recommending cloud sizing, and preparing migration automation.

## Current Version

The first version focuses on a clean FastAPI backend:

- VM assessment input model.
- Lift-and-shift sizing recommendation.
- Migration risk classification.
- Docker and Kubernetes deployment baseline.
- Testable service layer for future AI and Terraform generation.

## Next Architecture Steps

- Add OpenAI-powered recommendation enrichment.
- Persist assessments in PostgreSQL.
- Generate Terraform plans from approved recommendations.
- Add a worker service for long-running discovery and migration tasks.
- Deploy to AKS with ingress, managed identity, and observability.
