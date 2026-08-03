---
name: reviewing-code
description: >
  Adversarial code review and quality gate validation. Verifies implementation
  against plan/research specs with extensible deterministic tooling. Reads
  agent-native PLAN-SPEC, RESEARCH-SPEC, and IMPL-STATE formats (with legacy
  fallback). Produces a single REVIEW-SPEC with structured findings,
  traceability, tool results, and repair feedback. Human-readable validation
  report via humanize-spec on demand.
license: Proprietary
metadata:
  author: aipods-team
  version: 4.1.0
  category: engineering
  tags: code-review, validation, quality-gate, adversarial-review, agent-native, fic-methodology, secure-defaults
  compatibility: Requires bash
---

# Reviewing Code — Agent-Native Adversarial Validation

## SKILL PROTOCOL — ENTRY RULES (read first, do not skip)

1. **The protocol below is internally consistent.** If you perceive a conflict
   between the capability prompt and this skill, the skill wins for execution
   mechanics; the capability wins for paths/parameters. Do NOT exit citing
   "ambiguity" or "internal contradiction" — every section here has been
   tested in production runs.

2. **Begin Step 1 (Initialize Session) immediately.** Do NOT re-evaluate the
   protocol's completeness before starting. Step 1's first action (write
   `_progress.json` to `validation_output_path`) IS the verification. If a
   required input is genuinely missing, you will discover it during the
   Pre-Flight gate and call `exec-fail` — not before.

3. **Reference files are loaded on demand via `cat`** when each step's
   `READ ... NOW` pointer says so. They are NOT preloaded into your context.
   The Reference Files table at the bottom of this file is a pointer index,
   not a checklist of files you must already have.

4. **Asking the human a clarifying question = task FAILURE.** The capability
   prompt makes this explicit. There is no human watching. Either execute, or
   call `stepwise session exec-fail --message "<reason>"`. Never end with
   "If you want, I will continue…" — that is a refusal.

5. **No final response until REVIEW-SPEC + REVIEW-AUDIT exist on disk.** The
   Pre-Flight and Output Existence gates (in `references/review-gates.md`)
   list exactly what must exist before you can emit a closing summary. Any
   final response without those files is a protocol violation and will be
   flagged as a fabricated run.

6. **Write-Flush-Forget — non-negotiable.** After writing the REVIEW-SPEC
   skeleton in Step 4, NEVER re-read the spec file in full. Authoring a
   finding/section is exactly four operations: (a) read `_progress.json`
   (small), (b) load section-specific Tier 2 inputs (the code under review,
   not the spec), (c) one targeted `Edit` replacing the section's
   `WFF-SECTION:{name}:pending` anchor with the section body, (d) update
   `_progress.json`. The agent's working memory holds at most ONE in-flight
   finding/section body at a time. The REVIEW-SPEC file is write-only after
   the skeleton is laid down.

   **Why:** repeated `view` of the working spec inflates prompt tokens
   geometrically with iteration count and breaks prompt-cache continuity.

   **Forbidden tool patterns inside the section-author loop:**
   - `view REVIEW_SPEC_PATH` (any kind) AFTER the skeleton is written. Read `_progress.json` instead.
   - `replace_all=true` on REVIEW-SPEC. Use targeted anchored Edits.
   - `bash wc -l REVIEW_SPEC_PATH` to "verify" progress. Placeholder anchor presence is the verification.

   **Permitted exceptions (must be explicitly justified in agent reasoning):**
   - At the very end of the run, ONE final grep to verify all placeholders are
     replaced (`! grep "WFF-SECTION:.*:pending" REVIEW_SPEC_PATH`).
   - On REPAIR: ONE initial bounded read (offset/limit, max 80 lines) around
     the affected section to confirm placeholder state.

---

## Quick Start
Verify implementation against plan + research specs. Assumes non-compliance and
requires evidence of correctness. Output is a **single REVIEW-SPEC** with all
findings, traceability, tool results, and actionable repair feedback.

## Known Failure Modes
<!-- ACCUMULATING — appended by calibrating-updates (WS6). Newest first. Rules MUST be generic/behavioral (project-agnostic); project-specific fixes go to context packs, never here. Format + entry rules: engineering-skills/references/known-failure-modes-format.md. Read these at pre-flight so a lesson learned once recurs no more. -->

- **KFM-001** (2026-07-22, source: forensic analysis of a mock-first per-sub-goal loop that never converged)
  - Symptom: When this skill runs as the review gate of a mock-first, per-sub-goal LOOP (e.g. the agentic-development graph/mcp/ux Verdict-Gated-Transition gates), the reviewer never reaches PASSED. It re-derives the SAME BLOCKING findings every lap — "a mock/resolver returns canned/fabricated data", "a later-scope stub is permissive", "acceptance criteria not met" — even though build, tests, and functional probes all pass. The gate exhausts its retry budget and escalates a FAILED verdict to the human every single iteration, who then approves manually. The implementation is not actually broken.
  - Root cause: Those findings are architecturally UNCLOSEABLE within the iteration's scope — the real resolver/persistence/downstream node is out-of-scope or belongs to a later iteration. The reviewer applied full-system, production acceptance criteria to a scoped, mock-mode iteration, so "the mock isn't the real thing" and "the not-yet-built stub is permissive" were scored BLOCKING and regenerated on every lap.
  - Rule (CONDITIONAL — mock-first mode only): When the calling step declares a mock-first iteration scope (an iteration scope AND a mock/contract artifact are both provided), classify findings against the current iteration's SCOPE and MODE — (1) a test double behaving as a test double (canned data, no production-grade semantic enforcement) is DEFERRED unless the mock contract explicitly requires the behavior OR the mock's interface/signature/output-schema drifts; (2) a permissive later-scope stub is a deferred wiring condition, not a scope-boundary violation; (3) an acceptance criterion satisfiable only by out-of-scope/production code is DEFERRED, not FAILED/PARTIAL. Block only on build/test failures, current-scope deliverable defects, mock-contract interface/schema drift, current-scope mis-routing, and regressions. ABSENT such a declaration (normal full-scope, real-code review — e.g. code-development capabilities), apply the full severity taxonomy UNCHANGED. This gate does NOT relax production code review.

## Anti-Patterns (do NOT)
<!-- ACCUMULATING — appended by calibrating-updates (WS6). One line each: **AP-NNN** (ISO-date, source: REC-NNN): prohibition — why. -->

- **AP-001** (2026-07-22, source: mock-first loop non-convergence): In a declared mock-first iteration, do NOT score "the mock returns canned data", "the mock doesn't enforce production semantics", or "a later-scope stub is permissive" as BLOCKING or verdict-reducing — they are uncloseable in-scope and cause an infinite implement→review(FAILED) loop that escalates a FAILED to the human every lap. Defer them unless the mock contract requires the behavior or the mock interface/schema drifts. (Does NOT apply to full-scope real-code review — there the full taxonomy stands.)

## Output Architecture

```
{validation_output_path}/
├── REVIEW-SPEC-{session_id}.md    ← Agent-native: all findings + traceability + tools + AC
└── REVIEW-AUDIT-{session_id}.md   ← Session metadata (sources, timeline)
```

**Why single spec file:** Consolidates the former validation report (markdown) +
feedback (JSON) + tracking entry into one agent-consumable file. Findings are
compact structured entries — even 50+ finding reviews fit in ~800 lines.

