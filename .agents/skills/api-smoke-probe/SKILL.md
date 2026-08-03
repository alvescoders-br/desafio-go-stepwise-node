---
name: api-smoke-probe
description: >
  Probes a running HTTP service for runtime errors that server stderr does not always surface:
  4xx/5xx responses on the documented routes, OpenAPI schema drift between contract and live
  response, and boot-log error signals captured by `launching-app`. Reads `runtime_info.json`
  from `launching-app` to find the running URL and `runtime.log` to scan for boot errors that
  occurred during startup, discovers routes from `openapi.json` / `/swagger.json` /
  `/v3/api-docs` or by parsing framework-specific route decorators in source, executes
  read-only GET probes against each, and writes a single agent-native smoke report plus a
  machine-readable error JSON for downstream fix loops. Use when smoke-validating a freshly
  launched API or backend service, when re-running smoke after a fix, or when a service is
  headless (no browser) so `browser-smoke-probe` does not apply.
license: Proprietary
metadata:
  author: aipods-team
  version: 1.0.0
  category: testing
  tags: smoke, api, http, runtime-validation, openapi, error-detection
compatibility: Requires a running HTTP service (typically produced by `launching-app`) and the Bash tool for HTTP probing via curl.
---

# api-smoke-probe — Agent-Native Skill

## Quick Start

Probes a live HTTP API for runtime errors that server stderr does not surface as failures.
Three detector classes:
1. `http_error` — non-2xx response codes on probed routes, with severity tiering
2. `schema_drift` — response body does not match the OpenAPI contract for the route
3. `boot_log_error` — error patterns detected in `runtime.log` produced by `launching-app`

Probes are **read-only** (GET only by default; HEAD as fallback). The skill does not mutate
state. `max_routes` and `max_probe_seconds` cap runtime. Routes come from OpenAPI document
(preferred), framework route extraction (fallback), or operator override.

---

## Output Architecture

```
{output_folder}/
├── API-SMOKE-{SESSION_ID}.md      ← Smoke report (errors per detector, route inventory)
├── api_errors.json                 ← Machine-readable error blob for fix-loop failure_feedback
├── API-SMOKE-AUDIT-{SESSION_ID}.md
└── _progress.json
```

**Why both .md and .json.** The markdown is operator-readable in the runtime-validation
gate. The JSON is what `code-development(scope_type=bug-fixing)` reads verbatim.

---

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `runtime_info_path` | string | Yes | — | Path to `runtime_info.json` produced by `launching-app`. Skill reads `services[]` and prefers `target_url` when provided. |
| `target_url` | string | No | — | Explicit API surface URL to probe. Use this when an API surface is served by a service whose role is not `api`. |
| `service_role` | string | No | `api` | Backward-compatible lookup label. Used only when `target_url` is not provided. |
| `output_folder` | string | Yes | — | Absolute path where smoke report, error JSON, and audit are written. |
| `source_path` | string | No | — | Path to the backend source root. Used to parse framework route decorators when no OpenAPI doc is exposed. |
| `project_name` | string | No | `project` | Slug used in screenshot filenames |
| `openapi_url_override` | string | No | — | Operator-supplied OpenAPI doc URL (rare; usually auto-discovered) |
| `routes` | array | No | — | Operator-supplied list of routes to probe (relative paths). Each entry is `"METHOD /path"` or just `"/path"` (defaults to GET). When non-empty, overrides discovery. |
| `auth_headers` | object | No | `{}` | Headers to include on every probe (e.g., `{"Authorization": "Bearer ..."}`). NEVER logged verbatim — only header names appear in the report. |
| `max_routes` | integer | No | `25` | Hard ceiling on number of routes probed |
| `max_probe_seconds` | integer | No | `60` | Hard ceiling on total probe runtime |
| `failure_feedback` | string | No | — | REPAIR mode |

**If any Required parameter is not defined, ABORT EXECUTION.**

