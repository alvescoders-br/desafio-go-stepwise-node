---
name: planning-code-tasks
description: >
  Planning phase orchestration for code development. Supports two execution scopes:
  (1) TASK: Transforms focused bug-fix / user-story research into a concise 1-3 phase plan.
  (2) FULL_SDLC: Transforms research artifacts into phased implementation blueprints.
  Output is two files: PLAN-SPEC-{SESSION_ID}.md + PLAN-AUDIT-{SESSION_ID}.md.
  Consolidates 6 files (TASK) or 14+ files (FULL_SDLC) into a compact execution-facing
  agent-native spec. No prose. No narrative. Only structured data the implementing
  agent needs; validation detail lives in PLAN-AUDIT.
  Enforces Zero Invention Policy. BUILD and REPAIR modes.
  Applies RPI workflow. FIC context discipline (Correct, Complete, Concise).
  Human-readable output generated on demand via `humanize-spec` skill (separate).
license: Proprietary
metadata:
  author: aipods-team
  version: 4.1.0
  category: engineering
  tags: code-development, planning, automated, agent-native, dual-scope, quality-criteria
---

# Planning Code Tasks — Agent-Native Spec

## SKILL PROTOCOL — ENTRY RULES (read first, do not skip)

1. **The protocol below is internally consistent.** If you perceive a conflict
   between the capability prompt and this skill, the skill wins for execution
   mechanics; the capability wins for paths/parameters. Do NOT exit citing
   "ambiguity" or "internal contradiction" — every section here has been
   tested in production runs.

2. **Begin Step 1 immediately.** Do NOT re-evaluate the protocol's completeness
   before starting. Step 1's first action (write `_progress.json` to
   `EFFECTIVE_PLANNING_OUTPUT_PATH`) IS the verification. If a required input is genuinely
   missing, you will discover it during Step 2 validation and write a Gap
   Report — not before.

3. **Reference files are loaded on demand via `cat`** when each step's
   `READ ... NOW` pointer says so. They are NOT preloaded into your context.
   The Reference Files table at the bottom of this file is a pointer index.

4. **Zero Invention Policy is non-negotiable.** Any claim not traceable to
   research or source context must be registered in `open_questions` as a
   pending input/gap, or in `assumptions_to_validate` with an ASM-XX ID and
   deterministic fallback when non-blocking. Asking a clarifying question of
   the human = task FAILURE — there is no human watching. Either execute, or
   call `stepwise session exec-fail`.

   **Artifact Fidelity Rule — mandatory across all plan outputs.** When research
   or optional context contains explicit artifact-shaping details, the plan must
   preserve them as executable constraints rather than paraphrasing them away.
   This applies to code, SQL, configuration, schemas, infrastructure assets,
   contracts, structured data, and other implementation artifacts. Do not
   silently rename, simplify, generalize, reorder, or substitute explicit
   upstream details unless a higher-priority source explicitly authorizes it.

5. **No final response until PLAN-SPEC + PLAN-AUDIT exist on disk.** Both
   files (`PLAN-SPEC-{SESSION_ID}.md` and `PLAN-AUDIT-{SESSION_ID}.md`) must
   exist at `EFFECTIVE_PLANNING_OUTPUT_PATH` and be non-empty before you emit a closing
   summary. Any final response without those files is a protocol violation.

6. **Write-Flush-Forget — non-negotiable.** After writing the PLAN-SPEC
   skeleton in Step 3, NEVER re-read the spec file in full. Authoring a phase
   or section is exactly four operations: (a) read `_progress.json` (small),
   (b) load section-specific inputs (research extractions or phase fixtures),
   (c) one targeted `Edit` replacing the section's `WFF-SECTION:{name}:pending`
   anchor with the section body, (d) update `_progress.json`. The agent's
   working memory holds at most ONE in-flight section body at a time. The
   PLAN-SPEC file is write-only after the skeleton is laid down.

   **Why:** repeated `view` of the working spec inflates prompt tokens
   geometrically with iteration count and breaks prompt-cache continuity.
   Calibration evidence (Edenred sprint-3) showed 5M+ prompt tokens per
   failed run attributable to this pattern. The HU0301 planning run 4 truncation
   ($14.95 wipe) is also covered by execution-protocol §10.5.2 Safe-Write.

   **Forbidden tool patterns inside the section-author loop:**
   - `view PLAN_SPEC_PATH` (any kind) AFTER the skeleton is written. Read `_progress.json` instead.
   - `replace_all=true` on PLAN-SPEC. Use targeted anchored Edits.
   - `bash wc -l PLAN_SPEC_PATH` to "verify" progress. Placeholder anchor presence is the verification.

   **Permitted exceptions (must be explicitly justified in agent reasoning):**
   - At the very end of the run, ONE final grep to verify all placeholders are
     replaced (`! grep "WFF-SECTION:.*:pending" PLAN_SPEC_PATH`).
   - On REPAIR: ONE initial bounded read (offset/limit, max 80 lines) around
     the affected section to confirm placeholder state.

---

## Quick Start
Transform research artifacts into a phased implementation blueprint.
Output is **two files**:
- `{planning_output_path}/PLAN-SPEC-{SESSION_ID}.md` — Single agent-native spec (all sections)
- `{planning_output_path}/PLAN-AUDIT-{SESSION_ID}.md` — Session audit trail (metadata only)

**Human-readable output:** Not produced by this skill. Use `humanize-spec` skill
with the `code-task-planning` rendering profile to generate rich documents on demand.

