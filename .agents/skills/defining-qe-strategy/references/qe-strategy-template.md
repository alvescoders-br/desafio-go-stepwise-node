# Agent-Native QE Strategy Spec Template

## Spec Contract — these are not suggestions

The skill ABORTS in Step 3 (Quality Validation Gate) when any rule below is violated.

### ALLOWED top-level sections (exactly these 9, exact names, this order)

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

### PROHIBITED — DO NOT GENERATE these sections

These belong to `humanize-spec` (the rendering profile reconstructs them). Any
of these in the spec body → ABORT:

| Prohibited section | Belongs to |
|---|---|
| Purpose / Strategy Purpose / 1. Purpose and Objectives | humanize-spec → overview |
| Strategic Objectives / Governing Principles | humanize-spec → overview |
| Strategy Scope (narrative) | structured equivalent: `scope_summary` |
| Test Design Techniques / Test Level Strategies / TLS-XX | structured equivalent: `pyramid_config` |
| Bounded Context Test Coverage (narrative) | inside `pyramid_config` |
| Tool Stack and Rationale (narrative) | structured equivalent: `tool_selections` |
| CI/CD Integration Strategy (narrative) | structured equivalent: `cicd_stages` |
| Defect Management Strategy / Test Metrics and Reporting | humanize-spec → cross_cutting_detail |
| Reporting & Notifications / Flaky Test Management | humanize-spec → cicd_detail |
| Traceability Strategy / Traceability Index (narrative) | inside `validation_summary` |
| Enhancement Suggestions / Next Meeting Agenda | humanize-spec → enhancement / agenda |
| Process Log / Change Log | STRATEGY-AUDIT-{SESSION_ID}.md |

### Hard rules
- **Section headings MUST be lowercase snake_case.** `## scope_summary` ✓.
  `## 1. PURPOSE AND OBJECTIVES` or `## Test Level Strategies` → ABORT.
- **No prose.** Every section is structured data only — tables, key:value, bullets.
- **No narrative paragraphs.** No "why this matters", motivational text,
  guiding principles paragraphs, "this document defines…" introductions.
- **All items carry status.** `complete` | `pending` | `assumption`.
- **All pending items appear in open_questions.** Single registry, no scatter.
- **Source tags are mandatory.** No source → cannot be `complete`.
- **Technology neutrality.** No tool names outside `tool_selections` (except
  tool-specific config that names the already-selected tool).
- **BE/FE slicing.** Every test assignment specifies `[ID]-BE` or `[ID]-FE`.
- **Gherkin for gates.** Every CI/CD gate and performance gate includes
  Gherkin (happy + unhappy paths).
- **Filename:** must match `^STRATEGY-SPEC-[A-Za-z0-9_-]+\.md$`.
  Anything else (e.g. `QTS-SPEC-*`, `qe-test-strategy.md`) → ABORT.
- **Language:** generate in DETECTED_LANGUAGE. Section headers in English always.

---

## Spec File Structure

