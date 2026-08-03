---
name: validating-architecture-compliance
description: >
  VGT-ready pre-implementation gate that validates user stories / epics against
  the target architecture (and ADRs) for compliance. Unidirectional check —
  architecture is the immutable baseline; stories are evaluated against it.
  Per-story verdict is one of Approve / Return-to-Product / Initiate-ADR, rolled
  up into a closed-set compliance_status: PASSED / PARTIAL / FAILED. Six
  compliance areas are assessed: technology, pattern, component-service
  ownership, integrations, data, NFRs (performance + security). Output is a
  single agent-native COMPLIANCE-SPEC file plus an audit and Stepwise sidecar.
  Zero Invention Policy. BUILD and REPAIR modes. Sits between
  implementing-user-stories (input) and platform-export (downstream — only
  stories with PASSED compliance cross the gate). Human-readable output via
  humanize-spec.
license: Proprietary
metadata:
  author: aipods-team
  version: 1.2.0
  category: architecture
  tags: compliance, architecture-gate, user-stories, ADR, FIC, agent-native
---

# Validating Architecture Compliance — Agent-Native Spec

## SKILL PROTOCOL — ENTRY RULES (read first, do not skip)

1. **The protocol below is internally consistent.** If you perceive a conflict
   between the capability prompt and this skill, the skill wins for execution
   mechanics; the capability wins for paths/parameters. Do NOT exit citing
   "ambiguity" or "internal contradiction".

2. **Begin Step 1 (Initialize) immediately.** Step 1's first action (write
   `_progress.json` to `compliance_output_path`) IS the verification.

3. **Reference files load on demand via `cat`** when each step's `READ`
   pointer says so. They are NOT preloaded.

4. **Authority Boundary (NON-NEGOTIABLE).** This skill assesses; it never
   modifies the architecture. Recommend `Return to Product` for adjustable
   gaps and `Initiate ADR` for ASD changes. NEVER suggest specific replacement
   technologies or patterns — those decisions belong to the ADR process.

5. **Zero Invention Policy is non-negotiable.** Every gap finding MUST cite a
   specific architecture section (UNIT, principle, ADR id, NFR id) AND the
   exact story acceptance criterion or business rule it conflicts with.
   Asking the human a clarifying question = task FAILURE.

6. **No final response until COMPLIANCE-SPEC + COMPLIANCE-AUDIT exist on disk.**
   The 6 compliance areas MUST all be assessed for every story — partial
   coverage is a quality defect, not a permitted shortcut.

---

## Quick Start

Read every user story under `user_stories_path`, evaluate it against the target
architecture (and ADRs), produce a per-story verdict (Approve / Return-to-Product
/ Initiate-ADR) with cited gaps, roll those verdicts up into a VGT-ready
`compliance_status` (`PASSED` / `PARTIAL` / `FAILED`), and write a single
agent-native COMPLIANCE-SPEC.

```
{compliance_output_path}/
├── COMPLIANCE-SPEC-{SESSION_ID}.md     ← Per-story verdicts + gap registry + summary
├── COMPLIANCE-AUDIT-{SESSION_ID}.md    ← Sources, classification log, validations, open_questions
└── _progress.json                      ← Liveness signal
```

**Why single file:** Output is one file because downstream consumers (`platform-export`)
expect one path. This does **NOT** mean the spec is generated in a single inference
call. This skill applies the **section-shape protocol** defined in
`context-pack/execution-protocol.md` Section 10: skeleton-first + one-section-per-write
+ CONTINUE on re-entry. Per-story evaluations are emitted into the single COMPLIANCE-SPEC
file via targeted edits — one story per `Edit` call. Tool discipline (§10.5) is
mandatory; the non-ASCII fallback (§10.5.1) auto-applies when story content contains
non-English text.

**Human-readable output:** Not produced by this skill. Use `humanize-spec` with
profile `architecture-compliance` to render a human-friendly compliance report
(per-story sections, summary table, action items for Product and Architecture teams).

## Pipeline Position

```
[implementing-user-stories]              (per-epic story files + manifest)
       +
[establishing-architecture-foundation]   (target architecture)
[specifying-architecture]                (UNIT files: communication, data, security, infra, NFR, …)
[researching-adrs]                       (ADRs)
       +
[generating-toolchain-record] (optional) (DTR — supplies tool-state context)
       ↓
[validating-architecture-compliance]     ← YOU ARE HERE
       ↓
   ┌───┴────────────────────────────────┐
   ↓ compliance_status = PASSED          ↓ PARTIAL / FAILED
[human quality gate → platform-export]  [PARTIAL: retry product stories via VGT;
                                        FAILED: escalate to architecture/human]
```

