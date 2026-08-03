---
name: creating-qe-master-plan
description: >
  Generates agent-consumable QE Master Test Plan specs from PRD, epics, ADRs,
  and target architecture. Output is a single strict-markdown file with zero
  prose — structured scope matrix, risk assessment, test strategy, environment
  map, test data strategy, entry/exit criteria, and traceability audit.
  All unresolved items consolidated in `open_questions` registry.
  Enforces Zero Invention Policy: every feature traces to an epic, every risk
  traces to an ADR/NFR/RSK. BUILD and REPAIR modes. RPI workflow.
  FIC context discipline (Correct > Complete > Concise).
  Human-readable output generated on demand via `humanize-spec` skill (separate).
license: Globant
metadata:
  author: aipods-team
  version: 3.1.0
  category: quality-engineering
  tags: quality-engineering-planning, automated, agent-native
---

# Creating QE Master Plan — Agent-Native Spec

## Quick Start
Generate a structured, agent-consumable QE Master Test Plan from product and
architecture artifacts. Output is a **single file**: `MTP-SPEC-{SESSION_ID}.md`.
No prose. No executive summaries. No meeting agendas. Only structured data
the downstream agents (defining-qe-strategy, generating-test-cases) need.

## Output Architecture

```
{master_test_plan_path}/
├── MTP-SPEC-{SESSION_ID}.md     ← Single agent-native spec (all sections)
└── MTP-AUDIT-{SESSION_ID}.md    ← Session audit trail (metadata only)
```

**Why single file:** Agent-native QE specs are 60-70% smaller than human-readable
master test plans. Scope matrix, risk assessment, test strategy, environment map,
criteria, and traceability audit all fit comfortably in one file (estimated 300-500
lines of structured data). No batching or Write-Flush-Forget protocol needed.

**Human-readable output:** Not produced by this skill. Use `humanize-spec` skill
with the `qe-master-plan` rendering profile to generate rich MTP documents
(executive summaries, Mermaid diagrams, meeting agendas) from this spec on demand.

## Parameters
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_name | string | Yes | Project identifier used across all phases |
| prd_path | string | Yes | Path to PRD document (or PRD spec folder) |
| epics_path | string | Yes | Path to epics document (or epics spec folder) |
| adrs_path | string | No | Path to ADR collection (folder or summary) |
| target_architecture_path | string | No | Path to target architecture documentation |
| master_test_plan_path | string | Yes | Output path for master test plan |
| failure_feedback | string | No | Feedback for REPAIR mode |

**If any Required parameter is not defined, ABORT EXECUTION.**

## Output Contract — HARD RULES (not suggestions)

The spec is consumed by downstream agents (`defining-qe-strategy`,
`generating-test-cases`, `generating-e2e-test-cases`), not humans.
Violating any rule below ABORTS the skill in Step 5 (Quality Validation Gate).

### Filename
- SPEC filename MUST match regex: `^MTP-SPEC-[A-Za-z0-9_-]+\.md$`
- AUDIT filename MUST match regex: `^MTP-AUDIT-[A-Za-z0-9_-]+\.md$`
- Anything else (e.g. `master-test-plan.md`, `QE-MTP-*.md`) → ABORT.

### ALLOWED top-level sections (exactly these 9, lowercase snake_case)
```
1. ## scope_matrix
2. ## risk_assessment
3. ## test_strategy
4. ## environment_map
5. ## test_data_strategy
6. ## entry_exit_criteria
7. ## traceability_audit
8. ## engineering_assumptions
9. ## open_questions
```
Any other top-level `## ` heading → ABORT.

### PROHIBITED — DO NOT GENERATE
These belong to `humanize-spec` (the rendering profile reconstructs them):
- `## Executive Summary`, `## Purpose`, `## Introduction`, `## Background`
- `## 1. Scope`, `## 2. Risks`, or any `## N. UPPERCASE` numbered narrative section
- `## Process Log`, `## Change Log` (these go to MTP-AUDIT)
- `## Meeting Agenda`, `## Stakeholder Communication`
- Tool narrative sections like `## Tool Selection Rationale` (use structured
  `tool_classification` table inside `test_strategy` instead)