**Human-readable output:** Not produced by this skill. Use `humanize-spec` skill
to generate a rich validation report from this spec on demand.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project_name` | string | Yes | — | Project identifier |
| `plan_folder_path` | string | Yes | — | Path to plan folder (PLAN-SPEC or legacy phase docs) |
| `research_folder_path` | string | Yes | — | Path to research folder (RESEARCH-SPEC or legacy docs) |
| `progress_folder_path` | string | Yes | — | Path to implementation state (IMPL-STATE or legacy progress+audit) |
| `source_path` | string | Yes | — | Path to implemented source code root |
| `validation_tools` | object | No | — | Tool configurations (overrides auto-detected and context pack tools) |
| `validation_output_path` | string | No | `{progress_folder_path}` | Directory for REVIEW-SPEC output |
| `failure_feedback` | string | No | — | Specific issues to re-validate (triggers REPAIR mode) |
| `review_feedback` | string | No (output) | — | Structured one-line-per-finding summary for coordinator routing. Format: `[SEVERITY] [FILE] [DESCRIPTION]` per line. Empty when review passes. |
| `review_scope` | string | No | auto | `targeted` \| `full`. Default = `targeted` when scope_type is `bug-fixing` or `feature-impl` AND IMPL-STATE.total_files_modified ≤ 10; `full` otherwise. `targeted` limits review to changed files + their tests + their direct imports. `full` reads the entire planned phase scope. |

**If any Required parameter is not defined, ABORT EXECUTION.**

## Prerequisites

Before execution:
- [ ] Implementation phase completed (or partial for incremental review)
- [ ] Plan folder exists with PLAN-SPEC-*.md or legacy phase documents
- [ ] Research folder exists with RESEARCH-SPEC-*.md or legacy numbered docs
- [ ] Implementation state exists (IMPL-STATE-*.md or legacy impl-progress + impl-audit)
- [ ] Source code accessible at `source_path`

## Adversarial Review Principles

The six principles that govern every finding (Assume Non-Compliance, Seek
Discrepancies, Verify Completeness, Challenge Deviations, Trust Nothing, Trace
Everything) live in **`references/reviewing-principles.md`**. Read that file at
the start of Step 1 and keep its principles in scope for the entire session.

## Severity & Repair Feedback Quality

The BLOCKING / HIGH / MEDIUM / LOW classification and the actionable-feedback
rule (BEFORE/AFTER snippets, file:line, verification hint) live in
**`references/severity-taxonomy.md`**. Read that file at Step 2.

The enumerable **secure-default defect classes** (SD-01…SD-10 — fail-open auth,
plaintext/world-readable secrets, dev bypass reachable in prod, unprotected
privileged endpoints, non-durable audit logs) and their fixed severities live in
**`references/secure-defaults-taxonomy.md`**. Read that file at Step 4.7 and
apply its deterministic subset at Step 5.

## Tool Framework

Tool detection, configuration, context pack extension, and execution protocol
are defined in the reference file. **READ** `references/tool-execution-protocol.md`
when you reach Step 5.

Key points:
- If `validation-tools.md` exists in the context pack, it is the primary tool source
- Otherwise, tools are auto-detected from the project's tech stack (14+ languages supported)
- The `validation_tools` parameter provides session-level overrides
- Review runs ALL tool categories (build, test, lint, typecheck, security, coverage, complexity)

## Output Template

**READ** `references/code-review-template.md` when you reach Step 8.

The template defines the REVIEW-SPEC structure: header, summary, findings,
traceability, tool results, AC status, repair delta, and implementation_feedback.

**VERIFY_ONLY emission:** When SCOPE = VERIFY_ONLY (IMPL-STATE shows
total_files_modified=0 with valid pre-applied-fix deviation), emit a REVIEW-SPEC
with `overall_status: PASSED`, `blocking_count: 0`, `high_count: 0`, and a single
finding-class entry under `verification_only`:

  - id: VO-001
    type: pre-applied-verification
    file: <from IMPL-STATE deviation evidence>
    description: "Confirmed pre-applied fix per IMPL-STATE evidence"
    verification_command_result: <PASS | FAIL | SKIPPED>

If the pre-applied evidence in IMPL-STATE does NOT match the file content at review
time, emit `overall_status: FAILED`, `blocking_count: 1`, with a finding describing
the mismatch.

---

## Execution Protocol

### Step 1: Initialize Session

**READ** `references/review-gates.md` **NOW** for the Pre-Flight Validation gate.
Run all four checks in that file before initializing — abort if any fail.

**READ** `references/reviewing-principles.md` **NOW** to load the six adversarial
principles for the session.

```
INPUT:
  - plan_folder_path, research_folder_path, progress_folder_path, source_path
  - validation_tools, validation_output_path, failure_feedback

INITIALIZE tracking:
  SOURCE_LOG = []
  FINDING_LOG = []
  TOOL_RESULTS = []
  TRACEABILITY = []

## Scope re-anchor (feature_id-unset case — MANDATORY, apply BEFORE OUTPUT_DIR init and spec discovery):
##   The review artifacts and the IMPL-STATE they validate MUST live under the SAME
##   scope as plan_folder_path (its parent directory). When feature_id is unset,
##   upstream research/planning (and the re-anchored implementing-code) self-derive a
##   scope subfolder; reviewing-code must follow it or it will read/write from a flat,
##   empty folder — the split-artifact failure this rule prevents.
##   FOR each of progress_folder_path AND validation_output_path:
##     IF the path does NOT share plan_folder_path's parent directory
##        (e.g. flat {output_folder}/code-review-output while plan_folder_path is
##         scoped {output_folder}/{SCOPE}/code-task-planning):
##       RE-ANCHOR: path = dirname(plan_folder_path) + '/' + basename(path)
##       LOG deviation: "re-anchored {param} to plan scope {dirname(plan_folder_path)} — provided path was out of scope (feature_id unset)."
##   Skip a path that already shares plan_folder_path's parent. If plan_folder_path is
##   itself flat, do NOT re-anchor (no scope to recover). Use the re-anchored
##   progress_folder_path to locate IMPL-STATE and the re-anchored validation_output_path
##   as OUTPUT_DIR and the §11 sidecar review_output_path.

## SESSION_ID and OUTPUT_DIR initialization:
##   SESSION_ID is provided by the harness/execution metadata per execution-protocol.md §1.
##   OUTPUT_DIR = validation_output_path
##   REPAIR mode MUST reuse the existing session_id from the prior REVIEW-SPEC filename.

**FIRST ACTION — MANDATORY:** Write `_progress.json` to OUTPUT_DIR before any other file write.
This prevents the orchestrator from sending SIGINT.
WRITE OUTPUT_DIR + '/_progress.json':
  { "skill": "reviewing-code", "session_id": "initializing",
    "status": "RUNNING", "started_at": "<ISO timestamp>", "completed_at": null,
    "total": 0, "completed": 0, "items": [] }

