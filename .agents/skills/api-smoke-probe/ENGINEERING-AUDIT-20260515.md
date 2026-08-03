# api-smoke-probe — Engineering Audit
session: ENGINEERING-APISMOKE-20260515
mode: BUILD
date: 2026-05-15T14:45:00Z
source: new skill
status: complete

## Session Summary
- skill_name: api-smoke-probe
- output_path: /Users/guillermo.meyer/Documents/globai-repos/aipods-agents-skills/.agents/skills/api-smoke-probe
- files_written: 6
- total_lines: ~1,200
- pattern_compliance: 8/8 patterns present
- evals_generated: 3

## Pattern Compliance

| Pattern | Status | Evidence |
|---|---|---|
| P1 Write-Flush-Forget | ✅ | Per-route detectors stored in API_SMOKE_INDEX.routes_probed immediately; raw response files in {tmp} flushed before next route |
| P2 Carry-forward index | ✅ | API_SMOKE_INDEX with route_plan, routes_probed, boot_log_errors, api_errors, smoke_route_inventory, api_status |
| P3 REPAIR folder reuse | ✅ | output_folder preserved; SESSION_ID extracted from PRIOR_FILE filename in REPAIR |
| P4 Surgical REPAIR | ✅ | 5 directive targets (route:METHOD /path, detector:{name}, boot-log, phase-a/route-plan, full/global) |
| P5 Mandatory source loading | ✅ | curl reissued per probe; log file re-read on `boot-log` directive; runtime_info.json re-read each invocation |
| P6 Pre-write fidelity check | ✅ | Phase C explicit checklist: 7 sections, JSON validity, auth-redaction grep, count matches |
| P7 Living progress tracker | ✅ | _progress.json after each of 3 phases |
| P8 Domain/infra separation | ✅ | execution-protocol.md delegated; FIRST/LAST ACTION blocks present |

## Anti-Pattern Sweep

| ID | Status | Notes |
|---|---|---|
| AP-01 TEMP_BUFFER | ✅ | Each curl response written to {tmp}/response-{seq}.txt, excerpted into structured detector entry, then flushed before next route |
| AP-02 Session ID in folder | ✅ | output_folder is parameter; SESSION_ID in filenames only |
| AP-03 Lightweight Phase 1 | ✅ | Step 1 reads runtime_info.json, validates URL schema, sets up MODE |
| AP-04 Flush w/o index update | ✅ | Post-Section Protocols order: Update → Verify → Flush |
| AP-05 Global REPAIR | ✅ | 5 directive targets; "full" is explicit |
| AP-06 {{variable}} | ✅ | grep confirms zero matches |
| AP-07 Hardcoded tools | ⚠️ scoped | curl is the probe mechanism (replaces an HTTP-client abstraction); framework patterns (NestJS @Get, FastAPI @app.get, Spring @GetMapping) are REQUIRED for source-parse fallback — each pattern is documented with rationale in phase-a |
| AP-08 Summary counts | ✅ | Phase C verifies count headers |
| AP-09 FOR EACH continuation | ✅ | Probe loop has max_probe_seconds early-exit + open_questions; pattern-scan loop is bounded by log line count |
| AP-10 Fidelity check post-write | ✅ | All in pre-write position |
| AP-11 SESSION_ID construction | ✅ | `[Extract from EXECUTION METADATA]` in BUILD; `extract from PRIOR_FILE filename` in REPAIR; zero literals |
| AP-12 _shared/references/ | ✅ | grep zero |
| AP-13 FIRST/LAST ACTION + Memory Bank | ✅ | Step 1 FIRST writes _progress.json; Step 5 LAST updates COMPLETED + Memory Bank rows |

## Files Written

| Path | Lines | Status |
|---|---|---|
| SKILL.md | ~380 | ✅ written |
| references/phase-a-route-discovery.md | ~210 | ✅ written |
| references/phase-b-http-probing.md | ~265 | ✅ written |
| references/phase-c-report.md | ~225 | ✅ written |
| evals/evals.json | 30 | ✅ written |
| ENGINEERING-AUDIT-20260515.md | (this file) | ✅ written |

## Reference Files Gate

All 3 reference files present with 5/5 sections each (Context Contract, Mode-Specific Behavior, Content, Source Fidelity Check, Post-Section Protocol).

## Architecture Decisions

- output_pattern: single_file + sidecar JSON (API-SMOKE-SPEC.md + api_errors.json)
- reference_file_count: 3 (discovery / probing / report)
- chunking_needed: false (route loop bounded by max_routes)
- carry_forward_index_name: API_SMOKE_INDEX
- progress_json_needed: true (probe can take up to 60s)
- upstream_id_namespaces: none

## Security Decisions

- auth_headers values NEVER written to any output file
- Bearer tokens in response bodies redacted to `[REDACTED]`
- Header names allowed in audit (transparency); values withheld
- Only GET/HEAD probes — read-only contract enforced

## Downstream Wiring (for capability YAML)

Inputs:
- `runtime_info_path` ← `launching-app.runtime_info_path`
- `output_folder` ← capability path
- `source_path` ← capability source_path (for source-parse fallback)
- `routes`, `auth_headers`, `max_routes`, `max_probe_seconds` ← capability defaults

Outputs:
- `api_status` (gates downstream)
- `errors_json_path` (consumed by runtime-validation gate as failure_feedback for bug-fix loop)
- `smoke_route_inventory` (handoff to downstream QE automation)

## Open Questions

| ID | Description | Impact |
|---|---|---|
| OQ-01 | Skill only probes GET/HEAD. POST/PUT/DELETE/PATCH from OpenAPI are surfaced as non_probed_documented_routes for transparency but never invoked. | Acceptable for smoke (must be read-only). Mutation coverage belongs in integration tests via quality-engineering-api-automation. |
| OQ-02 | Schema_drift uses shallow checks (required-field presence + type-check), not full JSON Schema validation. | Acceptable for smoke. Deep validation belongs in contract testing. |
| OQ-03 | Boot-log scan reads runtime.log produced by launching-app. If launching-app's log_path is null (e.g., container with stdout-only logging), boot-log scan is skipped with a decisions_log entry. | Document in launching-app capability YAML that log_path must be a real file (not /dev/stdout) for this skill to extract value. |

Skill is deployable.