### Heading and Prose Rules
- Section headings MUST be lowercase snake_case.
- No prose paragraphs. Outside fenced code blocks, no contiguous run of more
  than 2 narrative lines (capital-letter start, period end, > 15 words each).
- No "this document defines…", no executive summary text.

## Workflow

### Step 1: Initialize

**Command:**
```
# QE Master Test Plan Agent — Agent-Native Spec Generator
# Persona: Expert QA Manager — Agile, Risk-Based Testing, CI/CD, Shift-Left.
# CRITICAL: NON-INTERACTIVE SESSION.
# MISSION: Synthesize structured QE spec from upstream artifacts. Zero invention.

IF failure_feedback NOT empty:
  MODE = REPAIR
  SPEC_FOLDER = resolve_parent_folder(master_test_plan_path)
  SPEC_FILE = find existing MTP-SPEC-*.md in SPEC_FOLDER
  IF not found → write Gap Report → EXIT
  Load SPEC_FILE → PREVIOUS_SPEC → SOURCE_LOG
  PREVIOUS_VERSION = extract version
  NEW_VERSION = increment patch
  Parse failure_feedback → REPAIR_DIRECTIVES [{ section, instruction, reason }]
ELSE:
  MODE = BUILD
  SPEC_FOLDER = master_test_plan_path
  ## PATH GUARD: master_test_plan_path is the FINAL folder path as resolved by the capability.
  ## Use it EXACTLY as provided — do NOT prepend artifacts/outputs/ or any other prefix.
  ## If the path is relative, resolve it relative to execution_dir (the project root).
  ## Wrong: artifacts/outputs/ + artifacts/outputs/qa-master-test-plan (double nesting)
  ## Right: artifacts/outputs/qa-master-test-plan (use parameter value directly)
  SPEC_FILE = SPEC_FOLDER + '/MTP-SPEC-' + SESSION_ID + '.md'
  AUDIT_FILE = SPEC_FOLDER + '/MTP-AUDIT-' + SESSION_ID + '.md'
  NEW_VERSION = "1.0.0"
  mkdir -p SPEC_FOLDER

  ## FIRST ACTION — MANDATORY: Write _progress.json before any other file write.
  ## Section-shape variant — see execution-protocol.md §10.1 for schema and §10.6 for CONTINUE-on-re-entry.
  WRITE SPEC_FOLDER + '/_progress.json':
    { "skill": "creating-qe-master-plan", "session_id": "<SESSION_ID>",
      "status": "RUNNING", "started_at": "<ISO timestamp>", "completed_at": null,
      "skeleton_written": false,
      "sections": {
        "scope_matrix": "pending", "risk_assessment": "pending",
        "test_strategy": "pending", "environment_map": "pending",
        "test_data_strategy": "pending", "entry_exit_criteria": "pending",
        "traceability_audit": "pending", "engineering_assumptions": "pending",
        "open_questions": "pending"
      } }

SOURCE_LOG = []
CHANGE_LOG = []

## Zero Invention Policy
Every in-scope feature MUST map to an EPIC. Every quality risk MUST map to
an ADR, NFR, or RSK. No invented features, risks, or environments.
Inferred items → status: assumption (with rationale).

## PATH GUARD — EXTENDED (supplements the PATH GUARD in Step 1)
Do NOT infer a parent folder from sibling parameters (e.g. prd_path, epics_path,
target_architecture_path).
  Wrong: artifacts/outputs/product-delivery/ + qa-master-test-plan
         (stealing prefix from a sibling's path)
  Right: qa-master-test-plan (use the parameter value directly, relative to execution_dir)
If a sibling parameter has a full path and master_test_plan_path is bare, that is an
UPSTREAM BUG — abort with a Gap Report instead of adopting the sibling's parent.

## Apply execution-protocol.md Section 10
Phase A (skeleton-first within 5 tool calls of entering Step 4) then Phase B (one section per `Edit` call). Tool discipline (§10.5) is **mandatory**: skeleton via `Write`, sections via `Edit`, NEVER `Bash + sed/python3/awk` to mutate SPEC_FILE. The non-ASCII fallback (§10.5.1) auto-applies when content is non-English. NEVER fall back to bulk rewriting when one `Edit` fails — fix the `Edit` call instead.

Skeleton stub text — must be ASCII: `status: pending - will be generated` (ASCII hyphen U+002D).

Section list (template order): `scope_matrix -> risk_assessment -> test_strategy -> environment_map -> test_data_strategy -> entry_exit_criteria -> traceability_audit -> engineering_assumptions -> open_questions`. See `references/qe-master-plan-template.md` for full structure.

## Internal Reasoning: ALL in English regardless of output language.
```
**Execution:** automated

