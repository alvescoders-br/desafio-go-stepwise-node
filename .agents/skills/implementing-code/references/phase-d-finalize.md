# Phase D: Finalize Phase

## Context Contract
- **Inputs:** IMPL_INDEX with all phases complete, build verification results
- **Outputs:** Updated IMPL_STATE_FILE, phase retrospective data
- **Writes (Memory Bank):** `context-pack/active-context.md` (current state snapshot), `context-pack/progress.md` (append milestone entry)
- **Carries Forward:** Final IMPL_INDEX for next phase (if any)
- **Flush After:** Phase-specific code context
- **Dependency:** Phase C must be COMPLETE

---

## Step 0: Phase C Artifact Verification (Defense-in-Depth)

Safety net in case Phase C's own gate was bypassed:

- Verify README.md exists at `{IMPL_INDEX.project_root}/README.md`. If missing → go back to Phase C Step 4.
- On final phase: verify AGENTS.md exists at `{IMPL_INDEX.project_root}/AGENTS.md`. If missing → go back to Phase C Step 5.

LOG: "Phase C artifacts verified. Proceeding to finalize."

---

## Step 1: Determine Phase Status

```
EVALUATE results from Phase B and Phase C:

## ── Build / test gate first (CAL-INF-001) ──────────────────────────────
## The Phase C Completion Gate already classified any UNRESOLVED build/test
## failure (one that survived the 3 self-correction attempts) into
## IMPL_INDEX.phase_c_outcome. A genuine failure must NOT be downgraded to a
## warning — that was the old fall-through this fix removes.
## NOTE: this is a status assignment, NOT a retry. Phase D never re-runs tests.
## REPAIR (for FAILED) is driven by the orchestrator re-invoking the skill with
## failure_feedback — externally bounded, no loop inside this run.

IF IMPL_INDEX.phase_c_outcome == "FAILED":
  STATUS = "FAILED"
  ## Genuine build/test failure (assertion, compile error, logic bug). The code
  ## does not work. Route to REPAIR — do NOT emit a success/warning summary.

ELSE IF IMPL_INDEX.phase_c_outcome == "BLOCKED":
  STATUS = "BLOCKED"
  ## Environmental failure — the runner could not build/execute (sandbox,
  ## unavailable service, no network). Code may be correct; a human must unblock.

ELSE IF all files written successfully AND scaffolding gate passed:
  IF build verification passed OR was skipped (no bash):
    STATUS = "COMPLETED"
  ELSE:
    IF build errors are in blockers with "Manual fix needed":
      STATUS = "COMPLETED_WITH_WARNINGS"
      ## Reserved for NON-build / NON-test residue only (e.g., a tolerated lint
      ## or typecheck warning). An unresolved build/test failure can never reach
      ## here — it was already caught above as FAILED/BLOCKED.
    ELSE:
      STATUS = "FAILED"

IF any files failed to write:
  STATUS = "FAILED"
  ## File write failures are unrecoverable within this session.
  ## The human must diagnose (permissions, disk, path issues) and re-invoke with failure_feedback.

IF blockers exist that prevent continuation:
  STATUS = "BLOCKED"
  ## Blockers indicate external dependencies that the agent cannot resolve.
  ## Examples: missing API credentials, unavailable services, ambiguous requirements.

IF any blocker has resolution == "REQUIRES_PLAN_REVISION":
  STATUS = "ARCHITECTURE_FLAW"
  ## This status signals that the plan itself is flawed — the architectural approach
  ## doesn't work in practice (e.g., incompatible library versions, circular dependencies,
  ## impossible constraints discovered during implementation).
  ## The capability orchestrator should route back to the planning phase,
  ## NOT retry implementation. The human must revise the plan.
```

---

## Step 2: Update IMPL-STATE and Memory Bank

**Update IMPL_INDEX:**
- Set `phases[ACTIVE_PHASE].status = {STATUS}`, `completed_at = now`, `files_count`, `tests_count`
- If REPAIR mode: finalize `repair_log` entry with all `files_modified` and `change_summary`
- Log any plan adherence returns that occurred during this phase

**Write IMPL_STATE_FILE to disk — MANDATORY TOOL CALL**

**Memory Bank — Append phase milestone to `context-pack/progress.md` (RULE 11):**

> **This is a SEPARATE write from updating IMPL-STATE — two different files.**
> IMPL-STATE tracks this session. progress.md is a cross-session ledger shared across
> ALL capabilities. Writing IMPL-STATE does NOT satisfy this step.
> This runs after EVERY phase — not only the final one.

