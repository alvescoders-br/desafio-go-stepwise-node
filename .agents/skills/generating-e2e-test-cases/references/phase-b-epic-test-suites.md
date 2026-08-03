# Phase B: Per-Epic E2E Test Suite Generation -- Atomic Loop

## Context Contract
- **Inputs:** TC_INDEX.journey_map (from Phase A), TC_CONTEXT (full), BDD Engineering Rules (from SKILL.md Step 4)
- **Outputs:** One file per epic in SUITES_SUBFOLDER/epic-{NN}-e2e-suite.md
- **Carries Forward:** TC_INDEX.epic_suites, .tc_catalog, .coverage_map, .gap_detected per epic
- **Flush After:** Each epic's suite text flushed BEFORE generating the next
- **Dependency:** Phase A COMPLETE with TC_INDEX.journey_map populated
- **H1 Title per file:** `# {project_name} -- EPIC-XX: {Epic Title} E2E Test Suite`

## Output Quality Protocols
- **Exhaustive Coverage:** Every acceptance criterion from source -> a Then assertion.
- **Anti-Truncation:** Full Gherkin for ALL test cases. No grouping or skipping.
- **Uniform Depth:** Last epic's suite = same depth as first epic's suite.
- **Realistic Data:** No generic placeholders. Invent realistic dummy data.
- **Gap Engineering:** Proactively identify missing negative/boundary paths.

## Mode-Specific Behavior
- **REPAIR:** Check if REPAIR_DIRECTIVES target this epic.
  IF none -> SKIP (preserve existing file). Log "Preserved: EPIC-XX".
  IF targeted -> load existing file, apply directive, rewrite in place.
- **BUILD:** Generate from scratch.

---

## Atomic Loop Protocol

**CRITICAL -- TOOL-CALL BOUNDARY:**
Each epic suite: generate -> write file (tool call) -> flush.
Do NOT accumulate multiple epics in memory.

**CHUNKED GENERATION FOR LARGE EPICS:**
If an epic has 8+ user journeys, generate test cases in chunks of 2-3 journeys,
appending each chunk to the epic file and flushing before the next chunk.
Same nested write-flush pattern as User Stories' chunked generation.

**CONTINUATION MANDATE:**
Process ALL in-scope epics. Do NOT stop after the first.

```
REMAINING_EPICS = [epics with PENDING status in TC_INDEX.suite_status]
COMPLETED_EPICS = []
TOTAL_EPICS = len(REMAINING_EPICS)

WHILE REMAINING_EPICS is not empty:

  EPIC-XX = REMAINING_EPICS.pop_first()

  #================================================================
  # PHASE 1: LOAD EPIC SOURCE DATA
  #================================================================
  # After flushing previous epic, agent has NO knowledge of this epic.

  1. LOAD journeys for this epic from TC_INDEX.journey_map[EPIC-XX]
  2. LOAD epic details from TC_CONTEXT.epic_list (title, priority, complexity)
  3. LOAD user stories from TC_CONTEXT.user_stories for this epic (if available):
     - For each story: narrative, acceptance_criteria, business_rules, in_scope
  4. LOAD FR descriptions from TC_CONTEXT.prd_fr_ids for FRs mapped to this epic
  5. LOAD personas from TC_CONTEXT.epic_personas[EPIC-XX]
  6. DETERMINE test_priority from TC_CONTEXT.scope_features

  7. IF REPAIR and no directive targets this epic -> SKIP. CONTINUE.

  ## ZERO INVENTION CHECKPOINT:
  Journeys MUST match TC_INDEX.journey_map[EPIC-XX].
  Test steps MUST derive from loaded acceptance criteria and business rules.
  Actors MUST be loaded personas. Gaps found during engineering -> [Gap-Detected].

  #================================================================
  # PHASE 2: PLAN TEST COVERAGE
  #================================================================

  FOR EACH journey in this epic:
    PLAN:
    - 1 Happy Path Scenario (mandatory)
    - N Negative/Error Scenarios (from loaded ACs + gap engineering)
    - Scenario Outlines with Examples if data variations exist
    - Boundary test cases for numeric/text inputs

    Apply priority-based depth:
    P0: happy + ALL negative + boundary + data variations
    P1: happy + key negative + data variations
    P2: happy + critical negative only

  TC_COUNTER = starting sequence for this epic

  #================================================================
  # PHASE 3: GENERATE TEST CASES (chunked if large)
  #================================================================

  IF journey count > 6:
    Use chunked generation: 2-3 journeys per chunk.
    Write file header first, then append chunks.
  ELSE:
    Generate all journeys in one pass.

  FOR EACH journey (or journey chunk):

    Generate test cases using MANDATORY TEMPLATE below.

    ## Per-Chunk Fidelity Check (before writing/appending):
    - Journey name matches TC_INDEX.journey_map
    - Actor matches loaded persona
    - Every Then assertion traces to an AC or business rule from source
    - No invented features (gaps marked [Gap-Detected])
    IF violations -> correct before writing.

    ## WRITE/APPEND to epic file. Mandatory tool call.
    ## FLUSH chunk content (if chunked).

  #================================================================
  # PHASE 4: FINALIZE EPIC SUITE
  #================================================================

  4a. CONFIRM: File exists, non-empty, contains all planned TCs.

  4b. UPDATE TC_INDEX:
      TC_INDEX.epic_suites[EPIC-XX] = {
        file: "epic-{NN}-e2e-suite.md",
        tc_count: N,
        journey_count: N,
        types: { positive: N, negative: N, boundary: N, data_variation: N },
        gaps_found: N
      }
      TC_INDEX.tc_catalog += [{ tc_id, epic, title, type, journey, priority }]
      TC_INDEX.coverage_map += {FR-XX -> [TC_IDs]}
      TC_INDEX.gap_detected += [any gaps found for this epic]

  4c. UPDATE 00-e2e-index.md: this epic -> "COMPLETE ({N} test cases)".

  4d. FLUSH: Drop ALL Gherkin text. Only TC_INDEX survives.

  4e. LOG: "EPIC-XX complete: {N} TCs across {N} journeys.
      Progress: {completed}/{TOTAL_EPICS}."

  Add EPIC-XX to COMPLETED_EPICS. CONTINUE.

## Loop Completion Gate
ASSERT len(COMPLETED_EPICS) == TOTAL_EPICS
IF not equal -> re-enter loop for missing.
```