## VGT Compliance Contract

`compliance_status` is the closed-set verdict used by Stepwise VGT routing:

| Status | Meaning | Recommended route |
|--------|---------|-------------------|
| `PASSED` | Every in-scope story has per-story verdict `APPROVE`; no validator integrity failures. | Proceed to human backlog/compliance gate, then platform export. |
| `PARTIAL` | At least one story is `RETURN_TO_PRODUCT` and zero stories are `INITIATE_ADR`; gaps are requirement-adjustment issues. | Automated VGT retry to `backlog-story-generation` with `compliance_feedback`. |
| `FAILED` | At least one story is `INITIATE_ADR`, or this validator could not complete its own integrity checks. | Do not auto-retry backlog blindly; send to human gate for architecture escalation or validator repair. |

`PARTIAL` is repairable by Product story regeneration. `FAILED` is not assumed
repairable by Product because an ADR/architecture decision may be required.

## Compliance Areas (all 6 mandatory per story)

| # | Area | What it checks |
|---|------|----------------|
| 1 | Technology fit | Does the story require a tech category not in the architecture stack? |
| 2 | Architecture pattern fit | Does the story fit the documented patterns (REST, event-driven, CQRS, …)? |
| 3 | Component / service fit | Can an existing service own this capability, or would a new one be needed? |
| 4 | Integration fit | Are required integrations defined in the architecture? |
| 5 | Data fit | Does it use architecture-defined data stores / models? |
| 6 | NFR fit | Both subareas: (6a) Performance vs SLOs; (6b) Security vs controls. Citing one does NOT satisfy the other. |

Skipping any area = quality defect — Step 4 validation fails.

## Verdict Decision Tree

```
For each story:

1. Run all 6 compliance checks. Collect gaps.

2. IF gaps is empty:
     verdict = APPROVE

3. ELIF every gap can be resolved by adjusting the requirement (no architecture change):
     verdict = RETURN_TO_PRODUCT
     # Examples: ambiguous AC ("real-time"), unclear data model, undefined SLO

4. ELIF at least one gap requires an architecture change:
     verdict = INITIATE_ADR
     # Examples: tech category not in stack, new external integration, new bounded context

5. Mixed gaps (some adjustable, some require ADR) -> verdict = INITIATE_ADR
   (the ADR is the blocking decision; adjust requirements after the ADR resolves)

Ambiguous AC that COULD imply a prohibited mechanism = RETURN_TO_PRODUCT
even if a compliant implementation path exists. The compliant path existing
does NOT make the requirement itself compliant when its language is unresolved.
```

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project_name` | string | Yes | Project identifier |
| `user_stories_path` | string | Yes | Path to the user stories folder (output of implementing-user-stories — manifest + per-epic files) |
| `target_architecture_path` | string | Preferred | Path to target architecture folder (manifest + per-UNIT specs). When absent, the skill falls back to context pack content (see Step 2 — Architecture Resolution). |
| `context_pack_path` | string | No (default `./context-pack`) | Path to the context pack folder. Used as the fallback architecture source when `target_architecture_path` is not provided. |
| `adr_path` | string | Recommended | Path to ADR catalog folder |
| `epics_path` | string | No | Path to epics folder (used for cross-checking acceptance criteria provenance) |
| `prd_path` | string | No | PRD folder (NFR provenance) |
| `dtr_path` | string | No | DTR file or folder — when present, the Tool State column is consulted. Stories that depend on `legacy` or `migrating` tools are flagged in audit. |
| `compliance_output_path` | string | Yes | Output folder for COMPLIANCE-SPEC and COMPLIANCE-AUDIT |
| `story_scope` | enum | No (default `all`) | `all` \| `epic:<epic_id>` \| `story:<id1,id2,…>` — limits which stories are evaluated |
| `failure_feedback` | string | No | REPAIR mode directives (per-story or per-area) |
| `custom_message` | string | No | Optional focus areas / scope hints |

**If any Required parameter is not defined, ABORT EXECUTION via `stepwise session exec-fail`.**
**`target_architecture_path` is preferred but not required.** When absent, the skill resolves architecture context from the context pack (Step 2B-fallback). Only aborts if neither the path nor any usable context pack content can be found.

## COMPLIANCE_INDEX — Carry-Forward Contract

Initialize at Step 1. Update after every step.

```
COMPLIANCE_INDEX = {
  session_id: string,
  project_name: string,
  output_path: string,
  arch_source: "provided" | "context_pack_fallback",   // set in Step 2B
  arch_source_files: [string],                         // exact files used to build ARCH_CONTEXT
  inputs_loaded: { stories: bool, arch: bool, adrs: bool, prd: bool, dtr: bool },
  stories_total: N,
  stories_evaluated: N,
  verdicts: {
    approve: [story_id…],
    return_to_product: [story_id…],
    initiate_adr: [story_id…]
  },
  compliance_status: null,     // PASSED | PARTIAL | FAILED
  compliance_route: null,      // PROCEED | RETRY_BACKLOG | ESCALATE_ARCHITECTURE | VALIDATOR_REPAIR
  compliance_feedback: string,
  gaps_total: N,
  gap_categories: { technology, pattern, component, integration, data, nfr_perf, nfr_sec },
  arch_units_referenced: [unit_id…],
  adrs_referenced: [adr_id…],
  files_written: [{ path, status, line_count }],
  blockers: [],
  open_questions: []
}
```

---

## Workflow

### Step 1: Initialize

**Command:**
```
# Architecture Compliance Validator — Pre-Implementation Gate
# Persona: Senior Architect & Compliance Reviewer
# CRITICAL: NON-INTERACTIVE SESSION.
# MISSION: Validate stories against architecture. Architecture is immutable here.
#          Three verdicts only: Approve / Return-to-Product / Initiate-ADR.

