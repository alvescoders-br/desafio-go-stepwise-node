---
name: bootstrapping-runtime-environment
description: >
  Prepares a local runtime so a service produced by `code-development` can actually boot.
  Detects language/framework/ORM/database from source code and an optional Development Toolchain
  Record (DTR), provisions or reuses local services (Postgres, MySQL, Mongo, Redis), synthesizes
  a `.env` from config schemas, runs ORM generate + migrate, and surfaces unresolvable blockers
  (missing secrets, port collisions, prod-only credentials) in a structured report. Output is a
  single agent-native bootstrap report — zero prose, structured fields only. Supports BUILD and
  REPAIR modes. Use when preparing a freshly generated codebase to launch for the first time,
  when re-running runtime validation after a fix, or when QE automation needs a matching local
  backing store.
license: Proprietary
metadata:
  author: aipods-team
  version: 1.0.0
  category: deployment
  tags: runtime, environment, bootstrap, database, migrations
compatibility: Requires Docker (when DB strategy uses containers), Python 3.11, Node, or the language toolchain implied by the source code.
---

# bootstrapping-runtime-environment — Agent-Native Skill

## Quick Start

Bootstraps the local execution environment for a service produced by `code-development`.
Primary output is a single **bootstrap report** — not a runbook, not a script. The report
records every decision taken (stack detected, services provisioned, env vars synthesized,
migrations applied) and lists structured blockers that need operator action.

The skill reads the source tree (and an optional DTR) to decide what to provision, runs
non-interactive provisioning commands, then emits `BOOT-SPEC-{SESSION_ID}.md` and a
ready-to-source `.env` file. Downstream consumer `launching-app` reads the env file path
and `services_running[]` directly from the report.

---

## Output Architecture

```
{output_folder}/
├── BOOT-SPEC-{SESSION_ID}.md   ← Bootstrap report (decisions, services, env vars, blockers)
├── .env                         ← Generated env file (sourced by launching-app)
├── BOOT-AUDIT-{SESSION_ID}.md  ← Lightweight session metadata
└── _progress.json               ← RUNNING → COMPLETED transition tracker
```

**Why a single report.** The runtime is one cohesive state — stack, services, env, DB readiness
are tightly coupled. Splitting into per-service files would force the downstream consumer to
re-stitch state. The report is < 600 lines for typical engagements and trivially loadable.

