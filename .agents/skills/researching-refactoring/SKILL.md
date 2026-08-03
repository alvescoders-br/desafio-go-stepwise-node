---
name: researching-refactoring
description: >
  Refactoring and upgrade research phase. Analyzes an existing codebase for
  platform/framework upgrades AND structural refactoring to produce a single
  agent-native research spec with zero prose — structured scope summary,
  current-state analysis, compatibility breaks, coupling analysis, dependency
  migration matrix, build system impact, migration sequence, code transformation
  catalog, acceptance criteria, test strategy, and open_questions registry.
  Supports three refactoring types: version-upgrade, structural, combined.
  Does NOT require full SDLC upstream. Requires source code + migration/refactoring spec.
  Downstream consumer: planning-code-tasks (TASK mode).
  Human-readable output via humanize-spec.
license: Proprietary
metadata:
  author: aipods-team
  version: 4.2.0
  category: engineering
  tags: upgrade, migration, refactor, platform, framework, version, research, FIC, RPI, agent-native
---

# Researching Refactoring — Agent-Native Spec

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
   to source code, migration spec, migration guide, or architecture notes.
   Missing data → mark `status: pending` and register an open_questions entry.
   Asking the human a clarifying question = task FAILURE.

4a. **Host-codebase precondition — its absence is a BLOCKER, not a fillable gap.**
   This scope (refactoring/upgrade) presumes an **existing codebase** at
   `source_path`. That codebase is a *precondition* of the task, so Entry Rule #4's
   "missing data → mark pending" does NOT apply to the codebase itself, and the
   `source_path`-defined check is not enough — the path must exist on disk AND
   actually contain the application being refactored (not empty, not a stub: the
   application entry point and the modules in the refactor's blast radius are
   physically present). If `source_path` is absent/empty, or lacks the codebase the
   migration/refactoring spec presumes, **STOP and escalate as a BLOCKER**
   (`stepwise session exec-fail` / `NEEDS_REPLAN`) naming the missing precondition.
   Do NOT proceed by marking the whole codebase as `assumption`/`pending`, and do
   NOT synthesize a minimal/stub module — a research spec built on an absent
   codebase is not "actionable for planning," it is a blocker. (Calibration:
   CalcService3 cdal-01 — `./source` was absent; research proceeded on assumptions
   and implementation built a stub that passed code-review yet could not boot.)

5. **No final response until RESEARCH-SPEC + RESEARCH-AUDIT exist on disk.**

---

## Quick Start
Analyze an existing application codebase against a target platform version, structural
refactoring objectives, or both, to produce a structured, agent-consumable research spec.
Output is a **single file**: `{research_output_path}/RESEARCH-SPEC-{SESSION_ID}.md`.
No prose. No narrative. Only structured data the implementing agent needs to execute
Research/Plan/Implement cycles.

## Known Failure Modes
<!-- ACCUMULATING — appended by calibrating-updates (WS6). Newest first. Rules MUST be generic/behavioral (project-agnostic); project-specific fixes go to context packs, never here. Format + entry rules: engineering-skills/references/known-failure-modes-format.md. Read these at pre-flight so a lesson learned once recurs no more. -->

## Anti-Patterns (do NOT)
<!-- ACCUMULATING — appended by calibrating-updates (WS6). One line each: **AP-NNN** (ISO-date, source: REC-NNN): prohibition — why. -->

## Output Architecture

```
{research_output_path}/
├── RESEARCH-SPEC-{SESSION_ID}.md     ← Single agent-native spec (all sections)
└── RESEARCH-AUDIT-{SESSION_ID}.md    ← Session audit trail (metadata only)
```

**Why single file:** Agent-native specs are 60-70% smaller than the original 11-document
research set. No batching needed — the entire spec fits comfortably in context.
The Write-Flush-Forget protocol applies only if context exceeds 60% mid-generation
(unlikely with zero-prose output).

**Human-readable output:** Not produced by this skill. Use `humanize-spec` skill
to generate rich 11-document research report from this spec on demand.

**Pipeline Position:**