SESSION_ID = [Extract from EXECUTION METADATA]

## SESSION_ID is provided by the harness/execution metadata per execution-protocol.md §1.
## REPAIR mode MUST reuse the existing session_id from prior COMPLIANCE-SPEC-* filenames.
## BUILD mode MUST also use the harness-provided SESSION_ID — never generate a
## date-based or project-based session_id locally. A re-run of the same Stepwise
## session/step produces the same SESSION_ID and therefore the same filenames,
## which is what enables overwrite-on-re-run instead of duplicate-file-on-re-run.
## SESSION_ID goes in filenames only, never in folder names.

IF failure_feedback NOT empty:
  MODE = REPAIR
  COMP_FOLDER = resolve_parent_folder(compliance_output_path)
  COMP_FILE = find existing COMPLIANCE-SPEC-*.md in COMP_FOLDER
  IF not found -> write Gap Report at COMP_FOLDER/COMPLIANCE-GAP-REPORT.md -> EXIT
  Load COMP_FILE -> PREVIOUS_SPEC -> SOURCE_LOG
  ## REPAIR MUST reuse the SESSION_ID embedded in the prior COMPLIANCE-SPEC filename.
  SESSION_ID = extract session_id from PREVIOUS_SPEC filename (COMPLIANCE-SPEC-{SESSION_ID}.md)
  PREVIOUS_VERSION = extract version from PREVIOUS_SPEC header
  NEW_VERSION = increment patch
  Parse failure_feedback -> REPAIR_DIRECTIVES [{ target_story_id|target_area|"global", instruction, reason }]
ELSE:
  ## BUILD mode — auto-detect prior artifacts BEFORE creating new ones.
  ## If a COMPLIANCE-SPEC with the SAME harness SESSION_ID already exists, this is a
  ## clean re-run of the same session — overwrite that file (preserves continuity).
  ## If a COMPLIANCE-SPEC with a DIFFERENT session_id exists, the operator is rebuilding
  ## from scratch in a new session; log the prior file path for traceability and proceed
  ## with the new SESSION_ID (do NOT delete prior files automatically).
  MODE = BUILD
  COMP_FOLDER = compliance_output_path
  COMP_FILE = COMP_FOLDER + '/COMPLIANCE-SPEC-' + SESSION_ID + '.md'
  AUDIT_FILE = COMP_FOLDER + '/COMPLIANCE-AUDIT-' + SESSION_ID + '.md'
  NEW_VERSION = "1.0.0"
  mkdir -p COMP_FOLDER

  ## Surface prior artifacts (if any) for the audit log — informational, non-blocking.
  PRIOR_SPECS = list COMPLIANCE-SPEC-*.md in COMP_FOLDER excluding COMP_FILE itself
  IF PRIOR_SPECS not empty:
    LOG to CHANGE_LOG: "Prior COMPLIANCE-SPEC artifacts present in output folder: {PRIOR_SPECS}.
                       This run produces a new artifact with SESSION_ID={SESSION_ID}.
                       To repair the prior spec instead, re-run this skill with
                       failure_feedback specifying which stories or areas to revise."

  ## EARLY SIGNAL — FIRST action after mkdir (MANDATORY)
  ## Section-shape variant — see execution-protocol.md §10.1 for schema and §10.6 for CONTINUE-on-re-entry.
  ## The `sections` map uses the fixed top-level structure; per-story sub-evaluations are tracked
  ## in COMPLIANCE_INDEX.stories_evaluated since story count is unknown until Step 2 input loading.
  WRITE COMP_FOLDER + '/_progress.json':
    { "skill": "validating-architecture-compliance", "session_id": "<SESSION_ID>",
      "status": "RUNNING", "started_at": "<ISO timestamp>", "completed_at": null,
      "skeleton_written": false,
      "sections": {
        "header": "pending", "stories_index": "pending",
        "per_story_evaluations": "pending", "gap_registry": "pending",
        "summary": "pending"
      } }