## Multiple-spec tie-breaker — defines PICK_SPEC(folder, glob) used below.
##
## When two or more sessions have written to the same folder (concurrent runs,
## stale specs, missing feature_id scope), bare-glob "first match wins" is
## non-deterministic and risks reviewing the wrong feature. PICK_SPEC enforces
## a deterministic choice or fails fast.
##
## PICK_SPEC(folder, glob):
##   1. List all files in `folder` matching `glob`. Sort by mtime DESCENDING.
##   2. If no candidates → return null (caller falls through to legacy detect).
##   3. If exactly one candidate → return it. Log: "{glob} selection: {filename} (single)".
##   4. If >1 candidates:
##      a. Filter by SESSION_ID match: prefer files whose name contains the
##         current SESSION_ID's feature_slug component (or the Stepwise
##         session_name when feature_id is unset). Substring match is enough.
##      b. If exactly one passes the filter → return it. Log: "{glob} selection: {filename} (scope-matched, candidates={N})".
##      c. If none pass the filter → return the most-recently-modified.
##         Log: "{glob} selection: {filename} (mtime-fallback, candidates={N}, no scope match)".
##      d. If the top two candidates have mtimes within 1 second of each
##         other AND neither matches the scope filter → ABORT-with-guidance:
##           "Cannot disambiguate {glob} in {folder}. Two files were written
##            within 1s of each other and neither matches the current
##            feature_id/session_name. Re-run with feature_id set, or remove
##            the stale file. Aborting to prevent reviewing the wrong feature."
##         Call `stepwise session exec-fail` with this reason.

Dual-format detection for plan, research, and impl state:
  IF PICK_SPEC(plan_path, "PLAN-SPEC-*.md") returns a file:
    PLAN_FORMAT = "AGENT_NATIVE"
    PLAN_FILE   = chosen file path
  ELSE IF SCAN plan_path FOR "00-plan-index.md" finds a match:
    PLAN_FORMAT = "LEGACY"
  ELSE:
    ABORT: "No plan found — expected PLAN-SPEC-*.md or 00-plan-index.md"

  IF PICK_SPEC(research_output_path, "RESEARCH-SPEC-*.md") returns a file:
    RESEARCH_FORMAT = "AGENT_NATIVE"
    RESEARCH_FILE   = chosen file path
  ELSE IF SCAN research_output_path FOR numbered docs (e.g. "01-*.md") finds matches:
    RESEARCH_FORMAT = "LEGACY"
  ELSE:
    ABORT: "No research found — expected RESEARCH-SPEC-*.md or numbered docs"

  ## IMPL-STATE lives in progress_folder_path (the implementation artifact folder),
  ## which is a sibling of plan_folder_path after the Scope re-anchor above. Search
  ## it there first; fall back to validation_output_path only for legacy runs that
  ## colocated IMPL-STATE with the review output.
  IF PICK_SPEC(progress_folder_path, "IMPL-STATE-*.md") returns a file:
    IMPL_FORMAT = "AGENT_NATIVE"
    IMPL_FILE   = chosen file path
  ELSE IF PICK_SPEC(validation_output_path, "IMPL-STATE-*.md") returns a file:  # legacy colocated
    IMPL_FORMAT = "AGENT_NATIVE"
    IMPL_FILE   = chosen file path
  ELSE IF SCAN progress_folder_path FOR "impl-progress-*.md" finds a match:
    IMPL_FORMAT = "LEGACY"
  ELSE:
    ABORT: "No implementation state — expected IMPL-STATE-*.md or impl-progress-*.md in progress_folder_path"

## Cross-Artifact Scope Validation (mandatory after spec discovery, before review):
##
## Verify all three loaded artifacts (plan, research, IMPL-STATE) refer to the
## same feature/session. Without this check, the wrong-spec scenarios prevented
## by PICK_SPEC could still slip through if the user manually pre-staged
## inconsistent inputs.
##
##   PARAM_SCOPE    = feature_id (parameter) OR session_name (Stepwise) OR null
##   PLAN_SCOPE     = parse PLAN_FILE header for SESSION_ID / feature_id
##   RESEARCH_SCOPE = parse RESEARCH_FILE header for SESSION_ID / feature_id
##   IMPL_SCOPE     = parse IMPL_FILE header for SESSION_ID / feature_id
##
## IF PARAM_SCOPE is null:
##   LOG once: "WARNING: feature_id/session_name not provided. Cross-scope validation skipped."
##   Continue.
##
## IF any pair of (PLAN_SCOPE, RESEARCH_SCOPE, IMPL_SCOPE) is set and disagrees,
## OR if PARAM_SCOPE is set and disagrees with any of them:
##   ABORT-with-guidance via `stepwise session exec-fail`:
##     "Cross-artifact scope mismatch in code review.
##      param={PARAM_SCOPE}, plan={PLAN_SCOPE}, research={RESEARCH_SCOPE}, impl={IMPL_SCOPE}.
##      Reviewing inconsistent inputs would produce findings against the wrong artifact set.
##      Verify feature_id is correct and remove stale specs from the input folders."
##
## ELSE: LOG: "Scope validation passed. param/plan/research/impl all align with {PARAM_SCOPE}."

DETECT previous review:
  SCAN OUTPUT_DIR for REVIEW-SPEC-{session_id}*.md
  IF found: PREVIOUS_SPEC = most recent by version

DETECT mode:
  IF the prompt contains a `## Previous verification (lap N-1)` block:
    ## REVERIFY — automated Verdict-Gated-Transition loop re-review: implementation
    ## was re-made after this gate's prior FAILED verdict, and the harness threaded
    ## the prior review report + verdict into that block (verdict memory).
    MODE = "REVERIFY"
    PARSE the `## Previous verification (lap N-1)` block → PRIOR_VERDICT + PRIOR_FINDINGS.
      This block is the AUTHORITATIVE prior-report source for the repair_delta — use it
      even when no PREVIOUS_SPEC file is present in OUTPUT_DIR (the prior lap's folder
      may have been cleaned). If a PREVIOUS_SPEC file also exists, prefer the block.
    previous_version = version from the block (or PREVIOUS_SPEC, else "1.0.0")
    NEW_VERSION = increment_patch(previous_version)
  ELIF failure_feedback is not empty OR PREVIOUS_SPEC exists with status=FAILED:
    MODE = "REPAIR"
    LOAD PREVIOUS_SPEC → extract previous_version, previous_findings
    NEW_VERSION = increment_patch(previous_version)
  ELSE:
    MODE = "FRESH"
    NEW_VERSION = "1.0.0"

LOG: "Session initialized. Mode: {MODE}. Version: {NEW_VERSION}. Formats: plan={PLAN_FORMAT}, research={RESEARCH_FORMAT}, impl={IMPL_FORMAT}"
```

**If MODE == "REPAIR" or "REVERIFY": READ** `references/repair-mode.md` **NOW** for the
Review Consistency Rule, Fresh Review Spec Rule, REPAIR cycle scoping, and the
REVERIFY (VGT-loop verdict-memory) sub-section. REVERIFY runs the SAME full-scope
stable-checklist review as REPAIR — it differs only in where the prior report comes
from (the threaded block) and that its delta is stated against the prior lap's verdict.

**Execution:** automated

---

### Step 1.5: Resume from `_progress.json` (REPAIR support)

If `_progress.json` already exists at `OUTPUT_DIR`:

```
LOAD _progress.json.

IF _progress.json.status IN ["RUNNING", "PARTIAL"]:
  PARSE _progress.json.sections{} -> SECTION_STATUS
  FOR EACH section in review_spec_section_catalog:
    IF SECTION_STATUS[section.name] == "complete":
      MARK section as SKIP (already written; do NOT re-author)
    IF SECTION_STATUS[section.name] == "in_progress":
      MARK section as RESUME (re-author from scratch; previous attempt incomplete)
    IF SECTION_STATUS[section.name] == "pending":
      MARK section as DO

