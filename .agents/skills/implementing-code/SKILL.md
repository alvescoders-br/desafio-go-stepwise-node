---
name: implementing-code
description: >
  Execution phase orchestration — converts approved compact PLAN-SPEC artifacts
  into tested, verified, buildable code. Reads agent-native PLAN-SPEC as the
  implementation contract, with optional RESEARCH-SPEC fallback only when the
  plan has a documented self-containment gap. Produces source code, tests, README.md,
  AGENTS.md, and a single IMPL-STATE tracking file. All execution mechanics
  preserved: TDAD, scaffolding gates, self-correction loops, Phase B→C→D
  cycling, 26 implementation consistency rules.
license: Proprietary
metadata:
  author: aipods-team
  version: 4.0.0
  category: engineering
  tags: code-implementation, tdd, state-management, fic-methodology, build-verification, agent-native, repair-checklist, path-portability
  compatibility: Requires git, bash
---

# Implementing Code — Agent-Native Execution Skill

## SKILL PROTOCOL — ENTRY RULES (read first, do not skip)

1. **The protocol below is internally consistent.** If you perceive a conflict
   between the capability prompt and this skill, the skill wins for execution
   mechanics; the capability wins for paths/parameters. Do NOT exit citing
   "ambiguity" or "internal contradiction" — every section here has been
   tested in production runs.

2. **Begin Phase A immediately.** Do NOT re-evaluate the protocol's completeness
   before starting. Phase A's first action (write `_progress.json` to the
   progress folder) IS the verification. If a required input is genuinely
   missing, you will discover it during Phase A and call `exec-fail` — not
   before.

3. **Reference files are loaded on demand via `cat`** when each phase begins.
   They are NOT preloaded into your context. The list at the bottom of this
   file is a pointer table, not a checklist of files you must already have.
   In particular: do NOT read `phase-c-checklist.md`, `phase-c-tools.md`,
   `consistency-rules.md`, `repair-mode.md`, or `recovery-protocol.md` at
   session start. Each has a defined trigger in the table below — read it
   only when that trigger fires. Pre-loading these inflates steady-state
   context by ~1,800 lines per phase and contributes to compaction failures.

4. **Asking the human a clarifying question = task FAILURE.** The capability
   prompt makes this explicit. There is no human watching. Either execute, or
   call `stepwise session exec-fail --message "<reason>"`. Never end with
   "If you want, I will continue…" — that is a refusal.

   **Artifact Fidelity Rule — mandatory across all implementation work.** Treat
   explicit upstream artifact details as binding implementation constraints
   unless a higher-priority source explicitly supersedes them. This applies to
   code, SQL, configuration, schemas, infrastructure definitions, contracts,
   structured data, and other implementation artifacts. Do not silently rename,
   simplify, normalize, reorder, or substitute explicit identifiers, literals,
   predicates, mappings, configuration keys, dependency declarations, or
   contract shapes during execution.

5. **No final response until artifacts exist on disk.** The Session
   Termination Contract (below) lists the files that must exist before you
   can emit a closing summary. Any final response without those files is a
   protocol violation and will be flagged as a fabricated run.

6. **Write-Flush-Forget — non-negotiable (IMPL-STATE only).** After writing
   the IMPL-STATE skeleton (Phase A), NEVER re-read the IMPL-STATE file in
   full. Updating a per-file or per-phase entry is exactly four operations:
   (a) read `_progress.json` (small), (b) load the just-emitted source file
   (or its build output), (c) one targeted `Edit` replacing the entry's
   `WFF-SECTION:{name}:pending` anchor with the completion entry,
   (d) update `_progress.json`.

   **Scope of this rule:** the Write-Flush-Forget discipline applies to the
   **IMPL-STATE artifact only** (`IMPL-STATE-{session_id}.md` and its
   `_progress.json`). It does NOT apply to source files — source files are
   authored normally with `Write`/`Edit`, are not re-read during the Phase B
   loop unless an explicit fix requires it, and do not need WFF anchors.

   **Why:** repeated `view` of the IMPL-STATE file inflates prompt tokens
   geometrically with iteration count and breaks prompt-cache continuity.
   Calibration evidence (Edenred sprint-3) showed 5M+ prompt tokens per
   failed run attributable to this pattern.

   **Forbidden tool patterns inside the per-file / per-phase loop:**
   - `view IMPL_STATE_PATH` (any kind) AFTER the skeleton is written. Read `_progress.json` instead.
   - `replace_all=true` on IMPL-STATE. Use targeted anchored Edits.
   - `bash wc -l IMPL_STATE_PATH` to "verify" progress. Placeholder anchor presence is the verification.

   **Permitted exceptions (must be explicitly justified in agent reasoning):**
   - At the very end of the run, ONE final grep to verify all placeholders are
     replaced (`! grep "WFF-SECTION:.*:pending" IMPL_STATE_PATH`).
   - On REPAIR: ONE initial bounded read (offset/limit, max 80 lines) around
     the affected section to confirm placeholder state.

---

## Quick Start
Convert approved implementation plans into working, buildable, tested code.
Primary output is **source code** — not documents. The IMPL-STATE file is
operational metadata for orchestration, not the deliverable.

This skill reads PLAN-SPEC as the normal execution contract and produces code
through a strict Phase A→B→C→D loop with mandatory verification at every phase
boundary. RESEARCH-SPEC is optional fallback/forensics context, not part of the
default Phase B load.

## Known Failure Modes
<!-- ACCUMULATING — appended by calibrating-updates (WS6). Newest first. Rules MUST be generic/behavioral (project-agnostic); project-specific fixes go to context packs, never here. Format + entry rules: engineering-skills/references/known-failure-modes-format.md. Read these at pre-flight so a lesson learned once recurs no more. -->

- **KFM-001** (2026-07-21, source: REC-002, CAL-INF-001)
  - Symptom: Implementation output passes the agent's own internal quality check but fails the downstream automated review gate (e.g., review-graph, review-mcp-tools, review-ux-components), triggering a 2-3 iteration implement→review→implement loop before eventual PASS.
  - Root cause: The implementing-code skill has no mandatory pre-completion self-review pass that simulates the downstream reviewer's criteria. After review rejection with failure_feedback, the agent successfully reworks the artifacts — proving the criteria are knowable and applicable pre-commit. The gap is timing: criteria are only applied reactively (post-rejection) rather than proactively (pre-commit).
  - Rule: Before finalizing any implementation output, perform a self-review pass against the downstream reviewer's acceptance criteria. For each major deliverable check: (1) all required interfaces are implemented (not stubbed), (2) integration points match the specification, (3) no placeholder code (TODO, pass, raise NotImplementedError) in required paths, (4) tests exist and pass for core functionality, (5) naming conventions match the spec. Only submit if all criteria pass. If any item fails, repair before submitting.

## Anti-Patterns (do NOT)
<!-- ACCUMULATING — appended by calibrating-updates (WS6). One line each: **AP-NNN** (ISO-date, source: REC-NNN): prohibition — why. -->

