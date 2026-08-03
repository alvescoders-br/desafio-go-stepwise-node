# api-smoke-probe — Phase B: HTTP Probing & Error Classification

## Context Contract

- **Inputs:** `API_SMOKE_INDEX.route_plan`, `runtime_url`, `log_path`, parameter `auth_headers`, parameter `max_probe_seconds`
- **Outputs:** `routes_probed[]`, `boot_log_errors[]`, `api_errors[]`, `smoke_route_inventory[]`, `api_status`
- **Carries Forward:** All probe results
- **Flush After:** Raw response body files (keep first 500B excerpt + structured detector entries)
- **Dependency:** Phase A must be COMPLETE
- **H1 Title:** `# Phase B — HTTP Probing`

## Mode-Specific Behavior

- **BUILD:** Scan boot log once, then probe every route in `route_plan`.
- **REPAIR — `boot-log`:** Only re-scan log; preserve `routes_probed`.
- **REPAIR — `route:METHOD /path`:** Re-probe one route only; preserve others.
- **REPAIR — `detector:{name}`:** Re-classify named detector across probed routes; preserve other detectors.
- **REPAIR — `full`:** Re-scan + re-probe.

---

## Sub-Phase 3a — Boot Log Scan

Scan `runtime.log` produced by `launching-app` for error signals that the live HTTP
endpoint may not surface (initialisation errors, config gaps, migration failures).

### Pattern Library

| Pattern | Severity | suggested_root_cause |
|---|---|---|
| `/^(Error: \|FATAL\|panic:)/m` | high | unhandled exception during startup; cross-reference with launching-app boot_errors |
| `/UnhandledPromiseRejection.*/` | high | async error during startup; check the rejection reason in nearby log lines |
| `/ECONNREFUSED.*(127\.0\.0\.1\|localhost)/` | fatal | service tried to connect to a local dependency that isn't running; bootstrapping-runtime-environment may have missed a service |
| `/(Cannot find module\|ModuleNotFoundError\|ImportError\|ClassNotFoundException)/` | fatal | missing dependency; check package install (npm/pip/maven) or import paths |
| `/EADDRINUSE/` | fatal | port collision; launching-app should have surfaced this, but pattern persists in log |
| `/(Migration failed\|relation .* does not exist\|table .* does not exist)/` | high | schema not migrated; bootstrapping-runtime-environment migrations did not run or failed silently |
| `/(JWT_SECRET\|API_KEY\|DATABASE_URL).* (required\|missing\|undefined\|null)/i` | high | required env var not set; check .env file |
| `/(Failed to load config\|Configuration error)/` | high | config file invalid or missing; check application.yml / config.json / settings.py |
| `/(deprecation\|warning)/i` | (none) | suppress — noise, not an error |

For each pattern match:
```
boot_log_errors += {
  pattern: "{pattern label}",
  line_number: {N},
  log_excerpt: "{N-1}: prev line\n{N}: MATCHED line\n{N+1}: next line",
  severity: "{severity}",
  suggested_root_cause: "{lookup hint}"
}
```

**Deduplicate** by `(pattern, log_excerpt)` — long-running services may log the same
error repeatedly; one entry per distinct excerpt is enough.

### Skip Scan When

```
IF log_path is null OR file does not exist OR size > 50MB:
  decisions_log += { phase: "phase-b-3a", decision: "boot-log scan skipped", evidence: "<reason>" }
  boot_log_errors = []
```

---

## Sub-Phase 3b — HTTP Probe (per-route)

### curl Invocation

```
header_args = ""
FOR EACH (name, value) in auth_headers:
  header_args += " -H '{name}: {value}'"

# Use a separate file for response body so we don't conflate the metrics line
CALL: Bash bash -c "
  curl -s \
       -o {tmp}/response-{seq}.txt \
       -w '%{http_code}|%{time_total}|%{content_type}|%{size_download}' \
       --max-time 10 \
       {header_args} \
       -X {method} \
       '{runtime_url}{path}'
"

PARSE output: status, time_total, content_type, size_download

IF curl exit code != 0:
  result.status = -1
  result.network_error = stderr_excerpt
  detectors.http_error += { kind: "network_error", evidence: "curl failed: {stderr}", severity: "fatal", suggested_root_cause: "service unreachable; verify runtime_url and that launching-app reported RUNNING" }
ELSE:
  body_excerpt = first 500 bytes of {tmp}/response-{seq}.txt
  # Redact bearer tokens in body
  body_excerpt = re.sub(/Bearer [A-Za-z0-9._-]+/, "Bearer [REDACTED]", body_excerpt)
  body_excerpt = re.sub(/"token"\s*:\s*"[^"]+"/, '"token": "[REDACTED]"', body_excerpt)
```

### Auth Header Privacy

Header VALUES are passed to curl but NEVER written to any output file. The audit logs
header names only (`"Authorization header was included"`).

---

## Detector 1 — http_error

```
IF status >= 400:
  severity =
    "fatal"  IF status >= 500 (server error)
    "high"   IF status == 404 AND target.source == "openapi" (documented route missing)
    "medium" IF status in [401, 403] (auth gate)
    "medium" IF status == 404 AND target.source != "openapi" (probe shot in the dark)
    "medium" IF status == 422 (validation rejection)
    "low"    IF status == 400 AND body suggests validation
    "high"   otherwise (other 4xx)

  entry = {
    status: status,
    severity: severity,
    evidence: "{method} {path} returned {status}; body: {body_excerpt[:200]}",
    suggested_root_cause: see lookup
  }

  suggested_root_cause lookup:
    status 500          → "server-side exception; cross-reference runtime.log at the timestamp of this probe; the same exception may also appear in launching-app boot_errors"
    status 502/503/504  → "upstream service unreachable; check bootstrapping-runtime-environment services_running for the dependency"
    status 404 (openapi)→ "route is documented in OpenAPI but returns 404 at runtime; controller may be registered with a different prefix or the migration didn't seed the route's resource"
    status 401          → "endpoint requires auth; pre-seed Authorization header in auth_headers parameter for authenticated probing"
    status 422          → "validation error on default smoke payload; the smoke probe substituted {id}=1 — the value may be invalid"

  detectors.http_error += entry
```