---

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source_path` | string | Yes | — | Absolute path to the code-development source root the runtime must boot |
| `output_folder` | string | Yes | — | Absolute path where `BOOT-SPEC-*.md`, `.env`, and audit are written. This IS the output location — files are written directly here, no subfolder is created. |
| `project_name` | string | No | `project` | Project slug, used to namespace Docker container names (e.g. `{project_name}-postgres`) |
| `dtr_path` | string | No | — | Development Toolchain Record produced by `software-architecture`. Preferred source for stack identification. |
| `env_template_path` | string | No | — | Path to a `.env.example` or operator-supplied template. When absent, the skill synthesizes env vars from config schemas it discovers. |
| `db_strategy` | enum | No | `auto` | One of `auto`, `reuse-existing-docker`, `spin-up-new-docker`, `sqlite-in-memory`. Forces a provisioning path when auto-detection is wrong. |
| `existing_db_url` | string | No | — | Verbatim `DATABASE_URL` override. When set, the skill skips DB provisioning entirely and uses this URL. |
| `failure_feedback` | string | No | — | REPAIR mode directives describing what to fix from a previous bootstrap run |

**If any Required parameter is not defined, ABORT EXECUTION.**

---

## Prerequisites

- [ ] `source_path` exists on disk and contains at least one recognised stack signal (`package.json`, `requirements.txt`, `pom.xml`, `pyproject.toml`, `Gemfile`)
- [ ] `output_folder` is writable
- [ ] `docker` CLI is available when `db_strategy` resolves to `reuse-existing-docker` or `spin-up-new-docker`
- [ ] The language toolchain implied by the source code is installed (node + npm/pnpm/bun; python + pip; java + maven/gradle; ruby + bundler)

---

## BOOT_INDEX — Carry-Forward Contract

Initialize at Step 1. Update after every phase. This is the SOLE source of truth between
phases. Never carry full file contents or command output — only IDs, paths, decisions,
and status.

```
BOOT_INDEX = {
  session_id: string,
  mode: BUILD | REPAIR,
  output_folder: string,
  source_path: string,
  project_name: string,

  // Phase A — Stack detection
  stack: {
    language: string,             // node | python | java | ruby | go | dotnet | unknown
    framework: string,            // nest | express | fastify | fastapi | django | spring | rails | unknown
    package_manager: string,      // npm | pnpm | bun | yarn | pip | poetry | maven | gradle | bundler | unknown
    orm: string,                  // prisma | typeorm | drizzle | sqlalchemy | hibernate | activerecord | none
    db_engine: string,            // postgres | mysql | mongodb | sqlite | none
    needs_redis: boolean,
    needs_queue: string | null,   // rabbit | sqs | redis-streams | null
    source_evidence: [{ signal, file_path }]  // why each decision was made
  },

  // Phase B — Service provisioning
  services_running: [
    { name, kind, host, port, container_id?, container_name?, reused: boolean }
  ],
  port_collisions: [{ port, occupying_process }],

  // Phase C — Env + migrations
  env_file_path: string,
  env_keys_synthesized: [string],
  env_blockers: [{ kind, key, description, suggested_remediation }],
  migrations_applied: [{ tool, command, duration_ms, exit_code }],
  db_ready: boolean,

  // Phase D — Output
  spec_path: string,              // BOOT-SPEC-{SESSION_ID}.md
  audit_path: string,             // BOOT-AUDIT-{SESSION_ID}.md
  env_status: READY | BLOCKED,    // READY when zero env_blockers, BLOCKED otherwise

  // Audit trail
  repair_log: [{ directive, target, outcome }],
  decisions_log: [{ phase, decision, evidence }],
  blockers: [],
  open_questions: []
}
```

---

## Workflow

### Step 1: Initialize & Environment Setup

**FIRST ACTION — MANDATORY:** Write `_progress.json` to `{output_folder}` before any other
file write. This prevents the orchestrator from sending SIGINT.

```
WRITE {output_folder}/_progress.json:
{
  "skill": "bootstrapping-runtime-environment",
  "session_id": "initializing",
  "status": "RUNNING",
  "started_at": "<ISO timestamp>",
  "completed_at": null,
  "total": 4,
  "completed": 0,
  "items": []
}
```

**Command:**
```
1. SESSION_ID = [Extract from EXECUTION METADATA]
   ## Sourced from the harness per execution-protocol.md §1. Do NOT generate locally.
   ## SESSION_ID goes in FILENAMES only, never in folder names.

2. REPAIR detection:
   IF failure_feedback is non-empty:
     MODE = REPAIR
     FOLDER = output_folder (already exists)
     PRIOR_FILE = find BOOT-SPEC-*.md in FOLDER
     IF PRIOR_FILE not found → write Gap Report → EXIT
     LOAD PRIOR_FILE → PRIOR_SPEC → PRIOR_DECISIONS
     SESSION_ID = extract session_id from PRIOR_FILE filename
     PARSE failure_feedback → REPAIR_DIRECTIVES [{ target, instruction, reason }]
     ## REPAIR examples for this skill:
     ##   target = "phase-b-service-provisioning"  → re-run service detection only
     ##   target = "env_keys_synthesized.DATABASE_URL"  → fix one env var
     ##   target = "migrations"  → re-run migrations only
     NOTE: output_folder MUST already exist. Never mkdir for REPAIR.
   ELSE:
     MODE = BUILD
     CREATE output_folder (mkdir -p — idempotent, safe on re-run)
     PRIOR_FILES = list BOOT-SPEC-*.md in output_folder
     IF PRIOR_FILES not empty:
       LOG to decisions_log: "Prior artifacts present: {PRIOR_FILES}. This run produces
                              BOOT-SPEC-{SESSION_ID}.md. To repair the prior file instead,
                              re-run with failure_feedback."

3. Initialize BOOT_INDEX with session_id, mode, output_folder, source_path, project_name.

4. Zero Invention Policy: every decision recorded in BOOT_INDEX.decisions_log MUST carry an
   evidence field pointing to a file or command output. No inferences without source.

5. Memory Bank:
   READ context-pack/active-context.md → prior session state (if exists)
   APPEND to context-pack/progress.md → "Session {SESSION_ID} started: {date} | bootstrapping-runtime-environment | {MODE}"

6. STOP-GATE — abort if:
   - source_path does not exist on disk
   - source_path contains zero recognised stack signals (package.json / requirements.txt / pom.xml / pyproject.toml / Gemfile)
   - output_folder is not writable
   - db_strategy ∉ { auto, reuse-existing-docker, spin-up-new-docker, sqlite-in-memory }
   LOG: "Step 1 COMPLETE. Session: {SESSION_ID}, Mode: {MODE}"