```
Migration Spec / Refactoring Objectives
            ↓
  [Source Code Repository]       (REQUIRED)
            ↓
  [Optional: Migration Guides, Architecture Notes, Context Pack]
            ↓
  [researching-refactoring]      ← YOU ARE HERE
            ↓
  [planning-code-tasks]          (TASK mode)
            ↓
  [implementing-code]
```

**When to use this skill (vs alternatives):**

| Scenario | Skill |
|----------|-------|
| Isolated defect fix with a bug ticket | researching-bug-fixing (1 spec) |
| Implementing a story/feature into an existing app | researching-feature-impl (1 spec) |
| Platform/framework upgrade, structural refactoring, or combined | **researching-refactoring** (1 spec, 11 sections) ← THIS |
| Full greenfield build with PRD, Epics, Stories, ADRs | researching-code-design (1 spec, 20 sections) |

**Refactoring types:**

| Type | Trigger | Key Sections |
|------|---------|-------------|
| `version_upgrade` | Language/framework/runtime/library version change | compatibility_analysis, dependency_migration_matrix, migration_sequence |
| `structural` | Module extraction, pattern migration, coupling reduction | coupling_analysis, code_transformation_catalog |
| `combined` | Upgrade + restructure (default) | All sections active |

## Parameters
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_name | string | Yes | Project identifier |
| source_path | string | Yes | Path to source code repository (REQUIRED) |
| migration_spec_path | string | Yes | Path to migration/refactoring specification file |
| refactoring_type | string | No | `version_upgrade`, `structural`, or `combined` (default) |
| migration_guides_path | string | No | Path to official migration/release notes |
| architecture_notes_path | string | No | Path to ADRs, architecture decision docs |
| context_pack_path | string | No | Tech-policy, arch-standards, coding-standards |
| research_output_path | string | No | Output folder. When invoked via capability, the resolved path includes `feature_id` scope when set: `{output_folder}/{project_name}/{feature_id}/research-output`. Without `feature_id`: `{output_folder}/{project_name}/research-output`. Standalone default: `./research/` |
| failure_feedback | string | No | Present only in REPAIR mode — targeted fix directives |
| custom_message | string | No | Optional user instructions or focus areas |

**If any Required parameter is not defined, ABORT EXECUTION.**

## Workflow

### Step 1: Initialize

**Command:**
```
# Refactoring Research Agent — Agent-Native Spec Generator
# Persona: Senior Platform Migration Analyst & Refactoring Strategist
# CRITICAL: NON-INTERACTIVE SESSION.
# MISSION: Extract structured migration/refactoring research from codebase + spec. Zero invention.

SESSION_ID = [Extract from EXECUTION METADATA]

IF failure_feedback NOT empty:
  MODE = REPAIR
  SPEC_FOLDER = resolve_parent_folder(research_output_path)
  SPEC_FILE = find existing RESEARCH-SPEC-*.md in SPEC_FOLDER
  IF not found → write Gap Report → EXIT
  Load SPEC_FILE → PREVIOUS_SPEC → SOURCE_LOG
  PREVIOUS_VERSION = extract version
  NEW_VERSION = increment patch
  Parse failure_feedback → REPAIR_DIRECTIVES [{ section, instruction, reason }]
ELSE:
  MODE = BUILD
  SESSION_ID = "UPGRADE-{PROJECT_NAME_UPPER}-{YYYYMMDD}"
  SPEC_FOLDER = research_output_path + '-' + SESSION_ID + '/'
  SPEC_FILE = SPEC_FOLDER + 'RESEARCH-SPEC-' + SESSION_ID + '.md'
  NEW_VERSION = "1.0.0"
  mkdir -p SPEC_FOLDER

  ## EARLY SIGNAL — FIRST action after mkdir (MANDATORY)
  ## Section-shape variant — see execution-protocol.md §10.1 for schema and §10.6 for CONTINUE-on-re-entry.
  WRITE SPEC_FOLDER + '_progress.json':
    { "skill": "researching-refactoring", "session_id": "<SESSION_ID>",
      "status": "RUNNING", "started_at": "<ISO timestamp>", "completed_at": null,
      "skeleton_written": false,
      "sections": {
        "scope_summary": "pending", "current_state_analysis": "pending",
        "compatibility_analysis": "pending", "coupling_analysis": "pending",
        "dependency_migration_matrix": "pending", "build_system_impact": "pending",
        "migration_sequence": "pending", "code_transformation_catalog": "pending",
        "acceptance_criteria": "pending", "test_strategy": "pending",
        "validations": "pending", "open_questions": "pending"
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
Not in source → status: pending. Never infer, assume, or create information.
Inferred industry standards → status: assumption (with ASM-XX ID).

## Internal Reasoning: ALL in English regardless of output language.
```
**Execution:** automated

