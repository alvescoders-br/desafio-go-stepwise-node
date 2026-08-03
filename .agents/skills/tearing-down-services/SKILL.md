---
name: tearing-down-services
description: >
  Cleanly stops the services that `launching-app` spawned for runtime validation. Reads
  `runtime_info.json`, identifies services this skill owns (`reused_existing == false`
  AND `pid != null` AND `launch_status == "RUNNING"`), sends each PID a SIGTERM, waits a
  grace period for graceful shutdown, then sends SIGKILL if the process is still alive.
  Pre-existing / reused services are NEVER killed — the skill does not own them and the
  prior launcher is still responsible for their lifecycle. Produces a single teardown
  report listing what was killed, what was skipped, and any zombies. Use as the final
  step of `local-runtime-validation` (or any capability that owns launched processes)
  to avoid leaking processes between runs.
license: Proprietary
metadata:
  author: aipods-team
  version: 1.0.0
  category: deployment
  tags: teardown, cleanup, process-management, runtime-validation
compatibility: Requires the Bash tool (kill, ps, sleep). Unix-like environment (macOS / Linux).
---

# tearing-down-services — Agent-Native Skill

## Quick Start

Stops the services this run launched. Reads `runtime_info.json` and only touches PIDs we
own (`reused_existing == false`). Reused services are left running with a clear note in
the teardown report. Safe to invoke as a no-op when `runtime_info.json` is missing or all
services are reused.

---

## Output Architecture

```
{output_folder}/
├── TEARDOWN-{SESSION_ID}.md   ← Teardown report (per-service action + outcome)
├── TEARDOWN-AUDIT-{SESSION_ID}.md
└── _progress.json
```

---

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `runtime_info_path` | string | Yes | — | Path to `runtime_info.json` produced by `launching-app`. The skill reads `services[]`. |
| `output_folder` | string | Yes | — | Absolute path where TEARDOWN-{SESSION_ID}.md and audit are written. |
| `project_name` | string | No | `project` | Slug used in report header. |
| `grace_seconds` | number | No | `5` | Seconds to wait after SIGTERM before sending SIGKILL. |
| `dry_run` | boolean | No | `false` | When true, identifies targets and writes the report but sends NO signals. Useful for verifying which PIDs would be touched before a real teardown. |
| `force` | boolean | No | `false` | When true, skips SIGTERM and sends SIGKILL directly. Use only when SIGTERM has been observed to hang on this stack (rare). |
| `failure_feedback` | string | No | — | REPAIR mode directives. |

**If any Required parameter is not defined, ABORT EXECUTION.**

---

## Prerequisites

- [ ] `runtime_info_path` exists and parses as JSON
- [ ] `output_folder` is writable
- [ ] `kill` and `ps` are available in PATH

---

## TEARDOWN_INDEX — Carry-Forward Contract

```
TEARDOWN_INDEX = {
  session_id: string,
  mode: BUILD | REPAIR,
  output_folder: string,
  runtime_info_path: string,
  dry_run: boolean,

  // Phase A — Targets
  services_all: [...],                  // copy of services[] from runtime_info.json
  targets: [                            // services we will act on
    { role, pid, port, url, log_path, launch_status }
  ],
  skipped: [                            // services we will NOT touch + reason
    { role, pid, reason }
      // reason ∈ { reused_existing, no_pid, not_running, already_dead }
  ],

  // Phase B — Actions
  actions: [
    {
      role, pid,
      signals_sent: [{ signal, sent_at, exit_after_ms }],
      final_state: TERMINATED | KILLED | STILL_ALIVE | ALREADY_DEAD | DRY_RUN,
      stderr_excerpt: string
    }
  ],

  // Phase C — Report
  spec_path: string,
  audit_path: string,
  teardown_status: CLEAN | PARTIAL | NOTHING_TO_DO,
    // CLEAN         = every target ended TERMINATED or KILLED
    // PARTIAL       = at least one target still alive
    // NOTHING_TO_DO = no targets after filtering

  repair_log: [{ directive, target, outcome }],
  decisions_log: [{ phase, decision, evidence }],
  blockers: [],
  open_questions: []
}
```

---

## Workflow

### Step 1: Initialize & Identify Targets

