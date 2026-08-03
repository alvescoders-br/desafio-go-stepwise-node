# browser-smoke-probe — Engineering Audit
session: ENGINEERING-BROWSERSMOKE-20260515
mode: BUILD
date: 2026-05-15T14:25:00Z
source: new skill
status: complete

## Session Summary
- skill_name: browser-smoke-probe
- output_path: /Users/guillermo.meyer/Documents/globai-repos/aipods-agents-skills/.agents/skills/browser-smoke-probe
- files_written: 6
- total_lines: ~1,500
- pattern_compliance: 8/8 patterns present
- evals_generated: 3

## Pattern Compliance

| Pattern | Status | Evidence |
|---|---|---|
| P1 Write-Flush-Forget | ✅ | Per-route detector results written into SMOKE_INDEX; raw payloads flushed after structured extraction; browser_errors.json written before LAUNCH-SPEC rewrite |
| P2 Carry-forward index | ✅ | SMOKE_INDEX with route_plan, routes_probed, browser_errors, smoke_route_inventory, browser_status |
| P3 REPAIR folder reuse | ✅ | Step 1 REPAIR branch reuses output_folder; SESSION_ID extracted from PRIOR_FILE filename |
| P4 Surgical REPAIR | ✅ | 4 directive targets (route:{path}, detector:{name}, route-plan/phase-a, full/global) |
| P5 Mandatory source loading | ✅ | Per-probe browser_navigate fresh; clear_console_logs before each route; runtime_info.json re-read on each REPAIR |
| P6 Pre-write fidelity check | ✅ | Phase C explicit checklist: 7 sections, JSON validity, count matches, screenshot existence |
| P7 Living progress tracker | ✅ | _progress.json after each of 3 phases |
| P8 Domain/infra separation | ✅ | execution-protocol.md delegated |

## Anti-Pattern Sweep

| ID | Status | Notes |
|---|---|---|
| AP-01 TEMP_BUFFER | ✅ | Per-route detectors written into SMOKE_INDEX.routes_probed[] immediately; cross-route browser_errors[] aggregated AFTER all probes (acceptable: aggregation step is bounded by N routes, not unbounded text) |
| AP-02 Session ID in folder | ✅ | output_folder is parameter; SESSION_ID in filenames only |
| AP-03 Lightweight Phase 1 | ✅ | Step 1 reads runtime_info.json, detects MCP, validates inputs |
| AP-04 Flush w/o index update | ✅ | Post-Section Protocols order: Update → Verify → Flush |
| AP-05 Global REPAIR | ✅ | 4 directive targets; "full" is explicit, not default |
| AP-06 {{variable}} | ✅ | grep confirms zero matches |
| AP-07 Hardcoded tools | ⚠️ scoped | MCP tool names (mcp__playwright__*, mcp__mcp-web-inspector__*) are REQUIRED — the skill drives specific MCP servers. The `mcp_server` parameter abstracts the choice. Reference table documents both. |
| AP-08 Summary counts | ✅ | Phase C explicitly verifies count headers; auto-fix on mismatch |
| AP-09 FOR EACH continuation | ✅ | Probe loop has explicit max_probe_seconds early-exit + open_questions registration; detector loops within each probe are bounded |
| AP-10 Fidelity check post-write | ✅ | All in pre-write position; Phase C re-parses JSON AFTER write as additional gate (not skip) |
| AP-11 SESSION_ID construction | ✅ | `[Extract from EXECUTION METADATA]` in BUILD; `extract from PRIOR_FILE filename` in REPAIR; zero string literals |
| AP-12 _shared/references/ | ✅ | grep zero |
| AP-13 FIRST/LAST ACTION + Memory Bank | ✅ | Step 1 FIRST writes _progress.json; Step 5 LAST updates COMPLETED + Memory Bank |

## Files Written

| Path | Lines | Status |
|---|---|---|
| SKILL.md | ~430 | ✅ written |
| references/phase-a-route-planning.md | ~165 | ✅ written |
| references/phase-b-probe-execution.md | ~280 | ✅ written |
| references/phase-c-smoke-report.md | ~210 | ✅ written |
| evals/evals.json | 30 | ✅ written |
| ENGINEERING-AUDIT-20260515.md | (this file) | ✅ written |

## Reference Files Gate

All 3 reference files present with 5/5 sections each.

## Architecture Decisions

- output_pattern: single_file + sidecar JSON (BROWSER-SMOKE-SPEC.md + browser_errors.json + screenshots/)
- reference_file_count: 3 (planning / execution / report)
- chunking_needed: false (route loop is bounded by max_routes)
- carry_forward_index_name: SMOKE_INDEX
- progress_json_needed: true (probe can take 120-180s)
- upstream_id_namespaces: none

## Downstream Wiring (for capability YAML)

Inputs:
- `runtime_info_path` ← `launching-app.runtime_info_path`
- `output_folder` ← capability path
- `discovery_package_path` ← `prototype-reverse-engineering.discovery_package_path` (optional)
- `validated_test_cases_path` ← `quality-engineering-web-automation.validated_test_cases_path` (optional, for later runs)
- `routes`, `viewports`, `max_routes`, `max_probe_seconds`, `mcp_server` ← capability defaults

Outputs:
- `browser_status` (gates downstream)
- `errors_json_path` (consumed by runtime-validation gate as failure_feedback for bug-fix loop)
- `smoke_route_inventory` (handoff to downstream QE automation)

## Open Questions

| ID | Description | Impact |
|---|---|---|
| OQ-01 | Skill assumes either Playwright OR web-inspector MCP is attached. Capability YAML should declare MCP requirement; without MCP, browser_status = NOT_APPLICABLE. | Document in SKILL.md Prerequisites (done) and surface in capability gate. |
| OQ-02 | Skill does NOT attempt authentication. Auth-gated routes will redirect to /login and be recorded as redirect events. For authenticated probing, operators pre-seed an auth session before invocation. | Acceptable for v1.0. Could add `auth_seed` parameter in v2.0 (out of scope). |

Skill is deployable.