**Downstream consumer:** `implementing-code` reads PLAN-SPEC directly.

**Spec sections and structure:** See `references/code-task-planning-template.md`
for the complete section definitions.

## Known Failure Modes
<!-- ACCUMULATING — appended by calibrating-updates (WS6). Newest first. Rules MUST be generic/behavioral (project-agnostic); project-specific fixes go to context packs, never here. Format + entry rules: engineering-skills/references/known-failure-modes-format.md. Read these at pre-flight so a lesson learned once recurs no more. -->

## Anti-Patterns (do NOT)
<!-- ACCUMULATING — appended by calibrating-updates (WS6). One line each: **AP-NNN** (ISO-date, source: REC-NNN): prohibition — why. -->

## Output Architecture

```
{planning_output_path}/
├── PLAN-SPEC-{SESSION_ID}.md     ← Single agent-native spec (scope-adaptive sections)
└── PLAN-AUDIT-{SESSION_ID}.md    ← Session audit trail (metadata only)
```

**Scaling:** Single file at all scales. The implementing agent loads one phase
section at a time regardless of total phase count, so file size is not a
consumption bottleneck.

---

## Parameters

| Name                   | Type   | Required | Scope      | Notes                                      |
|------------------------|--------|----------|------------|---------------------------------------------|
| project_name           | string | Yes      | Both       | Abort if missing                            |
| feature_id             | string | No       | Both       | Optional artifact scope. When empty, follow a scoped `research_output_path` reported by research. |
| research_output_path   | string | Yes      | Both       | Abort if missing. Reads RESEARCH-SPEC (agent-native) or legacy 20-doc format |
| planning_output_path   | string | Yes      | Both       | Pre-composed planning folder. When `feature_id` is empty but `research_output_path` is scoped, Step 1 writes to the sibling planning folder under that same scope and reports it. |
| user_stories_path       | string | No       | FULL_SDLC  | Required for FULL_SDLC scope only           |
| target_architecture    | string | No       | FULL_SDLC  | Required for FULL_SDLC scope only           |
| adr_path               | string | No       | Both       | Optional                                    |
| domain_boundaries_path | string | No       | Both       | Optional                                    |
| source_path            | string | No       | Both       | Optional                                    |
| context_pack_path      | string | No       | Both       | Optional                                    |
| quality_criteria_path  | string | No       | Both       | Optional. Path to a quality-criteria document (e.g., `criteria/code-development-criteria.md`). When provided AND the file exists, REQUIRED items are extracted and emitted as explicit acceptance criteria (see Step 2 and Step 3). |
| test_cases_path        | string | No       | Both       | Optional. Path to a functional test-case (FTC) suite folder produced upstream by `quality-engineering-design` (`generating-test-cases`) — a `FTC-MANIFEST-*.md` plus `suites/epic-NN-func-tests.md`. When provided AND present, the plan treats the FTCs as the **authority on WHAT must be verified**; the planner remains the **authority on HOW** (which FTC becomes a unit test, an integration test, or is deferred to e2e). Each FTC id is carried into `testing_strategy` for traceability. When empty or absent, planning falls back to deriving tests from ACs + research exactly as before (fully backward-compatible). |
| design_specs_path      | string | No       | Both       | Optional. UI/UX specs forwarded from the capability. The plan reads RESEARCH-SPEC's DESIGN_CONTEXT for UI grouping; this raw path is forwarded for visual cross-check only and is **not re-loaded** when RESEARCH-SPEC already encodes DESIGN_CONTEXT. Used to scope UI phases per screen and size image-heavy work. |
| design_images_path     | string | No       | Both       | Optional. Directory of design images. Same forwarding semantics as `design_specs_path` — the plan trusts RESEARCH-SPEC's DESIGN_CONTEXT enumeration; raw path passes through to the implementer for on-demand visual reference. |
| failure_feedback       | string | No       | Both       | Present triggers REPAIR mode                |
| custom_message         | string | No       | Both       | Processing: applied as additional constraints during generation. If it names specific sections → prioritize depth. If it names concerns → add to open_questions if unresolvable. Never overrides validation rules. |

**If any Required parameter is not defined → ABORT EXECUTION immediately.**

---

## Dual-Format Input

| Format | Detection | Handling |
|--------|-----------|---------|
| Agent-native RESEARCH-SPEC | Single `RESEARCH-SPEC-*.md` file in `research_output_path` | Parse structured sections directly |
| Legacy 20-doc format | Multiple numbered files (00-XX) in `research_output_path` | Read index (00-*), then load referenced files on demand |

Detection is automatic at Step 1. Agent-native format is preferred.

**Multiple-spec tie-breaker (mandatory when more than one `RESEARCH-SPEC-*.md` exists):**

When two or more sessions have written to the same `research_output_path` (a real risk when `feature_id` is unset, or when an old run left a stale spec behind), Step 1 MUST pick deterministically:

1. List all `RESEARCH-SPEC-*.md` files in `research_output_path` and sort by mtime descending.
2. Prefer the spec whose SESSION_ID component matches the current `feature_id` parameter (or the Stepwise `session_name` when feature_id is unset). Match is exact-substring of the SESSION_ID-derived slug.
3. If no filename matches the current scope, pick the most-recently-modified file. Log the choice on a single line: `RESEARCH-SPEC selection: {chosen_filename} (mtime={...}, candidates={N})`.
4. **ABORT-with-guidance** if the top two candidates have mtimes within 1 second of each other AND neither matches the scope filter — the run cannot disambiguate, and silently picking would risk planning against the wrong feature's research. Emit:
   `Cannot disambiguate RESEARCH-SPEC. Two specs were written within 1s of each other and neither matches the current feature_id/session_name. Re-run with feature_id set, or remove the stale spec from {research_output_path}.`