COMPLIANCE_INDEX = {session_id, project_name, output_path: COMP_FOLDER,
                    inputs_loaded: {}, stories_total: 0, stories_evaluated: 0,
                    verdicts: {approve: [], return_to_product: [], initiate_adr: []},
                    gaps_total: 0, gap_categories: {},
                    arch_units_referenced: [], adrs_referenced: [],
                    files_written: [], blockers: [], open_questions: []}

SOURCE_LOG = []
CHANGE_LOG = []

## Internal Reasoning: ALL in English regardless of output language.
```
**Execution:** automated

### Step 2: Input Loading

**Command:**
```
## STOP-GATE — Mandatory Inputs

# User stories are always required.
IF user_stories_path is empty OR folder does not exist:
  WRITE {COMP_FOLDER}/COMPLIANCE-GAP-REPORT.md:
    session_id: {SESSION_ID}
    status: BLOCKED
    reason: Missing User Stories
    expected_at: {user_stories_path}
  Call stepwise session exec-fail with the same reason.
  EXIT — Do not proceed.

# Architecture source: provided path OR context pack fallback.
RESOLVE_ARCH_SOURCE:
  IF target_architecture_path is non-empty AND folder exists:
    ARCH_MODE = "provided"
  ELSE:
    ARCH_MODE = "context_pack_fallback"
    # Fallback: scan context pack for architecture-relevant content.
    CP = context_pack_path OR "./context-pack"
    CANDIDATE_FILES = []
    FOR EACH file in CP (recursively):
      IF filename matches any of:
        *architecture*, *tech-policy*, *tech_policy*, *coding-standard*,
        *coding_standard*, *nfr*, *security-policy*, *security_policy*,
        *infrastructure*, *adr*, *component*, *stack*, *platform*
      OR content contains any of:
        "architecture principles", "technology stack", "service catalog",
        "NFR", "security controls", "integration", "data store"
      → ADD to CANDIDATE_FILES
    ALSO check: active-context.md in CP for direct architecture references
    ALSO check: known fallback locations:
      - ./artifacts/outputs/software-architecture/ (any *.md files)
      - ./artifacts/outputs/specifying-architecture/ (any *.md files)
      - ./artifacts/outputs/establishing-architecture-foundation/ (any *.md files)
    IF CANDIDATE_FILES is empty:
      WRITE {COMP_FOLDER}/COMPLIANCE-GAP-REPORT.md:
        session_id: {SESSION_ID}
        status: BLOCKED
        reason: No target_architecture_path provided and no architecture-relevant
                content found in context pack. Provide target_architecture_path
                or add architecture standards / tech-policy files to the context pack.
      Call stepwise session exec-fail with the same reason.
      EXIT — Do not proceed.
    LOG open_question: "No target_architecture_path provided. Compliance assessment
      based on context pack fallback using: {CANDIDATE_FILES}. Findings may be less
      precise than a full architecture spec. Provide target_architecture_path for
      a definitive assessment."
    COMPLIANCE_INDEX.arch_source = "context_pack_fallback"
    COMPLIANCE_INDEX.arch_source_files = CANDIDATE_FILES

COMPLIANCE_INDEX.arch_source = ARCH_MODE
IF ARCH_MODE == "provided":
  COMPLIANCE_INDEX.arch_source_files = [target_architecture_path]

## 2A. Load User Stories -> STORIES_INDEX

Read user_stories_path/manifest (the lightweight story_map produced by
implementing-user-stories). Apply story_scope filter:

  story_scope == "all"            -> evaluate every story
  story_scope == "epic:E-12"      -> only stories under epic E-12
  story_scope == "story:US-1,US-2"-> only listed story ids

For each in-scope story, ON DEMAND read its per-epic file (lazy load).
Extract:

STORY_CONTEXT[story_id] = {
  id, title, parent_epic, persona, goal, benefit,
  acceptance_criteria: [{id, given/when/then or bullet}],
  business_rules: [bullet],
  domain_tags: [BE/FE/DATA/INFRA/AI],
  technical_matrix: [{tag, scenario}],
  affected_areas: [],
  dependencies: [story_id],
  constraints: []
}

