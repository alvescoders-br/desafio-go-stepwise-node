# bootstrapping-runtime-environment — Phase A: Stack Detection

## Context Contract

- **Inputs:** `BOOT_INDEX.source_path`, optional `BOOT_INDEX.dtr_path`
- **Outputs:** `BOOT_INDEX.stack` fully populated; entries in `BOOT_INDEX.decisions_log`
- **Carries Forward:** `BOOT_INDEX.stack` — every downstream phase reads `language`, `package_manager`, `orm`, `db_engine`, `needs_redis`, `needs_queue` from this
- **Flush After:** Raw source-tree listings and full manifest file contents — drop after extracting signals. Only the structured `stack` survives.
- **Dependency:** Step 1 (Initialize) must be COMPLETE
- **H1 Title:** `# Phase A — Stack Detection`

## Mode-Specific Behavior

- **BUILD:** Run full detection. Read every relevant manifest. Read DTR when provided.
- **REPAIR:** Skip entirely when no directive targets `stack` or `phase-a`. When targeted, re-run from scratch and overwrite `BOOT_INDEX.stack`. Preserve `services_running` and `migrations_applied` from prior run.
- **RESUME:** Not applicable — this phase is fast (< 30s) and idempotent.

---

## Detection Order (first match wins per category)

### Language

| Signal | Verdict |
|---|---|
| `package.json` present | `node` |
| `pyproject.toml` or `requirements.txt` or `Pipfile` | `python` |
| `pom.xml` or `build.gradle` or `build.gradle.kts` | `java` |
| `Gemfile` | `ruby` |
| `go.mod` | `go` |
| `*.csproj` or `*.sln` | `dotnet` |
| none of the above | `unknown` — STOP-GATE: register blocker and exit phase |

### Framework

Read the manifest's dependency list (`package.json:dependencies`, `pyproject.toml:[tool.poetry.dependencies]`, etc.).

| Language | Framework signal (dependency name) | Verdict |
|---|---|---|
| node | `@nestjs/core` | `nest` |
| node | `express` | `express` |
| node | `fastify` | `fastify` |
| node | `next` | `next` |
| python | `fastapi` | `fastapi` |
| python | `django` | `django` |
| python | `flask` | `flask` |
| java | `org.springframework.boot` in pom/gradle | `spring-boot` |
| ruby | `rails` in Gemfile | `rails` |
| go | `github.com/gin-gonic/gin` | `gin` |
| go | `github.com/labstack/echo` | `echo` |
| (none matched) | — | `unknown` (continue — not a STOP) |

### Package Manager

| Lockfile present | Verdict |
|---|---|
| `package-lock.json` | `npm` |
| `pnpm-lock.yaml` | `pnpm` |
| `yarn.lock` | `yarn` |
| `bun.lockb` | `bun` |
| `Pipfile.lock` | `pipenv` |
| `poetry.lock` | `poetry` |
| `requirements.txt` only | `pip` |
| `mvnw` or `pom.xml` only | `maven` |
| `gradlew` or `build.gradle*` | `gradle` |
| `Gemfile.lock` | `bundler` |

### ORM

| Signal (in order) | Verdict |
|---|---|
| `prisma/schema.prisma` exists | `prisma` |
| dependency `typeorm` AND `data-source.ts` or `entities/` dir | `typeorm` |
| dependency `drizzle-orm` | `drizzle` |
| `alembic.ini` exists OR dependency `sqlalchemy` | `sqlalchemy` |
| dependency `mongoose` | `mongoose` (NoSQL — db_engine becomes `mongodb` automatically) |
| dependency `hibernate-core` or `spring-data-jpa` | `hibernate` |
| `db/migrate/` dir AND ruby | `activerecord` |
| none | `none` |

**Conflict resolution:** when both `prisma` AND `typeorm` appear in manifest, prefer the one with a config file present (schema.prisma vs data-source.ts). If both present, log conflict to `decisions_log` and prefer the first declared in dependencies.

### DB Engine