This rule applies symmetrically when discovering existing PLAN-SPEC files in REPAIR mode. In REPAIR,
write the repaired PLAN-SPEC/PLAN-AUDIT back to the EXACT discovered filename — never recompute a
SESSION_ID or append a fresh date (execution-protocol.md §1); the date is fixed at BUILD time and a
later-day repair that re-mints it produces a duplicate instead of overwriting.

---

## Scope Detection

| Signal | Scope | Phase Count |
|--------|-------|-------------|
| Research contains `task_id` + `task_type` (BUG_FIX / USER_STORY / ENHANCEMENT) | TASK | LOW=1, MEDIUM=2, HIGH=3 |
| Research contains `user_stories_path` + multi-story structure | FULL_SDLC | Re-interpreted from research sequencing (see `references/phase-decomposition-rules.md`) |

---

## Workflow

### Step 1: Initialize + Scope Detection

> **⚠️ RESEARCH SPEC DISCOVERY — MANDATORY (execute before any other action in this step):**
>
> ```
> 1. Call list_directory({research_output_path}) — ONE tool call.
> 2. Find all files matching RESEARCH-SPEC-*.md in the listing.
>    Apply mtime tie-breaker (see Dual-Format Input section above):
>    sort descending by mtime, prefer the file whose SESSION_ID
>    component matches the current feature_id / session_name.
> 3. If no RESEARCH-SPEC-*.md is found:
>    a. Read {research_output_path}/_progress.json.
>    b. Extract session_id from that file.
>    c. Construct filename: RESEARCH-SPEC-{session_id}.md.
>    d. Verify the constructed path exists before proceeding.
> 4. If STILL not found after step 3 → ABORT with Gap Report:
>    "RESEARCH-SPEC not found in {research_output_path}. Listed
>     {N} files. Checked _progress.json for session_id fallback.
>     Cannot proceed without a resolvable RESEARCH-SPEC."
> DO NOT probe or guess individual filenames under any circumstances.
> DO NOT attempt reads like RESEARCH-SPEC-{project_name}.md,
> README.md, index.md, or any other speculative filename.
> The directory listing IS the discovery mechanism — use it.
> ```

> **⚠️ OUTPUT PATH — MANDATORY (verify before writing any output file):**
>
> ```
> RAW_PLANNING_OUTPUT_PATH = planning_output_path.
> EFFECTIVE_PLANNING_OUTPUT_PATH = RAW_PLANNING_OUTPUT_PATH by default.
>
> If `feature_id` is non-empty, RAW_PLANNING_OUTPUT_PATH is already the
> canonical scoped output directory. Use it as-is.
>
> If `feature_id` is empty and research reported a scoped path, follow that
> scope instead of writing to the flat fallback:
>   research_output_path = /.../code-development/{scope_slug}/research-output
>   planning_output_path = /.../code-development/code-task-planning
>   EFFECTIVE_PLANNING_OUTPUT_PATH =
>     /.../code-development/{scope_slug}/code-task-planning
>
> Use this sibling rule only when basename(dirname(research_output_path)) is
> not the code-development base folder and dirname(dirname(research_output_path))
> equals dirname(RAW_PLANNING_OUTPUT_PATH). If RAW_PLANNING_OUTPUT_PATH is
> already under the same scoped parent as research_output_path, use it as-is.
> When the sibling rule applies, set EFFECTIVE_PLANNING_OUTPUT_PATH to the
> sibling folder shown above.
>
> Write ALL output files (PLAN-SPEC-*.md, PLAN-AUDIT-*.md, _progress.json)
> directly to EFFECTIVE_PLANNING_OUTPUT_PATH.
>
> DO NOT prepend project_name, output_folder, or any unrelated directory.
>
> Correct:  write to {EFFECTIVE_PLANNING_OUTPUT_PATH}/PLAN-SPEC-*.md
> WRONG:    write to {output_folder}/{project_name}/{feature_id}/planning/PLAN-SPEC-*.md
>
> If planning_output_path is missing or empty → ABORT immediately.
> ```

**MODE detection:**
- `failure_feedback` NOT empty → `MODE = REPAIR`. Discover and load the existing PLAN-SPEC per the
  execution-protocol.md §7 discovery+reuse algorithm: if `failure_feedback` names a rejected artifact
  path, search `dirname(<path>)` for `basename(<path>)` (do NOT trust the possibly-re-rendered
  `planning_output_path` parameter for discovery); reuse the discovered file's folder AND filename
  verbatim (§1 — never recompute SESSION_ID/date). If a rejected path was named but no file is found →
  **ABORT with guidance, do NOT BUILD** (a fresh BUILD on a divergent path is the duplicate-on-REPAIR
  defect). Then parse directives.
- Otherwise → `MODE = BUILD`.

**Scope detection:**
- Research contains `task_id` + `task_type` → `SCOPE = TASK`
- Research contains `user_stories_path` or multi-story structure → `SCOPE = FULL_SDLC`
- Cannot determine → ABORT with Gap Report