---

## Prerequisites

- [ ] `runtime_info_path` exists and parses as JSON. It may use the current `services[]` contract or a legacy top-level `runtime_url`.
- [ ] Bash tool is available (`curl` for HTTP probes)
- [ ] `output_folder` is writable

---

## API_SMOKE_INDEX — Carry-Forward Contract

```
API_SMOKE_INDEX = {
  session_id: string,
  mode: BUILD | REPAIR,
  output_folder: string,
  runtime_url: string,
  log_path: string,

  // Phase A — Route discovery
  openapi_source: openapi-url | source-parse | operator | none,
  openapi_doc_path: string | null,  // path to fetched openapi.json if any
  route_plan: [
    { method, path, source, openapi_responses: { "200": ..., "400": ... } }
  ],

  // Phase B — Probe results
  routes_probed: [
    {
      method, path, final_url, status, response_time_ms,
      response_body_excerpt: string (first 500 bytes),
      detectors: {
        http_error: [...],
        schema_drift: [...],
        boot_log_error: [...]   // only populated once, on first route
      }
    }
  ],
  boot_log_errors: [
    { pattern, line_number, log_excerpt, severity, suggested_root_cause }
  ],

  // Phase B — Aggregates
  api_errors: [
    { detector, route, severity, evidence, suggested_root_cause }
  ],
  smoke_route_inventory: [
    { method, path, status, response_time_ms }
  ],

  // Phase C — Report
  api_status: PASS | FAIL | NOT_APPLICABLE,
  spec_path: string,
  audit_path: string,
  errors_json_path: string,

  // Audit
  repair_log: [{ directive, target, outcome }],
  decisions_log: [{ phase, decision, evidence }],
  blockers: [],
  open_questions: []
}
```

---

## Workflow

### Step 1: Initialize

**FIRST ACTION — MANDATORY:** Write `_progress.json`.

```
WRITE {output_folder}/_progress.json:
{ "skill": "api-smoke-probe", "session_id": "initializing", "status": "RUNNING",
  "started_at": "<ISO>", "completed_at": null, "total": 3, "completed": 0, "items": [] }
```

**Command:**
```
1. SESSION_ID = [Extract from EXECUTION METADATA]
   ## Per execution-protocol.md §1.

2. REPAIR detection:
   IF failure_feedback is non-empty:
     MODE = REPAIR
     PRIOR_FILE = find API-SMOKE-*.md in output_folder
     IF PRIOR_FILE not found → write Gap Report → EXIT
     LOAD PRIOR_FILE → PRIOR_SMOKE
     SESSION_ID = extract from PRIOR_FILE filename
     PARSE failure_feedback → REPAIR_DIRECTIVES
     ## Supported targets: "route:METHOD /path", "detector:{name}", "boot-log", "full"
   ELSE:
     MODE = BUILD
     CREATE output_folder

3. LOAD runtime_info_path → RUNTIME_INFO (parse JSON)
   IF target_url is provided:
     runtime_url = target_url
     target_source = "target_url"
     IF RUNTIME_INFO.services[] exists:
       target_service = first RUNNING service where service.url == target_url OR surfaces[] contains { url: target_url }
       log_path = target_service.log_path OR ""
     ELSE:
       log_path = ""
   ELIF RUNTIME_INFO.services[] exists:
     target_role = parameter service_role (default "api")
     api_service = first entry in RUNTIME_INFO.services where launch_status == "RUNNING" AND (
       role == target_role
       OR surfaces[] contains { kind: "api" }
     )
     IF found surface.kind == "api": runtime_url = surface.url
     ELIF found service.url: runtime_url = service.url
     ELSE:
       api_status = NOT_APPLICABLE
       decisions_log += { phase: "step-1", decision: "no RUNNING API surface; skipping api smoke", evidence: runtime_info_path }
       SKIP to Step 4 (report).
     log_path = api_service.log_path
   ELSE:
     IF RUNTIME_INFO.launch_status != RUNNING:
       api_status = NOT_APPLICABLE
       decisions_log += { phase: "step-1", decision: "launch_status={status}; skipping api smoke", evidence: runtime_info_path }
       SKIP to Step 4 (report).
     runtime_url = RUNTIME_INFO.runtime_url
     log_path = RUNTIME_INFO.log_path OR ""

4. Initialize API_SMOKE_INDEX.

5. Memory Bank:
   READ context-pack/active-context.md
   APPEND to context-pack/progress.md → "Session {SESSION_ID}: api-smoke-probe started ({MODE})"

6. STOP-GATE:
   - runtime_url is empty or unreachable schema (not http:// or https://)
   - max_routes < 1 OR > 200
   - max_probe_seconds < 5 OR > 600

LOG: "Step 1 COMPLETE. Session: {SESSION_ID}, Mode: {MODE}, URL: {runtime_url}"
```