| Signal | Verdict |
|---|---|
| `prisma/schema.prisma` contains `provider = "postgresql"` | `postgres` |
| `prisma/schema.prisma` contains `provider = "mysql"` | `mysql` |
| `prisma/schema.prisma` contains `provider = "sqlite"` | `sqlite` |
| `prisma/schema.prisma` contains `provider = "mongodb"` | `mongodb` |
| dependency `mongoose` OR `pymongo` | `mongodb` |
| dependency `pg` OR `psycopg2` OR `psycopg` OR `asyncpg` | `postgres` |
| dependency `mysql2` OR `mysql-connector-python` OR `PyMySQL` | `mysql` |
| dependency `better-sqlite3` OR `aiosqlite` | `sqlite` |
| no DB dependency found | `none` |

### Needs Redis

Single check: any of `ioredis`, `redis`, `redis-py`, `jedis`, `sidekiq`, `bull`, `bullmq`, `celery` in the dependency list. The `celery` signal also forces `needs_queue` (broker = redis or rabbit, decided by config).

### Needs Queue

| Dependency | Queue kind |
|---|---|
| `amqplib`, `kombu` (rabbit URL), `spring-amqp` | `rabbit` |
| `@aws-sdk/client-sqs`, `boto3` with `sqs` references | `sqs` |
| `bull`, `bullmq` | `redis-streams` |
| `celery` without rabbit config | `redis-streams` |

---

## DTR Priority Override

When `dtr_path` is provided AND the DTR is loadable AND its lifecycle classification for
Backend (or Frontend, for SSR apps) is `production-ready` or `stable`:

1. Read the DTR's Backend tab declared `language`, `framework`, `ORM`, `database`.
2. If the DTR values disagree with source-code inference, **the DTR wins**.
3. Log the conflict to `decisions_log` with:
   - `phase: "phase-a"`
   - `decision: "DTR override: source said {X}, DTR said {Y}, using DTR"`
   - `evidence: "dtr_path:#Backend.ORM"` (cite the DTR section)

When DTR lifecycle is `experimental` or `not-applicable`, source-code signals win and the
DTR is logged as supplementary evidence only.

---

## Source Evidence Recording

Every entry in `BOOT_INDEX.stack` MUST carry at least one row in `stack.source_evidence`:

```
stack.source_evidence = [
  { signal: "language=node",          file_path: "{source_path}/package.json" },
  { signal: "framework=nest",         file_path: "{source_path}/package.json:dependencies.@nestjs/core" },
  { signal: "orm=prisma",             file_path: "{source_path}/prisma/schema.prisma" },
  { signal: "db_engine=postgres",     file_path: "{source_path}/prisma/schema.prisma:datasource.provider" },
  { signal: "needs_redis=true",       file_path: "{source_path}/package.json:dependencies.ioredis" },
]
```

Empty `source_evidence` for any populated stack field → fidelity check fails, register
open question.

---

## Source Fidelity Check (before writing)

- [ ] Every populated field in `stack` has at least one row in `source_evidence`
- [ ] Conflicting signals (e.g. prisma + typeorm) are logged to `decisions_log` with the conflict resolution rule cited
- [ ] DTR overrides (when present) are logged with `evidence: dtr_path:#Section`
- [ ] `language == unknown` → `BOOT_INDEX.blockers += { kind: stack_unknown }` AND skip is logged as decision
- [ ] No technology guessed without source — if the signal is absent, the field is `unknown` or `none`, never invented

## Post-Section Protocol

1. **Update** `BOOT_INDEX.stack` (all fields), `BOOT_INDEX.decisions_log` (additions for this phase)
2. **Update** `_progress.json`: `completed: 1`, `items[0] = { phase: "stack-detection", status: "COMPLETE" }`
3. **Flush** raw manifest file contents and tree listings from memory — keep only `BOOT_INDEX.stack`
4. **Verify** every field in `stack` is set (use `unknown`/`none` for missing, never null)
5. **Log:** `"Phase A COMPLETE. Stack: {language}/{framework}, ORM: {orm}, DB: {db_engine}, needs_redis: {needs_redis}, needs_queue: {needs_queue or 'no'}"`