- **AP-001** (2026-07-21, source: REC-002, CAL-INF-001): Do NOT submit implementation output without first running a self-review pass against the downstream reviewer's acceptance criteria — skipping it creates a predictable implement→review(FAIL)→implement loop that wastes 400-500M tokens per full playlist run.

## Output Architecture

```
Tracking:
  {progress_folder_path}/IMPL-STATE-{session_id}.md   ← Single consolidated state file

Code (UNCHANGED from v2.x):
  {source_path}/...                               ← Source code + tests
  {source_path}/README.md                         ← Build instructions
  {source_path}/AGENTS.md                         ← Agentic metadata (final phase only)

Memory Bank (UNCHANGED from v2.x):
  context-pack/active-context.md                  ← Cross-session state
  context-pack/progress.md                        ← Cumulative milestone ledger
```

**Why single tracking file:** IMPL-STATE consolidates the former progress + audit
files. Tracking data is compact — even 7-phase / 100-file projects produce ~600 lines.
The orchestrator reads one file for status, blockers, and repair context.

**Phase retrospectives:** No longer written to plan files. Data captured in IMPL-STATE
`execution_log` and `validations` sections. Rendering profile generates human-readable
retrospectives on demand.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project_name` | string | Yes | — | Project identifier |
| `source_path` | string | Yes | — | Root directory for source code. This IS the code location — files are written directly here, no subfolder is created. |
| `plan_folder_path` | string | Yes | — | Path to plan folder (PLAN-SPEC or legacy phase docs) |
| `research_folder_path` | string | No | — | Optional fallback path to research folder. Do not load by default; use only when PLAN-SPEC fails self-containment and log a deviation. |
| `progress_folder_path` | string | No | `{plan_folder_path}/../progress` | Directory for IMPL-STATE file |
| `failure_feedback` | string | No | — | Feedback for REPAIR mode (from failed validation or rejection) |
| `partial_execution` | boolean | No | false | Allow partial phase completion |
| `custom_instructions` | string | No | — | Optional user overrides |
| `execution_scope` | string | No | `"all"` | `"all"` or `"single"` — process all PENDING phases or just one |
| `tdad_mode` | boolean | No | auto | Enable TDAD (Red-Green-Refactor). Default: true for TASK scope, false for FULL_SDLC |
| `design_specs_path` | string | No | — | Optional. UI/UX specs (markdown / text). When provided AND the current phase touches UI files (per PLAN-SPEC's `design_ref` annotations on `file_specifications`), Step 2 loads the relevant screen/component entries before Phase B generates each file. Skipped when no UI files in scope. |
| `design_images_path` | string | No | — | Optional. Directory of design image files. When provided AND the current file's `design_ref` resolves to an image filename in this directory, the implementer opens that image for visual reference during Phase B (one image at a time, flushed after the file is written — do NOT preload). |
| `parallel_scopes` | array | No | — | OPT-IN fan-out, default OFF. A list of independent, **provably disjoint** work scopes to implement concurrently — each entry `{ id, plan_folder_path, source_path, progress_folder_path? }` with its OWN plan and its OWN non-overlapping `source_path` subtree. Absent/empty ⇒ normal single-scope sequential execution (unchanged — zero impact on every existing caller). When present, Step 0 runs the fan-out coordinator: gate disjointness, spawn one isolated sub-agent per scope, then consolidate shared roots once. This NEVER parallelizes files within a single plan (they are interdependent) — only whole disjoint scopes. See `references/parallel-execution.md`. |
| `test_cases_path` | string | No | — | Optional. Folder holding upstream functional test cases (FTCs) from `quality-engineering-design` — a `FTC-MANIFEST-*.md` + `suites/epic-NN-func-tests.md`. Same load discipline as `design_specs_path`: NOT preloaded. The PLAN-SPEC's `testing_strategy.test_case_id` column already tells this skill which FTC each planned test row satisfies; when a phase's RED step cites an FTC id, Step 3 loads that one suite file, uses its Gherkin (Given/When/Then) as the RED assertion source, then flushes it. When empty/absent, TDAD RED derives assertions from the plan + research exactly as before (fully backward-compatible). The planner already fixed the level (unit/integration/e2e); this skill does NOT reclassify — it honors the plan's `type`. |

**If any Required parameter is not defined, ABORT EXECUTION.**

**Path fidelity (with scope re-anchoring):** When `progress_folder_path` is
provided, use it verbatim for `_progress.json` and every `IMPL-STATE-*` write —
EXCEPT for the one out-of-scope case below. Never derive it from `project_name`
or `output_folder`.

  **Scope re-anchor (feature_id-unset case — MANDATORY):** The implementation
  artifact folder MUST be a sibling of `plan_folder_path` (share its parent
  directory). If the provided `progress_folder_path` does NOT share
  `plan_folder_path`'s parent — e.g. it resolves flat directly under the
  capability output folder (`{output_folder}/implementation`) while
  `plan_folder_path` is nested under a scope subfolder
  (`{output_folder}/{SCOPE}/code-task-planning`) — then `feature_id` was unset
  and upstream research/planning self-derived `{SCOPE}`. RE-ANCHOR to follow it:

      EFFECTIVE_PROGRESS_PATH = dirname(plan_folder_path) + '/' + basename(progress_folder_path)

  Write `_progress.json` and IMPL-STATE there (create if absent), and report
  `EFFECTIVE_PROGRESS_PATH` as `impl_output_path` in the §11 sidecar (per the
  PATH-EMIT CONTRACT). Log a deviation: `"re-anchored progress folder to plan
  scope {dirname(plan_folder_path)} — provided path was out of scope (feature_id
  unset)."` This makes implementation symmetric with planning (which already
  writes as a sibling of the scoped research folder), so artifacts never split
  across a feature subfolder and a flat folder — the failure that put IMPL-STATE
  under `{output_folder}/implementation` instead of `{output_folder}/{SCOPE}/…`.
  Only ABORT with `EXEC_FAIL_IMPL_PROGRESS_PATH` when `plan_folder_path` is ALSO
  flat (no scope to recover from) yet the paths still disagree.

**Design inputs are optional, even for UI-heavy projects.** First use PLAN-SPEC's
`required_artifacts`, phase `design_ref` annotations, and inline UI constraints.
If `design_specs_path` / `design_images_path` are not provided and the plan does
not name a required design artifact for a UI-bearing file, log a deviation in
IMPL-STATE.deviations: `"UI implemented from PLAN-SPEC prose only — no design assets supplied"`.
Do not load RESEARCH-SPEC to recover design context unless the plan is missing a
required executable detail and `research_folder_path` is provided as fallback.

## Prerequisites

Before execution:
- [ ] Valid plan folder exists at `plan_folder_path` (contains PLAN-SPEC-*.md or 00-plan-index.md)
- [ ] If `research_folder_path` is provided, it exists (fallback only)
- [ ] `source_path` is defined and the directory exists (or can be created)
- [ ] `progress_folder_path` is the feature-scoped implementation artifact folder
      when `plan_folder_path` is feature-scoped; never a project/root fallback folder