**Task-shape verification (TASK only):**
After SCOPE = TASK is set, re-classify `task_type` based on research CONTENT
(not just the filename of the research artifact):

  1. EXTRACT regression_signals from research:
     - terms matching: regression, broken, fails, crash, exception, NPE,
       wrong value, off-by-one, deadlock, leak, race
     - root_cause section references an EXISTING method/file with a defect
  2. EXTRACT net_new_signals from research:
     - 3+ acceptance criteria that name NEW behaviors not present in current code
     - root_cause section says "method/feature does not exist" or "missing instrumentation"

  3. CLASSIFY:
     - regression_signals dominate → task_type = BUG_FIX
     - net_new_signals dominate     → task_type = ENHANCEMENT
     - both present                 → task_type = BUG_FIX (research filename wins
                                                            as tiebreaker)
     - neither                       → task_type = USER_STORY (default)

  4. IF the inferred task_type differs from the value read from the research
     artifact filename (e.g., filename says BUGFIX-* but content is
     ENHANCEMENT-shaped):
     - Log assumption ASM-XX: "task_type re-classified from BUG_FIX to
       ENHANCEMENT based on content analysis."
     - Use the inferred task_type for downstream phase planning. ENHANCEMENT
       plans emphasize new-file creation and UI wiring; BUG_FIX plans
       emphasize regression-prevention tests and diagnostic forensics.

**Zero Invention Policy:**
Not in research/source context -> register in `open_questions`. Never infer,
assume, or create information. Inferred standard practices -> register in
`assumptions_to_validate` with an ASM-XX ID.

**FIRST ACTION — MANDATORY:** Write `_progress.json` to the output folder before any other file write.
This early signal prevents the orchestrator from sending SIGINT to a running skill.

```json
{ "skill": "planning-code-tasks", "session_id": "initializing",
  "status": "RUNNING", "started_at": "<ISO timestamp>", "completed_at": null }
```

**Execution:** automated

---

### Step 1.5: Resume from `_progress.json` (REPAIR support)

Note: Scope detection (TASK vs FULL_SDLC) is handled inside Step 1 above — this
sub-step does NOT re-do that work. It is the resume contract only.

If `_progress.json` already exists at the planning output folder:

```
LOAD _progress.json.

IF _progress.json.status IN ["RUNNING", "PARTIAL"]:
  PARSE _progress.json.sections{} -> SECTION_STATUS
  FOR EACH section in plan_spec_section_catalog (see Step 3 template):
    IF SECTION_STATUS[section.name] == "complete":
      MARK section as SKIP (already written; do NOT re-author)
    IF SECTION_STATUS[section.name] == "in_progress":
      MARK section as RESUME (re-author from scratch; previous attempt incomplete)
    IF SECTION_STATUS[section.name] == "pending":
      MARK section as DO

IF _progress.json.status == "complete":
  No work to do. Emit "plan already complete" and exit.

ELSE (no _progress.json):
  Already written in Step 1; all sections = "pending".

CHECKPOINT after every 3 sections completed OR every 30 iterations:
  UPDATE _progress.json:
    sections.{name}.status = "complete" | "in_progress"
    sections.{name}.iterations_used = <count>
    last_checkpoint_iter = <current iter>

  IF (configured_max_iterations - current_iter) < (remaining_section_count * 20):
    EXIT_REASON = "ITERATION_BUDGET_EXHAUSTED"
    UPDATE _progress.json.status = "PARTIAL"
    Exit cleanly. A subsequent REPAIR can resume.

REPAIR validation: before SKIPping a "complete" section, verify its
WFF-SECTION:{name}:complete anchor exists in PLAN_SPEC_PATH. If absent
(stale status), demote to RESUME and re-author.
```

**Execution:** automated

---

### Step 2: Input Validation + Context Extraction