**FIRST ACTION — MANDATORY:** Write `_progress.json` first.

```
WRITE {output_folder}/_progress.json:
{
  "skill": "tearing-down-services",
  "session_id": "initializing",
  "status": "RUNNING",
  "started_at": "<ISO>",
  "completed_at": null,
  "total": 2,
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
     PRIOR_FILE = find TEARDOWN-*.md in output_folder
     IF PRIOR_FILE not found → write Gap Report → EXIT
     LOAD PRIOR_FILE → PRIOR_TEARDOWN
     SESSION_ID = extract from PRIOR_FILE filename
     PARSE failure_feedback → REPAIR_DIRECTIVES
     ## Supported targets: "role:{name}" (retry one role), "force" (re-kill all targets with SIGKILL), "global"
   ELSE:
     MODE = BUILD
     CREATE output_folder (mkdir -p)

3. LOAD runtime_info_path → RUNTIME_INFO (parse JSON; expect schema_version == "2.0" with services[])
   IF parse fails OR services[] is missing:
     teardown_status = NOTHING_TO_DO
     decisions_log += { phase: "step-1", decision: "no parseable runtime_info.json; nothing to teardown", evidence: runtime_info_path }
     SKIP to Step 3 (report).

4. Initialize TEARDOWN_INDEX. services_all = RUNTIME_INFO.services[].

5. Read `references/phase-a-target-identification.md` for the full classification rules.

   For each service in RUNTIME_INFO.services[]:
     IF service.reused_existing == true:
       skipped += { role, pid: service.pid, reason: "reused_existing" }
     ELIF service.pid is null OR service.pid <= 0:
       skipped += { role, pid: null, reason: "no_pid" }
     ELIF service.launch_status != "RUNNING":
       skipped += { role, pid: service.pid, reason: "not_running ({launch_status})" }
     ELIF process service.pid is not alive (verify with `ps -p {pid}`):
       skipped += { role, pid: service.pid, reason: "already_dead" }
     ELSE:
       targets += { role, pid, port, url, log_path, launch_status }

   FIDELITY CHECK:
     - targets ∪ skipped covers every entry in services_all (no orphans)
     - every targets entry has a numeric pid > 0
     - every targets entry's pid is currently alive

6. Memory Bank:
   READ context-pack/active-context.md
   APPEND to context-pack/progress.md → "Session {SESSION_ID} started: {date} | tearing-down-services | {MODE}"

7. STOP-GATE — abort if:
   - grace_seconds < 0 or > 60
   - runtime_info_path exists but is not valid JSON

UPDATE TEARDOWN_INDEX: targets, skipped, decisions_log
UPDATE _progress.json: completed=1
LOG: "Step 1 COMPLETE. Session: {SESSION_ID}, targets: {N}, skipped: {M}, dry_run: {dry_run}"
```

---

### Step 2: Stop Services

Read `references/phase-b-signal-and-verify.md` before executing this step.

