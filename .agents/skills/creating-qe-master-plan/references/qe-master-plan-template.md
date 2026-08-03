# Agent-Native QE Master Test Plan Template

## Spec Contract — these are not suggestions

The skill ABORTS in Step 5 (Quality Validation Gate) when any rule below is violated.

### ALLOWED top-level sections (exactly these 9, lowercase snake_case, this order)
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

### PROHIBITED — DO NOT GENERATE
| Prohibited section | Belongs to |
|---|---|
| Executive Summary / Purpose / Introduction / Background | humanize-spec → executive_summary |
| `## 1. Scope`, `## 2. Risks`, any `## N. UPPERCASE` numbered narrative | use snake_case sections instead |
| Tool Selection Rationale (narrative) | structured `tool_classification` table inside `test_strategy` |
| Meeting Agenda / Stakeholder Communication | humanize-spec → governance |
| Process Log / Change Log | MTP-AUDIT-{SESSION_ID}.md |

### Hard rules
- **No prose.** Every section is structured data only.
- **No executive summaries.** No "this document provides…" paragraphs.
- **No narrative.** Outside fenced code blocks, no contiguous run of more than
  2 narrative lines (capital-letter start, period end, > 15 words each).
- **All items carry status.** `complete` | `pending` | `assumption`.
- **All pending items appear in open_questions.** Single registry, no scatter.
- **Source tags are mandatory.** No source → cannot be `complete`.
- **Zero Invention.** Every feature traces to an epic. Every risk traces to ADR/NFR/RSK.
- **Filename:** must match `^MTP-SPEC-[A-Za-z0-9_-]+\.md$`. AUDIT must match
  `^MTP-AUDIT-[A-Za-z0-9_-]+\.md$`. Anything else → ABORT.
- **Language:** Generate in DETECTED_LANGUAGE. Section headers in English always.

---

## Spec File Structure

