# Phase B: Execute Implementation

## Context Contract
- **Inputs:** IMPL_INDEX (from Phase A, includes `source_path` and `project_root`), PLAN-SPEC phase load set, explicitly required artifacts
- **Outputs:** Generated source files, test files — all written under `{IMPL_INDEX.project_root}/`
- **Carries Forward:** Updated IMPL_INDEX with files_touched, repair_log
- **Flush After:** Each file's content after writing. Phase document after all files done.
- **Dependency:** Phase A must be COMPLETE

## Source Directory

All file creation and modification happens under `{IMPL_INDEX.project_root}` (i.e., `{source_path}`).
File paths in plan documents may be relative — resolve them against `{IMPL_INDEX.project_root}`.
Do NOT write source files into the plan, research, or progress directories.

---

## Step 0: Post-Compaction Recovery (execute ONLY after context continuation)

```
IF you are resuming after a context compaction boundary (compact_boundary event,
   continuation summary, or you have no memory of prior file reads in this session):

  ## MANDATORY: Read recovery files BEFORE doing anything else.
  ## This prevents the #1 waste pattern: re-reading 10+ files that were already processed.

  1. READ {progress_folder_path}/RECOVERY-CHECKPOINT-{session_id}.md
     IF exists:
       EXTRACT: current_phase, current_file, completed_files, key_decisions, next_action
       LOG: "Recovery checkpoint loaded. Resuming: {next_action}"
     ELSE:
       LOG: "No recovery checkpoint found. Falling back to IMPL-STATE."

  2. READ {progress_folder_path}/IMPL-STATE-{session_id}.md
     EXTRACT: files_touched (with status), active_phase, output_contract
     LOG: "IMPL-STATE loaded. {N} files already completed."

  3. DETERMINE what to read next:
     - Do NOT re-read files listed in IMPL-STATE files_touched with status: COMPLETED
     - Do NOT re-read research/plan sections already summarized in the recovery checkpoint
     - READ ONLY:
       a) The PLAN-SPEC phase load set for the CURRENT phase (header, required_artifacts, canonical_values, phase block, related ACs/open questions)
       b) The current file being worked on (if status was IN_PROGRESS)
       c) Required artifact files listed for the current phase

  4. RESUME from the "next_action" in the recovery checkpoint.
     If no checkpoint exists, resume from the first PENDING file in IMPL-STATE.

  LOG: "Post-compaction recovery complete. Skipped re-reading {N} completed files."
```

---

## Step 0.5: Pre-Phase Git Snapshot (MANDATORY before Phase B writes)

```
This step exists because the only reliable recovery surface from a destructive
edit (file wiped by an Edit collision, accidental Write overwrite, or a
truncating tool failure) is git. Without a git baseline, recovery degrades to
guesswork and the agent burns tokens scavenging caches that never contain the
file. See references/recovery-protocol.md for the failure mode this prevents.

PRE-FLIGHT CHECK (run once at the start of each phase, before any file write):

  cd {source_path}
  git status --short

  IF the working tree is dirty (any output from `git status --short` that is
     NOT a wip(impl) commit's untracked artefact):
    OPTION A — clean tree was expected but isn't:
      LOG: "WARNING: working tree dirty at phase start. Stashing under label."
      git stash push -u -m "implementing-code/{session_id}/{phase_id}/pre-phase"
      RECORD the stash ref in IMPL-STATE blockers as informational
        (so a human can recover the stash post-run if needed).
    OPTION B — repo is intentionally a worktree off main with prior wip commits:
      Confirm via `git log --oneline -5` that recent commits are wip(impl)/{session_id}.
      If yes, proceed without stash.

  IF this is NOT a git repository (`git rev-parse --is-inside-work-tree` fails):
    LOG: "WARNING: source_path is not a git repo. Recovery surface degraded."
    INITIALIZE: git init && git add -A && git commit -m "wip(impl): {session_id}/baseline"
    Continue. Without git, the integrity-break recovery in
    references/recovery-protocol.md will fall through to fail-fast.

LOG: "Pre-phase snapshot complete. Baseline committed at {short_sha}."
```