**Command:**
```
IF mode == REPAIR AND directive target == "role:{name}":
  PROCESS_LIST = filter targets to that role
ELIF mode == REPAIR AND directive target == "force":
  PROCESS_LIST = targets; force = true
ELSE:
  PROCESS_LIST = targets

IF dry_run == true:
  FOR EACH target in PROCESS_LIST:
    actions += {
      role: target.role,
      pid: target.pid,
      signals_sent: [],
      final_state: "DRY_RUN",
      stderr_excerpt: ""
    }
  decisions_log += { phase: "phase-b", decision: "dry_run=true; no signals sent", evidence: "parameter" }
  GOTO Step 3.

FOR EACH target in PROCESS_LIST:
  action = { role: target.role, pid: target.pid, signals_sent: [], stderr_excerpt: "" }

  # Final pre-flight check — the pid may have died between Step 1 and now
  IF process target.pid is not alive:
    action.final_state = "ALREADY_DEAD"
    actions += action
    continue

  IF force == true:
    # Skip SIGTERM, go straight to SIGKILL
    CALL: Bash kill -KILL {target.pid}
    action.signals_sent += { signal: "SIGKILL", sent_at: now(), exit_after_ms: null }
    WAIT 1s
    IF process target.pid is not alive: action.final_state = "KILLED"
    ELSE: action.final_state = "STILL_ALIVE"; action.stderr_excerpt = "process did not respond to SIGKILL"
    actions += action
    continue

  # === Normal path: SIGTERM, grace, then SIGKILL if needed ===
  start = now()
  CALL: Bash kill -TERM {target.pid}
  action.signals_sent += { signal: "SIGTERM", sent_at: now(), exit_after_ms: null }

  # Wait for graceful exit, polling every 250ms up to grace_seconds
  elapsed_ms = 0
  WHILE elapsed_ms < (grace_seconds * 1000):
    SLEEP 250ms
    elapsed_ms += 250
    IF process target.pid is not alive:
      action.signals_sent[0].exit_after_ms = elapsed_ms
      action.final_state = "TERMINATED"
      BREAK

  IF action.final_state != "TERMINATED":
    # Still alive after grace — escalate
    CALL: Bash kill -KILL {target.pid}
    action.signals_sent += { signal: "SIGKILL", sent_at: now(), exit_after_ms: null }
    WAIT 1s
    IF process target.pid is not alive:
      action.final_state = "KILLED"
    ELSE:
      action.final_state = "STILL_ALIVE"
      action.stderr_excerpt = "process did not exit after SIGTERM + grace + SIGKILL"
      blockers += { kind: "process_zombie", role: target.role, pid: target.pid }

  actions += action

# === Aggregate ===
IF len(targets) == 0:
  teardown_status = NOTHING_TO_DO
ELIF every action.final_state in {TERMINATED, KILLED, ALREADY_DEAD, DRY_RUN}:
  teardown_status = CLEAN
ELSE:
  teardown_status = PARTIAL

FIDELITY CHECK:
  - len(actions) == len(PROCESS_LIST)
  - every action has final_state, signals_sent (may be empty when DRY_RUN)
  - when teardown_status == PARTIAL, blockers has at least one process_zombie entry
  - no action was taken against any pid in skipped[]

UPDATE TEARDOWN_INDEX.actions, teardown_status, decisions_log, blockers
UPDATE _progress.json: completed=2
LOG: "Step 2 COMPLETE. teardown_status: {teardown_status}. Actions: {summary of role=final_state}"
```

---

### Step 3: Write Report

Read `references/phase-c-teardown-report.md` before executing this step.

**Command:**
```
=== TEARDOWN-{SESSION_ID}.md ===

GENERATE per phase-c template (5 sections, zero prose):
  1. Session (project_name, session_id, mode, dry_run, force, teardown_status)
  2. Targets ({N}) — table of services we acted on (role, pid, port, url)
  3. Skipped ({N}) — services we did NOT touch (role, pid, reason)
  4. Actions ({N}) — per-target table (role, pid, signals_sent summary, exit_after_ms, final_state, stderr_excerpt)
  5. Decisions Log + Open Questions

WRITE {output_folder}/TEARDOWN-{SESSION_ID}.md — MANDATORY TOOL CALL.
spec_path = the written path.

=== TEARDOWN-AUDIT ===

GENERATE TEARDOWN-AUDIT-{SESSION_ID}.md (8-pattern compliance + files written + safety rules verified).

WRITE {output_folder}/TEARDOWN-AUDIT-{SESSION_ID}.md — MANDATORY TOOL CALL.
audit_path = the written path.

UPDATE TEARDOWN_INDEX.spec_path, audit_path
LOG: "Step 3 COMPLETE. Spec: {spec_path}, status: {teardown_status}"
```

---

### Step 4: Finalize

**LAST ACTION — MANDATORY:**

```
UPDATE _progress.json:
{
  "skill": "tearing-down-services",
  "session_id": "{SESSION_ID}",
  "status": "COMPLETED",
  "completed_at": "<ISO>",
  "total": 2,
  "completed": 2,
  "items": [
    { "phase": "target-identification", "status": "COMPLETE" },
    { "phase": "signal-and-verify", "status": "COMPLETE" }
  ]
}

Memory Bank:
  OVERWRITE context-pack/active-context.md with: session_id, teardown_status, killed count, skipped count
  APPEND to context-pack/progress.md:
    | {SESSION_ID} | {date} | tearing-down-services | {MODE} | {teardown_status} | 1 teardown report | {killed} killed, {skipped} skipped |

LOG: "Skill complete. teardown_status: {teardown_status}. Spec: {spec_path}."
```

