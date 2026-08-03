---
name: browser-smoke-probe
description: >
  Drives a running web application via MCP browser tools (Playwright or web-inspector
  protocol) and detects runtime errors that server-side stderr cannot see: HTTP 4xx/5xx
  on probed routes, page-level JavaScript errors, network anomalies like redirect cycles,
  CSS-sanity failures from missing build configs, and script load failures. Reads
  `runtime_info.json` from `launching-app` to find the running URL and consumes optional
  selector inventories from `prototype-reverse-engineering` or `web-discovery` to drive
  realistic navigation. Produces a single agent-native smoke report with structured error
  blob that downstream fix loops consume verbatim as `failure_feedback`. Use when smoke-
  validating a freshly launched web application, when re-running smoke after a fix, or
  when a downstream capability needs proof that the app loads and the golden path renders.
license: Proprietary
metadata:
  author: aipods-team
  version: 1.0.0
  category: testing
  tags: smoke, browser, mcp, runtime-validation, error-detection
compatibility: Requires an MCP browser server (playwright or mcp-web-inspector) and a running web application (typically produced by `launching-app`).
---

# browser-smoke-probe — Agent-Native Skill

## Quick Start

Probes a live web app for runtime errors that server stderr does not surface. Primary
output is a smoke report with five detector classes (HTTP errors, console errors,
network anomalies including redirect cycles, CSS sanity failures from missing build
configs, and script load failures) plus per-route screenshots. The report's
`browser_errors[]` blob is shaped for direct injection into the fix loop's
`failure_feedback`.

The skill is **bounded**: it never crawls indefinitely. `max_routes` and
`max_probe_seconds` cap runtime; the probe walks the home page first, then any
operator-supplied route list, then nav-discovered links. It never modifies application
state — all probes are read-only (`GET`, click on links, no form submissions).

---

## Output Architecture

```
{output_folder}/
├── BROWSER-SMOKE-{SESSION_ID}.md   ← Smoke report (errors per detector, route inventory)
├── browser_errors.json              ← Machine-readable error blob for fix-loop failure_feedback
├── screenshots/                     ← One per route probed
│   └── {route-hash}-{viewport}.png
├── BROWSER-SMOKE-AUDIT-{SESSION_ID}.md
└── _progress.json
```

**Why both .md and .json.** The markdown is operator-readable in the runtime-validation
gate. The JSON is what `code-development(scope_type=bug-fixing)` reads verbatim.

---

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `runtime_info_path` | string | Yes | — | Path to `runtime_info.json` produced by `launching-app`. Skill reads `services[]` and prefers `target_url` when provided. |
| `output_folder` | string | Yes | — | Absolute path where smoke report, error JSON, screenshots, and audit are written. |
| `project_name` | string | No | `project` | Slug used in screenshot filenames |
| `target_url` | string | No | — | Explicit browser surface URL to probe. Use this when a browser surface is served by a service whose role is not `web`. |
| `service_role` | string | No | `web` | Backward-compatible lookup label. Used only when `target_url` is not provided. |
| `discovery_package_path` | string | No | — | Path to `prototype-reverse-engineering` output; when present, route inventory + selectors come from here |
| `validated_test_cases_path` | string | No | — | Path to `web-discovery` output; selectors and probed flows come from here |
| `routes` | array | No | `["/"]` | Operator-supplied list of routes to probe (relative paths). When discovery_package_path is set, this is the seed list before nav-discovery extends it. |
| `viewports` | array | No | `["desktop:1440x900", "mobile:375x667"]` | Viewports to probe in each route. Increase risk surface but multiply runtime. |
| `max_routes` | integer | No | `10` | Hard ceiling on number of distinct routes probed |
| `max_probe_seconds` | integer | No | `180` | Hard ceiling on total probe runtime |
| `mcp_server` | enum | No | `auto` | One of `auto`, `playwright`, `web-inspector`. `auto` detects which MCP server is attached. |
| `failure_feedback` | string | No | — | REPAIR mode |

**If any Required parameter is not defined, ABORT EXECUTION.**

---

## Prerequisites

- [ ] Optional for an actual browser probe: an MCP browser server is attached to the session (Playwright `mcp__playwright__*` tools OR `mcp__mcp-web-inspector__*` tools). If absent, write `browser_status = "NOT_APPLICABLE"` plus a zero-error `browser_errors.json` stub.
- [ ] `runtime_info_path` exists and parses as JSON. It may use the current `services[]` contract or a legacy top-level `runtime_url`.
- [ ] `output_folder` is writable

