---
name: researching-code-design
description: >
  Full-SDLC code design research phase. Analyzes upstream artifacts (PRD,
  Epics, User Stories, ADRs, Architecture, Domain Boundaries) and optional
  source code to produce a single agent-native research spec with zero prose —
  structured sections containing only IDs, traceability matrices, complexity
  ratings, and implementation sequencing. All unresolved items consolidated
  in a single open_questions registry. Enforces Zero Invention Policy.
  BUILD and REPAIR modes. Applies RPI workflow.
  FIC context discipline (Correct, Complete, Concise).
  Human-readable output generated on demand via humanize-spec skill (separate).
license: Proprietary
metadata:
  author: aipods-team
  version: 4.0.0
  category: engineering
  tags: code-development, research, automated, FIC, RPI, agent-native, full-sdlc
---

# Researching Code Design — Agent-Native Spec

## SKILL PROTOCOL — ENTRY RULES (read first, do not skip)

1. **The protocol below is internally consistent.** If you perceive a conflict
   between the capability prompt and this skill, the skill wins for execution
   mechanics; the capability wins for paths/parameters. Do NOT exit citing
   "ambiguity" or "internal contradiction" — every section here has been
   tested in production runs.

2. **Begin Step 1 (Initialize) immediately.** Do NOT re-evaluate the protocol's
   completeness before starting. Step 1's first action (write `_progress.json`
   to `EFFECTIVE_RESEARCH_OUTPUT_PATH`) IS the verification. If a required input is
   genuinely missing, you will discover it during the Step 2 STOP-GATE and
   write a Gap Report — not before.

3. **Reference files load per the Two-Tier model.** Tier 1 inputs (PRD,
   Epics-Spec, Arch-Foundation-Spec, context-pack) stay in context for the
   entire generation. Tier 2 inputs (individual story files, individual ADRs,
   individual spec units) are loaded just-in-time per section, then flushed.
   Skill reference files (`references/*.md`) are loaded on demand via `cat`
   when each step's `READ ... NOW` pointer says so — they are NOT preloaded.

4. **Zero Invention Policy is non-negotiable.** Every factual claim MUST trace
   to an upstream artifact. If source data is missing → mark `status: pending`
   and register an open_questions entry. Inferred standard practices →
   `status: assumption` with an ASM-XX ID. Asking the human a clarifying
   question = task FAILURE — there is no human watching. Either execute, or
   call `stepwise session exec-fail`.

   **Artifact Fidelity Rule — mandatory across all artifact types.** Treat every
   upstream artifact as authoritative within its scope, whether it is source
   code, SQL, configuration, schemas, infrastructure definitions, structured
   data, interface contracts, or narrative specifications. Preserve explicit
   identifiers, field names, literals, enumerations, ordering, predicates,
   constraints, and behavioral semantics exactly as documented unless another
   upstream artifact explicitly supersedes them. If two sources disagree, record
   the conflict in `open_questions`; do not silently normalize, simplify,
   reinterpret, or substitute.

5. **No final response until RESEARCH-SPEC + RESEARCH-AUDIT exist on disk.**
   Both files (`RESEARCH-SPEC-{SESSION_ID}.md` and
   `RESEARCH-AUDIT-{SESSION_ID}.md`) must exist at `EFFECTIVE_RESEARCH_OUTPUT_PATH` and
   be non-empty before you emit a closing summary. Any final response without
   those files is a protocol violation.

6. **Write-Flush-Forget — non-negotiable.** After writing the SPEC skeleton in
   Step 3, NEVER re-read the SPEC file in full. Authoring a section is exactly
   four operations: (a) read `_progress.json` (small), (b) load section-specific
   Tier 2 inputs, (c) one targeted `Edit` replacing the section's
   `WFF-SECTION:{name}:pending` anchor with the section body, (d) update
   `_progress.json`. The agent's working memory holds at most ONE in-flight
   section body at a time. The SPEC file is write-only after the skeleton is
   laid down.

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
     replaced (`! grep "WFF-SECTION:.*:pending" SPEC_PATH`; if empty, run the
     Finalization step — set `_progress.json.status: COMPLETED` with `completed_at`).
   - On REPAIR: ONE initial bounded read (offset/limit, max 80 lines) around
     the affected section to confirm placeholder state.

---

## Quick Start
Analyze all upstream SDLC artifacts (PRD, Epics, User Stories, ADRs, Architecture,
Domain Boundaries) and optional source code to produce a single agent-native
research spec with full traceability.

Output is **2 files**: `RESEARCH-SPEC-{SESSION_ID}.md` + `RESEARCH-AUDIT-{SESSION_ID}.md`.
No prose. No narrative. No document navigation. Only structured data the
planning agent needs to execute Plan/Implement cycles.

**When to use this skill (vs alternatives):**

| Scenario | Skill |
|----------|-------|
| Isolated defect fix with a bug ticket | researching-bug-fixing |
| Implementing a story/feature into an existing app | researching-feature-impl |
| Full build with PRD, Epics, Stories, ADRs | **researching-code-design** (THIS) |

## Known Failure Modes
<!-- ACCUMULATING — appended by calibrating-updates (WS6). Newest first. Rules MUST be generic/behavioral (project-agnostic); project-specific fixes go to context packs, never here. Format + entry rules: engineering-skills/references/known-failure-modes-format.md. Read these at pre-flight so a lesson learned once recurs no more. -->

## Anti-Patterns (do NOT)
<!-- ACCUMULATING — appended by calibrating-updates (WS6). One line each: **AP-NNN** (ISO-date, source: REC-NNN): prohibition — why. -->

## Output Architecture

```
{research_output_path}/
├── RESEARCH-SPEC-{SESSION_ID}.md   ← Single agent-native spec (19 sections)
└── RESEARCH-AUDIT-{SESSION_ID}.md  ← Session audit trail (metadata only)
```

**Why 2 files (not 22):** Agent-native specs use zero-prose structured data,
producing 60-70% smaller output than 20 human-readable documents. The entire spec
fits in a single file (typically 600-2,000 lines).

**Human-readable output:** Not produced by this skill. Use `humanize-spec` skill
with the `code-design-research` rendering profile to generate the original 20+1
human-readable document set on demand.

**Downstream consumer:** planning-code-tasks (FULL-SDLC scope).

