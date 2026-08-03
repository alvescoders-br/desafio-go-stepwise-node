# tearing-down-services — Engineering Audit
session: ENGINEERING-TEARDOWN-20260515
mode: BUILD
date: 2026-05-15T19:40:00Z
source: new skill
status: complete

## Session Summary
- skill_name: tearing-down-services
- output_path: /Users/guillermo.meyer/Documents/globai-repos/aipods-agents-skills/.agents/skills/tearing-down-services
- files_written: 6
- total_lines: ~900
- pattern_compliance: 8/8 patterns present
- evals_generated: 3

## Pattern Compliance

| Pattern | Status | Evidence |
|---|---|---|
| P1 Write-Flush-Forget | ✅ | Per-target action recorded in TEARDOWN_INDEX.actions immediately; pre-flight ps output flushed |
| P2 Carry-forward index | ✅ | TEARDOWN_INDEX with services_all, targets, skipped, actions, teardown_status |
| P3 REPAIR folder reuse | ✅ | output_folder preserved; SESSION_ID in filenames |
| P4 Surgical REPAIR | ✅ | 3 directive targets (role:{name}, force, global) |
| P5 Mandatory source loading | ✅ | runtime_info.json re-read on each invocation; ps -p re-verified just before each kill |
| P6 Pre-write fidelity check | ✅ | Phase B verifies actions vs skipped intersection = ∅; Phase C verifies count headers |
| P7 Living progress tracker | ✅ | _progress.json updated after each of 2 phases |
| P8 Domain/infra separation | ✅ | execution-protocol.md delegated; FIRST/LAST ACTION blocks present |

## Anti-Pattern Sweep

| ID | Status | Notes |
|---|---|---|
| AP-01 TEMP_BUFFER | ✅ | Each per-target action written to actions[] before next target |
| AP-02 Session ID in folder | ✅ | output_folder is parameter; SESSION_ID in filenames only |
| AP-03 Lightweight Phase 1 | ✅ | Step 1 reads runtime_info.json, classifies, validates inputs |
| AP-04 Flush w/o index update | ✅ | Post-Section Protocols order: Update → Verify → Flush |
| AP-05 Global REPAIR | ✅ | 3 directive targets; "global" is explicit |
| AP-06 {{variable}} | ✅ | grep zero |
| AP-07 Hardcoded tools | ⚠️ scoped | `kill`, `ps` are required — process management is the skill's purpose; documented in Prerequisites |
| AP-08 Summary counts | ✅ | Phase C verifies count headers |
| AP-09 FOR EACH continuation | ✅ | Per-target loop has explicit BUILD-completes-or-records-blocker contract; no early exits |
| AP-10 Fidelity check post-write | ✅ | All in pre-write position |
| AP-11 SESSION_ID construction | ✅ | `[Extract from EXECUTION METADATA]` in BUILD; `extract from PRIOR_FILE filename` in REPAIR |
| AP-12 _shared/references/ | ✅ | grep zero |
| AP-13 FIRST/LAST ACTION + Memory Bank | ✅ | Step 1 FIRST writes _progress.json; Step 4 LAST updates COMPLETED + Memory Bank rows |

## Files Written

| Path | Lines | Status |
|---|---|---|
| SKILL.md | ~310 | ✅ written |
| references/phase-a-target-identification.md | ~140 | ✅ written |
| references/phase-b-signal-and-verify.md | ~210 | ✅ written |
| references/phase-c-teardown-report.md | ~220 | ✅ written |
| evals/evals.json | 24 | ✅ written |
| ENGINEERING-AUDIT-20260515.md | (this file) | ✅ written |

## Reference Files Gate

All 3 reference files present with 5/5 sections each (Context Contract, Mode-Specific Behavior, Content, Source Fidelity Check, Post-Section Protocol).

## Architecture Decisions

- output_pattern: single_file (TEARDOWN-SPEC.md) + audit
- reference_file_count: 3 (target-identification / signal-and-verify / report)
- chunking_needed: false (target loop is bounded by services count)
- carry_forward_index_name: TEARDOWN_INDEX
- progress_json_needed: true (may run up to 60s with high grace_seconds × many services)
- upstream_id_namespaces: none

## Safety Decisions

- **Reused services are off-limits** — HARD invariant; verified by actions ∩ skipped = ∅ pre-write
- **PIDs only from runtime_info.json** — no pgrep, no name matching
- **Lstart cross-check** — guards against pid reuse (best-effort, second-granularity)
- **SIGTERM-first by default** — frameworks get to honour shutdown hooks (DB cleanup, buffer flush)
- **`force=true` is opt-in** — operator must consciously skip the grace period

## Downstream Wiring (for capability YAML)

Inputs:
- `runtime_info_path` ← from `launching-app.runtime_info_path` (chained through `local-runtime-validation`)
- `output_folder` ← capability path (typically `{output_folder}/{project_name}/teardown`)
- `grace_seconds`, `dry_run`, `force` ← capability parameters

Outputs:
- `teardown_status` (CLEAN | PARTIAL | NOTHING_TO_DO) — gates capability completion
- `actions_killed_count`, `actions_skipped_count` — for audit

## Open Questions

| ID | Description | Impact |
|---|---|---|
| OQ-01 | The skill cannot reliably tear down a process group (children of the launched process). It signals only the recorded pid. If `launching-app` spawned a process tree (e.g., a parent shell + child node), only the parent gets the signal. Most modern Node/Python/Java apps run directly without an intermediate shell, but legacy launchers may need group-kill (`kill -- -{pgid}`). | Acceptable for v1.0. Could add `kill_group: bool` parameter in v2.0 if shell-wrapper launches become common. |
| OQ-02 | Pid-reuse cross-check uses lstart with second-granularity. A same-second relaunch could fool the check. | Acceptable — pid reuse within 1 second is rare and the launching-app SESSION_ID in the report lets operators verify post-hoc. |

Skill is deployable.
