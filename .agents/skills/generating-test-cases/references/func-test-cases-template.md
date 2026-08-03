# Agent-Native Functional Test Cases — Template Reference

## Architecture: Manifest + Per-Epic Gherkin Suites

The output is ALWAYS a manifest plus per-epic suite files.
Per-epic files use strict Gherkin format — they are already agent-native
and require no structural changes from v2.0.1.

```
FTC/
├── FTC-MANIFEST-{SESSION_ID}.md   ← Coverage data + validations (always in context)
├── suites/
│   ├── epic-01-func-tests.md       ← Gherkin test cases (loaded on demand)
│   ├── epic-02-func-tests.md
│   └── ...
└── FTC-AUDIT-{SESSION_ID}.md       ← Session metadata
```

**Consumption pattern:**
The QA automation agent loads the MANIFEST (always) + ONE suite file (current work).
When it finishes an epic, it drops the file and loads the next.
It never needs all test cases in context.

---

## File 1: FTC-MANIFEST-{SESSION_ID}.md

```markdown
# {project_name} — Functional Test Cases Manifest
version: {NEW_VERSION}
session: {SESSION_ID}
mode: {BUILD | REPAIR}
date: {ISO 8601}
language: {DETECTED_LANGUAGE}
status: {draft | complete}

---

## scope

- target: {target_epic | "All Epics"}
- total_epics: {N}
- total_stories: {N}
- total_test_cases: {N}
- strategy_source: {test_strategy_path}
- mtp_source: {master_test_plan_path}
- stories_source: {user_stories_path}

---

## epic_map

| epic | title | stories | tcs | positive | negative | boundary | mvp | file | status |
|------|-------|---------|-----|----------|----------|----------|-----|------|--------|
| EPIC-01 | {title} | {N} | {N} | {N} | {N} | {N} | Yes | suites/epic-01-func-tests.md | complete |
| EPIC-02 | {title} | {N} | {N} | {N} | {N} | {N} | No | suites/epic-02-func-tests.md | complete |
| EPIC-03 | {title} | {N} | {N} | {N} | {N} | {N} | Yes | suites/epic-03-func-tests.md | pending |

---

## tc_catalog

### EPIC-01: {title}

| tc_id | story_id | title | type | tag | priority | ac_or_rule |
|-------|----------|-------|------|-----|----------|------------|
| FTC_01_01_01 | US-01-01-BE | {title} | positive | BE | P0 | AC-01 |
| FTC_01_01_02 | US-01-01-BE | {title} | negative | BE | P0 | AC-02 |
| FTC_01_01_03 | US-01-01-BE | {title} | boundary | BE | P1 | BR-01 |

### EPIC-02: {title}

| tc_id | story_id | title | type | tag | priority | ac_or_rule |
|-------|----------|-------|------|-----|----------|------------|
| FTC_02_01_01 | US-02-01-FE | {title} | positive | FE | P1 | AC-01 |

---

## ac_coverage

| story_id | total_acs | covered_acs | missing_acs | status |
|----------|-----------|-------------|-------------|--------|
| US-01-01-BE | 4 | 4 | — | covered |
| US-01-02-FE | 3 | 3 | — | covered |
| US-02-01-FE | 5 | 4 | AC-05 | gap |

ac_coverage_pct: {N}%

---

## business_rule_coverage

| rule_id | source_story | tc_ids | status |
|---------|-------------|--------|--------|
| BR-01 | US-01-01-BE | FTC_01_01_03, FTC_01_01_04 | covered |
| BR-02 | US-01-03-BE | FTC_01_03_02 | covered |
| BR-03 | US-02-01-FE | — | gap |

br_coverage_pct: {N}%

---

## test_type_distribution

| type | count | percentage | assessment |
|------|-------|------------|------------|
| positive | {N} | {pct}% | — |
| negative | {N} | {pct}% | — |
| boundary | {N} | {pct}% | — |

health: {balanced | flag: >70% positive, insufficient negative coverage}

---

## mvp_depth_verification

| epic | mvp | extra_negative_tcs | injection_tcs | concurrency_tcs | dependency_tcs | status |
|------|-----|--------------------|---------------|-----------------|----------------|--------|
| EPIC-01 | Yes | {N} | {N} | {N} | {N} | pass |
| EPIC-03 | Yes | {N} | {N} | {N} | {N} | pass |
| EPIC-02 | No | — | — | — | — | n/a |

---

## domain_tag_consistency

| tc_id | tc_tag | story_tag | match |
|-------|--------|-----------|-------|
| FTC_01_01_01 | BE | BE | yes |
| FTC_01_02_01 | FE | FE | yes |

mismatches: {N}
consistency_pct: {N}%

Note: Only list mismatches in this section if any exist.
If 100% consistent, write: "All TCs match source story tags. 0 mismatches."

---

## validations

| check | result | details |
|-------|--------|---------|
| story_coverage | pass | {N}/{N} stories covered |
| ac_exhaustion | pass | {N}/{N} ACs covered |
| br_coverage | pass | {N}/{N} rules covered |
| type_distribution | pass | Balanced |
| mvp_depth | pass | All MVP epics have extra depth |
| tag_consistency | pass | 0 mismatches |
| count_verification | pass | Suite count = epic count, TC totals match |
| anti_fade | pass | First/last epic depth within ±20% |
| gherkin_compliance | pass | All TCs strict Given/When/Then |
| source_fidelity | pass | All TCs trace to AC or BR |

validations_passed: {N}/10
status: {draft | complete}

---

## open_questions

### coverage_gaps

| id | type | item_id | description |
|----|------|---------|-------------|
| CG-01 | uncovered_ac | US-02-01-FE:AC-05 | AC not covered by any TC |
| CG-02 | uncovered_br | BR-03 | Business rule not covered |

### missing_inputs

| id | type | epic | story_id | field | impact |
|----|------|------|----------|-------|--------|
| MI-01 | missing | EPIC-02 | US-02-03-BE | business_rules | Cannot generate BR scenarios |

### assumptions_to_validate

| id | assumption | story_id | impact_if_wrong |
|----|-----------|----------|-----------------|
| ASM-F01 | Boundary at 255 chars | US-01-01-BE | Boundary TCs invalid |

### upstream_gaps_carried_forward

| id | source | description | recommendation |
|----|--------|-------------|----------------|
| UG-01 | User Stories | US-03-01 has 2 ACs (below minimum) | Add ACs or confirm intentional |

### summary
- total_test_cases: {N}
- by_type: positive: {n}, negative: {n}, boundary: {n}
- epics_covered: {N}/{N}
- ac_coverage_pct: {N}%
- br_coverage_pct: {N}%
- coverage_gaps: {N}
- missing_inputs: {N}
- assumptions: {N}
- upstream_gaps: {N}
- validations_passed: {N}/10
- status: {draft | complete}
```

