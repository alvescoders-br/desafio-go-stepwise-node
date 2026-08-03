# Agent-Native E2E Test Cases — Template Reference

## Architecture: Manifest + Per-Epic Gherkin Suites

The output is ALWAYS a manifest plus per-epic suite files.
Per-epic files use strict Gherkin format — they are already agent-native
and require no structural changes from v2.0.1.

```
E2E/
├── E2E-MANIFEST-{SESSION_ID}.md   ← Journey map + coverage data + validations (always in context)
├── suites/
│   ├── epic-01-e2e-suite.md       ← Gherkin E2E test cases (loaded on demand)
│   ├── epic-02-e2e-suite.md
│   └── ...
└── E2E-AUDIT-{SESSION_ID}.md      ← Session metadata
```

**Consumption pattern:**
The QA automation agent loads the MANIFEST (always) + ONE suite file (current work).
When it finishes an epic, it drops the file and loads the next.
It never needs all E2E test cases in context.

---

## Template Rules

- **No prose.** Every section is structured data only.
- **No narrative.** No motivational text, no context paragraphs.
- **All items carry status.** `complete` | `pending` | `assumption`.
- **All gaps in open_questions.** Single registry, no scatter.
- **Source tags mandatory.** No source → cannot be `complete`.
- **Language:** Generate in DETECTED_LANGUAGE. Section headers in English always.
- **Journey traceability:** Every TC traces to a named journey. Every journey traces to source stories/FRs.
- **Gap markers:** BDD-engineer-identified gaps marked `[Gap-Detected]` with rationale.

---

## File 1: E2E-MANIFEST-{SESSION_ID}.md

