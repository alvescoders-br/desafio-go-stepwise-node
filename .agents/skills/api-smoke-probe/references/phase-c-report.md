# api-smoke-probe — Phase C: Report

## Context Contract

- **Inputs:** Fully populated `API_SMOKE_INDEX`
- **Outputs:** `{output_folder}/api_errors.json`, `{output_folder}/API-SMOKE-{SESSION_ID}.md`, `{output_folder}/API-SMOKE-AUDIT-{SESSION_ID}.md`
- **Carries Forward:** `API_SMOKE_INDEX.spec_path`, `audit_path`, `errors_json_path`
- **Flush After:** Generated report text
- **Dependency:** Phase B must be COMPLETE
- **H1 Title:** `# Phase C — Report`

## Mode-Specific Behavior

- **BUILD:** Generate all 3 artefacts.
- **REPAIR:** Re-load PRIOR_SMOKE, apply REPAIR_DIRECTIVES, rewrite report + errors JSON in place. Append `## Repair Pass {N}` to audit.

---

## Output 1: api_errors.json (Fix-Loop Handoff)

```json
{
  "schema_version": "1.0",
  "session_id": "{SESSION_ID}",
  "skill": "api-smoke-probe",
  "runtime_url": "{runtime_url}",
  "api_status": "PASS | FAIL | NOT_APPLICABLE",
  "routes_probed_count": 12,
  "errors_count": {total},
  "errors_by_severity": {
    "fatal": {count},
    "high": {count},
    "medium": {count},
    "low": {count}
  },
  "errors": [
    {
      "detector": "http_error | schema_drift | boot_log_error",
      "route": "GET /api/users | <startup>",
      "severity": "fatal | high | medium | low",
      "evidence": "specific observed data",
      "suggested_root_cause": "hint for bug-fix research"
    }
  ]
}
```

Field rules:
- `errors` sorted: fatal → high → medium → low, then route asc
- `evidence` is concise (≤ 300 chars), concrete, with no auth-header values
- `route = "<startup>"` for boot_log_error entries
- WRITE atomically (tmp + mv)

---

## Output 2: API-SMOKE-{SESSION_ID}.md

```markdown
# API Smoke Report — {project_name}
session: {SESSION_ID}
generated_at: {ISO}

## 1. Session

| Field | Value |
|---|---|
| session_id | {SESSION_ID} |
| mode | BUILD | REPAIR |
| started_at | {ISO} |
| completed_at | {ISO} |
| runtime_url | {runtime_url} |
| api_status | PASS | FAIL | NOT_APPLICABLE |
| openapi_source | openapi-url | source-parse | operator | none |
| openapi_doc_path | {output_folder}/openapi.snapshot.json OR null |
| auth_headers_included | (list of header NAMES only, never values) |
| spec_path | {output_folder}/API-SMOKE-{SESSION_ID}.md |
| errors_json_path | {output_folder}/api_errors.json |
| audit_path | {output_folder}/API-SMOKE-AUDIT-{SESSION_ID}.md |

## 2. Route Plan ({N})

| # | method | path | source |
|---|---|---|---|
| 1 | GET | / | common-probe |
| 2 | GET | /health | common-probe |
| 3 | GET | /api/users | openapi |
| ... | ... | ... | ... |

## 3. Routes Probed ({N})

For each row, a sub-table per detector if findings exist.

### 3.{i}. {method} {path}

| Field | Value |
|---|---|
| status | {code} |
| response_time_ms | {ms} |
| content_type | {ct} |
| response_body_excerpt | {first 500 bytes, tokens redacted} |

#### http_error ({n})
| status | severity | evidence | suggested_root_cause |
|---|---|---|---|

#### schema_drift ({n})
| severity | evidence | suggested_root_cause |
|---|---|---|

(omit sub-tables for detectors with zero findings on this route)

---

## 4. Aggregated Errors ({total})

| # | detector | route | severity | evidence | suggested_root_cause |
|---|---|---|---|---|---|
| 1 | http_error | GET /api/students | fatal | GET /api/students returned 500 | server-side exception; cross-reference runtime.log |
| 2 | boot_log_error | <startup> | high | "ImportError: No module named 'redis'" | missing dependency; check package install |
| ... | ... | ... | ... | ... | ... |

Severity breakdown:
- fatal: {F}
- high: {H}
- medium: {M}
- low: {L}

## 5. Route Inventory ({N})

(for downstream QE automation)

| method | path | status | response_time_ms |
|---|---|---|---|
| GET | / | 200 | 45 |
| GET | /api/users | 200 | 120 |
| ... | ... | ... | ... |

## 6. Boot Log Findings ({N})

| # | pattern | line_number | severity | log_excerpt | suggested_root_cause |
|---|---|---|---|---|---|
| 1 | ImportError | 12 | fatal | "ImportError: No module named 'redis'" | missing dependency |
| ... | ... | ... | ... | ... | ... |

## 7. Decisions & Open Questions

### Decisions ({N})

| phase | decision | evidence |
|---|---|---|
| phase-a | trimmed 5 routes to fit max_routes=25 | list of trimmed paths |
| phase-a | substituted {id}=1 in /users/{id} | OpenAPI path template |
| ... | ... | ... |

### Open Questions ({N})

| id | type | description | impact |
|---|---|---|---|
| OQ-01 | non_probed_documented_routes | OpenAPI declares POST /api/users and DELETE /api/users/{id}, not probed (smoke is read-only) | mutation endpoints uncovered by smoke; route to integration tests |
| OQ-02 | probe_skipped_timeout | max_probe_seconds reached at 60s; 4 routes not probed | bug-fix loop may miss errors on those routes |
```

