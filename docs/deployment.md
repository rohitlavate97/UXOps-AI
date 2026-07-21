# Deployment & Production Operations Guide

## Overview

This guide details deployment options for **UXOps AI**, ranging from multi-container Docker Compose environments to production Kubernetes clusters.

---

## 1. Environment Variables

Production deployments require setting the following environment variables:

| Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `ENVIRONMENT` | Deployment mode | `production` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@db:5432/uxops_db` |
| `REDIS_URL` | Redis cache & Celery broker URL | `redis://redis:6379/0` |
| `SECRET_KEY` | JWT signing secret key (Min 32 chars) | `super-secret-random-key` |
| `ALGORITHM` | JWT signing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token validity duration | `11520` (8 days) |
| `S3_ENDPOINT_URL` | Object storage endpoint | `https://s3.amazonaws.com` |
| `S3_BUCKET_NAME` | Object storage bucket name | `uxops-screenshots` |
| `VITE_API_URL` | Frontend API client base URL | `https://api.uxops.ai/api/v1` |

---

## 2. Docker Compose Production Deployment

For single-node or staging deployments, use `docker-compose.yml`:

```bash
# Clone production branch
git clone https://github.com/rohitlavate97/UXOps-AI.git
cd UXOps-AI

# Create production .env file
cp .env.example .env

# Build and start services in detached mode
docker compose -f docker-compose.yml up -d --build
```

### Health Checks
Verify container health:
```bash
docker compose ps
curl http://localhost:8000/health
```

---

## 3. Kubernetes Deployment (`/kubernetes`)

For enterprise scalable production deployments, Kubernetes manifests are provided in the `/kubernetes` directory.

### Cluster Manifests
```text
kubernetes/
├── namespace.yaml         # UXOps AI namespace definition
├── postgres-deployment.yaml # PostgreSQL StatefulSet & Service
├── redis-deployment.yaml    # Redis Deployment & Service
├── backend-deployment.yaml  # FastAPI Deployment & HorizontalPodAutoscaler
├── celery-worker-deployment.yaml # Celery Worker Deployment
├── frontend-deployment.yaml # Nginx / React Frontend Deployment
└── ingress.yaml             # Ingress Controller Routing
```

### Applying Manifests
```bash
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/ -n uxops-ai
```

---

## 4. Database Migrations in Production

Run Alembic schema upgrades prior to routing live traffic to updated backend pods:

```bash
# Execution inside backend container / pod
alembic upgrade head
```

---

## 5. Monitoring & Health Status

* **Health Endpoint**: `GET /health` returns `{"status": "healthy"}`.
* **Celery Inspection**: Run `celery -A common.celery_app inspect ping` to verify worker availability.
* **Logs**: View application logs via `docker compose logs -f backend` or `kubectl logs -l app=uxops-backend -n uxops-ai`.