**Spec sections and structure:** See `references/code-design-research-template.md`
for the complete 19-section spec structure with example entries.

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_name | string | Yes | Project identifier |
| prd_path | string | Yes | Path to Product Requirements Document |
| epics_path | string | Yes | Path to Epics Backlog document |
| user_stories_path | string | Yes | Path to User Stories Backlog document |
| target_architecture | string | Yes | Path to Target Architecture Specifications document |
| adr_path | string | Yes | Path to Architecture Decision Records (summary or directory) |
| domain_boundaries_path | string | Yes | Path to Domain Boundary Analysis document |
| source_path | string | No | Path to existing source code (empty for greenfield) |
| context_pack_path | string | No | Tech-policy, arch-standards, coding-standards |
| test_strategy_path | string | No | Path to existing Test Strategy document |
| test_planning_path | string | No | Path to existing Test Planning document |
| test_cases_path | string | No | Path to existing Test Cases document |
| legacy_docs_path | string | No | Path to Legacy documentation or analysis |
| design_specs_path | string | No | Path to UI/UX specs, wireframes, design tokens, or mockup descriptions (markdown / text). When present, DESIGN_CONTEXT.specs is loaded (Tier 1) and referenced by `file_specifications`, `acceptance_criteria`, and `patterns_conventions`. Applies to greenfield UI work or brownfield UI changes — both feature-impl and full code-development scopes. |
| design_images_path | string | No | Path to a directory of UI/UX design image files (PNG/JPG/SVG). When present, file list (filename + dimensions + screen hint from filename) is enumerated into DESIGN_CONTEXT.images. **Do NOT embed image binaries** — reference filenames only. Downstream skills (planning, implementation) may open individual images on demand. |
| feature_id | string | No | Optional artifact scope. When empty, Step 1 derives an effective scope from the current task/comment or `task_description_path`, mirroring the quick-fix `EFFECTIVE_FEATURE_ID` pattern. |
| task_description_path | string | No | Optional current task/intent file. When this is the only task-specific input, use it both as research input and as the preferred source for derived scope. |
| research_output_path | string | No | Pre-composed output folder. When invoked via capability, this includes explicit `feature_id` scope when set: `{output_folder}/{feature_id}/research-output`; without `feature_id` it may be flat (`{output_folder}/research-output`). If `feature_id` is empty and an effective scope is derived, Step 1 writes to `{dirname(research_output_path)}/{scope_slug}/{basename(research_output_path)}` and reports that actual path. Standalone default: `./research/` |
| failure_feedback | string | No | Feedback from a previous failed run (triggers REPAIR mode) |
| custom_message | string | No | Optional focus directives. Processing: applied as additional constraints during generation. If it names specific sections → prioritize depth there. If it names specific concerns → add to open_questions if unresolvable. Never overrides upstream consistency rules. |

## Workflow

### Step 1: Initialize

**OPERATION_MODE detection:**
- `failure_feedback` exists and is not empty → `OPERATION_MODE = REPAIR`. Parse failure_feedback → REPAIR_DIRECTIVES `[{ section, item_id, instruction, reason }]`. If no structured targets found → `REPAIR_DIRECTIVES = [{ section: "global", instruction: failure_feedback }]`.
- Otherwise → `OPERATION_MODE = BUILD`.

**BUILD_CONTEXT detection:**
- `source_path` exists and contains code → `BUILD_CONTEXT = BROWNFIELD`
- Otherwise → `BUILD_CONTEXT = GREENFIELD`

Note: These are orthogonal. A REPAIR can target a BROWNFIELD project. The spec header carries both: `mode: {BUILD | REPAIR}`, `build_context: {GREENFIELD | BROWNFIELD}`.

**Zero Invention Policy:**
Every factual claim MUST trace to an upstream artifact. If source data is missing → `status: pending` + open_questions entry. NEVER invent. Technology names/versions ONLY from ADRs or source code.

**Artifact fidelity extraction mandate:**
When extracting from upstream artifacts, capture explicit artifact-shaping details
without rewriting them into a looser interpretation. This includes identifiers,
field/column/property names, enum members, constants, paths, routes, query
predicates, ordering clauses, validation rules, configuration keys, dependency
coordinates, file names, and contract shapes. If an upstream artifact expresses
behavior in a structured form, preserve that structure in the extracted context
or mark the gap as pending — do not collapse it into a summary that loses
implementation-relevant detail.

**Path Resolution:**
```
RAW_RESEARCH_OUTPUT_PATH = research_output_path (or derived default "./research/")

## Resolve EFFECTIVE_FEATURE_ID using the same class-vs-instance behavior as quick-fix.
## Pick the first source that resolves:
##   a. feature_id parameter, if non-empty.
##   b. Explicit scope in this prompt's current task/comment text, including
##      `custom_message`, Additional Instructions, or current run context.
##      Recognize forms such as `scope: <x>`, `feature: <x>`, ticket/story ids
##      (`JIRA-1234`, `US-008`, `BUG-003`), or concise task names.
##   c. task_description_path, when it points to one task/intent file. Prefer an
##      explicit id in the file or filename. Otherwise derive from the first H1/title
##      or first meaningful sentence.
##   d. NONE. Do not invent a scope if no task-specific signal exists.
##
## Normalize SCOPE_SLUG: lowercase, replace non-alphanumeric runs with `-`,
## trim leading/trailing `-`, and cap at 48 characters without cutting a word
## when practical. Examples:
##   "CRM mock" -> crm-mock
##   "python script to list primes" -> python-script-list-primes
##   "JIRA-1234" -> jira-1234

IF feature_id parameter is non-empty:
  EFFECTIVE_FEATURE_ID = feature_id
  SCOPE_SLUG = normalized(feature_id)
  SPEC_FOLDER = RAW_RESEARCH_OUTPUT_PATH
ELSE IF a scope was derived from task/comment or task_description_path:
  EFFECTIVE_FEATURE_ID = derived scope label
  SCOPE_SLUG = normalized(EFFECTIVE_FEATURE_ID)
  IF basename(dirname(RAW_RESEARCH_OUTPUT_PATH)) == SCOPE_SLUG:
    SPEC_FOLDER = RAW_RESEARCH_OUTPUT_PATH
  ELSE:
    SPEC_FOLDER = dirname(RAW_RESEARCH_OUTPUT_PATH) + "/" + SCOPE_SLUG + "/" + basename(RAW_RESEARCH_OUTPUT_PATH)
ELSE:
  EFFECTIVE_FEATURE_ID = ""
  SCOPE_SLUG = ""
  SPEC_FOLDER = RAW_RESEARCH_OUTPUT_PATH

CREATE SPEC_FOLDER if not exists

IF MODE = BUILD:
  SESSION_ID    = sourced from execution metadata per execution-protocol.md Section 1
                  when present. If no typed id is provided, generate:
                  - scope resolved: RESEARCH-{PROJECT_NAME_UPPER}-{SCOPE_SLUG_UPPER}-{YYYYMMDD}
                  - no scope:       RESEARCH-{PROJECT_NAME_UPPER}-{YYYYMMDD}
  PREVIOUS_VERSION = 0
  NEW_VERSION      = "1.0.0"

ELSE IF MODE = REPAIR:
  FIND files in SPEC_FOLDER matching "RESEARCH-SPEC-*.md"
  IF no matching file exists:
    FAIL: "REPAIR mode requires an existing RESEARCH-SPEC-*.md in SPEC_FOLDER"
  SELECT the most recently modified matching file
  SPEC_FILE        = basename of selected file
  SESSION_ID       = SPEC_FILE with prefix "RESEARCH-SPEC-" and suffix ".md" removed
  PREVIOUS_VERSION = parse version: field from existing spec header (default 1 if absent)
  NEW_VERSION      = PREVIOUS_VERSION + 1

SPEC_PATH  = "{SPEC_FOLDER}/RESEARCH-SPEC-{SESSION_ID}.md"
AUDIT_PATH = "{SPEC_FOLDER}/RESEARCH-AUDIT-{SESSION_ID}.md"
```