Follow execution-protocol.md RULE 11 for header creation (if needed) and row format.
Memory Bank artifact type: `"N files, M tests"` (e.g., `"48 files, 32 tests"`).

---

## Step 3: Fill Phase Retrospective

If STATUS is COMPLETED or COMPLETED_WITH_WARNINGS, capture in IMPL-STATE execution_log:
- What went well, challenges, deviations from plan
- Build verification result (PASS / PASS with auto-fixes / SKIPPED)
- Self-corrections made (count)
- Files not in plan (emergent files created)

No longer written to plan files — data lives in IMPL-STATE execution_log and validations sections.

---

## Step 4: Update Audit Trail

Append to IMPL_STATE_FILE execution_log:
- Execution entry: `| {now} | {ACTIVE_PHASE} | {STATUS} | {details} |`
- Updated metrics: files created, files modified, tests created, self-corrections, repair iterations, build verifications

FLUSH IMPL_STATE_FILE to disk — MANDATORY TOOL CALL

---

## Step 4B: Final IMPL-STATE Self-Check

Before Step 5 or any final response, run this gate against the written
IMPL_STATE_FILE. This is exit-blocking for `COMPLETED` and
`COMPLETED_WITH_WARNINGS`.

Required checks:
- Header status is terminal: `completed`, `completed_with_warnings`, `failed`,
  `blocked`, or `architecture_flaw`.
- No final WFF markers remain pending:
  `! grep "WFF-SECTION:.*:pending" "$IMPL_STATE_FILE"`.
- Empty `blockers`, `deviations`, and `execution_log` sections contain explicit
  `none` rows and `complete` markers, not pending markers.
- `files_touched` contains every tracked file created or modified in this run.
  Verify with `git -C {source_path} status --short` and the plan file list.
- `metrics` and `tool_results` reflect the latest executed tool output
  (test/build pass counts, files created/modified, repair iterations).
- `validations` has rows for scaffolding, plan adherence, AC coverage, tool
  build/test/lint/typecheck as applicable, README, AGENTS.md, and the Phase C
  completion gate.
- The source worktree is clean before a completed exit:
  `git -C {source_path} status --short` returns no rows, unless the run is
  terminal `FAILED`/`BLOCKED` and the dirty files are listed in blockers.

If any check fails, repair IMPL_STATE_FILE or commit/record the missing file
state, then re-run this gate once. If it still fails, set STATUS = "FAILED",
write the failure to `blockers`, and call `stepwise session exec-fail` with:

```
Implementation FAILED: IMPL-STATE final self-check failed. See IMPL-STATE blockers.
```

---

## Step 5: Determine Next Action

**If COMPLETED or COMPLETED_WITH_WARNINGS:**

Check for next PENDING phase in IMPL_INDEX:
- If `NEXT_PHASE` exists AND `execution_scope != "single"`:
  - Update `active_phase = NEXT_PHASE`, set status = IN_PROGRESS
  - Flush IMPL_STATE_FILE
  - **CONTINUATION MANDATE:**
    **DO NOT STOP. Continue processing the next phase.**
    **DO NOT wait for human confirmation.**
    **DO NOT write stepwise output parameters yet.**
    **GOTO SKILL.md Step 3 (Phase B) — load next phase document and execute.**
- If `NEXT_PHASE` exists AND `execution_scope == "single"`:
  - Log "single scope — stopping after this phase"
  - Write stepwise output parameters and finish
- If no NEXT_PHASE: go to Step 6 (Final Summary)

**If FAILED:**
Write IMPL-STATE (status=FAILED, blockers, tool_results) and Memory Bank, THEN
escalate so the orchestrator routes to REPAIR — do NOT emit a success or
"completed-with-warnings" summary for an unresolved build/test failure:

```
stepwise session exec-fail --message "Implementation FAILED: unresolved {build|test} failure after 3 self-correction attempts. See IMPL-STATE blockers / tool_results (failure_class=GENUINE). Re-invoke in REPAIR mode with failure_feedback."
```

This is a terminal exit, not a retry — the skill does NOT re-run tests here. The
bounded iteration is the orchestrator re-invoking the skill in REPAIR mode with
`failure_feedback`; repair attempts are tracked in `repair_log` and capped by the
orchestrator. Do NOT prompt for interactive input — this is headless execution.

**If BLOCKED:**
Log blocker description (environmental — runner could not build/execute). Write
IMPL-STATE and Memory Bank, then surface the blocker per the Escape Hatch Protocol
so a human can unblock. Do NOT silently mark the phase COMPLETED. Terminal exit —
no retry loop.

