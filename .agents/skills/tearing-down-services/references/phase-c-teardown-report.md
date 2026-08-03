# tearing-down-services — Phase C: Teardown Report

## Context Contract

- **Inputs:** Fully populated `TEARDOWN_INDEX`
- **Outputs:** `{output_folder}/TEARDOWN-{SESSION_ID}.md`, `{output_folder}/TEARDOWN-AUDIT-{SESSION_ID}.md`
- **Carries Forward:** `TEARDOWN_INDEX.spec_path`, `audit_path`
- **Flush After:** Generated report text
- **Dependency:** Phase B must be COMPLETE
- **H1 Title:** `# Phase C — Teardown Report`

## Mode-Specific Behavior

- **BUILD:** Generate both artefacts.
- **REPAIR:** Re-load PRIOR_TEARDOWN, apply changes from directives, rewrite report in place. Append `## Repair Pass {N}` to audit.

---

## Output 1: TEARDOWN-{SESSION_ID}.md

Template — 5 sections, zero prose, counts in headers match row counts.

```markdown
# Teardown Report — {project_name}
session: {SESSION_ID}
generated_at: {ISO}

## 1. Session

| Field | Value |
|---|---|
| session_id | {SESSION_ID} |
| mode | BUILD | REPAIR |
| started_at | {ISO} |
| completed_at | {ISO} |
| runtime_info_path | {runtime_info_path} |
| dry_run | true | false |
| force | true | false |
| grace_seconds | {N} |
| teardown_status | CLEAN | PARTIAL | NOTHING_TO_DO |
| spec_path | {output_folder}/TEARDOWN-{SESSION_ID}.md |
| audit_path | {output_folder}/TEARDOWN-AUDIT-{SESSION_ID}.md |

## 2. Targets ({N})

(services this skill acted on — those we own)

| # | role | pid | port | url | launch_status |
|---|---|---|---|---|---|
| 1 | api | 12345 | 3001 | http://localhost:3001 | RUNNING |
| ... | ... | ... | ... | ... | ... |

## 3. Skipped ({N})

(services this skill did NOT touch)

| # | role | pid | reason |
|---|---|---|---|
| 1 | api | 96344 | reused_existing |
| 2 | worker | null | no_pid |
| ... | ... | ... | ... |

Allowed reason values: `reused_existing`, `no_pid`, `not_running ({status})`, `already_dead`.

## 4. Actions ({N})

| # | role | pid | signals_sent | exit_after_ms | final_state | stderr_excerpt |
|---|---|---|---|---|---|---|
| 1 | web | 98093 | SIGTERM | 850 | TERMINATED | |
| 2 | worker | 12999 | SIGTERM, SIGKILL | — | KILLED | (did not honour SIGTERM) |
| ... | ... | ... | ... | ... | ... | ... |

Final-state enumeration: `TERMINATED`, `KILLED`, `ALREADY_DEAD`, `STILL_ALIVE`, `DRY_RUN`.

## 5. Decisions & Open Questions

### Decisions ({N})

| phase | decision | evidence |
|---|---|---|
| phase-a | reused_existing=true on role=api; not killing pid=96344 | runtime_info.json services[0] |
| phase-b | sent SIGTERM to pid=98093 (web); exited after 850ms | kill -TERM |
| ... | ... | ... |

### Open Questions ({N})

| id | type | description | impact |
|---|---|---|---|
| OQ-01 | process_zombie | pid=12999 (worker) did not exit after SIGTERM + grace + SIGKILL | manual `kill -9 -{pid}` of the process group may be required |

### Blockers ({N})

| kind | role | pid | description |
|---|---|---|---|
| process_zombie | worker | 12999 | did not exit |
```

### Count verification

Before writing, for each `({N})` heading, verify `stated == actual row count`. Auto-fix on mismatch.

---

## Output 2: TEARDOWN-AUDIT-{SESSION_ID}.md

```markdown
# Teardown Audit — {project_name}
session: {SESSION_ID}
mode: {BUILD | REPAIR}
date: {ISO}
status: {COMPLETE}

## Pattern Compliance

| Pattern | Status | Evidence |
|---|---|---|
| P1 Write-Flush-Forget | ✅ | Per-target action recorded into TEARDOWN_INDEX before next target |
| P2 Carry-forward index | ✅ | TEARDOWN_INDEX across all phases |
| P3 REPAIR folder reuse | ✅ | output_folder fixed; SESSION_ID in filenames |
| P4 Surgical REPAIR | ✅ | 3 directive targets (role:{name}, force, global) |
| P5 Mandatory source loading | ✅ | runtime_info.json re-loaded; ps -p re-verified per target |
| P6 Pre-write fidelity check | ✅ | Phase B verifies actions vs skipped intersection; Phase C verifies count headers |
| P7 Living progress tracker | ✅ | _progress.json updated per phase |
| P8 Domain/infra separation | ✅ | execution-protocol.md delegated |

## Safety Invariants Verified

| Rule | Status |
|---|---|
| Reused services never killed | ✅ — actions.pid ∩ skipped.pid = ∅ |
| Only PIDs from runtime_info.json acted on | ✅ — no pgrep, no name matching |
| Pre-flight ps -p before every signal | ✅ — recorded in decisions_log |
| Lstart cross-check (pid reuse defence) | ✅ — verified for every target |

## Files Written

| Path | Size | Status |
|---|---|---|
| TEARDOWN-{SESSION_ID}.md | {lines} | ✅ written |
| TEARDOWN-AUDIT-{SESSION_ID}.md | (this file) | ✅ written |

## Phase Timing

| Phase | Duration ms | Skipped (REPAIR) |
|---|---|---|
| A — Target identification | {ms} | no |
| B — Signal & verify | {ms} | no |
| C — Report | {ms} | no |

## Repair Passes (if applicable)

### Repair Pass {N} — {ISO}

| Directive | Target | Outcome |
|---|---|---|
| ... | ... | ... |
```

---

## REPAIR Surgical Rewrite

```
LOAD PRIOR_TEARDOWN from disk

FOR EACH REPAIR_DIRECTIVE:
  CASE directive.target:
    "role:{name}"  → replace rows in Section 2/3/4 for that role; recompute teardown_status
    "force"        → replace all rows in Section 4 (force-mode actions); preserve Section 3
    "global"       → replace all sections

REGENERATE Section 1 always.
WRITE the rewrite (overwrite same path).
APPEND ## Repair Pass {N} to audit.
```

---

## Source Fidelity Check (before writing)

- [ ] All 5 sections present in TEARDOWN-SPEC; counts match
- [ ] Section 1 `teardown_status` matches `TEARDOWN_INDEX.teardown_status`
- [ ] Section 2 row count equals `len(targets)`
- [ ] Section 3 row count equals `len(skipped)`
- [ ] Section 4 row count equals `len(actions)`
- [ ] No row in Section 2 has a pid that also appears in Section 3 (HARD invariant)
- [ ] Every row in Section 3 has a `reason` from the fixed enum

## Post-Section Protocol

1. **Write** `{output_folder}/TEARDOWN-{SESSION_ID}.md`. MANDATORY TOOL CALL.
2. **Write** `{output_folder}/TEARDOWN-AUDIT-{SESSION_ID}.md`. MANDATORY TOOL CALL.
3. **Update** `TEARDOWN_INDEX.spec_path`, `audit_path`
4. **Update** `_progress.json`: `completed: 2` → ready for finalize
5. **Flush** generated text
6. **Verify** both files exist on disk
7. **Log:** `"Phase C COMPLETE. Spec: {spec_path}, status: {teardown_status}"`
