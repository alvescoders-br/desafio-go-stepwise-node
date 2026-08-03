# tearing-down-services — Phase B: Signal & Verify

## Context Contract

- **Inputs:** `TEARDOWN_INDEX.targets[]`, parameters `grace_seconds`, `dry_run`, `force`
- **Outputs:** `TEARDOWN_INDEX.actions[]`, `TEARDOWN_INDEX.teardown_status`, `TEARDOWN_INDEX.blockers`
- **Carries Forward:** actions, teardown_status (consumed by Phase C)
- **Flush After:** Per-action working state — only structured action records survive
- **Dependency:** Phase A must be COMPLETE
- **H1 Title:** `# Phase B — Signal & Verify`

## Mode-Specific Behavior

- **BUILD:** Send SIGTERM → wait grace_seconds → SIGKILL if needed.
- **`force=true`:** Skip SIGTERM, send SIGKILL directly.
- **`dry_run=true`:** No signals; record `final_state=DRY_RUN`.
- **REPAIR — `role:{name}`:** Re-execute Phase B for the named role only.
- **REPAIR — `force`:** Re-execute Phase B for all targets with SIGKILL.

---

## Signal Semantics

| Signal | When | Effect | Process gets to |
|---|---|---|---|
| SIGTERM (15) | Default first signal | Polite shutdown request | Run cleanup hooks: close DB connections, flush write buffers, save state |
| SIGKILL (9) | After grace_seconds OR `force=true` | Unconditional termination | NOTHING — kernel reaps immediately |

Send via `kill -TERM {pid}` or `kill -KILL {pid}`. Always use the explicit name form to
avoid platform differences on signal numbers.

---

## Per-Target Procedure

```
FOR EACH target in PROCESS_LIST:
  action = { role: target.role, pid: target.pid, signals_sent: [], stderr_excerpt: "" }

  # === Pre-flight re-check (HARD safety) ===
  CALL: ps -p {target.pid} -o pid= -o lstart=
  IF non-zero exit OR empty output:
    action.final_state = "ALREADY_DEAD"
    actions += action
    continue

  # Cross-check lstart vs launched_at (defends against pid reuse)
  IF lstart < target.launched_at:
    action.final_state = "ALREADY_DEAD"
    action.stderr_excerpt = "lstart {lstart} predates launched_at {launched_at} — pid reuse"
    actions += action
    continue

  # === DRY-RUN short-circuit ===
  IF dry_run == true:
    action.final_state = "DRY_RUN"
    actions += action
    continue

  # === FORCE path: straight to SIGKILL ===
  IF force == true:
    sent_at = now()
    CALL: kill -KILL {target.pid}
    action.signals_sent += { signal: "SIGKILL", sent_at, exit_after_ms: null }
    SLEEP 1s
    CALL: ps -p {target.pid}
    IF not alive:
      action.final_state = "KILLED"
    ELSE:
      action.final_state = "STILL_ALIVE"
      action.stderr_excerpt = "process did not respond to SIGKILL within 1s"
      blockers += { kind: "process_zombie", role: target.role, pid: target.pid }
    actions += action
    continue

  # === Normal path ===

  # 1. SIGTERM
  sigterm_at = now()
  CALL: kill -TERM {target.pid}
  action.signals_sent += { signal: "SIGTERM", sent_at: sigterm_at, exit_after_ms: null }

  # 2. Wait for graceful exit (poll every 250ms up to grace_seconds)
  elapsed_ms = 0
  exited = false
  WHILE elapsed_ms < (grace_seconds * 1000):
    SLEEP 250ms
    elapsed_ms += 250
    CALL: ps -p {target.pid}
    IF not alive:
      action.signals_sent[0].exit_after_ms = elapsed_ms
      action.final_state = "TERMINATED"
      exited = true
      BREAK

  # 3. Escalate to SIGKILL if still alive
  IF NOT exited:
    sigkill_at = now()
    CALL: kill -KILL {target.pid}
    action.signals_sent += { signal: "SIGKILL", sent_at: sigkill_at, exit_after_ms: null }
    SLEEP 1s
    CALL: ps -p {target.pid}
    IF not alive:
      action.final_state = "KILLED"
    ELSE:
      action.final_state = "STILL_ALIVE"
      action.stderr_excerpt = "process did not exit after SIGTERM + grace + SIGKILL"
      blockers += { kind: "process_zombie", role: target.role, pid: target.pid }

  actions += action
```

---

## Why SIGTERM First (and not just SIGKILL)

Most app frameworks register a SIGTERM handler that:
- Closes DB connections cleanly (avoiding connection pool exhaustion on the DB side)
- Flushes pending writes (file buffers, log streams)
- Releases ports atomically (rather than waiting for TCP TIME_WAIT)
- Cancels in-flight work (cancels child workers, drains queues)

SIGKILL bypasses all of this. The framework cannot intercept. State that should have
been persisted may be lost. Open file handles linger as zombies under certain kernels.
Database connections leak until the DB detects timeout (can be minutes).

`grace_seconds=5` is enough for most stacks. Spring Boot apps with heavy DB workloads
may need 15-30s. Adjust via parameter when the runtime stack documents a longer shutdown.

---

## Final State Enumeration

| state | What it means | What the operator should do |
|---|---|---|
| `TERMINATED` | SIGTERM was honoured within grace_seconds | Nothing — clean exit |
| `KILLED` | SIGKILL was needed (process did not respond to SIGTERM) | Investigate whether the framework's shutdown hook is broken |
| `ALREADY_DEAD` | Process exited before this skill could signal it | Nothing — already cleaned up |
| `STILL_ALIVE` | Even SIGKILL did not work (zombie, kernel issue, parent process holding it) | Manual `kill -9 -{pid}` of process group, or reboot |
| `DRY_RUN` | dry_run=true; no signal sent | Re-run with dry_run=false to actually terminate |

`STILL_ALIVE` adds a blocker entry — the capability gate (or operator) should see it.

---

## REPAIR Surgical Re-Execution

```
IF mode == REPAIR:
  target_directive = REPAIR_DIRECTIVES[0].target

  IF target_directive == "role:{name}":
    PROCESS_LIST = filter targets to that role
    PRESERVE: actions for other roles from PRIOR_TEARDOWN

  ELIF target_directive == "force":
    PROCESS_LIST = all current targets
    force = true (override parameter)

  ELIF target_directive == "global":
    PROCESS_LIST = all current targets (normal path)
```

---

## Source Fidelity Check (before exiting Phase B)

- [ ] `len(actions) == len(PROCESS_LIST)` (no missed targets)
- [ ] Every action has `final_state ∈ {TERMINATED, KILLED, ALREADY_DEAD, STILL_ALIVE, DRY_RUN}`
- [ ] Every TERMINATED action has `signals_sent[0].exit_after_ms` set (the grace observation)
- [ ] Every KILLED action has 2 signals_sent entries (SIGTERM + SIGKILL) OR force=true (1 entry)
- [ ] Every STILL_ALIVE action has a corresponding `blockers[]` entry
- [ ] No action was performed against any pid in `skipped[]` (HARD invariant — re-verify by intersecting actions.pid vs skipped.pid; intersection MUST be empty)

## Post-Section Protocol

1. **Update** `TEARDOWN_INDEX.actions`, `teardown_status`, `blockers`, `decisions_log`
2. **Update** `_progress.json`: `completed: 2`
3. **Flush** per-target working state (keep only structured action records)
4. **Verify** the fidelity-check assertions
5. **Log:** `"Phase B COMPLETE. status={teardown_status}. Actions: {role}={final_state} pairs"`