> **Before any discovery scan — apply execution-protocol.md Section 13 (Code-Location Discipline).** Read `context-pack/codebase-map.md` (and `project-inventory.md` if present) to locate each task's target site BEFORE running a repository-wide `grep`/`glob`/`find` to discover where it lives — **consult before scan, not never scan**. Read the specific files the map names directly; fall back to a scoped scan only where the map is absent or insufficient, and flag that gap in the plan's open-questions so the map can be corrected. Map first (§13), then delegate the residual sweep (§12).
>
> **During context extraction — apply execution-protocol.md Section 12 (Delegated Exploration) if your harness supports it.** Broad read-only sweeps for this skill (e.g. confirming the files named in the research spec still exist and locating each task's target site, diffing a branch when planning against in-flight work) MAY be delegated to a read-only exploration subagent on a cheap/fast model, which returns conclusions + `file:line` pointers (not file dumps). Plan sequencing, decisions, and all writing stay with this agent, which verifies any delegated `file:line` before using it (Zero-Invention still applies). With no subagent capability, explore inline under the usual scope constraint — output quality is identical either way.

```
## 2A. Validation Gate

IF SCOPE == TASK:
  Validate: task_id present, task_type valid, minimum 1 affected file
  Detect complexity: LOW (1 file), MEDIUM (2-5 files), HIGH (6+ files or cross-cutting)
ELSE:
  Validate: user_stories_path present, target_architecture present
  Detect complexity from story count and dependency depth

IF validation fails → write Gap Report → EXIT

## 2B. Context Extraction

Initialize SOURCE_LOG = []
Initialize REFERENCE_MAP = []

# Primary: research artifacts
Load research content → SOURCE_LOG → extract all requirements → REFERENCE_MAP
Extract artifact fidelity constraints → REFERENCE_MAP with tags such as:
  - exact identifiers/names
  - literals/constants/enums
  - contract/schema shapes
  - query/filter/order semantics
  - configuration keys and dependency declarations
  - file/path/location constraints

# Optional context enrichment
FOR EACH optional_path in [adr_path, domain_boundaries_path, source_path, context_pack_path]:
  IF exists: Read → SOURCE_LOG → extract relevant data → REFERENCE_MAP

# MANDATORY: Quality Criteria Extraction
IF quality_criteria_path is provided AND the file exists:
  READ quality_criteria_path in full.
  EXTRACT every item in the following categories and add to REFERENCE_MAP with tag QUALITY_CRITERIA:
    - Build tools, build commands, and wrapper/launcher scripts required
    - Test frameworks, test types, and test source set structure required
    - Code quality tools (linters, mutation testing, static analysis) and their configurations
    - Required folder structures and file naming conventions
    - Verification commands that must pass before submission
  For each extracted item, assign classification:
    REQUIRED: if the criteria document uses language like "must", "required", "shall", "MUST"
    OPTIONAL: if the criteria document uses "should", "recommended", "may"
  LOG: "Quality criteria extracted: {N} REQUIRED items, {M} OPTIONAL items"
ELSE IF quality_criteria_path is provided AND the file does NOT exist:
  LOG: "WARNING: quality_criteria_path provided but file not found at {path} — skipping quality criteria extraction"

# OPTIONAL: Functional Test-Case (FTC) Ingestion — authority on WHAT, not HOW
IF test_cases_path is provided AND a FTC-MANIFEST-*.md exists under it:
  READ the FTC manifest FIRST (it is ~120 lines and stays in context).
  From the manifest `tc_catalog`, build FTC_MAP and add to REFERENCE_MAP with tag TEST_CASES:
    FTC_MAP[tc_id] = { story_id, title, type (Positive/Negative/Boundary),
                       tag ([BE]/[FE]/[DATA]), priority (P0/P1/P2), ac_or_rule }
  SCOPE FILTER: keep only FTCs whose story_id is in the current plan's scope
    (match against the user stories / ACs already in REFERENCE_MAP). Record the
    excluded count; out-of-scope epics belong to other plan runs / feature_ids.
  Do NOT load individual `suites/epic-NN-func-tests.md` bodies yet — load a suite
    on demand only when a phase needs the exact Gherkin for a specific FTC, then
    flush it (Write-Flush-Forget; same discipline as loading one design image).
  ZERO INVENTION preserved: FTCs are evidence, not license — never invent an FTC
    id or alter an FTC's assertion. If a needed test has no FTC, derive it from
    ACs/research as before and mark its `test_case_id` as `[derived]`.
  LOG: "FTCs ingested: {N} in-scope test cases from {manifest}, {X} out-of-scope skipped"
ELSE IF test_cases_path is provided AND no manifest found:
  LOG: "WARNING: test_cases_path provided but no FTC-MANIFEST-*.md found at {path} — planning tests derived from ACs + research (legacy behavior)"

Detect language from research → DETECTED_LANGUAGE

## 2C. REPAIR Context
IF MODE == REPAIR:
  Parse PREVIOUS_SPEC sections → identify repair targets
  Apply REPAIR_DIRECTIVES to REFERENCE_MAP

## 2D. custom_message Processing
IF custom_message is not empty:
  Parse for:
  - Section focus directives → increase depth in named sections
  - Specific concerns → add to assumptions_to_validate if unresolvable
  - NEVER override validation rules or upstream consistency
  Log: "custom_message applied: {summary}"

## 2E. Pre-Applied Change Detection

Applies when research has identified a concrete change set with target files and
expected post-change markers. This is most common for TASK scope, but also
applies to any FULL_SDLC phase where a deterministic pre-applied comparison is
available. Skip open-ended work (refactoring, architectural changes) where the
comparison would require LLM judgment.

PROCEDURE:
  FOR EACH planned_change in REFERENCE_MAP (where target file + expected text are known):
    READ target_file at the planned location.
    COMPARE current content vs expected post-change content (semantic match — exact
      string for code constants, AST/structural match for refactors).
    RECORD result in PRE_APPLIED_MAP[file] = {APPLIED | PARTIAL | NOT_APPLIED}

  COMPUTE coverage:
    applied_ratio = count(APPLIED) / count(planned_changes)

  CLASSIFY:
    applied_ratio == 1.0  → plan_status: VERIFY_ONLY  (all changes already in code)
    0 < applied_ratio < 1 → plan_status: PARTIAL_APPLIED  (some changes pre-applied,
                            others still needed — list each)
    applied_ratio == 0    → plan_status: PROCEED  (normal flow)

  WRITE plan status and file-table evidence:
    plan_status: <VERIFY_ONLY | PARTIAL_APPLIED | PROCEED>
    implementation_required: <false for VERIFY_ONLY, true otherwise>
    For VERIFY_ONLY/PARTIAL_APPLIED, add a `pre_applied` column to each
    files_to_create/files_to_modify table row:
      - non-`none` value = evidence to verify before skipping that row
        (commit/hash + expected marker, existing path + expected marker, or
        passing test name)
      - `none` = this row still needs implementation

  LOG: "Pre-applied detection: {applied}/{total} changes already in code → {plan_status}"

LIMITATIONS:
  - Only runs when expected post-change content is concrete enough to compare.
  - For ambiguous changes (e.g., "improve error handling"), skip detection and use PROCEED.
  - Comparison must be deterministic (no LLM judgement) — string match or AST match only.
```
**Execution:** automated

### Step 3: Generate Agent-Native Spec

**FORBIDDEN FIELDS — Zero Invention Policy.**
This plan is consumed by `implementing-code` (an AI agent), not a human
delivery team. The spec MUST NOT include any of these human-PM fields:
`estimated_days`, `days`, `effort_hours`, `effort_days`, `sprints`, `weeks`,
`schedule`, `start_date`, `end_date`, `delivery_date`, `team_size`, `velocity`.
There is no signal in the upstream research artifacts to ground these values;
emitting them violates Zero Invention. Use `complexity` (LOW/MEDIUM/HIGH),
`files_touched`, `story_count`, and dependency ordering instead. Token, cost,
and month estimates belong to `estimating-token-budget` — never reproduce them
here, even on request via `custom_message`.

**EARLY-WRITE RULE — MANDATORY (silent-failure prevention).**
You MUST write a skeleton SPEC_FILE (`PLAN-SPEC-{SESSION_ID}.md`) with the
header metadata and section stubs within **5 tool calls** after entering Step 3
— counting ANY tool call (think, view, bash, edit). Each section stub is:

```
## {section_name}
<!-- WFF-SECTION:{section_name}:pending -->
status: pending - will be generated
```

Then populate sections with subsequent edits — exactly ONE section per `Edit`
call (single in-memory composition of the entire spec is the anti-pattern).

**Section-author loop (Write-Flush-Forget — see Entry Rule #6):**

```
FOR EACH section in plan_spec_section_catalog:
  1. status = _progress.json.sections[section.name].status
     IF status == "complete": SKIP (already authored — see Step 1.5).
  2. LOAD only this section's inputs (research extractions, phase fixtures).
     Do NOT re-read PLAN_SPEC_PATH.
  3. Compose section body in working memory — ONE in-flight body at a time.
  4. Single targeted Edit replacing `<!-- WFF-SECTION:{name}:pending -->`
     with body + `<!-- WFF-SECTION:{name}:complete -->`.
     (Anchor is non-empty, > 30 chars — passes §10.5.2 Safe-Write guard.)
  5. Update _progress.json: sections[name].status = "complete".
  6. FLUSH: discard body. Do not re-read PLAN_SPEC_PATH.
  7. Checkpoint: IF (cap - current_iter) < (remaining_sections * 20),
     mark _progress.json.status = "PARTIAL" and exit. REPAIR can resume.

FINAL VERIFICATION:
  ! grep "WFF-SECTION:.*:pending" PLAN_SPEC_PATH
  IF empty: _progress.json.status = "complete".
```

Step 3 → 3B → 4 all operate on the in-memory spec; without an early skeleton
write, a multi-minute thinking loop or context overflow during any of those
steps loses 100% of the work and leaves no recoverable state for REPAIR mode.
If you find yourself in a 3rd `think` block before the first SPEC_FILE write,
STOP and write the skeleton now, even if incomplete (mark missing pieces
`status: pending`). Update `_progress.json` after the skeleton write and after
each section is populated.

**READ** `references/code-task-planning-template.md` **NOW** for section structure.
**READ** `references/phase-decomposition-rules.md` **NOW** for TASK/FULL_SDLC phase
re-interpretation rules, TDAD per-phase Red-Green-Refactor sequencing, BUG_FIX
Prove-It sequencing, Status Protocol, Source Tagging, Anti-Fade Rule, and Quality
Criteria Integration requirements.

Generate the complete spec following the template. The template defines two
scope-specific section sets — generate ONLY the set matching the detected scope.

Every phase/task entry must preserve implementation-relevant upstream detail at
execution grade. If research specifies exact artifact behavior or structure,
translate it into explicit plan constraints, acceptance criteria, file targets,
verification steps, or open questions. Do not emit plans that weaken exact
source detail into generic intent when the downstream implementation depends on
the original structure.

**Scope-Adaptive Sections:**

| TASK Sections | FULL_SDLC Sections |
|--------------|-------------------|
| task_summary | plan_overview |
| scope | blocker_resolution (view over open_questions — see note below) |
| tech_stack | current_state |
| impact | desired_end_state |
| phases (1-3) | implementation_strategy |
| testing_strategy | phases (N, re-interpreted from research) |
| acceptance_criteria | cross_phase |
| | risks |
| | deployment |
| | acceptance_criteria |

**Header-level execution sections (both scopes):** required_artifacts, canonical_values, plan_status_semantics, security_decisions (required when the scope has a security surface — auth/authz, secret/credential handling, session/cookie issuance, privileged endpoints, sensitive-data persistence, or secret-bearing file/config writes; else emit the one-line "none" declaration)

**Shared sections (both scopes):** validation_summary, open_questions

**Generation Order:**
```
HEADER (always first)
  ↓
required_artifacts / canonical_values / plan_status_semantics / security_decisions
  ↓
scope-specific sections (in order listed above)
  ↓
validation_summary
  ↓
open_questions (always LAST)
```

Apply phase decomposition, status protocol, source tagging, anti-fade, and
quality-criteria-integration rules per `references/phase-decomposition-rules.md`.

Planning fidelity rules:
- preserve exact upstream identifiers, names, and artifact targets in phase steps
- preserve explicit behavioral constraints from source artifacts, including
  mappings, predicates, ordering, validation rules, and configuration semantics
- put cross-phase shared literals in `canonical_values`; every phase that uses
  one must list its `CV-XX` in `canonical_values_used`
- put external files the executor must read in `required_artifacts` with
  deterministic `phases_using`
- compute and preserve `research_fingerprint` as `sha256:<64 lowercase hex chars>`
  or `N/A`; `mtime:`, bare hashes, filenames, and session IDs are invalid. If it
  no longer matches `research_source` at execution launch, the harness must
  refuse execution and require re-planning unless an explicit stale-research
  override is supplied and logged to PLAN-AUDIT
- if `tdad_mode=true`, phase implementation steps must preserve Red-Green-Refactor
  ordering instead of smoothing it into generic implementation prose
- when exact upstream detail cannot be executed as-is, route it to
  `open_questions` with `phase_ref` and `fallback_behavior` for non-blocking gaps; do not silently rewrite it
- acceptance criteria must verify the preserved artifact behavior, not only a
  generalized business outcome
- when the work produces build/packaging outputs (compiled binaries, packages,
  bundles, container images, generated archives), the plan MUST declare the
  **expected output artifacts as explicit acceptance items** — their filenames
  (or filename patterns) and the directory they must land in — so implementation
  can verify their presence before completing. Keep these tech-agnostic in the
  plan; concrete per-project specifics (exact package names, build tooling)
  belong in the project context-pack, not invented here.

**Execution:** automated

### Step 3B: Automated Structural Validation (Pre-Consolidation Gate)

**READ** `references/structural-validation-rules.md` **NOW** for the SV-01…SV-10
checks. Run all checks BEFORE the consolidation pass. If any FAIL, fix inline
(max 2 self-correction attempts) before proceeding to Step 4.

**SV-FORBIDDEN-FIELDS check (HARD GATE — auto-fix mandatory):**
Scan the populated SPEC_FILE for any of the forbidden field names:
`estimated_days`, `\bdays\b` as a column header or list field,
`effort_hours`, `effort_days`, `sprints?`, `\bweeks?\b`, `schedule`,
`start_date`, `end_date`, `delivery_date`, `team_size`, `velocity`.
For each match, REMOVE the field/column from SPEC_FILE and log the deletion
to PLAN-AUDIT under `## Forbidden Fields Removed`. Do NOT replace with a
substitute estimate — `complexity` and `files_touched` already convey size.
Run this check as the LAST sub-check in Step 3B; if any field re-appears
after auto-fix, ABORT with a Gap Report.

**Gate:** If FLAGS > 0 after 2 self-correction attempts → document remaining
flags in PLAN-AUDIT under `## Structural Validation` and proceed to Step 4.
Do NOT block indefinitely.

**Execution:** automated

### Step 4: Consolidation Pass + Validation

**READ** `references/spec-validation-checklist.md` **NOW** for the 4A consolidation
pass (including the implementability override), V01…V20 validation checks, plus the
Common Rationalizations / Red Flags / Verification Checklist that must pass before exit.

Run consolidation pass + V01…V20. On FAIL → fix in place, log correction, re-run
consolidation (max 2 retries). Compute `quality_score = (PASS_count / 20) * 100`.
**V18 (CONTRADICTORY_PLAN_STATUS, REC-009):** a plan may not be PROCEED/CONDITIONAL
while any implementability-gating open question is unresolved — such targets are
blockers (→ `plan_status: BLOCKED`), not silently-deferred open questions.
**V19 (EXECUTION_SELF_CONTAINMENT):** implementation-relevant facts must be
literal in PLAN-SPEC or in a path listed in `required_artifacts`; never require
the executor to load RESEARCH-SPEC to recover executable details.
**V20 (RESEARCH_FINGERPRINT_SHA256):** `research_fingerprint` must be `N/A` or
`sha256:<64 lowercase hex chars>`. Any `mtime:` value is a validation failure.

Artifact fidelity validation is mandatory during consolidation: verify that the
plan still carries forward exact upstream artifact constraints needed for
implementation, testing, and verification. If a phase/task only preserves a
high-level summary where the source provided exact executable detail, fix the
plan before exit.

**Execution:** automated

### Step 5: Write Outputs

SPEC_FILE (`PLAN-SPEC-{SESSION_ID}.md`) is already on disk from the Step 3
EARLY-WRITE skeleton + per-section populate edits. Step 5 finalises:

1. Apply any remaining edits to SPEC_FILE so it reflects the final compact
   post-validation state (`validation_summary` + open_questions last). Full
   V01-V20 details go to PLAN-AUDIT, not PLAN-SPEC.
2. Write AUDIT_FILE (`PLAN-AUDIT-{SESSION_ID}.md`) for the first time here.
   AUDIT_FILE is NOT optional — a run that wrote PLAN-SPEC but no PLAN-AUDIT is
   incomplete, even if every SPEC section is `complete`.
3. **MANDATORY existence gate — do NOT skip.** Run:
   `ls {EFFECTIVE_PLANNING_OUTPUT_PATH}/PLAN-SPEC-*.md {EFFECTIVE_PLANNING_OUTPUT_PATH}/PLAN-AUDIT-*.md`
   Both must be listed and non-empty. If PLAN-AUDIT is missing, write it now and
   re-run the `ls`. You may NOT proceed to the LAST ACTION (mark `COMPLETED`) until
   this `ls` shows BOTH files. Marking `COMPLETED` with PLAN-AUDIT absent is a
   protocol violation (the documented "planning wrote SPEC but no AUDIT" defect).

SPEC_FILE includes: header metadata, header-level execution sections, all scope-appropriate sections from Step 3, validation_summary, and open_questions (always last).

AUDIT_FILE includes: session metadata, research input format, sources referenced, decisions made, custom_message_applied, full validation results (V01-V20 and SV-01-SV-10), quality score, summary counts, and (REPAIR-only) directives applied/sections preserved/regenerated.

Memory Bank artifact type: `"N tasks (M phases)"` (e.g., `"12 tasks (4 phases)"`).

**Memory Bank — MANDATORY session-end writes:**
1. Overwrite `context-pack/active-context.md` with session status, decisions, blockers, key artifacts.
   Log all planning decisions to the Decisions Log table (see execution-protocol.md Section 4 for schema).
2. Append one milestone row to `context-pack/progress.md` with artifact count above.

**Section 2 LAST ACTION — MANDATORY:** Only after the Step 5 existence gate has
confirmed BOTH `PLAN-SPEC-*.md` and `PLAN-AUDIT-*.md` exist and are non-empty,
update `_progress.json`: set `status` to `COMPLETED`, add `completed_at`, and set
`audit_written: true`. `status: COMPLETED` asserts that PLAN-AUDIT is on disk — do
NOT set it on the basis of SPEC sections alone. If PLAN-AUDIT is missing or the
session failed, set status to `FAILED` (or leave `PARTIAL`) — never `COMPLETED`.

**Execution:** automated

---

### Step 6: Emit Harness Outputs Sidecar

**Apply execution-protocol.md Section 11** — Harness Output Sidecar. Mandatory when the prompt contains a `## Run metadata` block. This is the FINAL file write of the run (after AUDIT/SPEC verification in Step 5, after Memory Bank, after `_progress.json` set to COMPLETED). Without it, the orchestrator records `outputs: {}`, and downstream steps receive a corrupted `planning_output_path` from the framework's `value_template` fallback (the template re-prepends `{{output_folder}}/{{project_name}}/{{feature_id}}/` on top of an already-absolute path, producing a doubly-nested folder).

**Output parameters this skill produces** (one key per row of the prompt's `## Output parameters` table):

- `planning_output_path`: the actual `EFFECTIVE_PLANNING_OUTPUT_PATH` written in Step 1 — the folder that holds `PLAN-SPEC-{SESSION_ID}.md`, `PLAN-AUDIT-{SESSION_ID}.md`, and `_progress.json`. If `feature_id` was empty and Step 1 followed a scoped `research_output_path`, report that nested sibling path here, not the flat `planning_output_path` parameter. Do NOT re-prepend `{output_folder}`, `{project_name}`, or `{feature_id}`.

**POST-WRITE ASSERTION** (execution-protocol.md §11.1.1, mandatory): before emitting the sidecar, run `ls {EFFECTIVE_PLANNING_OUTPUT_PATH}/PLAN-SPEC-*.md` and confirm the file is there. The value you report MUST be byte-identical to the directory that actually holds the PLAN-SPEC/PLAN-AUDIT you just wrote — never the flat `planning_output_path` parameter when Step 1 wrote to a scoped sibling. A mismatch here is the documented cause of the duplicate-folder defect: the next REPAIR run is handed the wrong folder and rebuilds a duplicate.

**Implementation:** the harness here accepts Bash heredoc for the sidecar write (the sidecar is NOT the SPEC_FILE, so §10.5's anti-Bash rule does not apply). Execute:

```
cat > {stepwise_outputs_file} << 'OUTPUTS_EOF'
{ "planning_output_path": "{EFFECTIVE_PLANNING_OUTPUT_PATH}" }
OUTPUTS_EOF
```

Replace `{EFFECTIVE_PLANNING_OUTPUT_PATH}` with the actual folder resolved in Step 1. `{stepwise_outputs_file}` is the path from the prompt's `## Run metadata` block's `output_file = '...'` line — copy it verbatim, do NOT reconstruct it.

Self-check: `cat {stepwise_outputs_file}` — verify non-empty. If empty or missing, re-execute. DO NOT describe output registration in response text — EXECUTE it. No tool calls after this; the next event is `final_response`.

**Execution:** automated

---

## REPAIR Mode
Triggered when `failure_feedback` is provided. Follow execution-protocol.md Section 7.
In summary: load existing PLAN-SPEC, apply directives to flagged sections only,
preserve all other sections verbatim, re-run validation (Step 4), increment version.

---

## Reference Files

| File | Load when | Purpose |
|------|-----------|---------|
| `references/code-task-planning-template.md` | Step 3 | PLAN-SPEC section structure (TASK + FULL_SDLC) |
| `references/phase-decomposition-rules.md` | Step 3 | TASK/FULL_SDLC phase rules, TDAD, Prove-It, Anti-Fade, Quality Criteria Integration |
| `references/structural-validation-rules.md` | Step 3B | SV-01…SV-10 pre-consolidation checks |
| `references/spec-validation-checklist.md` | Step 4 (and before exit) | Consolidation pass (incl. implementability override), V01…V20, Common Rationalizations, Red Flags, Verification Checklist |
| `context-pack/execution-protocol.md` | As referenced | Session ID, _progress.json lifecycle, Memory Bank, REPAIR Section 7 |