### Step 2: Input Loading

> **Before any discovery scan — apply execution-protocol.md Section 13 (Code-Location Discipline).** Read `context-pack/codebase-map.md` (and `project-inventory.md` if present) to locate the symbols and modules in the refactor's blast radius BEFORE running a repository-wide `grep`/`glob`/`find` to discover where they live — **consult before scan, not never scan**. Read the specific files the map names directly; fall back to a scoped scan only where the map is absent or insufficient (call-site enumeration often needs a real `grep` — that is allowed when the map cannot answer it), and flag that gap in the research output so the map can be corrected. Map first (§13), then delegate the residual sweep (§12).
>
> **During input loading — apply execution-protocol.md Section 12 (Delegated Exploration) if your harness supports it.** Broad read-only sweeps for this skill (e.g. enumerating every call site and usage of the symbols being refactored, surveying the blast radius across modules) MAY be delegated to a read-only exploration subagent on a cheap/fast model, which returns conclusions + `file:line` pointers (not file dumps). Synthesis, decisions, and all writing stay with this agent, which verifies any delegated `file:line` before using it (Zero-Invention still applies). With no subagent capability, explore inline under the usual scope constraint — output quality is identical either way.

**Command:**
```
## STOP-GATE — Mandatory Inputs

REQUIRED = [
  { name: "Source Code Repository", path: source_path },
  { name: "Migration/Refactoring Specification", path: migration_spec_path }
]

FOR EACH input IN REQUIRED:
  IF input.path is empty OR file/directory does not exist:
    WRITE {SPEC_FOLDER}/RESEARCH-SPEC-GAP-REPORT.md:
      session_id: {SESSION_ID}
      status: BLOCKED
      reason: Missing {input.name}
      expected_at: {input.path}
      action: Provide the missing input and re-run.
    EXIT — Do not proceed.

## 2A. Load Migration/Refactoring Specification → REFACTOR_CONTEXT

Read migration_spec_path completely. Extract:

REFACTOR_CONTEXT = {
  contract_mode:          # auto-detected: structured | partial | unstructured
  content_hash:           # sha256:<64 lowercase hex> if declared by migration/refactoring spec; else N/A
  hash_status:            # match | mismatch_accepted | mismatch_blocked | not_verified | N/A
  source_version:          # Current platform/framework version
  target_version:          # Target platform/framework version
  refactoring_type:        # version_upgrade | structural | combined (from param or inferred)
  migration_type:          # language_version | framework | runtime | library | build_system | multi
  goals:                   # Why upgrading/refactoring: EOL, performance, security, decoupling
  constraints:             # Timeline, budget, team size, no-downtime requirements
  exclusions:              # Explicitly out of scope
  intermediate_stops:      # Intermediate versions (e.g., "go through Java 11, 17 first")
  breaking_changes_known:  # Breaking changes already identified in spec
  deprecations_known:      # Deprecations already identified in spec
  rollback_requirements:   # Rollback strategy requirements
  performance_targets:     # Performance expectations post-migration
  compliance_requirements: # Regulatory or compliance drivers
  structural_objectives:   # (structural/combined) Module extraction, pattern migration goals
  coupling_targets:        # (structural/combined) Coupling reduction targets
  literal_refs:            # LIT-XX references and exact values if present
  fallback_refs:           # pending input / assumption fallback IDs if present
  evidence_gaps:           # structured/prose discrepancies, invalid hashes, missing proof
}

# Zero Invention Policy: If a field is absent → set to "[Not specified in spec]".

Detect `contract_mode` automatically:
- `structured`: migration/refactoring spec declares `contract_format: structured`,
  globally scoped rule/task IDs, enriched open_questions if gaps exist, valid
  SHA-256 hashes for declared source fields, and upstream completeness is certified.
- `partial`: some structured fields exist, or a declared-structured spec fails
  its own contract during WARN-mode rollout. Use available structured rows, but
  still mine the prose as a cross-check.
- `unstructured`: no structured contract fields. This is valid for external
  vendor/client/changelog inputs; use current prose extraction behavior.

Hash format gate:
- Treat only `sha256:<64 lowercase hex chars>` as a valid hash value.
- Any field named `content_hash`, `*_source_hash`, or `source_hash` with a
  missing value, bare hash, mtime, session ID, filename, or placeholder is
  invalid for structured mode.
- Invalid hash fields demote the spec to `partial`, require prose cross-check,
  and create an `evidence_gaps` row. Do not emit `hash_status: match` for a
  non-SHA value.
- If an upstream artifact is loaded and a valid declared hash mismatches,
  forward-verify recorded dependencies (IDs, literals, fallbacks). If unchanged,
  proceed and log the acceptance in the audit only; never edit upstream artifacts.

Authentication security defaults:
- If the refactor touches auth, sessions, identity, OAuth, or password reset,
  persisted password-reset tokens are secrets and must be hashed at rest. Raw
  reset-token storage is an `evidence_gaps` row unless a binding upstream source
  explicitly requires it.
- OAuth provider values must come from an explicit allow-list before selecting
  provider columns, scopes, or identity fields. A fallback such as "non-google
  means github" is an `evidence_gaps` row.

## 2B. Load Source Code → SOURCE_CONTEXT (REQUIRED)

SOURCE_CONTEXT = {
  project_structure:     directory tree (relevant areas)
  language_version:      detected from build files
  framework_versions:    framework → version from build/config files
  dependencies:          library → version from build file (ALL dependencies)
  build_tool:            build tool name + version + configuration
  build_plugins:         plugin → version from build configuration
  compiler_flags:        compiler options, source/target compatibility settings
  test_framework:        test framework name, version, test commands
  ci_cd_config:          CI/CD pipeline files
  module_system:         module-info.java presence, package structure
  deprecated_api_usage:  detected usage of known deprecated APIs
  reflection_usage:      reflective access patterns
  serialization_usage:   serialization patterns
  internal_api_usage:    usage of internal/restricted APIs
  code_patterns:         version-sensitive patterns detected
  entry_points:          main classes, servlet configs, bootstrap
  coupling_metrics:      (structural/combined) module coupling, dependency direction
  external_integrations: version-sensitive external protocols/clients
}

## 2C. Load Migration Guides → GUIDE_CONTEXT (if available)

IF migration_guides_path exists:
  GUIDE_CONTEXT = {
    breaking_changes:    official list of breaking changes
    deprecated_apis:     APIs deprecated and replacements
    removed_apis:        APIs removed entirely
    new_apis:            New APIs replacing old patterns
    behavioral_changes:  Subtle behavioral changes
    migration_steps:     Official recommended migration steps
  }
ELSE:
  GUIDE_CONTEXT = null

## 2D. Load Architecture Notes → ARCH_CONTEXT (if available)

IF architecture_notes_path exists:
  ARCH_CONTEXT = {
    decisions:     ADR-style decisions relevant to migration
    constraints:   architectural constraints
    tech_stack:    approved technologies and versions
    patterns:      required patterns that may be version-sensitive
  }
ELSE:
  ARCH_CONTEXT = null

## 2E. Load Context Pack (if available)

IF context_pack_path exists:
  Read tech-policy, arch-standards, coding-standards → SOURCE_LOG

## 2F. REPAIR Mode — Parse Directives

IF MODE == REPAIR:
  Parse failure_feedback into:
  REPAIR_DIRECTIVES = [
    { target: "scope_summary"|"current_state_analysis"|"compatibility_analysis"|
              "coupling_analysis"|"dependency_migration_matrix"|"build_system_impact"|
              "migration_sequence"|"code_transformation_catalog"|"acceptance_criteria"|
              "test_strategy"|"validations"|"global",
      instruction, reason }
  ]
  Sections WITHOUT directives → PRESERVE (keep from PREVIOUS_SPEC).
  "global" → regenerate entire spec.

## 2G. Detect Language

Detect language from migration spec → DETECTED_LANGUAGE

## CHECKPOINT 1 — Write skeleton spec after input loading (BUILD mode only)
## Purpose: Preserve extracted contexts if killed during Step 3 generation.
IF MODE == BUILD:
  WRITE SPEC_FILE with:
    - Header metadata (version: NEW_VERSION, session: SESSION_ID, mode: BUILD,
      date: today, language: DETECTED_LANGUAGE, refactoring_type,
      source_path, migration_spec_path, source_version, target_version, migration_type)
    - scope_summary section: populated from REFACTOR_CONTEXT
      (migration_overview, goals, constraints, exclusions, risk_profile, complexity)
    - current_state_analysis section: populated from SOURCE_CONTEXT
      (tech_stack, project_structure, dependencies, deprecated_api_usage,
       reflection_usage, serialization_usage, internal_api_usage,
       version_features, module_system, external_integrations)
    - All remaining sections as stubs:
      ## {section_name}
      status: pending - will be generated in Step 3
    - Top-level spec_status: draft
  LOG: "CHECKPOINT 1: skeleton spec written with scope_summary + current_state_analysis"
```
**Execution:** automated

