# Agent-Native Refactoring Research Spec Template

## Template Rules
- **No prose.** Every section is structured data only.
- **No narrative.** No "why this matters", no motivational text, no context paragraphs.
- **No formatting for humans.** No prominent text, no callouts, no visual emphasis.
- **All items carry status.** `complete` | `pending` | `assumption`.
- **All pending items appear in open_questions.** Single registry, no scatter.
- **Source tags are mandatory.** No source → cannot be `complete`.
- **Language:** Generate in DETECTED_LANGUAGE. Section headers in English always.
- **Refactoring type gating:** Sections marked with `[version_upgrade]`, `[structural]`, or `[combined]` indicate when they are active. `combined` activates all.

---

## Spec File Structure

```markdown
# {project_name} — Refactoring Research Spec
version: {NEW_VERSION}
session: {SESSION_ID}
mode: {BUILD | REPAIR}
date: {ISO 8601}
language: {DETECTED_LANGUAGE}
refactoring_type: {version_upgrade | structural | combined}
source_path: {source_path}
migration_spec_path: {migration_spec_path}
migration_guides_path: {migration_guides_path | "not provided"}
architecture_notes_path: {architecture_notes_path | "not provided"}
source_version: {REFACTOR_CONTEXT.source_version}
target_version: {REFACTOR_CONTEXT.target_version}
migration_type: {language_version | framework | runtime | library | build_system | multi}
refactor_contract_mode: {structured | partial | unstructured}
input_hashes:
  content_hash: {sha256:<64 lowercase hex> | invalid | N/A}
  hash_status: {match | mismatch_accepted | mismatch_blocked | not_verified | N/A}
status: {draft | complete}

---

## scope_summary

### migration_overview
- source_platform: {REFACTOR_CONTEXT.source_version}
- target_platform: {REFACTOR_CONTEXT.target_version}
- refactoring_type: {version_upgrade | structural | combined}
- migration_type: {language_version | framework | runtime | library | build_system | multi}
- intermediate_stops: {list | "Direct migration"}
- primary_driver: {EOL | Performance | Security | New Features | Compliance | Decoupling}
- source: {migration_spec_path}
- status: {complete | pending}

### input_contract
| field | value | source | status |
|-------|-------|--------|--------|
| contract_mode | {structured | partial | unstructured} | {migration_spec_path} | complete |
| content_hash | {sha256:<64 lowercase hex> | invalid | N/A} | {migration_spec_path} | {complete | pending} |
| hash_format | {valid_sha256 | invalid | N/A} | {migration_spec_path} | {complete | pending} |
| hash_status | {match | mismatch_accepted | mismatch_blocked | not_verified | N/A} | {migration_spec_path} | {complete | pending} |
| literal_refs | {LIT-XX list | N/A} | {migration_spec_path} | {complete | pending} |
| fallback_refs | {PI/OQ/ASM list | N/A} | {migration_spec_path} | {complete | pending} |

### accepted_hash_overrides
| artifact | declared_hash | observed_hash | verification_result | decision |
|----------|---------------|---------------|---------------------|----------|
| {Migration spec upstream | N/A} | {sha256:<64 lowercase hex> | N/A} | {sha256:<64 lowercase hex> | N/A} | {all recorded dependencies still present identically | not_verified | N/A} | {accepted in this research audit only | N/A} |

### goals
- {goal 1} | source: {ref} | status: {complete | pending}
- {goal 2} | source: {ref} | status: {complete | pending}
- [PENDING: goals] | status: pending

### constraints
- {constraint 1} | source: {ref} | status: {complete | pending}
- [PENDING: constraints] | status: pending

### exclusions
- {exclusion 1} | source: {ref} | status: {complete | pending}
- [PENDING: exclusions] | status: pending

### risk_profile

| factor | level | rationale | source | status |
|--------|-------|-----------|--------|--------|
| API Breaking Changes | {Low/Med/High/Critical} | {based on version distance} | {ref} | {complete | assumption} |
| Dependency Compatibility | {Low/Med/High/Critical} | {based on dep count/age} | {ref} | {complete | assumption} |
| Build System Impact | {Low/Med/High/Critical} | {based on build tool} | {ref} | {complete | assumption} |
| Runtime Behavioral Changes | {Low/Med/High/Critical} | {based on known shifts} | {ref} | {complete | assumption} |
| Test Infrastructure | {Low/Med/High/Critical} | {based on test compat} | {ref} | {complete | assumption} |
| Overall | {Low/Med/High/Critical} | {weighted assessment} | {ref} | {complete | assumption} |

### complexity

| factor | rating | evidence | source | status |
|--------|--------|----------|--------|--------|
| Version Distance | {Low/Med/High} | {N major versions apart} | {ref} | {complete | assumption} |
| Codebase Size | {Low/Med/High} | {approximate scope} | {ref} | {complete | assumption} |
| Dependency Graph | {Low/Med/High} | {N deps, age distribution} | {ref} | {complete | assumption} |
| Reflection/Serialization | {Low/Med/High} | {detected patterns} | {ref} | {complete | assumption} |
| Custom Extensions | {Low/Med/High} | {custom plugins, annotations} | {ref} | {complete | assumption} |
| Overall | {Low/Med/High} | {weighted assessment} | {ref} | {complete | assumption} |

### phase_complexity

| phase | complexity | risk_level |
|-------|------------|------------|
| Research & Planning | {LOW/MEDIUM/HIGH} | {LOW/MEDIUM/HIGH} |
| Build System & Dependencies | {LOW/MEDIUM/HIGH} | {LOW/MEDIUM/HIGH} |
| Code Transformations | {LOW/MEDIUM/HIGH} | {LOW/MEDIUM/HIGH} |
| Testing & Validation | {LOW/MEDIUM/HIGH} | {LOW/MEDIUM/HIGH} |
| Stabilization & Rollout | {LOW/MEDIUM/HIGH} | {LOW/MEDIUM/HIGH} |

---

## current_state_analysis

### tech_stack

| layer | technology | version | migration_sensitive | source | status |
|-------|-----------|---------|---------------------|--------|--------|
| Language | {e.g., Java} | {e.g., 1.8.0_362} | YES | {source_path} | complete |
| Framework | {e.g., Spring Boot} | {e.g., 2.7.18} | YES | {source_path} | complete |
| Build | {e.g., Maven} | {e.g., 3.8.7} | YES | {source_path} | complete |
| Test | {e.g., JUnit} | {e.g., 4.13.2} | {YES/NO} | {source_path} | complete |

### project_structure
{Directory tree of relevant areas — only paths verified against source}

### deprecated_apis

| pattern | files | count | risk | source | status |
|---------|-------|-------|------|--------|--------|
| {e.g., javax.* packages} | {file:lines} | {N} | {severity} | {source_path} | complete |

### reflection_usage

| pattern | files | count | risk | source | status |
|---------|-------|-------|------|--------|--------|
| {e.g., setAccessible(true)} | {file:lines} | {N} | {severity} | {source_path} | complete |

### serialization_usage

| pattern | files | count | risk | source | status |
|---------|-------|-------|------|--------|--------|
| {e.g., ObjectInputStream} | {file:lines} | {N} | {severity} | {source_path} | complete |

### internal_apis

| pattern | files | count | risk | source | status |
|---------|-------|-------|------|--------|--------|
| {e.g., sun.misc.Unsafe} | {file:lines} | {N} | {severity} | {source_path} | complete |

### version_features

| feature | status_in_target | files | action_needed | source | status |
|---------|------------------|-------|---------------|--------|--------|
| {e.g., SecurityManager} | Removed in Java 17 | {files} | Remove usage | {ref} | complete |

### module_system
- present: {YES | NO | Partial}
- module_info_files: {list | "None"}
- package_structure: {description}
- classpath_setup: {description}
- source: {source_path}
- status: {complete | pending}

### external_integrations

| integration | protocol | version_sensitive | source | status |
|-------------|----------|-------------------|--------|--------|
| {e.g., REST API v2} | {HTTP/gRPC/AMQP} | {YES/NO} | {source_path} | complete |

---

## compatibility_analysis
[version_upgrade, combined]

### breaks

| id | category | api_or_feature | introduced_in | removed_in | replacement | files_affected | severity | source | status |
|----|----------|---------------|---------------|-----------|-------------|----------------|----------|--------|--------|
| BREAK-001 | removed_api | {e.g., javax.xml.bind} | {deprecated_in} | {removed_in} | {replacement} | {files} | {Critical/High/Medium/Low} | {guide/codebase/changelog} | complete |
| BREAK-002 | behavioral | {e.g., String.split()} | {changed_in} | — | — | {files} | {severity} | {ref} | complete |
| BREAK-003 | module_restriction | {e.g., reflective access} | {restricted_in} | — | {alternative} | {files} | {severity} | {ref} | complete |
| BREAK-004 | compiler_language | {e.g., sealed keyword} | {introduced_in} | — | — | {files} | {severity} | {ref} | complete |
| BREAK-005 | security_crypto | {e.g., TLS 1.0 disabled} | {version} | — | — | {files} | {severity} | {ref} | complete |
| BREAK-006 | deprecated_removed | {e.g., Nashorn} | {deprecated_in} | {removed_in} | {replacement} | {files} | {severity} | {ref} | complete |

### version_map
[version_upgrade, combined — skip if structural only]

| version_boundary | break_ids | critical_count |
|-----------------|-----------|----------------|
| {8→11} | BREAK-001, BREAK-002 | {N} |
| {11→17} | BREAK-003 | {N} |
| {17→21} | BREAK-004 | {N} |
| {21→23} | BREAK-005 | {N} |

---

## coupling_analysis
[structural, combined — skip if version_upgrade only]

### module_coupling

| module_a | module_b | coupling_type | direction | strength | files | source | status |
|----------|----------|--------------|-----------|----------|-------|--------|--------|
| {module} | {module} | {runtime/compile/data} | {A→B/B→A/bidirectional} | {tight/moderate/loose} | {files} | {source_path} | complete |

### coupling_hotspots

| hotspot | modules_affected | coupling_count | risk | refactoring_target | source | status |
|---------|-----------------|----------------|------|-------------------|--------|--------|
| {class/package} | {N} | {N} | {High/Medium/Low} | {YES/NO} | {source_path} | complete |

### target_architecture
- current_modules: {N}
- target_modules: {N}
- modules_to_extract: {list}
- modules_to_merge: {list}
- circular_dependencies: {list | "None detected"}
- source: {migration_spec_path}
- status: {complete | pending}

---

## dependency_migration_matrix

### dependencies

| id | group_artifact | current_version | target_compatible_version | status_flag | action | risk | notes | source | status |
|----|---------------|-----------------|--------------------------|-------------|--------|------|-------|--------|--------|
| DEP-001 | {e.g., org.springframework:spring-core} | {5.3.31} | {6.1.x} | needs_bump | Update to 6.1.x | {High/Medium/Low} | {e.g., Spring Boot 3.x requires Spring 6} | {source_path} | complete |
| DEP-002 | {e.g., javax.servlet:javax.servlet-api} | {4.0.1} | — | needs_replacement | Replace with jakarta.servlet-api 6.0.x | High | {javax→jakarta} | {ref} | complete |
| DEP-003 | {e.g., commons-io:commons-io} | {2.11.0} | {2.11.0} | compatible | No change | Low | — | {source_path} | complete |
| DEP-004 | {e.g., custom:internal-lib} | {1.0.0} | — | unknown | [Compatibility unknown — test required] | — | — | {source_path} | pending |

### transitive_conflicts

| primary_dependency | conflict_with | conflict_version | resolution | source | status |
|-------------------|--------------|-----------------|------------|--------|--------|
| {dep} | {transitive dep} | {conflicting version} | {resolution strategy} | {ref} | complete |

### migration_order
- step_1: {group of deps that must move together} | rationale: {why}
- step_2: {next group} | depends_on: step_1 | rationale: {why}

---

## build_system_impact

### tool

| aspect | current | required_for_target | action | source | status |
|--------|---------|-------------------|--------|--------|--------|
| Build Tool Version | {e.g., Maven 3.8.7} | {e.g., Maven 3.9+} | {Upgrade/No change} | {source_path} | complete |
| Wrapper Version | {if applicable} | {required} | {action} | {source_path} | complete |

### plugins

| plugin | current_version | target_compatible | action | notes | source | status |
|--------|----------------|-------------------|--------|-------|--------|--------|
| {e.g., maven-compiler-plugin} | {3.10.1} | {3.12+} | Bump | {source/target changes} | {source_path} | complete |

### compiler

| setting | current | required | file | source | status |
|---------|---------|----------|------|--------|--------|
| source level | {1.8} | {23} | {pom.xml} | {source_path} | complete |
| target level | {1.8} | {23} | {pom.xml} | {source_path} | complete |
| add-opens flags | {none} | {list if needed} | {build file} | {ref} | {complete | pending} |

### cicd

| pipeline_file | change_needed | description | source | status |
|--------------|---------------|-------------|--------|--------|
| {e.g., Jenkinsfile} | JDK image | Update base image | {source_path} | complete |

### custom_scripts

| script | change | rationale | source | status |
|--------|--------|-----------|--------|--------|
| {script path} | {change needed} | {why} | {source_path} | complete |

### packaging

| aspect | current | required | source | status |
|--------|---------|----------|--------|--------|
| {e.g., JAR manifest} | {current config} | {required config} | {source_path} | complete |

---

## migration_sequence

### strategy
- approach: {Direct | Staged | Strangler-fig | Branch-by-abstraction}
- rationale: {structured reason — from risk profile and constraints}
- source: {ref}
- status: {complete | assumption}

### stages

#### STAGE-01: {source} → {intermediate_1}
- from: {version}
- to: {version}
- focus: {primary focus of this stage}
- complexity: {LOW/MEDIUM/HIGH}
- prerequisites:
  - {prerequisite 1}
  - {prerequisite 2}
- steps:
  - {step 1 — concrete action}
  - {step 2 — concrete action}
- breaks_addressed: BREAK-001, BREAK-002
- validation:
  - {checkpoint 1 — e.g., "Application compiles with {version} compiler"}
  - {checkpoint 2 — e.g., "All unit tests pass"}
- rollback: {how to revert this stage}
- risk: {top risk} | mitigation: {mitigation strategy}
- source: {ref}
- status: {complete | pending}

#### STAGE-02: {intermediate_1} → {intermediate_2}
{Same structure as STAGE-01}

#### STAGE-N: {intermediate_N} → {target}
{Same structure as STAGE-01}

### cross_dependencies

| stage | depends_on | parallelizable_with | notes |
|-------|-----------|---------------------|-------|
| STAGE-02 | STAGE-01 | — | {dependency reason} |

---

## code_transformation_catalog

### transformations

#### TRANSFORM-001: {Name}
- addresses: BREAK-{XXX}
- category: {namespace | api_replacement | pattern_change | configuration | behavioral}
- automatable: {YES — regex/IDE refactor | Partial — needs review | NO — semantic change}
- files: {list of affected files}
- before: |
  ```{language}
  {exact current code pattern from codebase}
  ```
- after: |
  ```{language}
  {transformed code pattern}
  ```
- notes: {edge cases, gotchas, manual verification needed}
- source: {ref}
- status: complete

#### TRANSFORM-002: {Name}
{Same structure}

### execution_order

| order | transform_id | depends_on | stage |
|-------|-------------|-----------|-------|
| 1 | TRANSFORM-001 | — | STAGE-01 |
| 2 | TRANSFORM-003 | TRANSFORM-001 | STAGE-01 |

### manual_interventions

| transform_id | reason | guidance | source | status |
|--------------|--------|----------|--------|--------|
| TRANSFORM-0XX | {why it cannot be automated} | {developer guidance} | {ref} | complete |

---

## acceptance_criteria

### parity

| id | area | criterion | verification_method | source | status |
|----|------|-----------|-------------------|--------|--------|
| AC-P-001 | {e.g., User authentication} | {e.g., Login flow produces identical tokens} | {e.g., Integration test} | {ref} | complete |

### new_capability
[version_upgrade, combined — optional for structural]

| id | capability | criterion | verification_method | source | status |
|----|-----------|-----------|-------------------|--------|--------|
| AC-N-001 | {e.g., Virtual threads} | {e.g., Thread pool supports virtual threads} | {e.g., Load test} | {ref} | {complete | pending} |

### non_functional

| id | category | criterion | threshold | verification | source | status |
|----|----------|-----------|-----------|-------------|--------|--------|
| AC-NF-001 | Performance | {e.g., Startup time} | {e.g., ≤ baseline + 10%} | {benchmark} | {ref} | complete |
| AC-NF-002 | Security | {e.g., No new CVEs} | zero | {dep scan} | {ref} | complete |

### definition_of_done
- [ ] Application compiles on target version without errors
- [ ] All existing unit tests pass (≥ pre-migration pass rate)
- [ ] All existing integration tests pass
- [ ] All functional parity criteria verified
- [ ] No new runtime warnings related to deprecated APIs
- [ ] Dependency scan shows no new critical/high CVEs
- [ ] Performance benchmarks within thresholds
- [ ] CI/CD pipeline runs green on target version
- [ ] Rollback procedure tested and documented

---

## test_strategy

### infrastructure

| component | current | post_migration | action | source | status |
|-----------|---------|---------------|--------|--------|--------|
| Test Framework | {e.g., JUnit 4.13} | {e.g., JUnit 5.10} | {Bump/Replace} | {source_path} | complete |
| Mocking Library | {e.g., Mockito 3.x} | {e.g., Mockito 5.x} | {action} | {source_path} | complete |
| Test Runner | {e.g., Surefire 2.x} | {e.g., Surefire 3.x} | {action} | {source_path} | complete |

### existing_tests

| category | tests_affected | migration_action | source | status |
|----------|---------------|-----------------|--------|--------|
| {e.g., JUnit 4 annotations} | {N tests} | {e.g., @Before→@BeforeEach} | {source_path} | complete |

### new_tests

| id | purpose | type | covers_ac | source | status |
|----|---------|------|-----------|--------|--------|
| NEW-T-001 | {e.g., Verify javax→jakarta} | {Unit/Integration} | AC-P-001 | {ref} | complete |

### regression_plan

| stage | test_suites | pass_criteria | source | status |
|-------|------------|--------------|--------|--------|
| STAGE-01 | {suites} | {criteria} | {ref} | complete |

### benchmarks

| benchmark | tool | metric | pre_migration_baseline | post_migration_target | source | status |
|-----------|------|--------|----------------------|----------------------|--------|--------|
| {e.g., Startup time} | {e.g., time java -jar} | {seconds} | {capture before} | {≤ baseline + 10%} | {ref} | complete |

### commands

| action | command | source | status |
|--------|---------|--------|--------|
| Run unit tests | {exact command} | {source_path} | complete |
| Run integration tests | {exact command} | {source_path} | complete |
| Run with compat flags | {command with --add-opens} | {ref} | {complete | pending} |
| Performance benchmark | {command} | {ref} | {complete | pending} |

---

## validations

| check | result | details |
|-------|--------|---------|
| Codebase Fidelity | {PASS/FAIL} | {N file references verified} |
| Version Consistency | {PASS/FAIL} | {N version references verified} |
| Breaking Change Coverage | {PASS/FAIL} | {N breaks traced, M from guide covered} |
| Dependency Matrix Completeness | {PASS/FAIL} | {N/total deps covered} |
| Migration Sequence Validity | {PASS/FAIL} | {N stages, prerequisites satisfied} |
| Transformation ↔ Break Alignment | {PASS/FAIL} | {N transforms linked, M critical/high have transforms} |
| AC Coverage | {PASS/FAIL} | {N functional areas with parity criteria} |
| Anti-Fade | {PASS/FAIL} | {scope_summary vs test_strategy depth comparison} |
| Cross-Section Consistency | {PASS/FAIL} | {session_id, versions consistent} |
| Count Verification | {PASS/FAIL} | {all summary counts match actual items} |
| Refactor Contract Mode | {PASS/FAIL} | mode={structured | partial | unstructured}; unstructured accepted |
| Partial Cross-Check | {PASS/FAIL | N/A} | discrepancies={N} |
| Hash Forward Verification | {PASS/FAIL | N/A} | valid_sha256={yes | no}; accepted_hash_overrides={N}; blocked={N} |
| Auth Security Defaults | {PASS/FAIL | N/A} | reset_tokens_hashed={yes | no | N/A}; oauth_provider_allow_list={yes | no | N/A} |

---

## open_questions

### pending_inputs

| id | affected_ids | blocking | type | section | item_id | field | impact | fallback_behavior | source_ref |
|----|--------------|----------|------|---------|---------|-------|--------|-------------------|------------|
| PI-01 | {BREAK-XXX | DEP-XXX | TRANSFORM-XXX | AC-XXX | all | N/A} | {yes | no} | missing | {section} | {item_id} | {field} | {impact on downstream} | {fallback or BLOCKED} | {migration_spec_path} |

### evidence_gaps

| id | affected_ids | type | section | item_id | gap | required_evidence | decision |
|----|--------------|------|---------|---------|-----|-------------------|----------|
| EG-01 | {BREAK-XXX | DEP-XXX | TRANSFORM-XXX | AC-XXX | LIT-XX | all | N/A} | {missing_source | structured_discrepancy | invalid_hash | hash_dependency_gap | auth_security_gap | compatibility_unknown} | compatibility_analysis | BREAK-0XX | [Needs verification] | Confirm in migration guide | {accepted | carried_forward | blocks} |
| EG-02 | {DEP-XXX | all | N/A} | compatibility_unknown | dependency_migration_matrix | DEP-0XX | [Compatibility unknown] | Test against target version | {accepted | carried_forward | blocks} |

### assumptions_to_validate

| id | affected_ids | blocking | assumption | impact_if_wrong | validation_method | fallback_behavior | source_ref |
|----|--------------|----------|------------|-----------------|-------------------|-------------------|------------|
| ASM-01 | {BREAK-XXX | DEP-XXX | TRANSFORM-XXX | AC-XXX | all | N/A} | {yes | no} | {statement} | {consequence} | {how to confirm/deny} | {fallback or BLOCKED} | {migration_spec_path} |

### upstream_gaps_carried_forward

| id | affected_ids | blocking | source_artifact | gap | impact_on_spec | fallback_behavior |
|----|--------------|----------|----------------|-----|----------------|-------------------|
| UG-01 | {BREAK-XXX | DEP-XXX | TRANSFORM-XXX | AC-XXX | all | N/A} | {yes | no} | {migration_spec} | {unresolved item from migration spec} | {which sections affected} | {fallback or BLOCKED} |

### summary
- total_breaking_changes: {N}
- total_dependencies: {N}
- total_transformations: {N}
- migration_stages: {N}
- ac_parity: {N}
- ac_new_capability: {N}
- tests_to_write: {N}
- tests_to_update: {N}
- affected_files: {N}
- pending_inputs: {N}
- evidence_gaps: {N}
- assumptions: {N}
- upstream_gaps: {N}
- overall_risk: {Low/Med/High/Critical}
- overall_complexity: {Low/Med/High}
- status: {draft | complete}
```