---

### Step 2: Discover Routes

Read `references/phase-a-route-discovery.md` before executing this step.

**Command:**
```
IF mode == REPAIR AND no directive targets "phase-a" or "route-plan":
  LOAD route_plan from PRIOR_SMOKE
  GOTO Step 3.

IF parameter routes is non-empty:
  PARSE each entry: "METHOD /path" or "/path" (default METHOD=GET)
  route_plan = parsed entries, source = "operator"
  openapi_source = "operator"
  GOTO fidelity check.

# === Discover OpenAPI doc ===
openapi_urls = [
  runtime_url + "/openapi.json",
  runtime_url + "/swagger.json",
  runtime_url + "/v3/api-docs",
  runtime_url + "/api-docs",
  runtime_url + "/api/openapi.json",
  runtime_url + "/api/docs/openapi.json"
]
IF openapi_url_override is set: openapi_urls = [openapi_url_override] + openapi_urls

FOR EACH url in openapi_urls:
  CALL: Bash curl -s -o {tmp}/openapi-candidate.json -w "%{http_code}" --max-time 5 {url}
  IF http_code == 200 AND file is valid JSON AND contains "paths" key:
    openapi_doc_path = {output_folder}/openapi.snapshot.json (copy from tmp)
    openapi_source = "openapi-url"
    BREAK

IF openapi_doc_path:
  PARSE openapi.snapshot.json:
    FOR EACH (path, methods) in spec.paths:
      FOR EACH method in methods.keys() where method in [get, head]:
        route_plan += {
          method: method.upper(),
          path: path,
          source: "openapi",
          openapi_responses: methods[method].get("responses", {})
        }
ELIF source_path is set:
  # Fallback: parse framework route decorators
  PARSE source_path per detection rules (see phase-a-route-discovery.md):
    NestJS: @Get(), @Controller decorators
    FastAPI: @app.get(), @router.get()
    Spring: @GetMapping
    Flask/Django: route() / urls.py patterns
  route_plan = extracted GET routes
  openapi_source = "source-parse"
ELSE:
  openapi_source = "none"
  route_plan = [{ method: "GET", path: "/", source: "default" }]
  decisions_log += { phase: "phase-a", decision: "no OpenAPI doc and no source_path; probing root only", evidence: "all openapi_urls returned non-200" }

# === Add common health/info routes ===
common_probes = ["/health", "/healthz", "/api/health", "/ready", "/metrics", "/"]
FOR EACH p in common_probes:
  IF p not already in route_plan paths:
    route_plan += { method: "GET", path: p, source: "common-probe" }

# === Cap ===
IF len(route_plan) > max_routes:
  KEEP first max_routes entries (preserving OpenAPI order then common-probes)
  decisions_log += { phase: "phase-a", decision: "trimmed {N} routes", evidence: "max_routes={max_routes}" }

FIDELITY CHECK:
  - route_plan non-empty
  - every entry has method, path, source
  - method is one of GET, HEAD
  - paths are normalised (start with /, no trailing /)

UPDATE API_SMOKE_INDEX.route_plan, openapi_source, openapi_doc_path, decisions_log
UPDATE _progress.json: completed=1
LOG: "Step 2 COMPLETE. Routes: {N}, source: {openapi_source}"
```

