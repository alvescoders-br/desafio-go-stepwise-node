---
name: researching-feature-impl
description: >
  Feature/user-story research phase for existing applications. Analyzes a user
  story or feature request alongside the existing codebase to produce a single
  agent-native research spec with zero prose — structured story summary, codebase
  analysis, impact assessment, integration mapping, implementation approach,
  acceptance criteria, and test strategy. All unresolved items in unified
  open_questions. Mid-weight alternative between researching-bug-fixing (5 sections)
  and researching-code-design FULL_SDLC (20 sections). Downstream consumer:
  planning-code-tasks (TASK mode). Human-readable output via humanize-spec.
license: Proprietary
metadata:
  author: aipods-team
  version: 4.2.0
  category: engineering
  tags: feature, user-story, research, implementation, FIC, RPI, agent-native, mid-weight
---

# Researching Feature Implementation — Agent-Native Spec

## SKILL PROTOCOL — ENTRY RULES (read first, do not skip)

1. **The protocol below is internally consistent.** If you perceive a conflict
   between the capability prompt and this skill, the skill wins for execution
   mechanics; the capability wins for paths/parameters. Do NOT exit citing
   "ambiguity" or "internal contradiction".

2. **Begin Step 1 (Initialize) immediately.** Step 1's first action (write
   `_progress.json` to `research_output_path`) IS the verification.

3. **Reference files load on demand via `cat`** when each step's `READ`
   pointer says so. They are NOT preloaded.

4. **Zero Invention Policy is non-negotiable.** Every factual claim MUST trace
   to the user story, source code, design spec, API contract, or architecture
   notes. Missing data → mark `status: pending` and register an open_questions
   entry. Asking the human a clarifying question = task FAILURE.

4a. **Host-codebase precondition — its absence is a BLOCKER, not a fillable gap.**
   This scope (feature-impl) presumes an **existing application** at `source_path`.
   That host codebase is a *precondition* of the task, so Entry Rule #4's "missing
   data → mark pending" does NOT apply to the codebase itself. Before any
   discovery, verify `source_path` exists on disk AND actually contains the host
   application — not empty, not a stub: at minimum the application entry point is
   present, and any component the task names as a pre-existing / untouchable
   boundary (e.g. a controller or service the DoD says "do not change") is
   physically present. If `source_path` is absent/empty, or lacks the host
   application the task presumes, **STOP and escalate as a BLOCKER**
   (`stepwise session exec-fail` / `NEEDS_REPLAN`) naming the missing precondition.
   Do NOT proceed by marking the whole host codebase as `assumption`/`pending`,
   and do NOT synthesize a minimal/stub module — a research spec built on an absent
   host codebase is not "actionable for planning," it is a blocker. (Calibration:
   CalcService3 cdal-01 — `./source` was absent; research proceeded on assumptions
   and implementation built a stub that passed code-review yet could not boot.)

5. **No final response until RESEARCH-SPEC + RESEARCH-AUDIT exist on disk.**

6. **Write-Flush-Forget — non-negotiable.** After writing the SPEC skeleton in
   Phase A (Step 3), NEVER re-read the SPEC file in full. Authoring a section is
   exactly four operations: (a) read `_progress.json` (small), (b) load
   section-specific Tier 2 inputs, (c) one targeted `Edit` replacing the
   section's `WFF-SECTION:{name}:pending` anchor with the section body,
   (d) update `_progress.json`. The agent's working memory holds at most ONE
   in-flight section body at a time. The SPEC file is write-only after the
   skeleton is laid down.

   **Why:** repeated `view` of the working spec inflates prompt tokens
   geometrically with iteration count and breaks prompt-cache continuity.
   Calibration evidence (Edenred sprint-3) showed 5M+ prompt tokens per failed
   run attributable to this pattern.

   **Forbidden tool patterns inside the section-author loop:**
   - `view SPEC_PATH` (any kind) AFTER the skeleton is written. Read `_progress.json` instead.
   - `replace_all=true` on the SPEC file. Use targeted anchored Edits.
   - `bash wc -l SPEC_PATH` to "verify" progress. Placeholder anchor presence is the verification.

   **Permitted exceptions (must be explicitly justified in agent reasoning):**
   - At the very end of the run, ONE final grep to verify all placeholders are
     replaced (`! grep "WFF-SECTION:.*:pending" SPEC_PATH`; if empty, mark
     `_progress.json.status: complete`).
   - On REPAIR: ONE initial bounded read (offset/limit, max 80 lines) around
     the affected section to confirm placeholder state.