- [ ] Plan status is executable: `PROCEED`, `CONDITIONAL`, `VERIFY_ONLY`, or
      `PARTIAL_APPLIED` (check PLAN-SPEC header or `00-plan-index.md`);
      `BLOCKED` aborts before Phase B
- [ ] Target repository/directory accessible at `{source_path}`
- [ ] Development environment configured (per PLAN-SPEC tech stack)

## Implementation Consistency Rules

The 26 rules that govern every file write, test, and IMPL-STATE update live in
**`references/consistency-rules.md`**. Read that file at the end of Phase A
(after writing `_progress.json` and the IMPL-STATE skeleton) and keep its rules
in scope for the entire session. The same file also contains:

In addition, preserve artifact fidelity across all writes: when the plan or a
PLAN-SPEC `required_artifacts` file specifies exact artifact behavior or
structure, implement that exact behavior or structure unless a documented
conflict forces escalation. If the implementation cannot preserve an explicit
upstream detail, record the blocker or deviation with source tags — never
replace it with a quieter approximation.

- Test Suite Integrity Rule (no xdescribe/xit/fdescribe/fit)
- Test Impact Checklist (after modifying any service/pipe/component)
- Prove-It Pattern (Bug Fix Protocol)
- Common Rationalizations table
- Red Flags

Do NOT skip reading it — code review will reject violations of any of the 26 rules.

## Carry-Forward Index: IMPL_INDEX

The carry-forward contract between phases. Updated after each file write,
persisted to `{progress_folder_path}/IMPL-STATE-{session_id}.md`.

Key fields:

| Field | Description |
|-------|-------------|
| `session_id` | Typed session ID for this implementation run |
| `project_name` | Project identifier |
| `source_path` | Root directory for source code |
| `project_root` | Same as source_path — all code lives here |
| `mode` | `"STANDARD"` or `"REPAIR"` |
| `input_format` | `"AGENT_NATIVE"` or `"LEGACY"` — detected plan/research format |
| `active_phase` | Currently executing phase |
| `output_contract` | Pinned at Phase A — survives compaction (RULE 21) |
| `phases` | `[{ id, status, started_at, completed_at, files_count, tests_count }]` |
| `files_touched` | `[{ phase, path, action, status, test_file, test_case_ref }]` — `test_case_ref` = upstream FTC id(s) the test satisfies, when `test_cases_path` supplied |
| `repair_log` | `[{ iteration, phase, feedback, files_modified }]` |
| `blockers` | `[{ phase, description, timestamp, resolution }]` |
| `deviations` | `[{ phase, description, reason, impact }]` |
| `build_commands_discovered` | Populated during Phase C |
| `tech_stack_detected` | Populated during Phase C |
| `tool_results` | Build/test/lint verification results |
| `execution_log` | Per-phase execution entries (replaces audit) |
| `metrics` | Files written, tests passed, coverage |
| `validations` | Structured validation results |
| `open_questions` | Consolidated gaps/blockers |

See execution-protocol.md for the full IMPL_INDEX schema.

## Phase Loop Continuation Mandate

```
CRITICAL — READ THIS BEFORE EXECUTING:

By default, execute ALL PENDING phases sequentially within a single session.
After completing each phase's cycle (B→C→D), loop back to Phase B for the
next PENDING phase.

Do NOT stop after completing one phase.
Do NOT wait for human confirmation between phases.
Do NOT skip Phase C (Verify) or Phase D (Finalize) — they are MANDATORY.

Process ALL PENDING phases: Phase A → [Phase B → C → D] → [Phase B → C → D] → ...

Stop ONLY when:
  - All phases are COMPLETED
  - A phase is BLOCKED (unresolvable blocker)
  - execution_scope == "single" (explicit parameter override)

The per-phase cycle is ALWAYS: B (generate) → C (verify + README) → D (finalize).
Skipping C or D is a VIOLATION of the skill protocol.
```

## Session Termination Contract

```
BEFORE you emit any final response, completion message, or session summary,
verify ALL of the following exist on disk. If ANY is missing, you are NOT
done — execute the missing step.

TERMINATION CHECKLIST — run these exact commands before finishing:

  ls -la {source_path}/README.md {source_path}/AGENTS.md \
         {progress_folder_path}/IMPL-STATE-*.md \
         "$output_file" 2>&1

  Where $output_file is the JSON path declared in the run-metadata block of the
  capability prompt (e.g., /tmp/_stepwise_outputs_<run_id>.json). It is the
  contract between this skill and the orchestrator.

  If ANY file reports "No such file":
    - README.md missing      → EXECUTE Phase C Step 4 NOW
    - AGENTS.md missing      → EXECUTE Phase C Step 5 NOW (final phase)
    - IMPL-STATE missing     → WRITE IT NOW (see Phase D)
    - $output_file missing   → WRITE IT NOW (see step 6 below)

  DO NOT emit a final response until all files are confirmed on disk.

  Full checklist:
  1. IMPL-STATE file exists at {progress_folder_path}/IMPL-STATE-{session_id}.md
     → MANDATORY output. The orchestrator uses IMPL-STATE to track
       session progress across features. Missing IMPL-STATE = invisible session.
       EXIT-BLOCKING (consistency-rules.md RULE 4): also verify the file's
       last write timestamp falls inside the current run window. A stale
       IMPL-STATE from a prior run does NOT satisfy this check.
  2. README.md exists at {source_path}/README.md
     → MANDATORY deliverable. Generate from discovered tech stack.
  3. AGENTS.md exists at {source_path}/AGENTS.md (final phase only)
     → MANDATORY deliverable on final phase (Rule 9).
  4. Phase D has been executed (IMPL-STATE contains execution_log entries)
     → If no execution_log: READ references/phase-d-finalize.md and execute NOW
  5. Memory Bank files updated (context-pack/active-context.md and progress.md)
     → If missing: EXECUTE Phase D Step 7 NOW
  6. Stepwise output JSON exists at $output_file (the run-metadata path) and
     contains every key listed in the capability's "Output parameters" table
     with non-empty values.
     → MANDATORY contract output. The orchestrator parses this file to route
       to the next step. Missing output JSON = downstream step starts with
       null parameters and fails. EXIT-BLOCKING: never emit a success summary
       with the JSON missing.

     **PATH-EMIT CONTRACT (feature-scope fidelity — EXIT-BLOCKING):**
     Report output paths using the parameter values you RECEIVED, verbatim.
     Do NOT re-derive, re-compose, or re-prepend `{output_folder}`,
     `{project_name}`, or `{feature_id}` onto them — the caller already
     resolved feature scope into these values, and re-prefixing corrupts the
     path into an unscoped or doubly-nested folder (the root cause of impl/
     review artifacts escaping the feature subfolder).
       - `impl_output_path`: the `progress_folder_path` parameter EXACTLY as
         received in the `## Parameters` table — the folder that holds
         `IMPL-STATE-*.md` and `_progress.json`. This is the same value you
         used for every IMPL-STATE write (Path fidelity rule above); the emit
         MUST match it byte-for-byte. If it does not, you wrote artifacts to a
         different folder than you are reporting — abort with
         `EXEC_FAIL_IMPL_PROGRESS_PATH`.
       - `source_path`: the `source_path` parameter EXACTLY as received.
     Mirrors reviewing-code's §11 path-emit contract; keep them identical.
  7. files_touched coverage check (consistency-rules.md RULE 19):
     For each path in `git -C {source_path} diff --name-only HEAD~N..HEAD`,
     verify there is a corresponding row in IMPL-STATE files_touched. If any
     path is missing, append it before exit.
  8. Integrity-break recovery (if applicable):
     If a file went through recovery via references/recovery-protocol.md
     during this run, IMPL-STATE.repair_log (or .deviations in non-REPAIR
     mode) MUST contain the integrity-break entry. Verify before exit.