**FIRST ACTION — MANDATORY:** Write `_progress.json` to the output folder before any other file write.
This prevents the orchestrator from sending SIGINT. See execution-protocol.md Section 2 for the schema.

**If MODE == REPAIR: READ** `references/repair-mode.md` **NOW** for the REPAIR
mechanics that govern Step 3 generation.

**Execution:** automated

---

### Step 1.5: Scope Triage Gate (mandatory pre-author check)

Before reading any upstream artifact in detail, compute a scope complexity
estimate from file-size and count signals only (no LLM reasoning yet). If the
estimate exceeds the configured envelope, write a Gap Report and exit cleanly
with `SCOPE_REFUSED`. The downstream coordinator MUST then surface the
reduce-scope guidance to the operator — do NOT retry the same scope.

**Inputs to the estimate (cheap signals only — `wc -l` / `ls` / `grep -roc`):**

If `task_description_path` points to an existing single task/intent file and one
or more full-SDLC upstream artifacts are absent, run in `TASK_DESCRIPTION_ONLY`
mode for triage: set `US_COUNT = 1`, `BC_COUNT = 0`, `ADR_COUNT = count existing
ADR files if any else 0`, and compute `OPEN_Q_HINT` from the task description.
Do not scan stale PRD/Epic/Story folders to infer a different task.

```
US_COUNT          = count of user-story files under user_stories_path (or stories listed in epics_path)
BC_COUNT          = count of bounded-context files referenced under domain_boundaries_path
                    (fallback: count distinct top-level service folders under source_path/src)
ADR_COUNT         = count of ADR-*.md files under adr_path
OPEN_Q_HINT       = count of "[to be identified]", "[TBD]", "[?]" tokens across
                    PRD + Epics + Stories (single grep -roc)
EPIC_HEAVY        = 1 if any single epic file > 800 lines OR > 25 KB; else 0
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

**Decision table (code-design thresholds):**

| SCORE   | Verdict           | Action                                                    |
|---------|-------------------|-----------------------------------------------------------|
| `<= 15` | SAFE              | Proceed to Step 1.6.                                      |
| `16–30` | BORDERLINE        | Proceed BUT write a WARNING into `_progress.json` (`scope_warning: true`, `recommend_split_after: <N> sections`). Continue authoring. |
| `> 30`  | **SCOPE_REFUSED** | **STOP authoring. Write Gap Report. Exit.**               |

**Hard rule (independent of SCORE):** if `US_COUNT > 3 AND BC_COUNT > 1`
→ SCOPE_REFUSED. Epic-level research at this scale cannot finish within the
iteration budget.

**On SCOPE_REFUSED:**

1. Update `_progress.json`:
   ```json
   {
     "status": "SCOPE_REFUSED",
     "score": <computed>,
     "us_count": <N>,
     "bc_count": <N>,
     "recommended_decomposition": "per-US"
   }
   ```
2. Write `RESEARCH-AUDIT-{SESSION_ID}.md` with a single section `## Gap Report — SCOPE_REFUSED`:
   ```markdown
   # RESEARCH-AUDIT (Gap Report)
   verdict: SCOPE_REFUSED
   score: <N>   (threshold: 30)
   us_count: <N>
   bc_count: <N>
   adr_count: <N>
   open_q_hint: <N>

   ## Recommended decomposition
   Run `researching-feature-impl` once per user story under this scope:
   - <list of US IDs detected>

   ## Why the gate triggered
   Epic-level research at this complexity cannot reliably finish within the
   agent's iteration budget. Prior calibration evidenceconfirms monolithic specs at this scale hit the cap
   before completion.

   ## To proceed
   Either:
   (a) Split this scope into per-US `researching-feature-impl` runs, OR
   (b) Reduce the scope to <= 3 user stories AND <= 1 bounded context, OR
   (c) If you understand the risk, override by setting `scope_triage_override: true`
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
Step 1.6. The override exists so a human can force epic-level research after
weighing the risk — default behavior is REFUSE.

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

IF _progress.json.status == "COMPLETED":
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

### Step 2: Input Validation + Context Extraction

> **Before any discovery scan — apply execution-protocol.md Section 13 (Code-Location Discipline).** Read `context-pack/codebase-map.md` (and `project-inventory.md` if present) to locate the modules and call sites the design touches BEFORE running a repository-wide `grep`/`glob`/`find` to discover where they live — **consult before scan, not never scan**. Read the specific files the map names directly; fall back to a scoped scan only where the map is absent or insufficient, and flag that gap in the research output so the map can be corrected. Map first (§13), then delegate the residual sweep (§12).
>
> **During context extraction — apply execution-protocol.md Section 12 (Delegated Exploration) if your harness supports it.** Broad read-only sweeps for this skill (e.g. mapping the modules and call sites the design touches, surveying existing structural conventions to align with) MAY be delegated to a read-only exploration subagent on a cheap/fast model, which returns conclusions + `file:line` pointers (not file dumps). Synthesis, design decisions, and all writing stay with this agent, which verifies any delegated `file:line` before using it (Zero-Invention still applies). With no subagent capability, explore inline under the usual scope constraint — output quality is identical either way.

```
## 2A. STOP-GATE: Validate Required Inputs

REQUIRED_INPUTS = [
  { name: "PRD",           path: prd_path },
  { name: "Epics",         path: epics_path },
  { name: "User Stories",  path: user_stories_path },
  { name: "Architecture",  path: target_architecture },
  { name: "ADRs",          path: adr_path },
  { name: "Domain Bounds", path: domain_boundaries_path }
]

MISSING = []
FOR EACH input IN REQUIRED_INPUTS:
  IF input.path is empty OR file does not exist:
    MISSING.append(input)

TASK_DESCRIPTION_AVAILABLE = task_description_path is non-empty AND file exists

IF MISSING is not empty AND TASK_DESCRIPTION_AVAILABLE:
  INPUT_MODE = "TASK_DESCRIPTION_ONLY"
  Read task_description_path completely as TASK_DESCRIPTION_CONTEXT.
  Treat TASK_DESCRIPTION_CONTEXT as the authoritative current intent for this run.
  Do not merge unrelated PRD/Epic/Story content from stale project folders.
  Record each missing full-SDLC artifact as `status: pending` in open_questions,
  but proceed with research from TASK_DESCRIPTION_CONTEXT + source/context-pack.

IF MISSING is not empty AND NOT TASK_DESCRIPTION_AVAILABLE:
  WRITE gap report to {SPEC_FOLDER}/RESEARCH-GAP-REPORT.md
  EXIT — do not proceed

IF MISSING is empty:
  INPUT_MODE = "FULL_SDLC"
  If TASK_DESCRIPTION_AVAILABLE, read it as a supplemental current-intent constraint
  and reconcile it against PRD/Epics/Stories with conflicts recorded in open_questions.

## 2B. Two-Tier Context Loading

**Why two tiers:** Full SDLC runs produce 6+ upstream artifacts totaling 8,000+ lines.
Loading all content into a single prompt causes 1.5-2M token prompts that trigger
504 Gateway Timeouts. The architecture skills (researching-adrs, specifying-architecture)
avoid this with manifest-first reading + per-item selective loading. This skill
follows the same pattern.