```markdown
# {project_name} — QE Strategy Spec
version: {NEW_VERSION}
session: {SESSION_ID}
mode: {BUILD | REPAIR}
date: {ISO 8601}
language: {DETECTED_LANGUAGE}
mtp_source: {master_test_plan_path}
prd_source: {prd_path}
status: {draft | complete}

---

## scope_summary

- features_in_scope: {N}
- features_out_of_scope: {N}
- quality_risks: {N}
- environments: {N}
- test_levels: {N}
- services: {N} | source: {domain_boundaries | mtp_derived | assumption}
- mtp_ref: {master_test_plan_path}

---

## tool_selections

### evaluation_criteria
| criterion | weight | description |
|---|---|---|
| capability_fit | 30% | Covers required test types |
| tech_stack_compat | 25% | Works with ADR-decided technologies |
| team_expertise | 15% | Current team proficiency |
| cicd_integration | 15% | Pipeline-native support |
| cost_licensing | 10% | Open source vs commercial |
| community_ecosystem | 5% | Plugin availability, documentation |

### category: unit_be
- option_a: {tool} | score: {N}/5 | pros: {list} | cons: {list}
- option_b: {tool} | score: {N}/5 | pros: {list} | cons: {list}
- recommended: {tool} | score: {N}/5 | rationale: {why}
- adr_ref: {ADR-NNN | none}
- status: {complete | assumption}
- source: {ref}

### category: unit_fe
- option_a: {tool} | score: {N}/5 | pros: {list} | cons: {list}
- option_b: {tool} | score: {N}/5 | pros: {list} | cons: {list}
- recommended: {tool} | score: {N}/5 | rationale: {why}
- adr_ref: {ADR-NNN | none}
- status: {complete | assumption}
- source: {ref}

### category: api_integration
- option_a: {tool} | score: {N}/5 | pros: {list} | cons: {list}
- option_b: {tool} | score: {N}/5 | pros: {list} | cons: {list}
- recommended: {tool} | score: {N}/5 | rationale: {why}
- adr_ref: {ADR-NNN | none}
- status: {complete | assumption}
- source: {ref}

### category: e2e_fe
- option_a: {tool} | score: {N}/5 | pros: {list} | cons: {list}
- option_b: {tool} | score: {N}/5 | pros: {list} | cons: {list}
- recommended: {tool} | score: {N}/5 | rationale: {why}
- adr_ref: {ADR-NNN | none}
- status: {complete | assumption}
- source: {ref}

### category: performance
- option_a: {tool} | score: {N}/5 | pros: {list} | cons: {list}
- option_b: {tool} | score: {N}/5 | pros: {list} | cons: {list}
- recommended: {tool} | score: {N}/5 | rationale: {why}
- adr_ref: {ADR-NNN | none}
- status: {complete | assumption}
- source: {ref}

### category: sast
- option_a: {tool} | score: {N}/5 | pros: {list} | cons: {list}
- option_b: {tool} | score: {N}/5 | pros: {list} | cons: {list}
- recommended: {tool} | score: {N}/5 | rationale: {why}
- adr_ref: {ADR-NNN | none}
- status: {complete | assumption}
- source: {ref}

### category: dast
- option_a: {tool} | score: {N}/5 | pros: {list} | cons: {list}
- option_b: {tool} | score: {N}/5 | pros: {list} | cons: {list}
- recommended: {tool} | score: {N}/5 | rationale: {why}
- adr_ref: {ADR-NNN | none}
- status: {complete | assumption}
- source: {ref}

### category: contract
- option_a: {tool} | score: {N}/5 | pros: {list} | cons: {list}
- option_b: {tool} | score: {N}/5 | pros: {list} | cons: {list}
- recommended: {tool} | score: {N}/5 | rationale: {why}
- adr_ref: {ADR-NNN | none}
- status: {complete | assumption}
- source: {ref}

### category: accessibility
- option_a: {tool} | score: {N}/5 | pros: {list} | cons: {list}
- option_b: {tool} | score: {N}/5 | pros: {list} | cons: {list}
- recommended: {tool} | score: {N}/5 | rationale: {why}
- adr_ref: {ADR-NNN | none}
- status: {complete | assumption}
- source: {ref}

### tool_stack_summary
| category | selected_tool | scope | license | adr_ref |
|---|---|---|---|---|
| unit_be | {tool} | {scope} | {license} | {ADR-NNN | —} |
| unit_fe | {tool} | {scope} | {license} | {ADR-NNN | —} |
| api_integration | {tool} | {scope} | {license} | {ADR-NNN | —} |
| e2e_fe | {tool} | {scope} | {license} | {ADR-NNN | —} |
| performance | {tool} | {scope} | {license} | {ADR-NNN | —} |
| sast | {tool} | {scope} | {license} | {ADR-NNN | —} |
| dast | {tool} | {scope} | {license} | {ADR-NNN | —} |
| contract | {tool} | {scope} | {license} | {ADR-NNN | —} |
| accessibility | {tool} | {scope} | {license} | {ADR-NNN | —} |

---

## pyramid_config

### ratios
| level | target_pct | execution_time_budget | automation_target |
|---|---|---|---|
| unit | 60-70% | < 5 min | 100% |
| integration_api | 20-25% | < 15 min | > 90% |
| e2e_ui | 5-10% | < 30 min | > 50% critical paths |
| manual_exploratory | 5% | as_needed | 0% |
- adjustments: {project-specific ratio adjustments with rationale}
- status: {complete | assumption}
- source: {ref}

### SVC-XX: {service_name}

#### [{SVC-XX}-BE] backend
| level | scope | tool_category | automation | coverage_target | status |
|---|---|---|---|---|---|
| unit | domain logic, business rules, repositories | unit_be | automated | > 80% | {status} |
| integration | API contracts, service-to-service | api_integration | automated | > 70% | {status} |
| contract | provider/consumer contracts | contract | automated | all cross-service APIs | {status} |
- source: {ref}

#### [{SVC-XX}-FE] frontend
| level | scope | tool_category | automation | coverage_target | status |
|---|---|---|---|---|---|
| unit | components, state management | unit_fe | automated | > 80% | {status} |
| e2e | critical user journeys | e2e_fe | automated | P0 scenarios | {status} |
| visual | regression against baselines | e2e_fe | automated | key pages | {status} |
| accessibility | WCAG compliance | accessibility | automated | all pages | {status} |
- source: {ref}
- note: only for user-facing services

### isolation_strategy
- be_unit: mock external services, in-memory stores
- be_integration: real stores, mock external services
- fe_unit: mock API responses, component isolation
- fe_e2e: real backend
- fe_dom: DOM isolation for component tests
- status: {complete | assumption}
- source: {ref}

---

## data_strategy

### ENV-XX: {environment_name}
- data_source: {synthetic_fixtures | synthetic_generated | anonymized_production | real}
- volume: {minimal | moderate | production_like | full}
- refresh: {per_test_run | per_pipeline_run | weekly | na}
- provisioning: {seed_scripts | data_generators | masking_pipeline | monitoring_only}
- privacy_level: {none | controlled | restricted}
- status: {complete | assumption}
- source: {ref}

### per_test_level
| level | data_approach | state_management | cleanup |
|---|---|---|---|
| unit | in-memory fixtures, mocks | isolated per test | automatic (GC) |
| integration | seed scripts, test containers | reset between suites | teardown scripts |
| e2e | pre-provisioned scenarios | dedicated test accounts | post-suite cleanup |
| performance | scaled synthetic datasets | pre-loaded | volume reset |
- status: {complete | assumption}
- source: {ref}

### privacy_compliance
- pii_masking_approach: {description}
- data_retention: {policy}
- regulatory_constraints: {from PRD | none | [PENDING]}
- status: {complete | pending | assumption}
- source: {ref}

---

## performance_gates

### GATE-XX: {nfr_id} — {metric_name}
- nfr_id: {NFR-XX}
- metric: {response_time_p99 | throughput | error_rate | ...}
- slo_target: {value with unit}
- gate_threshold: {value with margin}
- measurement_tool_category: performance
- test_type: {load | stress | endurance | spike}
- status: {complete | assumption}
- source: {ref}

### performance_test_types
| type | purpose | when | duration | pass_criteria |
|---|---|---|---|---|
| load | verify SLO under expected load | pre-release | 15-30 min | all SLOs met |
| stress | find breaking point | monthly / major change | 30-60 min | graceful degradation |
| endurance | memory leaks, connection pool drain | pre-release | 2-8 hours | no degradation |
| spike | recovery from sudden load increase | quarterly | 15 min | recovery < threshold |

### per_service_profile
| service | critical_operations | expected_load | slo | test_approach | slice |
|---|---|---|---|---|---|
| {SVC-XX} | {ops} | {load} | {slo} | {approach} | BE |
- note: FE performance measured via Core Web Vitals separately

### fe_performance_budget
| metric | budget | measurement |
|---|---|---|
| lcp | < 2.5s | lighthouse / lab |
| fid | < 100ms | real user monitoring |
| cls | < 0.1 | lighthouse |
| bundle_size | < {threshold}KB | build-time check |
- status: {complete | assumption}
- source: {ref}

### gherkin_gate: performance

```gherkin
Feature: Performance Quality Gate

  Scenario: Performance gate passes
    Given the load test has completed with {N} virtual users
    And all API response times are below SLO thresholds
    And error rate is below {threshold}%
    When the performance gate is evaluated
    Then the build is promoted to next environment

  Scenario: Performance gate fails
    Given the load test has completed
    But p99 response time exceeds SLO by more than {margin}%
    When the performance gate is evaluated
    Then the build is blocked
    And a performance regression ticket is created