COMPLIANCE_INDEX.stories_total = count of in-scope stories.

## 2B. Load Target Architecture -> ARCH_CONTEXT

IF ARCH_MODE == "provided":
  Read target_architecture_path. Extract:
  ARCH_CONTEXT = {
    principles:        [{id, statement}]
    service_catalog:   [{id, name, owns_capabilities, tech_stack}]
    units: {
      communication: { patterns: [REST, event, gRPC, …], constraints: [] },
      data:          { stores: [{id, type, owners}], schemas: [], constraints: [] },
      security:      { authn, authz, controls: [] },
      observability: { telemetry, logging },
      infrastructure:{ cloud_provider, regions, deployment_targets },
      nfr:           [{id, category: performance|scalability|availability|security|…,
                       metric, target, scope: "global"|service_id }]
    },
    migration_roadmap: [{phase, in_scope_services}],
    integrations:      [{id, system, direction, contract}]
  }
  COMPLIANCE_INDEX.inputs_loaded.arch = true

ELSE: // ARCH_MODE == "context_pack_fallback"
  READ each file in COMPLIANCE_INDEX.arch_source_files.
  Build ARCH_CONTEXT by extracting whatever is available across all files:
    - principles / guiding rules / tech policies → ARCH_CONTEXT.principles
    - technology stack mentions, allowed/disallowed tech → ARCH_CONTEXT.service_catalog[*].tech_stack
    - communication patterns (REST, event-driven, etc.) → ARCH_CONTEXT.units.communication
    - data stores, databases mentioned → ARCH_CONTEXT.units.data
    - security controls, auth mechanisms → ARCH_CONTEXT.units.security
    - performance / scalability targets → ARCH_CONTEXT.units.nfr (category: performance)
    - external systems / integrations → ARCH_CONTEXT.integrations
  For any ARCH_CONTEXT field with no supporting content found: mark as null
  and note its absence in COMPLIANCE_INDEX.open_questions so reviewers know
  that compliance area used best-effort inference rather than a formal spec.
  COMPLIANCE_INDEX.inputs_loaded.arch = true  // populated from context pack

## 2C. Load ADRs -> ADR_CONTEXT (if available)

IF adr_path exists:
  ADR_CONTEXT = {
    adrs: [{id, status, decision, scope_services, scope_capabilities,
            rationale, alternatives, consequences}]
  }
  inputs_loaded.adrs = true
ELSE:
  ADR_CONTEXT = null

## 2D. Load DTR (if available)

IF dtr_path exists:
  DTR_CONTEXT = {
    rows: [{tab, field, tool, version, state, source_ref}]
  }
  inputs_loaded.dtr = true
  # Stories that depend on legacy/migrating tools will be flagged in audit.
ELSE:
  DTR_CONTEXT = null

## 2E. Load PRD / Epics for AC and NFR provenance (if available)

IF prd_path exists: load NFR section -> ARCH_CONTEXT.nfr cross-reference
IF epics_path exists: load epic AC -> story AC traceability cross-reference

## 2F. REPAIR Mode — Parse Directives

IF MODE == REPAIR:
  REPAIR_DIRECTIVES = [{ target_story_id|target_area|"global", instruction, reason }]
  Stories WITHOUT directives -> PRESERVE (keep verdict from PREVIOUS_SPEC).
  Targeted stories or areas -> re-evaluate.
  Before regenerating: archive any orphaned files (different SESSION_ID) to /repair-archive/.

## CHECKPOINT 1 — Write skeleton COMPLIANCE-SPEC after input loading
WRITE COMP_FILE with:
  - Header (project, session, version, mode, date)
  - Stories index (one row per in-scope story_id with verdict: pending)
  - Per-story section stubs
  - Gap registry placeholder
  - Summary placeholder
  - Top-level compliance_status: draft