```markdown
# {project_name} — QE Master Test Plan Spec
version: {NEW_VERSION}
session: {SESSION_ID}
mode: {BUILD | REPAIR}
date: {ISO 8601}
language: {DETECTED_LANGUAGE}
status: {draft | complete}
upstream_sources:
  prd: {prd_path}
  epics: {epics_path}
  adrs: {adrs_path | "not provided"}
  architecture: {target_architecture_path | "not provided"}

---

## scope_matrix

### in_scope

#### SF-01: {epic_title}
- epic_id: EPIC-XX
- priority_tier: {must_have | should_have | could_have}
- test_priority: {P0 | P1 | P2}
- fr_coverage: FR-XX, FR-YY
- test_approach: {functional + integration | API + performance | etc.}
- automation_mandate: {all_automated_ci | unit_integration_automated | unit_automated}
- status: complete
- source: epics/{epic_ref}

#### SF-02: {epic_title}
- epic_id: EPIC-XX
- priority_tier: {tier}
- test_priority: {priority}
- fr_coverage: FR-XX
- test_approach: {approach}
- automation_mandate: {mandate}
- status: complete
- source: epics/{epic_ref}

### enablers_spikes

#### ES-01: {title}
- source_id: {ENABLER-XX | SPIKE-XX}
- type: {enabler | spike}
- test_approach: {infrastructure_integration | poc_validation}
- status: complete
- source: epics/{ref}

### out_of_scope
- {item} | source: {ref} | rationale: {reason}
- {item} | source: {ref} | rationale: {reason}

### scope_verification
- total_epics: {N}
- in_scope_count: {N}
- out_of_scope_count: {N}
- coverage_check: {in_scope + out_of_scope == total_epics}

---

## risk_assessment

### adr_derived_risks

#### QR-001: {risk_description}
- source: ADR-NNN
- adr_decision: {decision_summary}
- category: {architecture | data | security | integration | performance}
- likelihood: {H | M | L}
- impact: {H | M | L}
- risk_level: {critical | high | medium | low}
- test_mitigation: {mitigation_approach}
- status: complete

#### QR-002: {risk_description}
- source: ADR-NNN
- adr_decision: {decision_summary}
- category: {category}
- likelihood: {L}
- impact: {L}
- risk_level: {level}
- test_mitigation: {approach}
- status: complete

### nfr_derived_risks

#### QR-NNN: {risk_description}
- source: NFR-XX
- nfr_category: {performance | security | availability | etc.}
- nfr_target: {quantitative_target | [PENDING INPUT - NFR Target]}
- test_type: {performance | security | load | etc.}
- pass_criteria: {measurable_criteria}
- status: {complete | pending}

### prd_risk_carryforward

#### QR-NNN: {prd_risk_as_qa_risk}
- source: RSK-XX
- prd_risk: {original_risk_description}
- qa_impact: {how_it_affects_testing}
- test_mitigation: {approach}
- status: complete

### risk_priority_matrix
- critical: {count} | response: automated_regression_ci_gate
- high: {count} | response: targeted_suite_sprint_level
- medium: {count} | response: exploratory_periodic_regression
- low: {count} | response: acceptance_criteria_coverage_only

---

## test_strategy

### test_levels

#### TL-01: unit
- scope: single_component_class
- responsibility: developer
- automation_target: "> 80%"
- tools_capability: unit_testing_framework
- status: complete

#### TL-02: integration
- scope: service_to_service_api_contracts
- responsibility: developer_qa
- automation_target: "> 70%"
- tools_capability: api_testing_framework, contract_testing
- status: complete

#### TL-03: system_e2e
- scope: full_user_workflows
- responsibility: qa
- automation_target: "> 50% critical paths"
- tools_capability: e2e_testing_framework
- status: complete

#### TL-04: performance
- scope: load_stress_endurance
- responsibility: qa_platform
- automation_target: key_scenarios
- tools_capability: performance_testing_tool
- status: complete

#### TL-05: security
- scope: vulnerability_penetration
- responsibility: security_qa
- automation_target: sast_dast_in_ci
- tools_capability: security_scanning_tool
- status: complete

#### TL-06: accessibility
- scope: wcag_compliance
- responsibility: qa
- automation_target: automated_checks
- tools_capability: accessibility_audit_tool
- status: {complete | assumption}

### test_types_per_priority
- P0_must_have: unit + integration + e2e + performance | automation: all_automated_ci
- P1_should_have: unit + integration + e2e | automation: unit_integration_automated
- P2_could_have: unit + exploratory | automation: unit_automated

### nfr_test_approach

#### NTA-01: {nfr_id}
- nfr_category: {category}
- nfr_target: {target | [PENDING INPUT]}
- test_approach: {approach}
- pass_criteria: {criteria}
- status: {complete | pending}

### automation_strategy
- pyramid: unit > integration > e2e
- ci_integration: {integration_points}
- regression_management: {approach}
- status: complete

---

## environment_map

### environments

#### ENV-01: {environment_name}
- purpose: {purpose}
- test_types: {unit, component | unit, integration, sast | e2e, performance, security | smoke, synthetic_monitoring}
- data_strategy: {synthetic | anonymized_production_like | production}
- access: {developer | automated | qa_devops | controlled}
- source: {architecture/{ref} | [Assumption: default environment]}
- status: {complete | assumption}

#### ENV-02: {environment_name}
- purpose: {purpose}
- test_types: {types}
- data_strategy: {strategy}
- access: {access}
- source: {ref}
- status: {complete | assumption}

### promotion_pipeline
- sequence: ENV-01 → ENV-02 → ENV-03 → ENV-04

#### gate: ENV-01 → ENV-02
- criteria: {gate_criteria}
- automated: {yes | no | partial}
- rollback: {strategy}

#### gate: ENV-02 → ENV-03
- criteria: {gate_criteria}
- automated: {yes | no | partial}
- rollback: {strategy}

#### gate: ENV-03 → ENV-04
- criteria: {gate_criteria}
- automated: {yes | no | partial}
- rollback: {strategy}

### service_environment_mapping
(if architecture available)
- SVC-XX: {env_01: deployed, env_02: deployed, env_03: deployed}
- SVC-YY: {env_01: deployed, env_02: deployed, env_03: mock}

---

## test_data_strategy

### data_categories
- synthetic: environments: [local, ci] | management: seed_scripts_factories
- anonymized: environments: [staging] | management: data_masking_pipeline
- production: environments: [production] | management: read_only_monitoring

### data_requirements_per_level
- unit: source: in_memory_fixtures | volume: minimal | refresh: per_test_run
- integration: source: synthetic_seeds | volume: moderate | refresh: per_deploy
- e2e: source: anonymized_subset | volume: production_like | refresh: weekly
- performance: source: scaled_synthetic | volume: high | refresh: per_test_cycle

### data_privacy
- pii_handling: {approach}
- masking_rules: {rules}
- retention_policy: {policy}
- regulatory_constraints: {from PRD or [PENDING]}
- status: {complete | pending | assumption}

---

## entry_exit_criteria

### phase_criteria

#### phase: {environment/phase_name}

entry:
- {prerequisite_1} | status: {required | recommended}
- {prerequisite_2} | status: required

exit:
- {quality_gate_1} | status: required
- {quality_gate_2} | status: required

gherkin_gate:
```gherkin
Feature: {Phase} Quality Gate

  Scenario: Gate passed
    Given all {phase} test suites have executed
    And code coverage exceeds {threshold}%
    And zero critical/high defects remain open
    When the quality gate review is conducted
    Then the build is promoted to {next_phase}

  Scenario: Gate failed
    Given {phase} test suites have executed
    But {N} critical defects remain open
    When the quality gate review is conducted
    Then the build is rejected
    And defects are triaged for resolution
