---
name: generating-test-cases
description: >
  Generates detailed functional verification test cases from user stories, acceptance
  criteria, and business rules using FIC methodology. Produces a manifest file
  (epic_map + tc_catalog + coverage data + validations + open_questions) plus
  one Gherkin test case file per epic under a suites/ subfolder. Each test case uses
  strict Gherkin format derived from user story ACs: every AC bullet becomes a Then
  assertion, every business rule becomes a Scenario. Generates positive (happy path),
  negative (error/constraint), and boundary test cases per story. Cross-references
  test strategy for tool compatibility and MTP for risk-based depth. Applies chunked
  per-story generation within each epic file to prevent timeout. Uses FTC_INDEX as
  carry-forward contract. BUILD and surgical REPAIR modes. Can target a single epic
  or all epics. Human-readable output via `humanize-spec` rendering profile on demand.
license: Proprietary
metadata:
  author: aipods-team
  version: 3.0.0
  category: quality-engineering
  tags: quality-engineering-planning, automated, agent-native
---

# Generating Functional Test Cases — Agent-Native Spec

## Quick Start
Generate functional test cases from user stories and acceptance criteria.
Output is a **manifest + per-epic Gherkin suites**:

```
{ftc_folder}/
├── FTC-MANIFEST-{SESSION_ID}.md      ← Epic map, coverage data, validations, open_questions
├── suites/                            ← One Gherkin file per epic (UNCHANGED format)
│   ├── epic-01-func-tests.md
│   ├── epic-02-func-tests.md
│   └── ...
└── FTC-AUDIT-{SESSION_ID}.md         ← Session metadata
```

## Known Failure Modes
<!-- ACCUMULATING — appended by calibrating-updates (WS6). Newest first. Rules MUST be generic/behavioral (project-agnostic); project-specific fixes go to context packs, never here. Format + entry rules: engineering-skills/references/known-failure-modes-format.md. Read these at pre-flight so a lesson learned once recurs no more. -->

## Anti-Patterns (do NOT)
<!-- ACCUMULATING — appended by calibrating-updates (WS6). One line each: **AP-NNN** (ISO-date, source: REC-NNN): prohibition — why. -->

## Why This Architecture

The QA automation agent processes ONE epic's test suite at a time.
It does not need all test cases in context to automate one epic.

**Manifest (always loaded):** Epic map with TC counts, coverage summaries,
validation results, open questions. ~120 lines for a 10-epic project.
Cheap to keep in context.

**Per-epic suite files (loaded on demand):** Full Gherkin test cases.
Already agent-native — strict Given/When/Then with TC_ID, tags, traceability.
80-120 scenarios per MVP epic. The QA automation agent loads one, works through it,
drops it, loads the next.

**Per-epic files are UNCHANGED from v2.0.1.** They were already structured
executable specs. The refactoring targets only the coordination layer
(index + audit + governance → single manifest).

**Human-readable output:** Not produced by this skill. Use `humanize-spec` skill
with `profiles/func-test-cases.md` rendering profile to generate formatted index,
traceability audit, and governance documents on demand.

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_name | string | Yes | Project identifier |
| user_stories_path | string | Yes | Path to user stories (folder or file for target epic) |
| test_strategy_path | string | No | Path to test strategy document. When missing or empty, use Gherkin format with standard positive/negative/boundary distribution. |
| master_test_plan_path | string | No | Path to master test plan. When missing or empty, treat all epics as MVP priority and apply uniform test depth. |
| test_cases_path | string | No | Output path for functional test cases. Falls back to default if not provided. |
| prd_path | string | No | Path to the document containing PRD of the project. Optional — PRD business rules cross-reference is skipped if absent. |
| epics_path | string | No | Path to story mapping documentation. Optional — epic context derived from user stories if absent. |
| adrs_path | string | No | Path to ADR collection (output from adr-generation) |
| failure_feedback | string | No | Feedback for REPAIR mode |

**If any Required parameter is not defined, ABORT EXECUTION.**

## Workflow

Read reference files from `references/` ONLY when you reach that phase.

### Step 1: Initialize & Environment Setup