If you are about to write a summary or respond and ANY item above is missing,
STOP. Execute the missing step. Then return here.

If after a good-faith attempt you cannot satisfy item 1, 6, 7, or 8 (e.g.,
the progress folder is read-only, or the output JSON path the runtime declared
does not exist), call `stepwise session exec-fail` with a structured reason —
do NOT emit a success summary. The orchestrator's post-run verification will
flag fabricated success and the run will be marked failed regardless.
```

## Execution Protocol

### Step 0: Fan-Out Coordinator Mode (opt-in — ONLY when `parallel_scopes` is set)

This step is a no-op for every normal invocation. It exists so a caller can
implement several **provably independent** scopes concurrently WITHOUT baking any
domain concept (agents, modules, services) into this skill — the caller decides the
partition; this skill only parallelizes disjoint subtrees and refuses anything else.

```
IF parallel_scopes is empty or absent:
  SKIP Step 0 entirely → proceed to Step 1 (normal single-scope sequential
  execution — byte-for-byte the prior behavior).

ELSE (fan-out requested) → READ references/parallel-execution.md NOW and follow it:

  1. SAFETY GATE — ALL must hold, else DO NOT fan out:
     - Every scope's source_path is pairwise DISJOINT — no source_path equals,
       contains, or is contained by another's (no shared files or directories).
     - No two scopes concurrently write a SHARED mutable root: a common package
       manifest / lockfile, a single git index, a shared config, or a root
       README/AGENTS.md. Shared/root files are the coordinator's job (step 4),
       never written inside a parallel scope.
     - Each scope has its own plan_folder_path AND its own progress_folder_path.
     IF the gate fails for ANY pair → ABORT fan-out and run the scopes SEQUENTIALLY
       (ordinary Step 1→5 per scope, one at a time), logging
       `FANOUT_DEGRADED_SEQUENTIAL` with the offending overlap. Correctness beats
       speed — this is what protects callers whose "independent" units actually
       share build state (e.g. agents in one graph sharing scaffold/deps).

  2. Write the coordinator _progress.json (skill=implementing-code, mode=fanout,
     total = number of scopes) — the heartbeat, before any other write.

  3. Spawn ONE isolated implementing-code sub-agent PER scope, each invoked with
     that scope's { plan_folder_path, source_path, progress_folder_path } plus the
     shared READ-ONLY inputs. Each sub-agent runs the ordinary sequential skill
     confined to its OWN subtree. Barrier: wait for all.

  4. COORDINATOR FINALIZATION (sequential, single-writer): after the barrier, write
     or merge any SHARED root artifacts EXACTLY ONCE — cross-scope root
     README/AGENTS.md, a single dependency install / lockfile, one git commit
     spanning the tree — so no two writers ever touch a shared file at the same
     time. Consolidate per-scope IMPL-STATE into one report + the §11 sidecar.

  5. A scope that BLOCKS/FAILS does NOT abort its siblings — record it and surface
     it in the consolidated report (partial-success semantics).
```

**Invariant:** fan-out is across disjoint SCOPES only, never files within one plan.

---

### Step 1: Initialize Session (Phase A)
**READ** `references/phase-a-initialize.md` **NOW**.

Detect mode (STANDARD vs REPAIR), resolve folders, initialize or load
IMPL_INDEX, determine target phase.

**FIRST ACTION — MANDATORY (heartbeat):** Write `_progress.json` to the progress
folder before any other file write. Mirror the pattern used by reviewing-code and
planning-code-tasks. This is the early signal the orchestrator monitors for ghost
detection — emit it within the first 60 seconds of execution.

```
WRITE progress_folder_path + '/_progress.json':
  { "skill": "implementing-code", "session_id": "<resolved>",
    "status": "RUNNING", "started_at": "<ISO timestamp>", "completed_at": null,
    "phase": "A", "total_phases": <N>, "completed_phases": 0 }
```

Initialize IMPL_INDEX with session metadata. Write IMPL-STATE skeleton.

**After IMPL-STATE skeleton is written:** READ `references/consistency-rules.md`
to load the 26 rules. If `failure_feedback` is non-empty, ALSO read
`references/repair-mode.md`.

Follow execution-protocol.md for Memory Bank (session start write) and dual-format detection.

**Execution:** automated

---

### Step 1.5: Pre-Applied Fix Short-Circuit

**READ the plan header BEFORE entering Phase B.** Check the `plan_status` field.

```
plan_status: VERIFY_ONLY     -> execute verify-only branch (below)
plan_status: PARTIAL_APPLIED -> verify file rows with `pre_applied` evidence;
                                skip verified rows and execute Phase B only for
                                rows where `pre_applied` is `none`
plan_status: PROCEED         -> execute Phase B for all files (default flow)
plan_status: CONDITIONAL     -> execute Phase B using documented fallback_behavior
plan_status: BLOCKED         -> abort with exec-fail; plan is not executable
```

For `VERIFY_ONLY` and `PARTIAL_APPLIED`, read the `pre_applied` column from every
`files_to_create` and `files_to_modify` row in the active plan/phase. Evidence
may be a commit/hash, existing file path plus expected content marker, or passing
test name. If the column is absent for these statuses, abort with
`REQUIRES_PLAN_REVISION`.

**Verify-only branch (skip Phase B and Phase C generation):**

1. Re-confirm every planned file row has non-`none` `pre_applied` evidence, then
   verify that evidence against the current workspace. If any file fails
   verification -> abort short-circuit and fall through to normal Phase B (the
   plan was wrong about pre-application).
2. Run only the cheapest available verification: `validation-tools.md` test command for the changed files (NOT the full test suite if `validation-tools.md` exposes a scoped command; full suite as fallback). If unavailable, skip.
   **If this verification FAILS (non-zero exit, genuine failure):** the plan's
   "already applied" claim is wrong or the fix is broken. Do NOT exit as
   `ALREADY_VERIFIED`. Abort the short-circuit and fall through to normal Phase B
   so the failure is handled by the Phase C gate (CAL-INF-001). This is a
   one-time fall-through, not a loop — Phase B/C run once with their own caps.
3. Write IMPL-STATE with:
   ```yaml
   status: ALREADY_VERIFIED
   total_files_modified: 0
   files_touched: []
   deviations:
     - { type: pre-applied-fix, planned: <change>, actual: already in code, source: <plan file row pre_applied> }
   verification: { ran: <command-or-skipped>, result: <PASS | FAIL | SKIPPED> }
   ```
4. Update Memory Bank (`progress.md`) with the verify-only entry.
5. EXIT — do not enter Phase B or write Phase C/D artifacts.

**Partial-applied branch (Phase B still runs):**

1. Verify each file row whose `pre_applied` value is not `none`.
2. If evidence passes, mark that row as `SKIPPED_PRE_APPLIED` in IMPL-STATE and
   do not rewrite that file for the pre-applied change.
3. If evidence fails, mark that row as `PENDING_AFTER_EVIDENCE_MISS`, record a
   deviation with the failed `pre_applied` value, and include the row in Phase B.
4. Execute Phase B only for rows where `pre_applied` is `none` or verification
   failed. Continue through normal Phase C/D gates.

**REPAIR mode override:** If `failure_feedback` is non-empty, the verify-only branch is DISABLED. The orchestrator wants the full flow because the previous run was rejected.

**Execution:** automated

---

### Step 1.6: Resume from `_progress.json` (REPAIR support)

If `_progress.json` already exists at the IMPL output folder (list-shape
variant for implementing-code — files/phases instead of named sections):

```
LOAD _progress.json.