**Token budget target:** Tier 1 (always loaded) ≤ 120K tokens. Tier 2 (on-demand)
adds ≤ 15K tokens per section, flushed after each section is written.

---

### TIER 1 — Always loaded (stays in context for the entire generation)

When `INPUT_MODE = TASK_DESCRIPTION_ONLY`, Tier 1 is:
- `TASK_DESCRIPTION_CONTEXT` from `task_description_path`.
- Relevant source/context-pack files discovered through targeted reads.
- Any optional architecture/ADR/design artifacts that actually exist.

In this mode, every section that normally cites PRD/Epics/Stories must cite
`TASK_DESCRIPTION_CONTEXT` instead, and missing full-SDLC artifact categories
must remain `status: pending`; do not fill them from stale folders.

**Upstream contract auto-detection.** For each loaded PRD, Epics, and Stories
artifact, detect `contract_mode` without a parameter:
- `structured`: artifact declares `contract_format: structured`, required
  structured fields parse, and upstream validation/certified completeness says
  those fields are complete.
- `partial`: artifact has some structured fields, or declares
  `contract_format: structured` but fails its own contract during WARN-mode
  rollout. Use available structured rows, but still run the unstructured
  extraction as a cross-check.
- `unstructured`: artifact has no structured contract fields. Treat it as a
  valid external/client/vendor input and use today's re-derivation behavior.

Required structured fields are:
- PRD: `content_hash`, `literal_registry`, enriched `open_questions`
  (`affected_ids`, `blocking`, `fallback_behavior`), and globally qualified AC
  IDs.
- Epics: `prd_source_hash`, `prd_id_ownership`, enriched `open_questions`.
- Stories: `prd_source_hash`, `epics_source_hash`, globally qualified AC IDs,
  literal/fallback refs where present, and enriched `open_questions`.

**Hash format gate.** Any field named `content_hash`, `*_source_hash`, or
`source_hash` that participates in structured-mode validation MUST match
`^[a-f0-9]{64}$`. A missing value, a session ID, an mtime, or any other
non-SHA-256 placeholder means the artifact is not fully structured for this
research run. Demote it to `partial`, run the prose cross-check, and add an
`evidence_gaps` row explaining the invalid hash field. Do not emit
`hash_status: match` for a non-SHA value.

In `partial` mode, structured fields are authoritative for the rows they
declare, but never sufficient proof of completeness. Cross-check prose-derived
IDs, literals, fallbacks, and ownership against the structured rows; any
unregistered prose value becomes `open_questions.evidence_gaps`, not silent
trust. Only `structured` mode with certified completeness may skip the
cross-check.

Use SHA-256 content hashes only; never use mtime. If an upstream declared hash
mismatches the current source content, do not edit the upstream artifact or
rewrite its declared hash. Forward-verify the recorded dependencies this research run needs
(IDs, literals, fallbacks, ownership rows). If all still exist identically,
proceed and record the decision in `RESEARCH-AUDIT.accepted_hash_overrides`
with artifact, declared_hash, observed_hash, verification_result, and decision.
If any depended-on value is absent or changed, block or require regeneration.

**Read FULL content** from these compact artifacts:

```
READ FULL → PRD-SPEC (typically 600-1200 lines)
  Extract PRD_CONTEXT:
    contract_mode:        {structured | partial | unstructured}
    content_hash:         {declared sha256 | computed sha256 | N/A}
    hash_status:          {match | mismatch_accepted | mismatch_blocked | N/A}
    accepted_hash_override:{audit row id | N/A}
    literal_registry:     {LIT-XX → exact_value, type, applies_to_ids, source_ref}
    derived_literals:     {prose-derived literals used for partial/unstructured cross-check}
    evidence_gaps:        [structured/prose discrepancies]
    fr_ids:               {FR-XX → description, priority}
    nfr_ids:              {NFR-XX → description, target}  # ORIGINAL IDs — never renumber
    jtbd_ids:             {JTBD-XX → description}
    kpi_ids:              {KPI-XX → description, target, method}
    asm_ids:              {ASM-XX → description, status}
    rsk_ids:              {RSK-XX → description, likelihood, impact}
    personas:             [persona name → goals, pain points]
    api_paths:            [concrete API paths from PRD]
    api_contracts:        [status codes, field names, response structures]
    pending_inputs:       [all PENDING INPUT / pending items with location]
    traceability_gaps:    [all items from traceability / gap tables]
    mvp_scope:            [Must Have items]
    roadmap:              [Phase → Capability → Timeline]
    upstream_gaps:        [from PRD open_questions if agent-native format]
    enhancement_suggestions: [all items from PRD Enhancement Suggestions]

READ FULL → EPICS-SPEC (typically 400-700 lines)
  Extract EPIC_CONTEXT:
    contract_mode:        {structured | partial | unstructured}
    prd_source_hash:      {declared sha256 | N/A}
    hash_status:          {match | mismatch_accepted | mismatch_blocked | N/A}
    accepted_hash_override:{audit row id | N/A}
    prd_id_ownership:     {PRD ID → owning epic(s) | cross_cutting | deferred}
    evidence_gaps:        [ownership/prose discrepancies]
    epics:                {EPIC-XX → value prop, traceability (FR/NFR/JTBD/KPI), complexity, priority}
    persona_coverage:     {EPIC-XX → [persona names]}
    risk_annotations:     {EPIC-XX → [RSK-XX, ASM-XX]}
    dependencies:         [Epic → Epic dependency pairs]
    tiers:                {Tier 1 → [EPICs], Tier 2 → [EPICs], Tier 3 → [items]}
    upstream_gaps:        [from Epics open_questions if agent-native format]

READ FULL → ARCH-FOUNDATION-SPEC (typically 400-600 lines)
  Extract ARCH_CONTEXT:
    services:             {SVC-XX → BC, responsibility, API contract, tech stack, NFR targets}
    communication:        [source → target → pattern → protocol]
    nfr_targets:          {SVC-XX → latency, availability, throughput}
    principles:           [principle → rationale]
    c4_diagrams:          [diagram type → PlantUML content]

READ FULL → {context_pack_path}/*.md if context_pack_path provided, else context-pack/*.md (typically 100-200 lines each)
  Extract STANDARDS_CONTEXT:
    coding_standards:     [convention → rule]
    tech_policy:          [layer → technology → version → constraint]
    arch_standards:       [pattern → when to apply]
```

**Read MANIFEST ONLY** from these large multi-file artifacts:

```
READ MANIFEST ONLY → STORIES-MANIFEST (catalog table, NOT individual story files)
  Extract STORY_INDEX:
    contract_mode:        {structured | partial | unstructured}
    prd_source_hash:      {declared sha256 | N/A}
    epics_source_hash:    {declared sha256 | N/A}
    hash_status:          {match | mismatch_accepted | mismatch_blocked | N/A}
    accepted_hash_override:{audit row id | N/A}
    literal_refs:         {US-XX-XX → [LIT-XX]}
    fallback_refs:        {US-XX-XX → [PI/OQ/ASM IDs]}
    evidence_gaps:        [story/prose discrepancies]
    story_catalog:        {US-XX-XX → epic_id, domain_tag, ac_count, description_one_liner}
    story_count:          COUNT(stories)
    epic_coverage:        {EPIC-XX → [US-XX-XX list]}
    personas_used:        {US-XX-XX → persona from catalog row}
    upstream_gaps:        [from manifest open_questions if present]

  DO NOT READ individual story files (epics/epic-NN.md) at this stage.
  The STORY_INDEX catalog provides IDs, epic mappings, domain tags, and AC counts —
  sufficient for 80% of sections. Individual files are loaded on-demand in Tier 2.

READ MANIFEST ONLY → ADR-SPEC (decision catalog table, NOT individual ADR files)
  Extract ADR_INDEX:
    decision_catalog:     {ADR-XXX → title, status, key_technology, rationale_one_liner}
    tech_stack_summary:   {Layer → Technology → Version}
    nfr_coverage:         {NFR-XX → [ADR-XXX addressing it]}
    risk_mapping:         {RSK-XX → [ADR-XXX mitigating it]}

  DO NOT READ individual ADR files (adrs/adr-NNN-*.md) at this stage.
  The decision catalog provides IDs, tech choices, and NFR/risk mappings —
  sufficient for most sections. Individual ADRs loaded on-demand for architecture detail.

READ MANIFEST ONLY → BOUNDARIES-SPEC (context catalog + relationship map)
  Extract DOMAIN_INDEX:
    context_catalog:      {BC-XX → name, subdomain_type, aggregate_count}
    relationship_map:     [BC-XX → BC-YY → relationship_type]
    ubiquitous_lang:      {BC-XX → [term → definition]}  # if in manifest
    domain_events:        {BC-XX → [event → type]}  # if in manifest

READ MANIFEST ONLY → ARCH-SPECS-MANIFEST (unit catalog table)
  Extract SPECS_INDEX:
    unit_catalog:         {UNIT-XX → title, scope_summary}

  DO NOT READ individual spec unit files (units/unit-NN-*.md) at this stage.
```

**Optional Tier 1 inputs** (read full if available and compact):

```
IF source_path exists (BROWNFIELD):
  SOURCE_CONTEXT:
    project_structure:  directory tree (ls -R, max 200 lines)
    existing_patterns:  [pattern → file:lines]  # selective grep, not full file reads
    conventions:        [naming, structure, error handling]
    test_framework:     [framework, commands, conventions]
    dependencies:       [library → version from build file]
    artifact_constraints: [artifact → preserved identifiers, contracts, literals, schemas, config keys]
  Budget: read build files + directory structure only. Do NOT read source files in Tier 1.

IF test_strategy_path exists:
  TEST_STRATEGY_CONTEXT:
    coverage_targets:   {level → target %}
    test_pyramid:       {unit → %, integration → %, e2e → %}
    tool_selection:     [test framework, mocking, assertions]

IF test_planning_path exists:
  TEST_PLANNING_CONTEXT:
    test_phases:        [phase → stories covered]

IF test_cases_path exists:
  TEST_CASES_CONTEXT:
    test_cases:         {TC-XX → description, type, priority, story mapping}
    coverage_mapping:   {US-XX-XX → [TC-XX list]}

IF legacy_docs_path exists:
  LEGACY_CONTEXT:
    existing_systems:   [system → current state]
    migration_notes:    [breaking changes, deprecations]
    patterns_to_preserve: [pattern → rationale]

IF design_specs_path exists OR design_images_path exists:
  DESIGN_CONTEXT = {
    specs: {                                  # populated from design_specs_path when present
      screens:        [screen_name → purpose, components, states, route_hint]
      components:     [component_name → variants, props_hint, source_screen]
      interactions:   [flow_name → trigger, steps, outcome]
      design_tokens:  [token → value (color/typography/spacing)]
      responsive:     [breakpoint → behavior]
      accessibility:  [requirement → scope (a11y notes from specs)]
    },
    images: {                                 # populated from design_images_path when present
      files: [{ filename, dimensions_px, screen_hint, format }]   # filename only, NEVER binaries
    }
  }
  Budget: read design_specs_path full content if compact (<400 lines); otherwise
  read manifest/index + load individual screen files on demand. For design_images_path,
  enumerate with `ls -la` only — do NOT cat binary files.
ELSE:
  DESIGN_CONTEXT = null  (backend-only project, or UX artifacts pending)
```

---

### TIER 2 — On-demand selective loading (per section, then flushed)

When a section needs deep detail from an individual item, load it just-in-time.
After the section is written to the checkpoint file, FLUSH the loaded content.

**Selective load rules per section:**

| Section | Tier 2 load | How | Flush after |
|---|---|---|---|
| architecture | 2-3 ADRs that map to specific services (group by BC) | `cat {adr_path}/adrs/adr-NNN-*.md` for relevant ADRs only | section written |
| nfr_implementation | Spec units: unit-14 (security), unit-17 (characteristics) | `cat {target_architecture}/units/unit-14-*.md {target_architecture}/units/unit-17-*.md` | section written |
| implementation_sequencing | Individual story files, ONE EPIC at a time | `cat {user_stories_path}/epics/epic-01.md` → generate rows → flush → `cat {user_stories_path}/epics/epic-02.md` → ... | each epic processed |
| acceptance_criteria | Individual story files, ONE EPIC at a time (same per-epic pattern) | Same as implementation_sequencing | each epic processed |
| file_specifications | Spec units: unit-12 (communication), unit-13 (data), unit-16 (infrastructure) | `cat {target_architecture}/units/unit-12-*.md {target_architecture}/units/unit-13-*.md {target_architecture}/units/unit-16-*.md` | section written |
| security_assessment | unit-14 (security) — skip if already loaded for nfr_implementation | `cat {target_architecture}/units/unit-14-*.md` | section written |
| test_strategy | unit-15 (observability) + test strategy/planning docs if available | `cat {target_architecture}/units/unit-15-*.md` | section written |
| patterns_conventions | Source code files (if brownfield) — selective grep/read | Targeted file reads, not tree traversal | section written |
| dependencies | Individual ADRs for integration patterns (2-3 max) | `cat {adr_path}/adrs/adr-NNN-*.md` for communication-related ADRs | section written |

**Sections that need ONLY Tier 1 (no on-demand loading):**

| Section | Why Tier 1 is sufficient |
|---|---|
| context_inventory | Uses input paths, auto-detected contract modes, and upstream hash decisions from validation step, normalized to workspace-root-relative form (strip the workspace-root prefix; never absolute) |
| executive_metrics | Uses counts from STORY_INDEX, EPIC_CONTEXT, ADR_INDEX |
| requirements_traceability | Uses PRD_CONTEXT IDs (FR, NFR, JTBD, KPI) and EPIC_CONTEXT.prd_id_ownership when structured/partial |
| complexity_assessment | Uses metadata from prior sections (no new input) |
| risks | Uses PRD_CONTEXT.rsk_ids + ADR_INDEX.risk_mapping |
| assumptions | Uses PRD_CONTEXT.asm_ids + ADR_INDEX.asm_mapping |
| sources | Uses input paths only |
| validations | Uses IDs and counts from all prior sections |
| open_questions | Uses gaps surfaced during generation |