---

## Quick Start
Analyze a user story / feature request and the existing codebase to produce a
structured, agent-consumable research spec for safe, well-integrated feature
implementation. Output is a **single file**:
`{research_output_path}/RESEARCH-SPEC-{SESSION_ID}.md`.
No prose. No narrative. Only structured data the implementing agent needs to
execute Research/Plan/Implement cycles.

## Known Failure Modes
<!-- ACCUMULATING — appended by calibrating-updates (WS6). Newest first. Rules MUST be generic/behavioral (project-agnostic); project-specific fixes go to context packs, never here. Format + entry rules: engineering-skills/references/known-failure-modes-format.md. Read these at pre-flight so a lesson learned once recurs no more. -->

## Anti-Patterns (do NOT)
<!-- ACCUMULATING — appended by calibrating-updates (WS6). One line each: **AP-NNN** (ISO-date, source: REC-NNN): prohibition — why. -->

## Output Architecture

```
{research_output_path}/
├── RESEARCH-SPEC-{SESSION_ID}.md     <- Single agent-native spec (all sections)
└── RESEARCH-AUDIT-{SESSION_ID}.md    <- Session audit trail (metadata only)
```

**Why single file:** Agent-native specs are 60-70% smaller than multi-document
research sets. No batching needed — the entire spec fits comfortably in context.
The Write-Flush-Forget protocol applies only if context exceeds 60% mid-generation
(unlikely with zero-prose output).

**Human-readable output:** Not produced by this skill. Use `humanize-spec` skill
with profile `feature-impl-research` to generate the full 9-document research set
on demand.

**Pipeline Position:**

```
User Story / Feature Request (Jira / GitHub / file)
            |
  [Source Code Repository]      (strongly recommended)
            |
  [Optional: Design Specs, API Contracts, ADRs, Architecture Notes]
            |
  [researching-feature-impl]    <- YOU ARE HERE
            |
  [planning-code-tasks]         (TASK mode)
            |
  [implementing-code]
```

**When to use this skill (vs alternatives):**

| Scenario | Skill |
|----------|-------|
| Isolated defect fix with a bug ticket | researching-bug-fixing (5 sections) |
| Implementing a story/feature into an existing app | **researching-feature-impl** (9 sections) <- THIS |
| Full greenfield build with PRD, Epics, Stories, ADRs | researching-code-design FULL_SDLC (20 sections) |

## Parameters
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_name | string | Yes | Project identifier |
| story_path | string | Yes | Path to user story / feature request file (Markdown, JSON, or plain text) |
| source_path | string | Recommended | Path to source code repository |
| design_specs_path | string | No | Path to UI/UX specs, wireframes, mockup descriptions |
| api_contract_path | string | No | Path to API contract (OpenAPI, GraphQL schema, or doc) |
| architecture_notes_path | string | No | Path to ADRs, architecture decision docs, or tech stack notes |
| context_pack_path | string | No | Tech-policy, arch-standards, coding-standards |
| research_output_path | string | No | Output folder. When invoked via capability, the resolved path includes `feature_id` scope when set: `{output_folder}/{project_name}/{feature_id}/research-output`. Without `feature_id`: `{output_folder}/{project_name}/research-output`. Standalone default: `./research/` |
| failure_feedback | string | No | Present only in REPAIR mode — targeted fix directives |
| custom_message | string | No | Optional user instructions |

**If any Required parameter is not defined, ABORT EXECUTION.**

## Workflow

### Step 1: Initialize

