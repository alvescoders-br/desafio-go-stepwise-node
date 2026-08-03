---
name: defining-qe-strategy
description: >
  Develops comprehensive test strategy from master test plan, PRD, architecture,
  and domain boundaries. Output is a single agent-native spec with zero prose —
  structured tool selections, test pyramid configuration, data strategy,
  performance gates, CI/CD integration, and cross-cutting concerns. All items
  carry status and source tags. Validation audit runs as generation-time gate.
  All gaps consolidated in single open_questions registry.
  Enforces upstream consistency with MTP scope and risk assessment.
  BUILD and REPAIR modes. FIC context discipline (Correct > Complete > Concise).
  Human-readable output generated on demand via humanize-spec skill (separate).
license: Globant
metadata:
  author: aipods-team
  version: 3.1.0
  category: quality-engineering
  tags: quality-engineering-planning, automated, agent-native
---

# Defining QE Strategy — Agent-Native Spec

## Quick Start
Develop detailed test strategy from master test plan and architecture artifacts.
Output is a **single file**: `{strategy_output_path}/STRATEGY-SPEC-{SESSION_ID}.md`.
No prose. No narrative. No meeting agendas. Only structured data that downstream
agents (test case generation, E2E test cases, test scripts, framework setup) need.

## Output Architecture

```
{strategy_output_path}/
├── STRATEGY-SPEC-{SESSION_ID}.md     ← Single agent-native spec (all sections)
└── STRATEGY-AUDIT-{SESSION_ID}.md    ← Session audit trail (metadata only)
```

**Why single file:** Agent-native strategy specs are 50% smaller than human-readable
versions. Even at enterprise scale (50+ services), the spec fits comfortably in context
because strategies define *approaches* (one row per service/level), not individual test
cases. No batching or Write-Flush-Forget needed.

**Human-readable output:** Not produced by this skill. Use `humanize-spec` skill
with the `qe-strategy` rendering profile to generate rich strategy documents
(executive overview, guiding principles, enhancement suggestions) from this spec on demand.

## Parameters
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_name | string | Yes | Project identifier |
| prd_path | string | Yes | Path to PRD document or PRD-SPEC |
| master_test_plan_path | string | Yes | Path to master test plan (output from creating-qe-master-plan) |
| strategy_output_path | string | Yes | Output path for test strategy |
| domain_boundaries_path | string | No | Path to domain boundaries documentation |
| adrs_path | string | No | Path to ADR collection |
| target_architecture_path | string | No | Path to target architecture documentation |
| failure_feedback | string | No | Feedback for REPAIR mode |

**If any Required parameter is not defined, ABORT EXECUTION.**

## Output Contract — HARD RULES (not suggestions)

The spec is consumed by downstream agents, not humans. Violating any rule below
ABORTS the skill in Step 3 (Quality Validation Gate).

### Filename
- Output filename MUST match regex: `^STRATEGY-SPEC-[A-Za-z0-9_-]+\.md$`
- Example valid: `STRATEGY-SPEC-qeplan-001.md`
- Example invalid: `QTS-SPEC-qeplan-001.md`, `qe-test-strategy.md`, anything else.

### ALLOWED_SECTIONS (top-level `## ` headings, exact set, exact names)
Only these 9 top-level headings may appear in the spec body, in this order:
```
1. ## scope_summary
2. ## tool_selections
3. ## pyramid_config
4. ## data_strategy
5. ## performance_gates
6. ## cicd_stages
7. ## cross_cutting
8. ## validation_summary
9. ## open_questions
```
Any other top-level heading → ABORT.

### PROHIBITED — DO NOT GENERATE
These belong to `humanize-spec` (the rendering profile reconstructs them).
If any of these appear in the spec, ABORT:
- `## Purpose`, `## Strategy Purpose`, `## 1. Purpose and Objectives`, or any prose
  "this document defines…" introduction
- `## Strategic Objectives`, `## Governing Principles`
- `## Strategy Scope` (the structured equivalent is `scope_summary`)
- `## Test Design Techniques`, `## Test Level Strategies`, `## TLS-XX` sections
- `## Bounded Context Test Coverage` (lives inside `pyramid_config`)
- `## Tool Stack and Rationale` (the structured equivalent is `tool_selections`)
- `## CI/CD Integration Strategy` (the structured equivalent is `cicd_stages`)
- `## Defect Management Strategy`, `## Test Metrics and Reporting`,
  `## Reporting & Notifications`, `## Flaky Test Management`
