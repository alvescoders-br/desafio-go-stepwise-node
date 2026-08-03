# Agent-Native Feature Implementation Research Spec Template

## Template Rules
- **No prose.** Every section is structured data only.
- **No narrative.** No "why this matters", no motivational text, no context paragraphs.
- **No formatting for humans.** No prominent text, no callouts, no visual emphasis.
- **No Quick Navigation.** Single file — no cross-document links.
- **All items carry status.** `complete` | `pending` | `assumption`.
- **All pending items appear in open_questions.** Single registry, no scatter.
- **Source tags are mandatory.** No source -> cannot be `complete`.
- **Language:** Generate in DETECTED_LANGUAGE. Section headers in English always.

---

## Spec File Structure

```markdown
# {project_name} — Feature Implementation Research Spec
version: {NEW_VERSION}
session: {SESSION_ID}
mode: {BUILD | REPAIR}
date: {ISO 8601}
language: {DETECTED_LANGUAGE}
story_path: {story_path}
source_path: {source_path | "not provided"}
design_specs_path: {design_specs_path | "not provided"}
api_contract_path: {api_contract_path | "not provided"}
architecture_notes_path: {architecture_notes_path | "not provided"}
story_id: {STORY_CONTEXT.id}
story_format: {STORY_CONTEXT.story_format}
story_contract_mode: {structured | partial | unstructured}
upstream_hashes:
  prd_source_hash: {sha256:<64 lowercase hex> | invalid | N/A}
  epics_source_hash: {sha256:<64 lowercase hex> | invalid | N/A}
  hash_status: {match | mismatch_accepted | mismatch_blocked | not_verified | N/A}
status: {draft | complete}

---

## story_summary

### overview
- id: {STORY_CONTEXT.id}
- title: {STORY_CONTEXT.title}
- format: {user_story | feature_request | generic}
- priority: {P0 | P1 | P2 | P3 | P4}
- parent_epic: {STORY_CONTEXT.parent_epic | "[Not specified]"}
- source: {story_path}
- status: {complete | pending}

### contract_summary
| field | value | source | status |
|-------|-------|--------|--------|
| contract_mode | {structured | partial | unstructured} | {story_path} | complete |
| prd_source_hash | {sha256:<64 lowercase hex> | invalid | N/A} | {story_path} | {complete | pending} |
| epics_source_hash | {sha256:<64 lowercase hex> | invalid | N/A} | {story_path} | {complete | pending} |
| hash_format | {valid_sha256 | invalid | N/A} | {story_path} | {complete | pending} |
| hash_status | {match | mismatch_accepted | mismatch_blocked | not_verified | N/A} | {story_path} | {complete | pending} |
| literal_refs | {LIT-XX list | N/A} | {story_path} | {complete | pending} |
| fallback_refs | {PI/OQ/ASM list | N/A} | {story_path} | {complete | pending} |

### accepted_hash_overrides
| artifact | declared_hash | observed_hash | verification_result | decision |
|----------|---------------|---------------|---------------------|----------|
| {PRD | Epics} | {sha256:<64 lowercase hex>} | {sha256:<64 lowercase hex>} | {all recorded dependencies still present identically | not_verified} | {accepted in this research audit only | N/A} |

### persona_goal_benefit
- persona: {STORY_CONTEXT.persona | "[Not specified]"}
- goal: {STORY_CONTEXT.goal}
- benefit: {STORY_CONTEXT.benefit | "[Not specified]"}
- status: {complete | pending}
- source: {story_path}

### description
{STORY_CONTEXT.description — verbatim from story}

### scope
- in_scope:
  - {scope item 1 — from story description}
  - {scope item N}
- out_of_scope:
  - {STORY_CONTEXT.out_of_scope — or "[Not specified in story]"}
- status: {complete | pending}
- source: {story_path}

### affected_areas

| area | type | notes | source | status |
|------|------|-------|--------|--------|
| {area} | [File/Module/Service/Screen/Endpoint] | {notes from story} | {story_path} | {complete | pending} |

### dependencies

| dependency | type | dep_status | source | status |
|------------|------|------------|--------|--------|
| {STORY_CONTEXT.dependencies[N]} | [Story/Service/Feature/External] | [Available/Pending/Unknown] | {story_path} | {complete | pending} |

IF STORY_CONTEXT.dependencies is empty:
  [No dependencies specified in story.]

### constraints

| constraint | source_ref | status |
|------------|-----------|--------|
| {STORY_CONTEXT.constraints[N]} | [Story / Architecture notes / Context pack] | {complete | pending} |

IF no constraints:
  [No explicit constraints specified.]

### sourced_constraints
| constraint | source_ref | disposition | status |
|------------|------------|-------------|--------|
| {positive or negative constraint} | {ADR-XXX | tech-policy | context-pack | story_path} | {preserve | evidence_gap_if_unsourced} | {complete | pending} |

### architecture_authority_gaps
| item | structural_type | reason | decision | status |
|------|-----------------|--------|----------|--------|
| {unsourced path/package/layer/framework/storage/runtime/deployment/module placement} | {path | package | layer | framework | storage | runtime | deployment | module} | {no authoritative source_ref} | {moved to evidence_gaps | pending input} | {pending | assumption} |

### complexity_assessment
- overall_complexity: {LOW | MEDIUM | HIGH} | rationale: {based on scope, integration points}
- regression_risk: {LOW | MEDIUM | HIGH} | rationale: {based on centrality of affected areas}
- integration_complexity: {LOW | MEDIUM | HIGH} | rationale: {based on touchpoints}
- implementation_complexity: {LOW | MEDIUM | HIGH} | rationale: {based on scope, dependencies}

---

## codebase_analysis

### tech_stack

| layer | technology | version | source | status |
|-------|------------|---------|--------|--------|
| {layer} | {EXACT from build file} | {EXACT version} | {build file path} | {complete | pending | assumption} |

IF SOURCE_CONTEXT is null AND ARCH_CONTEXT exists:
  - note: "Technology stack from architecture notes — verify against actual build files"
  - status: assumption

IF SOURCE_CONTEXT is null AND ARCH_CONTEXT is null:
  - note: "Technology stack not available — no source code or architecture notes provided"
  - status: pending

### project_structure
```
{Relevant directory tree from SOURCE_CONTEXT.project_structure}
{Focus on: areas the feature will touch, similar existing features, test locations}
```
- status: {complete | pending}
- source: {source_path}

IF SOURCE_CONTEXT is null:
  [Project structure not available — no source code provided.]
  - status: pending

### existing_capability

| capability | location | relevant_to_story | source | status |
|------------|----------|-------------------|--------|--------|
| {what currently exists} | `path/to/file.ext:L-N` | [Yes — extend / No — adjacent] | {source_path} | {complete | assumption} |

### gap_analysis

| gap | impact_on_feature | severity | source | status |
|-----|-------------------|----------|--------|--------|
| {what's missing} | {how it affects implementation} | [Blocking/Significant/Minor] | {source_path} | {complete | assumption} |

### similar_features

| feature | location | pattern | reuse_potential | source | status |
|---------|----------|---------|-----------------|--------|--------|
| {existing similar feature} | `path/to/example.ext:L-N` | {pattern name} | [HIGH/MEDIUM/LOW] | {source_path} | {complete | assumption} |

IF no similar features:
  [No directly similar features found in codebase.]

### architecture_layers

#### data_layer

| aspect | current_state | feature_impact | source | status |
|--------|--------------|----------------|--------|--------|
| ORM / Data Access | {SOURCE_CONTEXT.data_layer} | {changes needed} | {source_path} | {complete | assumption} |
| Schema / Migrations | {location, tool} | {new tables/columns?} | {source_path} | {complete | assumption} |

#### api_layer

| aspect | current_state | feature_impact | source | status |
|--------|--------------|----------------|--------|--------|
| Framework / Router | {SOURCE_CONTEXT.api_layer} | {new endpoints?} | {source_path} | {complete | assumption} |
| Auth / Middleware | {approach} | {changes needed?} | {source_path} | {complete | assumption} |

#### ui_layer

| aspect | current_state | feature_impact | source | status |
|--------|--------------|----------------|--------|--------|
| Component Framework | {SOURCE_CONTEXT.ui_layer} | {new components?} | {source_path} | {complete | assumption} |
| State Management | {approach} | {new state?} | {source_path} | {complete | assumption} |
| Routing | {approach} | {new routes?} | {source_path} | {complete | assumption} |

IF no UI impact:
  [No UI layer changes — backend-only feature.]

### conventions

| convention | example_location | apply_to | source | status |
|------------|-----------------|----------|--------|--------|
| {naming} | `path/to/example.ext` | {where} | {source_path} | {complete | assumption} |
| {file structure} | `path/to/example/` | {where} | {source_path} | {complete | assumption} |
| {error handling} | `path/to/example.ext:L-N` | {where} | {source_path} | {complete | assumption} |
| {testing} | `path/to/example.spec.ext` | {where} | {source_path} | {complete | assumption} |

---

## impact_assessment

### direct_impact

| file | change_type | risk | reason | source | status |
|------|-------------|------|--------|--------|--------|
| `{exact/path/file.ext}` | {Create | Modify | Delete} | {LOW | MED | HIGH} | {why — traced to story} | {source_path} | {complete | assumption} |

### indirect_impact

| component | how_affected | risk | mitigation | source | status |
|-----------|-------------|------|------------|--------|--------|
| {component/file} | {regression scenario} | {LOW | MED | HIGH} | {how to mitigate} | {source_path} | {complete | assumption} |

### dependencies_affected

| dependency | dep_type | impact | action_required | source | status |
|------------|----------|--------|-----------------|--------|--------|
| {internal module / external library} | {Internal | External} | {how affected} | {Update | Test | Monitor} | {source_path} | {complete | assumption} |

### data_impact

| data_store | impact | migration_needed | rollback_strategy | source | status |
|------------|--------|------------------|-------------------|--------|--------|
| {DB/Cache/Queue | "None"} | {how affected} | {Yes — details | No} | {how to rollback} | {source_path} | {complete | pending} |

IF no data changes:
  [No data model changes required for this feature.]

### api_impact

| interface | change | breaking | consumers | migration_path | source | status |
|-----------|--------|----------|-----------|----------------|--------|--------|
| {endpoint / method | "None"} | {New | Modified | Deprecated} | {Yes | No} | {who calls it} | {versioning approach} | {source_path} | {complete | pending} |

IF no API changes:
  [No API changes required for this feature.]

### ui_impact

| screen_component | change | risk | notes | source | status |
|-----------------|--------|------|-------|--------|--------|
| {screen or component} | {New | Modified} | {LOW | MED | HIGH} | {visual regression, a11y} | {source_path} | {complete | pending} |

IF no UI changes:
  [No UI changes required for this feature.]

### risk_summary
- overall: {LOW | MEDIUM | HIGH}
- regression: {LOW | MEDIUM | HIGH}
- data: {LOW | MEDIUM | HIGH}
- api: {LOW | MEDIUM | HIGH}
- ui: {LOW | MEDIUM | HIGH}

---

## integration_mapping

### module_integration_points

| id | existing_module | integration_type | feature_interaction | files_involved | source | status |
|----|----------------|-----------------|---------------------|----------------|--------|--------|
| IP-01 | {module name} | {Extends | Consumes | Produces | Modifies} | {how feature interacts} | `{path/to/file.ext}` | {source_path} | {complete | assumption} |

### data_flow

#### current_flow
- trigger: {source/trigger}
- steps:
  - {step 1: module/file}
  - {step 2: module/file}
- destination: {destination/output}
- source: {source_path}
- status: {complete | assumption}

#### flow_after_feature
- trigger: {source/trigger}
- steps:
  - {step 1}
  - {NEW: feature step}
  - {step 2 — modified?}
- destination: {destination}
- source: {source_path}
- status: {complete | assumption}

### new_data_entities

| entity | store | relationships | notes | source | status |
|--------|-------|---------------|-------|--------|--------|
| {new table/collection/model} | {DB/Cache} | {FK to existing} | {cardinality, constraints} | {source_path} | {complete | assumption} |

IF no new data entities:
  [No new data entities required.]

### ui_integration

#### navigation_routing

| route_path | route_type | connected_to | source | status |
|-----------|-----------|-------------|--------|--------|
| {/new-route or modified} | {New | Modified} | {existing page/component} | {source_path} | {complete | assumption} |

IF no routing changes:
  [No routing changes required.]

#### component_hierarchy
```
{ParentComponent}
+-- {ExistingChild}
+-- {NEW: FeatureComponent}     <- Feature adds here
|   +-- {SubComponent1}
|   +-- {SubComponent2}
+-- {ExistingChild2}
```
- source: {source_path}
- status: {complete | assumption}

IF no UI components:
  [No UI component changes — backend-only feature.]

#### design_screen_mapping (if DESIGN_CONTEXT available)

| design_screen | existing_screen | integration_point | notes | source | status |
|---------------|----------------|-------------------|-------|--------|--------|
| {from DESIGN_CONTEXT.screens} | {current screen or "New"} | {where it connects} | {layout, interaction} | {design_specs_path} | {complete | assumption} |

### api_integration

#### new_endpoints

| method | path | purpose | auth | consumes | produces | source | status |
|--------|------|---------|------|----------|----------|--------|--------|
| {GET/POST/PUT/DELETE} | {/api/path} | {purpose} | {Required | Optional | None} | {request shape} | {response shape} | {source_path | api_contract_path} | {complete | assumption} |

IF API_CONTEXT available:
  contract_validation: All endpoints verified against {api_contract_path}

#### modified_endpoints

| method | path | change | backward_compatible | source | status |
|--------|------|--------|---------------------|--------|--------|
| {method} | {/api/path} | {what changes} | {Yes | No — migration path} | {source_path} | {complete | assumption} |

IF no API changes:
  [No API integration changes — internal feature.]

### external_service_integration

| service | protocol | purpose | error_handling | source | status |
|---------|----------|---------|----------------|--------|--------|
| {external service} | {REST | GraphQL | gRPC | Event} | {why needed} | {retry/circuit breaker/fallback} | {source_path} | {complete | assumption} |

IF no external services:
  [No external service integration required.]

### architecture_constraint_compliance

| constraint | constraint_source | compliance | notes | status |
|------------|------------------|------------|-------|--------|
| {constraint from ARCH_CONTEXT} | {ADR/Architecture notes} | {compliant | deviation} | {details} | {complete | assumption} |

IF ARCH_CONTEXT is null:
  [No architecture constraints provided — implementation follows existing codebase patterns.]

### integration_risk

| integration_point | risk | rationale | mitigation | source | status |
|-------------------|------|-----------|------------|--------|--------|
| {module/API/data/UI} | {LOW | MED | HIGH} | {why risky} | {how to mitigate} | {source_path} | {complete | assumption} |

---

## implementation_approach

### strategy
- approach: {what to build — 1 sentence}
- rationale: {why this approach — 1 sentence}
- primary_pattern: {existing codebase pattern to follow}
- pattern_location: {path:L-N}

### phases

| phase | description | file_count | dependency | source | status |
|-------|-------------|------------|------------|--------|--------|
| 1 | {Foundation — data model, core logic} | {N} | None | {source_path} | {complete | assumption} |
| 2 | {Integration — wire to existing modules} | {N} | Phase 1 | {source_path} | {complete | assumption} |
| 3 | {Surface — UI/API exposure} | {N} | Phase 2 | {source_path} | {complete | assumption} |
| 4 | {Verification — tests, manual QA} | {N} | Phase 3 | {source_path} | {complete | assumption} |

### files_to_create

| path | purpose | pattern_reference | phase | source | status |
|------|---------|-------------------|-------|--------|--------|
| `{exact/path/new-file.ext}` | {purpose} | Follow `{existing/pattern.ext:L-N}` | {1/2/3/4} | {source_path} | {complete | assumption} |

IF no new files:
  [No new files required — all changes are modifications to existing files.]

### files_to_modify

| path | change | pattern_reference | phase | source | status |
|------|--------|-------------------|-------|--------|--------|
| `{exact/path/existing.ext}` | {specific change} | {pattern ref} | {1/2/3/4} | {source_path} | {complete | assumption} |

### implementation_steps

#### phase_1: {Foundation}
1. {step 1 — specific action with file and location}
2. {step 2 — specific action}

#### phase_2: {Integration}
3. {step 3 — specific action}
4. {step 4 — specific action}

#### phase_3: {Surface}
5. {step 5 — specific action}
6. {step 6 — specific action}

#### phase_4: {Verification}
7. {step 7 — test action}
8. {step N — final verification}

### code_patterns

#### pattern_1: {primary pattern}
- location: `{path/to/example.ext:L-N}`
- source: {source_path}

```{language}
// Example (10-15 lines) from SOURCE_CONTEXT.existing_patterns
{code example}
```

#### pattern_2: {secondary pattern — if applicable}
- location: `{path/to/example.ext:L-N}`
- source: {source_path}

```{language}
{code example}
```

IF SOURCE_CONTEXT is null:
  [Code patterns are illustrative — verify against actual codebase conventions.]

### edge_cases

| edge_case | handling | phase | source | status |
|-----------|----------|-------|--------|--------|
| {edge case from story or inferred} | {how to handle} | {phase} | {source_path | inference} | {complete | assumption} |

### constraints
- {constraint from codebase conventions, architecture notes, or context pack} | source: {ref}

### out_of_scope_improvements

| improvement | rationale | effort | source | status |
|-------------|-----------|--------|--------|--------|
| {improvement NOT part of story} | {why it would help} | {LOW | MED | HIGH} | {source_path} | {complete | assumption} |

IF none:
  [No out-of-scope improvements identified.]

---

## acceptance_criteria

### story_ac (MANDATORY — preserve verbatim)

| id | criterion | source | verification | status |
|----|-----------|--------|--------------|--------|
| SAC-01 | {AC from STORY_CONTEXT.ac — verbatim} | {story_path} | {how to verify} | complete |
| SAC-NN | {AC from story — verbatim} | {story_path} | {how to verify} | complete |

IF STORY_CONTEXT.ac is empty:
  [No acceptance criteria provided in story.]
  - status: pending
  - registered in open_questions

### derived_ac

| id | criterion | rationale | verification | source | status |
|----|-----------|-----------|--------------|--------|--------|
| DAC-01 | Feature accessible via {navigation path / API endpoint} | Core functionality | {specific verification} | {story_path} | complete |
| DAC-02 | Feature behavior matches story goal: "{STORY_CONTEXT.goal}" | Story fulfillment | {specific verification} | {story_path} | complete |
| DAC-NN | {additional derived criterion} | {why needed} | {how to verify} | {ref} | {complete | assumption} |

### ui_ac (if DESIGN_CONTEXT available)

| id | criterion | design_reference | verification | source | status |
|----|-----------|-----------------|--------------|--------|--------|
| UAC-01 | {UI criterion from DESIGN_CONTEXT} | {screen/component} | {visual/interaction check} | {design_specs_path} | {complete | assumption} |

IF DESIGN_CONTEXT is null:
  [No design specs provided — UI criteria derived from story description.]

### api_ac (if API_CONTEXT available)

| id | criterion | contract_reference | verification | source | status |
|----|-----------|-------------------|--------------|--------|--------|
| AAC-01 | {API criterion from API_CONTEXT} | {endpoint/operation} | {request/response validation} | {api_contract_path} | {complete | assumption} |

IF API_CONTEXT is null AND api_changes > 0:
  [No API contract provided — API criteria derived from implementation approach.]

### regression_ac

| id | criterion | verification | source | status |
|----|-----------|--------------|--------|--------|
| RAC-01 | All existing tests pass | `{test command from SOURCE_CONTEXT.test_framework}` | {source_path} | {complete | pending} |
| RAC-02 | Existing features in {affected area} still work correctly | {verification method} | {source_path} | {complete | assumption} |
| RAC-NN | {specific regression scenario from impact_assessment} | {verification} | {source_path} | {complete | assumption} |

### definition_of_done
- [ ] All story AC verified
- [ ] All derived criteria verified
- [ ] All regression criteria verified
- [ ] No new test failures introduced
- [ ] Code follows existing conventions (naming, structure, error handling)
- [ ] Integration points verified
- [ ] PR/review ready

---

## test_strategy

### tests_to_write

| test | type | file | covers | phase | source | status |
|------|------|------|--------|-------|--------|--------|
| {test description — specific to feature} | {Unit | Integration | E2E} | `{test/file/path.spec.ext}` | {SAC-XX | DAC-XX | RAC-XX} | {1/2/3/4} | {source_path} | {complete | assumption} |

### tests_to_update

| test | file | change_needed | reason | source | status |
|------|------|---------------|--------|--------|--------|
| {existing test name} | `{test/file/path.spec.ext}` | {what to update} | {why} | {source_path} | {complete | assumption} |

IF no existing tests need updating:
  [No existing tests require changes.]

### test_commands

```bash
# Run new feature tests
{exact test command targeting new test files}