IF _progress.json.status IN ["RUNNING", "PARTIAL"]:
  PARSE _progress.json.files[] (list-shape: per-file completion status)
        AND _progress.json.phases{} (Phase A/B/C/D status)
  FOR EACH file entry in plan's file list:
    IF file is marked status == "complete" AND file exists on disk:
      MARK file as SKIP (already written; do NOT re-author)
    IF file is marked status == "in_progress":
      MARK file as RESUME (re-author from scratch; previous attempt incomplete)
    IF file is marked status == "pending" or unknown:
      MARK file as DO
  FOR EACH phase in [A, B, C, D]:
    Honor phase status the same way (Phase A skeleton skip if complete, etc.)

IF _progress.json.status == "complete":
  No work to do. Emit "implementation already complete" and exit.

ELSE (no _progress.json):
  Already written in Step 1; all files = "pending".

CHECKPOINT after every 3 files completed OR every 30 iterations:
  UPDATE _progress.json:
    files[i].status = "complete" | "in_progress"
    files[i].iterations_used = <count>
    last_checkpoint_iter = <current iter>

  IF (configured_max_iterations - current_iter) < (remaining_file_count * 20):
    EXIT_REASON = "ITERATION_BUDGET_EXHAUSTED"
    UPDATE _progress.json.status = "PARTIAL"
    Exit cleanly. A subsequent REPAIR can resume.