```

---

## cicd_stages

### STAGE-XX: {stage_name}
- trigger: {push_pr | merge_main | integration_pass | manual}
- tests_executed: {test types with BE/FE slice}
- gate_criteria: {summary}
- duration_target: {time}
- automated: {yes | partial | no}
- status: {complete | assumption}
- source: {ref}

#### gherkin_gate: {stage_name}

```gherkin
Feature: {stage_name} Pipeline Gate

  Scenario: {stage_name} gate passes
    Given all {stage} test suites have completed
    And code coverage is at or above {threshold}%
    And zero critical defects are open
    And {stage-specific criterion}
    When the pipeline gate evaluates
    Then the build proceeds to {next_stage}

  Scenario: {stage_name} gate fails
    Given {stage} test suites have completed
    But {failure condition}
    When the pipeline gate evaluates
    Then the build is blocked at {stage}
    And {remediation action}
```

### parallelization
- parallel_suites: {which test types run in parallel}
- sequential_suites: {which must be sequential}
- sharding: {approach for large suites}
- resource_allocation: {per stage}
- status: {complete | assumption}
- source: {ref}

---

## cross_cutting

### security
| test_type | scope | tool_category | frequency | gate | status |
|---|---|---|---|---|---|
| sast | source code vulnerabilities | sast | every commit | block on critical/high | {status} |
| dast | runtime vulnerability scanning | dast | staging deploy | block on critical | {status} |
| dependency_scan | known CVEs in dependencies | sast | every build | block on critical | {status} |
| penetration | manual security assessment | manual | quarterly / pre-release | report-based | {status} |
- source: {ref}

### accessibility
| standard | scope | tool_category | automation | gate | status |
|---|---|---|---|---|---|
| WCAG 2.1 AA | all user-facing pages | accessibility | automated in CI | block on violations | {status} |
- applies_to: [{SVC-XX}-FE slices]
- source: {ref}

### contract_testing
| pattern | scope | tool_category | when | status |
|---|---|---|---|---|
| consumer-driven | API contracts between services | contract | integration stage | {status} |
- applies_to: [{SVC-XX}-BE with cross-service dependencies]
- source: {ref}

### chaos_resilience
| experiment | target | expected_behavior | frequency | status |
|---|---|---|---|---|
| service_shutdown | {SVC-XX} | graceful degradation, no data loss | pre-release | {status} |
| network_partition | inter-service | circuit breaker activation | monthly | {status} |
| resource_exhaustion | memory/CPU | auto-scaling trigger | quarterly | {status} |
- condition: only if quality_risks includes availability/resilience risks
- source: {ref}

---

## validation_summary

| check | expected | actual | status |
|---|---|---|---|
| mtp_scope_coverage | 100% | {pct}% | {PASS | FAIL} |
| mtp_risk_coverage | 100% | {pct}% | {PASS | FAIL} |
| nfr_test_coverage | 100% | {pct}% | {PASS | FAIL} |
| tool_completeness | all levels | {pct}% | {PASS | FAIL} |
| be_fe_slicing | 0 hybrids | {count} hybrids | {PASS | FAIL} |
| gherkin_gates | all stages | {pct}% | {PASS | FAIL} |
| tech_neutrality | 0 violations | {count} violations | {PASS | FAIL} |
| source_fidelity | 0 violations | {count} violations | {PASS | FAIL} |
- overall_status: {PASS | FAIL}
- fail_reasons: {list if FAIL}

---

## open_questions

### pending_inputs
| id | description | impact | source |
|---|---|---|---|
| OQ-XX | {missing input description} | {what strategy sections are affected} | {which upstream artifact} |

### coverage_gaps
| id | type | ref_id | description | affected_section |
|---|---|---|---|---|
| GAP-XX | {scope_feature | quality_risk | nfr} | {feature/risk/NFR ID} | {what is missing} | {section} |

### assumptions_to_validate
| id | assumption | section | rationale | confidence | validation_needed |
|---|---|---|---|---|---|
| ASM-XX | {assumption text} | {section} | {why assumed} | {high | medium | low} | {what to validate} |

### upstream_gaps_carried_forward
| id | origin | description | impact_on_strategy |
|---|---|---|---|
| UG-XX | {MTP | PRD} | {gap description} | {how it affects strategy} |

### summary
- total_pending: {N}
- total_gaps: {N}
- total_assumptions: {N}
- total_upstream_gaps: {N}
- overall_status: {clean | has_gaps | has_critical_gaps}
```

