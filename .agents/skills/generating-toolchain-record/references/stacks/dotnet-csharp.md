# .NET / C# — DTR Field Reference

Use this file when the ASD describes a backend built with .NET (ASP.NET Core).

---

## General Development

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Language | C# | 12 / 13 | Version tracks .NET runtime: .NET 8 → C# 12, .NET 9 → C# 13 |
| IDE | Visual Studio | 2022 | Or `JetBrains Rider` (cross-platform), `Visual Studio Code` |
| Dependency Management | NuGet | — | Built into the .NET SDK; no separate version needed |
| Artifact Repository | Azure Artifacts | managed | Or `GitHub Packages`, `JFrog Artifactory`, `Sonatype Nexus` |
| Version Control | GitHub | SaaS | Or `Azure DevOps`, `GitLab`, `Bitbucket` |
| CI/CD Quality | SonarCloud | SaaS | Self-hosted: `SonarQube`; built-in analyzer: `Roslyn Analyzers` (note in Toolchain Notes) |
| Dynamic/Runtime Analysis | dotMemory | — | Or `ANTS Profiler`, `Visual Studio Profiler` (built-in); omit if not used |
| Mocking | NSubstitute | 5.x | Alternatives: `Moq` (4.x), `FakeItEasy` (8.x) |
| Unit Testing | xUnit | 2.x | Alternatives: `NUnit` (4.x), `TUnit` (newer), `MSTest` (v3) |
| Performance Testing | BenchmarkDotNet | 0.13.x | Load testing: `k6`, `NBomber`, `Apache JMeter` |
| Logging | Serilog | 4.x | Alternatives: `NLog` (5.x), `Microsoft.Extensions.Logging` (built-in) |
| Monitoring | Azure Monitor | managed | Or `Datadog`, `New Relic`, `Dynatrace`, `Prometheus + Grafana` |
| CI/CD Pipeline Automation | GitHub Actions | — | Or `Azure DevOps`, `GitLab CI`, `Jenkins`, `TeamCity` |

---

## API

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Framework / Type | ASP.NET Core | 8 / 9 | Always list the .NET version (e.g., ASP.NET Core 8) |
| Gateway | Azure API Management | managed | Or `YARP` (self-hosted reverse proxy), `Kong`, `AWS API Gateway` |
| API Specification/Design | OpenAPI | 3.1 | ASP.NET Core 9 has native OpenAPI support; older: `Swashbuckle.AspNetCore` |
| API Lifecycle Management | Asp.Versioning.Http | 8.x | Handles URL, query string, or header versioning |
| API Documentation UI | Swagger UI | — | Or `Scalar`, `ReDoc`; configured via `Swashbuckle` or `NSwag` |

---

## Microservices

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Microservice Toolkit | .NET Aspire | 8.x | Or `Dapr`, `NServiceBus`; omit for monoliths |
| Service Discovery | .NET Aspire Service Discovery | — | Or `HashiCorp Consul`, `Kubernetes Services` |
| Service Registry | Kubernetes Services | — | Or `HashiCorp Consul`; omit if discovery is DNS-based |
| HealthCheck | Microsoft.Extensions.Diagnostics.HealthChecks | — | Built into ASP.NET Core; widely used |
| Load Balancer | YARP | 2.x | Or `Kubernetes Ingress`, `Azure Load Balancer`, `AWS ALB` |
| Container Orchestration | Azure Kubernetes Service (AKS) | managed | Or `Amazon EKS`, `GKE`, `Azure Container Apps`, `Amazon ECS` |
| Image Registry | Azure Container Registry (ACR) | managed | Or `Amazon ECR`, `Google Artifact Registry`, `Docker Hub` |
| Messaging Framework | MassTransit | 8.x | Alternatives: `NServiceBus`, `Rebus`; omit if using broker SDK directly |
| Message Broker | Azure Service Bus | managed | Or `RabbitMQ`, `Apache Kafka`, `Amazon SQS` |
| Distributed Cache (L2) | Redis | 7.x | Via `StackExchange.Redis`; or `NCache` |
| Resiliency Patterns | Polly | 8.x | Standard resilience library for .NET; Microsoft.Extensions.Resilience wraps it |
| Log Analysis Platform | Azure Log Analytics | managed | Or `Datadog Logs`, `ELK Stack`, `Splunk` |
| Trace Backend | Azure Monitor | managed | Or `Datadog APM`, `Jaeger`, `Tempo`, `OpenTelemetry Collector` |
| CQRS Mediator | MediatR | 12.x | Or `Wolverine` (8.x), `PipelinR` |

---

## Infrastructure Management

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Infrastructure Definition Tool | Terraform | 1.x | Or `Bicep` (Azure-native), `Azure Resource Manager`, `Pulumi` |
| Server Templating | Azure Image Builder | managed | Omit for container or PaaS workloads |
| Secrets Management | Azure Key Vault | managed | Or `HashiCorp Vault`, `AWS Secrets Manager`, `Google Secret Manager` |
| Version Control | GitHub | SaaS | Or `Azure DevOps` (same or separate IaC repo) |

---

## Other Tools

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| AuthZ/AuthN | Microsoft Entra ID | SaaS | Or `Keycloak`, `Auth0`, `IdentityServer` (Duende), `OpenIddict` |
| Database | Azure SQL Database | SaaS | Or `PostgreSQL`, `SQL Server`, `MongoDB`, `CosmosDB` |
| ORM | Entity Framework Core | 8.x / 9.x | Lightweight: `Dapper` (2.x); or `NHibernate` (5.x) |
| Background Jobs/Scheduling | Hangfire | 1.8.x | Or `Quartz.NET` (3.x), `Worker Services` (built-in), `Azure Functions Timer` |
| CDN | Azure CDN | managed | Or `Cloudflare`, `Amazon CloudFront`; omit if not serving assets from backend |

---

## Linting & Code Quality

| Tool | Canonical DTR Name | Notes |
|---|---|---|
| Static analysis | Roslyn Analyzers | Built into .NET SDK; no extra package needed |
| Style enforcement | StyleCop | Optional; often replaced by EditorConfig + Roslyn |
| Code coverage | Coverlet | Commonly paired with xUnit or NUnit |
| Mutation testing | Stryker.NET | Optional; note in Toolchain Notes if used |

---

## Common Tool Pairings

| Stack Type | Typical Combination |
|---|---|
| REST API (monolith) | ASP.NET Core 8 + EF Core + SQL Server/PostgreSQL + xUnit + NSubstitute + Serilog + GitHub Actions |
| Microservices | ASP.NET Core 8 + MassTransit + Azure Service Bus + .NET Aspire + Polly + MediatR |
| Azure-native | ASP.NET Core + Azure SQL + Azure Key Vault + Azure Monitor + Azure DevOps + Bicep |
| CQRS pattern | ASP.NET Core + MediatR + EF Core + PostgreSQL + xUnit + NSubstitute |