This step runs ONCE per phase. Skipping it means the Per-Phase Commit Cadence
below has nothing to commit against.

---

## Step 1: Load Phase Context

```
LOAD PLAN CONTEXT:
  IF PLAN-SPEC-*.md exists in {plan_folder_path}:
    READ only the Phase Load Contract slice for ACTIVE_PHASE:
      - header
      - required_artifacts rows where phases_using is "all" or ACTIVE_PHASE
      - canonical_values rows where phases_using is "all" or ACTIVE_PHASE
      - plan_status_semantics
      - implementation_strategy.phase_summary row for ACTIVE_PHASE if present
      - full ACTIVE_PHASE block
      - cross_phase rows involving ACTIVE_PHASE
      - acceptance_criteria rows mapped to ACTIVE_PHASE
      - HIGH open_questions and MEDIUM/LOW open_questions where `phase_ref` is "all" or includes ACTIVE_PHASE
    OPEN each matching required_artifacts path exactly once for this phase.
  ELSE (legacy plan):
    READ: {plan_folder_path}/00-plan-index*.md
    FIND: Phase document path for ACTIVE_PHASE
    READ: {plan_folder_path}/{phase_document_filename}

  EXTRACT (store in working memory):
    - Goal (1 sentence)
    - Prerequisites Checklist
    - Required Artifacts loaded
    - Canonical Values for this phase
    - User Stories table
    - Files to Create table
    - Files to Modify table
    - Implementation Notes (constraints, edge cases, code patterns)
    - Testing Strategy (commands, coverage targets)
    - Success Criteria
    - Escape Hatch protocol

LOAD RESEARCH CONTEXT (fallback only):
  IF a required executable value is missing from PLAN-SPEC AND research_folder_path is provided:
    READ the smallest relevant RESEARCH-SPEC slice needed to recover that value.
    RECORD IMPL-STATE deviation: "PLAN-SPEC self-containment gap; consulted research fallback."
  ELSE:
    DO NOT load RESEARCH-SPEC.

LOAD CODE CONTEXT:
  IF MODE == "STANDARD":
    READ: Files listed in "Files to Modify" (if they exist on disk)
  IF MODE == "REPAIR":
    READ: All files in IMPL_INDEX.files_touched for ACTIVE_PHASE
    READ: Existing test files for ACTIVE_PHASE
    PRIORITIZE: failure_feedback as primary instruction

LOG: "Context loaded. Files to create: {N}. Files to modify: {M}."
```

---

## Step 2: Execute — STANDARD Mode

