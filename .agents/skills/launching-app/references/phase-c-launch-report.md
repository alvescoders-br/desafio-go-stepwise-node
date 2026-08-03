# launching-app — Phase C: Launch Report & Validation

## Context Contract

- **Inputs:** Fully populated `LAUNCH_INDEX` (launch, process, health_probe, launch_status, boot_errors, decisions_log)
- **Outputs:** `{output_folder}/runtime_info.json`, `{output_folder}/LAUNCH-SPEC-{SESSION_ID}.md`, `{output_folder}/LAUNCH-AUDIT-{SESSION_ID}.md`
- **Carries Forward:** `LAUNCH_INDEX.spec_path`, `audit_path`, `runtime_info_path`
- **Flush After:** Generated report text — write and forget. Memory Bank writes happen in Step 5 Finalize.
- **Dependency:** Phases A and B must be COMPLETE
- **H1 Title:** `# Phase C — Launch Report`

## Mode-Specific Behavior

- **BUILD:** Generate all three artefacts.
- **REPAIR:** Re-load `PRIOR_LAUNCH`, apply only the changes from `REPAIR_DIRECTIVES`, rewrite `LAUNCH-SPEC-*.md` and `runtime_info.json` in place. Append a `## Repair Pass {N}` section to `LAUNCH-AUDIT`.
- **RESUME:** Not applicable.

---

## Output 1: runtime_info.json

This is the **handoff file** consumed by downstream smoke probes (`browser-smoke-probe`,
`api-smoke-probe`) and by capability teardown. Keep it minimal and stable — adding fields
later is fine; renaming or removing breaks consumers.

```text
{
  "schema_version": "2.0",
  "session_id": "{SESSION_ID}",
  "project_name": "{project_name}",
  "launch_status": "RUNNING | PARTIAL | FAILED",
  "monorepo": { "tool": "none", "detected": false },
  "services": [
    {
      "role": "api | web | worker | other",
      "url": "<service_url>",
      "pid": 12345,
      "port": "<port>",
      "log_path": "/abs/path/to/runtime-{role}.log",
      "launched_at": "2026-05-15T14:00:00Z",
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
```

**Field rules:**
- `services[]`: one entry per planned service; downstream consumers should use this array, not legacy top-level `runtime_url`.
- `pid`: integer when we spawned; `null` when `reused_existing == true` AND we did not get the pid from `lsof`.
- `port`: set when discoverable from URL, log, env, or port probe.
- `url`: service URL; use the actual bound URL, not a hardcoded default.
- `log_path`: absolute path when we spawned; empty string when `reused_existing == true`.
- `surfaces[]`: runtime smoke targets inferred generically from role, response content, route discovery, and probe evidence. A service can expose both `browser` and `api`.
- aggregate `launch_status`: `RUNNING` when all planned services run, `PARTIAL` when at least one runs and one does not, `FAILED` when none run.

WRITE atomically (tmp + mv) to prevent partial reads by a parallel smoke probe.

---

## Output 2: LAUNCH-SPEC-{SESSION_ID}.md

Template — 7 sections, zero prose. Counts in section headers must match table row counts.

```markdown
# Launch Report — {project_name}
session: {SESSION_ID}
generated_at: {ISO}

## 1. Session

| Field | Value |
|---|---|
| session_id | {SESSION_ID} |
| mode | BUILD | REPAIR |
| started_at | {ISO} |
| completed_at | {ISO} |
| launch_status | RUNNING | FAILED | TIMEOUT |
| spec_path | {output_folder}/LAUNCH-SPEC-{SESSION_ID}.md |
| audit_path | {output_folder}/LAUNCH-AUDIT-{SESSION_ID}.md |
| runtime_info_path | {output_folder}/runtime_info.json |

## 2. Launch Command

| Field | Value | Source |
|---|---|---|
| command | {launch.command} | {launch.detected_from} |
| cwd | {launch.cwd} | parameter source_path |
| package_manager | {launch.package_manager} | lockfile inference |
| framework | {launch.framework} | manifest inference |
| override_applied | {bool} | parameter launch_command_override |

## 3. Process

| Field | Value |
|---|---|
| pid | {process.pid or null} |
| port | {process.port} |
| runtime_url | {process.runtime_url} |
| log_path | {process.log_path} |
| launched_at | {process.launched_at} |
| reused_existing | {process.reused_existing} |

## 4. Health Probe

| Field | Value |
|---|---|
| method | {health_probe.method} |
| target | {health_probe.target} |
| attempts | {health_probe.attempts} |
| elapsed_ms | {health_probe.elapsed_ms} |
| final_status | PASS | FAIL | TIMEOUT |
| last_response | {health_probe.last_response} |

## 5. Boot Errors ({N})

| line_number | category | severity | excerpt |
|---|---|---|---|
| {row per boot_errors[]} | | | |

(Empty table when launch_status == RUNNING)

## 6. Decisions Log ({N})

| phase | decision | evidence |
|---|---|---|
| phase-a | ... | ... |
| phase-b | ... | ... |

## 7. Open Questions ({N})

| id | type | description | impact |
|---|---|---|---|
```

### Count verification