---

## Detector 2 — schema_drift

This detector runs only when the route came from OpenAPI (so we have an expected schema)
AND the response body is JSON.

### When OpenAPI declares a JSON schema for the status code

```
expected_response = target.openapi_responses[str(status)]
IF expected_response is null:
  # Status code not documented; may itself be drift
  IF status == 200 AND no 200 documented:
    detectors.schema_drift += {
      severity: "medium",
      evidence: "{method} {path} returned 200 but OpenAPI only documents {documented_status_codes}",
      suggested_root_cause: "endpoint returns a status code not declared in OpenAPI; update spec or endpoint"
    }
  SKIP further schema check (no expected shape to compare against).
ELSE:
  schema = expected_response.content["application/json"].schema  # if present
  IF body content-type is not application/json:
    detectors.schema_drift += {
      severity: "medium",
      evidence: "OpenAPI declares application/json but server returned {content_type}",
      suggested_root_cause: "endpoint returns wrong content-type; check response middleware"
    }
  ELIF body_excerpt is valid JSON:
    # Shallow comparison only (avoid full schema validator dependency)
    SHALLOW_CHECK:
      - If schema.type is "object" with required[]: each required key present in body? (one drift entry per missing key)
      - If schema.type is "array": body is JSON array? (drift if scalar/object)
      - If schema.type is scalar (string/integer/boolean/number): body is that type?
    FOR EACH SHALLOW_CHECK failure:
      detectors.schema_drift += {
        severity: "medium",
        evidence: "expected {desc}, got {actual}",
        suggested_root_cause: "response shape diverges from OpenAPI spec; update endpoint or spec"
      }
  ELSE:
    # JSON content-type but body not parseable
    detectors.schema_drift += {
      severity: "high",
      evidence: "Content-Type is application/json but body is not valid JSON: {body_excerpt[:200]}",
      suggested_root_cause: "broken JSON serialization; likely an exception during response construction (check runtime.log)"
    }
```

The skill does NOT pull a full schema validation library. Shallow checks are enough for
smoke. Deep validation belongs in contract-testing, not smoke.

---

## Detector 3 — boot_log_error

Boot-log errors are aggregated into `api_errors` with `route = "<startup>"`. They are NOT
attached to any specific probed route — they refer to startup state.

```
FOR EACH boot_err in API_SMOKE_INDEX.boot_log_errors:
  api_errors += {
    detector: "boot_log_error",
    route: "<startup>",
    severity: boot_err.severity,
    evidence: boot_err.log_excerpt[:300],
    suggested_root_cause: boot_err.suggested_root_cause
  }
```

This means a service that boots cleanly but returns 500s on all routes will have no
`boot_log_error` entries — that's correct. The errors only register what `runtime.log`
captured during startup, not what happened after.

---

## Aggregation: api_errors[]

```
api_errors = []

FOR EACH result in routes_probed:
  FOR EACH detector_name in [http_error, schema_drift]:
    FOR EACH entry in result.detectors[detector_name]:
      api_errors += {
        detector: detector_name,
        route: "{result.method} {result.path}",
        severity: entry.severity,
        evidence: entry.evidence,
        suggested_root_cause: entry.suggested_root_cause
      }

# Append boot-log entries
(see Detector 3 block above)

DEDUPLICATE api_errors by (detector, evidence)
SORT api_errors by:
  severity rank: fatal=0, high=1, medium=2, low=3
  then route asc
```

---

## api_status Derivation

```
IF any api_errors entry has severity ∈ {fatal, high}: api_status = FAIL
ELIF api_errors is empty: api_status = PASS
ELSE: api_status = PASS  # medium tolerated as warnings
```

`api_status = NOT_APPLICABLE` is set in Step 1 if `launch_status != RUNNING` — Phase B
is then skipped.

---

## Source Fidelity Check (before writing)

- [ ] Every routes_probed entry has `detectors {}` with 3 keys (boot_log_error always empty array per route — boot errors live at top level)
- [ ] api_errors aggregation count matches sum of detector entries across routes + boot_log_errors count
- [ ] api_status matches derivation rule
- [ ] No auth header values appear in any string field of routes_probed or api_errors
- [ ] Response body excerpts have bearer tokens redacted
- [ ] smoke_route_inventory row count == routes_probed row count
- [ ] When `max_probe_seconds` triggered early exit, decisions_log has entry AND open_questions lists skipped routes

## Post-Section Protocol

1. **Update** `API_SMOKE_INDEX.routes_probed`, `boot_log_errors`, `api_errors`, `smoke_route_inventory`, `api_status`, `decisions_log`
2. **Update** `_progress.json`: `completed: 2`
3. **Flush** raw response body files from {tmp} (keep only structured detector entries + body_excerpts)
4. **Verify** auth redaction; api_status matches rule
5. **Log:** `"Phase B COMPLETE. Routes probed: {N}, boot errors: {B}, api_errors: {E} (fatal/high: {FH}, medium: {M}, low: {L}), api_status: {status}"`