```
GET file_list:
  files_to_create = Phase document "Files to Create"
  files_to_modify = Phase document "Files to Modify"
  total_files = files_to_create + files_to_modify

## Context-budget sub-batching (MANDATORY when total_files > 100)
IF count(total_files) > 100:
  SPLIT total_files into ordered sub-batches of <= 50 files each.
  Process ONE sub-batch, then at the sub-batch boundary run the Per-Phase
  Commit Cadence (commit + IMPL-STATE flush) and TREAT IT AS A CONTEXT RESET:
  do NOT carry the prior sub-batch's source files in context — rely on the
  Step 0 post-compaction recovery + _progress.json to resume. This bounds
  in-context source so a 100+ item phase does not trip mid-run compaction.
  (This is context segmentation, NOT Write-Flush-Forget on source files —
  source files are still authored normally; only the working set is bounded.)

FOR EACH file in total_files (within the current sub-batch):
  DO NOT STOP after first file. Process ALL files in the list.

  ## Pre-Generation Gate
  IF this is NOT the first file in the loop:
    VERIFY: IMPL_STATE_FILE was updated after the previous file (files_touched
    includes the previous file path with status COMPLETED).
    IF NOT → STOP. Update IMPL_STATE_FILE with previous file's status NOW.
    Reason: Without this update, an interruption loses all progress since the
    last IMPL-STATE write. This gate is non-negotiable.

  ## Pre-Generation
  UPDATE IMPL_INDEX:
    current_file = {file_path}
    current_file_status = "IN_PROGRESS"
  UPDATE IMPL_STATE_FILE (current_work + files_touched sections)

  ## Architecture Flaw Detection (RPI HALT Protocol)
  BEFORE generating, check:
  - Does the plan's specified approach conflict with actual codebase structure?
  - Are plan prerequisites unmet due to architectural constraints not found during research?
  - Does the phase require a design pattern or integration approach that is fundamentally incompatible?

  IF architecture_flaw_detected:
    LOG: "ARCHITECTURE_FLAW: {description of the incompatibility}"
    UPDATE IMPL_INDEX:
      current_file_status = "ARCHITECTURE_FLAW"
      blockers += { phase: ACTIVE_PHASE, description: "Architecture flaw: {details}", timestamp: now, resolution: "REQUIRES_PLAN_REVISION" }
    UPDATE IMPL_STATE_FILE (current_work + files_touched sections)
    STATUS = "ARCHITECTURE_FLAW"
    ## HALT — Do NOT attempt to work around architectural flaws.
    ## The plan must be revised by the human and the planning phase re-executed.
    GOTO Phase D with STATUS = "ARCHITECTURE_FLAW"

  ## API Contract Compliance Check (BEFORE generating)
  When the plan specifies API endpoint paths, URL patterns, or route mappings:
  - Use EXACTLY the paths specified in the plan document
  - If a deviation is necessary (e.g., framework convention conflict), document it
    in the IMPL_STATE_FILE with explicit justification BEFORE proceeding
  - Undocumented deviations from plan-specified API paths are BLOCKING issues in code review
  - Check: controller annotations, route definitions, and OpenAPI specs match plan

  ## Source Fidelity Check (BEFORE generating)
  - Verify this file is in the plan's file list
  - Verify any types/interfaces it imports from other files exist
    (or are being created in this same phase)
  - If file has dependencies not yet created → note but proceed

  ## Generate
  IF file in files_to_create:
    CREATE file at specified path
    IMPLEMENT per phase document specifications
    FOLLOW code patterns from Implementation Notes
    USE CORRECT COMMENT SYNTAX for the file type:
      .java → // comment
      .ts/.tsx/.js → // comment
      .py → # comment
      .sql → -- comment
      .yml/.yaml → # comment
      .xml/.html → <!-- comment -->
      Dockerfile → # comment
      .tf → # comment
      .sh → # comment
      .md → <!-- comment --> or plain text

  IF file in files_to_modify:
    READ existing file from disk
    APPLY changes as specified in phase document
    PRESERVE existing functionality not being changed

  ## Large-File Edit Discipline (>300 lines)
  ##
  ## A Write that emits the full content of a large file is the #1 cause of
  ## destructive edit collisions in this skill. The file may end up truncated,
  ## reordered, or replaced by a templated stub. Once that happens recovery
  ## costs scale with file size — re-reading a 1,915-line file 6 times to
  ## reconstruct it consumes ~30K-50K tokens.
  ##
  ## FOR EACH file in files_to_modify with line count > 300:
  ##   PREFER `Edit` tool with anchored old_string / new_string. The anchor
  ##   makes the edit surgical and verifiable from a small diff.
  ##   FORBIDDEN: emitting the whole file via Write to "rewrite" it. If you
  ##   feel you must rewrite the whole file, the planning artifact is wrong —
  ##   raise it as an architecture flaw, do not improvise.
  ##   FORBIDDEN: chained `replace_all` calls on a large file. Prefer multiple
  ##   anchored Edits with explicit context lines.
  ##
  ## FOR EACH file with line count > 1000:
  ##   Serialize edits — one Edit call per logical change, with an
  ##   IMPL-STATE files_touched append between calls. This caps the blast
  ##   radius of any single tool failure to one logical change.

  ## Write File — MANDATORY TOOL CALL
  WRITE file to disk using the file-write (or anchored Edit) tool.
  This is a tool call, not a deferred intention.

  ## Integrity Self-Check (immediate, single bash call — not a re-read)
  ##
  ## After every write to a file with line count > 300, confirm the on-disk
  ## state with a CHEAP signal — not a full re-read.
  ##
  ##   wc -l {file_path}
  ##   git -C {source_path} diff --stat -- {file_path}
  ##
  ## EXPECT: line count is within +/- the change you intended; diff --stat
  ## reports a non-empty change confined to the expected file.
  ##
  ## IF wc -l reports zero or near-zero lines after a non-deletion edit,
  ## OR diff --stat reports the file as fully replaced (e.g. "+1900 -1900"
  ## when you intended a 5-line tweak):
  ##   → INTEGRITY BREAK. Read references/recovery-protocol.md NOW and follow
  ##     the protocol. Do NOT improvise. Do NOT search caches. Do NOT re-read
  ##     the file 5 times to figure out what you broke.
  ##
  ## A full file re-read to "verify the edit" is FORBIDDEN for files > 300
  ## lines. Trust the Edit tool's success indicator and the cheap signals
  ## above. Only re-read in full if the build/test signal in Phase C
  ## disagrees with what the diff says.

  ## Test-Driven Agentic Development (TDAD) Protocol
  ##
  ## When tdad_mode is enabled, follow a structured test–implement–refine cycle per file unit.
  ## Default: enabled for TASK scope, disabled for FULL_SDLC scope.
  ## When disabled, fall back to an ad-hoc "test WITH implementation" flow (tests may be written
  ## or updated after generate).

  IF tdad_mode == true:
    ## TEST (RED): Write or update tests to expose current gaps
    Derive test file path from source file path
    ## FTC-anchored RED (when the plan row's `test_case_id` cites an FTC id AND
    ## test_cases_path is provided):
    ##   - LOAD only the one suite file for that FTC's epic
    ##     ({test_cases_path}/suites/epic-NN-func-tests.md), read the cited FTC's
    ##     Gherkin (Given/When/Then), then FLUSH the suite file (Write-Flush-Forget —
    ##     same "one at a time" discipline as design images; never preload all suites).
    ##   - The test's assertions MUST reflect that FTC's Then clauses. Do NOT invent
    ##     assertions that contradict the FTC; do NOT reclassify the level — honor the
    ##     plan row's `type` (unit/integration). Rows marked `type: e2e` /
    ##     `covered_by: qe-web-automation` are NOT implemented here (automation owns them).
    ##   - Rows with `test_case_id: [derived]` (no FTC) behave exactly as legacy.
    WRITE or UPDATE test file targeting the already-generated implementation
    Include: assertions from the cited FTC's Gherkin (when FTC-anchored), plus
    happy path tests, edge cases from Implementation Notes, failure modes from research
    WRITE test file to disk — MANDATORY TOOL CALL
    RUN test command (from phase document Testing Strategy) — expect FAILURE (tests must fail
    against the current implementation to confirm they cover real gaps)
    LOG: "TDAD RED: Test written, verified failing for {file_path}"

    ## GREEN: Fix implementation until tests pass
    ## (The "Generate" step above already created the implementation file)
    RUN test command — expect PASS
    IF test fails:
      APPLY localized fix (OODA loop: observe error, orient to plan, decide fix, act)
      Maximum 3 self-correction attempts
      RUN test command after each fix
    LOG: "TDAD GREEN: Tests passing for {file_path}"

    ## REFACTOR: Optimize while tests stay green (optional)
    IF obvious code quality improvements exist AND tests are passing:
      APPLY refactoring (rename, extract method, simplify conditionals)
      RUN test command — MUST still pass
      IF test fails after refactor: REVERT refactoring
    LOG: "TDAD REFACTOR: Complete for {file_path}"

  ELSE:
    ## Standard mode: Write test WITH implementation
    Derive test file path from source file path
    Include: Happy path tests
    Include: Edge cases from Implementation Notes
    Include: Failure modes from research
    WRITE test file to disk — MANDATORY TOOL CALL

  ## Post-File Protocol (Write-Flush-Forget)
  1. UPDATE IMPL_INDEX in memory:
       current_file_status = "COMPLETED"
       files_touched += { phase, path, action: CREATE|MODIFY, status: COMPLETED, test_file }
  2. APPEND to IMPL_STATE_FILE — MANDATORY TOOL CALL. Use EOL append, NOT full rewrite:
       Option A (Bash tool available):
         cat >> {IMPL_STATE_FILE} << 'EOL'
         | {phase} | {file_path} | {create|modify} | completed | {test_file|N/A} |
         EOL
       Option B (Edit tool only):
         Append one row to the end of the files_touched table section.
         Do NOT read the full file. Do NOT rewrite it. Insert the row only.
     The file must be immediately readable on disk after this call.
     Reading the whole IMPL-STATE to update it is PROHIBITED here — append only.
  3. FLUSH generated file content from memory — DO NOT retain
  4. VERIFY file exists on disk (ls or stat)
  5. LOG: "Appended to IMPL-STATE: {file_path} | completed"

  ## BLOCKING GATE — IMPL-STATE Update Verification
  Before proceeding to the NEXT file:
    CHECK: Was IMPL_STATE_FILE actually written to disk in step 2 above?
    IF IMPL_STATE_FILE was NOT updated (no tool call made):
      STOP. Write IMPL_STATE_FILE NOW. This is not optional.
      The next file MUST NOT be generated until IMPL-STATE reflects the current state.
    This gate prevents the agent from batching multiple files without progress tracking.
    Skipping IMPL-STATE updates means interrupted runs cannot resume — all progress is lost.

  IF file write failed:
    UPDATE IMPL_INDEX: current_file_status = "FAILED"
    UPDATE IMPL_STATE_FILE — even failures must be recorded
    Log error and continue to next file if partial_execution is true
    Otherwise GOTO Escape Hatch

## Per-Phase Commit Cadence (MANDATORY at phase boundary)

After the FOR EACH file loop completes for this phase, before exiting Phase B:

  cd {source_path}
  git add -A
  git commit -m "wip(impl): {session_id}/{phase_id} — {N} files, {M} tests" \
    --author="implementing-code <implementing-code@aipods.local>" \
    -- 2>/dev/null || LOG: "Nothing to commit (phase made no source changes)."

  RECORD the resulting commit SHA in IMPL-STATE under
    phases[ACTIVE_PHASE].wip_commit_sha = <short_sha>

  This commit is the integrity-break recovery baseline for the NEXT phase.
  Without it, references/recovery-protocol.md can only restore state to the
  pre-session baseline — losing all completed phases since.

  IF git commit fails for a reason other than "nothing to commit"
  (e.g., pre-commit hook rejection, SSH signing failure, repo in detached
  HEAD that the orchestrator placed it in deliberately):
    LOG: "WARNING: per-phase commit failed: {error}"
    DO NOT --no-verify the hook. DO NOT force the commit. DO NOT amend.
    Record the failure in IMPL_INDEX.deviations and proceed — the next phase
    will run without this checkpoint. This degrades recovery but does not
    block progress.

LOG: "All files generated for Phase {ACTIVE_PHASE}. Total: {N} files, {M} tests."
LOG: "Phase wip-commit recorded at {short_sha}."
```