---

### Step 3: Probe Routes & Scan Boot Log

Read `references/phase-b-http-probing.md` before executing this step.

**Command:**
```
=== 3a: Scan boot log (one-shot) ===

IF log_path exists:
  CALL: Bash cat {log_path}
  FOR EACH line in log content:
    APPLY boot-log error patterns (see phase-b reference):
      /^(Error|FATAL|Uncaught|UnhandledPromiseRejection|panic:|FATAL.*Database connection)/
      /(ECONNREFUSED|EADDRINUSE)/
      /(Cannot find module|ImportError|ModuleNotFoundError|ClassNotFoundException)/
      /(Migration failed|relation .* does not exist|table .* does not exist)/
      /(JWT_SECRET|API_KEY|DATABASE_URL).* (required|missing|undefined|null)/
    IF matched: boot_log_errors += { pattern, line_number, log_excerpt (line ± 1), severity, suggested_root_cause }
  DEDUPLICATE boot_log_errors by (pattern, log_excerpt)
ELSE:
  decisions_log += { phase: "phase-b-3a", decision: "no log_path; skipping boot-log scan", evidence: "RUNTIME_INFO.log_path was null" }

=== 3b: Probe routes ===

IF mode == REPAIR:
  IF directive target "route:METHOD /path": PROBE_LIST = filter route_plan to match
  ELIF directive target "detector:{name}":   PROBE_LIST = all (re-run named detector)
  ELIF directive target "boot-log":          PROBE_LIST = [] (only 3a re-runs)
  ELIF directive target "full":              PROBE_LIST = route_plan
ELSE:
  PROBE_LIST = route_plan

start_time = now()

FOR EACH target in PROBE_LIST:
  IF (now() - start_time) >= max_probe_seconds:
    decisions_log += { phase: "phase-b", decision: "max_probe_seconds reached; stopping early", evidence: "{elapsed}s elapsed" }
    BREAK

  url = runtime_url + target.path
  headers_args = build -H args from auth_headers (NEVER log values verbatim — log header NAMES only)

  CALL: Bash curl -s -o {tmp}/response-body.txt -w "%{http_code}|%{time_total}|%{content_type}" --max-time 10 {headers_args} -X {target.method} {url}
  PARSE output: status, time_total, content_type
  body_excerpt = first 500 bytes of {tmp}/response-body.txt

  result = {
    method: target.method,
    path: target.path,
    status: status,
    response_time_ms: int(time_total * 1000),
    content_type: content_type,
    response_body_excerpt: body_excerpt,
    detectors: { http_error: [], schema_drift: [], boot_log_error: [] }
  }

  # === Detector 1: http_error ===
  IF status >= 400:
    severity = derive (see phase-b reference): 5xx → high; 401/403 → medium; 404 on documented route → high; 4xx → medium
    result.detectors.http_error += {
      status, severity,
      evidence: "{method} {path} returned {status}",
      suggested_root_cause: see lookup
    }

  # === Detector 2: schema_drift ===
  IF target.openapi_responses is non-empty AND status code is documented:
    expected_schema = openapi_responses[str(status)]
    IF body_excerpt is valid JSON:
      drift = check_schema(body, expected_schema) — see phase-b reference
      IF drift is non-empty:
        result.detectors.schema_drift += {
          severity: "medium",
          evidence: "response missing required field {field} / extra field {field} / wrong type at {path}",
          suggested_root_cause: "endpoint contract drift; the OpenAPI spec says X but the runtime returns Y"
        }
    ELIF content_type is application/json AND body_excerpt is not JSON:
      result.detectors.schema_drift += {
        severity: "high",
        evidence: "Content-Type is application/json but body is not valid JSON: {excerpt}",
        suggested_root_cause: "broken JSON serialization; likely exception during response construction"
      }

  routes_probed += result
  smoke_route_inventory += { method: target.method, path: target.path, status, response_time_ms: result.response_time_ms }

=== 3c: Aggregate ===

api_errors = []

FOR EACH result in routes_probed:
  FOR EACH detector_name in [http_error, schema_drift]:
    FOR EACH entry in result.detectors[detector_name]:
      api_errors += {
        detector: detector_name,
        route: "{method} {path}",
        severity: entry.severity,
        evidence: entry.evidence,
        suggested_root_cause: entry.suggested_root_cause
      }

# boot_log_errors don't belong to any route — they're added as their own detector entries
FOR EACH boot_err in boot_log_errors:
  api_errors += {
    detector: "boot_log_error",
    route: "<startup>",
    severity: boot_err.severity,
    evidence: boot_err.log_excerpt,
    suggested_root_cause: boot_err.suggested_root_cause
  }

DEDUPLICATE api_errors by (detector, evidence)
SORT by severity (fatal → high → medium → low) then route

=== 3d: Compute status ===

IF any api_errors entry has severity in {fatal, high}: api_status = FAIL
ELIF api_errors is empty: api_status = PASS
ELSE: api_status = PASS  # medium tolerated

FIDELITY CHECK:
  - every routes_probed entry has detectors {} with all 3 keys
  - api_errors deduplicated
  - api_status matches derivation

UPDATE API_SMOKE_INDEX.routes_probed, boot_log_errors, api_errors, smoke_route_inventory, api_status
UPDATE _progress.json: completed=2
LOG: "Step 3 COMPLETE. Routes: {N}, boot errors: {B}, api_errors: {E}, status: {api_status}"
```

