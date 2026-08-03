# Node.js / TypeScript — DTR Field Reference

Use this file when the ASD describes a backend built with Node.js (TypeScript or JavaScript).

---

## General Development

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Language | TypeScript | 5.x | Use `JavaScript` only if the project explicitly avoids TypeScript |
| IDE | Visual Studio Code | — | WebStorm / IntelliJ IDEA when team prefers JetBrains |
| Dependency Management | npm | 10.x | Alternatives: `yarn` (4.x), `pnpm` (9.x), `bun` (1.x) |
| Artifact Repository | npm Registry | SaaS | Private: `GitHub Packages`, `JFrog Artifactory`, `AWS CodeArtifact` |
| Version Control | GitHub | SaaS | Or `GitLab`, `Azure DevOps`, `Bitbucket` |
| CI/CD Quality | SonarCloud | SaaS | Self-hosted: `SonarQube`; lightweight: `ESLint` (note in Toolchain Notes) |
| Dynamic/Runtime Analysis | Clinic.js | — | Or `0x`, `Node.js --inspect` (built-in); omit if not used |
| Mocking | Jest | 29.x | Alternatives: `Sinon`, `Vitest` |
| Unit Testing | Jest | 29.x | `Vitest` (faster, ESM-native); `Mocha` (older stacks) |
| Performance Testing | k6 | — | Or `Autocannon`, `Artillery`, `Apache JMeter` |
| Logging | Winston | 3.x | Or `Pino` (high-performance), `Bunyan` |
| Monitoring | Datadog | SaaS | Or `New Relic`, `Dynatrace`, `Prometheus + Grafana`, `AWS CloudWatch` |
| CI/CD Pipeline Automation | GitHub Actions | — | Or `GitLab CI`, `Jenkins`, `CircleCI`, `Azure Pipelines` |

---

## API

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Framework / Type | NestJS | 10.x | Alternatives: `Fastify` (4.x), `Express` (4.x / 5.x), `Hono` (4.x), `Koa` |
| Gateway | Kong Gateway | — | Or `AWS API Gateway`, `NGINX`, `Traefik`, `Azure API Management` |
| API Specification/Design | OpenAPI | 3.1 | NestJS: via `@nestjs/swagger`; Fastify: via `@fastify/swagger` |
| API Lifecycle Management | Fastify versioning | — | Or `nestjs-versioning`; omit if no versioning strategy |
| API Documentation UI | Swagger UI | — | Or `ReDoc`, `Scalar` |

---

## Microservices

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Microservice Toolkit | NestJS | 10.x | Or `Fastify` (when used as microservice base), `Moleculer`, `Dapr` |
| Service Discovery | Kubernetes Services | — | Or `HashiCorp Consul`; usually handled at orchestration layer |
| Service Registry | Kubernetes Services | — | Omit if no dedicated registry beyond Kubernetes |
| HealthCheck | @nestjs/terminus | — | Or custom Fastify health route; omit if not implemented |
| Load Balancer | Kubernetes Ingress | — | Or `NGINX`, `AWS ALB`; often managed by orchestration |
| Container Orchestration | Amazon EKS | managed | Or `GKE`, `AKS`, `Amazon ECS`; omit if Lambda/serverless |
| Image Registry | Amazon ECR | managed | Or `Google Artifact Registry`, `Azure Container Registry`, `Docker Hub` |
| Messaging Framework | KafkaJS | 2.x | Or `bullmq` (1.x), `amqplib` (RabbitMQ), `@aws-sdk/client-sqs` |
| Message Broker | Apache Kafka | — | Or `RabbitMQ`, `Amazon SQS`, `Azure Service Bus` |
| Distributed Cache (L2) | Redis | 7.x | Via `ioredis` or `@nestjs/cache-manager`; or `Memcached` |
| Resiliency Patterns | Cockatiel | — | Or `nestjs-resilience`, custom retry logic; omit if not implemented |
| Log Analysis Platform | Datadog Logs | SaaS | Or `ELK Stack`, `AWS CloudWatch Logs`, `Grafana Loki` |
| Trace Backend | AWS X-Ray | managed | Or `Datadog APM`, `Jaeger`, `Tempo`, `OpenTelemetry Collector` |
| CQRS Mediator | — | — | No widely adopted CQRS mediator in Node.js; omit unless using custom |

---

## Infrastructure Management

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Infrastructure Definition Tool | Terraform | 1.x | Or `AWS CDK` (TypeScript), `Pulumi` (TypeScript), `Bicep` |
| Server Templating | — | — | Omit for container-based workloads; use `HashiCorp Packer` for VM images |
| Secrets Management | AWS Secrets Manager | managed | Or `HashiCorp Vault`, `Google Secret Manager`, `Azure Key Vault` |
| Version Control | GitHub | SaaS | Same as application repo or separate IaC repo |

---

## Other Tools

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| AuthZ/AuthN | Passport.js | 0.7.x | Or `Keycloak` (OIDC), `Auth0`, `AWS Cognito`, `Microsoft Entra ID` |
| Database | PostgreSQL | 16 | Or `MySQL`, `MongoDB`, `DynamoDB`, `Redis` (primary or secondary) |
| ORM | Prisma | 5.x | Or `TypeORM` (0.3.x), `Drizzle` (0.30.x), `Sequelize` (6.x), `Mongoose` (MongoDB) |
| Background Jobs/Scheduling | BullMQ | 5.x | Or `Agenda`, `node-cron`, `Temporal`; serverless: `AWS Lambda` scheduled |
| CDN | Amazon CloudFront | managed | Or `Cloudflare`, `Azure CDN`, `Fastly`; omit if backend does not serve assets |

---

## Linting & Formatting (CI/CD Quality context)

| Tool | Canonical DTR Name | Notes |
|---|---|---|
| Code style | ESLint + Prettier | Most common combination; include in CI/CD Quality or as a note |
| All-in-one | Biome | Faster alternative to ESLint + Prettier |
| Type checking | tsc (TypeScript Compiler) | Built-in; note in Toolchain Notes if strict mode is enforced |

---

## Common Tool Pairings

| Stack Type | Typical Combination |
|---|---|
| NestJS REST API | NestJS + TypeORM/Prisma + PostgreSQL + Jest + GitHub Actions |
| Fastify Microservice | Fastify + Prisma + PostgreSQL + KafkaJS + Redis + Jest |
| Serverless (Lambda) | TypeScript + AWS Lambda + DynamoDB/Aurora + SQS + AWS CloudWatch |
| Event-driven | NestJS + KafkaJS + Apache Kafka + Redis + PostgreSQL + Datadog |