---

## Generation Rules

### Section Ordering
Generate sections in the order shown above. This order reflects dependency flow:
scope_summary → current_state_analysis → compatibility_analysis → coupling_analysis →
dependency_migration_matrix → build_system_impact → migration_sequence →
code_transformation_catalog → acceptance_criteria → test_strategy → validations →
open_questions.

**Dependencies between sections:**
- `compatibility_analysis` requires `current_state_analysis` (deprecated APIs, patterns)
- `coupling_analysis` requires `current_state_analysis` (module structure)
- `dependency_migration_matrix` requires `current_state_analysis` (dependency list)
- `build_system_impact` requires `current_state_analysis` (build tool, plugins)
- `migration_sequence` requires `compatibility_analysis`, `dependency_migration_matrix`, `build_system_impact`
- `code_transformation_catalog` requires `compatibility_analysis` (BREAK-XXX refs)
- `acceptance_criteria` requires all prior sections
- `test_strategy` requires `acceptance_criteria` (AC-XXX refs)
- `validations` requires all content sections generated
- `open_questions` is ALWAYS LAST — consolidates from all prior sections

### Consolidation Pass (Before Writing)
After generating all sections, perform a single consolidation pass:
1. Scan every section for items with status: pending → create PI-XX in open_questions
2. Scan for [Needs verification] markers → create EG-XX in evidence_gaps
3. Scan for [Compatibility unknown] markers → create EG-XX in evidence_gaps
4. Scan assumptions → create entry in assumptions_to_validate
5. Carry forward unresolved items from migration spec → upstream_gaps_carried_forward
6. In partial contract mode, cross-check structured refs against prose-derived
   IDs/literals/fallbacks; create EG-XX for discrepancies
