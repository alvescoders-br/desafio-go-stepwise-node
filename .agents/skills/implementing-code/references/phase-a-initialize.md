# Phase A: Initialize Session

## Context Contract
- **Inputs:** Parameters (project_name, source_path, plan_folder_path, optional research_folder_path, progress_folder_path, failure_feedback)
- **Reads (Memory Bank):** `context-pack/active-context.md` (prior session state), `context-pack/progress.md` (cumulative milestone ledger)
- **Outputs:** Initialized IMPL_INDEX, IMPL-STATE file on disk, _progress.json early signal
- **Carries Forward:** IMPL_INDEX with session metadata, phase status table, source_path, Memory Bank context
- **Flush After:** Raw parameter text, plan index raw content
- **Dependency:** None (first phase)

---

## Mode Detection & Folder Resolution

Verify all required paths exist (`project_name`, `source_path`, `plan_folder_path`;
`research_folder_path` only when supplied). If `progress_folder_path` is not set, default to
`{plan_folder_path}/../progress`. Create `progress_folder_path` if absent.

**Scope re-anchor (apply BEFORE the first write — see SKILL.md "Path fidelity"):**
If `progress_folder_path` does NOT share `plan_folder_path`'s parent directory
(i.e. it is not already a sibling of the plan folder — the flat
`{output_folder}/implementation` vs scoped `{output_folder}/{SCOPE}/code-task-planning`
case that occurs when `feature_id` was unset and research/planning self-derived
`{SCOPE}`), set `progress_folder_path = dirname(plan_folder_path) + '/' + basename(progress_folder_path)`
and record a deviation. All subsequent `_progress.json`, IMPL-STATE, and §11
sidecar references use this re-anchored value.

Detect mode:
- If `failure_feedback` is non-empty and not a placeholder → `MODE = "REPAIR"`
- Otherwise → `MODE = "STANDARD"`

For session ID generation and dual-format plan/research detection,
see **execution-protocol.md**.

**Multiple-spec tie-breaker (mandatory when more than one match exists):**

When discovering input files in `plan_folder_path` and optional `research_folder_path`, multiple `PLAN-SPEC-*.md` or `RESEARCH-SPEC-*.md` files may be present (concurrent sessions, stale runs, or feature_id collisions on the same project folder). Pick deterministically:

1. List all candidates and sort by mtime descending.
2. Prefer the file whose SESSION_ID component matches the current `feature_id` parameter (or, when feature_id is unset, the Stepwise `session_name`). Match is exact-substring of the SESSION_ID-derived slug.
3. If none match by scope, pick the most-recently-modified. Log: `{TYPE}-SPEC selection: {filename} (mtime={...}, candidates={N})`.
4. **ABORT-with-guidance** if the top two candidates have mtimes within 1 second of each other AND neither matches the scope filter:
   `Cannot disambiguate {TYPE}-SPEC. Two specs were written within 1s of each other and neither matches the current feature_id/session_name. Re-run with feature_id set, or remove the stale spec from {folder}.`
   Call `stepwise session exec-fail` with this reason — silently picking the wrong spec would cause implementation against the wrong plan, which is harder to detect later than a fail-fast at Phase A.

The same rule applies to discovering existing IMPL-STATE files when entering REPAIR mode (see Mode: REPAIR below). If `research_folder_path` is absent, skip RESEARCH-SPEC discovery entirely.

**FIRST ACTION — MANDATORY:** Write `_progress.json` to `{progress_folder_path}`
before any other file write. This prevents the orchestrator from sending SIGINT.
Do NOT proceed to IMPL-STATE creation until `_progress.json` exists on disk.

```json
{
  "skill": "implementing-code",
  "session_id": "{SESSION_ID or 'initializing'}",
  "status": "RUNNING",
  "started_at": "{ISO timestamp}",
  "completed_at": null
}
```

---

## Memory Bank — Read and Write Prior Context

Follow execution-protocol.md Section 4: read `active-context.md` + `progress.md` at
session start, write `active-context.md` at session start (RULE 10).
If neither file exists, this is the first session — proceed without prior context.

---

## Mode: STANDARD (BUILD)

If IMPL-STATE file does not exist, initialize IMPL_INDEX and write it:

```
IMPL_INDEX fields to populate:
  session_id, project_name, source_path, project_root (= source_path),
  mode = "STANDARD", input_format (from detection),
  phases = [all phases from plan, status = PENDING],
  files_touched = [], repair_log = [], blockers = [], deviations = [],
  build_commands_discovered = [], tech_stack_detected = {}
```