---

### Step 4: Write Reports

Read `references/phase-c-report.md` before executing this step.

**Command:**
```
=== api_errors.json ===

IF API_SMOKE_INDEX is not initialized because the probe was skipped:
  API_SMOKE_INDEX = {
    runtime_url: runtime_url OR "",
    api_status: api_status OR "NOT_APPLICABLE",
    routes_probed_count: 0,
    errors_count: 0,
    errors_by_severity: { "fatal": 0, "high": 0, "medium": 0, "low": 0 },
    errors: [],
    smoke_route_inventory: [],
    decisions_log: decisions_log
  }

GENERATE per schema (see phase-c-report.md):
{
  "schema_version": "1.0",
  "session_id": "{SESSION_ID}",
  "skill": "api-smoke-probe",
  "runtime_url": "{runtime_url}",
  "api_status": "{api_status}",
  "routes_probed_count": {N},
  "errors_count": {total},
  "errors_by_severity": { ... },
  "errors": [
    { "detector": "...", "route": "...", "severity": "...", "evidence": "...", "suggested_root_cause": "..." }
  ]
}

WRITE {output_folder}/api_errors.json — MANDATORY.
errors_json_path = the path.

=== API-SMOKE-{SESSION_ID}.md ===

GENERATE per phase-c-report.md template (7 sections):
  1. Session
  2. Route Plan
  3. Routes Probed (per-route detector breakdown)
  4. Aggregated Errors
  5. Route Inventory (for downstream QE)
  6. Boot Log Findings
  7. Decisions Log + Open Questions

WRITE {output_folder}/API-SMOKE-{SESSION_ID}.md — MANDATORY.
spec_path = the path.

=== API-SMOKE-AUDIT ===

GENERATE pattern compliance audit + repair log.
WRITE {output_folder}/API-SMOKE-AUDIT-{SESSION_ID}.md — MANDATORY.
audit_path = the path.

UPDATE API_SMOKE_INDEX.spec_path, audit_path, errors_json_path
UPDATE _progress.json: completed=3
LOG: "Step 4 COMPLETE."
```