---

## MANDATORY TEST CASE TEMPLATE

Apply to EVERY test case. Structure exactly as follows:

```markdown
---
**TC_ID:** TC_{EPIC_ID}_{SEQ} (e.g., TC_EPIC01_01)
**Title:** {Descriptive scenario name}
**Type:** Positive / Negative / Boundary / Data Variation
**Priority:** P0 / P1 / P2
**Journey:** {Journey name from TC_INDEX.journey_map}
**Actor:** {Persona name from TC_CONTEXT}
**Source:** {US-XX-NN-TAG AC #N / FR-XX / [Gap-Detected]}
**Test Data:**
* {Variable 1}: {Realistic value} (e.g., "Company Name: Acme Logistics Corp")
* {Variable 2}: {Realistic value} (e.g., "Container ID: MSCU-7654321")
* {Variable N}: {Realistic value}
---
```

````gherkin
Feature: {Journey Name} - {Epic Title}

  Background:
    Given {precondition 1 from source}
    And {precondition 2 if applicable}

  @{EPIC_ID} @{type_tag} @{priority_tag}
  Scenario: {TC_ID} - {Descriptive name}
    When {action step 1 - declarative business language}
    And {action step 2}
    Then {verification step 1 - specific, independently verifiable}
    And {verification step 2}
    And {verification step 3}
````

### Scenario Strategy Rules

**Happy Path (1 per journey, mandatory):**
```gherkin
  Scenario: TC_EPIC01_01 - Successful container registration
    Given the operator is authenticated and on the registration screen
    And the container "MSCU-7654321" is not yet registered
    When the operator enters container ID "MSCU-7654321"
    And selects container type "40ft Dry"
    And submits the registration form
    Then the success confirmation is displayed with registration number
    And the container appears in the active containers list
    And the audit log records the registration event with operator ID
```

**Data Variation (Scenario Outline when input varies):**
```gherkin
  Scenario Outline: TC_EPIC01_02 - Registration with different container types
    Given the operator is authenticated
    When the operator registers container "<container_id>" as type "<type>"
    Then the container is registered with correct type classification

    Examples:
      | container_id  | type          |
      | MSCU-1234567  | 20ft Dry      |
      | TCLU-9876543  | 40ft Reefer   |
      | MSKU-5555555  | 40ft High Cube|
```

**Negative Path (separate Scenarios for each error condition):**
```gherkin
  Scenario: TC_EPIC01_03 - Registration fails for duplicate container
    Given container "MSCU-7654321" is already registered
    When the operator attempts to register "MSCU-7654321" again
    Then the duplicate error message is displayed
    And the existing registration details are shown
    And no new record is created
```

**Boundary (targeting limits, empty inputs, overflow):**
```gherkin
  Scenario: TC_EPIC01_04 - Registration with maximum-length container ID
    Given the operator is on the registration screen
    When the operator enters a container ID of 15 characters
    Then the system accepts the input
    But entering 16 characters shows a validation error
```

### NEVER Rules (from BDD Architect)
- NEVER use generic placeholders: "[Enter Name Here]" -> "Acme Logistics Corp"
- NEVER summarize verification: "Then the form works" -> "Then the confirmation shows registration #REG-2024-0001 And the container status is 'Active'"
- NEVER use imperative/HTML steps: "When I click #submit-btn" -> "When I submit the registration form"
- NEVER skip preconditions: if source says "user is authenticated" -> Given step must exist
- NEVER ignore business criteria: every bullet in source ACs -> a Then assertion

### Gap Engineering Markers
When the BDD engineer identifies a missing path not in source material:
```
**Source:** [Gap-Detected] No cancel flow defined in AC. Generated for completeness.
```
These are flagged in TC_INDEX.gap_detected and surfaced in the traceability audit
for stakeholder review.

---

## Post-Phase B Protocol

1. **Verify:** All epic suite files exist. Count == in-scope epic count.
2. **Summary Count Verification:** TC count across all suites == TC_INDEX.tc_catalog length.
3. **Anti-Fade Check:** Compare TC density of first epic vs last epic.
4. **Update TC_INDEX:** Phase B complete.
5. **Log:** "Phase B complete. {N} test cases across {N} epics, {N} gaps detected."
