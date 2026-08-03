---
name: generating-e2e-test-cases
description: >
  Generates end-to-end test cases for user journeys from epics, user stories, test strategy,
  and master test plan using FIC methodology. Produces a manifest file
  (journey_map + epic_map + tc_catalog + coverage data + validations + open_questions) plus
  one Gherkin E2E test case file per epic under a suites/ subfolder. Each test case uses
  strict Gherkin format derived from user journey analysis: every acceptance criterion becomes
  a Then assertion, every gap-detected path is marked. Generates positive (happy path),
  negative (error/cancel/timeout), boundary, and data variation test cases per journey.
  Cross-references test strategy for tool compatibility and MTP for risk-based depth.
  Applies BDD engineering mindset: does not just translate — engineers tests, finding gaps,
  boundary conditions, and negative paths. Uses TC_INDEX as carry-forward contract.
  BUILD and surgical REPAIR modes. Human-readable output via humanize-spec on demand.
license: Globant
metadata:
  author: aipods-team
  version: 3.0.0
  category: quality-engineering
  tags: quality-engineering-planning, automated, agent-native
---

# Generating E2E Test Cases — Agent-Native Spec

## Quick Start
Generate E2E test cases for all user journeys. Output is a **manifest + per-epic Gherkin suites**:

```
{e2e_folder}/
├── E2E-MANIFEST-{SESSION_ID}.md      ← Journey map, coverage data, validations, open_questions
├── suites/                            ← One Gherkin file per epic (UNCHANGED format)
│   ├── epic-01-e2e-suite.md
│   ├── epic-02-e2e-suite.md
│   └── ...
└── E2E-AUDIT-{SESSION_ID}.md         ← Session metadata
```

## Known Failure Modes
<!-- ACCUMULATING — appended by calibrating-updates (WS6). Newest first. Rules MUST be generic/behavioral (project-agnostic); project-specific fixes go to context packs, never here. Format + entry rules: engineering-skills/references/known-failure-modes-format.md. Read these at pre-flight so a lesson learned once recurs no more. -->

## Anti-Patterns (do NOT)
<!-- ACCUMULATING — appended by calibrating-updates (WS6). One line each: **AP-NNN** (ISO-date, source: REC-NNN): prohibition — why. -->

## Why This Architecture

The QA automation agent processes ONE epic's E2E suite at a time.
It does not need all journeys in context to automate one epic.

**Manifest (always loaded):** Journey map with epic-to-journey mappings, TC counts,
FR coverage, validation results, open questions. ~200 lines for a 10-epic project.
Cheap to keep in context.

**Per-epic suite files (loaded on demand):** Full Gherkin E2E test cases.
Already agent-native — strict Given/When/Then with TC_ID, tags, traceability.
60-150 scenarios per P0 epic. The QA automation agent loads one, works through it,
drops it, loads the next.

**Per-epic files are UNCHANGED from v2.0.1.** They were already structured
executable specs. The refactoring targets only the coordination layer
(index + journey map + audit + governance → single manifest).

**Human-readable output:** Not produced by this skill. Use `humanize-spec` skill
with `profiles/e2e-test-cases.md` rendering profile to generate formatted index,
traceability audit, and governance documents on demand.

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_name | string | Yes | Project identifier |
| prd_path | string | Yes | Path to PRD document |
| epics_path | string | Yes | Path to epics document (or epics index folder) |
| master_test_plan_path | string | Yes | Path to master test plan |
| test_strategy_path | string | Yes | Path to test strategy document |
| e2e_tc_path | string | Yes | Output path for E2E test cases |
| user_stories_path | string | No | Path to user stories (for acceptance criteria) |
| adrs_path | string | No | Path to ADR collection |
| failure_feedback | string | No | Feedback for REPAIR mode |

**If any Required parameter is not defined, ABORT EXECUTION.**

## Output Contract — HARD RULES (not suggestions)

The outputs are consumed by the QA automation agent, not humans.
Violating any rule below ABORTS the skill in Step 4.5 (Quality Validation Gate).

### Filenames (regex enforced)
- Manifest: `^E2E-MANIFEST-[A-Za-z0-9_-]+\.md$`
- Audit:    `^E2E-AUDIT-[A-Za-z0-9_-]+\.md$`
- Per-epic suite: `^epic-[0-9]{2}-e2e-suite\.md$` (under `suites/` subfolder)