---

### Step 5: Emit Harness Outputs Sidecar

**Apply execution-protocol.md Section 11** — Harness Output Sidecar. Mandatory when the prompt contains a `## Run metadata` block. FINAL file write of the run (after TEARDOWN-SPEC verification in Step 3, after Memory Bank in Step 4, after `_progress.json` set to COMPLETED). Without it, the orchestrator falls back to the capability `value_template`, which corrupts `teardown_spec_path` into a doubly-nested folder when the parameter has already been pre-resolved to an absolute path.

**Output parameters this skill produces** (one key per row of the prompt's `## Output parameters` table):

- `teardown_status`: `"CLEAN"` | `"PARTIAL"` | `"NOTHING_TO_DO"` | `"SKIPPED"` (from TEARDOWN-SPEC Section 1).
- `teardown_spec_path`: the resolved `output_folder` parameter VERBATIM — the folder that holds `TEARDOWN-*.md` and `TEARDOWN-AUDIT-*.md`. Do NOT re-prepend `{output_folder}` or `{project_name}`.
- `services_killed_count`: integer count of `actions[]` entries with final_state ∈ {TERMINATED, KILLED}.
- `services_skipped_count`: integer `len(skipped[])` from TEARDOWN-SPEC.

**Implementation:** the harness here accepts Bash heredoc for the sidecar write. Execute:

```
cat > {stepwise_outputs_file} << 'OUTPUTS_EOF'
{
  "teardown_status": "{teardown_status}",
  "teardown_spec_path": "{output_folder}",
  "services_killed_count": {services_killed_count},
  "services_skipped_count": {services_skipped_count}
}
OUTPUTS_EOF
```

`{stepwise_outputs_file}` is the path from the prompt's `## Run metadata` block's `output_file = '...'` line — copy it verbatim, do NOT reconstruct it.

Self-check: `cat {stepwise_outputs_file}` — verify non-empty and valid JSON. If empty, missing, or malformed, re-execute. DO NOT describe output registration in response text — EXECUTE it. No tool calls after this; the next event is `final_response`.

**Execution:** automated

---

## REPAIR Mode — Surgical Directives

| Target | Action |
|---|---|
| `role:{name}` | Retry teardown for one service role |
| `force` | Retry all targets with SIGKILL (skip SIGTERM grace) |
| `global` | Re-run everything |

---

## Safety Rules (HARD invariants)

### 1. Never Kill Reused Services
Any service with `reused_existing == true` is OFF-LIMITS. The skill does not own its
lifecycle — killing it would terminate a process the prior launcher is still expecting
to manage. Pre-flight check enforces this; violation is a critical bug.

### 2. Never Guess PIDs
The skill ONLY acts on PIDs explicitly present in `runtime_info.json`'s `services[]`
array. No port scanning, no `pgrep`, no name matching. If the JSON says null pid, the
skill skips that service.

### 3. PID Re-verification Before Kill
Right before sending any signal, the skill re-checks `ps -p {pid}` is alive. PIDs can
recycle on Unix — if the original process has already exited and the kernel reassigned
its number to an unrelated process, killing it would terminate a stranger.

### 4. Reused Services Are Reported, Not Modified
The skipped[] list records every untouched service with its reason. The report shows
operators exactly which services are still running and why this skill did not stop them.

### 5. Force Mode Requires Explicit Parameter
`force=true` skips SIGTERM and goes straight to SIGKILL. This is destructive for
processes that need cleanup hooks (DB connections, write buffers). The capability
should pass `force=false` by default; operators set it consciously.

---

## FIC Context Management

This skill runs in < 30s typically. FIC compaction is not expected. If grace_seconds is
set high (close to 60) and there are many services, the skill may approach 60% context
usage; at that threshold, truncate `services_all` to targets + skipped only (drop the
unused fields like health_probe, launched_at).

---

## Reference Files

- `references/phase-a-target-identification.md` — exhaustive classification rules + ps probing
- `references/phase-b-signal-and-verify.md` — kill semantics, grace polling, force escalation
- `references/phase-c-teardown-report.md` — TEARDOWN-SPEC template + fidelity gate