7. Enforce hash format: only `sha256:<64 lowercase hex>` is valid; invalid
   hash fields demote structured specs to partial and create EG-XX
8. For auth/OAuth/session/password-reset refactors, create EG-XX unless reset
   tokens are hashed at rest and OAuth provider values use an explicit allow-list
9. Compute summary counts
10. Set top-level status: `complete` if zero pending_inputs AND zero blocking evidence_gaps.
   Otherwise: `draft`.

### Refactoring Type Gating
- `version_upgrade`: Skip `coupling_analysis` (write "N/A — version_upgrade mode")
- `structural`: Skip `compatibility_analysis.version_map`; reduce `dependency_migration_matrix` to structural dependencies only
- `combined`: All sections fully populated

### REPAIR Mode
- Load existing spec file
- Apply REPAIR_DIRECTIVES to targeted sections
- Preserve untargeted content verbatim
- Preserve existing IDs. New items: max(existing) + 1. Retired IDs: never reuse.
- ALWAYS rebuild open_questions from scratch
- Increment version, log changes

### Scaling
- Estimated items: 20-100 breaking changes, 30-150 dependencies, 20-100 transformations
- Lines per item: ~6 (breaks), ~4 (deps), ~12 (transforms), ~15 (stages)
- Threshold: Single file sufficient at all expected scales (est. 1,800-4,500 lines)
- If context exceeds 60% mid-generation: apply Write-Flush-Forget for remaining sections