**NEVER LOAD simultaneously:**
- All individual ADR files (14 files, ~2100 lines, ~63K tokens)
- All individual story files (7 files, ~700 lines, ~21K tokens)
- All individual spec unit files (10 files, ~1300 lines, ~38K tokens)

These three bulk loads caused the 1.9M token blowout. The manifests provide
sufficient context for most sections; individual files are only needed for
deep-detail sections and should be loaded 1-3 at a time.

---

### Per-Epic Selective Loading Pattern (for implementation_sequencing and acceptance_criteria)

These sections need individual story details but NOT all at once:

```
FOR EACH epic_id IN EPIC_CONTEXT.tiers (tier order):
  1. READ epic story file: {user_stories_path}/epics/epic-{NN}.md
     (typically 60-130 lines per file)
  2. Extract story details for this epic:
     stories_in_epic: {US-XX-XX → full narrative, AC (Given/When/Then), DoR, DoD, tech matrix}
  3. Generate section rows for this epic's stories
  4. APPEND rows to section accumulator
  5. FLUSH stories_in_epic from context — only the generated rows survive
  6. CONTINUE to next epic

Peak context per iteration: Tier 1 (~120K) + one epic file (~3K) = ~123K
```

---

## 2C. Detect Language
DETECTED_LANGUAGE = detect from PRD or upstream artifacts. Default: English.
```

**Skeleton spec checkpoint — MANDATORY HARD GATE** (BUILD mode only).

You MUST write SPEC_PATH skeleton to disk BEFORE entering Step 3. This is not
optional and not a "checkpoint to consider" — it is a precondition gate.

Skeleton contents:
- Header metadata (version, session_id, mode: BUILD, date, language, build_context)
- `context_inventory` section populated from Tier 1 contexts (artifact source map)
- All remaining 18 sections as stubs: each stub is the section heading followed by
  `<!-- WFF-SECTION:{section_name}:pending -->` on its own line. (HTML-comment
  anchor is ASCII-safe and invisible in rendered markdown. Optional companion
  line `status: pending - will be generated in Step 3` may follow the anchor.)
- `spec_status: draft`
- `loading_strategy: two-tier` (signals to REPAIR mode which loading model was used)

After writing the skeleton, update `_progress.json`:
```json
{ "current_step": "Step 3: Generate Spec",
  "skeleton_written": true,
  "sections_completed": ["context_inventory"],
  "sections_pending": ["executive_metrics", "architecture", ..., "open_questions"] }
```

**Why this is a HARD GATE.** If you skip the skeleton write and the run dies
during Step 3 (extended thinking timeout, context overflow, orchestrator
SIGINT), 100% of the loaded Tier 1 context is lost and there is no recoverable
state for REPAIR mode. The skeleton is the only durable checkpoint.

Tier 2 items are NOT stored in the skeleton — they are loaded on-demand per section.

**Execution:** automated

---

### Step 3: Generate Spec

**Precondition:** SPEC_PATH skeleton MUST already be on disk (Step 2C HARD GATE).
If basename(SPEC_PATH) does not exist on disk → ABORT and return to Step 2C.

**EARLY-WRITE RULE — MANDATORY (silent-failure prevention).**
You MUST upgrade the FIRST section stub (`executive_metrics`) to a populated
section in SPEC_PATH within **5 tool calls** after entering Step 3 — counting
ANY tool call (think, view, bash, edit). The #1 silent-failure pattern in this
skill is "read more, think more before writing" — multi-minute thinking loops
that produce no tool calls and no on-disk progress, and trigger orchestrator
SIGINT or context overflow. If you find yourself entering a 3rd `think` block
before the first section write, STOP and write what you have, even if
incomplete (mark missing pieces `status: pending`).

**WRITE-FLUSH-FORGET PROTOCOL — MANDATORY** (also enforced by Entry Rule #6).

Section-author loop (one section per iteration; one in-flight body at a time):

```
FOR EACH section in section_catalog (generation order, respecting dependencies):
  1. status = _progress.json.sections[section.name].status
     IF status == "complete": SKIP (already authored — see Step 1.6 resume contract)
  2. LOAD only this section's Tier 2 inputs (per the Tier 2 loading pattern below).
     Do NOT re-read SPEC_PATH.
  3. Compose section body in working memory — one contiguous block of structured markdown.
  4. Single targeted Edit on SPEC_PATH:
       old_string = "<!-- WFF-SECTION:{name}:pending -->"
       new_string = body + "\n<!-- WFF-SECTION:{name}:complete -->"
     One tool call. Anchor is non-empty, > 30 chars — safe under §10.5.2 Safe-Write.
  5. Update _progress.json:
       sections[name].status = "complete"
       sections[name].iterations_used = current_iter - section_start_iter
       move name from sections_pending -> sections_completed
       last_section_completed_at: <ISO timestamp>
  6. FLUSH: discard body + Tier 2 inputs. Do not carry forward.
  7. Checkpoint budget: IF (cap - current_iter) < (remaining_sections * 20),
     mark _progress.json.status = "PARTIAL" and exit cleanly. REPAIR can resume.

FINAL VERIFICATION (single permitted post-skeleton read):
  ! grep "WFF-SECTION:.*:pending" SPEC_PATH
  IF empty: run the Finalization step (Step 5 LAST ACTION) — set status "COMPLETED"
            and completed_at. Idempotent; safe if already COMPLETED.
  ELSE: log unfinished sections and exit PARTIAL.
```

Do NOT generate all 19 sections in memory and write the whole spec at the end.
That is the anti-pattern that motivated this skill's hardening — single-shot
writes lose all work on failure and present no progress signal to operators.
Do NOT `view SPEC_PATH` between sections to "see what's done" — read
`_progress.json` instead (Entry Rule #6).

**READ** `references/code-design-research-template.md` **NOW** for the complete spec structure.
**READ** `references/consistency-rules.md` **NOW** for the 15 upstream consistency
rules that govern every section, every entry, every claim.
**READ** `references/per-section-protocol.md` **NOW** for the per-section inner
loop and `custom_message` processing.

```
## Generation Order (respects section dependencies + Tier 2 loading)

Sections are annotated with their input tier. Tier 1 = uses only pre-loaded context.
Tier 2 = needs on-demand selective loading (load → generate → flush).