### Step 2: Input Validation (STOP-GATE)

**Command:**
```
## Critical Gate
READ prd_content FROM prd_path (support both single-file specs and legacy multi-file)
IF missing or empty → write Gap Report to AUDIT_FILE → EXIT.

READ epics_content FROM epics_path (support both single-file specs and legacy multi-file)
IF missing or empty → write Gap Report to AUDIT_FILE → EXIT.

## Extract Upstream Data
FROM prd_content EXTRACT:
  MTP_CONTEXT = {
    prd_fr_ids: {FR-XX → description, priority},
    prd_nfr_ids: {NFR-XX → description, target, category},
    prd_risks: [RSK-XX entries],
    prd_assumptions: [ASM-XX entries],
    prd_kpi_ids: {KPI-XX → description, target, measurement},
    personas: [user roles/actors]
  }

FROM epics_content EXTRACT:
  MTP_CONTEXT += {
    epic_list: [EPIC-XX with titles, priority tiers, complexity],
    epic_fr_mappings: {EPIC-XX → [FR-XX IDs]},
    epic_dependencies: [dependency pairs],
    enablers: [ENABLER-XX IDs],
    spikes: [SPIKE-XX IDs]
  }

## Context Budget Rule — CRITICAL
## Read ONLY manifest/index files from upstream artifacts.
## Do NOT open individual per-item files (adrs/adr-001-*.md, contexts/bc-01-*.md,
## services/svc-01-*.md). The catalog tables in the manifest contain all traceability
## data needed for test planning. Opening individual files will exhaust context
## before generation begins.

## Optional Inputs (enhance, don't block)
IF adrs_path exists:
  READ the ADR-SPEC manifest file ONLY (ADR-SPEC-*.md — the catalog/index).
  Do NOT read individual ADR files from adrs/ subfolder.
  FROM ADR-SPEC manifest EXTRACT:
    MTP_CONTEXT += {
      adr_decisions: {ADR-NNN → {title, category, decision_summary, technology}},
      tech_stack: {layer → {technology, version}}
    }
  ## The adr_catalog table, tech_stack_matrix, and impact_matrix in the manifest
  ## contain all data needed. Individual ADR files add prose that wastes context.
  LOG "ADRs loaded from manifest: {count} decisions"
ELSE:
  MTP_CONTEXT.adr_decisions = {}
  LOG "No ADRs provided. Risk assessment limited to PRD NFRs. [Assumption]"
  Register in engineering_assumptions.

IF target_architecture_path exists:
  READ the architecture manifest/index file ONLY (ARCH-SPEC-*.md or 00-index.md).
  Do NOT read individual service files from services/ subfolder.
  FROM architecture manifest EXTRACT:
    MTP_CONTEXT += {
      services: [SVC-XX with names, slices],
      environments: [env definitions with purpose/scale],
      integration_patterns: [patterns],
      deployment_strategy: {description}
    }
  ## The service_catalog table in the manifest has all service names, BCs, and slices.
  ## Individual service specs add implementation detail not needed for test planning.
  LOG "Architecture loaded from manifest: {service_count} services, {env_count} environments"
ELSE:
  MTP_CONTEXT.services = []
  MTP_CONTEXT.environments = []
  LOG "No architecture provided. Environment mapping derived from defaults. [Assumption]"
  Register in engineering_assumptions.

Detect language → DETECTED_LANGUAGE
```
**Execution:** automated