REPAIR validation: before SKIPping a "complete" file, verify the file exists on
disk and is non-empty. If absent (stale status), demote to RESUME and re-author.
For IMPL-STATE entries themselves, before SKIPping verify the corresponding
WFF-SECTION:{name}:complete anchor exists in IMPL_STATE_PATH.
```

**Execution:** automated

---

### Step 2: Load Phase Context

> **Before any discovery scan — apply execution-protocol.md Section 13 (Code-Location Discipline).** The PLAN-SPEC already names each target file; use those paths directly. When you must locate a file the plan does NOT pin (an insertion point, a consumer to update, a helper to reuse), read `context-pack/codebase-map.md` (and `project-inventory.md` if present) BEFORE running a repository-wide `grep`/`glob`/`find` to discover where it lives — **consult before scan, not never scan**. Fall back to a scoped scan only where the map is absent or insufficient, and note that gap in IMPL-STATE.deviations so the map can be corrected.

**Context is loaded as part of Phase B.**

**From agent-native plan (PLAN-SPEC):**
- Load the target phase using the PLAN-SPEC Phase Load Contract: header,
  matching `required_artifacts`, matching `canonical_values`,
  `plan_status_semantics`, phase summary row, target phase block, cross-phase
  rows involving the phase, acceptance criteria rows for the phase, and relevant
  open_questions.
- Open only the `required_artifacts` files whose `phases_using` is `all` or the
  active phase.
- Do not load PLAN-AUDIT or RESEARCH-SPEC during normal execution.

**From legacy plan:**
- Read individual phase document file (`0N-phase-N-[name].md`)

**Research context (fallback only):**
- If PLAN-SPEC fails self-containment during execution (for example a needed
  literal/signature/path is missing) AND `research_folder_path` is provided,
  grep/read the smallest relevant research slice as a fallback.
- Record an IMPL-STATE deviation: `PLAN-SPEC self-containment gap; consulted RESEARCH-SPEC fallback`.
- If no fallback exists or the gap is implementability-gating, block with
  `ARCHITECTURE_FLAW` / `REQUIRES_PLAN_REVISION` rather than inventing.

**Code context per mode:**
- STANDARD: load list of files to create/modify from phase spec
- REPAIR: load `files_touched` from IMPL-STATE + `failure_feedback` directives

**Design context (UI-bearing files only):**
For each file in the current phase whose `design_ref` annotation points to a
screen / component / image (set by `researching-code-design` per its DESIGN_CONTEXT
consumption rules):

1. **Prefer PLAN-SPEC encodings first.** The planner has extracted screen names,
   components, interactions, design tokens, and any external design files into
   structured rows and `required_artifacts`. Most UI implementation work is fully
   driven by those rows.
2. **Open raw assets only when needed.** When `design_specs_path` is provided AND the
   structured rows are insufficient for the current file (e.g., the file is a screen
   container and needs the full interaction flow), `cat` the specific section of
   `design_specs_path` referenced by `design_ref`. Do NOT load the full design
   document — read the named screen / component block only.
3. **Open one image at a time.** When `design_images_path` is provided AND `design_ref`
   resolves to a filename in that directory, read that single image during the file's
   Phase B generation, then FLUSH it before moving to the next file. Never preload
   multiple images.
4. **Record the consultation** in IMPL_INDEX.files_touched: `design_consulted: "screens/Dashboard.png"`.
   Reviewers use this to verify visual fidelity claims.
5. **Fall back gracefully.** When `design_specs_path` / `design_images_path` are unset
   (or `design_ref` is `null`), implement from prose only and log
   `"UI implemented from prose only — no design assets supplied for {file}"` to
   IMPL_INDEX.deviations. Do not block. Do not invent visual specifics — keep styling
   token-driven and use semantic class names.

**Test-case (FTC) context — same on-demand discipline:**
The PLAN-SPEC already carries the test intent: each `testing_strategy` row names the
test file, its `type` (level), and a `test_case_id` (an upstream FTC id, or `[derived]`).
Do NOT preload the FTC suites here.

1. **Drive from the plan first.** The `test_case_id` column tells you which FTC each
   RED test satisfies and which rows are deferred (`type: e2e` + `covered_by:
   qe-web-automation`). That is enough to plan the phase's test work.
2. **Open one FTC suite only when writing its test.** During Step 3 RED for a file whose
   plan row cites an FTC id AND `test_cases_path` is provided, `cat` only that FTC's
   epic suite (`{test_cases_path}/suites/epic-NN-func-tests.md`), lift the cited FTC's
   Gherkin Then clauses into the test's assertions, then FLUSH the suite before the next
   file. Never load the whole `suites/` folder.
3. **Do not reclassify.** Honor the plan's `type`. Never turn an FTC marked for e2e into
   a unit/integration test here — that is the automation capability's work.
4. **Record the consultation** in IMPL_INDEX.files_touched: `test_case_ref: "FTC_01_03_02"`.
5. **Fall back gracefully.** When `test_cases_path` is unset (or a row is `[derived]`),
   derive RED assertions from the plan + research exactly as before. Do not block.

**Execution:** automated

---

### Step 3: Execute Implementation (Phase B)
**READ** `references/phase-b-execute.md` **NOW**.

For each file in the phase:
1. Update IMPL_INDEX: current_file = IN_PROGRESS
2. Generate file content respecting PLAN-SPEC and explicitly loaded required artifacts
3. Run an artifact fidelity pre-write check against the upstream constraints for that file/artifact
4. **WRITE FILE** (mandatory tool call — not deferred)
5. Write corresponding test file if applicable
6. Update IMPL_INDEX: current_file = COMPLETED, files_touched += path
7. **FLUSH** generated content from memory
8. Verify file exists on disk

**Per-file Write-Flush-Forget loop** (PRESERVED exactly from v2.x).

**TDAD protocol** (PRESERVED exactly):
- When enabled: Red → Green → Refactor per file
- Write failing test first, implement to pass, refactor while green

**Source Fidelity Check** (PRESERVED):
- Pre-write gate verifying content matches plan specification
- Verify explicit upstream artifact details remain intact: identifiers, literals,
  schema/contract shapes, query/filter/order semantics, configuration keys,
  dependency declarations, and file/path targets
- If fidelity cannot be preserved exactly, STOP and log blocker/deviation instead
  of silently implementing a simplified variant

**Architecture Flaw Detection** (PRESERVED):
- RPI HALT protocol when structural issues detected

**API Contract Compliance** (PRESERVED):
- Verify implementations match specified API contracts

**REPAIR mode** (PRESERVED):
- Apply only surgical fixes per `failure_feedback` directives
- Log every change to IMPL_INDEX.repair_log
- Full REPAIR protocol: see `references/repair-mode.md`

**All 26 Implementation Consistency Rules apply** — see `references/consistency-rules.md`.

**Execution:** automated

---

### Step 4: Verify Build, Generate README & Agentic Metadata (Phase C) — MANDATORY
**READ** `references/phase-c-verify.md` **NOW. DO NOT SKIP THIS STEP.**

**This step is MANDATORY after every Phase B completion. Skipping it is a protocol violation.**
This is the critical step that prevents the human repair loop.

**Step 1: Discover Tech Stack** (PRESERVED)
- Scan generated files to detect frameworks, languages, build tools
- Do NOT assume — read pom.xml, package.json, Dockerfile, docker-compose.yml,
  Makefile, build.gradle, etc.

**Step 2: Scaffolding Completeness Gate** (PRESERVED)
- Verify all cross-file references resolve (imports, build contexts, config references)

**Step 2b: Plan Adherence Verification** (PRESERVED)
- Verify every file specified in the phase plan was created/modified
- Verify no unplanned files were created
- Verify implemented artifact details still match the exact plan/research
  constraints that justified those file changes

**Step 2c: AC Test Coverage Matrix** (PRESERVED)
- Map acceptance criteria from plan to test files
- Flag any AC without corresponding test coverage
- Ensure tests cover preserved artifact semantics when the source specified exact
  behavior (for example: contract fields, query predicates/order, config-driven
  behavior, schema validation, dependency wiring)

**Step 2d: Boundary Value Coverage Check** (MANDATORY for numeric/duration parameters)
- For EVERY numeric parameter (count, duration, amount, size, index, ratio):
  - Test: `0` (zero / empty / null)
  - Test: `0.5` or fractional value (if domain supports non-integer values)
  - Test: `1` (minimum positive)
  - Test: representative large value `N`
- Flag any numeric AC or business rule with no corresponding boundary test
- This check is MANDATORY — do NOT skip even if main happy-path tests pass
- A passing build with no boundary tests is NOT a complete implementation

**Step 3: Tool Verification** (MOVED — formerly Step 5)
- **READ** `references/phase-c-tools.md` for tool verification protocol
- If bash available: run discovered build commands
- Self-correction loop: fix errors, retry (max 3 attempts)

**⛔ POST-BUILD GATE — DO NOT EXIT HERE ⛔**
Build passing means Step 3 is done. Phase C has 5 steps, not 3.
You MUST now execute Steps 4 and 5 below before Phase D or any final response.
**Verify by running:** `ls {source_path}/README.md {source_path}/AGENTS.md 2>/dev/null`
If either file is missing, you are NOT done — execute the corresponding step.

**Step 4: Generate README.md** — MANDATORY, runs on EVERY phase
- Using discovered tech stack, produce build/run instructions at `{source_path}/README.md`
- This is NOT optional. README.md is a deliverable artifact.
- **After writing, verify:** `ls -la {source_path}/README.md`

**Step 5: Generate AGENTS.md** — MANDATORY on final phase (Rule 9)
- Produce agentic metadata file at `{source_path}/AGENTS.md`
- Only runs when no PENDING phases remain after current phase
- On final phase this is MANDATORY — do NOT skip after tests pass
- **After writing, verify:** `ls -la {source_path}/AGENTS.md`

**Phase C Build Execution Hard Gate — BLOCKED until all builds recorded:**
MANDATORY: Before marking Phase 3 COMPLETE, execute each `build_commands_discovered`,
record exit_code in IMPL-STATE `tool_results`. Phase 3 is ONLY COMPLETE when
`tool_results` has entries for ALL commands in `build_commands_discovered`.
Apply `execution-protocol.md` §10.5.3 (tool-output retention): run each command in
full, but record only the verdict (exit code + pass/fail counts) — on failure, the
failing slice — in `tool_results`. Redirect verbose logs to a file and `grep`/`tail`
on demand; never let a full passing build/test log persist in context across the
implementation loop's round-trips. See `references/phase-c-checklist.md` item 9.

**Build Output Artifact Gate — BLOCKED until declared outputs exist:**
IF the plan declares expected build/packaging output artifacts (compiled binaries,
packages, bundles, container images, archives — as acceptance items naming filenames
or patterns + a directory): after the build commands succeed, `ls` the declared
directory and confirm each expected artifact (or pattern match) is present. If any
declared artifact is MISSING despite a zero exit code: STOP — do NOT mark Phase 3
COMPLETE; record the gap in `tool_results` and treat it as a build failure (a clean
exit with absent expected outputs is the documented "discarded at gate" failure mode).

**Phase C Completion Gate — BLOCKED until README.md + AGENTS.md exist:**
- Run: `ls {source_path}/README.md {source_path}/AGENTS.md 2>/dev/null | wc -l`
- If result < 2 (final phase) or < 1 (non-final): STOP. Go back and generate the missing file(s).
- Only after this check passes → proceed to Phase D

Phase C produces artifacts (README.md, AGENTS.md, tool_results) but does NOT:
  - Update IMPL-STATE with final status
  - Write Memory Bank files
  - Write stepwise output parameters
These happen in Phase D. Emitting final_response after BUILD SUCCESS skips them all.

**Execution:** automated

---

### Step 4b: Pre-Completion Quality Checklist (Phase C→D Boundary)

**READ** `references/phase-c-checklist.md` **NOW** before transitioning to Phase D.

**Review Criteria Pre-Check (MANDATORY — read before self-review):**
If `context-pack/test-standards.md` exists AND the current capability has a downstream
automated review step (e.g., review-graph, review-mcp-tools, review-ux-components):
1. Read the "Review Acceptance Criteria" section in `context-pack/test-standards.md`.
2. For each criterion listed, verify the current implementation satisfies it BEFORE
   submitting output. Do not defer this check to the review step.
3. If a criterion cannot be satisfied, record it as a blocker in IMPL-STATE.blockers
   rather than submitting a known-failing implementation.
If `context-pack/test-standards.md` does not exist or has no "Review Acceptance Criteria"
section, derive self-review criteria from the PLAN-SPEC acceptance criteria and log a
deviation: `"context-pack/test-standards.md missing review criteria — self-review derived from plan."`.

That file contains four checks that must all pass before Phase D:
1. TDAD Compliance Check (when tdad_mode enabled)
2. Implementation Completeness Self-Check
3. Plan File Coverage Gate
4. Pre-Completion Quality Checklist (10 items: read-before-write, resilience patterns, HTTP mappings, PMD, integration tests, source_path emission, Spring Boot test context, package.json, design image audit, etc.)

Before leaving Phase C, also verify artifact fidelity end-to-end: the final
implementation and tests must still reflect the exact upstream constraints that
were preserved by research and planning. If the delivered artifact only matches
intent at a high level while dropping explicit source detail, Phase C is not
complete. Record the result as `validations["artifact_fidelity"]`.

**Evidence is mandatory, not advisory (REC-001).** These checks are no longer an
honor-system list. Each one MUST record a structured verdict in
`IMPL_INDEX.validations[...]` (`plan_adherence`, `plan_file_coverage`,
`ac_coverage`, `artifact_fidelity`, and `tdad_compliance` when `tdad_mode`).
The Phase C Completion Gate (Check 5) reads those verdicts and **self-fails the
run (→ FAILED → REPAIR) if any required check is FAIL or its verdict is absent** —
before the human gate ever sees it. This mirrors the reviewer's checks inside the
generator so `implementation-validation` rejections (Incomplete / Wrong_Format)
are caught here. Absence of evidence is treated as failure, not as "probably fine."
Loop-safety: the gate derives a missing verdict from existing IMPL_INDEX state
(a read), never by re-running a Phase C step — it is evaluated exactly once.

Failure to verify these is the #1 source of code-review BLOCKING findings.

---

### Step 5: Finalize Phase (Phase D) — MANDATORY
**READ** `references/phase-d-finalize.md` **NOW. DO NOT SKIP THIS STEP.**

**This step is MANDATORY after every Phase C completion. Skipping it is a protocol violation.**

**MINIMUM PHASE D ACTIONS (execute even if reference file cannot be loaded):**
  1. Verify README.md and AGENTS.md (final phase) exist — generate if missing
  2. Update IMPL-STATE: set phase status to COMPLETED, write execution_log entry
  3. Write context-pack/active-context.md with session end state
  4. Append milestone row to context-pack/progress.md
  5. Write final summary
  6. ONLY THEN may you emit a final response

**Phase C Artifact Verification** (PRESERVED):
- Defense-in-depth check: verify README.md exists
- Final phase: verify AGENTS.md exists
- If missing: return to Phase C for the specific step

**Determine Phase Status** (CAL-INF-001 — test/build failures BLOCK completion):
- COMPLETED: all files written, scaffolding passed, build AND tests passed (or no bash)
- COMPLETED_WITH_WARNINGS: NON-build / NON-test residue only (e.g., a tolerated
  lint/typecheck warning). An unresolved build or test failure can NEVER land here.
- FAILED: unresolved GENUINE build/test failure after the 3 self-correction
  attempts, or any file write failure. Routes to REPAIR via `exec-fail` — the
  skill does NOT defer a failing test suite to the human gate.
- BLOCKED: environmental failure (runner could not build/execute — sandbox, no
  network, unavailable service) or other unresolvable blocker.
- ARCHITECTURE_FLAW: structural issue requiring plan revision

> **Loop-safety:** the only retry inside a single run is the 3-attempt
> self-correction budget in Phase C tool verification. A FAIL that survives it is
> recorded and converted to a terminal status here — it is NEVER re-run within the
> same invocation. Further iteration happens only via the orchestrator re-invoking
> this skill in REPAIR mode (bounded by `repair_log` and the orchestrator's cap).

**Update IMPL-STATE** (replaces separate progress + audit updates):
- Write phase status, files_touched, tool_results, execution_log entry
- Write metrics (files written, tests passed, coverage)
- Write validations (scaffolding gate, plan adherence, AC coverage results)
- Consolidate open_questions

**Memory Bank updates:**
At session end, follow execution-protocol.md for Memory Bank write
(active-context.md + progress.md). Artifact type: "N files, M tests".
Log all implementation decisions to active-context.md Decisions Log (see execution-protocol.md Section 4 for schema).

**Phase Loop Continuation Mandate** (PRESERVED):
- If more PENDING phases remain AND execution_scope != "single": continue to next phase
- Loop back to Step 3 (Phase B) for next PENDING phase
- Stop only when all phases COMPLETED, BLOCKED, or scope is "single"

**Final Summary** (PRESERVED):
- On last phase completion: write session summary to IMPL-STATE
- Include overall status, total files, total tests, blockers, deviations

**Execution:** automated

## REPAIR Mode

Triggered when `failure_feedback` parameter is provided.

**READ** `references/repair-mode.md` **NOW** if `failure_feedback` is non-empty.
That file covers:
- Mandatory rejection-checklist construction (cumulative across prior repairs)
- REPAIR mechanics (load IMPL-STATE, parse feedback, apply targeted fixes, regression check, repair_delta)
- Full Test Suite Verification (baseline → repair → re-run → classify residual failures)

In STANDARD mode, skip this section.

## Escape Hatch Protocol

```
TRIGGER: Prerequisites not met, tests failing after 3 attempts,
         external dependency unavailable, build failing after 3 attempts