---

## SMOKE_INDEX — Carry-Forward Contract

```
SMOKE_INDEX = {
  session_id: string,
  mode: BUILD | REPAIR,
  output_folder: string,
  runtime_url: string,
  mcp_server: playwright | web-inspector,

  // Phase A — Route plan
  route_plan: [{ path, source, viewport }],
                 // source ∈ { operator | discovery | validated_test_cases | nav-discovered }

  // Phase B — Per-route results
  routes_probed: [
    {
      path: string,
      viewport: string,
      final_url: string,           // after redirects
      load_time_ms: integer,
      screenshot_path: string,
      detectors: {
        http_error: [...],
        console_error: [...],
        network_anomaly: [...],
        css_sanity: [...],
        script_load_failure: [...]
      }
    }
  ],

  // Phase B — Cross-route aggregates
  browser_errors: [
    {
      detector: string,
      route: string,
      viewport: string,
      severity: string,
      evidence: string,
      suggested_root_cause: string
    }
  ],
  smoke_route_inventory: [           // for downstream QE automation
    { path, status_code, links_discovered, elements_with_testid }
  ],

  // Phase C — Report
  browser_status: PASS | FAIL | NOT_APPLICABLE,
  spec_path: string,
  audit_path: string,
  errors_json_path: string,

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

**FIRST ACTION — MANDATORY:** Write `_progress.json` first.

```
WRITE {output_folder}/_progress.json:
{
  "skill": "browser-smoke-probe",
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
   ## Per execution-protocol.md §1.

2. REPAIR detection:
   IF failure_feedback is non-empty:
     MODE = REPAIR
     FOLDER = output_folder (already exists)
     PRIOR_FILE = find BROWSER-SMOKE-*.md in FOLDER
     IF PRIOR_FILE not found → write Gap Report → EXIT
     LOAD PRIOR_FILE → PRIOR_SMOKE → PRIOR_DECISIONS
     SESSION_ID = extract session_id from PRIOR_FILE filename
     PARSE failure_feedback → REPAIR_DIRECTIVES
     ## Supported targets: "route:{path}" (re-probe one route), "detector:{name}" (re-run one detector across all routes), "full" (re-run everything)
   ELSE:
     MODE = BUILD
     CREATE output_folder (mkdir -p)
     CREATE output_folder/screenshots/

3. LOAD runtime_info_path → RUNTIME_INFO (parse JSON)
   IF target_url is provided:
     runtime_url = target_url
     target_source = "target_url"
   ELIF RUNTIME_INFO.services[] exists:
     service_role = parameter service_role OR "web"
     FIND first service where launch_status == "RUNNING" AND (
       role == service_role
       OR surfaces[] contains { kind: "browser" }
     )
     IF found surface.kind == "browser": runtime_url = surface.url
     ELIF found service.url: runtime_url = service.url
     ELSE:
       browser_status = NOT_APPLICABLE
       decisions_log += { phase: "step-1", decision: "skipping probe: no RUNNING browser surface", evidence: runtime_info_path }
       SKIP to Step 4 (report).
   ELSE:
     IF RUNTIME_INFO.launch_status != RUNNING:
       browser_status = NOT_APPLICABLE
       decisions_log += { phase: "step-1", decision: "skipping probe: launch_status={status}", evidence: runtime_info_path }
       SKIP to Step 4 (report).
     runtime_url = RUNTIME_INFO.runtime_url

4. DETECT MCP server:
   IF mcp_server == "auto":
     IF tools mcp__playwright__* are available → mcp_server = "playwright"
     ELIF tools mcp__mcp-web-inspector__* are available → mcp_server = "web-inspector"
     ELSE:
       blockers += { kind: no_mcp_browser }
       browser_status = NOT_APPLICABLE
       decisions_log += { phase: "step-1", decision: "browser MCP unavailable; wrote NOT_APPLICABLE stub", evidence: "no playwright/web-inspector MCP tools" }
       SKIP to Step 4 (report).

5. Initialize SMOKE_INDEX.

6. Memory Bank:
   READ context-pack/active-context.md
   APPEND to context-pack/progress.md → "Session {SESSION_ID} started: {date} | browser-smoke-probe | {MODE}"

7. STOP-GATE:
   - runtime_info_path does not exist OR cannot parse JSON
   - max_routes < 1 or > 100
   - max_probe_seconds < 10 or > 1800

LOG: "Step 1 COMPLETE. Session: {SESSION_ID}, Mode: {MODE}, MCP: {mcp_server}, URL: {runtime_url}"
```

---

### Step 2: Build Route Plan

Read `references/phase-a-route-planning.md` before executing this step.

**Command:**
```
IF mode == REPAIR AND no REPAIR_DIRECTIVE targets route planning or "phase-a":
  LOAD SMOKE_INDEX.route_plan from PRIOR_SMOKE
  LOG: "Step 2 skipped (REPAIR, no directive)."
  GOTO Step 3.

ROUTES = ["/"]   # always probe home

IF parameter routes is non-empty:
  ROUTES = parameter routes (operator wins)

IF validated_test_cases_path is provided AND file/dir exists:
  EXTRACT route list from validated_test_cases_path
    (parse Gherkin "When user navigates to X" / explicit route fields)
  ROUTES = ROUTES ∪ extracted (deduplicated, preserve order)

ELIF discovery_package_path is provided AND file/dir exists:
  EXTRACT route list from discovery_package_path (e.g. user-flows.mmd / selector-inventory.md)
  ROUTES = ROUTES ∪ extracted

# Otherwise: nav-discovery happens during Phase B (each probed page contributes anchor hrefs)

CAP ROUTES at max_routes (FIFO trim)

FOR EACH route in ROUTES:
  FOR EACH viewport in viewports:
    route_plan += { path: route, source: <where it came from>, viewport }

FIDELITY CHECK:
  - route_plan is non-empty
  - len(route_plan) <= max_routes * len(viewports)
  - "/" appears first (it's always probed)

UPDATE SMOKE_INDEX.route_plan, decisions_log
UPDATE _progress.json: completed=1
LOG: "Step 2 COMPLETE. {N} routes × {V} viewports = {N*V} probe targets."
```

---

### Step 3: Probe Routes

Read `references/phase-b-probe-execution.md` before executing this step.

**Command:**
```
IF mode == REPAIR:
  IF directive target is "route:{path}":
    PROBE_LIST = filter route_plan to entries matching that path
  ELIF directive target is "detector:{name}":
    PROBE_LIST = all route_plan entries; only the named detector re-runs per route
  ELIF directive target is "full":
    PROBE_LIST = all route_plan entries
ELSE:
  PROBE_LIST = route_plan

start_time = now()

FOR EACH probe_target in PROBE_LIST:
  IF (now() - start_time) >= max_probe_seconds:
    decisions_log += { phase: "phase-b", decision: "max_probe_seconds reached; stopping early", evidence: "{elapsed}s elapsed" }
    BREAK

  # === Resize viewport ===
  CALL: browser_resize(width, height) per probe_target.viewport

  # === Clear state (prevent cross-route contamination) ===
  CALL: clear_console_logs (web-inspector) or browser_evaluate("console.clear()") (playwright)

  # === Navigate ===
  CALL: browser_navigate(runtime_url + probe_target.path)
  WAIT: wait_for_network_idle(max=5s)

  result = { path: probe_target.path, viewport: probe_target.viewport, ... }

  # === Detector 1: HTTP error ===
  network_requests = list_network_requests()
  FOR EACH req in network_requests where status >= 400:
    result.detectors.http_error += { url: req.url, status: req.status, method: req.method }
    IF status >= 500 OR is the document request: severity = "high"; ELSE severity = "medium"

  # === Detector 2: Console error ===
  console_logs = get_console_logs(level=error,warning)
  FOR EACH log in console_logs:
    IF log.type == "error": result.detectors.console_error += { message, source, line, severity: "high" }
    IF log.type == "warning" AND log.message matches /deprecation|will be removed/: ignore (noise)

  # === Detector 3: Network anomaly (redirect cycles) ===
  url_hits = count network_requests by target URL within last 5s
  FOR EACH (url, count) in url_hits where count >= 3:
    IF url ends with probe_target.path: result.detectors.network_anomaly += { kind: "redirect_loop", url, count, severity: "fatal" }
  IF wait_for_network_idle returned TIMEOUT after 5s:
    result.detectors.network_anomaly += { kind: "never_settled", severity: "high" }

  # === Detector 4: CSS sanity ===
  # Heuristic 1: raw CSS payload check
  css_responses = filter network_requests where Content-Type contains "css"
  FOR EACH css_resp in css_responses:
    body_excerpt = fetch and head body (first 500 bytes)
    IF body_excerpt contains "@tailwind" or "@apply" (literal unprocessed directive):
      result.detectors.css_sanity += { kind: "css_not_compiled", evidence: css_resp.url, severity: "high" }
  # Heuristic 2: computed-style sentinel
  body_font_family = browser_evaluate("getComputedStyle(document.body).fontFamily")
  package_json_indicates_css_framework = check (if source_path available — optional)
  IF body_font_family in ["Times New Roman", "serif", "Times"] AND package_json_indicates_css_framework:
    result.detectors.css_sanity += { kind: "styles_not_applied", evidence: "body font = {body_font_family}", severity: "high" }
  # Heuristic 3: page extreme dimensions (giant unstyled content)
  body_scroll_height = browser_evaluate("document.body.scrollHeight")
  viewport_height = parse from probe_target.viewport
  IF body_scroll_height > (viewport_height * 20):
    result.detectors.css_sanity += { kind: "overflow_extreme", evidence: "body scroll {body_scroll_height}px vs viewport {viewport_height}px", severity: "medium" }

  # === Detector 5: Script load failure ===
  FOR EACH req in network_requests where Content-Type contains "javascript" AND status >= 400:
    result.detectors.script_load_failure += { url: req.url, status: req.status, severity: "high" }
  # Module-not-found in console (separate signal)
  module_errors = filter console_logs for /Cannot find module|Failed to resolve module|404.*\.js/
  FOR EACH e in module_errors: result.detectors.script_load_failure += { kind: "module_not_found", message: e.message, severity: "fatal" }

  # === Screenshot ===
  screenshot_path = {output_folder}/screenshots/{hash(path)}-{viewport_label}.png
  CALL: browser_take_screenshot(screenshot_path)
  result.screenshot_path = screenshot_path

  # === Inventory (for downstream QE) ===
  testid_count = browser_evaluate("document.querySelectorAll('[data-testid]').length")
  anchors = browser_evaluate("[...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'))")
  result.elements_with_testid = testid_count
  result.links_discovered = anchors (filtered to same-origin, deduplicated)

  # === Add nav-discovered routes (if not REPAIR and not exceeding max_routes) ===
  IF mode == BUILD AND len(route_plan) < max_routes:
    FOR EACH href in anchors:
      IF href starts with "/" AND href not in route_plan paths:
        route_plan += { path: href, source: "nav-discovered", viewport: probe_target.viewport }
        decisions_log += { phase: "phase-b", decision: "added nav-discovered route: {href}", evidence: "anchor on {probe_target.path}" }

  routes_probed += result
  smoke_route_inventory += { path, status_code: result.final_url status, links_discovered: len(anchors), elements_with_testid: testid_count }

# === Aggregate browser_errors[] across all routes ===
FOR EACH result in routes_probed:
  FOR EACH detector_name in [http_error, console_error, network_anomaly, css_sanity, script_load_failure]:
    FOR EACH entry in result.detectors[detector_name]:
      browser_errors += {
        detector: detector_name,
        route: result.path,
        viewport: result.viewport,
        severity: entry.severity,
        evidence: <entry-specific evidence string>,
        suggested_root_cause: <detector-specific hint, see phase-b reference>
      }

# === Compute browser_status ===
IF any browser_errors entry has severity ∈ {fatal, high}: browser_status = FAIL
ELIF browser_errors is empty: browser_status = PASS
ELSE: browser_status = PASS  # medium/low severity tolerated

FIDELITY CHECK:
  - every routes_probed entry has detectors {} with all 5 keys (may be empty arrays)
  - browser_errors aggregated count matches sum of detector entries across routes
  - smoke_route_inventory non-empty when routes_probed non-empty

UPDATE SMOKE_INDEX.routes_probed, browser_errors, smoke_route_inventory, browser_status, decisions_log
UPDATE _progress.json: completed=2
LOG: "Step 3 COMPLETE. Routes probed: {N}, errors: {M}, status: {browser_status}"
```

---

### Step 4: Write Reports

Read `references/phase-c-smoke-report.md` before executing this step.

**Command:**
```
=== browser_errors.json ===

IF SMOKE_INDEX is not initialized because the probe was skipped:
  SMOKE_INDEX = {
    runtime_url: runtime_url OR "",
    browser_status: browser_status OR "NOT_APPLICABLE",
    routes_probed_count: 0,
    errors: [],
    smoke_route_inventory: [],
    decisions_log: decisions_log
  }

GENERATE browser_errors.json (machine-readable handoff for fix loop):

{
  "schema_version": "1.0",
  "session_id": "{SESSION_ID}",
  "runtime_url": "{runtime_url}",
  "browser_status": "{browser_status}",
  "routes_probed_count": {N},
  "errors": [
    {
      "detector": "http_error | console_error | network_anomaly | css_sanity | script_load_failure",
      "route": "{path}",
      "viewport": "{viewport}",
      "severity": "fatal | high | medium | low",
      "evidence": "{evidence string}",
      "suggested_root_cause": "{hint for bug-fix research}"
    }
  ]
}

WRITE {output_folder}/browser_errors.json — MANDATORY TOOL CALL.
errors_json_path = the written path.

=== BROWSER-SMOKE-{SESSION_ID}.md ===

GENERATE per phase-c-smoke-report.md template (7 sections, zero prose):
  1. Session
  2. Route Plan
  3. Routes Probed (per-route detector breakdown)
  4. Aggregated Errors (table per browser_errors[] entry)
  5. Route Inventory (for downstream QE)
  6. Decisions Log
  7. Open Questions

WRITE {output_folder}/BROWSER-SMOKE-{SESSION_ID}.md — MANDATORY TOOL CALL.
spec_path = the written path.

=== BROWSER-SMOKE-AUDIT ===

GENERATE BROWSER-SMOKE-AUDIT-{SESSION_ID}.md (pattern compliance + files written + REPAIR pass history).

WRITE {output_folder}/BROWSER-SMOKE-AUDIT-{SESSION_ID}.md — MANDATORY TOOL CALL.
audit_path = the written path.

UPDATE SMOKE_INDEX.spec_path, audit_path, errors_json_path
UPDATE _progress.json: completed=3
LOG: "Step 4 COMPLETE. Spec: {spec_path}, errors_json: {errors_json_path}, status: {browser_status}"
```

---

### Step 5: Finalize

**LAST ACTION — MANDATORY:**

```
UPDATE _progress.json:
{
  "skill": "browser-smoke-probe",
  "session_id": "{SESSION_ID}",
  "status": "COMPLETED",
  "completed_at": "<ISO>",
  "total": 3,
  "completed": 3,
  "items": [
    { "phase": "route-planning", "status": "COMPLETE" },
    { "phase": "probe-execution", "status": "COMPLETE" },
    { "phase": "smoke-report", "status": "COMPLETE" }
  ]
}

Memory Bank:
  OVERWRITE context-pack/active-context.md with: session_id, browser_status, routes_probed count, errors count
  APPEND to context-pack/progress.md:
    | {SESSION_ID} | {date} | browser-smoke-probe | {MODE} | {browser_status} | 1 smoke report | {browser_errors count} errors |

LOG: "Skill complete. browser_status: {browser_status}. Spec: {spec_path}."
```

---

### Step 6: Emit Harness Outputs Sidecar

**Apply execution-protocol.md Section 11** — Harness Output Sidecar. Mandatory when the prompt contains a `## Run metadata` block. FINAL file write of the run (after BROWSER-SMOKE-SPEC verification in Step 4, after Memory Bank in Step 5, after `_progress.json` set to COMPLETED). Without it, the orchestrator falls back to the capability `value_template`, which corrupts `browser_errors_path`, `smoke_spec_path`, and `consolidated_errors_path` into doubly-nested folders when the parameters have already been pre-resolved to absolute paths. The capability's bug-fix loop then fails to read consolidated errors.

The `smoke-probing` capability step invokes BOTH `browser-smoke-probe` and `api-smoke-probe` and expects ONE sidecar covering all step-level outputs. When this skill runs as part of `smoke-probing`, write the FULL output set below — last write wins, and consolidation outputs (`runtime_status`, `consolidated_errors_path`, `runtime_validation_feedback`, `error_count_*`) come from the inline consolidation phase the step instructions describe.

**Output parameters this skill produces** (one key per row of the prompt's `## Output parameters` table):

- `browser_status`: `"PASS"` | `"FAIL"` | `"NOT_APPLICABLE"`.
- `api_status`: pass through from sibling `api-smoke-probe` if it ran in the same step; otherwise `"NOT_APPLICABLE"`.
- `browser_errors_path`: absolute path to `browser_errors.json` inside the resolved output folder. ALWAYS write this file, even when browser smoke is `NOT_APPLICABLE`.
- `api_errors_path`: pass through from sibling. If sibling did not run, write `api_errors.json` as a NOT_APPLICABLE zero-error stub and use that path.
- `smoke_route_inventory`: JSON-encoded merged `smoke_route_inventory[]` from this spec (and sibling, if both ran).
- `smoke_spec_path`: the resolved `output_folder` parameter VERBATIM — the folder that holds `BROWSER-SMOKE-*.md` and `browser_errors.json`. Do NOT re-prepend `{output_folder}` or `{project_name}`.
- `runtime_status`: from consolidation phase — `"PASS"` | `"FAIL"`.
- `consolidated_errors_path`: absolute path to `consolidated-errors.json` produced by the consolidation phase.
- `runtime_validation_feedback`: structured one-line-per-error string from consolidation (`""` when `runtime_status="PASS"`).
- `error_count_total`: integer total across all sources.
- `error_count_fatal_high`: integer count of fatal+high severity errors.

**Implementation:** the harness here accepts Bash heredoc for the sidecar write. Execute:

Before writing the sidecar:
- Ensure `{output_folder}/browser_errors.json` exists. Step 4 normally writes it; if not,
  write a NOT_APPLICABLE zero-error stub and set `browser_status="NOT_APPLICABLE"`.
- If `api_errors_path` is empty, missing, or points to a non-existent file, write
  `{output_folder}/api_errors.json` as a NOT_APPLICABLE zero-error stub:

```json
{
  "schema_version": "1.0",
  "session_id": "{SESSION_ID}",
  "skill": "api-smoke-probe",
  "runtime_url": "",
  "api_status": "NOT_APPLICABLE",
  "routes_probed_count": 0,
  "errors_count": 0,
  "errors_by_severity": { "fatal": 0, "high": 0, "medium": 0, "low": 0 },
  "errors": [],
  "decisions_log": [
    { "phase": "sidecar", "decision": "api smoke did not run in this step; stub written so required output path is durable" }
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
| `route:{path}` | Re-probe one route across all viewports |
| `detector:{name}` | Re-run one detector across all probed routes (e.g., refine css_sanity rules) |
| `route-plan` or `phase-a` | Re-run Step 2 only |
| `full` or `global` | Re-run everything |

---

## Source Tagging

Every detector finding carries an evidence pointer:
```
evidence: "GET /api/students returned 500 at 2026-05-15T14:12:33Z"
evidence: "console.error: TypeError: Cannot read properties of null (reading 'name')"
evidence: "5 requests to /login within 3.2s (redirect loop)"
evidence: "CSS body excerpt contains literal '@tailwind base;'"
evidence: "GET /assets/main-DZ8x9.js returned 404"
```

---

## Upstream Consistency Rules

### 1. Zero Invention Policy
Every entry in `browser_errors[]` MUST trace to actual observed data from an MCP call
(console logs, network requests, computed-style probe). No errors fabricated.

### 2. Route Provenance
Every entry in `route_plan` has a `source` field naming where the route came from:
`operator`, `discovery` (prototype-RE), `validated_test_cases` (web-discovery),
or `nav-discovered` (extracted from anchor hrefs during a previous probe).

### 3. Detector Independence
Each of the 5 detectors runs independently per probe. A failure in one does not
short-circuit the others. Each contributes its own entries to `browser_errors[]`.

### 4. Bounded Runtime
`max_routes` and `max_probe_seconds` are HARD ceilings. The skill never exceeds them
even if more routes were nav-discovered. Excess routes are dropped with a
`decisions_log` entry.

### 5. Per-Probe Source Loading
Each route probe re-loads the MCP state fresh (clear console, fresh navigation). No
detector reuses state from a prior probe.

---

## FIC Context Management

Browser smoke can generate verbose console logs and large network request lists.
At 60% context usage:
1. Truncate per-probe `network_requests` to top 100 by status code (4xx/5xx first)
2. Truncate console logs to errors+warnings only
3. Continue with SMOKE_INDEX only
4. Log compaction to audit

---

## Reference Files

- `references/phase-a-route-planning.md` — operator/discovery/test-cases route sources, nav-discovery seeding, deduplication
- `references/phase-b-probe-execution.md` — per-probe MCP call sequence, 5-detector classification logic, suggested_root_cause hints
- `references/phase-c-smoke-report.md` — BROWSER-SMOKE-SPEC template + fidelity gate + browser_errors.json schema