### Step 3: Generate Spec

**Apply execution-protocol.md Section 10** — Phase A (skeleton-first within 5 tool calls of entering Step 3) then Phase B (one section per `Edit` call). Tool discipline (§10.5) is **mandatory**: skeleton via `Write`, sections via `Edit`, NEVER `Bash + sed/python3/awk` to mutate SPEC_FILE. The non-ASCII fallback (§10.5.1) auto-applies when content is non-English. NEVER fall back to bulk rewriting when one `Edit` fails — fix the `Edit` call instead.

**Skeleton stub text — must be ASCII:** `status: pending - will be generated` (ASCII hyphen U+002D, not em dash).

**Section list (template order):** `scope_summary -> current_state_analysis -> compatibility_analysis -> coupling_analysis -> dependency_migration_matrix -> build_system_impact -> migration_sequence -> code_transformation_catalog -> acceptance_criteria -> test_strategy -> validations -> open_questions`. See `references/refactoring-research-template.md` for full structure.

**READ** `references/refactoring-research-template.md` **NOW** for section structure.
**READ** `references/consistency-rules.md` **NOW** for the 11 consistency rules
(Codebase Fidelity, Version Fidelity, Breaking Change Traceability, Dependency
Version Accuracy, Migration Guide Fidelity, Architecture Constraint Respect,
Zero Invention, Anti-Fade) plus Status Protocol, Source Tagging, and Refactoring
Type Gating rules.

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
   SOURCE_CONTEXT.project_structure or is marked [Assumption]
