# Python — DTR Field Reference

Use this file when the ASD describes a backend built with Python.

---

## General Development

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Language | Python | 3.12 | Always include minor version (3.11, 3.12, 3.13); avoid "Python 3" alone |
| IDE | Visual Studio Code | — | Or `PyCharm` (JetBrains) |
| Dependency Management | pip | — | Or `Poetry` (1.x), `uv` (fast modern alternative), `PDM`, `Pipenv` |
| Artifact Repository | PyPI | SaaS | Private: `AWS CodeArtifact`, `JFrog Artifactory`, `GitHub Packages` |
| Version Control | GitHub | SaaS | Or `GitLab`, `Azure DevOps`, `Bitbucket` |
| CI/CD Quality | SonarCloud | SaaS | Self-hosted: `SonarQube`; Python-specific: `Ruff`, `Flake8`, `mypy` (note in Toolchain Notes) |
| Dynamic/Runtime Analysis | Pyroscope | — | Or `py-spy`, `cProfile` (built-in); omit if not profiling |
| Mocking | pytest-mock | — | Wraps `unittest.mock` (built-in); `responses` for HTTP mocking |
| Unit Testing | pytest | 8.x | Standard; `unittest` is built-in but rarely used without pytest |
| Performance Testing | Locust | 2.x | Or `k6`, `Apache JMeter`, `Artillery` |
| Logging | structlog | 24.x | Or `loguru` (structured, simple), `logging` (built-in, note as `Python logging`) |
| Monitoring | AWS CloudWatch | managed | Or `Datadog`, `New Relic`, `Prometheus + Grafana`, `Sentry` (error monitoring) |
| CI/CD Pipeline Automation | GitHub Actions | — | Or `GitLab CI`, `Jenkins`, `Azure Pipelines`, `CircleCI` |

---

## API

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Framework / Type | FastAPI | 0.111.x | Or `Django REST Framework` (DRF), `Flask` (3.x), `Litestar` (2.x), `Starlette` |
| Gateway | AWS API Gateway | managed | Or `Kong`, `NGINX`, `Azure API Management`; omit for direct Lambda invocations |
| API Specification/Design | OpenAPI | 3.1 | FastAPI generates it automatically; DRF: `drf-spectacular`; note as `OpenAPI (built-in)` for FastAPI |
| API Lifecycle Management | — | — | No standard library; omit unless explicit versioning strategy is documented |
| API Documentation UI | Swagger UI | — | FastAPI serves it at `/docs`; note as `Swagger UI (built-in)` for FastAPI |

---

## Microservices

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Microservice Toolkit | — | — | Python has no dominant microservice toolkit; omit unless using `Dapr` or `Nameko` |
| Service Discovery | Kubernetes Services | — | Or via service mesh (Istio, Linkerd) |
| Container Orchestration | Amazon EKS | managed | Or `GKE`, `AKS`, `AWS Lambda` (serverless — omit container fields then) |
| Image Registry | Amazon ECR | managed | Or `Google Artifact Registry`, `Azure Container Registry (ACR)` |
| Messaging Framework | Celery | 5.x | Or `confluent-kafka` (Kafka direct), `boto3 SQS`; omit if no async messaging |
| Message Broker | Amazon SQS | managed | Or `Apache Kafka`, `RabbitMQ`, `Google Pub/Sub`, `Redis` (pub/sub) |
| Distributed Cache (L2) | Redis | 7.x | Via `redis-py`; or `Memcached` |
| Resiliency Patterns | Tenacity | — | Or `stamina`; omit if not explicitly used |
| Log Analysis Platform | AWS CloudWatch Logs | managed | Or `Datadog Logs`, `ELK Stack`, `Grafana Loki` |
| Trace Backend | AWS X-Ray | managed | Or `Datadog APM`, `Jaeger`, `Tempo`, `OpenTelemetry Collector` |
| CQRS Mediator | — | — | No established CQRS mediator in Python; omit unless using custom event bus |

---

## Infrastructure Management

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Infrastructure Definition Tool | Terraform | 1.x | Or `AWS CDK` (Python), `Pulumi` (Python SDK), `AWS CloudFormation` |
| Server Templating | — | — | Omit for Lambda/container workloads; `HashiCorp Packer` for VM images |
| Secrets Management | AWS Secrets Manager | managed | Or `HashiCorp Vault`, `Google Secret Manager`, `Azure Key Vault` |
| Version Control | GitHub | SaaS | Or `GitLab`, `Azure DevOps` |

---

## Other Tools

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| AuthZ/AuthN | AWS Cognito | managed | Or `Auth0`, `Keycloak`, `Microsoft Entra ID`; framework-level: `python-jose`, `Authlib` |
| Database | PostgreSQL | 16 | Or `MySQL`, `SQLite`, `MongoDB`, `DynamoDB`, `Snowflake` |
| ORM | SQLAlchemy | 2.x | Or `Django ORM` (built-in to Django), `Tortoise ORM` (async), `Peewee`; migrations: `Alembic` |
| Background Jobs/Scheduling | Celery | 5.x | Or `APScheduler`, `Dramatiq`, `Temporal`, `AWS Lambda` (scheduled events) |
| CDN | Amazon CloudFront | managed | Or `Cloudflare`; omit if not serving static assets |

---

## Linting & Code Quality

| Tool | Canonical DTR Name | Notes |
|---|---|---|
| Linting + formatting | Ruff | Modern, fast; replaces Flake8 + Black + isort in one tool |
| Type checking | mypy | Or `pyright`; important for typed Python codebases |
| Code formatting | Black | Or `Ruff format` (if using Ruff) |
| Import sorting | isort | Often replaced by `Ruff` |
| Coverage | pytest-cov | Standard pytest plugin; wraps `coverage.py` |

---

## Serverless-Specific Notes

When the ASD describes an AWS Lambda deployment:
- Omit `Container Orchestration` and `Image Registry` fields (mark absent, not N/A)
- Note in Toolchain Notes: "Lambda deployment — container orchestration not applicable"
- Runtime version goes in the Language field: e.g., `Python 3.12 (Lambda runtime)`
- `AWS Lambda` itself is the deployment target — record under Hosting if a web tab applies

---

## Common Tool Pairings

| Stack Type | Typical Combination |
|---|---|
| FastAPI REST API | FastAPI + SQLAlchemy + PostgreSQL + pytest + structlog + GitHub Actions |
| Django monolith | Django + Django ORM + PostgreSQL + pytest + Celery + Redis |
| Serverless (Lambda) | Python 3.12 + FastAPI (Mangum) / Flask + DynamoDB + SQS + AWS CloudWatch |
| Data pipeline / analytics | Python + SQLAlchemy + Snowflake + Celery + Redis + Airflow |