**files_touched table format (EOL append readiness — MANDATORY):**
Write the table with header + separator only — zero data rows.
Phase B appends rows one by one without rewriting the full file:

```
## files_touched
| phase | file_path | action | status | test_file |
|-------|-----------|--------|--------|-----------|
```

**Output contract (RULE 21):**
Pin `output_contract` in the IMPL-STATE header. Update the existing `_progress.json`
(written above) to add `output_contract` fields — see execution-protocol.md for the extended schema.

**PHASE A GATE:** IMPL-STATE must exist on disk before Phase B can start.
Verify it exists and is non-empty. If missing, write it again — BLOCKING.

If IMPL-STATE already exists, load and parse IMPL_INDEX from it.

Find `TARGET_PHASE` = first phase with status PENDING or IN_PROGRESS.
- If all phases are COMPLETED → go to Phase D Final Summary.
- If only BLOCKED phases remain → exit with blocker report.

Update `TARGET_PHASE.status = IN_PROGRESS`.

---

## Mode: REPAIR

Load existing IMPL-STATE (must exist — abort if not found).

Before parsing, normalize `failure_feedback` into a concrete repair source:
- If `failure_feedback` names a `VALIDATION_REPORT.md`, `REVIEW-SPEC-*.md`, or
  `REVIEW-AUDIT-*.md` path, read that file and parse blocking/high findings from
  it.
- If `failure_feedback` is generic human text (for example "there are fails",
  "fix the review", "some issues remain") or contains no file/severity/finding
  rows, locate the latest review report in this order:
  1. explicit `review_output_path` parameter, if supplied;
  2. sibling `code-review-output` folder next to the current `progress_folder_path`;
  3. newest `VALIDATION_REPORT.md` under the capability `output_folder`.
  Read it before creating directives.
- If no review report exists, keep one `GLOBAL` directive and record
  `repair_feedback_source: generic_text_no_report` in `repair_log`.

Parse the normalized feedback/report into structured `REPAIR_DIRECTIVES`:

```
FOR each issue in normalized feedback/report:
  REPAIR_DIRECTIVES += {
    category: [MISSING_FILE | COMPILATION_ERROR | SYNTAX_ERROR |
               CONFIG_ERROR | RUNTIME_ERROR | LOGIC_ERROR | OTHER],
    target_files: [...],
    instruction: specific fix description
  }
```

If feedback is too vague to parse, create one `GLOBAL` directive.

Determine `TARGET_PHASE`:
- If any phase has status FAILED → use that phase.
- Otherwise → use the last COMPLETED phase (re-repair).

Create a new `repair_log` entry. Update IMPL-STATE to disk.

---

## Cross-Artifact Scope Validation (mandatory after PLAN is loaded)

After PLAN-SPEC is loaded, and optional RESEARCH-SPEC only if fallback research was supplied, verify scopes BEFORE the first Phase B file write. This prevents the failure mode where the wrong plan or fallback research was selected from a shared folder.

```
EXTRACT scope identifiers:
  PARAM_SCOPE   = feature_id (parameter) OR session_name (Stepwise) OR null
  PLAN_SCOPE    = parse first 30 lines of PLAN_FILE for any of:
                    `session_id:`, `feature_id:`, frontmatter `feature:`, the `# {TYPE}-SPEC-...` heading
                  → extract the SESSION_ID/feature_slug component
  RESEARCH_SCOPE = same parse against RESEARCH_FILE if research fallback is supplied; otherwise null
  IMPL_PRIOR_SCOPE = (REPAIR mode only) parse the prior IMPL-STATE header

CASE 1 — PARAM_SCOPE is null (standalone or pre-fix legacy run):
  No assertion possible. LOG once:
    "WARNING: feature_id/session_name not provided. Cross-scope validation skipped.
     Concurrent sessions in this folder cannot be safely disambiguated."
  Continue.