---

## Step 3: Execute — REPAIR Mode

```
REPAIR operates surgically. It does NOT regenerate everything.

## Pattern-Based Fix Protocol
## When feedback identifies a pattern-based issue (same problem in multiple
## files), do NOT fix files one at a time as you encounter them.
##
## PROTOCOL:
##   1. FIRST: grep/search for ALL files exhibiting the problematic pattern
##   2. LIST all matches with file paths and line numbers
##   3. FIX ALL matches in a single pass (do not stop after the first file)
##   4. VERIFY: grep again — zero problematic matches must remain
##   5. Only then proceed to the next directive
##
## This prevents the "whack-a-mole" failure mode where fixing one file
## causes the review to discover the same issue in a sibling file,
## triggering another REPAIR cycle.

LOAD REPAIR_DIRECTIVES from IMPL_INDEX (parsed in Phase A)

## Determine scope
IF REPAIR_DIRECTIVES contains category "GLOBAL":
  SCOPE = all files in ACTIVE_PHASE
ELSE:
  SCOPE = only files matching directive targets

FOR EACH directive in REPAIR_DIRECTIVES:
  FOR EACH target_file matching this directive:

    ## Load current file
    READ target_file from disk (it MUST exist for REPAIR)
    IF NOT exists:
      This is a MISSING_FILE directive → treat as CREATE (not modify)

    ## Apply surgical fix
    ANALYZE directive.instruction:
      - COMPILATION_ERROR → Fix the specific syntax/type/import error
      - MISSING_FILE → Create the missing file
      - CONFIG_ERROR → Fix configuration (versions, references, paths)
      - SYNTAX_ERROR → Fix comment syntax, encoding, format issues
      - RUNTIME_ERROR → Fix logic or wiring issues
      - LOGIC_ERROR → Fix business logic per feedback

    CONSTRAINT: Modify ONLY what the directive requires.
    CONSTRAINT: Do NOT rewrite entire files unless necessary.
    CONSTRAINT: If feedback contradicts plan, feedback wins. Document deviation.

    ## Write fixed file — MANDATORY TOOL CALL
    WRITE file to disk

    ## Log repair action
    UPDATE IMPL_INDEX.repair_log (current iteration):
      files_modified += {
        path: target_file,
        change_summary: "1-line description of what changed"
      }

    ## Flush and verify
    FLUSH file content from memory
    VERIFY file exists on disk
    LOG: "REPAIR: Fixed {target_file} — {change_summary}"

## After all directives processed
UPDATE IMPL_STATE_FILE (current_work + files_touched sections) with updated repair_log

LOG: "REPAIR complete. Iteration {N}. Files modified: {count}."

## Post-REPAIR Regression Guard (MANDATORY)
## Prevents the common failure mode where a fix addresses one symptom
## but introduces new breakage or misses sibling occurrences.

AFTER applying all directive fixes but BEFORE proceeding to Phase C:

1. RUN FULL TEST SUITE
   Execute the test command from the phase document's Testing Strategy
   ALL tests must pass — not just tests related to the fixed files
   IF any test fails:
     ANALYZE: Is this a regression from the fix or a pre-existing failure?
     IF regression: Apply localized correction (max 2 attempts)
     IF pre-existing: Document in IMPL_INDEX.blockers, continue

2. COPY-PASTE ARTIFACT CHECK
   FOR EACH modified file in this REPAIR iteration:
     SCAN for: duplicate code blocks, repeated import statements,
     orphaned TODO/FIXME from the fix process, wrong entity names
     copied from adjacent code
     IF artifacts found: Clean them before proceeding

3. FIX-TO-FINDING VERIFICATION
   FOR EACH directive in REPAIR_DIRECTIVES:
     VERIFY: The applied fix directly addresses the specific issue described
     IF the fix is tangential or incomplete: re-apply with correct understanding

4. PATTERN SWEEP (cross-file)
   IF any directive mentions a pattern that may exist in multiple files:
     GREP for ALL instances of the pattern across the source tree
     Fix ALL remaining instances in a single pass
     Verify zero problematic matches remain

## MANDATORY: Proceed to Phase C after REPAIR
## Do NOT stop here. REPAIR fixes the code, but Phase C must still run to:
##   - Verify scaffolding completeness (Step 1)
##   - Run compilation/tests (Step 5)
##   - Update README.md if build commands changed (Step 3)
##   - Generate AGENTS.md if this is the final phase (Step 4 — RULE 9)
## GOTO: Phase C (read references/phase-c-verify.md)
```

---

## Source Fidelity Check (Per File, Before Writing)

Before writing ANY file to disk, verify:

1. **No hallucinated imports** — Every import/require references a file that exists
   OR is being created in this same phase
2. **Correct ID references** — Any upstream IDs (FR-XX, US-XX, ADR-NNN) match
   the plan document exactly
3. **Correct comment syntax** — File uses the right comment style for its type
4. **No template placeholders** — No {session_id}, {project_name} remain in
   generated code (they should be resolved to actual values)
5. **Technology consistency** — Versions, framework APIs match research/ADR decisions

If violations found → correct before writing. Log correction.

---

## Post-Phase Protocol

1. **Flush** phase document content from memory.
2. **Retain** only IMPL_INDEX.
3. **MANDATORY: Proceed to Phase C (Verify Build) NOW.**
   DO NOT skip Phase C. DO NOT go directly to writing output parameters.
   DO NOT mark the phase as COMPLETED before running Phase C.
   READ `references/phase-c-verify.md` and execute it BEFORE any finalization.