**Command:**
```
# QA Automation Lead - FIC Methodology / Agent-Native Architecture
# Persona: QA Automation Lead with strict adherence to project testing standards
#   and risk priorities. Technical, precise, exhaustive.
# CRITICAL: NON-INTERACTIVE SESSION. PROCEED AUTONOMOUSLY.

## Folder Resolution (BUILD vs REPAIR)
IF failure_feedback NOT empty (REPAIR detected):
  FTC_FOLDER = resolve_parent_folder(test_cases_path)
  IF FTC_FOLDER does not exist or is empty -> write Gap Report -> EXIT.
  SUITES_SUBFOLDER = FTC_FOLDER + 'suites/'
  MANIFEST = find existing FTC-MANIFEST-*.md in FTC_FOLDER
  IF not found -> write Gap Report -> EXIT.
  Load MANIFEST -> PREVIOUS_MANIFEST -> SOURCE_LOG
  PREVIOUS_VERSION = extract version -> NEW_VERSION = increment patch
  Parse failure_feedback -> REPAIR_DIRECTIVES [{ target_epic: "EPIC-XX"|"global", instruction, reason }]
ELSE (BUILD):
  FTC_FOLDER = test_cases_path.replace('.md', '') + '/'
  ## SESSION_ID goes in spec FILENAMES only — never in the folder name.
  ## The folder must match the capability YAML path parameter exactly.
  SUITES_SUBFOLDER = FTC_FOLDER + 'suites/'
  MANIFEST = FTC_FOLDER + 'FTC-MANIFEST-' + SESSION_ID + '.md'
  NEW_VERSION = "1.0.0"
  mkdir -p FTC_FOLDER
  mkdir -p SUITES_SUBFOLDER

## PATH NORMALIZATION RULE (MANDATORY)
All output paths recorded as skill output parameters MUST be relative to execution_dir.
Before emitting test_cases_path output:
  IF os.path.isabs(FTC_FOLDER):
    FTC_FOLDER_RECORDED = os.path.relpath(FTC_FOLDER, execution_dir)
  ELSE:
    FTC_FOLDER_RECORDED = FTC_FOLDER
Emit FTC_FOLDER_RECORDED (relative) as the test_cases_path output parameter.

  CHECKPOINT_FILE = SUITES_SUBFOLDER + '_checkpoint.json'

  **FIRST ACTION — MANDATORY:** Write `_progress.json` to the output folder before any other file write.
  This prevents the orchestrator from sending SIGINT. See execution-protocol.md Section 2 for the schema.

  ## Resume from checkpoint (if interrupted mid-suite-generation)
  IF CHECKPOINT_FILE exists:
    Load CHECKPOINT_FILE → FTC_INDEX (includes epic_map, tc_catalog, completed_suites)
    LOG: "RESUME: loaded checkpoint. Suites completed: {completed count}."
    # The Write-Flush-Forget loop will skip already-completed epic suites.

## State Initialization
SOURCE_LOG = []
CHANGE_LOG = []

## Zero Invention Policy
Not in source → status: pending. Never infer, assume, or create information.
Inferred industry standards → status: assumption (with ASM-XX ID).

## FIC Principles
1. Foundational: Zero Invention. Every test case traces to a user story AC or
   business rule. No invented scenarios. Positive, negative, and boundary TCs
   all derive from source acceptance criteria.
2. Instructional: Atomic per-epic execution. ONE epic's stories -> write file -> flush -> next.
   Within each epic, generate in chunks of 2-3 stories to prevent overflow.
3. Contextual: Carry forward ONLY FTC_INDEX, NOT full test case text.
4. Input Isolation: Load ONLY the user_stories_path for the current session.
   DO NOT load or reference prior test case output files from the output_folder.
   Prevents cumulative context growth across sessions.

## Write-Flush-Forget Protocol
After each epic's test cases:
  1. WRITE NOW: File-write tool. Mandatory tool call.
  2. UPDATE: Merge into FTC_INDEX.
  3. WRITE CHECKPOINT: Serialize FTC_INDEX to CHECKPOINT_FILE (_checkpoint.json).
     This enables resumption if interrupted mid-generation.
  4. UPDATE PROGRESS: Overwrite `_progress.json` with current intermediate state:
     ```json
     {
       "skill": "generating-test-cases",
       "session_id": "<SESSION_ID>",
       "status": "IN_PROGRESS",
       "epics_completed": <count of COMPLETE suites in FTC_INDEX.suite_status>,
       "epics_total": <count of all epics in scope>,
       "current_epic": "<EPIC-XX just completed>",
       "test_cases_generated_so_far": <sum of tc_catalog entries completed>
     }
     ```
  5. FORGET: Drop test case text. Only FTC_INDEX survives.
  6. VERIFY: File exists and is non-empty.
  IF FTC_INDEX shows this epic suite already completed (from checkpoint) → SKIP.

## Global Conventions
- H1 Title: `# {project_name} -- EPIC-XX: {Title} Functional Tests`
- TC_ID Format: FTC_{EPIC_NUM}_{STORY_NUM}_{SEQ} (e.g., FTC_01_03_01)
- Gherkin: Strict Given/When/Then. Format per test strategy guidelines.
- BE/FE Slicing: Test cases tagged with [BE] or [FE] matching story domain tags.
- Technology Neutrality: Use capability language in Gherkin steps.
  Reference specific tools only when describing framework-specific setup.