**Manifest size per project scale:**
- 3 epics, 15 stories, 60 TCs: ~150 lines (~450 tokens)
- 6 epics, 40 stories, 200 TCs: ~300 lines (~900 tokens)
- 10 epics, 80 stories, 500 TCs: ~550 lines (~1,700 tokens)

All fit comfortably in the QA automation agent's context alongside its
own instructions and the current epic's Gherkin file.

---

## File 2: suites/epic-{NN}-func-tests.md (Per-Epic Gherkin Suite)

Format is UNCHANGED from v2.0.1. See `references/phase-a-epic-func-suites.md`
for the mandatory TC template and Gherkin format rules.

Summary of format requirements:

```markdown
# {project_name} -- EPIC-XX: {Epic Title} Functional Tests
Priority: {tier} | MVP: {Yes/No} | Stories: {N}

---

## US-XX-NN-TAG: {Story Title}

---
**TC_ID:** FTC_{EPIC}_{STORY}_{SEQ}
**Story:** {US-XX-NN-TAG}
**AC/Rule:** {AC #N | BR-{N} | [Assumption]}
**Type:** Positive / Negative / Boundary
**Tag:** [{BE}] / [{FE}] / [{DATA}]
**Priority:** P0 / P1 / P2
---
```

````gherkin
Feature: {Story Title} - Functional Verification

  Background:
    Given {precondition from story context}

  @{EPIC_ID} @{STORY_ID} @{type_tag} @{domain_tag}
  Scenario: FTC_XX_NN_SS - {Descriptive name}
    Given {specific precondition from AC}
    When {action from AC - declarative business language}
    Then {verification from AC's Then clause}
    And {additional verification}
````

### Gherkin Rules (from Phase A reference)
- NEVER summarize verification: "Then it works" → explicit Then per AC bullet
- NEVER use imperative steps: "click button" → "submit the form"
- NEVER skip business rules: every BR → at least one scenario
- Domain tag on TC MUST match story tag
- MVP epics: generate dependency/infrastructure failure scenarios
- Technology-neutral language in all steps

---

## File 3: FTC-AUDIT-{SESSION_ID}.md

```markdown
# {project_name} — FTC Session Audit
session: {SESSION_ID}
version: {NEW_VERSION}
mode: {BUILD | REPAIR}
scope: {target_epic | "All Epics"}
date: {ISO 8601}

---

## sources

| source | path | status |
|--------|------|--------|
| User Stories | {user_stories_path} | Loaded |
| Test Strategy | {test_strategy_path} | Loaded |
| MTP | {master_test_plan_path} | Loaded |
| PRD | {prd_path} | Loaded / Not provided |
| Epics | {epics_path} | Loaded |
| ADRs | {adrs_path} | Loaded / Not provided |

---

## generation_log

| epic | stories | tcs | positive | negative | boundary | mvp_depth | duration |
|------|---------|-----|----------|----------|----------|-----------|----------|

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
