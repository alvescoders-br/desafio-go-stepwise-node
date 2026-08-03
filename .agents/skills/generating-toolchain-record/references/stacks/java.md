# Java — DTR Field Reference

Use this file when the ASD describes a backend built with Java.

---

## General Development

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Language | Java | 21 | LTS versions: 17 (still common), 21 (current LTS); use full version if specified |
| IDE | IntelliJ IDEA | — | Or `Eclipse`, `Visual Studio Code`, `Spring Tool Suite` |
| Dependency Management | Maven | 3.9.x | Or `Gradle` (8.x, Kotlin DSL preferred); note the build tool, not the runtime |
| Artifact Repository | JFrog Artifactory | — | Or `Sonatype Nexus`, `GitHub Packages`, `Azure Artifacts` |
| Version Control | GitHub | SaaS | Or `GitLab`, `Bitbucket`, `Azure DevOps` |
| CI/CD Quality | SonarQube | — | SaaS: `SonarCloud`; lightweight: `SpotBugs + Checkstyle` (note in Toolchain Notes) |
| Dynamic/Runtime Analysis | JProfiler | — | Or `async-profiler`, `VisualVM` (free); omit if not used |
| Mocking | Mockito | 5.x | Or `WireMock` (HTTP mocking), `EasyMock`; Mockito is the ecosystem standard |
| Unit Testing | JUnit 5 | 5.x | Always specify `JUnit 5` (not just `JUnit`) to distinguish from JUnit 4 |
| Integration Testing | Testcontainers | — | Runs real containers (PostgreSQL, Redis, Kafka, etc.) in tests; include when used alongside JUnit 5 |
| Performance Testing | Gatling | 3.x | Or `k6`, `Apache JMeter`, `JMH` (micro-benchmarking) |
| Logging | SLF4J + Logback | 2.x | SLF4J is the facade; `Logback` or `Log4j2` is the implementation; list both |
| Monitoring | Datadog | SaaS | Or `Dynatrace`, `New Relic`, `Prometheus + Micrometer`, `Google Cloud Monitoring` |
| CI/CD Pipeline Automation | GitHub Actions | — | Or `Jenkins`, `GitLab CI`, `Azure DevOps`, `TeamCity` |

---

## API

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Framework / Type | Spring Boot | 3.3.x | Or `Quarkus` (3.x), `Micronaut` (4.x), `Vert.x` (4.x) |
| Gateway | Spring Cloud Gateway | 4.x | Or `Kong`, `AWS API Gateway`, `Azure API Management` |
| API Specification/Design | OpenAPI | 3.1 | Via `SpringDoc OpenAPI` (2.x); Quarkus uses SmallRye OpenAPI |
| API Lifecycle Management | Spring API Versioning | — | Or custom `@RequestMapping` approach; omit if no versioning |
| API Documentation UI | Swagger UI | — | Embedded via SpringDoc or Quarkus SmallRye; or `ReDoc` |

---

## Microservices

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Microservice Toolkit | Spring Cloud | 2023.x | Or `Quarkus` (built-in), `Micronaut` (built-in), `Dapr`; omit for monoliths |
| Service Discovery | Kubernetes Services | — | Or `HashiCorp Consul`, `Spring Cloud Netflix Eureka` (legacy) |
| Service Registry | Kubernetes Services | — | Or `HashiCorp Consul`; `Eureka` in legacy stacks |
| HealthCheck | Spring Boot Actuator | — | Built into Spring Boot; Quarkus: `SmallRye Health`; MicroProfile: `MicroProfile Health` |
| Load Balancer | Spring Cloud LoadBalancer | — | Or `Kubernetes Ingress`, `AWS ALB`; `Ribbon` is legacy (deprecated) |
| Container Orchestration | Google Kubernetes Engine (GKE) | managed | Or `Amazon EKS`, `Azure Kubernetes Service (AKS)`, `Red Hat OpenShift` |
| Image Registry | Google Artifact Registry | managed | Or `Amazon ECR`, `Azure Container Registry (ACR)`, `JFrog Artifactory` |
| Messaging Framework | Spring for Apache Kafka | 3.x | Or `Spring AMQP` (RabbitMQ), `SmallRye Reactive Messaging` (Quarkus) |
| Message Broker | Apache Kafka | — | Or `RabbitMQ`, `Amazon SQS`, `Azure Service Bus`, `Google Pub/Sub` |
| Distributed Cache (L2) | Redis | 7.x | Via `Spring Data Redis`; or `Memcached`, `Infinispan` |
| Resiliency Patterns | Resilience4j | 2.x | Standard for Spring Boot 3+; Spring Cloud Circuit Breaker wraps it |
| Log Analysis Platform | ELK Stack | — | Or `Datadog Logs`, `Splunk`, `Google Cloud Logging` |
| Trace Backend | Zipkin | — | Or `Jaeger`, `Tempo`, `Datadog APM`; Spring Boot 3 uses Micrometer Tracing |
| CQRS Mediator | — | — | No standard CQRS mediator in Java; omit unless using Axon Framework |

---

## Infrastructure Management

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Infrastructure Definition Tool | Terraform | 1.x | Or `AWS CDK`, `Pulumi`, `Google Cloud Deployment Manager` |
| Server Templating | HashiCorp Packer | — | Omit for container-based workloads |
| Secrets Management | Google Secret Manager | managed | Or `AWS Secrets Manager`, `HashiCorp Vault`, `Azure Key Vault` |
| Version Control | GitHub | SaaS | Or `GitLab`, `Azure DevOps` |

---

## Other Tools

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| AuthZ/AuthN | Spring Security | 6.x | Or `Keycloak`, `Auth0`, `Okta`, `AWS Cognito`; often Spring Security + an IdP |
| Database | PostgreSQL | 16 | Or `MySQL`, `Oracle Database`, `MongoDB`, `DynamoDB`, `Google Cloud SQL` |
| ORM | Hibernate | 6.x | Via `Spring Data JPA`; or `jOOQ` (3.x, SQL-first), `MyBatis` |
| Background Jobs/Scheduling | Spring Batch | 5.x | Or `Quartz` (2.x), `Spring Scheduler` (built-in), `Temporal` |
| CDN | Amazon CloudFront | managed | Or `Cloudflare`, `Azure CDN`; omit if backend doesn't serve assets |

---

## Linting & Code Quality

| Tool | Canonical DTR Name | Notes |
|---|---|---|
| Static analysis | SpotBugs | Common; often paired with SonarQube |
| Style enforcement | Checkstyle | Standard Java style checker; often enforced in CI |
| PMD | PMD | Optional duplicate/dead code analysis |
| Coverage | JaCoCo | Standard Java code coverage tool |

---

## Common Tool Pairings

| Stack Type | Typical Combination |
|---|---|
| Spring Boot monolith | Spring Boot 3 + Spring Data JPA + PostgreSQL + JUnit 5 + Mockito + SLF4J + Logback + GitHub Actions |
| Spring microservices | Spring Boot 3 + Spring Cloud + Kafka + Redis + Resilience4j + GKE + Terraform |
| Quarkus native | Quarkus 3 + Hibernate Reactive + PostgreSQL + Kafka + SmallRye + GraalVM |
| GCP-hosted | Spring Boot + Cloud SQL + Google Secret Manager + Google Cloud Monitoring + GKE + Google Artifact Registry |