**If ARCHITECTURE_FLAW:**
Log the flaw and specify "ACTION REQUIRED: Return to Planning phase — do NOT retry implementation."

---

## Step 6: Final Summary (All Phases Complete)

```
## NOTE: This summary is a session-end convenience output (human-facing).
## The structured data lives in IMPL_STATE_FILE metrics + open_questions sections.
## A richer human-readable report can be generated via humanize-spec with the
## code-implementation rendering profile.

GENERATE summary:

  READ: IMPL_INDEX (complete)

  COMPILE metrics:
    - Total phases
    - Phases completed / failed / blocked
    - Total files created + modified
    - Total tests created
    - Total repair iterations
    - Total build verifications
    - Deviations from plan

  OUTPUT:
    # Implementation Complete: {project_name}

    ## Summary
    | Metric | Value |
    |--------|-------|
    | Session ID | {session_id} |
    | Total Phases | {N} |
    | Status | {COMPLETE / PARTIAL} |
    | Files Created | {N} |
    | Files Modified | {N} |
    | Tests Created | {N} |
    | Build Verified | {YES / NO / PARTIAL} |
    | Repair Iterations | {N} |

    ## Phase Results
    | Phase | Status | Files | Tests | Build |
    |-------|--------|-------|-------|-------|
    {for each phase}

    ## Build Verification
    {summary of what was tested and results}

    ## README Location
    {path to generated README.md}

    ## Deviations from Plan
    {list or "None"}

    ## Known Issues / Warnings
    {from blockers and COMPLETED_WITH_WARNINGS}

    ## Next Steps
    - [ ] Review generated code
    - [ ] Run full test suite (see README.md)
    - [ ] Deploy per deployment strategy
    - [ ] Validate acceptance criteria manually

    ## Artifacts
    - IMPL State: {IMPL_STATE_FILE}
    - README: {README_PATH}
    - AGENTS.md: {AGENTS_PATH} (if generated — final phase only)
    - Plan: {plan_folder_path}

LOG: "Implementation session complete."
```

---

## Step 7: Update Memory Bank — active-context.md

Write final session state to `context-pack/active-context.md` (OVERWRITE — represents "now").
This file is read by the next session's Phase A to understand "where are we?"

```
WRITE context-pack/active-context.md:

  ---
  document_type: active-context
  session_id: {SESSION_ID}
  project: {project_name}
  last_updated: {ISO timestamp}
  status: {STATUS}
  ---

  # Active Context: {project_name}

  ## Current Focus

  {IF STATUS == "COMPLETED" and all phases done:}
    All implementation phases complete. Code is ready for review.
    Last phase: {ACTIVE_PHASE} — {files_count} files, {tests_count} tests.
  {IF STATUS == "COMPLETED" and more phases remain:}
    Phase {ACTIVE_PHASE} complete. Next pending: {NEXT_PHASE}.
    Focus area: {phase description from plan index}
  {IF STATUS == "FAILED":}
    Phase {ACTIVE_PHASE} failed. Needs REPAIR.
    Failure: {IMPL_INDEX.blockers[-1].description or failure summary}
  {IF STATUS == "BLOCKED" or "ARCHITECTURE_FLAW":}
    Phase {ACTIVE_PHASE} blocked.
    Blocker: {IMPL_INDEX.blockers[-1].description}
    Required action: {resolution from blocker entry}

  ## Recent Decisions

  {List deviations from plan with justifications — from IMPL_INDEX.deviations}
  {List technology choices discovered during implementation — from tech_stack_detected}
  {If no deviations: "No deviations from plan."}

  ## Open Blockers

  {List unresolved blockers from IMPL_INDEX.blockers where resolution != "RESOLVED"}
  {If none: "No open blockers."}

  ## Key Files

  | Category | Path | Notes |
  |----------|------|-------|
  | IMPL State | {IMPL_STATE_FILE} | Session-scoped state (progress, audit, metrics) |
  | Plan | {plan_folder_path} | Implementation plan |
  | Source | {source_path} | Implemented code |
```

For `progress.md`: verify it was written in Step 2. Do NOT re-append here — Step 2 owns that write.

Verify both `active-context.md` and `progress.md` exist and are non-empty.
LOG: "Memory Bank updated. active-context.md and progress.md written to context-pack."

---

## Post-Phase Protocol (Final)

1. Write final IMPL_STATE_FILE to disk.
2. Write Memory Bank files (active-context.md verified, progress.md verified).
3. Verify IMPL_STATE_FILE and Memory Bank files exist and are non-empty.
4. Log: "Phase D complete. Implementation session finished."