### Count verification
Before writing, verify each `({N})` header equals actual row count. Auto-fix on mismatch.

---

## Output 3: API-SMOKE-AUDIT-{SESSION_ID}.md

```markdown
# API Smoke Audit — {project_name}
session: {SESSION_ID}
mode: {BUILD | REPAIR}
date: {ISO}
status: {COMPLETE | SKIPPED}

## Pattern Compliance

| Pattern | Status | Evidence |
|---|---|---|
| P1 Write-Flush-Forget | ✅ | Per-route results written into API_SMOKE_INDEX immediately; raw response bodies flushed |
| P2 Carry-forward index | ✅ | API_SMOKE_INDEX across all phases |
| P3 REPAIR folder reuse | ✅ | output_folder fixed; SESSION_ID in filenames |
| P4 Surgical REPAIR | ✅ | 5 directive targets (route, detector, boot-log, phase-a/route-plan, full) |
| P5 Mandatory source loading | ✅ | curl probe + log read per directive; runtime_info.json reread on REPAIR |
| P6 Pre-write fidelity check | ✅ | Phase C verifies counts + JSON validity + auth redaction before write |
| P7 Living progress tracker | ✅ | _progress.json updated per phase |
| P8 Domain/infra separation | ✅ | execution-protocol.md delegated |

## Files Written

| Path | Size | Status |
|---|---|---|
| api_errors.json | {bytes} | ✅ written |
| API-SMOKE-{SESSION_ID}.md | {lines} | ✅ written |
| API-SMOKE-AUDIT-{SESSION_ID}.md | (this file) | ✅ written |
| openapi.snapshot.json | {bytes} | ✅ written (if applicable) |

## Phase Timing

| Phase | Duration ms | Skipped (REPAIR) |
|---|---|---|
| A — Route discovery | {ms} | no |
| B — Probing + boot-log | {ms} | no |
| C — Report | {ms} | no |

## Privacy Compliance

- [ ] No auth_header values appear in any output file (grep verify)
- [ ] Bearer tokens redacted in body excerpts
- [ ] Header names listed; values withheld

## Repair Passes (if applicable)

### Repair Pass {N} — {ISO}

| Directive | Target | Outcome |
|---|---|---|
| ... | ... | ... |
```

---

## REPAIR Surgical Rewrite

```
LOAD PRIOR_SMOKE from disk

FOR EACH REPAIR_DIRECTIVE:
  CASE directive.target:
    "route:METHOD /path"  → replace Section 3.{i} entries for that route; recompute Section 4 + 5
    "detector:{name}"     → replace detector sub-tables across Section 3; recompute Section 4
    "boot-log"            → replace Section 6; recompute Section 4 (boot entries)
    "phase-a" or "route-plan" → replace Sections 2, 3, 4, 5
    "full"                → replace all sections

REGENERATE Section 1 always.
WRITE the rewrite (overwrite same path).
APPEND ## Repair Pass {N} to audit.
```

---

## Source Fidelity Check (before writing)

- [ ] All 7 sections present in API-SMOKE; counts match
- [ ] Section 1 `api_status` matches `API_SMOKE_INDEX.api_status`
- [ ] `api_errors.json` parses as valid JSON
- [ ] `api_errors.json.errors_count` == `len(errors[])`
- [ ] `errors_by_severity` totals match severity distribution
- [ ] No auth-header VALUES anywhere in any output
- [ ] Bearer tokens redacted in evidence strings
- [ ] `routes_probed_count` in JSON == `len(routes_probed)` in INDEX

## Post-Section Protocol

1. **Write** `{output_folder}/api_errors.json` (atomic). MANDATORY TOOL CALL.
2. **Write** `{output_folder}/API-SMOKE-{SESSION_ID}.md`. MANDATORY TOOL CALL.
3. **Write** `{output_folder}/API-SMOKE-AUDIT-{SESSION_ID}.md`. MANDATORY TOOL CALL.
4. **Update** `API_SMOKE_INDEX.spec_path`, `audit_path`, `errors_json_path`
5. **Update** `_progress.json`: `completed: 3`
6. **Flush** generated text
7. **Verify** all 3 files exist; reparse api_errors.json
8. **Log:** `"Phase C COMPLETE. Spec: {spec_path}, errors JSON: {errors_json_path}, status: {api_status}"`