IF _progress.json.status == "complete":
  No work to do. Emit "review already complete" and exit.

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
WFF-SECTION:{name}:complete anchor exists in REVIEW_SPEC_PATH. If absent
(stale status), demote to RESUME and re-author.
```

**Execution:** automated

---

### Step 2: Load Verification Context

> **Before any discovery scan — apply execution-protocol.md Section 13 (Code-Location Discipline).** Read `context-pack/codebase-map.md` (and `project-inventory.md` if present) to locate the changed files' consumers and the modules they touch BEFORE running a repository-wide `grep`/`glob`/`find` to discover where they live — **consult before scan, not never scan**. Read the specific files the map names directly; fall back to a scoped scan only where the map is absent or insufficient, and flag that gap in your output so the map can be corrected. Map first (§13), then delegate the residual sweep (§12).
>
> **While loading verification context — apply execution-protocol.md Section 12 (Delegated Exploration) if your harness supports it.** Broad read-only sweeps for this skill (e.g. diffing the branch / PR under review against its base, enumerating changed files and their consumers) MAY be delegated to a read-only exploration subagent on a cheap/fast model, which returns conclusions + `file:line` pointers (not file dumps). The review judgment, severity calls, and all writing stay with this agent, which verifies any delegated `file:line` before flagging it (Zero-Invention still applies). With no subagent capability, gather the diff inline under the usual scope constraint — output quality is identical either way.

**READ** `references/severity-taxonomy.md` **NOW** for severity definitions
used throughout this and later steps.

```
LOAD plan:
  IF PLAN_FORMAT == "AGENT_NATIVE":
    READ PLAN_FILE → APPEND to SOURCE_LOG
    EXTRACT: phases[], stories per phase, files per story, patterns, AC
  ELSE (LEGACY):
    READ plan index → APPEND to SOURCE_LOG
    FOR each phase_document in index:
      READ phase doc → APPEND to SOURCE_LOG
      EXTRACT: phase ID, stories, files to create/modify, patterns, testing strategy
    READ acceptance criteria doc → APPEND to SOURCE_LOG

LOAD research constraints:
  IF RESEARCH_FORMAT == "AGENT_NATIVE":
    READ RESEARCH_FILE → APPEND to SOURCE_LOG
    EXTRACT: ADR decisions, landmines, NFRs, tech constraints, security reqs
  ELSE (LEGACY):
    READ research index → APPEND to SOURCE_LOG
    EXTRACT same data from numbered documents

  IF research defines validation_tools:
    MERGE with parameter validation_tools (parameter wins conflicts)

LOAD implementation artifacts FIRST (before plan/research):
  IF IMPL_FORMAT == "AGENT_NATIVE":
    READ IMPL_FILE → APPEND to SOURCE_LOG
    EXTRACT: phase status, files touched, tests created, deviations, blockers,
             total_files_modified, status (e.g. ALREADY_VERIFIED)
  ELSE (LEGACY):
    READ impl-progress file → APPEND to SOURCE_LOG
    READ impl-audit file → APPEND to SOURCE_LOG
    EXTRACT same data from legacy format

  IMPL_STATE_SUMMARY = {
    files_touched: [...],
    total_files_modified: <int>,
    status: <NORMAL | ALREADY_VERIFIED>,
  }
  LOG: "IMPL-STATE: {total_files_modified} files modified, status={status}"

BUILD verification scope (review_scope-aware):
  PARSE failure_feedback for specific phases/files (if provided)
  IF MODE == "REVERIFY": derive the prior-finding files from PRIOR_FINDINGS (parsed
    from the `## Previous verification (lap N-1)` block) — there is no failure_feedback
    on a VGT gate re-run; the block is the equivalent input.
  REPAIR_FOCUS = files mentioned in feedback (REPAIR) or PRIOR_FINDINGS files (REVERIFY),
                 plus this lap's IMPL-STATE modified files + their dependencies; null in FRESH.
  ## REPAIR_FOCUS narrows the first load set and report priority. It does NOT
  ## narrow the verification categories: every category used in the prior lap is
  ## evaluated again. In REPAIR/REVERIFY, load prior validation report +
  ## current IMPL-STATE + REPAIR_FOCUS files/tests/direct deps first; expand to
  ## full plan/research/source only when a required check cannot be answered
  ## from that evidence.

  RESOLVE review_scope (from parameter, with auto-default):
    IF parameter review_scope is set: USE it
    ELSE IF scope_type IN {"bug-fixing", "feature-impl"} AND total_files_modified <= 10:
      review_scope = "targeted"
    ELSE:
      review_scope = "full"

  IF IMPL_STATE_SUMMARY.status == "ALREADY_VERIFIED" OR total_files_modified == 0:
    SCOPE = "VERIFY_ONLY"
    LOG: "No code changes per IMPL-STATE — verification-only review (no file scan)."
    # In VERIFY_ONLY, the review reads:
    #   - IMPL-STATE deviation reasons (must be 'pre-applied-fix' or similar valid)
    #   - The verification command result from IMPL-STATE
    # The review writes a REVIEW-SPEC with overall_status=PASSED, blocking_count=0,
    # high_count=0, and a single finding-class entry: VERIFICATION_ONLY confirming
    # the pre-applied-fix evidence. No file-level review is performed.
  ELSE IF review_scope == "targeted":
    SCOPE = files_touched + their direct test files + the files they import
    # Direct test files: same package, *Test.kt / *Spec.ts / test_*.py etc.
    # Direct imports: parsed from each touched file's import block (depth=1).
    # NEVER expand to other phases or unrelated files in targeted mode.
    LOG: "TARGETED review: {len(SCOPE)} files (changed + tests + direct imports)."
  ELSE:  # full
    SCOPE = all phases
    IF MODE IN {"REPAIR", "REVERIFY"}:
      LOG: "Full-checklist repair review. Initial load set: prior report + IMPL-STATE + REPAIR_FOCUS; expand only on evidence gaps."

  IF scope_type == "bug-fixing" AND MODE IN {"REPAIR", "REVERIFY"}:
    SCOPE = INTERSECT(SCOPE, REPAIR_FOCUS)  # never widen on repair/reverify

LOG: "Context loaded. Phases in scope: {count}. Files to verify: {count}."
```

**Execution:** automated

---

### Step 3: Build Traceability Matrix

```
FOR each phase in SCOPE:
  FOR each user_story in phase.stories:
    CREATE traceability entry:
      {
        story_id, story_description, phase,
        expected_files: [list],
        found_files: [],
        expected_tests: [list],
        found_tests: [],
        expected_patterns: [list],
        patterns_verified: [],
        acceptance_criteria: [mapped ACs],
        ac_status: [],
        status: "PENDING"
      }
    APPEND to TRACEABILITY

FOR each acceptance_criterion:
  LINK to corresponding traceability entries by phase/story mapping