---

## Generation Rules

### Section Ordering
Generate sections in this order (matches dependency chain):
1. `scope_summary` — overview, no dependencies
2. `tool_selections` — needs quality_risks, test_levels, services
3. `pyramid_config` — needs tool_selections
4. `data_strategy` — needs environment_map, scope_features
5. `performance_gates` — needs prd_nfr_ids, quality_risks
6. `cicd_stages` — needs tool_selections, pyramid_config, performance_gates
7. `cross_cutting` — needs scope_features, quality_risks, tool_selections
8. `validation_summary` — needs all above (audit consumer)
9. `open_questions` — consolidation pass (always last)

### REPAIR Mode Mechanics
- Load existing spec → identify sections targeted by REPAIR_DIRECTIVES
- Apply directives surgically to targeted sections only
- Preserve untargeted sections exactly
- Re-run validation_summary after all repairs
- Re-consolidate open_questions
- Increment patch version

### Tool Selection Categories
Derive from STRATEGY_CONTEXT.test_levels. Standard set:
unit_be, unit_fe, api_integration, e2e_fe, performance, sast, dast, contract, accessibility.
Add or remove categories based on actual test levels from MTP.

### Service-Level Configuration
- IF services available from domain_boundaries: per-service entries with SVC-XX IDs
- ELSE: generic entries per test priority tier (P0/P1/P2), status: assumption
- Always split into BE and FE slices

### Conditional Sections
- `chaos_resilience`: only generated if quality_risks includes availability/resilience risks
- `per_service_profile` (in performance): only if services available
- `fe_performance_budget`: only if FE services exist

### Removed Fields (reconstructed by humanize-spec)
These fields existed in v2.0.1 but are not in the agent-native spec.
The rendering profile derives them from spec data:
| Removed Field | Derivation Source | Rendering Profile Section |
|---|---|---|
| Strategy Purpose (prose) | scope_summary + mtp_source | overview |
| Guiding Principles (table) | Fixed content | overview |
| Scope Reference (narrative) | scope_summary counts | overview |
| Reporting & Notifications | cicd_stages | cicd_detail |
| Flaky Test Management | Fixed content | cross_cutting_detail |
| Enhancement Suggestions | open_questions | enhancement |
| Next Meeting Agenda | open_questions | agenda |
| Process Log | AUDIT file | governance |
| Change Log | AUDIT file | governance |