---

### Step 5: Finalize

**LAST ACTION — MANDATORY:**
```
UPDATE _progress.json:
{ "skill": "api-smoke-probe", "session_id": "{SESSION_ID}", "status": "COMPLETED",
  "completed_at": "<ISO>", "total": 3, "completed": 3,
  "items": [
    { "phase": "route-discovery", "status": "COMPLETE" },
    { "phase": "http-probing", "status": "COMPLETE" },
    { "phase": "report", "status": "COMPLETE" }
  ]
}

Memory Bank:
  OVERWRITE context-pack/active-context.md with session_id, api_status, routes_probed count, errors count
  APPEND to context-pack/progress.md:
    | {SESSION_ID} | {date} | api-smoke-probe | {MODE} | {api_status} | 1 smoke report | {api_errors count} errors |

LOG: "Skill complete. api_status: {api_status}. Spec: {spec_path}."
```

---

### Step 6: Emit Harness Outputs Sidecar

**Apply execution-protocol.md Section 11** — Harness Output Sidecar. Mandatory when the prompt contains a `## Run metadata` block. FINAL file write of the run (after API-SMOKE-SPEC verification in Step 4, after Memory Bank in Step 5, after `_progress.json` set to COMPLETED). Without it, the orchestrator falls back to the capability `value_template`, which corrupts `api_errors_path`, `smoke_spec_path`, and `consolidated_errors_path` into doubly-nested folders when the parameters have already been pre-resolved to absolute paths. The capability's bug-fix loop then fails to read consolidated errors.

The `smoke-probing` capability step invokes BOTH `browser-smoke-probe` and `api-smoke-probe` and expects ONE sidecar covering all step-level outputs. When this skill runs as part of `smoke-probing`, write the FULL output set below — last write wins, and consolidation outputs (`runtime_status`, `consolidated_errors_path`, `runtime_validation_feedback`, `error_count_*`) come from the inline consolidation phase the step instructions describe.

