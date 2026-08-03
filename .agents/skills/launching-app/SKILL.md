---
name: launching-app
description: >
  Launches the services produced by `code-development` in managed background processes,
  captures PID + log path + bound port per service, polls a health endpoint until each is
  ready, and surfaces server-side boot errors when a service fails to start. Supports
  multi-service apps (typical monorepo with `apps/api` + `apps/web`) — each service is
  launched independently and reported as an entry in `services[]`. Reads the `.env`
  produced by `bootstrapping-runtime-environment` and pairs naturally with downstream
  smoke probes that consume each service's `surfaces[]` entries. Produces a single launch
  report and a machine-readable `runtime_info.json` with a stable `services[]` contract.
  Each service also advertises runtime `surfaces[]` (`browser`, `api`, or both) so downstream
  smoke probes do not assume that only a service named `web` can be browser-tested. Use when
  validating that a freshly-bootstrapped service actually boots, when re-running runtime
  validation after a code fix, or when any downstream step needs the service(s) running and reachable.
license: Proprietary
metadata:
  author: aipods-team
  version: 1.0.0
  category: deployment
  tags: runtime, launch, health-check, process-management
compatibility: Requires the language toolchain implied by the source code (node, python, java, ruby) and a unix-like shell.
---

# launching-app — Agent-Native Skill

## Quick Start

Launches one or more services in background processes and verifies each became reachable.
Primary output is `runtime_info.json` with a `services[]` array — each entry carries
`role` (api | web | worker | other), `url`, `pid`, `log_path`, `port`, and per-service
`launch_status`. A monorepo with `apps/api` + `apps/web` produces two entries; a single
backend service produces one. The skill is non-destructive: if a process is already
listening on a target port AND its cwd matches that service's source folder, the skill
records reuse and skips the spawn. All process management is bounded — the skill never
blocks waiting on user input.

---

## Output Architecture

```
{output_folder}/
├── LAUNCH-SPEC-{SESSION_ID}.md   ← Launch report (command, health probe results, boot errors)
├── runtime_info.json              ← Machine-readable handoff to smoke probes
├── runtime.log                    ← Stdout + stderr from the launched process (tailable)
├── LAUNCH-AUDIT-{SESSION_ID}.md  ← Lightweight session metadata
└── _progress.json
```

**Why a log file.** Smoke probes and fix loops need the server's stderr to identify
stack traces and config-validation failures. The launched process redirects stdout +
stderr to `runtime.log`; the spec excerpts the relevant lines but the full log stays
on disk for later analysis.

