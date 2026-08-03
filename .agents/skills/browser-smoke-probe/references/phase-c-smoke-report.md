# browser-smoke-probe — Phase C: Smoke Report

## Context Contract

- **Inputs:** Fully populated `SMOKE_INDEX` (route_plan, routes_probed, browser_errors, smoke_route_inventory, browser_status, decisions_log)
- **Outputs:** `{output_folder}/browser_errors.json`, `{output_folder}/BROWSER-SMOKE-{SESSION_ID}.md`, `{output_folder}/BROWSER-SMOKE-AUDIT-{SESSION_ID}.md`
- **Carries Forward:** `SMOKE_INDEX.spec_path`, `audit_path`, `errors_json_path`
- **Flush After:** Generated report text — write and forget
- **Dependency:** Phase B must be COMPLETE
- **H1 Title:** `# Phase C — Smoke Report`

## Mode-Specific Behavior

- **BUILD:** Generate all 3 artefacts.
- **REPAIR:** Re-load PRIOR_SMOKE, apply changes from directives, rewrite report + errors JSON in place. Append `## Repair Pass {N}` to audit.

---

## Output 1: browser_errors.json (Fix-Loop Handoff)

This is the file `code-development(scope_type=bug-fixing)` reads verbatim as
`failure_feedback`. The shape MUST stay stable across versions.

```json
{
  "schema_version": "1.0",
  "session_id": "{SESSION_ID}",
  "skill": "browser-smoke-probe",
  "runtime_url": "{runtime_url}",
  "browser_status": "PASS | FAIL | NOT_APPLICABLE",
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
      "detector": "http_error | console_error | network_anomaly | css_sanity | script_load_failure",
      "route": "/login",
      "viewport": "desktop:1440x900",
      "severity": "fatal | high | medium | low",
      "evidence": "specific observed data",
      "suggested_root_cause": "hint for bug-fix research"
    }
  ]
}
```

**Field rules:**
- `errors` array is sorted: fatal first, then high, then medium, then low. Within a severity, sorted by route then detector.
- `evidence` is concise (≤ 300 chars) and concrete — not "a console error happened" but "console.error: TypeError: Cannot read properties of null (reading 'name') at apps/web/src/app/AuthProvider.tsx:17"
- `suggested_root_cause` is a hint — the bug-fix research skill may disagree after looking at code; that's fine.

WRITE atomically (tmp + mv).

---

## Output 2: BROWSER-SMOKE-{SESSION_ID}.md

Template — 7 sections, zero prose. Counts in section headers must match table row counts.

```markdown
# Browser Smoke Report — {project_name}
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
| mcp_server | playwright | web-inspector |
| browser_status | PASS | FAIL | NOT_APPLICABLE |
| spec_path | {output_folder}/BROWSER-SMOKE-{SESSION_ID}.md |
| errors_json_path | {output_folder}/browser_errors.json |
| audit_path | {output_folder}/BROWSER-SMOKE-AUDIT-{SESSION_ID}.md |

## 2. Route Plan ({N})

| # | path | viewport | source |
|---|---|---|---|
| 1 | / | desktop:1440x900 | operator |
| 2 | / | mobile:375x667 | operator |
| 3 | /login | desktop:1440x900 | discovery |
| ... | ... | ... | ... |

## 3. Routes Probed ({N})

For each row, a sub-table per detector. If a detector has no findings on this route, omit the sub-table for that detector.

### 3.{i}. {route.path} @ {route.viewport}

| Field | Value |
|---|---|
| final_url | (after redirects) |
| load_time_ms | {ms} |
| screenshot | screenshots/{filename}.png |
| elements_with_testid | {count} |
| links_discovered | {count} |

#### http_error ({n})
| status | method | url | severity | suggested_root_cause |
|---|---|---|---|---|
| 500 | GET | /api/students | high | server-side exception in handler |

#### console_error ({n})
| message | source | severity | suggested_root_cause |
|---|---|---|---|

(repeat per detector that fired)

---

## 4. Aggregated Errors ({total})

| # | detector | route | viewport | severity | evidence | suggested_root_cause |
|---|---|---|---|---|---|---|
| 1 | network_anomaly | /login?returnUrl=/login | desktop:1440x900 | fatal | 5 requests to /login within 3.2s | redirect cycle — guard redirecting to /login when on /login |
| 2 | css_sanity | / | desktop:1440x900 | high | CSS body contains literal '@tailwind base;' | missing postcss.config.js |
| ... | ... | ... | ... | ... | ... | ... |

Severity breakdown:
- fatal: {F}
- high: {H}
- medium: {M}
- low: {L}

## 5. Route Inventory ({N})

(For downstream QE automation — list of routes that booted cleanly with element counts)

| path | final_status | links_discovered | elements_with_testid |
|---|---|---|---|
| / | 200 | 14 | 8 |
| /login | 200 | 3 | 4 |
| ... | ... | ... | ... |

## 6. Decisions Log ({N})

| phase | decision | evidence |
|---|---|---|
| phase-a | trimmed 3 routes to fit max_routes=10 | "list of trimmed paths" |
| phase-b | added nav-discovered route: /students | anchor on / |
| ... | ... | ... |

## 7. Open Questions ({N})

| id | type | description | impact |
|---|---|---|---|
| OQ-01 | probe_skipped_timeout | max_probe_seconds reached at 180s; routes /reports, /settings not probed | downstream QE will not have routes from these — bug-fix loop may miss errors that only manifest on those routes |
```