**Output parameters this skill produces** (one key per row of the prompt's `## Output parameters` table):

- `browser_status`: pass through from sibling `browser-smoke-probe` if it ran in the same step; otherwise `"NOT_APPLICABLE"`.
- `api_status`: `"PASS"` | `"FAIL"` | `"NOT_APPLICABLE"`.
- `browser_errors_path`: pass through from sibling. If sibling did not run, write `browser_errors.json` as a NOT_APPLICABLE zero-error stub and use that path.
- `api_errors_path`: absolute path to `api_errors.json` inside the resolved output folder. ALWAYS write this file, even when API smoke is `NOT_APPLICABLE`.
- `smoke_route_inventory`: JSON-encoded merged `smoke_route_inventory[]` from this spec (and sibling, if both ran).
- `smoke_spec_path`: the resolved `output_folder` parameter VERBATIM — the folder that holds `API-SMOKE-*.md` and `api_errors.json`. Do NOT re-prepend `{output_folder}` or `{project_name}`.
- `runtime_status`: from consolidation phase — `"PASS"` | `"FAIL"`.
- `consolidated_errors_path`: absolute path to `consolidated-errors.json` produced by the consolidation phase.
- `runtime_validation_feedback`: structured one-line-per-error string from consolidation (`""` when `runtime_status="PASS"`).
- `error_count_total`: integer total across all sources.
- `error_count_fatal_high`: integer count of fatal+high severity errors.

**Implementation:** the harness here accepts Bash heredoc for the sidecar write. Execute:

Before writing the sidecar:
- Ensure `{output_folder}/api_errors.json` exists. Step 4 normally writes it; if not,
  write a NOT_APPLICABLE zero-error stub and set `api_status="NOT_APPLICABLE"`.
- If `browser_errors_path` is empty, missing, or points to a non-existent file, write
  `{output_folder}/browser_errors.json` as a NOT_APPLICABLE zero-error stub:

```json
{
  "schema_version": "1.0",
  "session_id": "{SESSION_ID}",
  "runtime_url": "",
  "browser_status": "NOT_APPLICABLE",
  "routes_probed_count": 0,
  "errors": [],
  "decisions_log": [
    { "phase": "sidecar", "decision": "browser smoke did not run in this step; stub written so required output path is durable" }
  ]
}
```

```
cat > {stepwise_outputs_file} << 'OUTPUTS_EOF'
{
  "browser_status": "{browser_status}",
  "api_status": "{api_status}",
  "browser_errors_path": "{output_folder}/browser_errors.json",
  "api_errors_path": "{output_folder}/api_errors.json",
  "smoke_route_inventory": {smoke_route_inventory_json},
  "smoke_spec_path": "{output_folder}",
  "runtime_status": "{runtime_status}",
  "consolidated_errors_path": "{consolidated_errors_path}",
  "runtime_validation_feedback": "{runtime_validation_feedback_escaped}",
  "error_count_total": {error_count_total},
  "error_count_fatal_high": {error_count_fatal_high}
}
OUTPUTS_EOF
```

`{stepwise_outputs_file}` is the path from the prompt's `## Run metadata` block's `output_file = '...'` line — copy it verbatim, do NOT reconstruct it. Embedded newlines in `runtime_validation_feedback` MUST be JSON-escaped as `\n`.

Self-check: `cat {stepwise_outputs_file}` — verify non-empty and valid JSON. If empty, missing, or malformed, re-execute. DO NOT describe output registration in response text — EXECUTE it. No tool calls after this; the next event is `final_response`.

**Execution:** automated

---

## REPAIR Mode — Surgical Directives

| Target | Action |
|---|---|
| `route:METHOD /path` | Re-probe one route |
| `detector:{name}` | Re-run one detector across all probed routes |
| `boot-log` | Re-scan boot log only |
| `route-plan` or `phase-a` | Re-run discovery |
| `full` or `global` | Re-run everything |

---

## Auth Header Privacy Rule

`auth_headers` values MUST NEVER appear in API-SMOKE-SPEC, api_errors.json, audit, or
decisions_log. Header NAMES may appear (e.g., "Authorization header included on all probes").
Body excerpts that may contain bearer tokens get the token replaced with `[REDACTED]`
before writing.

---

## Upstream Consistency Rules

### 1. Zero Invention Policy
Every `api_errors[]` entry traces to an actual curl response or actual log line. No errors
are fabricated.

### 2. Bounded Runtime
`max_routes` and `max_probe_seconds` are HARD ceilings.

### 3. Read-Only Probes
Only GET and HEAD methods are issued. POST/PUT/DELETE/PATCH are NEVER sent even if listed
in OpenAPI. Documented in decisions_log when skipped.

### 4. Detector Independence
Each of 3 detectors runs independently per probe.

### 5. Boot-log Scan is One-Shot
Boot log is scanned once at Step 3a, not per route. Same boot_log_errors appear in every
routes_probed entry's detectors.boot_log_error field — no; correction: they are recorded
ONCE in API_SMOKE_INDEX.boot_log_errors and aggregated into api_errors with route="<startup>".

---

## FIC Context Management

At 60% context usage:
1. Truncate `response_body_excerpt` from 500B to 100B per route
2. Drop full openapi.snapshot.json from memory; retain only paths/responses extracted
3. Continue with API_SMOKE_INDEX only
4. Log compaction to audit

---

## Reference Files

- `references/phase-a-route-discovery.md` — OpenAPI auto-discovery URLs, framework route extraction per stack, common-probe seeding
- `references/phase-b-http-probing.md` — curl invocation patterns, 3 detector classifiers with severity tiers, boot-log pattern library, schema_drift comparison rules
- `references/phase-c-report.md` — API-SMOKE-SPEC template + fidelity gate + api_errors.json schema