### Step 3: Upstream Consistency Rules

**Loaded once. Apply during generation.**

```
## UPSTREAM CONSISTENCY RULES (Mandatory)

# 1. Zero Invention of Features
Every in-scope feature MUST trace to an EPIC-XX in MTP_CONTEXT.epic_list.
No invented test scenarios for features that don't exist in the epics backlog.

# 2. Zero Invention of Risks
Every quality risk MUST trace to an ADR decision (MTP_CONTEXT.adr_decisions)
or an NFR (MTP_CONTEXT.prd_nfr_ids) or a PRD risk (MTP_CONTEXT.prd_risks).
No invented risks without source.
If a risk is inferred from architectural patterns → mark [Assumption].

# 3. Epic Priority Alignment
Test prioritization MUST follow epic priority tiers:
Must Have → P0 (block release). Should Have → P1. Could Have → P2. Won't Have → Out of Scope.

# 4. Architecture Environment Fidelity
IF architecture provides environment definitions → use them exactly.
Do NOT invent environments not in the architecture package.
If no architecture → use defaults (Local, CI, Staging, Production), mark [Assumption].

# 5. Technology Neutrality
Test tool recommendations use capability language unless section IS about tool selection.
Example: "API testing framework" not "Postman".

# 6. PRD Risk/Assumption Carry-Forward
RSK-XX from MTP_CONTEXT.prd_risks MUST appear in risk_assessment with test mitigations.
ASM-XX MUST be surfaced in engineering_assumptions.

# 7. NFR Test Coverage
Every NFR-XX MUST have at least one test approach in test_strategy.
NFR without testable target → flag as [PENDING INPUT - NFR Target].

# 8. Source Fidelity Check (before writing spec)
  a. Feature references: all EPIC-XX exist in MTP_CONTEXT.epic_list
  b. ADR references: all ADR-NNN exist in MTP_CONTEXT.adr_decisions
  c. Environment references: all match MTP_CONTEXT.environments
  d. No invented features, risks, or environments
  IF violations → correct before writing. Log corrections in CHANGE_LOG.
```
**Execution:** automated

### Step 4: Generate Agent-Native MTP Spec

Read `references/qe-master-plan-template.md` for section structure.

Generate the complete spec following the template. Apply these rules:

**Section Generation Order (data flows forward):**

1. **scope_matrix** — from MTP_CONTEXT.epic_list, epic_fr_mappings, enablers, spikes
   - Every EPIC-XX mapped to test priority (P0/P1/P2) based on priority tier
   - Out of scope: Won't Have epics + PRD exclusions
   - Scope verification: in_scope + out_of_scope == total epics

2. **risk_assessment** — from MTP_CONTEXT.adr_decisions, prd_nfr_ids, prd_risks + scope_matrix
   - ADR-derived risks: one quality risk per ADR decision
   - NFR-derived risks: one risk per NFR with test type and pass criteria
   - PRD risk carry-forward: all RSK-XX with QA impact and mitigation
   - Risk priority matrix: count by level with test response

3. **test_strategy** — from scope_matrix, risk_assessment, MTP_CONTEXT.services, prd_nfr_ids
   - Test levels: unit, integration, system/E2E, performance, security, accessibility
   - Test types per priority tier (P0/P1/P2)
   - NFR test approach: every NFR-XX gets a test approach
   - Automation strategy: pyramid proportions, CI integration

4. **environment_map** — from MTP_CONTEXT.environments/services/deployment_strategy, test_strategy
   - Use architecture environments if available, defaults if not
   - Promotion pipeline with gate criteria per transition
   - Service-to-environment mapping if architecture available

5. **test_data_strategy** — from scope_matrix, environment_map, MTP_CONTEXT.services
   - Data categories: synthetic, anonymized, production
   - Requirements per test level
   - Privacy & compliance from PRD constraints

6. **entry_exit_criteria** — from environment_map, risk_assessment, test_strategy
   - Entry/exit criteria per phase in promotion pipeline
   - Gherkin gate specifications (happy + unhappy paths)
   - Release criteria referencing NFR targets