### Count verification

Before writing, for each `({N})` heading, verify `stated == actual_row_count`. Auto-fix if mismatch.

---

## Output 3: BROWSER-SMOKE-AUDIT-{SESSION_ID}.md

```markdown
# Browser Smoke Audit — {project_name}
session: {SESSION_ID}
mode: {BUILD | REPAIR}
date: {ISO}
status: {COMPLETE | SKIPPED}

## Pattern Compliance

| Pattern | Status | Evidence |
|---|---|---|
| P1 Write-Flush-Forget | ✅ | Per-route detector results written into SMOKE_INDEX immediately; raw payloads flushed |
| P2 Carry-forward index | ✅ | SMOKE_INDEX across all phases |
| P3 REPAIR folder reuse | ✅ | output_folder fixed; SESSION_ID in filenames |
| P4 Surgical REPAIR | ✅ | route:{path}, detector:{name}, full directive targets |
| P5 Mandatory source loading | ✅ | Per-route MCP state reset (clear console, navigate); no cross-route state |
| P6 Pre-write fidelity check | ✅ | Phase C verifies counts + JSON validity before write |
| P7 Living progress tracker | ✅ | _progress.json updated per phase |
| P8 Domain/infra separation | ✅ | execution-protocol.md delegated |

## Files Written

| Path | Size | Status |
|---|---|---|
| browser_errors.json | {bytes} | ✅ written |
| BROWSER-SMOKE-{SESSION_ID}.md | {lines} | ✅ written |
| BROWSER-SMOKE-AUDIT-{SESSION_ID}.md | (this file) | ✅ written |
| screenshots/ | {N} files | ✅ written |

## Phase Timing

| Phase | Duration ms | Skipped (REPAIR) |
|---|---|---|
| A — Route planning | {ms} | no |
| B — Probe execution | {ms} | no |
| C — Smoke report | {ms} | no |

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
PARSE sections into map

FOR EACH REPAIR_DIRECTIVE:
  CASE directive.target:
    "route:{path}"        → replace ALL Section 3.{i} entries for that path; recompute Section 4 (aggregated errors) for those routes
    "detector:{name}"     → replace the detector sub-tables in each Section 3.{i}; recompute Section 4
    "route-plan"          → replace Section 2 and Section 3 + 4 + 5
    "full"                → replace all sections

REGENERATE Section 1 always.
WRITE the rewrite (overwrite same path).
APPEND ## Repair Pass {N} to audit.
```

---

## Source Fidelity Check (before writing)

- [ ] All 7 sections present in BROWSER-SMOKE; no missing sections; counts match
- [ ] Section 1 `browser_status` matches `SMOKE_INDEX.browser_status`
- [ ] `browser_errors.json` parses as valid JSON
- [ ] `browser_errors.json.errors_count` == `len(errors[])`
- [ ] `browser_errors.json.errors_by_severity` totals match actual severity distribution
- [ ] Every entry in `errors[]` has all 6 required fields (detector, route, viewport, severity, evidence, suggested_root_cause)
- [ ] Screenshots referenced in Section 3 exist on disk
- [ ] `routes_probed_count` in JSON matches `len(routes_probed)` in SMOKE_INDEX

## Post-Section Protocol

1. **Write** `{output_folder}/browser_errors.json` (atomic). MANDATORY TOOL CALL.
2. **Write** `{output_folder}/BROWSER-SMOKE-{SESSION_ID}.md`. MANDATORY TOOL CALL.
3. **Write** `{output_folder}/BROWSER-SMOKE-AUDIT-{SESSION_ID}.md`. MANDATORY TOOL CALL.
4. **Update** `SMOKE_INDEX.spec_path`, `audit_path`, `errors_json_path`
5. **Update** `_progress.json`: `completed: 3`
6. **Flush** generated text — SMOKE_INDEX survives for Step 5 Finalize
7. **Verify** all 3 files exist; reparse browser_errors.json
8. **Log:** `"Phase C COMPLETE. Spec: {spec_path}, errors JSON: {errors_json_path}, status: {browser_status}"`