## OUTPUT FOLDER CONVENTION (MANDATORY)
`test_cases_path` IS the final output folder, resolved by the capability (it is
already feature-scoped when the capability sets `feature_id`). Write suites and the
manifest DIRECTLY into it — see the PATH GUARD below.
- Do NOT compute or append a `{project_name}-test-cases-{feature_id}/` subfolder,
  a date stamp, or any other suffix. The capability owns folder scoping.
- When `feature_id` is provided, use it ONLY inside spec/manifest FILENAMES
  (the SESSION_ID component) — never to build a folder name.

## Target Epic Scoping
IF target_epic is provided:
  SCOPE = [target_epic only]
  LOG "Scoped to {target_epic}"
ELSE:
  SCOPE = [all in-scope epics]
  LOG "Generating for all epics"

## PATH GUARD — MANDATORY
test_cases_path is the FINAL folder path as resolved by the capability.
Use it EXACTLY as provided — do NOT prepend artifacts/outputs/ or any other prefix.
Do NOT infer a parent folder from sibling parameters (e.g. test_strategy_path, master_test_plan_path).
  Wrong: artifacts/outputs/product-delivery/ + test-cases
         (stealing prefix from a sibling's path)
  Right: test-cases (use the parameter value directly, relative to execution_dir)
If test_cases_path is a bare segment (no `/` or `./`), treat it as relative to CWD.
If a sibling parameter has a full path and yours is bare, that is an UPSTREAM BUG —
abort with a Gap Report instead of adopting the sibling's parent.

## EARLY-WRITE RULE — MANDATORY
Silent-failure prevention. You MUST write the FIRST epic suite file (first in-scope epic)
within 5 tool calls after entering the per-epic generation loop. "Read more, think more"
before the first suite write is the #1 silent-failure pattern — multi-minute thinking
loops that never produce output. If you cannot produce the first epic suite after 5 reads,
ABORT with a Gap Report identifying which inputs were missing. Each subsequent epic uses
Write-Flush-Forget (one tool call per epic suite), NOT a single final dump.

## Internal Reasoning: ALL in English regardless of output language.
```

**Execution:** automated


### Step 1.5: Input Validation (STOP-GATE)

**Command:**
```
## Critical Gate
READ user_stories FROM user_stories_path (folder or specific file)
IF missing or empty -> write Gap Report to MANIFEST -> EXIT.

READ strategy FROM test_strategy_path
IF missing or empty -> SET strategy_available = false; USE defaults:
  tool_selections = {}, output_format = "Gherkin", automation_framework = {}
ELSE -> SET strategy_available = true

READ mtp FROM master_test_plan_path
IF missing or empty -> SET mtp_available = false; USE defaults:
  scope_features = [all epics from user_stories], quality_risks = [], mvp_epics = [all EPIC-XX IDs]
ELSE -> SET mtp_available = true

## Extract from User Stories
FROM user_stories EXTRACT:
  FTC_CONTEXT = {
    stories_by_epic: {EPIC-XX -> [{
      story_id: "US-XX-NN-TAG",
      title: "...",
      tag: "BE/FE/DATA/...",
      narrative: "As a..., I want..., So that...",
      acceptance_criteria: [{ ac_num, given, when, then }],
      business_rules: [{ rule_id, gherkin_or_text }],
      in_scope: [...],
      out_of_scope: [...],
      dependencies: [...],
      assumptions: [...]
    }]},
    story_ids_all: [all US-XX-NN-TAG IDs]
  }

## Extract from Strategy (if available)
IF strategy_available:
  FROM strategy EXTRACT:
    FTC_CONTEXT += {
      tool_selections: {category -> tool},
      output_format: "Gherkin" (or as defined in strategy),
      automation_framework: {description from strategy}
    }
ELSE:
  FTC_CONTEXT += {
    tool_selections: {},
    output_format: "Gherkin",
    automation_framework: {}
  }

## Extract from MTP (if available)
IF mtp_available:
  FROM mtp EXTRACT:
    FTC_CONTEXT += {
      scope_features: [epic-to-test mappings with priorities],
      quality_risks: [risk mappings],
      mvp_epics: [Must Have EPIC-XX IDs -> get extra negative scenarios]
    }
ELSE:
  FTC_CONTEXT += {
    scope_features: [all epics from user_stories with equal priority],
    quality_risks: [],
    mvp_epics: [all EPIC-XX IDs from user_stories]
  }

## Optional: Epics for additional context
IF epics_path exists and is not empty:
  FROM epics EXTRACT:
    FTC_CONTEXT += {
      epic_titles: {EPIC-XX -> title},
      epic_priorities: {EPIC-XX -> priority_tier}
    }
ELSE:
  LOG "epics_path not provided — epic titles and priorities derived from user stories only."
  FTC_CONTEXT += {
    epic_titles: {},
    epic_priorities: {}
  }

## Optional: PRD for business rules cross-reference
IF prd_path exists and is not empty:
  FROM prd EXTRACT:
    FTC_CONTEXT += {
      prd_business_rules: [explicit rules],
      prd_fr_ids: {FR-XX -> {description, acceptance_criteria}}
    }
ELSE:
  LOG "prd_path not provided — PRD business rules cross-reference skipped."
  FTC_CONTEXT += {
    prd_business_rules: [],
    prd_fr_ids: {}
  }

## Apply Scope Filter
IF target_epic provided:
  SCOPED_EPICS = [target_epic]
  IF target_epic not in FTC_CONTEXT.stories_by_epic -> write Gap Report -> EXIT.
ELSE:
  SCOPED_EPICS = [all EPIC-XX keys in FTC_CONTEXT.stories_by_epic]

## Initialize FTC_INDEX
FTC_INDEX = {
  scoped_epics: SCOPED_EPICS,
  epic_suites: {},            # {EPIC-XX -> {file, tc_count, story_count, types}}
  tc_catalog: [],             # [{tc_id, story_id, title, type, tag}]
  ac_coverage: {},            # {US-XX-NN -> {total_acs, covered_acs, tc_ids}}
  business_rule_coverage: {}, # {rule_id -> [tc_ids]}
  gap_detected: [],
  suite_status: {}            # {EPIC-XX -> PENDING/COMPLETE}
}

FOR EACH epic in SCOPED_EPICS:
  FTC_INDEX.suite_status[EPIC-XX] = "PENDING"
```

**Execution:** automated

### Step 2: Mode Detection

**Command:**
```
IF failure_feedback NOT empty:
  MODE = REPAIR
  1. Load existing suite files -> SOURCE_LOG
  2. Extract version -> NEW_VERSION = increment MINOR
  3. Parse feedback -> REPAIR_DIRECTIVES [{ target_epic: "EPIC-XX"|"global", instruction, reason }]
  4. REPAIR Contract: rewrite targeted suite files IN PLACE. Preserve others.
ELSE:
  MODE = BUILD, NEW_VERSION = "1.0.0"
```

**Execution:** automated

### Step 3: Upstream Consistency Rules (Loaded Once)

```
## UPSTREAM CONSISTENCY RULES (Mandatory)

# 1. AC Exhaustion
Every acceptance criterion in every user story MUST produce at least one test case.
Every Given/When/Then from story ACs -> a corresponding Gherkin scenario.
Every business rule -> a corresponding scenario.
Missing AC -> flag in open_questions.

# 2. Risk-Based Depth
MVP epics (Must Have in MTP) get EXTRA negative scenarios:
- Every input field: empty, max length, special characters, SQL injection pattern
- Every state transition: invalid state, concurrent modification
- Every dependency: timeout, unavailable, malformed response
Non-MVP epics: positive + key negative only.

# 3. Story Domain Tag Fidelity
Test cases MUST be tagged matching the user story's domain tag:
US-XX-NN-BE story -> [BE] test cases (API, service, data)
US-XX-NN-FE story -> [FE] test cases (UI, visual, accessibility)
No hybrid test cases spanning BE+FE for a single story.

# 4. Technology Neutrality in Gherkin
Steps use declarative business language.
"When the user submits the form" NOT "When Playwright clicks #submit".
Framework-specific details belong in step definitions, not features.

# 5. Format Compliance
Output format MUST match test strategy guidelines.
If strategy says Gherkin -> strict Gherkin.
If strategy defines specific tagging conventions -> follow them.

# 6. Source Fidelity Check (Per Story, before writing)
  a. Every scenario traces to an AC number or business rule
  b. Actor matches story narrative persona
  c. No invented features or business logic
  d. Boundary values derive from explicit constraints or [Assumption]
  IF violations -> correct before writing.
```

**Execution:** automated (loaded into context)

### Step 4: Per-Epic Test Suite Generation (Atomic Loop)

Read `references/phase-a-epic-func-suites.md` for generation mechanics.

Generate one test case file per epic with chunked per-story generation.
This is the core production loop — see reference file for:
- Atomic loop protocol (REMAINING_EPICS → pop → generate → flush → continue)
- Chunked per-story generation (2-3 stories per chunk within each epic)
- Mandatory TC template (TC_ID, Story, AC/Rule, Type, Tag, Priority + Gherkin)
- Per-chunk fidelity checks
- Write-Flush-Forget enforcement
- FTC_INDEX update contract per epic

> **Parallel fan-out — DISPATCH DECISION (execution-protocol.md Section 14). Decide BEFORE writing any suite file.**
> - **IF the harness can dispatch multiple workers in a single turn AND there are >= 3 in-scope epics → fan out BY DEFAULT.** Concurrent foreground workers alone qualify — background/detached tasks are NOT required, and an absent `Parallel delegation:` advertisement does NOT force inline (execution-protocol.md §14 Applicability); fall back only when the harness is genuinely single-dispatch. **Dispatch all epic workers in ONE turn (§14.3 step 2) — one-worker-per-turn serializes them.** One worker per epic; do NOT fall back to the sequential loop. Each worker generates and writes ONLY its own `suites/{EPIC-XX}.feature` (running that epic's chunked per-story fidelity checks) and returns a compact result (epic id + TC count). **Workers NEVER write the FTC-MANIFEST, `_progress.json`, or the §11 sidecar** — those are yours.
> - **ELSE (harness is genuinely single-dispatch, or < 3 epics) → run the inline atomic loop below.** The < 3 epics case stays inline because the batch is too small to be worth fanning out.
>
> Independence proof: each epic's suite derives only from that epic's stories + ACs + business rules; no epic file reads another. Cross-epic roll-up (FR/AC coverage, TC counts, open_questions) is Step 4.5 + Step 5 coordinator work, not a worker's. Merge contract (coordinator, serial): after the workers finish, YOU run Step 4.5 validations + Step 5 manifest, then emit the §11 sidecar last. No worktree isolation is needed — each worker writes a distinct `.feature` file, not shared source. The suites, manifest, and coverage are IDENTICAL whether you fanned out or ran inline. Verify any worker-reported TC/AC id against the manifest before Step 5 (Zero-Invention).

**INTER-STEP CONTRACT:**
- This step produces: FTC_INDEX.epic_suites, .tc_catalog, .ac_coverage, .business_rule_coverage
- This step is a COMPLETE LOOP for all SCOPED_EPICS. Per-epic write-flush.
  Within each epic: chunked per-story (2-3 stories at a time) → append → flush chunk.
- Step 5 depends on: FTC_INDEX (complete after all epics processed)

**Execution:** automated

### Step 4.5: Quality Validation Gate

**Command:**
```
1. Source Fidelity: All test case references trace to real user stories and acceptance criteria
2. Completeness: All required sections populated (no empty stubs in any Gherkin file)
3. Cross-Reference Integrity: TC IDs, epic mappings, and coverage data cross-reference correctly
4. Status Protocol Compliance: Every item has status (complete|pending|assumption)
5. Source Tags: Every item with status:complete has a source reference
6. Count Verification: Summary counts match actual item counts in each section
7. Anti-Fade: Last epic's test case depth matches first epic's depth

IF corrections needed → apply in place, log to CHANGE_LOG
```
**Execution:** automated

### Step 5: Generate Manifest (with Validations)

**Command:**
```
## Run all validation checks against FTC_INDEX

CHECK_RESULTS = []

# Check 1: Story Coverage
FOR EACH story in scoped epics:
  At least one TC exists in FTC_INDEX.tc_catalog for this story?
  Missing -> GAP -> open_questions.
story_coverage_pct = covered/total

# Check 2: AC Exhaustion
FOR EACH story in FTC_INDEX.ac_coverage:
  IF covered_acs < total_acs -> list missing AC numbers -> open_questions.
ac_coverage_pct = covered_acs/total_acs

# Check 3: Business Rule Coverage
FOR EACH rule in FTC_INDEX.business_rule_coverage:
  Uncovered rule -> CRITICAL GAP -> open_questions.
br_coverage_pct = covered_rules/total_rules

# Check 4: Test Type Distribution
Count by type from FTC_INDEX.tc_catalog:
  positive_pct, negative_pct, boundary_pct
  Healthy: Positive 40-50%, Negative 35-45%, Boundary 10-20%.
  IF > 70% positive -> FLAG insufficient negative coverage.

# Check 5: MVP Depth Verification
FOR EACH MVP epic in FTC_CONTEXT.mvp_epics (in scope):
  Does it have extra negative scenarios (dependency failures, injection, concurrency)?
  MVP without extra depth -> FLAG.

# Check 6: Domain Tag Consistency
FOR EACH TC in FTC_INDEX.tc_catalog:
  TC tag matches source story tag?
  Mismatch -> FLAG -> open_questions.

# Check 7: Count Verification
  Suite file count == scoped epic count?
  TC count in manifest == sum of per-epic counts?
  Mismatch -> FLAG.

# Check 8: Anti-Fade Verification
  Compare first epic depth vs last epic depth.
  TC-per-story ratio within ±20%? If not -> FLAG.

# Check 9: Gherkin Format Compliance
  All TCs use strict Given/When/Then? Checked during generation.
  Non-compliant -> FLAG.

# Check 10: Source Fidelity
  All TCs trace to AC or business rule? Checked during generation.
  Untraced -> FLAG.

## Write FTC-MANIFEST
Read `references/func-test-cases-template.md` for structure.
Write MANIFEST with all sections:
  scope, epic_map, tc_catalog, ac_coverage, business_rule_coverage,
  test_type_distribution, mvp_depth_verification, domain_tag_consistency,
  validations, open_questions

## Set the manifest front-matter `version:` to NEW_VERSION. On REPAIR this MUST be the
## incremented patch (PREVIOUS_VERSION → NEW_VERSION) — editing content in place without
## bumping `version` is a §7 violation. See execution-protocol §7.2 step 8.
```

**Execution:** automated

### Step 6: Write Audit File & Finalize

**Command:**
```
## Write FTC-AUDIT-{SESSION_ID}.md
AUDIT_FILE = FTC_FOLDER + 'FTC-AUDIT-' + SESSION_ID + '.md'

WRITE to AUDIT_FILE:
  # {project_name} — FTC Session Audit
  session: {SESSION_ID}
  version: {NEW_VERSION}
  mode: {MODE}
  scope: {target_epic or "All Epics"}
  date: {ISO 8601}

  ## sources
  | source | path | status |
  | User Stories | {user_stories_path} | Loaded |
  | Test Strategy | {test_strategy_path} | Loaded |
  | MTP | {master_test_plan_path} | Loaded |
  | PRD | {prd_path} | Loaded / Not provided |
  | Epics | {epics_path} | Loaded / Not provided |
  | ADRs | {adrs_path} | Loaded / Not provided |

  ## generation_log
  | epic | stories | tcs | positive | negative | boundary | mvp_depth |

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

## Metadata
APPEND to ./artifacts/outputs/artifact-tracking.md:
  session, artifact_type: functional_test_cases, mode, version,
  scope, total_tcs, ac_coverage_pct, stories_covered, timestamp

## Checkpoint Cleanup
Delete CHECKPOINT_FILE (suites/_checkpoint.json) — no longer needed after successful completion.

## Verify all files
ASSERT MANIFEST exists and is non-empty
ASSERT all suite files in epic_map exist and are non-empty
ASSERT AUDIT_FILE exists


Memory Bank artifact type: `"{N} test-cases"` (e.g., `"35 test-cases"`).

**Memory Bank — MANDATORY session-end writes:**
1. Overwrite `context-pack/active-context.md` with session status, decisions, blockers, key artifacts (see execution-protocol.md Section 4 for schema).
2. Append one milestone row to `context-pack/progress.md` with artifact count above.

**LAST ACTION — MANDATORY:** Update `_progress.json` status to `COMPLETED` with `completed_at` timestamp.
If the session failed, set status to `FAILED` instead.

Ready for QA Review.
```

**Execution:** automated

## Reference Files
- `references/phase-a-epic-func-suites.md` — Per-epic atomic test case generation (loop protocol, TC template, fidelity checks)
- `references/func-test-cases-template.md` — Manifest + per-epic file structure templates