PROTOCOL:
1. DOCUMENT immediately in IMPL_INDEX.blockers
2. ASSESS: Can other phases proceed independently?
3. ESCALATE: Log owner and needed-by from phase document
4. APPLY workaround if possible, document in IMPL_INDEX.deviations

NOTE (CAL-INF-001): "tests failing after 3 attempts" and "build failing after 3
attempts" are NOT a license to mark the phase COMPLETED_WITH_WARNINGS and defer to
the human. They set BUILD_GATE / TEST_GATE = FAIL in Phase C; the Completion Gate
then BLOCKS `complete` and Phase D assigns FAILED (genuine → REPAIR via exec-fail)
or BLOCKED (environmental → human). This protocol DOCUMENTS the failure; it does
NOT retry — the 3-attempt budget is already spent, so there is no loop.

COMPONENT WIRING RESOLUTION — When resolving open questions about component
wiring or call sites:
1. Search for direct API/service consumers first.
2. If none found, trace the user flow — identify which component initiates
   the feature from the user's perspective (e.g., button clicks, navigation triggers).
3. If still unresolved, escalate as a blocker — do not defer or assume the
   wiring is impossible.
```

## Artifact Naming Convention (MANDATORY)

All output artifact filenames MUST follow these exact templates:
- Implementation state: `IMPL-STATE-{SESSION_ID}.md`
- Code review spec: `REVIEW-SPEC-{SESSION_ID}.md`
- Code review audit: `REVIEW-AUDIT-{SESSION_ID}.md`

Where `{SESSION_ID}` is generated per **execution-protocol.md Section 1** — priority order: feature_id-scoped → session_name-scoped → date-only. The SESSION_ID embeds enough scope to keep concurrent or sequential runs uniquely addressable in the same project folder.

**Backward-compatible read pattern:** When loading prior IMPL-STATE in REPAIR mode, accept BOTH the new SESSION_ID-scoped name AND the legacy `IMPL-STATE-{feature_id}.md` form. New writes always use the SESSION_ID form. If you find a legacy file, log a one-line deviation noting the rename so calibrating-execution can flag the stale convention.

## ADR Binding Protocol (MANDATORY — resolve before implementation)

When ADRs are available at `{adr_path}`, classify each ADR before implementing:

```
BINDING_ADRS = []
ADVISORY_ADRS = []