# Run affected area tests
{test command for affected modules}

# Run full suite (regression check)
{full test command from SOURCE_CONTEXT.test_framework}
```

IF SOURCE_CONTEXT is null:
  [Test commands not available — verify in project build configuration.]
  - status: pending

### coverage_matrix

| ac_criterion | test_type | test_file | test_status | source | status |
|-------------|-----------|-----------|-------------|--------|--------|
| {SAC-01} | {Unit | Integration | E2E} | `{path}` | {To write | Existing | To update} | {source_path} | {complete | assumption} |

### coverage_targets

| area | current | target | notes | source | status |
|------|---------|--------|-------|--------|--------|
| {new file/module} | N/A (new) | {target %} | {critical paths} | {source_path} | {complete | pending} |
| {modified file/module} | {current % | "Unknown"} | {target %} | {maintain/improve} | {source_path} | {complete | pending} |

### integration_test_scenarios

| scenario | modules_involved | expected_outcome | source | status |
|----------|-----------------|------------------|--------|--------|
| {from integration_mapping} | {Module A -> Module B} | {expected result} | {source_path} | {complete | assumption} |

### manual_verification_steps
1. {navigate to feature, verify accessible}
2. {exercise primary functionality, verify story goal}
3. {test edge cases from implementation_approach}
4. {verify regression scenarios from impact_assessment}
5. {verify all AC from acceptance_criteria}

---

## validations

| check | result | notes |
|-------|--------|-------|
| codebase_fidelity | {PASS | FAIL} | {details if FAIL} |
| story_ac_coverage | {PASS | FAIL} | {details if FAIL} |
| integration_mapping_completeness | {PASS | FAIL} | {details if FAIL} |
| technology_fidelity | {PASS | FAIL} | {details if FAIL} |
| api_contract_consistency | {PASS | FAIL | N/A} | {details if FAIL} |
| design_spec_consistency | {PASS | FAIL | N/A} | {details if FAIL} |
| anti_fade | {PASS | FAIL} | {details if FAIL} |
| section_completeness | {PASS | FAIL} | {details if FAIL} |
| count_verification | {PASS | FAIL} | {details if FAIL} |
| source_tags | {PASS | FAIL} | {details if FAIL} |
| story_contract_mode | {PASS | FAIL} | mode={structured | partial | unstructured}; unstructured accepted |
| partial_cross_check | {PASS | FAIL | N/A} | discrepancies={N} |
| architecture_authority | {PASS | FAIL} | unsourced structural mandates flagged={N}; sourced constraints preserved={N} |
| hash_forward_verification | {PASS | FAIL | N/A} | valid_sha256={yes | no}; accepted_hash_overrides={N}; blocked={N} |
| auth_security_defaults | {PASS | FAIL | N/A} | reset_tokens_hashed={yes | no | N/A}; oauth_provider_allow_list={yes | no | N/A} |

---

## open_questions

This section is the **single consolidated registry** of all unresolved items.
Every `pending` status, every `assumption` that needs validation — all appear
here once. Downstream skills (planning-code-tasks) read ONLY this section to
understand what is unresolved.

### pending_inputs

| id | affected_ids | blocking | type | section | item_id | field | impact | fallback_behavior | source_ref |
|----|--------------|----------|------|---------|---------|-------|--------|-------------------|------------|
| PI-01 | {US-XX-XX-AC-XX | all | N/A} | {yes | no} | missing | {section} | {item_id} | {field} | {impact on downstream} | {fallback or BLOCKED} | {story_path} |

### evidence_gaps

| id | affected_ids | type | section | claim | evidence_needed | impact | decision |
|----|--------------|------|---------|-------|-----------------|--------|----------|
| EG-01 | {US-XX-XX-AC-XX | LIT-XX | all | N/A} | {missing_source | structured_discrepancy | unsourced_structural_mandate | hash_dependency_gap} | {section} | {claim without full evidence} | {what evidence would confirm} | {impact if wrong} | {accepted | carried_forward | blocks} |

### assumptions_to_validate

| id | affected_ids | blocking | assumption | impact_if_wrong | validation_method | fallback_behavior | source_ref |
|----|--------------|----------|------------|-----------------|-------------------|-------------------|------------|
| ASM-01 | {US-XX-XX-AC-XX | all | N/A} | {yes | no} | {assumption statement} | {consequence} | {how to confirm/deny} | {fallback or BLOCKED} | {story_path} |

### upstream_gaps_carried_forward

| id | affected_ids | blocking | source | gap | impact_on_spec | fallback_behavior |
|----|--------------|----------|--------|-----|---------------|-------------------|
| UG-01 | {US-XX-XX-AC-XX | all | N/A} | {yes | no} | {story_path} | {what was missing from story} | {which sections affected} | {fallback or BLOCKED} |

### summary
- total_affected_files: {N}
- total_new_files: {N}
- total_integration_points: {N}
- total_data_model_changes: {N}
- total_api_changes: {N}
- total_ui_changes: {N}
- total_story_ac: {N}
- total_derived_ac: {N}
- total_regression_ac: {N}
- total_tests_to_write: {N}
- total_tests_to_update: {N}
- pending_inputs: {N}
- evidence_gaps: {N}
- assumptions: {N}
- overall_complexity: {LOW | MEDIUM | HIGH}
- overall_risk: {LOW | MEDIUM | HIGH}
- status: {draft | complete}
```