- `## Traceability Strategy` or `## Traceability Index` (lives in `validation_summary`)
- `## Enhancement Suggestions`, `## Next Meeting Agenda`
- `## Process Log`, `## Change Log` (these go to AUDIT_FILE)
- Any `## N. UPPERCASE NARRATIVE TITLE` heading (numbered narrative sections)

### Heading and Prose Rules
- Section headings MUST be lowercase snake_case (e.g., `## scope_summary`).
  Numbered narrative headings (`## 1. PURPOSE AND OBJECTIVES`) → ABORT.
- No narrative paragraphs. Prose density limit:
  - Outside fenced code blocks (```), no contiguous run of more than 2 lines
    where each line is a sentence (capital-letter start, period end, > 15 words).
  - Bulleted/listed structured items are fine; prose paragraphs are not.
- No motivational text, no "why this matters", no executive summaries.

## Workflow

### Step 1: Initialize

**Command:**
```
# Lead QA Automation Architect — Agent-Native Spec Generator
# Persona: Technical, precise, strategic. Expert in test architecture,
#   CI/CD integration, performance engineering, and shift-left practices.
# CRITICAL: NON-INTERACTIVE SESSION.
# MISSION: Operationalize MTP into actionable test strategy. Zero invention.

IF failure_feedback NOT empty:
  MODE = REPAIR
  SPEC_FOLDER = resolve_parent_folder(strategy_output_path)
  SPEC_FILE = find existing STRATEGY-SPEC-*.md in SPEC_FOLDER
  IF not found → write Gap Report → EXIT
  Load SPEC_FILE → PREVIOUS_SPEC → SOURCE_LOG
  PREVIOUS_VERSION = extract version
  NEW_VERSION = increment patch
  Parse failure_feedback → REPAIR_DIRECTIVES [{ section, instruction, reason }]
ELSE:
  MODE = BUILD
  SPEC_FOLDER = strategy_output_path + '/'
  SPEC_FILE = SPEC_FOLDER + 'STRATEGY-SPEC-' + SESSION_ID + '.md'
  NEW_VERSION = "1.0.0"
  mkdir -p SPEC_FOLDER

  ## SESSION_ID goes in spec FILENAMES only — never in the folder name.
  ## The folder must match the capability YAML path parameter exactly.

  ## FIRST ACTION — MANDATORY: Write _progress.json before any other file write.
  ## This prevents the orchestrator from sending SIGINT and gives downstream pre-gates
  ## a claim marker even if the skill dies before producing its spec.
  ## Section-shape variant — see execution-protocol.md §10.1 for schema and §10.6 for CONTINUE-on-re-entry.
  WRITE SPEC_FOLDER + '/_progress.json':
    { "skill": "defining-qe-strategy", "session_id": "<SESSION_ID>",
      "status": "RUNNING", "started_at": "<ISO timestamp>", "completed_at": null,
      "skeleton_written": false,
      "sections": {
        "scope_summary": "pending", "tool_selections": "pending",
        "pyramid_config": "pending", "data_strategy": "pending",
        "performance_gates": "pending", "cicd_stages": "pending",
        "cross_cutting": "pending", "validation_summary": "pending",
        "open_questions": "pending"
      } }

  ## SECOND ACTION — MANDATORY: Write skeleton SPEC_FILE stub immediately.
  ## If the skill fails at any later point, this stub lets the pre-gate detect an
  ## incomplete strategy and REJECT instead of silently approving.
  WRITE SPEC_FILE with skeleton:
    # {project_name} — QE Strategy Spec
    version: {NEW_VERSION}
    session_id: {SESSION_ID}
    status: STUB
    sections_pending: [scope_summary, tool_selections, pyramid_config,
                       data_strategy, performance_gates, cicd_stages,
                       cross_cutting, validation_summary, open_questions]

SOURCE_LOG = []
CHANGE_LOG = []

## Zero Invention Policy
Every test approach traces to an MTP scope feature, quality risk, or NFR.
Not in source → status: pending. Never infer test scenarios or tool mandates
without evaluation. Inferred industry standards → status: assumption (with ASM-XX ID).

## PATH GUARD — MANDATORY
strategy_output_path is the FINAL folder path as resolved by the capability.
Use it EXACTLY as provided — do NOT prepend artifacts/outputs/ or any other prefix.
Do NOT infer a parent folder from sibling parameters (e.g. master_test_plan_path, prd_path).
  Wrong: artifacts/outputs/product-delivery/ + qa-test-strategy
         (stealing prefix from a sibling's path)
  Right: qa-test-strategy (use the parameter value directly, relative to execution_dir)
If strategy_output_path is a bare segment (no `/` or `./`), treat it as relative to CWD.
If a sibling parameter has a full path and yours is bare, that is an UPSTREAM BUG —
abort with a Gap Report instead of adopting the sibling's parent.

## Apply execution-protocol.md Section 10
Phase A (skeleton-first within 5 tool calls of entering Step 2) then Phase B (one section per `Edit` call). Tool discipline (§10.5) is **mandatory**: skeleton via `Write`, sections via `Edit`, NEVER `Bash + sed/python3/awk` to mutate SPEC_FILE. The non-ASCII fallback (§10.5.1) auto-applies when content is non-English. NEVER fall back to bulk rewriting when one `Edit` fails — fix the `Edit` call instead.

Skeleton stub text — must be ASCII: `status: pending - will be generated` (ASCII hyphen U+002D).

Section list (template order): `scope_summary -> tool_selections -> pyramid_config -> data_strategy -> performance_gates -> cicd_stages -> cross_cutting -> validation_summary -> open_questions`. See `references/qe-strategy-template.md` for full structure.

## Context Utilization Monitoring — FIC Protocol
Standard §5 FIC monitoring applies. The per-section discipline of §10 already bounds per-call payload size; §5 covers the residual case where extraction inputs themselves grow large. On 60% threshold: write current state via Edit to the in-progress section, flip status to `COMPACTION_NEEDED`, log alert. No bulk in-memory dump — that violates §10.

## Internal Reasoning: ALL in English regardless of output language.
```
**Execution:** automated

### Step 1.5: Input Validation Gate

**Command:**
```
## Critical Gate
READ prd_content FROM prd_path
IF missing or empty → write Gap Report to SPEC_FILE → EXIT.

READ mtp_content FROM master_test_plan_path (or MTP folder if multi-file)
IF missing or empty → write Gap Report to SPEC_FILE → EXIT.
"Master Test Plan is REQUIRED. Cannot define strategy without scope and risk assessment."

## Extract from MTP
FROM mtp_content EXTRACT:
  STRATEGY_CONTEXT = {
    scope_features: [epic-to-test mappings with priorities from MTP],
    out_of_scope: [excluded items from MTP],
    quality_risks: [risk-to-mitigation mappings from MTP],
    test_levels: [test levels defined in MTP],
    environment_map: [environments from MTP],
    promotion_pipeline: [pipeline stages from MTP],
    nfr_test_approaches: [NFR-to-test mappings from MTP],
    mtp_assumptions: [engineering assumptions from MTP]
  }

## Extract from PRD
FROM prd_content EXTRACT:
  STRATEGY_CONTEXT += {
    prd_nfr_ids: {NFR-XX → description, target},
    prd_risks: [RSK-XX entries],
    prd_assumptions: [ASM-XX entries]
  }

## Optional Inputs (enhance, don't block)
IF domain_boundaries_path exists:
  FROM domain_boundaries EXTRACT:
    STRATEGY_CONTEXT += {
      bounded_contexts: [BC-XX],
      services: [SVC-XX with slices],
      integration_patterns: [patterns]
    }
  LOG "Domain boundaries loaded"
ELSE:
  STRATEGY_CONTEXT.services = []
  LOG "No domain boundaries. Service-level strategy derived from MTP. [Assumption]"

IF adrs_path exists:
  FROM adrs EXTRACT:
    STRATEGY_CONTEXT += {
      adr_decisions: {ADR-NNN → {category, technology, decision_summary}},
      tech_stack: {layer → {technology, version}}
    }
  LOG "ADRs loaded"
ELSE:
  STRATEGY_CONTEXT.adr_decisions = {}
  LOG "No ADRs. Tool selection based on capability needs. [Assumption]"

IF target_architecture_path exists:
  FROM architecture EXTRACT:
    STRATEGY_CONTEXT += {
      deployment_strategy: {description},
      cicd_pipeline: {stages if defined},
      nfrs_by_context: {per-service NFR targets}
    }
  LOG "Architecture loaded"

Detect language → DETECTED_LANGUAGE

IF MODE == REPAIR:
  Load existing SPEC_FILE sections → identify repair targets
  Apply REPAIR_DIRECTIVES
```
**Execution:** automated

### Step 2: Generate Agent-Native Strategy Spec (Chunked, Write-Flush-Forget)

Read `references/qe-strategy-template.md` for section structure.

Generate sections one at a time using Write-Flush-Forget:
  FOR EACH section in [scope_summary, tool_selections, pyramid_config,
                       data_strategy, performance_gates, cicd_stages,
                       cross_cutting, validation_summary, open_questions]:
    1. Generate section content in memory.
    2. APPEND section to SPEC_FILE (overwriting the `status: STUB` header on
       the first append, then appending subsequent sections).
    3. Update _progress.json: completed += 1, items += [section_name].
    4. Flush in-memory section text.

Apply these rules to ALL sections:

**Status Protocol:**
- Every item has a `status` field: `complete`, `pending`, or `assumption`
- `complete`: all fields populated from source evidence
- `pending`: one or more fields missing → item also registered in `open_questions`
- `assumption`: inferred from industry standard → ASM-XX ID assigned

**Source Tagging:**
- Every item has a `source` field pointing to MTP, PRD, ADR, or architecture
- No source → status MUST be `pending` or `assumption`

**Upstream Consistency Rules (apply during generation):**

1. MTP Scope Fidelity — Every test approach traces to a scope feature or quality
   risk from STRATEGY_CONTEXT. No invented test scenarios.

2. Technology Neutrality — ALL sections EXCEPT `tool_selections` use capability
   language ("E2E testing framework", not "Playwright"). After `tool_selections`,
   other sections MAY reference the selected tool BY NAME only when describing
   configuration specific to that tool.

3. Horizontal Slicing (BE/FE) — Every test type assignment specifies scope:
   - `[ID]-BE`: API tests, service integration, domain logic, data persistence
   - `[ID]-FE`: UI tests, visual regression, accessibility, client-side validation
   No hybrid "full-stack" test assignments.

4. Gherkin for Gate Criteria — CI/CD gate rules and performance gates include
   Gherkin specifications: Happy Path (gate passes) + Unhappy Path (gate fails).

5. NFR Traceability — Performance gates and quality thresholds reference NFR-XX IDs
   from PRD. No explicit NFR target → status: assumption with ASM-XX ID.

6. MTP Risk Coverage — Every quality risk in STRATEGY_CONTEXT.quality_risks has a
   corresponding test approach. Risk without test coverage → gap in open_questions.

**Section Generation Order & Dependencies:**
- `scope_summary`: needs STRATEGY_CONTEXT overview
- `tool_selections`: needs quality_risks, test_levels, services → produces tool decisions
- `pyramid_config`: needs tool_selections, scope_features, services → produces test structure
- `data_strategy`: needs environment_map, scope_features → produces data provisioning
- `performance_gates`: needs prd_nfr_ids, quality_risks → produces performance thresholds
- `cicd_stages`: needs tool_selections, pyramid_config, performance_gates, promotion_pipeline
- `cross_cutting`: needs scope_features, quality_risks, tool_selections
- `validation_summary`: needs all above sections → audit results
- `open_questions`: consolidation of all gaps (always last)

**Tool Selection Generation Rules:**
- Minimum 2 alternatives per category
- Each with Pros, Cons, Score (weighted against evaluation criteria)
- ADR alignment: if ADRs specify tech stack, tool compatibility MUST be verified
- Categories derived from STRATEGY_CONTEXT.test_levels: unit_be, unit_fe,
  api_integration, e2e_fe, performance, sast, dast, contract, accessibility

**Pyramid Configuration Rules:**
- IF services available: per-service with BE/FE slicing
- ELSE: generic pyramid per test priority tier (P0/P1/P2), status: assumption
- Coverage targets: unit >80%, integration >70%, E2E P0 scenarios

**Performance Gate Rules:**
- FOR EACH performance-related NFR: derive gate threshold (with margin)
- IF NFR lacks numeric target → assign assumption threshold, register in open_questions
- Include FE Performance Budget (Core Web Vitals: LCP, FID, CLS, Bundle Size)

**CI/CD Stage Rules:**
- FOR EACH stage: tests executed, gate criteria (Gherkin), duration target, automation
- Include parallelization strategy and sharding approach

**Cross-Cutting Rules:**
- Security: SAST (every commit), DAST (staging), dependency scan, penetration
- Accessibility: WCAG 2.1 AA, applies to [SVC-XX]-FE slices only
- Contract: consumer-driven, applies to [SVC-XX]-BE with cross-service dependencies
- Chaos/Resilience: only if quality_risks includes availability/resilience risks

**Execution:** automated

### Step 3: Quality Validation Gate

**Command:**
```
Run ALL checks. Auto-correct where possible. Log corrections to CHANGE_LOG.
Uncorrectable issues → register in open_questions.

1. MTP Scope Coverage:
   Every feature in STRATEGY_CONTEXT.scope_features addressed by ≥1 entry
   in pyramid_config. Missing → gap in open_questions.coverage_gaps.

2. MTP Risk Coverage:
   Every risk in STRATEGY_CONTEXT.quality_risks has a corresponding test approach.
   Missing → gap in open_questions.coverage_gaps.

3. NFR Test Coverage:
   Every NFR in STRATEGY_CONTEXT.prd_nfr_ids addressed by performance_gates
   or pyramid_config. Missing or target is assumption → flag in open_questions.

4. Tool Selection Completeness:
   Every test level in STRATEGY_CONTEXT.test_levels has a selected tool.
   Missing → gap in open_questions.

5. BE/FE Slicing Validation:
   Every pyramid_config entry specifies BE or FE scope. No hybrid assignments.
   Violations → auto-correct by splitting into BE + FE entries.

6. Gherkin Gate Coverage:
   Every CI/CD stage has Gherkin gate criteria (happy + unhappy).
   Missing → auto-generate from gate_criteria fields.

7. Technology Neutrality Compliance:
   Scan all sections except tool_selections for tool names that should be
   capability language. Violations → auto-correct. Log corrections.

8. Source Fidelity:
   a. Feature references trace to STRATEGY_CONTEXT.scope_features
   b. Risk references trace to STRATEGY_CONTEXT.quality_risks
   c. Environment references match STRATEGY_CONTEXT.environment_map
   Violations → correct before writing. Log corrections.

9. open_questions Completeness:
   Every pending/assumption/gap item appears exactly once in open_questions.
   No scatter. No duplicates.

10. ID Consistency:
    No duplicate IDs, no gaps in numbering across all sections.

11. Agent-Native Conformance (HARD GATE — fails the run, no auto-correct):
    a. Section allowlist: extract every line matching `^## ` from SPEC_FILE.
       The set MUST equal exactly {scope_summary, tool_selections, pyramid_config,
       data_strategy, performance_gates, cicd_stages, cross_cutting,
       validation_summary, open_questions} (no others, in any order).
       Any unknown ## heading → FAIL with reason "unknown_section: {name}".
    b. No numbered narrative headings: `^## [0-9]+\.` → FAIL.
    c. No PROHIBITED sections (see Output Contract above): grep for any of
       Purpose, Strategic Objectives, Governing Principles, Strategy Scope,
       Test Design Techniques, Test Level Strategies, TLS-, Bounded Context,
       Tool Stack and Rationale, CI/CD Integration Strategy,
       Defect Management, Test Metrics and Reporting, Reporting & Notifications,
       Flaky Test Management, Traceability Strategy, Traceability Index,
       Enhancement Suggestions, Next Meeting Agenda, Process Log, Change Log
       in `^## ` headings → FAIL with reason "prohibited_section: {name}".
    d. Heading case: every `^## ` heading body MUST be lowercase snake_case
       (regex `^## [a-z][a-z0-9_]*$`) → FAIL on any violation.
    e. Prose density: outside fenced code blocks, no contiguous run of more than
       2 narrative lines (capital-letter start, period end, > 15 words each) → FAIL.
    f. Filename: basename(SPEC_FILE) MUST match `^STRATEGY-SPEC-[A-Za-z0-9_-]+\.md$`
       → FAIL with reason "wrong_filename: {actual}".

    On any FAIL in check 11, ABORT the validation gate and return a Gap Report.
    Do NOT auto-correct (the model that produced the violation will likely
    reproduce it); REPAIR mode with the gap report is the correct recovery path.

Produce validation_summary table in spec:
| Check | Expected | Actual | Status |
Coverage percentages for checks 1-4. Counts for checks 5-7. PASS/FAIL per check.
Check 11 sub-checks (a-f) MUST each be reported individually with their FAIL reason
when applicable. Overall status: PASS or FAIL with reasons.

STOP-GATE: IF scope coverage < 50% AND risk coverage < 50% → ABORT.
STOP-GATE: IF check 11 (Agent-Native Conformance) FAILS any sub-check → ABORT
the run with a Gap Report describing the violation; do NOT write a PASS spec on top.
```
**Execution:** automated

### Step 4: Write Outputs

**Command:**
```
0. Filename guard (HARD GATE — do this BEFORE any write):
   ASSERT basename(SPEC_FILE)  =~ /^STRATEGY-SPEC-[A-Za-z0-9_-]+\.md$/
   ASSERT basename(AUDIT_FILE) =~ /^STRATEGY-AUDIT-[A-Za-z0-9_-]+\.md$/
   If either basename was tampered with at any earlier step (e.g. renamed to
   QTS-SPEC-*, qe-test-strategy.md, etc.) → ABORT with a Gap Report.
   Do NOT silently overwrite the path with the canonical name; surface the bug.

1. Write SPEC_FILE (STRATEGY-SPEC-{SESSION_ID}.md)
   - Set the STRATEGY-SPEC front-matter `version:` to NEW_VERSION. On REPAIR this MUST be
     the incremented patch (Step 1: PREVIOUS_VERSION → NEW_VERSION) — editing content in
     place without bumping `version` is a §7 violation. See execution-protocol §7.2 step 8.
2. Write AUDIT_FILE (STRATEGY-AUDIT-{SESSION_ID}.md):
   - Session metadata (version=NEW_VERSION, mode, session_id, timestamp, language)
   - Sources referenced (numbered list from SOURCE_LOG)
   - Decisions made (from CHANGE_LOG)
   - Summary counts: tools_selected, test_levels_configured, performance_gates,
     cicd_stages, mtp_risk_coverage_pct, open_questions count
   - REPAIR-only: set `mode: REPAIR` and APPEND (do not overwrite) a `## Repair History`
     entry — version, timestamp, directives_applied, sections_changed, sections_preserved,
     repair_delta (per execution-protocol §7.2 step 8).
3. REPAIR self-check (execution-protocol §7.2 step 9): before final_response, confirm the
   STRATEGY-SPEC `version` is strictly greater than PREVIOUS_VERSION AND the STRATEGY-AUDIT
   has the new `## Repair History` entry. If not, fix the bookkeeping now — do not finish.
4. Verify both files exist and are non-empty


Memory Bank artifact type: `"{N} strategy-sections"` (e.g., `"6 strategy-sections"`).

**Memory Bank — MANDATORY session-end writes:**
1. Overwrite `context-pack/active-context.md` with session status, decisions, blockers, key artifacts (see execution-protocol.md Section 4 for schema).
2. Append one milestone row to `context-pack/progress.md` with artifact count above.

**LAST ACTION — MANDATORY:** Update `_progress.json` status to `COMPLETED` with `completed_at` timestamp
(and flip the SPEC_FILE header from `status: STUB` to `status: COMPLETE`).
If the session failed, set _progress.json status to `FAILED` and leave SPEC_FILE header as `status: PARTIAL`.

Ready for downstream consumption (Test Cases, E2E Test Cases, Test Scripts, Framework Setup).
```
**Execution:** automated

### Step N: Emit Harness Outputs Sidecar

**Apply execution-protocol.md Section 11.** Mandatory when the prompt contains a `## Run metadata` block (Stepwise invocation); skip otherwise. FINAL file write of the run.

**Output parameters this skill produces** (one key per row of the prompt's `## Output parameters` table):

- `strategy_output_path`: the resolved `strategy_output_path` parameter — the SPEC_FOLDER you wrote into.

**Example sidecar contents** (values illustrative):

```json
{ "strategy_output_path": "/abs/path/to/artifacts/outputs/<capability>/strategy" }
```

## Reference Files
- `references/qe-strategy-template.md` — Agent-native spec structure

## Rendering
For human-readable output, use `humanize-spec` with the rendering profile at
`profiles/qe-strategy.md`. Supports full render and per-section render
(executive_overview, tool_selection, test_pyramid, data_strategy, performance,
cicd_integration, cross_cutting, traceability, governance).
