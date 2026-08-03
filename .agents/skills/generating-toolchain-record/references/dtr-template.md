# Development Toolchain Record

**Project:** {Project Name}
**Generated from:** Architecture Specification Document
**Date:** {YYYY-MM-DD}

---

<!--
FORMATTING RULES (strip this block from the final output)

Tool names: use the official name as it appears in the tool's documentation.
  ✓ PostgreSQL   ✗ postgres, PG
  ✓ Visual Studio Code   ✗ VSCode, vscode
  ✓ Entity Framework Core   ✗ EF Core, EFCore

Versions: no leading "v" — use 17.0.1, not v17.0.1
  - Known version → 17.0.1 or 17.0
  - Cloud / SaaS service → SaaS (or leave blank)
  - Managed / auto-updated → managed or latest
  - Decision pending → TBD

Multiple tools in one field: comma-separated — Tool1, Tool2
Framework built-ins: note explicitly — Next.js (built-in), HttpClient (built-in)
Inferred values: mark with (inferred)

Field inclusion:
  - Include a field only if it applies to this project.
  - Omit fields that genuinely do not apply — do not write N/A.
  - Use TBD when a tool will be used but has not been decided yet.
  - Fields marked † below are optional and should be omitted when not applicable.
  - The Microservices section must be omitted entirely for monolithic architectures.

Multiple backend technologies: create one Backend section per technology,
labeled Backend — .NET, Backend — Java, Backend — Node.js, etc.
-->

---

## Backend [— {Technology Label if multiple}]

> Type: {e.g., Node.js REST API · Microservices | .NET Web API · Monolith}

### General Development

| Field | Tool | Version |
|---|---|---|
| Language | | |
| Framework † | | |
| IDE | | |
| Dependency Management | | |
| Artifact Repository † | | |
| Version Control | | |
| CI/CD Quality † | | |
| Dynamic/Runtime Analysis † | | |
| Mocking † | | |
| Unit Testing | | |
| Performance Testing † | | |
| Logging | | |
| Monitoring † | | |
| CI/CD Pipeline Automation | | |

### API

| Field | Tool | Version |
|---|---|---|
| Gateway † | | |
| API Specification/Design † | | |
| API Lifecycle Management † | | |
| API Documentation UI † | | |

### Microservices

> Omit this entire section for monolithic architectures.

| Field | Tool | Version |
|---|---|---|
| Microservice Toolkit | | |
| Service Discovery † | | |
| Service Registry † | | |
| HealthCheck † | | |
| Load Balancer † | | |
| Container Orchestration † | | |
| Image Registry † | | |
| Messaging Framework † | | |
| Message Broker † | | |
| Distributed Cache (L2) † | | |
| Resiliency Patterns † | | |
| Log Analysis Platform † | | |
| Trace Backend † | | |
| CQRS Mediator † | | |

> **Messaging Framework vs. Message Broker:** Framework = in-code library (e.g., MassTransit); Broker = underlying platform (e.g., RabbitMQ). If using a broker SDK directly without an abstraction layer, enter the broker name in both fields.
> **Log Analysis Platform vs. Trace Backend:** if a single platform covers both (e.g., Datadog), enter it in both fields.

### Infrastructure Management

| Field | Tool | Version |
|---|---|---|
| Infrastructure Definition Tool † | | |
| Container Orchestration † | | |
| Image Registry † | | |
| Server Templating † | | |
| Secrets Management † | | |
| Version Control † | | |

### Other Tools

| Field | Tool | Version |
|---|---|---|
| AuthZ/AuthN † | | |
| CDN † | | |
| Database | | |
| ORM † | | |
| Background Jobs/Scheduling † | | |

---

## Frontend (Web) [— {Technology Label if multiple}]

> Type: {e.g., React SPA | Next.js SSR | Angular Enterprise App}

### General

| Field | Tool | Version |
|---|---|---|
| Language | | |
| Framework | | |
| State Management † | | |
| i18n / l10n † | | |
| Auth Handling † | | |
| Marketing Analytics † | | |
| Data Fetching | | |
| Search UI † | | |
| Real-time † | | |
| Offline Support † | | |
| Data Compliance (UI) † | | |
| CMS Integration † | | |
| Unit Testing | | |

### Project & Design

| Field | Tool | Version |
|---|---|---|
| CSS Approach | | |
| Component Docs † | | |

### Build, Tooling & Deployment

| Field | Tool | Version |
|---|---|---|
| Version Control | | |
| Package Manager | | |
| Linting & Formatting | | |
| Hosting | | |
| CDN † | | |
| Error Monitoring † | | |
| CI/CD | | |
| CI Audit † | | |
| Bundler † | | |

### Other Tools

| Field | Tool | Version |
|---|---|---|
| {Tool name or category} † | | |

---

## Mobile [— {Platform Label if multiple}]

> Type: {e.g., Flutter · iOS + Android | React Native · iOS + Android | Kotlin · Android}

### General Development

| Field | Tool | Version |
|---|---|---|
| Language | | |
| Framework | | |
| IDE | | |
| Dependency Management | | |
| Artifact Repository † | | |
| Version Control | | |
| Code Review Tool | | |
| Static and Dynamic Code Quality Inspection | | |
| Lint | | |
| Mocking † | | |
| Unit Testing | | |
| Monitoring † | | |
| CI/CD Pipeline Automation | | |
| App Distribution for Testing † | | |
| Security and Obfuscation Tool † | | |

> Platform defaults — Language / Lint / Dependency Management:
> Flutter → Dart / Dart Analyzer / Pub
> React Native → TypeScript / ESLint / npm (or yarn/pnpm)
> Kotlin (Android) → Kotlin / Ktlint / Gradle
> Swift (iOS) → Swift / SwiftLint / Swift Package Manager

### Monitoring

| Field | Tool | Version |
|---|---|---|
| Performance † | | |
| Analytics † | | |
| Crash Monitoring † | | |

### Other Tools

| Field | Tool | Version |
|---|---|---|
| {Tool name or category} † | | |

---

## Toolchain Notes

> Mode-specific subsections: greenfield runs typically populate only TBD / Inferred / Fields Omitted. Brownfield (extract) runs additionally populate Migration / Upgrade / Legacy / Planned / Gaps. Omit any subsection with no entries.

### Migration Entries  *(brownfield only)*
- **{Field name}:** {current_tool vX} → {target_tool vY} — {ASD/PB section reference describing the migration; expected timeline if known}

### Upgrade Entries  *(brownfield only)*
- **{Field name}:** {tool vX_current} → {tool vY_target} — {ASD/PB section reference; timeline if known}

### Legacy Entries  *(brownfield only — tools currently in production but slated for decommission)*
- **{Field name}:** {tool vX} `(legacy)` — {Decommission plan or rationale; ASD/PB section reference}

### Planned Entries  *(committed in ASD but not yet deployed)*
- **{Field name}:** {tool} `planned` — {ASD section reference; deployment trigger}

### TBD Entries
- **{Field name}:** {What decision is pending and who should make it.}

### Inferred Entries
- **{Field name}:** {Value} — {Reasoning; cite the ASD section or architecture pattern that led to the inference.}

### Gaps  *(brownfield only — categories that should have a known value but are undocumented)*
- **{Field name}:** Documentation missing — {Action item: who should document and where.}

### Fields Omitted
- **{Field name}:** Not applicable — {Cite the ASD section or explicit exclusion that justifies the omission.}
