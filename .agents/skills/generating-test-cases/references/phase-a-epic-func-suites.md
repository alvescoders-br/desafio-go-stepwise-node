# Phase A: Per-Epic Functional Test Suite Generation -- Atomic Loop

## Context Contract
- **Inputs:** FTC_INDEX (scoped_epics, suite_status), FTC_CONTEXT (stories_by_epic, tool_selections, mvp_epics, prd_business_rules), Upstream Rules (from SKILL.md Step 4)
- **Outputs:** One file per epic in SUITES_SUBFOLDER/epic-{NN}-func-tests.md
- **Carries Forward:** FTC_INDEX.epic_suites, .tc_catalog, .ac_coverage, .business_rule_coverage per epic
- **Flush After:** Each epic's test case text flushed BEFORE the next
- **H1 Title per file:** `# {project_name} -- EPIC-XX: {Title} Functional Tests`

## Output Quality Protocols
- **AC Exhaustion:** Every acceptance criterion -> at least one Then assertion.
- **Business Rule Coverage:** Every business rule -> at least one scenario.
- **Anti-Truncation:** Full Gherkin for ALL test cases. No skipping.
- **Uniform Depth:** Last story's TCs = same depth as first story's.
- **Risk-Based Depth:** MVP epics get extra negative/boundary scenarios.

## Mode-Specific Behavior
- **REPAIR:** Check if REPAIR_DIRECTIVES target this epic.
  IF none -> SKIP. IF targeted -> load file, apply, rewrite in place.
- **BUILD:** Generate from scratch.

---

## Atomic Loop Protocol

**Per-epic with chunked per-story generation inside each epic.**

```
REMAINING_EPICS = [epics with PENDING in FTC_INDEX.suite_status]
COMPLETED_EPICS = []
TOTAL_EPICS = len(REMAINING_EPICS)

WHILE REMAINING_EPICS is not empty:

  EPIC-XX = REMAINING_EPICS.pop_first()

  #================================================================
  # PHASE 1: LOAD EPIC SOURCE DATA
  #================================================================

  1. LOAD stories for this epic from FTC_CONTEXT.stories_by_epic[EPIC-XX]
     For each story: story_id, title, tag, narrative, acceptance_criteria,
     business_rules, in_scope, out_of_scope, dependencies, assumptions.
  2. DETERMINE if MVP epic: EPIC-XX in FTC_CONTEXT.mvp_epics?
     MVP -> full depth (positive + ALL negative + boundary).
     Non-MVP -> positive + key negative only.
  3. LOAD cross-reference business rules from FTC_CONTEXT.prd_business_rules (if available)
  4. IF REPAIR and no directive targets this epic -> SKIP. CONTINUE.

  ## ZERO INVENTION CHECKPOINT:
  Test cases MUST derive from loaded ACs and business rules.
  No invented business logic. Boundary values from explicit constraints
  or marked [Assumption].

  #================================================================
  # PHASE 2: CHUNKED PER-STORY GENERATION
  #================================================================

  STORIES = FTC_CONTEXT.stories_by_epic[EPIC-XX]
  TOTAL_STORIES = len(STORIES)
  CHUNK_SIZE = 2  # stories per chunk (each story produces 3-10+ TCs)
  CHUNKS = split STORIES into groups of CHUNK_SIZE
  TC_COUNTER = 0
  EPIC_FILE = SUITES_SUBFOLDER/epic-{NN}-func-tests.md

  ## Write File Header
  CREATE FILE at EPIC_FILE with:
    # {project_name} -- EPIC-XX: {Epic Title} Functional Tests
    Priority: {tier} | MVP: {Yes/No} | Stories: {TOTAL_STORIES}
    ---

  FOR EACH chunk in CHUNKS:

    chunk_stories = current chunk (up to CHUNK_SIZE stories)

    FOR EACH story in chunk_stories:

      ### Analyze Story
      1. Count ACs: {N} acceptance criteria
      2. Count business rules: {N} rules
      3. Identify inputs (fields, parameters, selections)
      4. Identify state transitions
      5. Identify dependencies on other stories/services

      ### Generate Test Cases

      #### Positive Test Cases (mandatory per story)
      FOR EACH acceptance criterion:
        Generate 1 happy path TC verifying the AC's expected behavior.
        TC_COUNTER += 1

      FOR EACH business rule:
        Generate 1 TC verifying the rule holds.
        TC_COUNTER += 1

      #### Negative Test Cases
      FOR EACH AC that implies validation/constraint:
        Generate TCs for: invalid input, missing required field,
        unauthorized access, constraint violation.
        TC_COUNTER += N

      IF MVP epic (extra depth):
        FOR EACH input field:
          - Empty/null value
          - Maximum length exceeded
          - Special characters / injection patterns
          - Invalid data type
        FOR EACH state transition:
          - Invalid source state
          - Concurrent modification
        FOR EACH dependency:
          - Dependency unavailable/timeout
          - Malformed response from dependency

      #### Boundary Test Cases (if constraints have numeric/size limits)
      FOR EACH constraint with explicit boundary:
        - At minimum value, below minimum
        - At maximum value, above maximum
        - At typical value
        TC_COUNTER += N

      ### Apply MANDATORY TEMPLATE to each TC (see below)

    ### Per-Chunk Fidelity Check
    FOR EACH generated TC in this chunk:
      a. Traces to an AC number or business rule? (no invented logic)
      b. Actor matches story narrative persona?
      c. Domain tag matches story tag ([BE]/[FE])?
      d. Gherkin syntax is strict Given/When/Then?
    IF violations -> correct before appending.

    ### APPEND chunk to epic file. Mandatory tool call.
    ### FLUSH chunk. Only FTC_INDEX metadata survives.
    ### LOG: "EPIC-XX chunk {N}/{total}: {stories} stories, {tcs} TCs appended."

  ## End chunked loop for this epic.

  #================================================================
  # PHASE 3: FINALIZE EPIC
  #================================================================

  3a. CONFIRM: File exists, non-empty, TC count matches.

  3b. UPDATE FTC_INDEX:
      FTC_INDEX.epic_suites[EPIC-XX] = {
        file: "epic-{NN}-func-tests.md",
        tc_count: TC_COUNTER,
        story_count: TOTAL_STORIES,
        types: { positive: N, negative: N, boundary: N }
      }
      FTC_INDEX.tc_catalog += [{tc_id, story_id, title, type, tag}]
      FTC_INDEX.ac_coverage[story_id] = { total_acs: N, covered_acs: N, tc_ids: [...] }
      FTC_INDEX.business_rule_coverage[rule_id] = [tc_ids]

  3c. WRITE CHECKPOINT: Serialize FTC_INDEX to CHECKPOINT_FILE (_checkpoint.json).
      Mark this epic as COMPLETE ({TC_COUNTER} TCs) in FTC_INDEX.suite_status.
  3d. FLUSH. Only FTC_INDEX survives.
  3e. LOG: "EPIC-XX complete: {TC_COUNTER} TCs for {TOTAL_STORIES} stories."

  Add to COMPLETED_EPICS. CONTINUE.

## Loop Completion Gate
ASSERT len(COMPLETED_EPICS) == TOTAL_EPICS.
```