FOR each ADR in adr_path:
  1. Check context-pack/adr-enforcement-rules.md (if exists):
     - BINDING section → add to BINDING_ADRS
     - ADVISORY section → add to ADVISORY_ADRS

  2. If adr-enforcement-rules.md does not exist, use the ADR's own status field:
     - status: Accepted → BINDING_ADRS
     - status: Proposed, Superseded, Deprecated → ADVISORY_ADRS

  3. If no status field, scan ADR content for explicit markers:
     - "MUST", "mandatory", "required", "binding" → BINDING_ADRS
     - "SHOULD", "preferred", "recommended", "advisory" → ADVISORY_ADRS
     - No marker → default to ADVISORY_ADRS; log as assumption

LOG: "ADR binding resolved: {N} BINDING, {M} ADVISORY"
```

Enforcement rules:
- BINDING ADRs: violation is a **blocking** implementation error. Do not deviate. If a BINDING ADR cannot be satisfied, block the phase and document in IMPL_INDEX.blockers.
- ADVISORY ADRs: deviation is allowed. Document the deviation and rationale in `IMPL_INDEX.deviations` as an accepted derogation.

## OpenAPI 3.0 Specification (conditional — REST endpoint implementations only)

**Apply this section ONLY when the feature being implemented exposes REST endpoints.**

If the phase document or user story defines REST endpoints (GET, POST, PUT, PATCH, DELETE paths), include the OpenAPI 3.0 specification as part of the implementation:

```
1. Determine if this phase implements REST endpoints:
   IF phase document contains route definitions, @RestController, @RequestMapping, or
   endpoint path/method specifications → apply this section
   ELSE → skip (not applicable for non-REST code such as batch jobs, CLI tools, domain logic)

2. Generate `src/main/resources/openapi.yaml` for all REST endpoints in scope:
   - path and HTTP method
   - request body schema (field names, types, required flags)
   - response codes (200, 400, 404, 422, 500 as applicable)
   - error response schemas

3. For Spring Boot projects, add SpringDoc dependency to pom.xml:
   <dependency>
     <groupId>org.springdoc</groupId>
     <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
     <version>2.x.x</version>
   </dependency>

4. Verify openapi.yaml is written and non-empty before phase completion
```

VIOLATION: Implementing REST endpoints without an openapi.yaml is a violation of ADR-006 (if that ADR is BINDING for this project). Check the ADR binding classification before flagging — see ADR Binding Protocol above.

## Reference Files

| File | Load when | Purpose |
|------|-----------|---------|
| `references/parallel-execution.md` | Step 0, ONLY when `parallel_scopes` is set | Fan-out safety gate (disjoint-subtree check), coordinator protocol, degrade-to-sequential rules |
| `references/phase-a-initialize.md` | Step 1 (Phase A) | Session init, mode detection, folder resolution, Memory Bank read |
| `references/consistency-rules.md` | End of Phase A | The 26 rules + Test Suite Integrity + Test Impact Checklist + Prove-It Pattern + Common Rationalizations + Red Flags |
| `references/repair-mode.md` | End of Phase A, only if `failure_feedback` non-empty; OR mid-Phase-B if an integrity break is detected | Rejection checklist, REPAIR mechanics, Full Test Suite Verification, integrity-break trigger |
| `references/recovery-protocol.md` | Mid-Phase-B, ONLY when an integrity-break signal fires (file wiped, truncated, fully replaced when it shouldn't be) | git-checkout-first decision tree, IMPL-STATE replay, banned bash scavenger hunts |
| `references/phase-b-execute.md` | Step 3 (Phase B) | File generation loop (BUILD + REPAIR), TDAD, Write-Flush-Forget |
| `references/phase-c-verify.md` | Step 4 (Phase C) | Scaffolding gate, plan adherence, tool verification, README/AGENTS.md generation |
| `references/phase-c-tools.md` | Step 4 → Tool Verification | Tool verification protocol (build, test, lint, typecheck) |
| `references/phase-c-checklist.md` | Step 4b (C→D boundary) | TDAD Compliance, Implementation Completeness, Plan File Coverage Gate, Pre-Completion Quality Checklist |
| `references/phase-d-finalize.md` | Step 5 (Phase D) | Phase completion, status determination, Memory Bank write |
| `references/code-implementation-template.md` | When generating IMPL-STATE | IMPL-STATE file structure template |
| `context-pack/execution-protocol.md` | As referenced | Session ID generation, _progress.json lifecycle, IMPL-STATE schema, Memory Bank protocol, FIC/Recovery Checkpoint, dual-format detection, REPAIR mechanics |

## Downstream Contract

**Primary consumer:** `reviewing-code` — reads source code at `{source_path}/`
**Secondary consumer:** `performing-acceptance-testing` — reads test results
**Orchestrator:** reads IMPL-STATE for status, blockers, repair context

| IMPL-STATE Field | Consumer Usage |
|-----------------|----------------|
| `status` | Route to next step or REPAIR |
| `phases[].status` | Determine completion |
| `blockers` | Determine if plan revision needed (ARCHITECTURE_FLAW) |
| `files_touched` | What was implemented |
| `tool_results` | Build/test verification status |
| `repair_log` | Track repair iterations |
| `open_questions` | Gaps for human review |