---

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source_path` | string | Yes | — | Absolute path to the project root. For a monorepo, this is the repo root; the skill discovers per-service folders under it (`apps/api`, `apps/web`, etc.). For a single-service project, services launch from `source_path` directly. |
| `env_file_path` | string | Yes | — | Path to the `.env` produced by `bootstrapping-runtime-environment`. Loaded into every launched process's environment. |
| `output_folder` | string | Yes | — | Absolute path where LAUNCH-SPEC, runtime_info.json, per-service `runtime-{role}.log`, and audit are written. |
| `project_name` | string | No | `project` | Project slug, used for process naming |
| `launch_targets` | string | No | `auto` | Comma-separated list of service roles to launch. `auto` = detect from `source_path` (monorepo discovery). Explicit list: e.g. `api`, `api,web`, `api,web,worker`. When a requested role cannot be detected, the skill records a blocker and skips that role (does not fabricate). |
| `monorepo_strategy` | enum | No | `auto` | `auto` (detect turbo/nx/pnpm-workspace/lerna and prefer their orchestrator), `concurrent` (spawn services in parallel directly), `sequential` (spawn one at a time — useful when later services depend on earlier ones being ready). |
| `service_commands` | string | No | — | JSON map of explicit launch commands per role, overriding auto-detection. Example: `{"api": "pnpm --filter api dev", "web": "pnpm --filter web dev"}`. |
| `service_health` | string | No | — | JSON map of explicit health endpoints per role. Example: `{"api": "/health", "web": "/"}`. Defaults to `/health` then `/` fallback per service. |
| `health_probe_method` | enum | No | `http` | Default probe method applied per service: `http`, `port`, or `log` (grep ready marker). |
| `launch_timeout_seconds` | number | No | `60` | Max seconds PER SERVICE to wait for health before declaring TIMEOUT. |
| `application_urls` | string | No | — | JSON map of pre-running URLs per role, e.g. `{"api": "http://localhost:<port>"}`. When set, the skill skips launching those roles and records them as `reused_existing = true` (still health-probes them). Use when the operator has a service running already. |
| `failure_feedback` | string | No | — | REPAIR mode directives |

**If any Required parameter is not defined, ABORT EXECUTION.**

---

## Prerequisites

- [ ] `source_path` exists and contains a recognised launch signal (`package.json` with `scripts.start*`, `pyproject.toml` with `scripts`, `pom.xml` with spring-boot-maven-plugin, `Gemfile` with rails/puma)
- [ ] `env_file_path` exists and is readable
- [ ] `output_folder` is writable
- [ ] The language toolchain is installed in PATH

---

## LAUNCH_INDEX — Carry-Forward Contract

```
LAUNCH_INDEX = {
  session_id: string,
  mode: BUILD | REPAIR,
  output_folder: string,
  source_path: string,
  project_name: string,

  // Phase A — Multi-service discovery
  monorepo: {
    detected: boolean,
    tool: turbo | nx | pnpm-workspaces | lerna | yarn-workspaces | none,
    detected_from: string
  },
  launch_targets_resolved: ["api", "web", ...],   // after auto-detection / operator filter

  services_planned: [
    {
      role: "api" | "web" | "worker" | "other",
      cwd: string,                    // absolute folder for this service
      command: string,                // verbatim shell command
      package_manager: string,
      framework: string,
      detected_from: string,          // file path that produced the decision
      command_source: "auto" | "service_commands" | "application_urls",
      health_endpoint: string,
      health_probe_method: http | port | log
    }
  ],

  // Phase B — One result per service
  services: [
    {
      role: "api" | "web" | "worker" | "other",
      url: string | null,                  // http://localhost:<port>
      pid: integer | null,
      port: integer | null,
      log_path: string,
      launched_at: ISO,
      reused_existing: boolean,            // true when already-listening OR application_urls override
      health_probe: {
        method: http | port | log,
        target: string,
        attempts: integer,
        elapsed_ms: integer,
        last_response: string,
        final_status: PASS | FAIL | TIMEOUT
      },
      surfaces: [
        {
          kind: browser | api,
          url: string,
          evidence: string,
          confidence: high | medium | low
        }
      ],
      launch_status: RUNNING | FAILED | TIMEOUT | SKIPPED,
      boot_errors: [
        { category, line_number, excerpt, severity }
      ]
    }
  ],

  // Phase C — Aggregate
  launch_status: RUNNING | PARTIAL | FAILED,
    // RUNNING = all planned services RUNNING
    // PARTIAL = at least one RUNNING, at least one not
    // FAILED  = zero RUNNING
  spec_path: string,
  audit_path: string,
  runtime_info_path: string,

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

**FIRST ACTION — MANDATORY:** Write `_progress.json` to `{output_folder}` first.

```
WRITE {output_folder}/_progress.json:
{
  "skill": "launching-app",
  "session_id": "initializing",
  "status": "RUNNING",
  "started_at": "<ISO>",
  "completed_at": null,
  "total": 3,
  "completed": 0,
  "items": []
}
```

**Command:**
```
1. SESSION_ID = [Extract from EXECUTION METADATA]
   ## Per execution-protocol.md §1. SESSION_ID is in filenames only.

2. REPAIR detection:
   IF failure_feedback is non-empty:
     MODE = REPAIR
     FOLDER = output_folder (already exists)
     PRIOR_FILE = find LAUNCH-SPEC-*.md in FOLDER
     IF PRIOR_FILE not found → write Gap Report → EXIT
     LOAD PRIOR_FILE → PRIOR_LAUNCH → PRIOR_DECISIONS
     SESSION_ID = extract session_id from PRIOR_FILE filename
     PARSE failure_feedback → REPAIR_DIRECTIVES
     ## Supported targets: "launch_command", "health_probe", "restart" (=re-run all)
     ## On REPAIR with target="restart": kill PRIOR_LAUNCH.process.pid (if alive), then re-launch
     NOTE: output_folder MUST already exist. Never mkdir for REPAIR.
   ELSE:
     MODE = BUILD
     CREATE output_folder (mkdir -p)

3. Initialize LAUNCH_INDEX with session_id, mode, output_folder, source_path, project_name.

4. Memory Bank:
   READ context-pack/active-context.md → prior session state
   APPEND to context-pack/progress.md → "Session {SESSION_ID} started: {date} | launching-app | {MODE}"

5. STOP-GATE — abort if:
   - source_path does not exist
   - env_file_path does not exist or is unreadable
   - output_folder is not writable
   - health_probe_method ∉ { http, port, log }
   - launch_timeout_seconds < 5 or > 600

LOG: "Step 1 COMPLETE. Session: {SESSION_ID}, Mode: {MODE}"
```

---

### Step 2: Discover Services & Resolve Launch Commands

Read `references/phase-a-launch-detection.md` before executing this step.

**Command:**
```
IF mode == REPAIR AND no REPAIR_DIRECTIVE targets "launch_command", "phase-a", or "services":
  LOAD LAUNCH_INDEX.services_planned, monorepo, launch_targets_resolved from PRIOR_LAUNCH
  LOG: "Step 2 skipped (REPAIR, no directive)."
  GOTO Step 3.

# === A.1 — Detect monorepo orchestrator ===
IF source_path/turbo.json exists:                 monorepo = { tool: "turbo", detected_from: "turbo.json" }
ELIF source_path/nx.json exists:                  monorepo = { tool: "nx", detected_from: "nx.json" }
ELIF source_path/pnpm-workspace.yaml exists:      monorepo = { tool: "pnpm-workspaces", detected_from: "pnpm-workspace.yaml" }
ELIF source_path/lerna.json exists:               monorepo = { tool: "lerna", detected_from: "lerna.json" }
ELIF source_path/package.json has "workspaces":   monorepo = { tool: "yarn-workspaces", detected_from: "package.json:workspaces" }
ELSE:                                             monorepo = { tool: "none" }
monorepo.detected = (monorepo.tool != "none")

# === A.2 — Discover services from filesystem ===
candidate_dirs = []
IF monorepo.detected:
  GLOB source_path/apps/*, source_path/packages/*, source_path/services/*
  FOR EACH dir matching: examine for manifest (package.json, pyproject.toml, pom.xml, Gemfile)
  Each matching dir → candidate service with inferred role (see phase-a reference for role inference rules)
ELSE:
  IF source_path has manifest → one candidate service (role inferred from manifest)

# === A.3 — Resolve launch_targets ===
IF launch_targets == "auto": resolved_targets = roles of every discovered candidate (e.g. ["api", "web"])
ELSE: resolved_targets = parse(launch_targets) (comma-separated)
  FOR EACH role in resolved_targets:
    IF no candidate with that role: blockers += { kind: "launch_target_missing", role: role }; continue

# === A.4 — Apply application_urls (pre-running services) ===
IF application_urls is set (JSON map):
  FOR EACH (role, url) in application_urls:
    services_planned += {
      role: role,
      cwd: candidate.dir OR source_path,
      command: "(reuse — already running)",
      command_source: "application_urls",
      health_endpoint: "/",
      detected_from: "parameter: application_urls"
    }
    decisions_log += { phase: "phase-a", decision: "role={role} marked as pre-running url={url}", evidence: "application_urls" }

# === A.5 — Resolve per-service launch commands for non-reused roles ===
FOR EACH role in resolved_targets where not already in services_planned:
  candidate = the candidate dir for this role
  IF service_commands is set AND has key for this role:
    command = service_commands[role]
    command_source = "service_commands"
    detected_from = "parameter: service_commands"
  ELIF monorepo.detected AND monorepo.tool has filter syntax (turbo/nx/pnpm):
    command = "<tool> run dev --filter={candidate.pkg_name}"  # see phase-a for exact syntax per tool
    command_source = "auto"
    detected_from = "<tool> filter inference"
  ELSE:
    DETECT package manager + framework by reading candidate.cwd/{manifest}.
    command = resolved dev command per phase-a detection matrix
    command_source = "auto"
    detected_from = candidate.cwd/{manifest}

  health_endpoint = service_health[role] (if set) OR (role == "web" ? "/" : "/health")
  health_probe_method = parameter health_probe_method

  services_planned += { role, cwd: candidate.cwd, command, command_source, health_endpoint, health_probe_method, package_manager, framework, detected_from }

FIDELITY CHECK:
  - services_planned is non-empty (at least one role resolved)
  - every entry has role, cwd, command, command_source, health_endpoint
  - every command excludes interactive flags (`-i`, `--prompt`, etc.)
  - every cwd exists and contains a manifest

UPDATE LAUNCH_INDEX.monorepo, launch_targets_resolved, services_planned, decisions_log
UPDATE _progress.json: completed=1
LOG: "Step 2 COMPLETE. Services planned: {N} ({list of roles}), monorepo: {monorepo.tool}"
```

---

### Step 3: Launch & Probe (per service)

Read `references/phase-b-launch-and-probe.md` before executing this step.

**Command:**
```
IF mode == REPAIR AND directive target startswith "restart:":
  target_role = directive after "restart:"
  FOR EACH service in PRIOR_LAUNCH.services where role == target_role AND pid is alive:
    SEND SIGTERM, wait 3s, SEND SIGKILL if still alive
    LOG: "Killed pid={pid} for role={target_role}"
ELIF mode == REPAIR AND no REPAIR_DIRECTIVE targets "health_probe" or "launch" or "phase-b":
  LOAD LAUNCH_INDEX.services from PRIOR_LAUNCH
  LOG: "Step 3 skipped (REPAIR, no directive)."
  GOTO Step 4.

services = []

# === Determine ordering ===
strategy = monorepo_strategy (parameter)
IF strategy == "auto":
  IF monorepo.tool in ["turbo", "nx"]: strategy = "concurrent"   # tools handle dep order
  ELIF services_planned has explicit role=api AND role=web: strategy = "sequential"  # api first (web likely depends on it)
  ELSE: strategy = "concurrent"

ordered_services = services_planned
IF strategy == "sequential" AND has both api+web: ordered = [api first, then others, web last]

# === Launch each ===
FOR EACH planned in ordered_services:
  result = { role: planned.role, cwd: planned.cwd, launched_at: now() }

  IF planned.command_source == "application_urls":
    # Pre-running: skip spawn, just probe
    result.url = application_urls[planned.role]
    result.pid = null
    result.port = parse_port_from_url(result.url)
    result.log_path = ""
    result.reused_existing = true
    GOTO probe-this-service.

  # === Reuse detection ===
  candidate_port = detect_default_port_for(planned.framework, planned.role)
  IF candidate_port AND a process listens there AND its cwd resolves to planned.cwd:
    result.pid = that pid
    result.port = candidate_port
    result.url = "http://localhost:" + candidate_port
    result.log_path = ""   # not ours; we can't tail it reliably
    result.reused_existing = true
    GOTO probe-this-service.

  # === Spawn ===
  log_path = {output_folder}/runtime-{planned.role}.log
  OPEN log_path for append.
  SPAWN background process:
    cd planned.cwd
    source env_file_path
    exec planned.command > log_path 2>&1 &
  CAPTURE pid
  result.pid = pid
  result.log_path = log_path
  result.reused_existing = false

  WAIT 3 seconds.

  IF pid no longer alive:
    TAIL log_path → boot_errors (see phase-b reference for category extraction)
    result.launch_status = FAILED
    result.boot_errors = extracted
    services += result
    IF strategy == "sequential": continue   # try next service anyway; aggregate will be PARTIAL
    ELSE: continue

  # Detect port from log (framework-specific patterns) OR env OR framework default
  result.port = detected port
  result.url = "http://localhost:" + result.port

  # === Health probe ===
  probe-this-service:
    LOOP per phase-b reference (exponential backoff up to launch_timeout_seconds)
      apply planned.health_probe_method against result.url + planned.health_endpoint
      ON 200-299: PASS
      ON 404 + first attempt + health_endpoint=="/health": retry with "/"
    result.health_probe = { method, target, attempts, elapsed_ms, last_response, final_status }

    IF probe PASSED: result.launch_status = RUNNING
    ELIF process died mid-probe: result.launch_status = FAILED
    ELSE (timeout, still alive): result.launch_status = TIMEOUT

    # === Runtime surface detection ===
    # Generic contract: service role is not the same thing as runtime surface.
    # A single HTTP service can expose browser pages, API endpoints, or both.
    result.surfaces = []
    IF result.launch_status == RUNNING AND result.url is not empty:
      IF result.health_probe.last_response OR a bounded GET of result.url/ shows HTML signals
         (content-type contains "text/html" OR body contains "<html" OR body contains "<form"
          OR body contains "<script" OR body contains "<a "):
        result.surfaces += { kind: "browser", url: result.url, evidence: "HTML response at service root or health fallback", confidence: "high" }
      IF planned.role == "web":
        result.surfaces += { kind: "browser", url: result.url, evidence: "planned role=web", confidence: "medium" }
      IF planned.role == "api":
        result.surfaces += { kind: "api", url: result.url, evidence: "planned role=api", confidence: "medium" }
      IF source/route discovery or probe evidence shows JSON/API routes
         (OpenAPI route, REST/router/controller route, "/api/" route, or application/json response):
        result.surfaces += { kind: "api", url: result.url, evidence: "API route or JSON response detected", confidence: "high" }
      DEDUPE result.surfaces by (kind, url), keeping the highest confidence evidence.

  IF result.launch_status != RUNNING AND result.log_path != "":
    TAIL result.log_path (last 200 lines)
    EXTRACT boot_errors per category (config_error, dependency_missing, port_collision, db_connection, generic)
    result.boot_errors = extracted
  ELSE:
    result.boot_errors = []

  services += result

# === Aggregate ===
running_count = count(services where launch_status == RUNNING)
total_count = len(services)
IF running_count == total_count: aggregate_status = RUNNING
ELIF running_count > 0:           aggregate_status = PARTIAL
ELSE:                             aggregate_status = FAILED

FIDELITY CHECK:
  - len(services) == len(services_planned)
  - every services entry has role, url|null, pid|null, log_path, launched_at, reused_existing, health_probe, surfaces[], launch_status, boot_errors
  - every entry's launch_status ∈ { RUNNING, FAILED, TIMEOUT, SKIPPED }
  - every RUNNING HTTP service has at least one surface OR an open_question explaining why no browser/api surface could be inferred
  - when result.launch_status != RUNNING and log_path != "", boot_errors has ≥ 1 entry
  - aggregate_status matches the running_count rule

UPDATE LAUNCH_INDEX.services, launch_status (aggregate), decisions_log
UPDATE _progress.json: completed=2
LOG: "Step 3 COMPLETE. aggregate={aggregate_status} ({running_count}/{total_count} RUNNING). Services: {role=status pairs}"
```

---

### Step 4: Write Reports

Read `references/phase-c-launch-report.md` before executing this step.

**Command:**
```
=== runtime_info.json ===

GENERATE runtime_info.json (machine-readable handoff for downstream smoke probes). The
schema is STABLE — downstream skills read `services[].surfaces[]` to find their target:

{
  "schema_version": "2.0",
  "session_id": "{SESSION_ID}",
  "project_name": "{project_name}",
  "launch_status": "RUNNING | PARTIAL | FAILED",
  "monorepo": { "tool": "turbo|nx|pnpm-workspaces|lerna|yarn-workspaces|none", "detected": true|false },
  "services": [
    {
      "role": "api | web | worker | other",
      "url": "<service_url>",
      "pid": 12345,
      "port": "<port>",
      "log_path": "{output_folder}/runtime-api.log",
      "launched_at": "<ISO>",
      "launch_status": "RUNNING | FAILED | TIMEOUT | SKIPPED",
      "reused_existing": false,
      "health_endpoint": "/health",
      "health_probe": { "method": "http", "target": "<service_url>/health", "attempts": 3, "elapsed_ms": 4200, "final_status": "PASS" },
      "surfaces": [
        { "kind": "browser", "url": "<service_url>", "evidence": "GET / returned text/html", "confidence": "high" },
        { "kind": "api", "url": "<service_url>", "evidence": "source route scan found API routes", "confidence": "high" }
      ]
    }
  ]
}

WRITE {output_folder}/runtime_info.json — MANDATORY TOOL CALL.
runtime_info_path = the written path.

**Backward-compat helper (do NOT add unless explicitly requested):** Older smoke skills
expecting `runtime_url` at the top level should be migrated to the `services[]` model.
The skill emits ONLY the new shape.

=== LAUNCH-SPEC ===

GENERATE LAUNCH-SPEC-{SESSION_ID}.md with these sections (zero prose, tables/lists only):

  ## 1. Session
  Table with session_id, mode, started_at/completed_at, aggregate launch_status, monorepo.tool

  ## 2. Services Planned ({N})
  Table per services_planned[] (role, cwd, command, command_source, framework, detected_from, health_endpoint)

  ## 3. Services Launched ({N})
  Table per services[] (role, url, pid, port, launch_status, reused_existing, log_path, launched_at)

  ## 4. Health Probes ({N})
  Table per services[].health_probe (role, method, target, attempts, elapsed_ms, final_status, last_response)

  ## 5. Boot Errors ({N})
  Cross-service table: role, category, line_number, excerpt, severity

  ## 6. Decisions Log
  Table per decisions_log[]

  ## 7. Open Questions
  Table per open_questions[]

FIDELITY CHECK:
  - All 7 sections present, no renames
  - aggregate launch_status in Section 1 matches LAUNCH_INDEX.launch_status
  - Section 3 row count == len(services); Section 4 row count == len(services with health_probe attempted)
  - Boot Errors count matches actual entries
  - When aggregate launch_status == RUNNING, Section 5 is empty (all services started clean)

WRITE {output_folder}/LAUNCH-SPEC-{SESSION_ID}.md — MANDATORY TOOL CALL.
spec_path = the written path.

=== LAUNCH-AUDIT ===

GENERATE LAUNCH-AUDIT-{SESSION_ID}.md with:
  - Pattern compliance table (8 patterns)
  - Files written
  - Probe timing

WRITE {output_folder}/LAUNCH-AUDIT-{SESSION_ID}.md — MANDATORY TOOL CALL.
audit_path = the written path.

UPDATE LAUNCH_INDEX.spec_path, audit_path, runtime_info_path
UPDATE _progress.json: completed=3
LOG: "Step 4 COMPLETE. Spec: {spec_path}, runtime_info: {runtime_info_path}"
```

---

### Step 5: Finalize

**LAST ACTION — MANDATORY:**

```
UPDATE _progress.json:
{
  "skill": "launching-app",
  "session_id": "{SESSION_ID}",
  "status": "COMPLETED",
  "completed_at": "<ISO>",
  "total": 3,
  "completed": 3,
  "items": [
    { "phase": "launch-detection", "status": "COMPLETE" },
    { "phase": "launch-and-probe", "status": "COMPLETE" },
    { "phase": "launch-report", "status": "COMPLETE" }
  ]
}

Memory Bank — MANDATORY session-end writes:
  OVERWRITE context-pack/active-context.md with: session_id, launch_status, runtime_url, pid, boot_errors count
  APPEND to context-pack/progress.md:
    | {SESSION_ID} | {date} | launching-app | {MODE} | {launch_status} | 1 launch report | {boot_errors count} boot errors |

LOG: "Skill complete. launch_status: {launch_status}. URL: {runtime_url}. Spec: {spec_path}."
```

**Critical:** the launched process REMAINS RUNNING. Downstream smoke probes read
`runtime_info_path` to find the URL and use it. A separate teardown step (in the
capability) is responsible for killing the PID when the smoke/validation pipeline
finishes.

---

### Step 6: Emit Harness Outputs Sidecar

**Apply execution-protocol.md Section 11** — Harness Output Sidecar. Mandatory when the prompt contains a `## Run metadata` block. FINAL file write of the run (after LAUNCH-SPEC verification in Step 4, after Memory Bank in Step 5, after `_progress.json` set to COMPLETED). Without it, the orchestrator falls back to the capability `value_template`, which corrupts `runtime_info_path` and `launch_spec_path` into doubly-nested folders when the parameter has already been pre-resolved to an absolute path. Downstream smoke probes then fail to locate `runtime_info.json`.

**Output parameters this skill produces** (one key per row of the prompt's `## Output parameters` table):

- `runtime_info_path`: absolute path to `runtime_info.json` inside the resolved output folder.
- `launch_status`: aggregate `"RUNNING"` | `"PARTIAL"` | `"FAILED"` | `"BLOCKED"` (`"BLOCKED"` when bootstrap `env_status="BLOCKED"`).
- `services_json`: JSON-encoded copy of the `services[]` array from `runtime_info.json`.
- `boot_errors_aggregate`: JSON-encoded list of `{role, category, line_number, excerpt, severity}` entries across all services. Empty array when launch was clean.
- `launch_spec_path`: the resolved `output_folder` parameter VERBATIM as received in the prompt — the folder that holds `LAUNCH-SPEC-*.md` and `runtime-{role}.log` files. Do NOT re-prepend `{output_folder}` or `{project_name}`.

**Implementation:** the harness here accepts Bash heredoc for the sidecar write. Execute:

```
cat > {stepwise_outputs_file} << 'OUTPUTS_EOF'
{
  "runtime_info_path": "{runtime_info_path}",
  "launch_status": "{launch_status}",
  "services_json": {services_json},
  "boot_errors_aggregate": {boot_errors_aggregate_json},
  "launch_spec_path": "{output_folder}"
}
OUTPUTS_EOF
```

`{stepwise_outputs_file}` is the path from the prompt's `## Run metadata` block's `output_file = '...'` line — copy it verbatim, do NOT reconstruct it. JSON-encoded fields (`services_json`, `boot_errors_aggregate`) MUST be valid JSON arrays.

Self-check: `cat {stepwise_outputs_file}` — verify non-empty and valid JSON. If empty, missing, or malformed, re-execute. DO NOT describe output registration in response text — EXECUTE it. No tool calls after this; the next event is `final_response`.

**Execution:** automated

---

## REPAIR Mode — Surgical Directives

| Target | Action |
|---|---|
| `launch_command` or `phase-a` | Re-run Step 2 (service discovery + command resolution) only |
| `services` | Re-run Step 2 (re-discover services) only |
| `health_probe:{role}` | Re-run health probe for one service role only |
| `restart:{role}` | Kill prior pid for that role, re-launch that role only |
| `restart` | Kill every prior pid, re-launch every planned service |
| `global` | Re-run all phases |

---

## Source Tagging

Every decision carries an evidence pointer:

```
evidence: "{source_path}/package.json:scripts.start:dev"  ← detected dev command
evidence: "parameter: launch_command_override"             ← operator override
evidence: "log_path:line 42 'Listening on http://...:<port>'" ← port discovery
evidence: "HTTP GET {url}/health returned 200"             ← health probe pass
```

---

## Upstream Consistency Rules

### 1. Zero Invention Policy
Every command, every port, every URL recorded in LAUNCH_INDEX MUST trace to a source
(manifest, env file, log line, parameter override). Never guess ports or commands.

### 2. Env File Provenance
The `env_file_path` MUST be the file emitted by `bootstrapping-runtime-environment`
(or operator-supplied). The skill DOES NOT generate env vars on its own — that is
the bootstrap skill's job. When required env vars are missing, the boot will fail and
the skill records the error (it does not silently fill in defaults).

### 3. Process Identity
For each spawned service, `pid` and `log_path` MUST be recorded together. A pid without
a log path is unactionable downstream. Pre-running services (`reused_existing=true`) may
have null pid and empty log_path — that's expected.

### 4. Reuse Detection
Before spawning each service, the skill checks whether a process is already listening on
the intended port AND that process's `cwd` resolves to the service's `cwd`. If both true,
`services[].reused_existing = true` and the skill skips the spawn for that service. This
prevents duplicate processes across re-runs of the capability.

### 6. Service Role Discipline
`role` values are drawn from a fixed enum: `api`, `web`, `worker`, `other`. Downstream
smoke skills filter on these roles. Custom names break the contract — when in doubt, use
`other` and let the operator override with `service_commands`.

### 5. Per-Phase Source Loading
Each step re-loads what it needs from `LAUNCH_INDEX` and disk — no reliance on
stale in-memory copies of the launch command or process metadata.

---

## FIC Context Management

This skill is short-running (target < 90 seconds end-to-end) and produces a small
report. FIC compaction is not expected. If context exceeds 60% during execution
(unusual — would mean a very chatty boot log):

1. Truncate captured log content to last 500 lines (full log stays on disk)
2. Continue with LAUNCH_INDEX only
3. Log compaction event to LAUNCH-AUDIT

---

## Reference Files

- `references/phase-a-launch-detection.md` — package-manager + framework → dev command resolution matrix; override handling
- `references/phase-b-launch-and-probe.md` — background spawn, port discovery, health-probe loop, boot-error extraction
- `references/phase-c-launch-report.md` — LAUNCH-SPEC section template and fidelity gate