LOG: "CHECKPOINT 1: skeleton COMPLIANCE-SPEC written; stories_total={N}"
```
**Execution:** automated

### Step 3: Per-Story Compliance Evaluation

**Apply execution-protocol.md Section 10** — Phase A (skeleton-first within 5 tool calls of entering Step 3) then Phase B (one story-section per `Edit` call). Tool discipline (§10.5) is **mandatory**: skeleton via `Write`, story sections via `Edit`, NEVER `Bash + sed/python3/awk` to mutate COMP_FILE. The non-ASCII fallback (§10.5.1) auto-applies when story content contains non-English text. NEVER fall back to bulk rewriting when one `Edit` fails — fix the `Edit` call instead.

**Skeleton stub text — must be ASCII:**

> `verdict: pending - will be evaluated`

ASCII hyphen (U+002D) only; never em dash.

**Per-story Phase B flow:** for each in-scope story (in `STORIES_INDEX` order), generate the story's evaluation, write it into the COMP_FILE per-story section via one `Edit` call, then update `_progress.json` (increment `stories_evaluated` count in COMPLIANCE_INDEX; flip `sections.per_story_evaluations` to `complete` only after the last story is written). Drop the story's evaluation body from working memory before moving to the next.

**READ** `references/validation-framework.md` **NOW** for the 6 compliance area definitions, gap calibration examples, and what is NOT a gap (implementation detail vs architectural gap).
**READ** `references/output-templates.md` **NOW** for the per-story output format (Templates 1a, 1b, 2, 3).

> **Parallel fan-out — DISPATCH DECISION (execution-protocol.md Section 14). Decide BEFORE the per-story loop.**
> - **IF the harness can dispatch multiple workers in a SINGLE turn AND there are >= 3 in-scope stories → fan out BY DEFAULT.** Concurrent foreground workers alone qualify — background/detached tasks are NOT required, and an absent `Parallel delegation:` advertisement does NOT force inline (execution-protocol.md §14 Applicability); fall back to inline ONLY when the harness is genuinely single-dispatch. Dispatch one worker per story, and **dispatch ALL story workers in ONE turn (§14.3 step 2) — one-worker-per-turn serializes them.** Each worker runs all 6 area checks for ONE story against the shared read-only `ARCH_CONTEXT` + `ADR_CONTEXT` + `DTR_CONTEXT`, applies the Verdict Decision Tree + the Authority guard, and returns a compact structured evaluation `{ story_id, verdict, gaps:[{area, what, where_in_architecture, severity, resolvable_by, ac/rule id}], dtr_observations }`. **Workers return data only — they NEVER edit COMPLIANCE-SPEC, `_progress.json`, or the §11 sidecar.**
> - **ELSE (harness is genuinely single-dispatch, or < 3 stories) → run the inline per-story loop below.**
>
> Independence proof: the architecture is the IMMUTABLE baseline; each story is evaluated unidirectionally against it, and no story's verdict depends on another story's evaluation (this is a per-story gate, not a cross-story synthesis). Because the output is section-shape (ONE COMPLIANCE-SPEC), workers do NOT edit that file — this is compute-parallel / write-serial. Merge contract (coordinator, serial): after the workers return, YOU write each story's section into COMPLIANCE-SPEC via one `Edit` per story (Phase B, §10.5 discipline), aggregate `COMPLIANCE_INDEX.verdicts` + `gap_categories`, run the Step 4 quality gate, and write the summary + audit + sidecar. No worktree needed (workers write nothing). Verdicts, gaps, and citations are IDENTICAL whether you fanned out or ran inline. Verify every worker-reported `where_in_architecture` / AC id actually exists in the inputs before it enters the spec (Zero-Invention — no phantom references, Step 4 check 10).

For each in-scope story:

1. **Run all 6 area checks in order:**
   - Technology fit → ARCH_CONTEXT.service_catalog[*].tech_stack
   - Pattern fit → ARCH_CONTEXT.units.communication.patterns
   - Component / service fit → ARCH_CONTEXT.service_catalog[*].owns_capabilities
   - Integration fit → ARCH_CONTEXT.integrations
   - Data fit → ARCH_CONTEXT.units.data.stores + schemas
   - NFR fit (6a Performance + 6b Security) → ARCH_CONTEXT.units.nfr (filter by category)

2. **For each gap found, record:**
   ```
   GAP = {
     id: G-{story_id}-{area_seq},
     story_id, area, what, where_in_architecture,
     severity: blocking | major,
     resolvable_by: requirement_adjustment | architecture_change
   }
   ```

3. **Apply the verdict decision tree** (see "Verdict Decision Tree" above).
   Append to `COMPLIANCE_INDEX.verdicts.{verdict}`.

4. **DTR cross-check (when DTR_CONTEXT present):**
   For every tool reference in the story's technical matrix that maps to a DTR row
   with state == legacy → add observation row to audit (NOT a gap):
   `OBS: story {id} depends on tool {tool} marked legacy; consider phased delivery.`
   For state == migrating → add observation row recommending the migrating-target tool.

5. **Authority guard:** if a gap implies "the architecture should X" or names a
   specific replacement technology, REWRITE the gap to describe the *category* of
   conflict only (e.g., "Salesforce API client / SDK not in architecture stack" —
   never enumerate specific libraries). Log the rewrite to CHANGE_LOG.

6. **Apply the appropriate output template** to the story section in COMP_FILE:
   - Template 2 — Approved
   - Template 1a — Return to Product
   - Template 1b — Initiate ADR

## CHECKPOINT 2 — Write complete draft COMPLIANCE-SPEC after evaluation loop
WRITE COMP_FILE with all per-story sections populated and Summary table (Template 3) at the end.
  - compliance_status: draft
LOG: "CHECKPOINT 2: complete draft COMPLIANCE-SPEC written (pre-validation)"

**Execution:** automated

### Step 4: Quality Validation Gate

**Command:**
```
1. Story Coverage: every in-scope story has a verdict (no `pending` remaining).
2. Six-Area Coverage: every story has been assessed against all 6 areas.
   For NFR specifically — both 6a Performance AND 6b Security must appear.