context_inventory         ← Tier 1 only (input paths from validation step)
executive_metrics         ← Tier 1 only (counts from STORY_INDEX, EPIC_CONTEXT, ADR_INDEX)
architecture              ← Tier 2: load 2-3 ADRs grouped by service/BC → generate → flush
requirements_traceability ← Tier 1 only (PRD_CONTEXT FR, JTBD, KPI IDs)
nfr_implementation        ← Tier 2: load unit-14 (security), unit-17 (characteristics) → generate → flush
implementation_sequencing ← Tier 2: per-epic story loading pattern (see Step 2B)
dependencies              ← Tier 2: load 2-3 ADRs for integration patterns → generate → flush
complexity_assessment     ← Tier 1 only (uses metadata from prior sections)
security_assessment       ← Tier 2: load unit-14 (security) if not cached from nfr_implementation → flush
patterns_conventions      ← Tier 2: selective source code reads if brownfield → flush
acceptance_criteria       ← Tier 2: per-epic story loading pattern (same as impl_sequencing)
risks                     ← Tier 1 only (PRD_CONTEXT.rsk_ids + ADR_INDEX.risk_mapping)
assumptions               ← Tier 1 only (PRD_CONTEXT.asm_ids + ADR_INDEX.asm_mapping)
file_specifications       ← Tier 2: load unit-12 (comm), unit-13 (data), unit-16 (infra) → flush
test_strategy             ← Tier 2: load unit-15 (observability) + test docs if available → flush
sources                   ← Tier 1 only (input paths)
validations               ← Tier 1 only (runs checks against IDs and counts from prior sections)
open_questions            ← ALWAYS LAST, Tier 1 only (accumulated gaps from generation)
```

**DESIGN_CONTEXT consumption (when DESIGN_CONTEXT is not null):**

| Section | DESIGN_CONTEXT use |
|---------|-------------------|
| `file_specifications.core_files` | UI-bearing files (components, screens, routes) MUST reference the originating screen/component name from `DESIGN_CONTEXT.specs.screens` or `DESIGN_CONTEXT.images.files`. Add a `design_ref` column inline in the file purpose, e.g. `purpose: "renders Dashboard screen — design_ref: DESIGN_CONTEXT.screens.Dashboard"`. |
| `acceptance_criteria.phase_N_criteria` | For UI stories, include visual/interaction AC sourced from `DESIGN_CONTEXT.specs.interactions`. Annotate source as `design_specs_path` (complete) or `[Inferred — no design spec]` when DESIGN_CONTEXT is null. |
| `patterns_conventions.coding_conventions` | When `DESIGN_CONTEXT.specs.design_tokens` is populated, surface design token usage convention (e.g. "colors via tokens, not inline literals"); source = `design_specs_path`. |
| `open_questions.evidence_gaps` | If user stories reference UI screens not present in DESIGN_CONTEXT (or DESIGN_CONTEXT is null for a UI-bearing project), log a `pending` entry: "Design spec missing for screen X — UI fidelity assumptions made". |

When `DESIGN_CONTEXT == null` AND the project has UI work (detected by user-story domain_tag == FE or by FR-XX descriptions referencing screens/views), proceed using inferred UI patterns from upstream artifacts, but mark every UI-related row `status: assumption` with an ASM-XX ID and register an open_questions entry. Do NOT block — agent-native specs degrade gracefully when design inputs are unavailable.

**Authentication security defaults.** When scope includes authentication,
OAuth, sessions, identity linking, or password reset, surface these as
implementation constraints in `security_assessment`, `file_specifications`, and
`test_strategy` unless an upstream security artifact explicitly overrides them:
- Persisted password-reset tokens are secrets and must be stored hashed at rest;
  raw reset-token storage is an evidence_gap unless a binding upstream source
  explicitly accepts it.
- OAuth provider values must be validated against an explicit allow-list before
  selecting provider-specific columns, scopes, or identity fields. A fallback
  branch such as "non-google means github" is an evidence_gap.

Apply the 15 upstream consistency rules per `references/consistency-rules.md`
and the per-section protocol per `references/per-section-protocol.md`. In
REPAIR mode, follow the protocol in `references/repair-mode.md`.

During section generation, preserve artifact fidelity across all source types:
- carry forward explicit identifiers and names exactly as written upstream
- preserve structured behavior (queries, mappings, schemas, config semantics,
  dependency declarations, API contracts) instead of paraphrasing them into
  weaker abstractions
- if a section needs to summarize a source artifact, keep the implementation-
  relevant constraints intact or mark the missing detail as pending
- if two upstream artifacts conflict, surface the conflict in `open_questions`
  with source tags rather than choosing one silently

**Final draft state.** SPEC_PATH already contains all populated sections
(written incrementally by the Write-Flush-Forget loop above). At this point:
- `_progress.json.sections_pending` MUST be empty.
- `spec_status: draft` (pre-validation).
- Verify all 19 sections are populated (no remaining `status: pending — will be generated in Step 3` stubs).
  If any stub remains, return to the loop and complete that section.

**Execution:** automated

---

### Step 4: Quality Validation Gate

When `INPUT_MODE = TASK_DESCRIPTION_ONLY`, apply these checks against
`TASK_DESCRIPTION_CONTEXT` where possible. PRD/Epic/Story categories that are
absent because the run intentionally supplied only `task_description_path` are
not fabrication gaps; leave them as `status: pending` and surface them in
open_questions. Do not backfill them from stale folders.

Run ALL checks below. Fix ALL failures before writing audit.

| Check | Name | What It Verifies | AUTO-CORRECT |
|-------|------|-----------------|--------------|
| CHECK 1 | fr_coverage | Every FR-XX in PRD appears in requirements_traceability | Insert missing FRs with status: pending |
| CHECK 2 | nfr_id_preservation | Every NFR-XX preserved with ORIGINAL ID (not renumbered) | Fix renumbered IDs, insert missing |
| CHECK 3 | jtbd_coverage | Every JTBD-XX appears in requirements_traceability | Insert with status: pending |
| CHECK 4 | kpi_coverage | Every KPI-XX appears in requirements_traceability | Insert with status: pending |
| CHECK 5 | rsk_carry_forward | Every RSK-XX from PRD appears in risks section | Insert missing risks |
| CHECK 6 | asm_carry_forward | Every ASM-XX from PRD appears in assumptions section | Insert missing assumptions |
| CHECK 7 | persona_coverage | Every persona from PRD referenced in executive_metrics.persona_capability_map | Insert missing personas |
| CHECK 8 | technology_fidelity | Every tech reference in architecture section exists in ADR_INDEX.tech_stack_summary or SOURCE_CONTEXT | Fix to ADR version or mark status: assumption |
| CHECK 9 | api_path_fidelity | Every API path in spec exists in PRD_CONTEXT.api_paths | Fix drifted paths or mark status: assumption |
| CHECK 10 | upstream_gap_surfacing | All PRD pending_inputs and traceability_gaps surfaced in open_questions | Insert missing items |
| CHECK 11 | story_count | STORY_INDEX.story_count matches executive_metrics.counts.user_stories | Fix reported count |
| CHECK 12 | anti_fade | Depth of first section matches last content section | Expand thin sections |
| CHECK 13 | adr_cross_reference | Every ADR-XXX referenced somewhere in spec | Route to open_questions if no relevant content (UNFIXABLE) |
| CHECK 14 | section_completeness | All 19 sections present | Generate missing sections |
| CHECK 15 | cross_section_consistency | session_id, project_name, date consistent throughout | Fix inconsistencies |
| CHECK 16 | id_uniqueness | No duplicate IDs within any section | Deduplicate |
| CHECK 17 | source_tags | Every item with status: complete has a source tag | Items without source → status: assumption + open_questions (UNFIXABLE) |
| CHECK 18 | bias_detection | No technology names or complexity/risk ratings without source evidence | Add source evidence or mark status: assumption |
| CHECK 19 | artifact_fidelity | Explicit upstream identifiers, literals, constraints, and structured semantics are preserved without silent reinterpretation | Restore exact upstream detail or downgrade to pending/open_questions |
| CHECK 20 | contract_mode_detection | PRD/Epics/Stories modes are detected as structured, partial, or unstructured and recorded in context_inventory; structured mode is forbidden when any required hash field is absent or not 64-char lowercase SHA-256 | Record mode and extraction basis; demote invalid declared-structured artifacts to partial with evidence_gaps; unstructured is valid |
| CHECK 21 | structured_cross_check | In partial mode, prose-derived IDs/literals/fallbacks/ownership are cross-checked against structured rows and discrepancies become evidence_gaps | Add missing evidence_gaps or demote invalid structured artifact to partial in WARN-mode |
| CHECK 22 | hash_forward_verification | Only SHA-256 hashes are treated as hashes; SHA-256 mismatches are forward-verified against recorded dependencies; accepted mismatches are audit-only and never upstream edits | Demote non-SHA hash placeholders to partial/evidence_gap; add accepted_hash_overrides audit row for real SHA mismatches or block when dependency changed |

**STOP-GATE:** If any CHECK has 0/{N} result (complete miss of a mandatory category) → attempt re-generation of affected section (max 2 retries). If still failing → write partial spec with failures in open_questions.

After all checks pass: update spec with auto-corrections, rebuild open_questions from scratch, write corrected spec to disk. Set `spec_status: complete` (or `draft` if validation failures exist).

**READ** `references/quality-gates.md` **NOW** for Common Rationalizations, Red
Flags, and the Verification Checklist. Apply each item before writing the spec
to disk — these catch superficial research before it ships.

**Execution:** automated

---

### Step 5: Write Outputs

**Validated spec checkpoint**: Write SPEC_PATH with all 19 sections, auto-corrections applied,
open_questions rebuilt from scratch. `spec_status: complete` (or `draft` if validation failures remain).

Write AUDIT_PATH (`RESEARCH-AUDIT-{SESSION_ID}.md`) with the following structure:

```
# {project_name} — Code Design Research Audit Trail
version: {NEW_VERSION}
previous_version: {PREVIOUS_VERSION or N/A}
session: {SESSION_ID}
operation_mode: {BUILD | REPAIR}
build_context: {GREENFIELD | BROWNFIELD}
input_mode: {FULL_SDLC | TASK_DESCRIPTION_ONLY}
effective_feature_id: {EFFECTIVE_FEATURE_ID or N/A}
research_output_path: {SPEC_FOLDER}
contract_modes: {PRD: structured|partial|unstructured|N/A, Epics: ..., Stories: ...}
date: {ISO 8601}
language: {DETECTED_LANGUAGE}