```

### release_criteria
- p0_p1_suites: passing
- performance: within_slo | nfr_refs: NFR-XX, NFR-YY
- security_scan: clean
- stakeholder_signoff: {required | not_required}
- status: complete

---

## traceability_audit

### epic_coverage
- expected: {total_in_scope_epics}
- actual: {covered_count}
- percentage: {N}%
- status: {PASS | FAIL}
- gaps: [{epic_id: EPIC-XX, issue: not_in_scope_matrix}]

### adr_alignment
- expected: {total_adrs}
- actual: {adrs_with_risk_mapped}
- percentage: {N}%
- status: {PASS | FAIL | N/A}
- gaps: [{adr_id: ADR-NNN, issue: no_quality_risk_mapped}]

### nfr_coverage
- expected: {total_nfrs}
- actual: {nfrs_with_test_approach}
- percentage: {N}%
- status: {PASS | FAIL}
- gaps: [{nfr_id: NFR-XX, issue: no_test_approach}]

### environment_alignment
- architecture_envs: {count}
- mtp_envs: {count}
- status: {PASS | FAIL | N/A}
- gaps: [{env: {name}, issue: {missing | invented}}]

### prd_risk_carryforward
- expected: {total_prd_risks}
- actual: {risks_mapped}
- percentage: {N}%
- status: {PASS | FAIL}
- gaps: [{rsk_id: RSK-XX, issue: not_mapped}]

### out_of_scope_completeness
- wont_have_epics: {count}
- in_out_of_scope: {count}
- status: {PASS | FAIL}

### audit_summary
| check | expected | actual | status |
| epic_coverage | 100% | {N}% | {PASS/FAIL} |
| adr_alignment | 100% | {N}% | {PASS/FAIL/N/A} |
| nfr_coverage | 100% | {N}% | {PASS/FAIL} |
| env_alignment | match | {match/mismatch} | {PASS/FAIL/N/A} |
| prd_risk_carryforward | 100% | {N}% | {PASS/FAIL} |

overall_status: {PASS | FAIL}
fail_reasons: [{reason}]

---

## engineering_assumptions

### ASM-MTP-01: {assumption_description}
- section_affected: {section_name}
- rationale: {why_assumed}
- confidence: {high | medium | low}
- validation_needed: {what_stakeholder_must_confirm}
- status: assumption

---

## open_questions

### OQ-MTP-01: {question}
- source: {section_name}
- type: {missing_input | ambiguity | pending_decision}
- impact: {what_is_blocked_or_degraded}
- default_applied: {what_was_used_instead | none}
- status: pending

### OQ-MTP-02: {question}
- source: {section_name}
- type: {type}
- impact: {impact}
- default_applied: {default}
- status: pending
```

---

## Template Usage Notes

### For BUILD mode
Generate all sections sequentially. Each section feeds data to subsequent sections:
- scope_matrix → risk_assessment (scope_features inform risk context)
- risk_assessment → test_strategy (quality_risks inform test levels)
- test_strategy → environment_map (test_levels inform environment needs)
- environment_map → entry_exit_criteria (promotion pipeline defines phases)
- All sections → traceability_audit (validation of completeness)

### For REPAIR mode
Load existing spec. Apply directives to targeted sections only.
Re-run traceability_audit after any section repair.
Increment version (patch).