3. Gap Citation Coverage: every gap row has a `where_in_architecture` value
   pointing to a specific UNIT id, principle, ADR id, or NFR id.
4. Story Trace Coverage: every gap row has at least one `acceptance_criterion_id`
   or `business_rule_id` it conflicts with.
5. Authority Boundary: no gap row recommends a specific replacement technology
   or architectural pattern (only categories of conflict are allowed).
6. Verdict Consistency: stories with no gaps have verdict APPROVE; stories with
   any architecture-change gap have verdict INITIATE_ADR; mixed -> INITIATE_ADR.
7. DTR Observations: when DTR_CONTEXT present, audit lists every story that
   touches legacy/migrating tools (informational, not gating).
8. Summary Math: Template 3 totals match COMPLIANCE_INDEX.verdicts counts.
9. ADR Cross-Reference: every INITIATE_ADR verdict references the architecture
   section that would need to change (specific UNIT or principle id).
10. No Phantom References: every UNIT/principle/ADR id cited exists in inputs.

IF corrections needed -> apply in place, log to CHANGE_LOG.
IF validation cannot pass -> set compliance_status: FAILED, compliance_route:
VALIDATOR_REPAIR, list failures in audit's open_questions, and STILL write the file.

## CHECKPOINT 3 — Write validated COMPLIANCE-SPEC after quality gate
WRITE COMP_FILE with validated content.
  - compliance_status: draft until Step 5 computes the final VGT verdict
LOG: "CHECKPOINT 3: validated COMPLIANCE-SPEC written"
```
**Execution:** automated

### Step 5: Write Outputs

**Command:**
```
1. Verify COMP_FILE (COMPLIANCE-SPEC-{SESSION_ID}.md) exists and is non-empty.
   - Set the COMPLIANCE-SPEC front-matter/header `version:` to NEW_VERSION. On REPAIR this
     MUST be the incremented patch (Step 1: PREVIOUS_VERSION → NEW_VERSION) — re-evaluating
     stories in place without bumping `version` is a §7 violation. See execution-protocol §7.2 step 8.
2. Compute the VGT aggregate verdict from actual counts and validation integrity:
   - approve_count = count(COMPLIANCE_INDEX.verdicts.approve)
   - return_to_product_count = count(COMPLIANCE_INDEX.verdicts.return_to_product)
   - initiate_adr_count = count(COMPLIANCE_INDEX.verdicts.initiate_adr)
   - IF Step 4 validation integrity failed:
       compliance_status = FAILED
       compliance_route = VALIDATOR_REPAIR
     ELIF initiate_adr_count > 0:
       compliance_status = FAILED
       compliance_route = ESCALATE_ARCHITECTURE
     ELIF return_to_product_count > 0:
       compliance_status = PARTIAL
       compliance_route = RETRY_BACKLOG
     ELSE:
       compliance_status = PASSED
       compliance_route = PROCEED
   VERIFY approve_count + return_to_product_count + initiate_adr_count == stories_total.
   IF mismatch -> set compliance_status = FAILED, compliance_route = VALIDATOR_REPAIR,
   add mismatch to open_questions.
3. Generate compliance_feedback:
   - Empty string when compliance_status == PASSED.
   - For each RETURN_TO_PRODUCT story:
     `[RETURN_TO_PRODUCT] [story_id] [gap_categories] [requirement_adjustment] <one-line fix directive>`
   - For each INITIATE_ADR story:
     `[INITIATE_ADR] [story_id] [gap_categories] [architecture_change] <architecture section / ADR trigger>`
   - For validator integrity failures:
     `[VALIDATOR_REPAIR] [global] [quality_gate] <failed quality check>`
4. Update COMP_FILE header / summary with:
   - compliance_status
   - compliance_route
   - approve_count, return_to_product_count, initiate_adr_count
   - compliance_feedback (or "none" when empty)