LOG: "Traceability matrix built. Stories: {count}. Criteria: {count}."
```

**Execution:** automated

---

### Step 4: Adversarial Code Review

**EARLY-WRITE RULE — MANDATORY (silent-failure prevention).**
Within **5 tool calls** of entering Step 4 — counting ANY tool call — you MUST
write a skeleton REVIEW-SPEC file to disk with header metadata and findings
section stubs. Then append individual findings to the file as they are
identified, rather than accumulating all findings in memory. Multi-minute
thinking loops with no on-disk progress trigger orchestrator SIGINT or context
overflow and lose 100% of the work. Update `_progress.json` after the skeleton
write and after each finding is committed.

**READ** `references/findings-classification.md` **NOW** for the ADR Binding
Protocol, Functional Equivalence Check, and MTP Tool Classification rules.
These govern how findings in this step are classified.

> **Parallel fan-out — DISPATCH DECISION (execution-protocol.md Section 14). Decide BEFORE reviewing files.**
> - **IF the harness can dispatch multiple workers in a single turn — concurrent foreground workers alone qualify; background/detached tasks are NOT required, and an absent `Parallel delegation:` advertisement does NOT force inline (execution-protocol.md §14 Applicability) — AND there are >= 3 files in SCOPE → fan out BY DEFAULT.** Dispatch one worker per changed file (or diff-hunk group), **emitting all file workers in ONE turn (§14.3 step 2) — one-worker-per-turn serializes them**; do NOT fall back to the sequential loop. Each worker reviews ONLY its own file (against that file's plan spec + direct imports/tests) and returns a compact per-file `FINDING_LOG` (findings with `file:line` + severity). **Workers NEVER write the REVIEW-SPEC, `_progress.json`, or the §11 sidecar, and never decide the overall verdict.**
> - **ELSE (the harness is genuinely single-dispatch, or < 3 files) → run the inline per-file loop below.**
>
> Independence proof: each file is reviewed against its own plan spec + direct imports/tests; a file's findings do not depend on another file's findings — cross-file concerns (shared contracts, wiring) stay with YOU in Step 6B goal-backward verification. Merge contract (coordinator, serial): collect each worker's per-file findings, then YOU **dedupe** overlapping findings, classify severity per `findings-classification.md`, write them into the single REVIEW-SPEC (the EARLY-WRITE skeleton is yours, not a worker's), and compute `blocking_count` / `high_count` / `review_status`. This does NOT narrow review scope — the Stable-Checklist rule still applies (every file in SCOPE is reviewed); fan-out only parallelizes WHO reviews each file. Findings and verdict are IDENTICAL whether you fanned out or ran inline. Verify any worker-reported `file:line` before it enters a finding (Zero-Invention).

```
### 4.1 File Existence Verification
FOR each phase in SCOPE:
  FOR each expected_file in phase.files_to_create:
    CHECK: Does file exist at {source_path}/{expected_file.path}?
    IF exists:
      READ file content → APPEND to SOURCE_LOG
      UPDATE traceability: found_files += expected_file
      VERIFY content:
        - Contains expected exports/classes/functions?
        - Follows specified patterns?
        - Includes required error handling?
        - Matches interface contracts from plan?
      FOR each verification:
        IF passed: ADD to FINDING_LOG: { type: "PASS", file, check, evidence }
        ELSE: ADD to FINDING_LOG: { type: "FAIL", severity: "BLOCKING", file, check, expected, actual }
    ELSE:
      ADD to FINDING_LOG: {
        type: "FAIL", severity: "BLOCKING", category: "MISSING_FILE",
        file: expected_file.path,
        expected: "File should exist per plan Phase {phase.id}",
        actual: "File not found"
      }
      UPDATE traceability: status = "FAIL"

  FOR each expected_file in phase.files_to_modify:
    CHECK: Does file exist?
    IF exists:
      READ file content → APPEND to SOURCE_LOG
      VERIFY modifications:
        - Changes specified in plan present?
        - Original functionality preserved?
        - No unintended side effects?
      Document findings
    ELSE:
      ADD to FINDING_LOG: {
        type: "FAIL", severity: "BLOCKING", category: "MISSING_FILE",
        description: "File to modify does not exist"
      }

### 4.2 Test Existence and Quality Verification
FOR each phase in SCOPE:
  FOR each expected_test in phase.testing_strategy.test_files:
    CHECK: Does test file exist?
    IF exists:
      READ test file content → APPEND to SOURCE_LOG
      UPDATE traceability: found_tests += expected_test
      VERIFY test quality (adversarial):
        - Tests actual functionality, not just existence?
        - Covers happy path?
        - Covers edge cases from plan?
        - Covers failure modes from research?
        - Assertions are meaningful (not just "expect(true)")?
        - Test names describe behavior?
      FOR each quality concern found:
        ADD to FINDING_LOG: {
          type: "FAIL", severity: "HIGH", category: "TEST_QUALITY",
          file: test_file, description: concern
        }
    ELSE:
      ADD to FINDING_LOG: {
        type: "FAIL", severity: "BLOCKING", category: "MISSING_TEST",
        expected: expected_test.path, actual: "Test file not found"
      }

### 4.3 Pattern and Architecture Verification
FOR each phase in SCOPE:
  FOR each required_pattern in phase.patterns:
    SCAN relevant files for pattern usage
    IF pattern found and correctly applied:
      ADD to FINDING_LOG: { type: "PASS", category: "PATTERN", pattern, evidence }
    ELSE IF pattern found but incorrectly applied:
      ADD to FINDING_LOG: {
        type: "FAIL", severity: "HIGH", category: "PATTERN_VIOLATION",
        pattern: required_pattern, description: "Pattern used incorrectly",
        evidence: specific_code_reference
      }
    ELSE:
      ADD to FINDING_LOG: {
        type: "FAIL", severity: "HIGH", category: "PATTERN_MISSING",
        pattern: required_pattern, description: "Required pattern not found"
      }

### 4.4 Research Constraint Verification
# Apply ADR Binding Protocol from references/findings-classification.md
FOR each adr_decision in research.adrs:
  DETERMINE binding status:
    IF adr_decision is BINDING:
      VERIFY implementation respects decision
      IF violation found:
        ADD to FINDING_LOG: {
          type: "FAIL", severity: "BLOCKING", category: "ADR_VIOLATION",
          adr: adr_decision.id, description: "Implementation violates BINDING ADR decision",
          evidence: specific_violation
        }
    ELIF adr_decision is ADVISORY:
      IF deviation found AND not documented in IMPL_INDEX.deviations:
        ADD to FINDING_LOG: {
          type: "WARN", severity: "HIGH", category: "ADR_DEVIATION_UNDOCUMENTED",
          adr: adr_decision.id, description: "Advisory ADR deviation not documented as accepted derogation",
          evidence: specific_deviation
        }

FOR each landmine in research.landmines:
  VERIFY implementation avoids landmine
  IF landmine triggered:
    ADD to FINDING_LOG: {
      type: "FAIL", severity: "BLOCKING", category: "LANDMINE_TRIGGERED",
      landmine: landmine.description, evidence: where_triggered
    }

FOR each nfr in research.nfrs:
  VERIFY implementation addresses NFR (where verifiable)
  Document findings

### 4.5 Deviation Verification
# Apply Functional Equivalence Check from references/findings-classification.md
# before marking any plan deviation as HIGH or BLOCKING.
COMPARE documented deviations vs actual deviations found:

FOR each deviation in impl_state.deviations:
  VERIFY:
    - Deviation actually exists in code?
    - Justification is reasonable?
    - Impact assessment is accurate?
  IF justified:
    ADD to FINDING_LOG: { type: "DEVIATION_ACCEPTED", description, justification }
  ELSE:
    ADD to FINDING_LOG: {
      type: "FAIL", severity: "HIGH", category: "UNJUSTIFIED_DEVIATION",
      description: deviation, reason: "Justification insufficient"
    }