```markdown
# {project_name} — E2E Test Cases Manifest
version: {NEW_VERSION}
session: {SESSION_ID}
mode: {BUILD | REPAIR}
date: {ISO 8601}
language: {DETECTED_LANGUAGE}
status: {draft | complete}

---

## scope

- total_epics: {N}
- total_journeys: {N}
- total_test_cases: {N}
- by_type: positive: {n}, negative: {n}, boundary: {n}, data_variation: {n}
- prd_source: {prd_path}
- epics_source: {epics_path}
- stories_source: {user_stories_path | "Not provided"}
- strategy_source: {test_strategy_path}
- mtp_source: {master_test_plan_path}

---

## journey_map

| epic | journey_name | actor | source_stories | fr_ids | priority | status |
|------|-------------|-------|----------------|--------|----------|--------|
| EPIC-01 | Container Registration Flow | Port Operator | US-01-01-BE, US-01-02-FE | FR-01, FR-02 | P0 | complete |
| EPIC-01 | Bulk Import Flow | Port Admin | US-01-03-BE | FR-03 | P0 | complete |
| EPIC-02 | Container Exit Processing | Gate Clerk | US-02-01-BE, US-02-02-FE | FR-05 | P1 | complete |
| EPIC-02 | Exit Billing Validation | Billing Admin | [Derived from FR] | FR-06 | P1 | assumption |

---

## journey_catalog

### EPIC-01: {title}

#### Container Registration Flow
- actor: Port Operator
- happy_path_steps: authenticate -> navigate to registration -> enter container data -> submit -> confirm
- alternative_flows: duplicate container, invalid format, system timeout
- source: US-01-01-BE, US-01-02-FE
- related_frs: FR-01, FR-02
- priority: P0
- status: complete

#### Bulk Import Flow
- actor: Port Admin
- happy_path_steps: authenticate -> upload CSV -> validate -> confirm import -> review results
- alternative_flows: malformed CSV, partial failure, duplicate entries
- source: US-01-03-BE
- related_frs: FR-03
- priority: P0
- status: complete

### EPIC-02: {title}

#### Container Exit Processing
- actor: Gate Clerk
- happy_path_steps: scan container -> verify documentation -> process exit -> generate receipt
- alternative_flows: missing documentation, container hold, system offline
- source: US-02-01-BE, US-02-02-FE
- related_frs: FR-05
- priority: P1
- status: complete

---

## epic_map

| epic | title | priority | journeys | tcs | positive | negative | boundary | data_var | gaps | file | status |
|------|-------|----------|----------|-----|----------|----------|----------|----------|------|------|--------|
| EPIC-01 | {title} | Must Have | 2 | 15 | 4 | 6 | 3 | 2 | 2 | suites/epic-01-e2e-suite.md | complete |
| EPIC-02 | {title} | Should Have | 2 | 10 | 3 | 4 | 2 | 1 | 1 | suites/epic-02-e2e-suite.md | complete |
| EPIC-03 | {title} | Could Have | 1 | 4 | 2 | 1 | 1 | 0 | 0 | suites/epic-03-e2e-suite.md | pending |

---

## tc_catalog

### EPIC-01: {title}

| tc_id | journey | title | type | priority | actor | source |
|-------|---------|-------|------|----------|-------|--------|
| TC_EPIC01_01 | Container Registration Flow | Successful container registration | positive | P0 | Port Operator | US-01-01-BE AC-01 |
| TC_EPIC01_02 | Container Registration Flow | Registration with different types | data_variation | P0 | Port Operator | US-01-01-BE AC-02 |
| TC_EPIC01_03 | Container Registration Flow | Duplicate container rejection | negative | P0 | Port Operator | US-01-01-BE AC-03 |
| TC_EPIC01_04 | Container Registration Flow | Cancel mid-registration | negative | P0 | Port Operator | [Gap-Detected] |
| TC_EPIC01_05 | Container Registration Flow | Max-length container ID | boundary | P0 | Port Operator | US-01-01-BE AC-01 |

### EPIC-02: {title}

| tc_id | journey | title | type | priority | actor | source |
|-------|---------|-------|------|----------|-------|--------|
| TC_EPIC02_01 | Container Exit Processing | Successful exit processing | positive | P1 | Gate Clerk | US-02-01-BE AC-01 |

---

## fr_coverage

| fr_id | description | journey(s) | tc_ids | status |
|-------|-------------|------------|--------|--------|
| FR-01 | Container registration | Container Registration Flow | TC_EPIC01_01, TC_EPIC01_02, TC_EPIC01_03 | covered |
| FR-02 | Registration validation | Container Registration Flow | TC_EPIC01_05 | covered |
| FR-05 | Exit processing | Container Exit Processing | TC_EPIC02_01 | covered |
| FR-08 | Reporting dashboard | — | — | gap |

fr_coverage_pct: {N}%

---

## ac_coverage

| story_id | total_acs | covered_acs | missing_acs | status |
|----------|-----------|-------------|-------------|--------|
| US-01-01-BE | 4 | 4 | — | covered |
| US-01-02-FE | 3 | 3 | — | covered |
| US-02-01-BE | 5 | 4 | AC-05 | gap |

ac_coverage_pct: {N}%
Note: N/A when user_stories not provided.

---

## test_type_distribution

| type | count | percentage | assessment |
|------|-------|------------|------------|
| positive | {N} | {pct}% | — |
| negative | {N} | {pct}% | — |
| boundary | {N} | {pct}% | — |
| data_variation | {N} | {pct}% | — |

health: {balanced | flag: >60% positive, insufficient negative coverage}

---

## persona_coverage

| persona | tc_count | epics | journeys | status |
|---------|----------|-------|----------|--------|
| Port Operator | {N} | EPIC-01 | Container Registration Flow | covered |
| Gate Clerk | {N} | EPIC-02 | Container Exit Processing | covered |
| Billing Admin | 0 | — | — | gap |

---

## gap_detected_items

| id | epic | journey | tc_id | description | rationale |
|----|------|---------|-------|-------------|-----------|
| GAP-01 | EPIC-01 | Container Registration Flow | TC_EPIC01_04 | Cancel mid-registration flow | No cancel flow defined in AC. Generated for completeness. |
| GAP-02 | EPIC-01 | Container Registration Flow | TC_EPIC01_08 | Session timeout during registration | No timeout scenario in source. Critical for long forms. |

---

## validations

| check | result | details |
|-------|--------|---------|
| epic_coverage | pass | {N}/{N} epics have suite files |
| fr_traceability | pass | {N}/{N} FRs covered by at least one TC |
| ac_exhaustion | pass | {N}/{N} ACs covered |
| journey_completeness | pass | All journeys have happy path TC |
| persona_coverage | pass | {N}/{N} personas represented |
| type_distribution | pass | Balanced |
| count_verification | pass | Suite count = epic count, TC totals match |
| anti_fade | pass | First/last epic depth within ±20% |
| gherkin_compliance | pass | All TCs strict Given/When/Then |
| source_fidelity | pass | All TCs trace to AC, FR, or [Gap-Detected] |

validations_passed: {N}/10
status: {draft | complete}

---

## open_questions

### coverage_gaps

| id | type | item_id | description |
|----|------|---------|-------------|
| CG-01 | uncovered_fr | FR-08 | FR not covered by any journey or TC |
| CG-02 | uncovered_ac | US-02-01-BE:AC-05 | AC not covered by any TC |
| CG-03 | missing_happy_path | EPIC-03:Reporting Flow | Journey has no happy path TC |

### missing_inputs

| id | type | epic | field | impact |
|----|------|------|-------|--------|
| MI-01 | missing | — | user_stories_path | Cannot verify AC exhaustion. Journeys derived from FRs only. |

### assumptions_to_validate

| id | assumption | item_id | impact_if_wrong | validation_method |
|----|-----------|---------|-----------------|-------------------|
| ASM-E01 | Boundary at 15 chars for container ID | TC_EPIC01_05 | Boundary TCs invalid | Confirm with engineering |
| ASM-E02 | Exit Billing journey actor is Billing Admin | EPIC-02 | Actor mismatch in TCs | Confirm with PO |

### upstream_gaps_carried_forward

| id | source | description | local_coverage | recommendation |
|----|--------|-------------|----------------|----------------|
| UG-01 | Epics | EPIC-04 has no FR mappings | Cannot derive journeys | Add FR mappings to epics |

### summary
- total_test_cases: {N}
- by_type: positive: {n}, negative: {n}, boundary: {n}, data_variation: {n}
- total_journeys: {N}
- epics_covered: {N}/{N}
- fr_coverage_pct: {N}%
- ac_coverage_pct: {N}% (or N/A)
- coverage_gaps: {N}
- missing_inputs: {N}
- assumptions: {N}
- upstream_gaps: {N}
- gap_detected_items: {N}
- validations_passed: {N}/10
- status: {draft | complete}
```