**Command:**
```
# Feature Implementation Research Agent — Agent-Native Spec Generator
# Persona: Senior Feature Analyst & Integration Researcher
# CRITICAL: NON-INTERACTIVE SESSION.
# MISSION: Extract structured feature analysis from story + source. Zero invention.

SESSION_ID = [Extract from EXECUTION METADATA]

IF failure_feedback NOT empty:
  MODE = REPAIR
  SPEC_FOLDER = resolve_parent_folder(research_output_path)
  SPEC_FILE = find existing RESEARCH-SPEC-*.md in SPEC_FOLDER
  IF not found -> write Gap Report -> EXIT
  Load SPEC_FILE -> PREVIOUS_SPEC -> SOURCE_LOG
  PREVIOUS_VERSION = extract version
  NEW_VERSION = increment patch
  Parse failure_feedback -> REPAIR_DIRECTIVES [{ section, instruction, reason }]
ELSE:
  MODE = BUILD
  SESSION_ID = "FEAT-{PROJECT_NAME_UPPER}-{YYYYMMDD}"
  SPEC_FOLDER = research_output_path + '-' + SESSION_ID + '/'
  SPEC_FILE = SPEC_FOLDER + 'RESEARCH-SPEC-' + SESSION_ID + '.md'
  NEW_VERSION = "1.0.0"
  mkdir -p SPEC_FOLDER

  ## EARLY SIGNAL — FIRST action after mkdir (MANDATORY)
  ## Section-shape variant — see execution-protocol.md §10.1 for schema and §10.6 for CONTINUE-on-re-entry.
  WRITE SPEC_FOLDER + '_progress.json':
    { "skill": "researching-feature-impl", "session_id": "<SESSION_ID>",
      "status": "RUNNING", "started_at": "<ISO timestamp>", "completed_at": null,
      "skeleton_written": false,
      "sections": {
        "story_summary": "pending", "codebase_analysis": "pending",
        "impact_assessment": "pending", "integration_mapping": "pending",
        "implementation_approach": "pending", "acceptance_criteria": "pending",
        "test_strategy": "pending", "validations": "pending",
        "open_questions": "pending"
      } }
  ## Coordinator output-check finds _progress.json and will NOT send SIGINT.

SOURCE_LOG = []
CHANGE_LOG = []

## Memory Bank — Cross-Session Continuity
Read `_shared/references/memory-bank.md` for the full protocol.
At session start: read context-pack/active-context.md and progress.md.
Write active-context.md with status: STARTING (crash recovery).
Use prior session context to avoid re-discovering known blockers and respect prior decisions.

## Zero Invention Policy
Not in source -> status: pending. Never infer, assume, or create information.
Inferred industry standards -> status: assumption (with ASM-XX ID).

## Internal Reasoning: ALL in English regardless of output language.
```
**Execution:** automated

---

### Step 1.5: Scope Triage Gate (mandatory pre-author check)

Before reading any upstream artifact in detail, compute a scope complexity
estimate from file-size and count signals only (no LLM reasoning yet). If the
estimate exceeds the configured envelope, write a Gap Report and exit cleanly
with `SCOPE_REFUSED`. The downstream coordinator MUST then surface the
reduce-scope guidance to the operator — do NOT retry the same scope.

**Inputs to the estimate (cheap signals only — `wc -l` / `ls` / `grep -roc`):**

```
US_COUNT          = count of user-story files at story_path (1 for single-story input)
BC_COUNT          = count of bounded-context files referenced under domain_boundaries_path
                    (fallback: count distinct top-level service folders under source_path/src)
ADR_COUNT         = count of ADR-*.md files under adr_path
OPEN_Q_HINT       = count of "[to be identified]", "[TBD]", "[?]" tokens across
                    story file + arch notes (single grep -roc)
EPIC_HEAVY        = 1 if the single story file > 800 lines OR > 25 KB; else 0
ARCH_BREADTH_HINT = count of distinct "service" / "bounded_context" / "domain" entries
                    declared in target_architecture (one grep)
```

**Scope complexity score:**

```
SCORE = (US_COUNT * 3)
      + (BC_COUNT * 5)
      + (ADR_COUNT * 1)
      + (OPEN_Q_HINT * 2)
      + (EPIC_HEAVY * 10)
      + (ARCH_BREADTH_HINT * 2)
```

**Decision table (feature-impl thresholds — tighter than code-design):**

| SCORE   | Verdict           | Action                                                  |
|---------|-------------------|---------------------------------------------------------|
| `<= 8`  | SAFE              | Proceed to Step 1.6.                                    |
| `9–15`  | BORDERLINE        | Proceed BUT write a WARNING into `_progress.json` (`scope_warning: true`). |
| `> 15`  | **SCOPE_REFUSED** | **STOP authoring. Write Gap Report. Exit.**             |

**Hard rule (independent of SCORE):** if `US_COUNT > 1` → SCOPE_REFUSED with
message "feature-impl is single-user-story; use code-development for multi-US scope".

**On SCOPE_REFUSED:**

1. Update `_progress.json`:
   ```json
   {
     "status": "SCOPE_REFUSED",
     "score": <computed>,
     "us_count": <N>,
     "bc_count": <N>,
     "recommended_decomposition": "split-into-feature-impl-or-use-code-development"
   }
   ```