FOR each undocumented deviation found:
  ADD to FINDING_LOG: {
    type: "FAIL", severity: "BLOCKING", category: "UNDOCUMENTED_DEVIATION",
    description: "Implementation deviates from plan without documentation",
    expected: plan_specification, actual: implementation_found
  }

### 4.6 Retrospective Verification
IF IMPL_FORMAT == "AGENT_NATIVE":
  # Agent-native: check IMPL-STATE execution_log and validations for completeness
  FOR each phase in SCOPE:
    IF phase has no execution_log entries or validation records:
      ADD to FINDING_LOG: {
        type: "FAIL", severity: "MEDIUM", category: "INCOMPLETE_EXECUTION_LOG",
        phase: phase.id, description: "Phase execution log or validations missing in IMPL-STATE"
      }
    IF IMPL-STATE deviations for phase != deviations found in code review:
      ADD to FINDING_LOG: {
        type: "FAIL", severity: "HIGH", category: "STATE_MISMATCH",
        description: "IMPL-STATE deviations don't match actual code deviations"
      }
ELSE (LEGACY):
  FOR each phase in SCOPE:
    READ phase document retrospective section
    IF retrospective is empty or contains only template placeholders:
      ADD to FINDING_LOG: {
        type: "FAIL", severity: "MEDIUM", category: "INCOMPLETE_RETROSPECTIVE",
        phase: phase.id, description: "Phase retrospective not filled"
      }
    IF retrospective.deviations != impl_progress.deviations for phase:
      ADD to FINDING_LOG: {
        type: "FAIL", severity: "HIGH", category: "RETROSPECTIVE_MISMATCH",
        description: "Retrospective deviations don't match progress file"
      }

LOG: "Adversarial review complete. Findings: {count}."
```

### 4.7 Secure-Default Verification

**READ** `references/secure-defaults-taxonomy.md` **NOW.** Apply it to every
review — secure-default defects (auth that fails open, secrets written in the
clear or world-readable, dev bypasses reachable in production, unprotected
privileged endpoints, in-memory audit logs that claim durability) are the
recurring failure class in generated code, and each is a fixed-severity finding.

```
DETERMINE the security surface of SCOPE (auth/authz, secret/credential handling,
  session/cookie issuance, privileged/admin endpoints, persistence of sensitive
  data, or file/config writes a secret flows into).
IF no security surface: LOG "no security surface in scope" and skip (do not invent).
ELSE FOR each class SD-01..SD-10:
  run the class signal, CONFIRM each candidate against the code, and on a
  confirmed defect ADD to FINDING_LOG with severity = the class's FIXED severity
  (SD-01..SD-06 BLOCKING, SD-07..SD-10 HIGH) and category SECURE_DEFAULT_<SD-id>,
  including BEFORE/AFTER/verification-hint feedback (AFTER shows the fail-closed
  / owner-only-permission / durable-sink form).
NEVER downgrade a secure-default finding on a "dev only / mock / temporary /
  installer sets it / already noted in a comment" rationalization — insecure
  defaults ship.
```

**Execution:** automated

---

### Step 5: Execute Deterministic Tools

**READ** `references/tool-execution-protocol.md` **NOW.**

Execute all tool categories (build, test, lint, typecheck, security, coverage, complexity)
following the detection, merge, and execution protocol defined in the reference.
For tool blocking-status decisions, apply the MTP Tool Classification Honor Protocol
from `references/findings-classification.md`.

**Secure-default deterministic subset (security category).** When SCOPE has a
security surface, also run the **exactly-checkable** signals from
`references/secure-defaults-taxonomy.md` (SD-01, SD-02 public-path helper, SD-03,
SD-05, SD-06 gitignore coverage, SD-07 cookie flags) as security-category checks.
These are grep/AST facts, so run them mechanically here — a signal fires
regardless of any "fine for dev" narrative; confirm each hit and classify it at
its fixed severity. This makes the greppable secure-default defects immune to
rationalization, independent of whether the context pack supplied a
`validation-tools.md` security entry.

Append results to TOOL_RESULTS and findings to FINDING_LOG per the reference protocol.

**Execution:** automated

---

### Step 6: Verify Acceptance Criteria

```
FOR each acceptance_criterion:
  DETERMINE verification method:
    IF criterion.verification_type == "automated":
      EXECUTE criterion.verification_command
      status = PASS if passes, FAIL if fails
    ELSE IF criterion.verification_type == "code_inspection":
      LOCATE relevant code in source_path
      CHECK for required elements per criterion
      status = PASS if found, FAIL if not
    ELSE:
      status = "MANUAL_REQUIRED"
      manual_steps = criterion.verification_steps

  UPDATE traceability: linked entries ac_status += { criterion_id, status, evidence }

  ADD to FINDING_LOG:
    IF FAIL: { type: "FAIL", severity: "BLOCKING", category: "ACCEPTANCE_CRITERIA", criterion_id, description, expected, actual }
    IF PASS: { type: "PASS", category: "ACCEPTANCE_CRITERIA", criterion_id, evidence }
    IF MANUAL: { type: "MANUAL", category: "ACCEPTANCE_CRITERIA", criterion_id, verification_steps }

COMPILE AC summary: total, passed, failed, manual

LOG: "AC verification complete. Passed: {passed}/{total}. Failed: {failed}. Manual: {manual}."
```

**Execution:** automated

---

### Step 6B: Goal-Backward Wiring Verification

For each NEW file in IMPL-STATE files_touched (action = CREATE):

```
Level 1 — Artifact Exists:
  - File exists at declared path → PASS
  - File missing → BLOCKING finding

Level 2 — Substantive (not stub):
  - File has >10 lines of non-comment code → PASS
  - File is empty, placeholder, or TODO-only → HIGH finding

