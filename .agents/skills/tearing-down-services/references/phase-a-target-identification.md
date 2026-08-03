# tearing-down-services — Phase A: Target Identification

## Context Contract

- **Inputs:** `runtime_info_path`, optional `failure_feedback`
- **Outputs:** `TEARDOWN_INDEX.targets[]`, `TEARDOWN_INDEX.skipped[]`, `TEARDOWN_INDEX.services_all`
- **Carries Forward:** targets (consumed by Phase B)
- **Flush After:** Raw runtime_info.json content (retain only services_all + classified targets)
- **Dependency:** Step 1 init must be COMPLETE
- **H1 Title:** `# Phase A — Target Identification`

## Mode-Specific Behavior

- **BUILD:** Classify every service in runtime_info.json as `target` or `skipped`.
- **REPAIR — `role:{name}`:** Re-classify ONLY the named role; preserve other classifications from PRIOR_TEARDOWN.
- **REPAIR — `force`:** Re-classify all targets; preserve skipped[].
- **REPAIR — `global`:** Re-classify everything from scratch.

---

## Classification Decision Tree

For each `service` in `RUNTIME_INFO.services[]`, apply these checks in order. The FIRST
matching rule wins:

```
1. IF service.reused_existing == true
   → skipped, reason = "reused_existing"
   Rationale: prior launcher owns this process; killing it leaks ownership.

2. ELIF service.pid is null OR service.pid <= 0
   → skipped, reason = "no_pid"
   Rationale: we don't have a handle to anything to signal.

3. ELIF service.launch_status != "RUNNING"
   → skipped, reason = "not_running ({status})"
   Rationale: FAILED or TIMEOUT services should already be dead (or never started);
   trying to kill might either be a no-op or hit a recycled PID.

4. ELIF `ps -p {service.pid}` returns non-zero (process not alive)
   → skipped, reason = "already_dead"
   Rationale: process exited between launching-app's report and this skill running.

5. ELSE
   → target, with pid, port, url, log_path, launch_status copied through
```

The reasons are part of the OUTPUT — they show up verbatim in the TEARDOWN-SPEC's
Section 3 (Skipped). Use the exact strings listed above so report grep stays stable.

---

## ps Probing (the alive check)

The "is process alive?" check must NOT use shell expansions that could match the wrong
process. The single safe form:

```
COMMAND: ps -p {pid} -o pid= -o state=
EXIT 0 + non-empty output → alive
EXIT non-zero OR empty output → dead (or never existed)
```

Do NOT use `ps aux | grep` — false positives are easy (the grep itself, processes with
similar names, recycled PIDs from a name match).

Optionally capture the process's command and start time:

```
ps -p {pid} -o pid=,lstart=,comm=
```

This goes into `decisions_log` so the audit shows WHAT the skill was about to kill (a
sanity record — when reviewing a teardown report later, the operator can confirm we
killed the right thing).

---

## Edge Case: PID Reuse

Unix PIDs recycle. A pid in `runtime_info.json` may have been reassigned to a totally
unrelated process by the time this skill runs. Two defenses:

1. **Cross-check `lstart`** (process start time). The launching-app skill records
   `services[].launched_at`. If `ps -p {pid} -o lstart=` returns a time EARLIER than
   `launched_at`, the original process exited and a new one took the pid. SKIP it as
   `already_dead`.
2. **Cross-check `comm`** (process name). When `lstart` confirms the time, the command
   should match a node / python / java / ruby process. If `comm` is something like
   `bash` or `vim`, treat as `already_dead` (pid reuse).

These defenses are best-effort — `lstart` granularity is seconds, so a same-second
relaunch could fool it. Pragmatically the launching-app session ID is in the report and
operators can verify post-hoc.

---

## REPAIR Mode — Surgical Re-Classification

```
IF mode == REPAIR:
  target_directive = REPAIR_DIRECTIVES[0].target

  IF target_directive == "role:{name}":
    PRESERVE: TEARDOWN_INDEX.targets and skipped from PRIOR_TEARDOWN for all roles != name
    RE-CLASSIFY: only the named role per the decision tree above
    decisions_log += { phase: "phase-a", decision: "REPAIR: reclassified role={name}", evidence: target_directive }

  ELIF target_directive == "force":
    PRESERVE: skipped[] from PRIOR_TEARDOWN (don't escalate skipped services to targets)
    RECLASSIFY: targets from PRIOR_TEARDOWN — verify each pid is still alive
      IF still alive: keep in targets[]; Phase B will SIGKILL it
      IF dead: move to skipped, reason = "already_dead"

  ELIF target_directive == "global":
    FULL RECLASSIFY: per BUILD path above
```

---

## Source Fidelity Check (before exiting Phase A)

- [ ] `services_all` count equals `len(RUNTIME_INFO.services)`
- [ ] `len(targets) + len(skipped) == len(services_all)` (no orphans, no duplicates)
- [ ] Every `targets` entry has numeric pid > 0 AND a verified alive `ps -p` result
- [ ] Every `skipped` entry has a `reason` from the fixed set: `reused_existing`, `no_pid`, `not_running ({status})`, `already_dead`
- [ ] No entry in `targets` has `reused_existing == true` (HARD invariant)

## Post-Section Protocol

1. **Update** `TEARDOWN_INDEX.targets`, `skipped`, `services_all`, `decisions_log`
2. **Update** `_progress.json`: `completed: 1`
3. **Flush** raw runtime_info.json content (keep only the structured arrays)
4. **Verify** the fidelity-check assertions; if any fails, halt with an error before Phase B
5. **Log:** `"Phase A COMPLETE. {len(targets)} targets, {len(skipped)} skipped ({reasons summary})"`