2. Write `RESEARCH-AUDIT-{SESSION_ID}.md` with a single section `## Gap Report — SCOPE_REFUSED`:
   ```markdown
   # RESEARCH-AUDIT (Gap Report)
   verdict: SCOPE_REFUSED
   score: <N>   (threshold: 15)
   us_count: <N>
   bc_count: <N>
   adr_count: <N>
   open_q_hint: <N>

   ## Recommended decomposition
   Either:
   (a) Reduce scope so US_COUNT == 1 AND SCORE <= 8, OR
   (b) Switch capability to code-development (multi-US, full-SDLC).

   ## Why the gate triggered
   feature-impl is sized for a single user story. At this complexity the
   agent's iteration budget cannot reliably finish. Prior calibration evidence
   (Edenred sprint-3 §"MAX_ITERATIONS") confirms this failure mode.

   ## To proceed
   (a) Reduce scope to a single user story AND SCORE <= 8, OR
   (b) If you understand the risk, override by setting `scope_triage_override: true`
       in config.yaml AND raise the agent iteration cap to >= 250.
   ```
3. Write `RESEARCH-SPEC-{SESSION_ID}.md` as a one-paragraph stub pointing at the AUDIT.
   This satisfies entry-rule #5 (both files must exist) without doing the authoring work.
4. Emit the structured final response:
   ```json
   {"event":"final_response","content":"SCOPE_REFUSED: research scope exceeded triage threshold. See RESEARCH-AUDIT for decomposition guidance."}
   ```
   Then exit. The runtime treats this as a successful step completion — it does NOT trigger an automatic retry.

**Override mechanism (intentional escape hatch):**

If `custom_message` or a `scope_triage_override: true` config parameter is
present, log the override decision in the AUDIT
(`override_acknowledged: true, override_reason: "<text>"`) and continue to
Step 1.6. The override exists so a human can force feature-impl over an
oversized scope after weighing the risk — default behavior is REFUSE.

**Execution:** automated

---

### Step 1.6: Resume from `_progress.json` (REPAIR support)

If `_progress.json` already exists at `SPEC_FOLDER`:

```
LOAD _progress.json.

IF _progress.json.status == "SCOPE_REFUSED":
  DO NOT proceed. Re-emit the SCOPE_REFUSED final_response and exit.
  (Operator must reduce scope per the Gap Report or set scope_triage_override: true.)

IF _progress.json.status IN ["RUNNING", "PARTIAL"]:
  PARSE _progress.json.sections{} -> SECTION_STATUS
  FOR EACH section in section_catalog:
    IF SECTION_STATUS[section.name] == "complete":
      MARK section as SKIP (already written; do NOT re-author)
    IF SECTION_STATUS[section.name] == "in_progress":
      MARK section as RESUME (re-author from scratch; previous attempt was incomplete)
    IF SECTION_STATUS[section.name] == "pending":
      MARK section as DO

IF _progress.json.status == "complete":
  No work to do. Emit "spec already complete" and exit.

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
WFF-SECTION:{name}:complete anchor exists in SPEC_FILE. If absent (stale
status), demote to RESUME and re-author.
```

**Execution:** automated

---

### Step 2: Input Loading

> **Before any discovery scan — apply execution-protocol.md Section 13 (Code-Location Discipline).** Read `context-pack/codebase-map.md` (and `project-inventory.md` if present) to locate the files and integration points the feature touches BEFORE running a repository-wide `grep`/`glob`/`find` to discover where they live — **consult before scan, not never scan**. Read the specific files the map names directly; fall back to a scoped scan only where the map is absent or insufficient, and flag that gap in the research output so the map can be corrected. Map first (§13), then delegate the residual sweep (§12).
>
> **During input loading — apply execution-protocol.md Section 12 (Delegated Exploration) if your harness supports it.** Broad read-only sweeps for this skill (e.g. locating the files and integration points the feature touches, mapping existing patterns to follow) MAY be delegated to a read-only exploration subagent on a cheap/fast model, which returns conclusions + `file:line` pointers (not file dumps). Synthesis, decisions, and all writing stay with this agent, which verifies any delegated `file:line` before using it (Zero-Invention still applies). With no subagent capability, explore inline under the execution-path constraint — output quality is identical either way.