Level 3 — Wired (imported and used):
  - Grep codebase for import/require/include of the new file
  - At least ONE other file imports or references it → PASS
  - Zero imports found → HIGH finding: "Orphaned file — created but never imported"
  - Exceptions: entry points (main.js, index.html, App.*, **/test/**) are exempt

Level 4 — Data-Flow Trace (API/service files only):
  - If file defines an API endpoint or service method:
    - Verify it is registered in the router/app config
    - Verify at least one call site passes real data (not hardcoded empty)
  - Disconnected endpoint → MEDIUM finding

**Output format** — populate this table in the REVIEW-SPEC under `## wiring_verification`:

| file | level_1_exists | level_2_substantive | level_3_wired | level_4_dataflow | verdict |
|------|---------------|---------------------|---------------|-----------------|---------|

One row per NEW file (action = CREATE in files_touched).
- level_1: PASS / MISSING
- level_2: PASS / STUB (lines < 10 or TODO-only)
- level_3: PASS / ORPHANED (zero imports found) — exempt: entry points, test files
- level_4: PASS / DISCONNECTED / N/A (only for API/service files)
- verdict: PASS / HIGH / BLOCKING

Then compile:
  wiring_score = (PASS_verdict_count / total_rows) * 100

Add wiring_score to the composite quality score under Architecture Integrity (20%).
A file that exists + passes tests but is never imported scores 0 on wiring —
this catches "tests pass but feature is disconnected from the application" failures.
```

**Execution:** automated

---

### Step 7: Compile Repair Comparison (REPAIR Mode Only)

```
IF MODE != "REPAIR": SKIP this step

LOAD previous findings from PREVIOUS_SPEC

FOR each previous_finding where type == "FAIL":
  SEARCH current FINDING_LOG for match (same category + file/location + description)
  IF match found AND current type == "FAIL": delta = "STILL_FAILING"
  ELSE: delta = "FIXED"

FOR each current_finding where type == "FAIL":
  IF no match in previous findings: delta = "REGRESSION"

COMPILE repair summary:
  fixed_count, still_failing_count, regression_count

LOG: "Repair analysis complete. Fixed: {fixed_count}. Still failing: {still_failing_count}. Regressions: {regression_count}."
```

**Execution:** automated

---

### Step 8: Generate REVIEW-SPEC

**READ** `references/quality-assurance.md` **NOW** for Common Rationalizations,
Red Flags, and the Verification Checklist. Apply each item before writing the
spec — these catch superficial reviews before they ship.

```
CALCULATE statistics:
  blocking_issues = FINDING_LOG where severity == "BLOCKING"
  high_issues = FINDING_LOG where severity == "HIGH"
  medium_issues = FINDING_LOG where severity == "MEDIUM"
  low_issues = FINDING_LOG where severity == "LOW"

  overall_status:
    IF count(blocking_issues) > 0: "FAILED"
    ELSE IF count(high_issues) > 0: "PARTIAL"
    ELSE: "PASSED"

## Quantitative Quality Score — FAR/FACTS Matrix

After completing all review checks, compute a numeric quality score:

| Dimension | Weight | Scoring (0-10) | Criteria |
|-----------|--------|-----------------|----------|
| Plan Adherence | 25% | 10=exact match, 5=minor deviations, 0=major drift | Files, interfaces, patterns match PLAN-SPEC |
| Code Correctness | 25% | 10=all checks pass, 5=minor issues, 0=critical bugs | Build, tests, type-checks, lint |
| Architecture Integrity | 20% | 10=clean patterns, 5=acceptable shortcuts, 0=violations | ADR compliance, dependency direction, coupling |
| Test Coverage | 15% | 10=all AC covered, 5=partial coverage, 0=missing tests | AC→test traceability, edge cases |
| Security & Safety | 15% | 10=no findings, 5=low-severity, 0=critical vulnerabilities | OWASP top 10, injection, auth, data exposure |

COMPOSITE_SCORE = weighted sum (0-10 scale)
QUALITY_GATE = PASS if COMPOSITE_SCORE >= 7.0, CONDITIONAL if >= 5.0, FAIL if < 5.0

Include composite_score, per-dimension scores, and quality_gate verdict in the review output.

READ references/code-review-template.md NOW

**Skeleton-first authoring (Write-Flush-Forget — see Entry Rule #6):**

```
PHASE A — Write SPEC_FILE skeleton ONCE (within 5 tool calls of entering Step 8):
  - Header metadata
  - For each section in template (Summary, Findings, Traceability, Tool Results,
    AC Status, Repair Delta, Research Compliance, Deviation Analysis):
      ## {section_name}
      <!-- WFF-SECTION:{section_name}:pending -->
  - Update _progress.json: skeleton_written = true.

PHASE B — Section-author loop (one section per Edit):
  FOR EACH section in review_spec_section_catalog:
    1. status = _progress.json.sections[section.name].status
       IF status == "complete": SKIP.
    2. LOAD only this section's inputs (FINDING_LOG slice for severity sections,
       TRACE_MATRIX for traceability, TOOL_RESULTS for tool status). Do NOT
       re-read SPEC_FILE.
    3. Compose section body in working memory — ONE in-flight body at a time.
    4. Single targeted Edit replacing `<!-- WFF-SECTION:{name}:pending -->`
       with body + `<!-- WFF-SECTION:{name}:complete -->`.
    5. Update _progress.json: sections[name].status = "complete".
    6. FLUSH: discard body. Do not re-read SPEC_FILE.
    7. Checkpoint: IF (cap - current_iter) < (remaining_sections * 20),
       mark _progress.json.status = "PARTIAL" and exit. REPAIR can resume.

FINAL VERIFICATION:
  ! grep "WFF-SECTION:.*:pending" SPEC_FILE
  IF empty: _progress.json.status = "complete".
```

Use the template structure below for the section list:
  - Header: session_id, version, mode, status, timestamp, source formats
  - Summary: counts for each severity, tools executed/passed, AC passed/total
  - Findings: all entries from FINDING_LOG grouped by severity
    Each finding includes: id, category, phase, file, line_range, description,
    expected, actual, fix_instruction, evidence
    BLOCKING/HIGH findings include: before_snippet, after_snippet, verification_hint
  - Traceability: story → files → tests → patterns → AC mapping
  - Tool Results: per-tool status, command, summary, issues
  - AC Status: per-criterion result with evidence
  - Repair Delta (REPAIR/REVERIFY mode): FIXED, STILL_FAILING, REGRESSION entries. In REVERIFY, the delta is stated against the prior lap's verdict from the `## Previous verification (lap N-1)` block (e.g. "3 blocking findings fixed, 0 regressions, 1 still failing").
  - Research Compliance: ADR status, landmine status
  - Deviation Analysis: documented vs undocumented

GENERATE implementation_feedback string:
  IF overall_status == "FAILED" OR overall_status == "PARTIAL":
    COMPILE feedback with BEFORE/AFTER snippets per REPAIR Feedback Quality Rule
    (see references/severity-taxonomy.md):
      "Review v{NEW_VERSION} found {blocking_count} blocking issues:\n"
      FOR each blocking issue (max 5):
        "- [{id}] {category} in {file}:{line_range}\n"
        "  Problem: {description}\n"
        "  BEFORE (current code):\n```\n{current_code_snippet}\n```\n"
        "  AFTER (required fix):\n```\n{fix_code_snippet}\n```\n"
        "  Verify: {verification_command or 'Manual check — re-read file after edit'}\n"
      FOR each high issue (max 3):
        "- [{id}] HIGH in {file}:{line_range}: {description}\n"
        "  Fix: {fix_instruction}\n"
    SET implementation_feedback = compiled string
```

**Execution:** automated

---

### Step 9: Write Outputs

**Apply Output Existence Validation** from `references/review-gates.md` —
verify both files exist on disk before proceeding to Step 10.

```
WRITE SPEC_FILE (REVIEW-SPEC) — completed in Step 8

WRITE AUDIT_FILE (REVIEW-AUDIT):
  session_id, version, mode, timestamp
  source_formats: plan={PLAN_FORMAT}, research={RESEARCH_FORMAT}, impl={IMPL_FORMAT}
  SOURCE_LOG entries (file, role, timestamp)
  Review timeline (start, context_loaded, review_complete, tools_complete, report_generated)
  Tool registry used (merged from all sources)

VERIFY files exist:
  IF SPEC_FILE missing: ERROR
  IF AUDIT_FILE missing: ERROR

LOG: "Outputs written. SPEC: {SPEC_FILE}. AUDIT: {AUDIT_FILE}."
```

**Execution:** automated

---

### Step 10: Deliver and Recommend

```
GENERATE review_feedback output parameter:
  IF overall_status != "PASSED":
    review_feedback_lines = []
    FOR each issue in blocking_issues:
      APPEND: "[BLOCKING] [{issue.file}] {issue.description}"
    FOR each issue in high_issues:
      APPEND: "[HIGH] [{issue.file}] {issue.description}"
    SET review_feedback = JOIN(review_feedback_lines, "\n")
  ELSE:
    SET review_feedback = ""

WRITE output parameters: review_feedback

PRESENT summary:
  # Review Complete: {project_name}
  Status: {overall_status}
  Version: {NEW_VERSION}
  Spec: {SPEC_FILE}

  Blocking: {blocking_count} | High: {high_count} | Medium: {medium_count} | Low: {low_count}

  IF MODE IN {"REPAIR", "REVERIFY"}:
    Fixed: {fixed_count} | Still Failing: {still_failing_count} | Regressions: {regression_count}

  IF overall_status == "FAILED":
    Blocking issues must be resolved. Pass implementation_feedback to implementing-code.

  IF overall_status == "PASSED":
    Implementation verified against plan and research. Ready for merge/deployment.

LOG: "Validation complete. Status: {overall_status}. Spec: {SPEC_FILE}"
```

**Execution:** automated

Memory Bank artifact type: `"{N} review-findings"` (e.g., `"17 review-findings"`).

**Memory Bank — MANDATORY session-end writes:**
1. Overwrite `context-pack/active-context.md` with session status, decisions, blockers, key artifacts (see execution-protocol.md Section 4 for schema).
2. Append one milestone row to `context-pack/progress.md` with artifact count above.

**Section 2 LAST ACTION — MANDATORY:** Update `_progress.json` status to `COMPLETED` with `completed_at` timestamp.
If the session failed, set status to `FAILED` instead.

---

### Step 11: Emit Harness Outputs Sidecar

**Apply execution-protocol.md Section 11** — Harness Output Sidecar. Mandatory when the prompt contains a `## Run metadata` block. This is the FINAL file write of the run (after SPEC/AUDIT verification in Step 9, after Step 10 presentation, after Memory Bank, after `_progress.json` set to COMPLETED). Without it, the orchestrator falls back to the capability `value_template`, which corrupts `review_output_path` into a doubly-nested folder when the parameter has already been pre-resolved to an absolute path.

**Output parameters this skill produces** (one key per row of the prompt's `## Output parameters` table):

- `review_output_path`: the resolved `validation_output_path` parameter VERBATIM as received in the prompt's `## Parameters` table — the folder that holds `REVIEW-SPEC-{SESSION_ID}.md` and `REVIEW-AUDIT-{SESSION_ID}.md`. Do NOT re-prepend `{output_folder}`, `{project_name}`, or `{feature_id}`.
- `review_status`: `"PASSED"` | `"PARTIAL"` | `"FAILED"` — the `overall_status` computed in Step 10.
- `blocking_count`: integer count of blocking issues.
- `high_count`: integer count of high-priority issues.
- `review_feedback`: the structured one-line-per-finding string computed in Step 10 (`""` when `review_status = "PASSED"`).

**Implementation:** the harness here accepts Bash heredoc for the sidecar write (the sidecar is NOT the SPEC_FILE, so §10.5's anti-Bash rule does not apply). Execute:

```
cat > {stepwise_outputs_file} << 'OUTPUTS_EOF'
{
  "review_output_path": "{validation_output_path}",
  "review_status": "{overall_status}",
  "blocking_count": {blocking_count},
  "high_count": {high_count},
  "review_feedback": "{review_feedback_escaped}"
}
OUTPUTS_EOF
```

`{stepwise_outputs_file}` is the path from the prompt's `## Run metadata` block's `output_file = '...'` line — copy it verbatim, do NOT reconstruct it. Embedded newlines in `review_feedback` MUST be JSON-escaped as `\n`.

Self-check: `cat {stepwise_outputs_file}` — verify non-empty and valid JSON. If empty, missing, or malformed, re-execute. DO NOT describe output registration in response text — EXECUTE it. No tool calls after this; the next event is `final_response`.

**Execution:** automated

---

## Source File Scoping for Feature Reviews

When scope_type == feature-impl:
1. Load ONLY files modified/created by implementation (from IMPL-STATE-*.md or git diff --name-only)
2. Include direct dependencies of changed files (one hop)
3. Load full source tree ONLY when: scope_type==code-development OR no changed file list available
4. Log: "Source scoping: {N} changed files vs full tree {M} files"

## REPAIR / REVERIFY Mode

Triggered when `failure_feedback` is provided, when a prior FAILED REVIEW-SPEC exists
(REPAIR), or when the prompt carries a `## Previous verification (lap N-1)` block
(REVERIFY — the automated VGT-loop re-review). The full protocol — Review Consistency
Rule, Fresh Review Spec Rule, REPAIR mechanics, scoped REPAIR cycle review, and the
REVERIFY verdict-memory sub-section — lives in **`references/repair-mode.md`**. Read
that file at Step 1 when MODE is detected as REPAIR or REVERIFY.

## Usage Examples

### Fresh Review
```
Execute reviewing-code with:
  project_name: "CalcService"
  plan_folder_path: "artifacts/outputs/plan/"
  research_folder_path: "artifacts/outputs/research/"
  progress_folder_path: "artifacts/outputs/progress/"
  source_path: "src/"
```

### Repair Review
```
Execute reviewing-code with:
  project_name: "CalcService"
  plan_folder_path: "artifacts/outputs/plan/"
  research_folder_path: "artifacts/outputs/research/"
  progress_folder_path: "artifacts/outputs/progress/"
  source_path: "src/"
  failure_feedback: "Review v1.0.0 found 3 blocking issues: [BLK-001] MISSING_FILE in src/Calculator.java..."
```

### With Custom Tools
```
Execute reviewing-code with:
  project_name: "CalcService"
  plan_folder_path: "artifacts/outputs/plan/"
  research_folder_path: "artifacts/outputs/research/"
  progress_folder_path: "artifacts/outputs/progress/"
  source_path: "src/"
  validation_tools: {
    "security": {
      "enabled": true,
      "command": "snyk test --json",
      "parser": "json",
      "fail_on": ["critical", "high"],
      "required": true
    }
  }
```

## Reference Files

| File | Load when | Purpose |
|------|-----------|---------|
| `references/review-gates.md` | Before Step 1 (Pre-Flight) and before Step 10 exit (Output Existence) | Pre-flight + post-write gates |
| `references/reviewing-principles.md` | Step 1 — once at session start | The 6 adversarial review principles |
| `references/severity-taxonomy.md` | Step 2 (and any time you classify a finding) | BLOCKING / HIGH / MEDIUM / LOW + REPAIR feedback quality rule |
| `references/secure-defaults-taxonomy.md` | Step 4.7 (judgment pass) + Step 5 (deterministic subset) | SD-01…SD-10 secure-default defect classes + fixed severities + fail-open rule |
| `references/repair-mode.md` | Step 1 if MODE == REPAIR or REVERIFY | Review Consistency Rule, Fresh Review Spec Rule, REPAIR mechanics, scoped repair, REVERIFY (VGT verdict-memory) |
| `references/findings-classification.md` | Step 4 (and Step 5 for tool blocking) | ADR Binding, Functional Equivalence, MTP Tool Classification |
| `references/tool-execution-protocol.md` | Step 5 | Tool detection, configuration, execution |
| `references/code-review-template.md` | Step 8 | REVIEW-SPEC template structure |
| `references/quality-assurance.md` | Before Step 8 final write | Common Rationalizations, Red Flags, Verification Checklist |
| `context-pack/execution-protocol.md` | As referenced | Session ID generation, _progress.json lifecycle, Memory Bank, REPAIR mechanics |