## sources
1. Task Description: {task_description_path} — {loaded | missing | not provided}
2. PRD: {prd_path} — {loaded | missing}
3. Epics: {epics_path} — {loaded | missing}
4. User Stories: {user_stories_path} — {loaded | missing}
5. Architecture: {target_architecture} — {loaded | missing}
6. ADRs: {adr_path} — {loaded | missing}
7. Domain Boundaries: {domain_boundaries_path} — {loaded | missing}
[Optional sources listed if present]

## generation_summary
| section | status | key_outputs |

## decisions
1. {decision} — Reason: {reason}

## accepted_hash_overrides
| artifact | declared_hash | observed_hash | verification_result | decision |
|----------|---------------|---------------|---------------------|----------|

## evidence_gaps
| id | artifact | affected_ids | description | decision |
|----|----------|--------------|-------------|----------|

## custom_message_applied
{How custom_message influenced generation, or "N/A"}

## repair_changes (REPAIR mode only)
| directive | target | instruction | outcome |

## validation_summary
| check | result |
```

Verify both SPEC_PATH and AUDIT_PATH exist and are non-empty.

Memory Bank artifact type: `"{N} research-docs"` (exact count of files written).

**Memory Bank — MANDATORY session-end writes:**
1. Overwrite `context-pack/active-context.md` with session status, decisions, blockers, key artifacts.
   Log all research decisions to the Decisions Log table (see execution-protocol.md Section 4 for schema).
2. Append one milestone row to `context-pack/progress.md` with artifact count above.

**Section 2 LAST ACTION — MANDATORY (Finalization step):** Single authoritative
finalization. Idempotent — safe to run even if already COMPLETED:
1. Read `_progress.json`.
2. Verify `sections_pending` is empty AND `! grep "WFF-SECTION:.*:pending" SPEC_PATH`
   returns nothing. If either is non-empty → do NOT finalize; set status `PARTIAL`
   and exit cleanly (REPAIR resumes).
3. Set `status: COMPLETED` and `completed_at: <ISO timestamp>`.
4. Write `_progress.json`.
If the session failed, set status to `FAILED` with `completed_at` instead.

**Execution:** automated

---

### Step 6: Emit Harness Outputs Sidecar

**Apply execution-protocol.md Section 11** — Harness Output Sidecar. Mandatory when the prompt contains a `## Run metadata` block. This is the FINAL file write of the run (after SPEC/AUDIT verification, after Memory Bank, after `_progress.json` set to COMPLETED). Without it, the orchestrator falls back to the capability `value_template`, which corrupts `research_output_path` into a doubly-nested folder when the parameter has already been pre-resolved to an absolute path.

**Output parameters this skill produces** (one key per row of the prompt's `## Output parameters` table):

- `research_output_path`: the actual `SPEC_FOLDER` / `EFFECTIVE_RESEARCH_OUTPUT_PATH` written in Step 1. If `feature_id` was empty and Step 1 derived a scope, report the nested path here, not the flat `research_output_path` parameter. Do NOT re-prepend `{output_folder}`, `{project_name}`, or `{feature_id}`.

**Implementation:** the harness here accepts Bash heredoc for the sidecar write (the sidecar is NOT the SPEC_FILE, so §10.5's anti-Bash rule does not apply). Execute:

```
cat > {stepwise_outputs_file} << 'OUTPUTS_EOF'
{ "research_output_path": "{SPEC_FOLDER}" }
OUTPUTS_EOF
```

Replace `{SPEC_FOLDER}` with the actual resolved folder from Step 1. `{stepwise_outputs_file}` is the path from the prompt's `## Run metadata` block's `output_file = '...'` line — copy it verbatim, do NOT reconstruct it.

Self-check: `cat {stepwise_outputs_file}` — verify non-empty. If empty or missing, re-execute. DO NOT describe output registration in response text — EXECUTE it. No tool calls after this; the next event is `final_response`.

**Execution:** automated

---

## Reference Files

| File | Load when | Purpose |
|------|-----------|---------|
| `references/code-design-research-template.md` | Step 3 | RESEARCH-SPEC 19-section structure with example entries |
| `references/consistency-rules.md` | Step 3 — once at section-generation start | The 15 Upstream Consistency Rules + Schema Literal Preservation |
| `references/per-section-protocol.md` | Step 3 — applied per section | Per-section inner loop (Zero Invention, Source Fidelity) and custom_message processing |
| `references/repair-mode.md` | Step 1 only if OPERATION_MODE == REPAIR | REPAIR mechanics: load existing spec, regenerate targeted sections, preserve untargeted, increment version |
| `references/quality-gates.md` | Before Step 5 final write | Common Rationalizations, Red Flags, Verification Checklist |
| `context-pack/execution-protocol.md` | As referenced | Session ID, _progress.json lifecycle, Memory Bank, REPAIR Section 7 |