**Command:**
```
## STOP-GATE — Mandatory Inputs

REQUIRED = [
  { name: "User Story / Feature Request", path: story_path }
]

FOR EACH input IN REQUIRED:
  IF input.path is empty OR file does not exist:
    WRITE {SPEC_FOLDER}/RESEARCH-SPEC-GAP-REPORT.md:
      session_id: {SESSION_ID}
      status: BLOCKED
      reason: Missing story/feature file
      expected_at: {story_path}
      action: Provide a user story or feature request file (Markdown, JSON, or plain text) and re-run.
    EXIT — Do not proceed.

## 2A. Load User Story / Feature Request -> STORY_CONTEXT

Read story_path completely. Extract:

STORY_CONTEXT = {
  contract_mode:    # auto-detected: structured | partial | unstructured
  prd_source_hash:  # sha256:<64 lowercase hex> if declared by story artifact; else N/A
  epics_source_hash:# sha256:<64 lowercase hex> if declared by story artifact; else N/A
  hash_status:      # match | mismatch_accepted | mismatch_blocked | not_verified | N/A
  id:               # Jira key (e.g., PROJ-456), GitHub issue #, or "N/A"
  title:            # Summary / title line
  description:      # Full description text
  persona:          # "As a [persona]" — extract if user story format; else "[Not specified]"
  goal:             # "I want [goal]" — extract if user story format; else infer from description
  benefit:          # "So that [benefit]" — extract if user story format; else "[Not specified]"
  story_format:     # "user_story" if As a/I want/So that detected, "feature_request" if functional spec, "generic" otherwise
  priority:         # P0-P4, MoSCoW, or inferred
  parent_epic:      # Epic reference if present; else "[Not specified]"
  ac:               # Acceptance criteria from story (may be empty)
  affected_areas:   # Files, modules, endpoints, UI screens mentioned
  dependencies:     # Other stories, services, or features mentioned as dependencies
  literal_refs:      # LIT-XX references and exact values if present
  fallback_refs:     # pending input / assumption fallback IDs if present
  labels:           # Tags / labels (if present)
  attachments:      # Mockups, designs, specs referenced (if present)
  constraints:      # Performance targets, compatibility requirements mentioned
  sourced_constraints: # Constraints with explicit ADR/tech-policy/context-pack/story source_ref
  evidence_gaps:    # structured/prose discrepancies, unsourced structural mandates
  out_of_scope:     # Explicitly excluded items (if present)
}

# Zero Invention Policy: If a field is absent -> set to "[Not provided in story]".
# Never infer acceptance criteria that the story does not state — derive and mark [Derived].

Detect `contract_mode` automatically:
- `structured`: story declares `contract_format: structured`, global AC IDs,
  enriched open_questions, literal/fallback refs if used, every required source
  hash is valid SHA-256, and upstream completeness is certified.
- `partial`: some structured fields exist, or a declared-structured story fails
  its own contract during WARN-mode rollout. Use available structured rows, but
  still derive IDs/literals/fallbacks from story prose as a cross-check.
- `unstructured`: no structured contract fields. This is valid for external
  story inputs; use the current prose parsing behavior.

Hash format gate:
- Treat only `sha256:<64 lowercase hex chars>` as a valid hash value.
- Any field named `content_hash`, `*_source_hash`, or `source_hash` with a
  missing value, bare hash, mtime, session ID, filename, or placeholder is
  invalid for structured mode.
- Invalid hash fields demote the story to `partial`, require prose cross-check,
  and create an `evidence_gaps` row. Do not emit `hash_status: match` for a
  non-SHA value.

Use SHA-256 content hashes only; never use mtime. If upstream PRD/Epics files
are loaded and a valid declared story hash mismatches, forward-verify the
story's recorded dependencies (IDs, literals, fallbacks). If unchanged, proceed
and log the acceptance in the audit only; never edit upstream artifacts. If
upstream files are not provided, set `hash_status: not_verified` and do not
block solely because verification is impossible.

Architecture authority rule for story inputs:
- Stories may carry behavior, acceptance criteria, and sourced positive or
  negative constraints with explicit ADR/tech-policy/context-pack/story refs.
- Stories may not introduce unsourced file paths, package names, layer
  assignments, framework choices, storage tools, runtime topology, deployment
  topology, or module placement. Move those to `evidence_gaps` or mark pending.

Authentication security defaults:
- If the story touches auth, sessions, identity, OAuth, or password reset,
  persisted password-reset tokens are secrets and must be hashed at rest. Raw
  reset-token storage is an `evidence_gaps` row unless a binding upstream source
  explicitly requires it.
- OAuth provider values must come from an explicit allow-list before selecting
  provider columns, scopes, or identity fields. A fallback such as "non-google
  means github" is an `evidence_gaps` row.

## 2B. Load Source Code -> SOURCE_CONTEXT (if available)

IF source_path exists:
  SOURCE_CONTEXT = {
    project_structure:   directory tree (relevant areas only)
    affected_files:      files matching STORY_CONTEXT.affected_areas
    existing_patterns:   [pattern -> file:lines] in areas the feature will touch
    conventions:         naming, structure, error handling, component patterns
    test_framework:      framework name, test commands, test conventions
    dependencies:        library -> version from build file
    data_layer:          ORM, database type, migration tool, schema location
    api_layer:           framework, router patterns, middleware, auth approach
    ui_layer:            component framework, state management, routing, styling approach
    existing_features:   similar features already implemented (for pattern reference)
  }
ELSE:
  SOURCE_CONTEXT = null

## 2C. Load Design Specs -> DESIGN_CONTEXT (if available)

IF design_specs_path exists:
  DESIGN_CONTEXT = {
    screens:         list of screens / views described
    components:      UI components specified
    interactions:    user flows / interactions described
    design_tokens:   colors, typography, spacing mentioned
    responsive:      responsive requirements
    accessibility:   a11y requirements
  }
ELSE:
  DESIGN_CONTEXT = null

## 2D. Load API Contract -> API_CONTEXT (if available)

IF api_contract_path exists:
  API_CONTEXT = {
    endpoints:        new/modified endpoints
    methods:          HTTP methods / GraphQL operations
    request_schemas:  request body / parameter shapes
    response_schemas: response body shapes
    auth:             authentication requirements
    versioning:       API versioning approach
  }
ELSE:
  API_CONTEXT = null

## 2E. Load Architecture Notes -> ARCH_CONTEXT (if available)

IF architecture_notes_path exists:
  ARCH_CONTEXT = {
    decisions:     ADR-style decisions relevant to this feature
    constraints:   architectural constraints (e.g., event-driven, CQRS, microservice boundary)
    tech_stack:    approved technologies and versions
    patterns:      required patterns (e.g., repository pattern, saga, circuit breaker)
  }
ELSE:
  ARCH_CONTEXT = null

## 2F. Load Context Pack (if available)

IF context_pack_path exists:
  Read tech-policy, arch-standards, coding-standards -> SOURCE_LOG

## 2G. REPAIR Mode — Parse Directives

IF MODE == REPAIR:
  Parse failure_feedback into:
  REPAIR_DIRECTIVES = [
    { target: "story_summary"|"codebase_analysis"|"impact_assessment"|
              "integration_mapping"|"implementation_approach"|
              "acceptance_criteria"|"test_strategy"|"global",
      instruction, reason }
  ]
  Sections WITHOUT directives -> PRESERVE (keep from PREVIOUS_SPEC).
  "global" -> regenerate entire spec.

  REPAIR CLEANUP RULE:
  Before generating new output files:
  1. List all files in SPEC_FOLDER excluding the canonical PREVIOUS_SPEC
  2. Archive or delete files from prior failed runs (different SESSION_ID)
  3. Log: "Archived {N} orphaned artifacts from prior failed runs"

## CHECKPOINT 1 — Write skeleton spec after input loading (BUILD mode only)
## Purpose: Preserve extracted contexts if killed during Step 3 generation.
IF MODE == BUILD:
  WRITE SPEC_FILE with:
    - Header metadata (version: NEW_VERSION, session: SESSION_ID, mode: BUILD,
      date: today, language: DETECTED_LANGUAGE, source_path)
    - story_summary section: populated from STORY_CONTEXT
    - codebase_analysis section: populated from SOURCE_CONTEXT
    - All remaining sections as stubs:
      ## {section_name}
      <!-- WFF-SECTION:{section_name}:pending -->
      status: pending - will be generated in Step 3
    - Top-level spec_status: draft
  LOG: "CHECKPOINT 1: skeleton spec written with story_summary + codebase_analysis"
```
**Execution:** automated