**Manifest size per project scale:**
- 3 epics, 10 journeys, 40 TCs: ~180 lines (~540 tokens)
- 6 epics, 25 journeys, 120 TCs: ~350 lines (~1,050 tokens)
- 10 epics, 50 journeys, 300 TCs: ~550 lines (~1,650 tokens)

All fit comfortably in the QA automation agent's context alongside its
own instructions and the current epic's Gherkin file.

---

## File 2: suites/epic-{NN}-e2e-suite.md (Per-Epic Gherkin Suite)

Format is UNCHANGED from v2.0.1. See `references/phase-b-epic-test-suites.md`
for the mandatory TC template and Gherkin format rules.

Summary of format requirements:

```markdown
# {project_name} -- EPIC-XX: {Epic Title} E2E Test Suite
Priority: {tier} | Journeys: {N}

---

## Journey: {Journey Name}

---
**TC_ID:** TC_{EPIC_ID}_{SEQ}
**Title:** {Descriptive scenario name}
**Type:** Positive / Negative / Boundary / Data Variation
**Priority:** P0 / P1 / P2
**Journey:** {Journey name from TC_INDEX.journey_map}
**Actor:** {Persona name from TC_CONTEXT}
**Source:** {US-XX-NN-TAG AC #N / FR-XX / [Gap-Detected]}
**Test Data:**
* {Variable 1}: {Realistic value}
* {Variable 2}: {Realistic value}
---
```