---

## Generation Rules

### Section Ordering
Generate sections in the order shown above. This order reflects dependency flow:
story_summary -> codebase_analysis -> impact_assessment -> integration_mapping ->
implementation_approach -> acceptance_criteria -> test_strategy -> validations ->
open_questions.

The validations section MUST come after all content sections are generated.
The open_questions section is ALWAYS LAST — it consolidates from all prior sections.

### Per-Item Rules
- Every table row MUST have `status` and `source` columns.
- `status: complete` requires a non-empty `source` value.
- `status: pending` -> item MUST also appear in `open_questions.pending_inputs`.
- `status: assumption` -> item MUST also appear in `open_questions.assumptions_to_validate`
  with an ASM-XX ID.

### REPAIR Mode
- Load existing spec file.
- Apply REPAIR_DIRECTIVES to targeted sections only.
- Sections without directives -> preserve verbatim from previous spec.
- "global" directive -> regenerate entire spec.
- Rebuild open_questions from scratch (always reflects current state).
- Increment version, log changes in CHANGE_LOG.
- Recalculate all summary counts after repair.

### Scaling
Always single file. Feature-impl research specs are scoped to one story/feature.
No batching, no multi-file splitting. If context exceeds 60% mid-generation
(unlikely), apply Write-Flush-Forget to the single file.

### Consolidation Pass (Before Writing)
After generating all sections, perform a single consolidation pass:
1. Scan every section for items with status: pending -> create PI-XX in open_questions
2. Scan every section for items with status: assumption -> create ASM-XX in open_questions
3. Scan for evidence gaps (claims without full source backing) -> create EG-XX
4. Carry forward upstream gaps from story -> create UG-XX
5. In partial contract mode, cross-check structured refs against prose-derived
   IDs/literals/fallbacks; create EG-XX for discrepancies
6. Enforce hash format: only `sha256:<64 lowercase hex>` is valid; invalid
   hash fields demote structured stories to partial and create EG-XX
7. Flag unsourced structural story mandates (paths, packages, layers,
   frameworks, storage, runtime, deployment, module placement) as EG-XX unless
   backed by ADR/tech-policy/context-pack/story source_ref
8. For auth/OAuth/session/password-reset stories, create EG-XX unless reset
   tokens are hashed at rest and OAuth provider values use an explicit allow-list
9. Compute summary counts
10. Set top-level status: `complete` if zero pending_inputs AND zero blocking evidence_gaps.
   Otherwise: `draft`.