### Manifest ALLOWED top-level sections (lowercase snake_case, this set only)
```
## scope
## journey_map
## journey_catalog
## epic_map
## tc_catalog
## fr_coverage
## ac_coverage
## test_type_distribution
## persona_coverage
## gap_detected_items
## validations
## open_questions
```
Any other `^## ` heading in the manifest → ABORT.

### Manifest PROHIBITED — DO NOT GENERATE
- `## Executive Summary`, `## Purpose`, `## Introduction`
- `## Process Log`, `## Change Log` (these go to E2E-AUDIT)
- Any `^## [0-9]+\.` numbered narrative section

### Manifest prose limit
Outside fenced code blocks, no contiguous run of more than 2 narrative
lines (capital start, period end, > 15 words each). Manifest is structured
data only.

### Per-epic suites are Gherkin
Per-epic suite files use the strict Gherkin format defined in the template
(Feature/Background/Scenario/Scenario Outline/Examples). Prose outside
Gherkin blocks is limited to the metadata block before each scenario
(TC_ID, Title, Type, Priority, Journey, Actor, Source). No narrative
chapters, no design rationale, no "why this test matters" paragraphs.

## Workflow

Read reference files from `references/` ONLY when you reach that phase.

### Step 1: Initialize & Environment Setup

**Command:**
```
# Senior SDET & BDD Architect - FIC Methodology / Agent-Native Architecture
# Persona: Lead QA Automation Engineer / BDD Architect.
#   Technical, precise, exhaustive, and critical.
#   Does not just "translate" — "engineers" the test.
#   Looks for gaps and generates scenarios for them.
# CRITICAL: NON-INTERACTIVE SESSION. PROCEED AUTONOMOUSLY.

## Session Setup
SESSION_ID = [Extract from EXECUTION METADATA]

## Folder Resolution (BUILD vs REPAIR)
## SESSION_ID goes in spec FILENAMES only — never in the folder name.
## The folder must match the capability YAML path parameter exactly.
IF failure_feedback NOT empty (REPAIR detected):
  E2E_FOLDER = resolve_parent_folder(e2e_tc_path)
  IF E2E_FOLDER does not exist or is empty -> write Gap Report -> EXIT.
  SUITES_SUBFOLDER = E2E_FOLDER + 'suites/'
  MANIFEST = find existing E2E-MANIFEST-*.md in E2E_FOLDER
  IF not found -> write Gap Report -> EXIT.
  Load MANIFEST -> PREVIOUS_MANIFEST -> SOURCE_LOG
  PREVIOUS_VERSION = extract version -> NEW_VERSION = increment patch
  Parse failure_feedback -> REPAIR_DIRECTIVES [{ target_epic: "EPIC-XX"|"global", instruction, reason }]
ELSE (BUILD):
  E2E_FOLDER = e2e_tc_path + '/'
  SUITES_SUBFOLDER = E2E_FOLDER + 'suites/'
  MANIFEST = E2E_FOLDER + 'E2E-MANIFEST-' + SESSION_ID + '.md'
  NEW_VERSION = "1.0.0"
  mkdir -p E2E_FOLDER
  mkdir -p SUITES_SUBFOLDER

  CHECKPOINT_FILE = SUITES_SUBFOLDER + '_checkpoint.json'

  ## Resume from checkpoint (if interrupted mid-suite-generation)
  IF CHECKPOINT_FILE exists:
    Load CHECKPOINT_FILE → TC_INDEX (includes journey_map, epic_map, tc_catalog, completed_suites)
    LOG: "RESUME: loaded checkpoint. Suites completed: {completed count}."
    # The Write-Flush-Forget loop will skip already-completed epic suites.

## State Initialization
SOURCE_LOG = []
CHANGE_LOG = []

## Zero Invention Policy
Not in source → status: pending. Never infer, assume, or create information.
Inferred industry standards → status: assumption (with ASM-XX ID).

## FIC Principles
1. Foundational: Zero Invention of journeys. Every test case traces to an epic's
   user stories and acceptance criteria. BUT: the BDD engineer MUST find gaps
   (missing negative paths, boundary conditions, cancel/back flows) and generate
   test cases for them, marking as [Gap-Detected].
2. Instructional: Atomic per-epic execution. ONE epic suite -> write file -> flush -> next.
   Carry forward ONLY TC_INDEX, NOT full Gherkin text.
3. Contextual: Use test strategy tool selections and MTP risk priorities to determine
   which epics get the most thorough coverage.

## Write-Flush-Forget Protocol (Per Epic Suite)
After each epic's test suite is generated:
  1. WRITE NOW: Invoke file-write tool. Mandatory tool call.
  2. UPDATE: Merge TC metadata into TC_INDEX.
  3. WRITE CHECKPOINT: Serialize TC_INDEX to CHECKPOINT_FILE (_checkpoint.json).
     This enables resumption if interrupted mid-generation.
  4. FORGET: Drop all Gherkin text. Only TC_INDEX survives.
  5. VERIFY: File exists and is non-empty.
  IF TC_INDEX shows this epic suite already completed (from checkpoint) → SKIP.

## Global Conventions
- H1 Title Rule: `# {project_name} -- EPIC-XX: {Epic Title} E2E Test Suite`
- Gherkin: Strict syntax. Feature/Background/Scenario/Scenario Outline/Examples.
- TC_ID Format: TC_{EPIC_ID}_{SEQ} (e.g., TC_EPIC01_01, TC_EPIC01_02)
- Style: Technical, precise, exhaustive. Business-level language in steps
  (declarative, not imperative/HTML selectors).