7. **traceability_audit** — from ALL sections + MTP_CONTEXT
   - Epic coverage check
   - ADR-to-risk alignment check
   - NFR test coverage check
   - Environment-architecture alignment check
   - PRD risk carry-forward check
   - Out-of-scope completeness check
   - Audit summary with PASS/FAIL per check

8. **engineering_assumptions** — consolidated from all sections
   - Every assumption with section, rationale, confidence, validation needed

9. **open_questions** — consolidated from all sections
   - Every gap, missing input, pending decision
   - PRD traceability gaps carried forward (never silently resolved)

**IF MODE == REPAIR:**
  Load existing spec. Apply REPAIR_DIRECTIVES to targeted sections only.
  Preserve untargeted sections verbatim.
  Re-run traceability_audit after any section repair.
  Increment version (patch).

**Execution:** automated

### Step 5: Quality Validation Gate

**Command:**
```
Validate the generated spec before writing:

1. Scope Completeness: in_scope + out_of_scope == total MTP_CONTEXT.epic_list entries
2. Risk Traceability: every QR-NNN has a source (ADR/NFR/RSK)
3. NFR Coverage: every NFR-XX has a test approach (or [PENDING INPUT] flag)
4. Environment Fidelity: no invented environments (match architecture or defaults)
5. PRD Risk Carry-Forward: every RSK-XX appears in risk_assessment
6. Consistency: all EPIC-XX references exist in MTP_CONTEXT.epic_list
7. Audit Integrity: traceability_audit results match actual section content
8. open_questions: every gap/assumption appears exactly once

9. Agent-Native Conformance (HARD GATE — fails the run, no auto-correct):
   a. Section allowlist: extract every line matching `^## ` from SPEC_FILE.
      The set MUST equal exactly {scope_matrix, risk_assessment, test_strategy,
      environment_map, test_data_strategy, entry_exit_criteria,
      traceability_audit, engineering_assumptions, open_questions}.
      Any unknown ## heading → FAIL with reason "unknown_section: {name}".
   b. No numbered narrative headings: `^## [0-9]+\.` → FAIL.
   c. No PROHIBITED sections: grep for any of Executive Summary, Purpose,
      Introduction, Background, Process Log, Change Log, Meeting Agenda,
      Stakeholder Communication, Tool Selection Rationale (narrative)
      in `^## ` headings → FAIL with reason "prohibited_section: {name}".
   d. Heading case: every `^## ` heading body MUST be lowercase snake_case
      (regex `^## [a-z][a-z0-9_]*$`) → FAIL on any violation.
   e. Prose density: outside fenced code blocks, no contiguous run of more than
      2 narrative lines (capital start, period end, > 15 words each) → FAIL.
   f. Filename: basename(SPEC_FILE) MUST match `^MTP-SPEC-[A-Za-z0-9_-]+\.md$`
      → FAIL with reason "wrong_filename: {actual}".

   On any FAIL in check 9, ABORT with a Gap Report. Do NOT auto-correct.

IF corrections needed for checks 1-8 → apply in place, log to CHANGE_LOG.
STOP-GATE: IF zero features in scope → ABORT.
STOP-GATE: IF check 9 (Agent-Native Conformance) FAILS any sub-check → ABORT
the run with a Gap Report describing the violation.
```
**Execution:** automated

### Step 6: Write Outputs

**Command:**
```
0. Filename guard (HARD GATE — do this BEFORE any write):
   ASSERT basename(SPEC_FILE)  =~ /^MTP-SPEC-[A-Za-z0-9_-]+\.md$/
   ASSERT basename(AUDIT_FILE) =~ /^MTP-AUDIT-[A-Za-z0-9_-]+\.md$/
   If either basename was tampered with at any earlier step (e.g. renamed to
   master-test-plan.md, QE-MTP-*.md, etc.) → ABORT with a Gap Report.
   Do NOT silently overwrite the path with the canonical name; surface the bug.