---

## MANDATORY TEST CASE TEMPLATE

Apply to EVERY test case:

```markdown
---
**TC_ID:** FTC_{EPIC}_{STORY}_{SEQ} (e.g., FTC_01_03_01)
**Story:** {US-XX-NN-TAG}
**AC/Rule:** {AC #N from story | BR-{N} | [Assumption]}
**Type:** Positive / Negative / Boundary
**Tag:** [{BE}] / [{FE}] / [{DATA}] (matches story domain tag)
**Priority:** P0 / P1 / P2 (from MTP)
---
```

````gherkin
Feature: {Story Title} - Functional Verification

  Background:
    Given {precondition from story context}

  @{EPIC_ID} @{STORY_ID} @{type_tag} @{domain_tag}
  Scenario: FTC_01_03_01 - {Descriptive name}
    Given {specific precondition from AC}
    When {action from AC - declarative business language}
    And {additional action step if multi-step}
    Then {verification from AC's Then clause}
    And {additional verification - every AC bullet = a Then}
````

### Positive TC Example
```gherkin
  @EPIC-01 @US-01-03-BE @positive @BE
  Scenario: FTC_01_03_01 - Successful container type classification
    Given the operator has started a new registration
    And container "MSCU-7654321" details are loaded
    When the operator selects container type "40ft Reefer"
    Then the container is classified as "Refrigerated"
    And the temperature monitoring flag is enabled
    And the classification audit entry is recorded
```

### Negative TC Example (from AC constraint)
```gherkin
  @EPIC-01 @US-01-03-BE @negative @BE
  Scenario: FTC_01_03_02 - Reject invalid container type
    Given the operator has started a new registration
    When the operator submits with container type field empty
    Then a validation error "Container type is required" is displayed
    And the registration is not created
    And the form retains the entered data
```

### Boundary TC Example
```gherkin
  @EPIC-01 @US-01-03-BE @boundary @BE
  Scenario: FTC_01_03_05 - Container ID at maximum length
    Given the operator is on the registration form
    When the operator enters a container ID of exactly 11 characters
    Then the input is accepted
    But entering 12 characters shows "Maximum 11 characters allowed"
```

### MVP Extra Negative Example
```gherkin
  @EPIC-01 @US-01-03-BE @negative @BE @mvp-depth
  Scenario: FTC_01_03_08 - Registration when persistence layer unavailable
    Given the operator has filled the registration form
    And the persistence layer is temporarily unavailable
    When the operator submits the registration
    Then a service unavailable error is displayed
    And the entered data is preserved for retry
    And the error is logged with correlation ID
```

### Rules
- NEVER summarize verification: "Then it works" -> explicit Then per AC bullet
- NEVER use imperative steps: "click button" -> "submit the form"
- NEVER skip business rules: every BR -> at least one scenario
- Domain tag on TC MUST match story tag
- MVP epics: generate dependency/infrastructure failure scenarios