### Step 3: Generate Spec

**Apply execution-protocol.md Section 10** — Phase A (skeleton-first within 5 tool calls of entering Step 3) then Phase B (one section per `Edit` call). Tool discipline (§10.5) is **mandatory**: skeleton via `Write`, sections via `Edit`, NEVER `Bash + sed/python3/awk` to mutate SPEC_FILE. The non-ASCII fallback (§10.5.1) auto-applies when content is non-English. The Safe-Write Protocol (§10.5.2) is **mandatory** for any SPEC edit > 30% / > 20 KB and refuses any `Edit` with `old_string` shorter than 10 characters. NEVER fall back to bulk rewriting when one `Edit` fails — fix the `Edit` call instead.

**Section-author loop (Write-Flush-Forget — see Entry Rule #6):**

```
FOR EACH section in section_catalog (template order, respecting dependencies):
  1. status = _progress.json.sections[section.name].status
     IF status == "complete": SKIP (already authored — see Step 1.6)
  2. LOAD only this section's Tier 2 inputs (e.g. for codebase_analysis,
     the target source files only; for acceptance_criteria, the user story
     file only). Do NOT re-read SPEC_FILE.
  3. Compose section body in working memory — ONE in-flight body at a time.
  4. Single targeted Edit replacing `<!-- WFF-SECTION:{name}:pending -->`
     with the body followed by `<!-- WFF-SECTION:{name}:complete -->`.
  5. Update _progress.json: sections[name].status = "complete";
     sections[name].iterations_used = current_iter - section_start_iter.
  6. FLUSH: discard body + Tier 2 inputs. Do not carry forward.
  7. Checkpoint budget: IF (cap - current_iter) < (remaining_sections * 20),
     mark _progress.json.status = "PARTIAL" and exit cleanly. REPAIR can resume.

FINAL VERIFICATION (single permitted post-skeleton read):
  ! grep "WFF-SECTION:.*:pending" SPEC_PATH
  IF empty: _progress.json.status = "complete".
  ELSE: log unfinished sections and exit PARTIAL.
```

**Skeleton stub text — must be ASCII:** `<!-- WFF-SECTION:{name}:pending -->` (HTML comment is ASCII-safe; `status: pending - will be generated` may remain as human-readable companion below the anchor).

**Section list (template order):** `story_summary -> codebase_analysis -> impact_assessment -> integration_mapping -> implementation_approach -> acceptance_criteria -> test_strategy -> validations -> open_questions`. See `references/feature-impl-research-template.md` for full structure.

**READ** `references/feature-impl-research-template.md` **NOW** for section structure.
**READ** `references/consistency-rules.md` **NOW** for the 10 consistency rules
(Codebase Fidelity, Story AC Preservation, Technology Fidelity, API Contract
Fidelity, Design Spec Fidelity, Architecture Constraint Respect, Zero Invention,
Anti-Fade) plus Status Protocol and Source Tagging.

Generate the complete spec following the template, applying all rules from the
references above.

## CHECKPOINT 2 — Write complete draft spec after generation
## Purpose: Preserve full draft if killed during Step 4 validation.
WRITE SPEC_FILE with all generated sections (overwrite skeleton from Checkpoint 1).
  - Top-level spec_status: draft
LOG: "CHECKPOINT 2: complete draft spec written (pre-validation)"

**Execution:** automated

### Step 4: Quality Validation Gate

**Command:**
```
1. Codebase Fidelity: Every file path references a real path from
   SOURCE_CONTEXT or is marked [Assumption]
2. Story AC Coverage: Every item from STORY_CONTEXT.ac appears verbatim in
   acceptance_criteria.story_ac
3. Integration Mapping Completeness: Every area from STORY_CONTEXT.affected_areas
   appears in integration_mapping section
4. Technology Fidelity: All technology references match SOURCE_CONTEXT.dependencies
   or ARCH_CONTEXT.tech_stack or are marked [Unknown]
5. API Contract Consistency: If API_CONTEXT exists, all endpoint references
   match the contract
6. Design Spec Consistency: If DESIGN_CONTEXT exists, all screen/component
   references match the spec
7. Anti-Fade: test_strategy depth matches story_summary depth
8. Section Completeness: All 9 mandatory sections present
   (story_summary, codebase_analysis, impact_assessment, integration_mapping,
    implementation_approach, acceptance_criteria, test_strategy, validations,
    open_questions)
9. Count Verification: Summary counts match actual item counts in each section
10. Source Tags: Every item with status:complete has a source reference
11. Story Contract Mode: STORY_CONTEXT.contract_mode is recorded as structured,
    partial, or unstructured; unstructured is valid for external story inputs
12. Partial Cross-Check: In partial mode, prose-derived IDs/literals/fallbacks
    are checked against structured rows and discrepancies become evidence_gaps
13. Architecture Authority: Sourced constraints pass; unsourced structural
    mandates are flagged as evidence_gaps or pending inputs
14. Hash Forward Verification: source hashes are valid `sha256:<64 lowercase hex>`
    values or marked invalid; valid mismatches are forward-verified against
    recorded dependencies and accepted only in the audit
15. Auth Security Defaults: auth/OAuth/password-reset stories carry reset-token
    hash-at-rest and provider allow-list constraints or evidence_gaps

IF corrections needed -> apply in place, log to CHANGE_LOG

## CHECKPOINT 3 — Write validated spec after quality gate
WRITE SPEC_FILE with validated content (overwrite draft from Checkpoint 2).
  - Top-level spec_status: complete (or draft if validation failures exist)
LOG: "CHECKPOINT 3: validated spec written"
```
**Execution:** automated

### Step 5: Write Outputs

**Command:**
```
1. Write SPEC_FILE (RESEARCH-SPEC-{SESSION_ID}.md)
   - Set the SPEC front-matter `version:` to NEW_VERSION. On REPAIR this MUST be the
     incremented patch (Step 1: PREVIOUS_VERSION → NEW_VERSION) — editing the content
     in place without bumping `version` is a §7 violation. See execution-protocol §7.2 step 8.
2. Write AUDIT_FILE (RESEARCH-AUDIT-{SESSION_ID}.md):
   - Session metadata (version=NEW_VERSION, mode, session_id, timestamp)
   - Sources referenced (numbered list from SOURCE_LOG):
     Story/Feature Request, Source Code, Design Specs, API Contract,
     Architecture Notes, Context Pack — each with load status
   - Story contract: contract_mode, upstream hashes, hash_status,
     accepted_hash_overrides, partial-mode evidence_gaps
   - Decisions made (from CHANGE_LOG)
   - Summary counts: affected_files, new_files, integration_points,
     data_model_changes, api_changes, ui_changes, story_ac, derived_ac,
     tests_to_write, tests_to_update, open_questions
   - REPAIR-only: set `mode: REPAIR` and APPEND (do not overwrite) a `## Repair History`
     entry — version, timestamp, directives_applied, sections_changed, sections_preserved,
     repair_delta (per execution-protocol §7.2 step 8).
3. REPAIR self-check (execution-protocol §7.2 step 9): before final_response, confirm the
   SPEC `version` is strictly greater than PREVIOUS_VERSION AND the AUDIT has the new
   `## Repair History` entry. If not, fix the bookkeeping now — do not finish.
4. Verify both files exist and are non-empty
5. UPDATE SPEC_FOLDER + '_progress.json':
   { "status": "COMPLETED", "completed_at": "<ISO timestamp>",
     "skill": "researching-feature-impl", "session_id": SESSION_ID }

Ready for downstream consumption (planning-code-tasks in TASK mode).

**Apply execution-protocol.md Section 11** — Harness Output Sidecar. Mandatory when the prompt contains a `## Run metadata` block. FINAL file write of the run (after Memory Bank, after `_progress.json` set to COMPLETED).

**Output parameters this skill produces** (one key per row of the prompt's `## Output parameters` table):

- `research_output_path`: the SPEC_FOLDER you actually wrote the RESEARCH-SPEC into, reported VERBATIM. SPEC_FOLDER is already bound to the received (feature-scoped) `research_output_path` param — do NOT re-prepend `{output_folder}`/`{project_name}`/`{feature_id}` or re-derive it from a `{% if feature_id %}` formula (that would drop the feature scope).

**Implementation:** the harness here accepts Bash heredoc for the sidecar write (the sidecar is NOT the SPEC_FILE, so §10.5's anti-Bash rule does not apply). Execute:

```
cat > {stepwise_outputs_file} << 'OUTPUTS_EOF'
{ "research_output_path": "{SPEC_FOLDER}" }
OUTPUTS_EOF
```

Self-check: `cat {stepwise_outputs_file}` — verify non-empty. If empty or missing, re-execute. DO NOT describe output registration in response text — EXECUTE it.
```
**Execution:** automated

## Memory Bank — Update Cross-Session State
Read `_shared/references/memory-bank.md` for the full protocol.
1. Overwrite context-pack/active-context.md with final session state (status, decisions, blockers, key artifacts).
2. Append one milestone row to context-pack/progress.md: `| {session_id} | {date} | {capability} | researching-feature-impl | {STATUS} | **{N} research-docs** | {1-line summary} |`
   Artifact count MUST be the exact number of research document files written (e.g., `"2 research-docs"`). See _shared/references/memory-bank.md Artifact Type Registry.
Both writes are MANDATORY — even on failure, record the failure.
After writing, VERIFY exists(context-pack/progress.md) and that the last row contains the research-docs count. LOG: "Memory Bank: progress.md updated — {N} research-docs recorded."

## Reference Files

| File | Load when | Purpose |
|------|-----------|---------|
| `references/feature-impl-research-template.md` | Step 3 | RESEARCH-SPEC section structure |
| `references/consistency-rules.md` | Step 3 — once at start | The 10 consistency rules + Status Protocol + Source Tagging |