Before writing, for each `({N})` heading:
```
stated_count = N in heading
actual_count = count of rows in matching LAUNCH_INDEX field
IF mismatch → fix stated_count
LOG: "Fixed summary count in section {N}: stated {X}, actual {Y}"
```

---

## Output 3: LAUNCH-AUDIT-{SESSION_ID}.md

Lightweight session metadata.

```markdown
# Launch Audit — {project_name}
session: {SESSION_ID}
mode: {BUILD | REPAIR}
date: {ISO}
status: {COMPLETE | FAILED | TIMEOUT}

## Pattern Compliance

| Pattern | Status | Evidence |
|---|---|---|
| P1 Write-Flush-Forget | ✅ | runtime_info.json written before LAUNCH-SPEC |
| P2 Carry-forward index | ✅ | LAUNCH_INDEX used across all phases |
| P3 REPAIR folder reuse | ✅ | output_folder used as-is; SESSION_ID in filenames only |
| P4 Surgical REPAIR | ✅ | REPAIR_DIRECTIVES parsed; untargeted phases skipped |
| P5 Mandatory source loading | ✅ | per-phase reads of LAUNCH_INDEX and disk artefacts |
| P6 Pre-write fidelity check | ✅ | Phase C check ran before LAUNCH-SPEC write |
| P7 Living progress tracker | ✅ | _progress.json updated per phase |
| P8 Domain/infra separation | ✅ | execution-protocol.md mechanics delegated |

## Files Written

| Path | Lines | Status |
|---|---|---|
| runtime_info.json | ~12 | ✅ written |
| LAUNCH-SPEC-{SESSION_ID}.md | {N} | ✅ written |
| LAUNCH-AUDIT-{SESSION_ID}.md | {M} | ✅ written |
| runtime.log | {K} (bytes: {B}) | ✅ written |
| .launch.pid | 1 | ✅ written |

## Phase Timing

| Phase | Duration ms | Skipped (REPAIR) |
|---|---|---|
| A — Command detection | {ms} | no |
| B — Launch & probe | {ms} | no |
| C — Report | {ms} | no |

## REPAIR Passes (if applicable)

### Repair Pass {N} — {ISO}

| Directive | Target | Outcome |
|---|---|---|
| (row per REPAIR_DIRECTIVE) | | |

## Open Issues

(Carry-forward from LAUNCH-SPEC Section 7)
```

---

## REPAIR Mode Behavior

When `MODE == REPAIR`:

```
LOAD PRIOR_LAUNCH spec from disk (LAUNCH-SPEC-{SESSION_ID}.md — SESSION_ID from PRIOR_FILE filename)
PARSE PRIOR_LAUNCH sections into a map { section_heading → content }

FOR EACH REPAIR_DIRECTIVE:
  CASE directive.target:
    "launch_command" or "phase-a"    → replace Section 2 from current LAUNCH_INDEX
    "health_probe" or "phase-b"       → replace Sections 3 + 4 + 5 from current LAUNCH_INDEX
    "restart"                          → kill PRIOR_LAUNCH process.pid, re-run Phases A+B, replace all sections
    "global"                           → re-run everything; replace all sections

REGENERATE Section 1 always (status and timestamps change)
PRESERVE every other section verbatim

WRITE LAUNCH-SPEC-{SESSION_ID}.md (overwrite same path)
WRITE runtime_info.json (overwrite same path with updated values)
APPEND ## Repair Pass {N} section to LAUNCH-AUDIT-{SESSION_ID}.md
```

---

## Source Fidelity Check (before writing)

- [ ] All 7 sections of LAUNCH-SPEC are present, in order, with exact headings
- [ ] Section 1's `launch_status` matches `LAUNCH_INDEX.launch_status` AND matches the value in `runtime_info.json`
- [ ] Every count in section headers matches actual row count
- [ ] No prose paragraphs — every section is a table
- [ ] `runtime_info.json` parses as valid JSON
- [ ] `runtime_info.json.pid == LAUNCH_INDEX.process.pid` (including null)
- [ ] When `launch_status == FAILED` or `TIMEOUT`, Section 5 has at least one row OR open_questions registers a silent-failure gap
- [ ] When `launch_status == RUNNING`, Section 5 is empty and Section 4's `final_status == PASS`

## Post-Section Protocol

1. **Write** `{output_folder}/runtime_info.json` (atomic). MANDATORY TOOL CALL.
2. **Write** `{output_folder}/LAUNCH-SPEC-{SESSION_ID}.md`. MANDATORY TOOL CALL.
3. **Write** `{output_folder}/LAUNCH-AUDIT-{SESSION_ID}.md`. MANDATORY TOOL CALL.
4. **Update** `LAUNCH_INDEX.spec_path`, `audit_path`, `runtime_info_path`
5. **Update** `_progress.json`: `completed: 3`
6. **Flush** generated report text from memory; LAUNCH_INDEX survives for Step 5 Finalize
7. **Verify** all three files exist; reparse `runtime_info.json` to confirm valid JSON
8. **Log:** `"Phase C COMPLETE. Spec: {spec_path}, runtime_info: {runtime_info_path}, status: {launch_status}"`