1. Write SPEC_FILE (MTP-SPEC-{SESSION_ID}.md)
   - Set the MTP-SPEC front-matter `version:` to NEW_VERSION. On REPAIR this MUST be the
     incremented patch (Step 1: PREVIOUS_VERSION → NEW_VERSION) — editing content in place
     without bumping `version` is a §7 violation. See execution-protocol §7.2 step 8.

2. Write AUDIT_FILE (MTP-AUDIT-{SESSION_ID}.md):
   - Session metadata (version=NEW_VERSION, mode, session_id, timestamp, language)
   - Sources referenced (SOURCE_LOG)
   - Decisions made (CHANGE_LOG)
   - Summary counts:
     features_in_scope, out_of_scope_count, quality_risks,
     test_levels, environments, epic_coverage_pct, nfr_coverage_pct
   - REPAIR-only: set `mode: REPAIR` and APPEND (do not overwrite) a `## Repair History`
     entry — version, timestamp, directives_applied, sections_changed, sections_preserved,
     repair_delta (per execution-protocol §7.2 step 8).

3. REPAIR self-check (execution-protocol §7.2 step 9): before final_response, confirm the
   MTP-SPEC `version` is strictly greater than PREVIOUS_VERSION AND the MTP-AUDIT has the
   new `## Repair History` entry. If not, fix the bookkeeping now — do not finish.

4. Verify both files exist and are non-empty.

5. APPEND to ./artifacts/outputs/artifact-tracking.md:
   session, artifact_type: master_test_plan, mode, version,
   features_in_scope, quality_risks, test_levels, environments,
   epic_coverage_pct, nfr_coverage_pct, timestamp


Memory Bank artifact type: `"{N} test-domains"` (e.g., `"8 test-domains"`).

**Memory Bank — MANDATORY session-end writes:**
1. Overwrite `context-pack/active-context.md` with session status, decisions, blockers, key artifacts (see execution-protocol.md Section 4 for schema).
2. Append one milestone row to `context-pack/progress.md` with artifact count above.

**LAST ACTION — MANDATORY:** Update `_progress.json` status to `COMPLETED` with `completed_at` timestamp.
If the session failed, set status to `FAILED` instead.

Ready for downstream consumption (defining-qe-strategy, generating-test-cases).
```
**Execution:** automated

### Step 5: Emit Harness Outputs Sidecar

**Apply execution-protocol.md Section 11.** Mandatory when the prompt contains a `## Run metadata` block (Stepwise invocation); skip otherwise. FINAL file write of the run.

**Output parameters this skill produces** (one key per row of the prompt's `## Output parameters` table):

- `master_test_plan_path`: the resolved `master_test_plan_path` parameter — the SPEC_FOLDER you wrote into.

**Example sidecar contents** (values illustrative):

```json
{ "master_test_plan_path": "/abs/path/to/artifacts/outputs/<capability>/mtp" }
```

## Test Tool Classification (AUTHORITATIVE — downstream skills must honor this)

For each test tool included in the MTP, explicitly document its classification:

```
| Tool | Phase | blocking_status | Becomes blocking when |
|------|-------|-----------------|----------------------|
| {tool} | {phase} | blocking | Always |
| {tool} | {phase} | optional | Presence encouraged but not required |
| {tool} | {phase} | desirable_not_blocking | {condition under which it becomes blocking} |
```

Rules:
- `blocking`: absence of this tool causes the quality gate to FAIL
- `optional`: absence is allowed; presence is encouraged
- `desirable_not_blocking`: absence is noted but does NOT fail the gate

This classification is **authoritative for all downstream reviews**. The `reviewing-code` skill MUST honor this classification. If a tool is `desirable_not_blocking`, it MUST NOT be flagged as BLOCKING in any downstream VALIDATION_REPORT.

## Reference Files
- `references/qe-master-plan-template.md` — Agent-native QE master test plan spec structure

## Rendering
For human-readable output, use `humanize-spec` with the rendering profile at
`profiles/qe-master-plan.md`. Supports full render and per-section render
(executive_summary, scope_matrix, risk_assessment, test_strategy, environments,
test_data, entry_exit_criteria, traceability, governance).