2. Version Consistency: All version references match SOURCE_CONTEXT.dependencies
   or REFACTOR_CONTEXT.target_version or are marked [Unknown]
3. Breaking Change Coverage: Every item in compatibility_analysis has a source
   (guide, codebase, or changelog) or is marked [Needs verification]
4. Breaking Change Completeness: IF GUIDE_CONTEXT exists, every official
   breaking change appears in compatibility_analysis
5. Dependency Matrix Completeness: Every dependency in SOURCE_CONTEXT.dependencies
   appears in dependency_migration_matrix
6. Migration Sequence Validity: Stage prerequisites satisfied by prior stages,
   no circular dependencies
7. Transformation ↔ Break Alignment: Every CRITICAL/HIGH break has a
   corresponding transformation; every transformation references a break
8. AC Coverage: Every major functional area has a parity criterion
9. Anti-Fade: test_strategy depth matches scope_summary depth
10. Count Verification: Summary counts match actual item counts in each section
11. Refactor Contract Mode: REFACTOR_CONTEXT.contract_mode is recorded as
    structured, partial, or unstructured; unstructured is valid for external specs
12. Partial Cross-Check: In partial mode, prose-derived IDs/literals/fallbacks
    are checked against structured rows and discrepancies become evidence_gaps
13. Hash Forward Verification: source hashes are valid `sha256:<64 lowercase hex>`
    values or marked invalid; valid mismatches are forward-verified against
    recorded dependencies and accepted only in the audit