5. Write AUDIT_FILE (COMPLIANCE-AUDIT-{SESSION_ID}.md):
   - Session metadata (session_id, mode, version=NEW_VERSION, timestamp, project_name)
   - VGT aggregate: compliance_status, compliance_route, approve_count,
     return_to_product_count, initiate_adr_count
   - Sources referenced (numbered list from SOURCE_LOG):
     User Stories, Target Architecture (mode: {arch_source} | files: {arch_source_files}),
     ADRs, PRD, Epics, DTR — each with load status.
     When arch_source == "context_pack_fallback": list every file used and note any
     ARCH_CONTEXT fields that defaulted to null due to missing content.
   - COMPLIANCE_INDEX summary:
     stories_total, stories_evaluated, verdict counts, gap counts by area,
     arch_units_referenced (unique), adrs_referenced (unique)
   - DTR observations (legacy/migrating tool dependencies per story)
   - Decisions made (CHANGE_LOG — including authority-guard rewrites)
   - REPAIR-only: set `mode: REPAIR` and APPEND (do not overwrite) a `## Repair History`
     entry — version, timestamp, directives_applied, sections_changed, sections_preserved,
     repair_delta (per execution-protocol §7.2 step 8).
   - Validation results from Step 4
   - open_questions registry
6. REPAIR self-check (execution-protocol §7.2 step 9): before final_response, confirm the
   COMPLIANCE-SPEC `version` is strictly greater than PREVIOUS_VERSION AND the AUDIT has the
   new `## Repair History` entry. If not, fix the bookkeeping now — do not finish.
7. UPDATE COMP_FOLDER + '/_progress.json':
   { "status": "COMPLETED", "completed_at": "<ISO timestamp>",
     "skill": "validating-architecture-compliance", "session_id": SESSION_ID,
     "compliance_status": compliance_status, "compliance_route": compliance_route,
     "verdicts": {approve: N, return_to_product: N, initiate_adr: N} }

**Apply execution-protocol.md Section 11** — Harness Output Sidecar. Mandatory when the prompt contains a `## Run metadata` block. This is the FINAL file write of the run (after `_progress.json` set to COMPLETED, after audit, after Memory Bank).

**Output parameters this skill produces** (one key per row of the prompt's `## Output parameters` table):

- `compliance_path`: absolute path to COMPLIANCE-SPEC-{SESSION_ID}.md
- `compliance_audit_path`: absolute path to COMPLIANCE-AUDIT-{SESSION_ID}.md
- `compliance_status`: `PASSED` | `PARTIAL` | `FAILED`
- `compliance_route`: `PROCEED` | `RETRY_BACKLOG` | `ESCALATE_ARCHITECTURE` | `VALIDATOR_REPAIR`
- `approve_count`: integer count of stories with verdict APPROVE
- `return_to_product_count`: integer count of stories with verdict RETURN_TO_PRODUCT
- `initiate_adr_count`: integer count of stories with verdict INITIATE_ADR
- `compliance_feedback`: one-line-per-non-approved-story summary; empty string when all stories APPROVE

**Implementation:** the harness here accepts Bash heredoc for the sidecar write (the sidecar is NOT the SPEC_FILE, so §10.5's anti-Bash rule does not apply). Execute exactly:

```
cat > {stepwise_outputs_file} << 'OUTPUTS_EOF'
{json with all 8 keys above}
OUTPUTS_EOF
```

Self-check: `cat {stepwise_outputs_file}` — verify file is non-empty. If empty or missing, re-execute. DO NOT describe output registration in response text — EXECUTE it.
```
**Execution:** automated

## Memory Bank — Update Cross-Session State
Read `_shared/references/memory-bank.md` for the full protocol.
1. Overwrite context-pack/active-context.md with final session state (verdict counts, top blockers).
2. Append one milestone row to context-pack/progress.md:
   `| {session_id} | {date} | {capability} | validating-architecture-compliance | {STATUS} | **N stories: A approve, R return, I ADR** | {1-line summary} |`
   Artifact format MUST be `"N stories: A approve, R return, I ADR"`.
Both writes are MANDATORY — even on failure, record the failure.
After writing, VERIFY exists(context-pack/progress.md). LOG: "Memory Bank: progress.md updated."

## Reference Files

| File | Load when | Purpose |
|------|-----------|---------|
| `references/validation-framework.md` | Step 3 — once at start | The 6 compliance area definitions, gap calibration examples, what is NOT a gap |
| `references/output-templates.md` | Step 3 — once at start | Per-story output templates (Templates 1a, 1b, 2, 3) |