CASE 2 — PARAM_SCOPE is set:
  IF PLAN_SCOPE is null AND RESEARCH_SCOPE is null:
    LOG: "WARNING: neither plan nor optional research carries a SESSION_ID header — cannot cross-validate. Treating as scope-less inputs."
    Continue.

  IF PLAN_SCOPE is set AND PARAM_SCOPE is NOT a substring of PLAN_SCOPE
     (case-insensitive, after slug-normalization):
    THIS IS A BLOCKING MISMATCH.
    APPEND to IMPL_INDEX.blockers:
      { phase: "A", description: "scope mismatch — parameter feature_id/session_name does not match PLAN_SPEC SESSION_ID",
        param_scope: PARAM_SCOPE, plan_scope: PLAN_SCOPE, plan_file: PLAN_FILE,
        timestamp: now, resolution: "REQUIRES_HUMAN_REVIEW" }
    WRITE IMPL-STATE with status = BLOCKED.
    CALL `stepwise session exec-fail` with reason:
      "Plan scope mismatch: param={PARAM_SCOPE}, plan={PLAN_SCOPE}.
       The plan loaded from {PLAN_FILE} appears to belong to a different feature/session.
       Verify feature_id is correct, or remove stale plan files from {plan_folder_path}."
    Do NOT proceed to Phase B.

  IF optional RESEARCH_SCOPE is set AND PARAM_SCOPE is NOT a substring of RESEARCH_SCOPE:
    THIS IS A BLOCKING MISMATCH (same handling as plan above, with description
    "scope mismatch — parameter feature_id/session_name does not match fallback RESEARCH_SPEC SESSION_ID").

  IF PLAN_SCOPE is set AND RESEARCH_SCOPE is set AND PLAN_SCOPE != RESEARCH_SCOPE:
    THIS IS A BLOCKING MISMATCH.
    The plan was generated against a different research than the fallback research currently supplied.
    APPEND to IMPL_INDEX.blockers and call exec-fail with reason:
      "Plan/research scope mismatch: plan={PLAN_SCOPE}, research={RESEARCH_SCOPE}.
       The plan was built against a different research artifact than the fallback selected here.
       This usually indicates concurrent sessions overwrote each other's research."

  ELSE (all three scopes align):
    LOG: "Scope validation passed. param={PARAM_SCOPE}, plan={PLAN_SCOPE}, research={RESEARCH_SCOPE or 'not supplied'}."

  IF MODE == REPAIR AND IMPL_PRIOR_SCOPE is set AND IMPL_PRIOR_SCOPE != PARAM_SCOPE:
    THIS IS A BLOCKING MISMATCH (REPAIR is supposed to continue the same session).
    Call exec-fail with reason:
      "REPAIR scope mismatch: param={PARAM_SCOPE}, prior IMPL-STATE={IMPL_PRIOR_SCOPE}.
       REPAIR must reuse the same SESSION_ID. Re-run BUILD if you intend a new feature."
```

This validation is the only end-to-end check that Fixes A and B are working as intended — without it, a wrong-spec selection would silently flow through Phase B and corrupt the implementation against the wrong plan.

---

## Research Fingerprint Guard (mandatory when PLAN header provides it)

After PLAN-SPEC is selected and before Phase B:

```
READ the PLAN-SPEC header fields:
  research_source
  research_fingerprint

IF research_fingerprint is present and not "N/A":
  IF research_fingerprint does not match `^sha256:[a-f0-9]{64}$`:
    WRITE IMPL-STATE with status = BLOCKED.
    CALL `stepwise session exec-fail` with reason:
      "Invalid research_fingerprint format: expected sha256:<64 lowercase hex chars>, got {research_fingerprint}. Re-run planning."
    Do NOT proceed to Phase B.

  VERIFY research_source still exists.
  COMPUTE current_fingerprint by hashing the selected RESEARCH-SPEC bytes as
  `sha256:<hash>`; never compare mtimes.

  IF current fingerprint != research_fingerprint:
    IF custom_instructions includes explicit `allow_stale_research=true`:
      RECORD IMPL-STATE deviation:
        "Research fingerprint mismatch overridden by operator; implementation proceeds from PLAN-SPEC contract."
      Continue.
    ELSE:
      WRITE IMPL-STATE with status = BLOCKED.
      CALL `stepwise session exec-fail` with reason:
        "Research fingerprint mismatch: PLAN-SPEC was derived from {research_fingerprint}, current research_source is {current_fingerprint}. Re-run planning before implementation."
      Do NOT proceed to Phase B.
```

The normal executor still does not load RESEARCH-SPEC for implementation. This
guard exists only to prevent silent stale-research drift.

---

## Post-Phase Protocol

1. **VERIFY** IMPL_STATE_FILE exists on disk and is non-empty — BLOCKING GATE.
2. **VERIFY** Cross-Artifact Scope Validation above ran and either passed or short-circuited via exec-fail. A Phase A that emits a final log without running this check is a protocol violation.
3. **VERIFY** Research Fingerprint Guard above ran when the PLAN-SPEC header had `research_fingerprint` not equal to `N/A`.
4. **Flush** raw plan index content from memory.
5. **Retain** only IMPL_INDEX (carry-forward).
6. **Log:** "Phase A complete. IMPL-STATE verified at {IMPL_STATE_FILE}. Mode: {MODE}. Target: {TARGET_PHASE}. Scope: {PARAM_SCOPE}."