14. Auth Security Defaults: auth/OAuth/password-reset refactors carry reset-token
    hash-at-rest and provider allow-list constraints or evidence_gaps

IF corrections needed → apply in place, log to CHANGE_LOG

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
   - Session metadata (version=NEW_VERSION, mode, session_id, timestamp, refactoring_type)
   - Sources referenced (numbered list from SOURCE_LOG)
   - Refactor contract: contract_mode, hashes, hash_status,
     accepted_hash_overrides, partial-mode evidence_gaps
   - Decisions made (from CHANGE_LOG)
   - Summary counts: breaking_changes, dependencies, transformations,
     migration_stages, ac_parity, ac_new, tests_to_write, tests_to_update,
     affected_files, open_questions
   - Validation results (14 checks, PASS/FAIL each)
   - REPAIR-only: set `mode: REPAIR` and APPEND (do not overwrite) a `## Repair History`
     entry — version, timestamp, directives_applied, sections_changed, sections_preserved,
     repair_delta (per execution-protocol §7.2 step 8).
3. REPAIR self-check (execution-protocol §7.2 step 9): before final_response, confirm the
   SPEC `version` is strictly greater than PREVIOUS_VERSION AND the AUDIT has the new
   `## Repair History` entry. If not, fix the bookkeeping now — do not finish.
4. Verify both files exist and are non-empty
5. UPDATE SPEC_FOLDER + '_progress.json':
   { "status": "COMPLETED", "completed_at": "<ISO timestamp>",
     "skill": "researching-refactoring", "session_id": SESSION_ID }

Ready for downstream consumption (planning-code-tasks in TASK mode).
```
**Execution:** automated

### Step N: Emit Harness Outputs Sidecar

**Apply execution-protocol.md Section 11.** Mandatory when the prompt contains a `## Run metadata` block (Stepwise invocation); skip otherwise. FINAL file write of the run (after Memory Bank, after `_progress.json` set to COMPLETED).

**Output parameters this skill produces** (one key per row of the prompt's `## Output parameters` table):

- `research_output_path`: the SPEC_FOLDER you actually wrote the RESEARCH-SPEC into, reported VERBATIM. SPEC_FOLDER is already bound to the received (feature-scoped) `research_output_path` param — do NOT re-prepend `{output_folder}`/`{project_name}`/`{feature_id}` or re-derive it from a `{% if feature_id %}` formula (that would drop the feature scope).

**Implementation:** the harness here accepts Bash heredoc for the sidecar write. Execute:

```
cat > {stepwise_outputs_file} << 'OUTPUTS_EOF'
{ "research_output_path": "{SPEC_FOLDER}" }
OUTPUTS_EOF
```

## Memory Bank — Update Cross-Session State
Read `_shared/references/memory-bank.md` for the full protocol.
1. Overwrite context-pack/active-context.md with final session state (status, decisions, blockers, key artifacts).
2. Append one milestone row to context-pack/progress.md: `| {session_id} | {date} | {capability} | researching-refactoring | {STATUS} | **{N} research-docs** | {1-line summary} |`
   Artifact count MUST be the exact number of research document files written (e.g., `"2 research-docs"`). See _shared/references/memory-bank.md Artifact Type Registry.
Both writes are MANDATORY — even on failure, record the failure.
After writing, VERIFY exists(context-pack/progress.md) and that the last row contains the research-docs count. LOG: "Memory Bank: progress.md updated — {N} research-docs recorded."

## Reference Files

| File | Load when | Purpose |
|------|-----------|---------|
| `references/refactoring-research-template.md` | Step 3 | RESEARCH-SPEC section structure |
| `references/consistency-rules.md` | Step 3 — once at start | The 11 consistency rules + Status Protocol + Source Tagging + Refactoring Type Gating |
