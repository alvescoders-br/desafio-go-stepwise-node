# Go — DTR Field Reference

Use this file when the ASD describes a backend built with Go (Golang).

---

## General Development

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Language | Go | 1.23 | Use full minor version: 1.21, 1.22, 1.23; avoid "Golang" |
| IDE | Visual Studio Code | — | Or `GoLand` (JetBrains); VS Code with `gopls` is most common |
| Dependency Management | Go Modules | — | Built-in since Go 1.11; no separate version; note as `Go Modules (built-in)` |
| Artifact Repository | — | — | Go binaries: `GitHub Releases`, `S3`; packages: public via `pkg.go.dev`; private: `GOPROXY` (JFrog) |
| Version Control | GitHub | SaaS | Or `GitLab`, `Bitbucket`, `Azure DevOps` |
| CI/CD Quality | SonarCloud | SaaS | Self-hosted: `SonarQube`; Go-native: `golangci-lint` (note in Toolchain Notes) |
| Dynamic/Runtime Analysis | pprof | — | Built-in to Go runtime (`net/http/pprof`); or `Pyroscope` for continuous profiling |
| Mocking | gomock | — | Or `testify/mock`, `moq`; generated mocks are common in Go |
| Unit Testing | testing | — | Built-in (`testing` package); enhanced with `testify` (assertions) |
| Performance Testing | k6 | — | Or `wrk`, `hey`, `Apache JMeter` |
| Logging | zerolog | — | Or `zap` (Uber), `slog` (built-in since Go 1.21), `logrus` |
| Monitoring | Datadog | SaaS | Or `Prometheus + Grafana`, `New Relic`, `Google Cloud Monitoring` |
| CI/CD Pipeline Automation | GitHub Actions | — | Or `GitLab CI`, `Jenkins`, `CircleCI` |

---

## API

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Framework / Type | Gin | 1.x | Or `Echo` (4.x), `Fiber` (2.x), `Chi` (5.x), `Huma` (2.x); `net/http` for minimal services |
| Gateway | Kong Gateway | — | Or `AWS API Gateway`, `NGINX`, `Traefik`, `Envoy` |
| API Specification/Design | OpenAPI | 3.1 | Via `swaggo/swag` (Gin/Echo); or `go-swagger`; `Huma` generates it natively |
| API Lifecycle Management | — | — | Versioned routes via path (e.g., `/v1/`, `/v2/`); omit unless a library handles it |
| API Documentation UI | Swagger UI | — | Via `swaggo/gin-swagger`; or `Scalar` |

---

## Microservices

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Microservice Toolkit | — | — | Go services are often framework-light; `go-kit` or `go-micro` for structured toolkit |
| Service Discovery | Kubernetes Services | — | Or `HashiCorp Consul`; most Go microservices rely on K8s DNS |
| Container Orchestration | Google Kubernetes Engine (GKE) | managed | Or `Amazon EKS`, `Azure Kubernetes Service (AKS)`, `Fly.io` |
| Image Registry | Google Artifact Registry | managed | Or `Amazon ECR`, `Azure Container Registry (ACR)`, `Docker Hub` |
| Messaging Framework | — | — | Go typically uses broker SDKs directly; `kafka-go` or `confluent-kafka-go` for Kafka |
| Message Broker | Apache Kafka | — | Or `NATS`, `RabbitMQ` (amqp091-go), `Amazon SQS`, `Google Pub/Sub` |
| Distributed Cache (L2) | Redis | 7.x | Via `go-redis`; or `Memcached` (via `gomemcache`) |
| Resiliency Patterns | — | — | No dominant library; `gobreaker` (circuit breaker) or `failsafe-go`; omit if not used |
| Log Analysis Platform | Datadog Logs | SaaS | Or `ELK Stack`, `Grafana Loki`, `Google Cloud Logging` |
| Trace Backend | Jaeger | — | Or `Tempo`, `Datadog APM`, `Zipkin`; via OpenTelemetry SDK |
| CQRS Mediator | — | — | No CQRS mediator convention in Go; omit |

---

## Infrastructure Management

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Infrastructure Definition Tool | Terraform | 1.x | Or `Pulumi` (Go SDK), `AWS CDK` (Go) |
| Server Templating | HashiCorp Packer | — | Omit for container workloads |
| Secrets Management | HashiCorp Vault | — | Or `AWS Secrets Manager`, `Google Secret Manager`, `Azure Key Vault` |
| Version Control | GitHub | SaaS | Or `GitLab`, `Azure DevOps` |

---

## Other Tools

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| AuthZ/AuthN | Keycloak | — | Or `Auth0`, `Casbin` (authorization), `golang-jwt/jwt` (JWT validation) |
| Database | PostgreSQL | 16 | Or `MySQL`, `MongoDB` (mongo-driver), `CockroachDB`, `SQLite` |
| ORM | GORM | 1.x | Or `sqlc` (SQL-first, code gen), `sqlx`, `Ent` (entity framework) |
| Background Jobs/Scheduling | Asynq | — | Or `robfig/cron`, `Temporal` (Go SDK), `Faktory` |
| CDN | Amazon CloudFront | managed | Or `Cloudflare`; omit if no static asset serving |

---

## Linting & Code Quality

| Tool | Canonical DTR Name | Notes |
|---|---|---|
| Meta-linter | golangci-lint | Runs many linters in one pass; industry standard |
| Static analysis | staticcheck | Included in golangci-lint; finds bugs and perf issues |
| Style | gofmt | Built-in; always used |
| Code formatting | goimports | Superset of gofmt; manages imports |
| Security | gosec | Optional; scans for security vulnerabilities |
| Coverage | go test -cover | Built-in; no separate tool needed |

---

## Common Tool Pairings

| Stack Type | Typical Combination |
|---|---|
| REST API | Gin + PostgreSQL + GORM + Redis + zerolog + GitHub Actions |
| gRPC microservice | Go + gRPC + protobuf + PostgreSQL + Kafka + Prometheus |
| High-throughput service | Go + Fiber/Chi + sqlc + Redis + zerolog + Datadog |
| GCP-native | Go + GKE + Cloud SQL + Google Secret Manager + Cloud Monitoring + Terraform |