````gherkin
Feature: {Journey Name} - {Epic Title}

  Background:
    Given {precondition from source}

  @{EPIC_ID} @{type_tag} @{priority_tag}
  Scenario: TC_EPIC01_01 - {Descriptive name}
    When {action step - declarative business language}
    Then {verification step - specific, independently verifiable}
    And {additional verification}
````

### Gherkin Rules (from BDD Engineering Rules)
- NEVER summarize verification: "Then it works" -> explicit Then per AC bullet
- NEVER use imperative steps: "click button" -> "submit the form"
- NEVER skip business rules: every criterion -> at least one scenario
- NEVER use generic placeholders: "[Enter Name Here]" -> "Acme Logistics Corp"
- Technology-neutral language in all steps
- Every Then step must be independently verifiable
- Gap-detected TCs marked with `[Gap-Detected]` source

---

## File 3: E2E-AUDIT-{SESSION_ID}.md

```markdown
# {project_name} — E2E Test Cases Session Audit
session: {SESSION_ID}
version: {NEW_VERSION}
mode: {BUILD | REPAIR}
date: {ISO 8601}

---

## sources

| source | path | status |
|--------|------|--------|
| PRD | {prd_path} | Loaded |
| Epics | {epics_path} | Loaded |
| User Stories | {user_stories_path} | Loaded / Not provided |
| MTP | {master_test_plan_path} | Loaded |
| Test Strategy | {test_strategy_path} | Loaded |
| ADRs | {adrs_path} | Loaded / Not provided |

---

## generation_log

| epic | journeys | tcs | positive | negative | boundary | data_variation | gaps_found |
|------|----------|-----|----------|----------|----------|----------------|------------|

---

## validation_summary

| check | result | details |
|-------|--------|---------|
(10 checks)

---

## change_log

(REPAIR mode only)

| version | directive | target | change | impact |
|---------|-----------|--------|--------|--------|
```

---

## Generation Rules

### Section Ordering
1. scope (independent)
2. journey_map (depends on: upstream epic_list, user_stories, prd_fr_ids)
3. journey_catalog (depends on: journey_map)
4. epic_map (depends on: per-epic suite generation complete)
5. tc_catalog (depends on: per-epic suite generation complete)
6. fr_coverage (depends on: tc_catalog + journey_map)
7. ac_coverage (depends on: tc_catalog + user_stories)
8. test_type_distribution (depends on: tc_catalog)
9. persona_coverage (depends on: tc_catalog)
10. gap_detected_items (depends on: per-epic suite generation complete)
11. validations (depends on: all above sections)
12. open_questions (ALWAYS LAST — depends on: validations + all gaps)

### Per-Epic Generation
Within each epic, follow the atomic loop from phase-b-epic-test-suites.md:
- Load epic context from TC_INDEX.journey_map + TC_CONTEXT
- Generate TCs per journey (chunked if >6 journeys)
- Fidelity check before writing
- Write -> flush -> update TC_INDEX -> continue

### REPAIR Mode
- Load existing manifest and suite files
- Apply REPAIR_DIRECTIVES to targeted epics only
- Preserve untargeted suite files verbatim
- Preserve existing TC IDs. New TCs: max(existing) + 1. Retired IDs: never reuse.
- IF upstream data changed: rebuild journey_map, fr_coverage, ac_coverage
- ALWAYS rebuild open_questions from scratch
- Increment version, log changes

### Scaling
- Estimated items: 3-15 epics, 10-80 journeys, 40-500 TCs
- Lines per TC in manifest: ~1 (tc_catalog row)
- Lines per journey in catalog: ~8
- Threshold: manifest stays under 600 lines at all expected scales
- Per-epic suites: 20-150 scenarios each (loaded one at a time)