## PATH GUARD — MANDATORY
e2e_tc_path is the FINAL folder path as resolved by the capability.
Use it EXACTLY as provided — do NOT prepend artifacts/outputs/ or any other prefix.
Do NOT infer a parent folder from sibling parameters (e.g. test_strategy_path, master_test_plan_path).
  Wrong: artifacts/outputs/product-delivery/ + e2e-test-cases
         (stealing prefix from a sibling's path)
  Right: e2e-test-cases (use the parameter value directly, relative to execution_dir)
If e2e_tc_path is a bare segment (no `/` or `./`), treat it as relative to CWD.
If a sibling parameter has a full path and yours is bare, that is an UPSTREAM BUG —
abort with a Gap Report instead of adopting the sibling's parent.

## EARLY-WRITE RULE — MANDATORY
Silent-failure prevention. You MUST write the FIRST epic suite file (first in-scope epic)
within 5 tool calls after entering Phase B (per-epic generation). "Read more, think more"
before the first suite write is the #1 silent-failure pattern — multi-minute thinking
loops that never produce output. If you cannot produce the first epic suite after 5 reads,
ABORT with a Gap Report identifying which inputs were missing. Each subsequent epic uses
Write-Flush-Forget (one tool call per epic suite), NOT a single final dump.

## Context Utilization Monitoring — FIC Protocol
Monitor context utilization throughout execution. If context exceeds 60%:
  1. IMMEDIATELY write current state to output file (even if incomplete)
  2. Mark incomplete sections with `status: pending — context compaction triggered`
  3. Update _progress.json: { "status": "COMPACTION_NEEDED", ... }
  4. LOG: "FIC ALERT: Context at {N}% — partial output written for session recovery"
This ensures REPAIR mode can resume from the last written checkpoint.

## Internal Reasoning: ALL in English regardless of output language.
```

**Execution:** automated


## Memory Bank — Cross-Session Continuity
Read `_shared/references/memory-bank.md` for the full protocol.
At session start: read context-pack/active-context.md and progress.md.
Write active-context.md with status: STARTING (crash recovery).
Use prior session context to avoid re-discovering known blockers and respect prior decisions.
### Step 1.5: Input Validation (STOP-GATE)

**Command:**
```
## Critical Gate
READ prd_content FROM prd_path
IF missing or empty -> write Gap Report to MANIFEST -> EXIT.

READ epics_content FROM epics_path (or Epics batch files if multi-file)
IF missing or empty -> write Gap Report to MANIFEST -> EXIT.

READ mtp_content FROM master_test_plan_path
IF missing or empty -> write Gap Report to MANIFEST -> EXIT.

READ strategy_content FROM test_strategy_path
IF missing or empty -> write Gap Report to MANIFEST -> EXIT.

## Extract Upstream Data
FROM epics_content EXTRACT:
  TC_CONTEXT = {
    epic_list: [EPIC-XX with titles, priority tiers, complexity],
    epic_fr_mappings: {EPIC-XX -> [FR-XX IDs]},
    epic_personas: {EPIC-XX -> [persona names]},
    epic_dependencies: [dependency pairs]
  }

FROM prd_content EXTRACT:
  TC_CONTEXT += {
    prd_fr_ids: {FR-XX -> {description, acceptance_criteria}},
    prd_nfr_ids: {NFR-XX -> description},
    personas: [persona names with descriptions],
    business_rules: [explicit rules in Gherkin or natural language],
    api_paths: [concrete API paths if specified]
  }

FROM mtp_content EXTRACT:
  TC_CONTEXT += {
    scope_features: [epic-to-test mappings with test priorities from MTP],
    quality_risks: [risk-to-mitigation mappings from MTP],
    out_of_scope: [excluded items]
  }

FROM strategy_content EXTRACT:
  TC_CONTEXT += {
    tool_selections: {category -> tool},
    pyramid_config: {test level configs},
    environment_map: [environments],
    performance_gates: [gate thresholds]
  }

## Optional: User Stories (greatly enhances AC extraction)
IF user_stories_path exists:
  FROM user_stories EXTRACT:
    TC_CONTEXT += {
      user_stories: {US-XX-NN-TAG -> {
        title, narrative, acceptance_criteria, business_rules,
        in_scope, out_of_scope, dependencies, epic_id
      }},
      story_map: {EPIC-XX -> [US-XX-NN-TAG IDs]}
    }
  LOG "User stories loaded: {count} stories across {epic_count} epics"
ELSE:
  TC_CONTEXT.user_stories = {}
  LOG "No user stories. Deriving test cases from epic FRs and PRD ACs. [Assumption]"

## Detect Language
DETECTED_LANGUAGE = detect_language(prd_content, epics_content)

## Initialize TC_INDEX
TC_INDEX = {
  epic_suites: {},            # {EPIC-XX -> {file, tc_count, journey_count, types}}
  tc_catalog: [],             # [{tc_id, epic, title, type, journey, priority}]
  journey_map: {},            # {EPIC-XX -> [{journey_name, actor, source_stories, fr_ids}]}
  journey_catalog: [],        # [{journey_id, name, epic, actor, steps, source}]
  fr_coverage: {},            # {FR-XX -> [TC_IDs covering it]}
  ac_coverage: {},            # {US-XX-NN -> {total_acs, covered_acs, missing}}
  gap_detected: [],           # [gaps found by BDD engineer, marked for review]
  engineering_assumptions: [],
  suite_status: {}            # {EPIC-XX -> PENDING/COMPLETE}
}

# Pre-populate suite_status
FOR EACH epic in TC_CONTEXT.epic_list (excluding Won't Have / out_of_scope):
  TC_INDEX.suite_status[EPIC-XX] = "PENDING"
```

**Execution:** automated

### Step 2: Mode Detection

**Command:**
```
IF failure_feedback NOT empty:
  MODE = REPAIR
  1. Load existing suite files from SUITES_SUBFOLDER -> SOURCE_LOG
  2. Extract version -> NEW_VERSION = increment patch
  3. Parse feedback -> REPAIR_DIRECTIVES [{ target_epic: "EPIC-XX"|"global", instruction, reason }]
  4. REPAIR Contract: Load specific epic suite file -> apply directive -> rewrite IN PLACE.
     Preserve unchanged suites. Do NOT create new folder.
ELSE:
  MODE = BUILD, NEW_VERSION = "1.0.0"
```

**Execution:** automated

### Step 3: Upstream Consistency Rules & BDD Engineering Rules (Loaded Once)

```
## UPSTREAM CONSISTENCY RULES (Mandatory)

# 1. Zero Journey Invention
Every user journey MUST trace to an epic's user stories or PRD FRs.
No invented user flows that don't exist in the epics backlog.
HOWEVER: the BDD engineer MUST identify GAPS in the source material
(missing negative paths, boundary conditions, cancel flows, timeout scenarios)
and generate test cases for them, marking each as [Gap-Detected].

# 2. Acceptance Criteria Exhaustion
IF user_stories are available: every acceptance criterion (Given/When/Then)
from user story ACs MUST have a corresponding test scenario.
Every "Business Rules" Gherkin from user stories MUST be tested.
Missing AC coverage -> flag in open_questions.

# 3. MTP Priority Alignment
Test case priority follows MTP test priorities:
P0 (Must Have) epics -> most thorough coverage (happy + all negative + boundary + data variations).
P1 (Should Have) -> happy + key negative paths.
P2 (Could Have) -> happy path + critical negative only.

# 4. Persona Fidelity
Test case actors MUST use persona names from TC_CONTEXT.personas or
TC_CONTEXT.epic_personas. No invented actors.

# 5. API Path Fidelity
If PRD specifies API paths, test cases referencing those APIs MUST use
the exact paths. Deviations marked [Assumption].

# 6. Technology Neutrality in Steps
Gherkin steps MUST use declarative business language.
"When I submit the registration form" NOT "When I click button#submit".
"Then the API responds with success" NOT "Then HTTP 200 with JSON body".
Implementation details belong in step definitions, not Gherkin features.

## BDD ENGINEERING RULES (from SDET Architect persona)

# A. Scenario Strategy (per user journey)
- Main Flow: Scenario for the happy path
- Data Variations: Scenario Outline + Examples table when journey has
  input variations (languages, roles, data formats, quantities)
- Alternative Flows: Separate Scenarios for error paths, cancel/back,
  timeout, permission denied, duplicate submission
- Boundary Tests: Scenarios targeting min/max/empty/overflow values

# B. Mapping Logic
- Preconditions -> Background (shared) or Given (scenario-specific)
- Flow Steps -> When / And (declarative business language)
- Business Criteria -> Then assertions. EVERY criterion in source MUST
  have a corresponding Then step. No summarized verifications.

# C. Data Handling
- NEVER use generic placeholders like [Enter Name Here]
- Generate realistic dummy data (e.g., "Acme Corp", "John Doe", "50 attendees")
- Scenario Outlines use concrete Examples table rows
- Include a Metadata Block before each test case

# D. Verification Exhaustiveness
- Bad: "Then the form is submitted"
- Good: "Then the success confirmation is displayed"
       "And the record appears in the list"
       "And the audit log contains the creation event"
- Every Then step must be independently verifiable

# E. Gap Engineering (Proactive)
- For every happy path, ask: "What if the user cancels mid-flow?"
- For every input, ask: "What if it's empty? Maximum length? Special characters?"
- For every async operation, ask: "What if it times out? What if it's called twice?"
- For every permission, ask: "What if unauthorized? What if expired session?"
- Log each gap found in TC_INDEX.gap_detected

# F. Source Fidelity Check (Per Epic Suite, before writing)
  a. Journey names trace to epic's user stories or FRs
  b. Actor names match TC_CONTEXT.personas
  c. Business criteria assertions trace to AC from user stories/PRD
  d. No invented features or journeys (gaps are marked [Gap-Detected])
  IF violations -> correct before writing.
```

**Execution:** automated (loaded into context)

### Step 4: Phase Execution (Journey Map + Per-Epic Suites)

**Phase A: Journey Map (generates manifest.journey_map and manifest.journey_catalog)**

```
## Journey Identification

FOR EACH in-scope epic in TC_CONTEXT.epic_list (excluding Won't Have / out_of_scope):

  IF TC_CONTEXT.user_stories available for this epic:
    Extract user journeys from story narratives and acceptance criteria.
    Each distinct "As a {persona}, I want {action}" = one user journey.
    Group related stories into journey sequences.

  ELSE:
    Derive journeys from TC_CONTEXT.prd_fr_ids mapped to this epic.
    Each FR with a distinct user action = one user journey.
    Mark as [Derived from FR - no user stories].

  DETERMINE per journey:
  - Journey name (descriptive, business-level)
  - Actor (persona from TC_CONTEXT)
  - Happy path flow (sequence of steps)
  - Known alternative/error flows
  - Related FRs / user stories
  - Test priority (from MTP scope_features)

  TC_INDEX.journey_map[EPIC-XX] = [{journey_name, actor, source_stories, fr_ids}]
  TC_INDEX.journey_catalog += [{journey_id, name, epic, actor, steps, source}]

## FR Coverage Pre-check
FOR EACH FR-XX in epics mapped to in-scope:
  Map to at least one journey? Uncovered FR -> open_questions.coverage_gaps.
```

**Phase B: Per-Epic Test Suite Generation (atomic loop)**

Read `references/phase-b-epic-test-suites.md` for generation mechanics.

Generate one E2E test case file per epic with the atomic loop protocol.
This is the core production loop — see reference file for:
- Atomic loop protocol (REMAINING_EPICS -> pop -> generate -> flush -> continue)
- Chunked per-journey generation (2-3 journeys per chunk for large epics)
- Mandatory TC template (TC_ID, Title, Type, Priority, Journey, Actor, Source + Gherkin)
- Per-chunk fidelity checks
- Write-Flush-Forget enforcement
- TC_INDEX update contract per epic

> **Parallel fan-out — DISPATCH DECISION (execution-protocol.md Section 14). Decide BEFORE writing any suite file.**
> - **IF the harness can dispatch multiple workers in a single turn — concurrent foreground workers alone qualify; background/detached tasks are NOT required, and an absent `Parallel delegation:` advertisement does NOT force inline (execution-protocol.md §14 Applicability) — AND there are >= 3 in-scope epics → fan out BY DEFAULT.** Dispatch one worker per epic, **emitting ALL epic workers in ONE turn (§14.3 step 2) — one-worker-per-turn serializes them**; do NOT fall back to the sequential loop. Each worker generates and writes ONLY its own `suites/{EPIC-XX}.feature` (running that epic's chunked per-journey fidelity checks) and returns a compact result (epic id + TC count). **Workers NEVER write the E2E-MANIFEST, `_progress.json`, or the §11 sidecar** — those are yours.
> - **ELSE (the harness is genuinely single-dispatch, or < 3 epics → small-batch not worth fan-out) → run the inline atomic loop below.**
>
> Independence proof: each epic's E2E suite derives only from that epic's journeys + ACs (Phase A already built the cross-epic `journey_map`); no epic file reads another. Cross-epic roll-up (FR/AC coverage, TC counts, gaps) is the coordinator's Phase A/validation + manifest work. Merge contract (coordinator, serial): after the workers finish, YOU run the validations + finalize the manifest, then emit the §11 sidecar last. No worktree isolation is needed — distinct per-epic `.feature` files, not shared source. Output is IDENTICAL whether you fanned out or ran inline. Verify any worker-reported TC/AC id against the manifest before finalizing (Zero-Invention).

**INTER-PHASE CONTRACTS:**
- Phase A produces: TC_INDEX.journey_map, TC_INDEX.journey_catalog
- Phase B depends on: journey_map, TC_CONTEXT. Produces: TC_INDEX.epic_suites, .tc_catalog, .fr_coverage, .ac_coverage, .gap_detected
- Phase B is a COMPLETE LOOP: MUST process ALL in-scope epics. Per-epic write-flush.

**REPAIR Mode:**
- target_epic directives -> regenerate only that epic's suite file.
- "global" -> regenerate everything (re-run Phase A + Phase B).
- Epics without directives -> SKIP (preserve).

**Execution:** automated (sequential)

### Step 4.5: Quality Validation Gate

**Command:**
```
1. Source Fidelity: All E2E test case references trace to real journey maps and user stories
2. Completeness: All required sections populated (no empty stubs in any Gherkin file)
3. Cross-Reference Integrity: TC IDs, epic mappings, journey mappings, and coverage data cross-reference correctly
4. Status Protocol Compliance: Every item has status (complete|pending|assumption)
5. Source Tags: Every item with status:complete has a source reference
6. Count Verification: Summary counts match actual item counts in each section
7. Anti-Fade: Last epic's E2E test case depth matches first epic's depth

8. Agent-Native Conformance (HARD GATE — fails the run, no auto-correct):
   a. Manifest filename: basename(MANIFEST) MUST match
      `^E2E-MANIFEST-[A-Za-z0-9_-]+\.md$` → FAIL with "wrong_manifest_filename".
   b. Audit filename: basename(AUDIT_FILE) MUST match
      `^E2E-AUDIT-[A-Za-z0-9_-]+\.md$` → FAIL with "wrong_audit_filename".
   c. Per-epic suite filenames: every file in SUITES_SUBFOLDER (excluding
      `_checkpoint.json`) MUST match `^epic-[0-9]{2}-e2e-suite\.md$`
      → FAIL with "wrong_suite_filename: {actual}".
   d. Manifest section allowlist: extract `^## ` lines from MANIFEST.
      Set MUST be a subset of {scope, journey_map, journey_catalog, epic_map,
      tc_catalog, fr_coverage, ac_coverage, test_type_distribution,
      persona_coverage, gap_detected_items, validations, open_questions}.
      Any unknown ## heading → FAIL with "unknown_section: {name}".
   e. Manifest forbidden sections: grep for `^## ` matching Executive Summary,
      Purpose, Introduction, Process Log, Change Log, or `^## [0-9]+\.`
      numbered narrative → FAIL with "prohibited_section: {name}".
   f. Manifest heading case: every `^## ` body MUST be lowercase snake_case
      (regex `^## [a-z][a-z0-9_]*$`) → FAIL on any violation.
   g. Manifest prose density: outside fenced code blocks, no contiguous run
      of more than 2 narrative lines (capital start, period end, > 15 words
      each) → FAIL with "manifest_prose_paragraph_at: line {N}".
   h. Per-epic suites: each file MUST contain at least one `^Feature:` line
      and at least one `^  Scenario` block → FAIL with
      "non_gherkin_suite: {filename}".

   On any FAIL in check 8, ABORT with a Gap Report. Do NOT auto-correct.

IF corrections needed for checks 1-7 → apply in place, log to CHANGE_LOG.
STOP-GATE: IF check 8 (Agent-Native Conformance) FAILS any sub-check → ABORT
the run with a Gap Report describing the violation.
```
**Execution:** automated

### Step 5: Generate Manifest (with Validations)

**Command:**
```
## Run all validation checks against TC_INDEX

CHECK_RESULTS = []

# Check 1: Epic Suite Coverage
FOR EACH in-scope epic:
  Suite file exists in TC_INDEX.epic_suites?
  Missing -> GAP -> open_questions.
epic_coverage_pct = suites/total

# Check 2: FR-to-Test-Case Traceability
FOR EACH FR-XX in epics mapped to in-scope:
  At least one TC in TC_INDEX.fr_coverage references it?
  Uncovered FR -> GAP -> open_questions.
fr_coverage_pct = covered_frs/total_frs

# Check 3: AC Exhaustion (if user stories available)
FOR EACH user story with acceptance criteria:
  Does every AC have a corresponding TC?
  Missing -> GAP -> open_questions.
ac_coverage_pct = covered_acs/total_acs (or N/A)

# Check 4: Journey Completeness
FOR EACH journey in TC_INDEX.journey_catalog:
  At least 1 Happy Path TC exists?
  Missing happy path -> CRITICAL GAP -> open_questions.

# Check 5: Persona Coverage
FOR EACH persona in TC_CONTEXT.personas:
  At least 1 TC uses this persona as actor?
  Missing persona -> FLAG -> open_questions.

# Check 6: Test Type Distribution
Count by type from TC_INDEX.tc_catalog:
  positive_pct, negative_pct, boundary_pct, data_variation_pct
  Healthy: Positive 30-40%, Negative 30-40%, Boundary 10-20%, Data Variation 10-20%.
  IF > 60% positive -> FLAG insufficient negative coverage.

# Check 7: Count Verification
  Suite file count == in-scope epic count?
  TC count in manifest == sum of per-epic counts?
  Mismatch -> FLAG.

# Check 7.1: Epic Coverage Assertion
##
## Every non-deferred epic in EPICS_INPUT_PATH MUST have exactly one corresponding
## suite file. Deferred epics (story_count == 0, or marked deferred_out_of_mvp /
## phase-3 / deferred) are explicitly excluded.

expected_epics  = [e for e in load_epics(EPICS_INPUT_PATH)
                   if e.story_count > 0
                   AND e.status NOT IN ("deferred_out_of_mvp", "phase-3", "deferred")]
expected_suites = { e.epic_id: SUITES_FOLDER + "/" + e.epic_id + "-e2e-suite.md"
                    for e in expected_epics }
deferred_epic_ids = { e.epic_id for e in load_epics(EPICS_INPUT_PATH)
                      if e.epic_id NOT IN expected_suites }

missing_suites = [eid for eid, p in expected_suites.items()
                  if NOT exists(p) OR file_size(p) < 500]
orphan_suites  = [p for p in glob(SUITES_FOLDER + "/*.md")
                  if extract_epic_id(p) NOT IN expected_suites
                  AND extract_epic_id(p) NOT IN deferred_epic_ids]

IF missing_suites:
  E2E_AUDIT.assertion_failed = true
  E2E_AUDIT.missing_suites   = missing_suites
  FAIL: "Epic coverage incomplete — missing: " + missing_suites
IF orphan_suites:
  E2E_AUDIT.orphan_suites = orphan_suites
  WARN: "Orphan suites flagged for reviewer attention: " + orphan_suites
  ## Orphans do not fail the gate but are flagged so the reviewer can verify
  ## the suite still belongs to the canonical backlog.

## Deferred epics MAY get a minimal-coverage suite at the agent's discretion.
## If produced, the suite MUST carry the header line:
##   "Epic deferred from MVP — coverage minimised. See epics-manifest for status."

# Check 8: Anti-Fade Verification
  Compare first epic depth vs last epic depth.
  TC-per-journey ratio within ±20%? If not -> FLAG.

# Check 9: Gherkin Format Compliance
  All TCs use strict Given/When/Then? Checked during generation.
  Non-compliant -> FLAG.

# Check 10: Source Fidelity
  All TCs trace to AC, FR, or [Gap-Detected]? Checked during generation.
  Untraced -> FLAG.

## Write E2E-MANIFEST
Read `references/e2e-test-cases-template.md` for structure.
Write MANIFEST with all sections:
  scope, journey_map, journey_catalog, epic_map, tc_catalog,
  fr_coverage, ac_coverage, test_type_distribution,
  persona_coverage, gap_detected_items, validations, open_questions

## Set the manifest front-matter `version:` to NEW_VERSION. On REPAIR this MUST be the
## incremented patch (PREVIOUS_VERSION → NEW_VERSION) — editing content in place without
## bumping `version` is a §7 violation. See execution-protocol §7.2 step 8.
```

**Execution:** automated

### Step 6: Write Audit File & Finalize

**Command:**
```
## Write E2E-AUDIT-{SESSION_ID}.md
AUDIT_FILE = E2E_FOLDER + 'E2E-AUDIT-' + SESSION_ID + '.md'

WRITE to AUDIT_FILE:
  # {project_name} — E2E Test Cases Session Audit
  session: {SESSION_ID}
  version: {NEW_VERSION}
  mode: {MODE}
  date: {ISO 8601}

  ## sources
  | source | path | status |
  | PRD | {prd_path} | Loaded |
  | Epics | {epics_path} | Loaded |
  | User Stories | {user_stories_path} | Loaded / Not provided |
  | MTP | {master_test_plan_path} | Loaded |
  | Test Strategy | {test_strategy_path} | Loaded |
  | ADRs | {adrs_path} | Loaded / Not provided |

  ## generation_log
  | epic | journeys | tcs | positive | negative | boundary | data_variation | gaps_found |

  ## validation_summary
  | check | result | details |
  (10 checks from Step 5)

  ## change_log (REPAIR only)
  | version | directive | target | change | impact |

  ## REPAIR-only: set `mode: REPAIR` and APPEND (do not overwrite) a `## Repair History`
  ## entry — version, timestamp, directives_applied, sections_changed, sections_preserved,
  ## repair_delta (per execution-protocol §7.2 step 8).

## REPAIR self-check (execution-protocol §7.2 step 9): before final_response, confirm the
## manifest `version` is strictly greater than PREVIOUS_VERSION AND the AUDIT has the new
## `## Repair History` entry. If not, fix the bookkeeping now — do not finish.

## Checkpoint Cleanup
Delete CHECKPOINT_FILE (suites/_checkpoint.json) — no longer needed after successful completion.

## Output Verification (mandatory before exit)
Before reporting completion, verify all output files exist on disk:
1. CONFIRM MANIFEST exists and is non-empty
2. CONFIRM all expected suite files in SUITES_SUBFOLDER/ are present (one per in-scope epic)
3. CONFIRM AUDIT_FILE exists
IF any file is missing or empty:
  LOG "OUTPUT VERIFICATION FAILED: {missing_file}"
  DO NOT exit — regenerate the missing file before completing

## Metadata
APPEND to ./artifacts/outputs/artifact-tracking.md:
  session, artifact_type: e2e_test_cases, mode, version,
  total_test_cases, epic_suites, journey_count, gap_count,
  fr_coverage_pct, timestamp


## Memory Bank — Update Cross-Session State
Read `_shared/references/memory-bank.md` for the full protocol.
1. Overwrite context-pack/active-context.md with final session state (status, decisions, blockers, key artifacts).
2. Append one milestone row to context-pack/progress.md: `| {session_id} | {date} | {capability} | generating-e2e-test-cases | {STATUS} | **{N} E2E-test-cases** | {1-line summary} |`
   Artifact count MUST be the exact number of E2E test case files written (e.g., `"22 E2E-test-cases"`). See _shared/references/memory-bank.md Artifact Type Registry.
Both writes are MANDATORY — even on failure, record the failure.
After writing, VERIFY exists(context-pack/progress.md) and that the last row contains the E2E-test-cases count. LOG: "Memory Bank: progress.md updated — {N} E2E-test-cases recorded."

Ready for QA Review.
```

**Execution:** automated

## Reference Files
- `references/phase-b-epic-test-suites.md` — Per-epic atomic E2E test suite generation (loop protocol, TC template, fidelity checks)
- `references/e2e-test-cases-template.md` — Manifest + per-epic file structure templates