```

---

### Step 2: Detect Stack & ORM

Read `references/phase-a-stack-detection.md` before executing this step.

**Command:**
```
IF mode == REPAIR AND no REPAIR_DIRECTIVE targets "stack" or "phase-a":
  LOAD BOOT_INDEX.stack from PRIOR_SPEC
  LOG: "Step 2 skipped (REPAIR, no directive)."
  GOTO Step 3.

LOAD source_path tree (one level deep + key files).
LOAD dtr_path content if provided.

DETECT in this order (first match wins per category):
  - Language: by manifest file (package.json → node, pyproject.toml → python, etc.)
  - Framework: by dependency in manifest (nest, express, fastapi, django, spring, rails)
  - Package manager: by lockfile (package-lock.json → npm, pnpm-lock.yaml → pnpm, Pipfile.lock → pipenv)
  - ORM: by config file or dependency (prisma/schema.prisma → prisma; entities/*.ts + typeorm dep → typeorm; alembic.ini → sqlalchemy)
  - DB engine: by ORM provider declaration OR explicit dependency
  - Needs Redis: by dependency (ioredis, redis, redis-py, jedis, sidekiq)
  - Needs queue: by dependency (amqplib, kombu, spring-amqp)

FOR EACH detection:
  source_evidence += { signal: <signal text>, file_path: <path> }

FIDELITY CHECK before writing BOOT_INDEX:
  - Every entry in stack carries a source_evidence row
  - Conflicting signals (e.g. prisma AND typeorm in package.json) → log as decision conflict, prefer first declared

UPDATE BOOT_INDEX: stack, decisions_log += "stack detected: {language}/{framework}/{orm}/{db_engine}"
UPDATE _progress.json: completed=1
LOG: "Step 2 COMPLETE. Stack: {language}/{framework}, ORM: {orm}, DB: {db_engine}."
```

---

### Step 3: Provision Services

Read `references/phase-b-service-provisioning.md` before executing this step.

**Command:**
```
IF mode == REPAIR AND no REPAIR_DIRECTIVE targets "services" or "phase-b":
  LOAD BOOT_INDEX.services_running from PRIOR_SPEC
  LOG: "Step 3 skipped (REPAIR, no directive)."
  GOTO Step 4.

IF existing_db_url is set:
  PARSE existing_db_url → { host, port, db_name, user }
  services_running += { name: db_name, kind: db_engine, host, port, reused: true }
  GOTO Step 4 (skip provisioning).

IF stack.db_engine == none AND not needs_redis AND not needs_queue:
  LOG: "No services needed."
  GOTO Step 4.

DECIDE provisioning per service (db, redis, queue):
  IF db_strategy == sqlite-in-memory OR stack.db_engine == sqlite:
    services_running += { kind: sqlite, host: "file::memory:", reused: false }
    CONTINUE
  
  IF db_strategy == auto OR reuse-existing-docker:
    RUN: docker ps --filter "name={kind}" --format "{{.Names}}\t{{.Ports}}"
    IF a compatible container is found AND port is reachable:
      PROBE: connect to container's exposed port
      IF success: services_running += { reused: true, container_id, ... }; CONTINUE
  
  IF db_strategy == auto AND no reusable container OR db_strategy == spin-up-new-docker:
    SPIN UP named container: docker run -d --name {project_name}-{kind} -p {port}:{default_port} {image}
    WAIT for readiness (max 30s, exponential backoff probe)
    services_running += { reused: false, container_id, container_name, ... }

PORT COLLISION HANDLING:
  IF target port is occupied by an unrelated process:
    port_collisions += { port, occupying_process }
    TRY: increment port (5432 → 5433 → 5434 …), update env later
    IF no port available within 5 attempts → register blocker { kind: port_collision }

FIDELITY CHECK:
  - Every entry in services_running has either container_id (for spun-up) OR explicit reused=true with rationale
  - All required services per stack.* signals are present or registered as blocker

UPDATE BOOT_INDEX: services_running, port_collisions, decisions_log
UPDATE _progress.json: completed=2
LOG: "Step 3 COMPLETE. Services: {N} running ({M} reused, {K} spun-up)."
```

---

### Step 4: Synthesize .env & Run Migrations

Read `references/phase-c-env-and-migrations.md` before executing this step.

**Command:**
```
IF mode == REPAIR AND no REPAIR_DIRECTIVE targets "env" or "migrations" or "phase-c":
  LOAD env_file_path, db_ready from PRIOR_SPEC
  LOG: "Step 4 skipped (REPAIR, no directive)."
  GOTO Step 5.

=== ENV SYNTHESIS ===

IF env_template_path is provided AND file exists:
  COPY env_template_path → output_folder/.env (preserving keys)
  TEMPLATE_KEYS = parse keys from template
ELSE:
  DISCOVER required env keys per stack:
    - node/nest: src/**/config.schema.ts, app.config.ts, ConfigService.get() calls
    - python: pydantic Settings classes, settings.py, os.environ.get() calls
    - java/spring: application.yml @Value("${X}") references, ConfigurationProperties
    - ruby/rails: config/application.rb, ENV["X"] references
  TEMPLATE_KEYS = union of discovered keys

FOR EACH key in TEMPLATE_KEYS:
  LOAD source for key:
    - DATABASE_URL → synthesize from services_running[kind=db]: postgresql://{user}:{pass}@{host}:{port}/{db}
    - REDIS_URL / REDIS_HOST → from services_running[kind=redis]
    - APP_ENV / NODE_ENV / SPRING_PROFILES_ACTIVE → "development"
    - PORT → next available port starting 3000
    - AWS_REGION / cloud-region keys → default "eu-west-1" but flag as "synthesized-default"
    - AUTH_* / OIDC_* in dev mode → mock_oidc values where applicable (per source code defaults)
    - any key matching ^(SECRET|API_KEY|TOKEN|PASSWORD)_ that has no dev default
       → env_blockers += { kind: missing_secret, key, description, suggested_remediation: "operator must supply" }
       → write key with placeholder `<REQUIRED_OPERATOR_INPUT>`

WRITE output_folder/.env atomically (write to tmp, mv on success)
env_file_path = output_folder/.env
env_keys_synthesized = list of keys with concrete values

=== MIGRATIONS ===

IF stack.orm == prisma:
  RUN: cd source_path && npx prisma generate
  IF prisma/migrations/ directory exists with prior migrations:
    RUN: npx prisma migrate dev --name auto-{SESSION_ID} --skip-seed
  ELSE:
    RUN: npx prisma db push --accept-data-loss --skip-generate
  CAPTURE: exit_code, stderr
  IF exit_code != 0 AND stderr mentions "CREATEDB" privilege:
    RUN: docker exec {db-container} psql -U postgres -c "ALTER USER {dbuser} CREATEDB;"
    RETRY the prisma command once
  migrations_applied += { tool: prisma, command, duration_ms, exit_code }

IF stack.orm == typeorm:
  RUN: cd source_path && npx typeorm migration:run -d {datasource path}
  migrations_applied += { tool: typeorm, command, duration_ms, exit_code }

IF stack.orm == sqlalchemy:
  RUN: cd source_path && alembic upgrade head
  migrations_applied += { tool: alembic, command, duration_ms, exit_code }

(repeat per supported ORM)

db_ready = all migrations_applied[].exit_code == 0
IF NOT db_ready:
  env_blockers += { kind: migration_failed, key: "migrations", description: stderr excerpt, suggested_remediation }

FIDELITY CHECK:
  - .env file exists, non-empty, contains every key in env_keys_synthesized + env_blockers[].key
  - placeholder values <REQUIRED_OPERATOR_INPUT> match env_blockers[].key 1:1

UPDATE BOOT_INDEX: env_file_path, env_keys_synthesized, env_blockers, migrations_applied, db_ready
UPDATE _progress.json: completed=3
LOG: "Step 4 COMPLETE. Env keys: {N} synthesized, {M} blocked. DB ready: {db_ready}."
```

---

### Step 5: Write Bootstrap Report & Audit

Read `references/phase-d-report-and-validation.md` before executing this step.

**Command:**
```
COMPUTE env_status:
  env_status = READY  IF len(env_blockers) == 0 AND db_ready
  env_status = BLOCKED otherwise

UPDATE BOOT_INDEX: env_status, spec_path, audit_path

=== GENERATE BOOT-SPEC ===

GENERATE BOOT-SPEC-{SESSION_ID}.md with this structure (zero prose, structured fields only):

  ## 1. Session
  | Field | Value |
  | session_id | {SESSION_ID} |
  | mode | BUILD | REPAIR |
  | started_at / completed_at | ISO 8601 |
  | env_status | READY | BLOCKED |

  ## 2. Stack
  Table of detected stack components with source_evidence column.

  ## 3. Services Running
  Table of every service in BOOT_INDEX.services_running.

  ## 4. Env Synthesis
  - Keys synthesized: bullet list with sources
  - Blockers: table of env_blockers[] (kind, key, description, suggested_remediation)

  ## 5. Migrations
  Table of migrations_applied[] with exit_code column.

  ## 6. Decisions Log
  Table of decisions_log[] (phase, decision, evidence).

  ## 7. Port Collisions
  Table (may be empty).

  ## 8. Open Questions
  Table (may be empty).

FIDELITY CHECK before writing:
  - Every section heading matches the template above (no renames, no missing sections)
  - Counts in section headings match actual table rows
  - env_status field appears in section 1 AND matches len(env_blockers) == 0 logic
  - No prose paragraphs — every section is tables or lists

WRITE {output_folder}/BOOT-SPEC-{SESSION_ID}.md — MANDATORY TOOL CALL.
spec_path = the written path.

=== GENERATE BOOT-AUDIT ===

GENERATE BOOT-AUDIT-{SESSION_ID}.md (lightweight session metadata):
  - Pattern compliance table (all 7 patterns + Pattern 8)
  - Files written summary
  - Decisions count
  - Skipped steps (REPAIR mode)

WRITE {output_folder}/BOOT-AUDIT-{SESSION_ID}.md — MANDATORY TOOL CALL.
audit_path = the written path.

UPDATE BOOT_INDEX: spec_path, audit_path
UPDATE _progress.json: completed=4
LOG: "Step 5 COMPLETE. Report: {spec_path}. Status: {env_status}."
```

---

### Step 6: Finalize

**LAST ACTION — MANDATORY:**

```
UPDATE _progress.json:
{
  "skill": "bootstrapping-runtime-environment",
  "session_id": "{SESSION_ID}",
  "status": "COMPLETED",
  "completed_at": "<ISO timestamp>",
  "total": 4,
  "completed": 4,
  "items": [
    { "phase": "stack-detection", "status": "COMPLETE" },
    { "phase": "service-provisioning", "status": "COMPLETE" },
    { "phase": "env-and-migrations", "status": "COMPLETE" },
    { "phase": "report-and-validation", "status": "COMPLETE" }
  ]
}

Memory Bank — MANDATORY session-end writes:
  OVERWRITE context-pack/active-context.md with:
    - session_id, status (env_status), decisions count, blockers count
    - key artifacts: spec_path, env_file_path
  APPEND to context-pack/progress.md:
    | {SESSION_ID} | {date} | bootstrapping-runtime-environment | {MODE} | {env_status} | 1 bootstrap report | {env_blockers count} blockers |

Reference execution-protocol.md Section 4 for Memory Bank schema.

LOG: "Skill complete. Spec: {spec_path}. env_status: {env_status}. Blockers: {len(env_blockers)}."
```

---

### Step 7: Emit Harness Outputs Sidecar

**Apply execution-protocol.md Section 11** — Harness Output Sidecar. Mandatory when the prompt contains a `## Run metadata` block. FINAL file write of the run (after BOOT-SPEC verification in Step 5, after Memory Bank in Step 6, after `_progress.json` set to COMPLETED). Without it, the orchestrator falls back to the capability `value_template`, which corrupts `env_file_path` and `bootstrap_spec_path` into doubly-nested folders when the parameter has already been pre-resolved to an absolute path. Downstream `launching-app` then fails to source the `.env`.

**Output parameters this skill produces** (one key per row of the prompt's `## Output parameters` table):

- `env_file_path`: absolute path to the synthesised `.env` written into the resolved output folder.
- `services_running`: JSON-encoded `services_running[]` from BOOT-SPEC.
- `env_status`: `"READY"` | `"BLOCKED"` | `"SKIPPED"`.
- `env_blockers`: JSON-encoded `env_blockers[]` (empty array `[]` when `env_status="READY"`).
- `bootstrap_spec_path`: the resolved `output_folder` parameter VERBATIM as received in the prompt — the folder that holds `BOOT-SPEC-*.md` and `BOOT-AUDIT-*.md`. Do NOT re-prepend `{output_folder}` or `{project_name}`.

**Implementation:** the harness here accepts Bash heredoc for the sidecar write. Execute:

```
cat > {stepwise_outputs_file} << 'OUTPUTS_EOF'
{
  "env_file_path": "{env_file_path}",
  "services_running": {services_running_json},
  "env_status": "{env_status}",
  "env_blockers": {env_blockers_json},
  "bootstrap_spec_path": "{output_folder}"
}
OUTPUTS_EOF
```

`{stepwise_outputs_file}` is the path from the prompt's `## Run metadata` block's `output_file = '...'` line — copy it verbatim, do NOT reconstruct it. JSON-encoded fields (`services_running`, `env_blockers`) MUST be valid JSON arrays — quote strings as needed.

Self-check: `cat {stepwise_outputs_file}` — verify non-empty and valid JSON. If empty, missing, or malformed, re-execute. DO NOT describe output registration in response text — EXECUTE it. No tool calls after this; the next event is `final_response`.

**Execution:** automated

---

## Output Status Protocol

Every field in BOOT-SPEC carries one of:
- `complete` — value populated from source evidence (file, command output, DTR)
- `pending` — required field could not be resolved; registered in open_questions
- `assumption` — value inferred from sensible default (e.g. `AWS_REGION=eu-west-1`); registered in env_blockers OR decisions_log

The downstream consumer (`launching-app`) MUST check env_status before reading env_file_path.

---

## Source Tagging

Every entry in `decisions_log` and `services_running` carries an evidence pointer:

```
evidence: "source_path/package.json:dependencies.@prisma/client"  ← explicit file:field
evidence: "docker ps output 2026-05-15T13:40Z"                    ← command output
evidence: "dtr_path:#Backend.ORM"                                  ← DTR section
evidence: "assumption: AWS_REGION dev default"                     ← assumption (flagged)
```

---

## Upstream Consistency Rules

### 1. Zero Invention Policy
Every entry in BOOT_INDEX.stack and BOOT_INDEX.decisions_log MUST carry an `evidence`
field pointing to a file path, command output, or DTR section. No stack components are
inferred without source.

### 2. DTR Takes Priority
When `dtr_path` is provided AND the DTR's Backend or Frontend tab is `production-ready`
or `stable`, the DTR's declared stack overrides any source-code inference. Log the
conflict to `decisions_log` with `evidence: dtr_path:#Section`.

### 3. ID Format Fidelity
- Container names: `{project_name}-{kind}` (e.g. `art-school-management-postgres`)
- Session ID in filenames only: `BOOT-SPEC-{SESSION_ID}.md`, never in folder names

### 4. Assumption Carry-Forward
Every default value used (e.g. `AWS_REGION=eu-west-1`, dev OIDC mock URLs) is
registered in `decisions_log` with `evidence: "assumption: {reason}"`. The bootstrap
report's section 6 surfaces all assumptions for operator review.

### 5. Source Fidelity Check (Per Phase)
Before writing BOOT-SPEC: re-load BOOT_INDEX from disk (`_progress.json`), verify every
referenced file path exists, every container_id is reachable, every env_key has either
a value or a corresponding blocker entry.

---

## FIC Context Management

This skill is short-running (typical execution < 5 minutes) and produces a single
report. FIC compaction is not expected. If context exceeds 60% during execution
(unusual — would indicate a very large source tree being analysed):

1. Flush source-code content already classified into `stack.source_evidence`
2. Continue with BOOT_INDEX only
3. Log compaction event to BOOT-AUDIT

---

## REPAIR Mode — Surgical Directives

REPAIR mode rewrites the existing `BOOT-SPEC-*.md` in place, applying only the
targeted directives.

Supported directive targets:

| Target | Action |
|---|---|
| `stack` or `phase-a` | Re-run Step 2 (stack detection) only |
| `services` or `phase-b` | Re-run Step 3 (service provisioning) only |
| `env` or `phase-c` | Re-run env synthesis only (preserve services + migrations) |
| `migrations` | Re-run ORM migrate only (preserve env file) |
| `env_keys_synthesized.{KEY}` | Fix one env var (e.g. `DATABASE_URL`); leave others |
| `global` | Re-run all four phases |

REPAIR never calls `mkdir`. It loads the prior `BOOT-SPEC-*.md`, reuses its
SESSION_ID, applies directives, and rewrites in place.

---

## Reference Files

- `references/phase-a-stack-detection.md` — language/framework/ORM/DB detection rules and the DTR-priority override
- `references/phase-b-service-provisioning.md` — reuse-existing-docker vs spin-up vs sqlite decision matrix, port collision handling
- `references/phase-c-env-and-migrations.md` — env synthesis rules per stack, ORM-specific migrate commands, secret blocker classification
- `references/phase-d-report-and-validation.md` — BOOT-SPEC section template and fidelity gate
