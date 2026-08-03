# Code Task Planning - Agent-Native Spec Template

## Template Rules
- **Execution-facing.** `PLAN-SPEC` is the compact contract consumed by `implementing-code`.
- **Self-contained for coding.** All implementation-relevant facts must be literal in the plan: file paths, signatures, constants, commands, constraints, edge cases, external artifact paths, and out-of-scope boundaries.
- **No research dereferencing.** Do not write "see research", "per research", or "per Parameter Schema" for facts the implementer needs. Restate the executable value.
- **Deterministic load set.** External artifacts and shared canonical values live in header-level sections so the harness can load `PLAN-SPEC` plus the exact files it names without grepping phase prose.
- **No per-line provenance ceremony.** Executable sections do not carry `status` or `source` columns. Use compact `evidence_refs` at section or phase level when useful; full provenance lives in `PLAN-AUDIT`.
- **Open questions are the only unresolved registry.** Pending inputs and assumptions live only in `open_questions`.
- **Omit empty sections.** Do not emit `N/A` tables or boilerplate sections. Missing optional sections mean no work in that category.
- **Technology fidelity.** Use exact names, versions, literals, paths, and identifiers from research or source code. Never generalize implementation-critical details.
- **Scope-adaptive.** File contains TASK sections OR FULL_SDLC sections, never both.

---

## Spec File Structure

```markdown
# {project_name} - Code Task Planning Spec
version: {version}
session: {session_id}
scope: {TASK | FULL_SDLC}
task_id: {task_id | N/A}
task_type: {BUG_FIX | USER_STORY | ENHANCEMENT | N/A}
mode: {BUILD | REPAIR}
date: {ISO 8601}
language: {detected_language}
tdad_mode: {true | false}
research_session: {research_session_id}
research_source: {research_output_path}
research_fingerprint: {sha256:<64 lowercase hex chars> | N/A}
plan_status: {PROCEED | CONDITIONAL | BLOCKED | VERIFY_ONLY | PARTIAL_APPLIED}
validation_status: {PASS | WARN | FAIL}
quality_score: {0-100}
status: {draft | complete}
```

---

## Header-Level Execution Sections

These sections appear immediately after the header for both TASK and FULL_SDLC
scopes when applicable. `canonical_values` and `plan_status_semantics` are part
of every phase load; `required_artifacts` is part of a phase load when rows match
that phase.

### required_artifacts

Machine-readable load contract for external artifacts the implementer must read
in addition to `PLAN-SPEC`.

```markdown
## required_artifacts
| path | purpose | phases_using |
|------|---------|--------------|
| {prototype.html} | {source UI behavior/layout reference} | {phase_1, phase_2} |
| {00-design-system.md} | {tokens, component rules, interaction conventions} | {all} |
```

Rules:
- Include only artifacts outside `PLAN-SPEC` that the executor genuinely needs.
- Exclude `RESEARCH-SPEC` and `PLAN-AUDIT`; those are fallback/forensics inputs, not normal execution inputs.
- `phases_using` is `all` or a comma-separated list of phase IDs.
- If no external artifacts are needed, omit the section.

### canonical_values

Shared literal contract for values used by more than one phase or needed by
tests and implementation. This replaces the research-only Parameter Schema at
execution time.

```markdown
## canonical_values
| id | name | value | type | phases_using | notes |
|----|------|-------|------|--------------|-------|
| CV-01 | division_by_zero_error_code | DIVISION_BY_ZERO | error_code | phase_1, phase_2 | exact literal; do not abbreviate |
| CV-02 | default_math_context | MathContext(10, HALF_UP) | runtime_constant | all | HALF_UP, not HALF_EVEN |
| CV-03 | precision_range | 0-50 | validation_range | phase_1 | inclusive bounds |
```

Rules:
- Include exact enum members, error codes, constants, default values, ranges,
  route strings, storage keys, event names, precision/rounding rules, and other
  shared literals.
- Every phase that uses a canonical value must list the relevant `CV-XX` in
  its `canonical_values_used` field.
- Do not rely on a phase-local paraphrase when a shared canonical value exists.

### plan_status_semantics

```markdown
## plan_status_semantics
| status | execution_meaning |
|--------|-------------------|
| PROCEED | Implement all planned phases normally. |
| CONDITIONAL | Implement using populated fallback_behavior for every non-blocking pending input. |
| BLOCKED | Do not implement; at least one implementability-gating input has no deterministic fallback. |
| VERIFY_ONLY | Do not implement; verify every file row's `pre_applied` evidence and run the cheapest relevant validation. |
| PARTIAL_APPLIED | Verify file rows with populated `pre_applied` evidence, skip those changes, and implement only rows where `pre_applied` is `none`. |
```

### security_decisions

**Required whenever the work has a security surface** — i.e. any phase touches
authentication/authorization, secret/credential/token handling, session or
cookie issuance, a privileged/admin/internal endpoint, persistence of sensitive
data, or code that writes files/config a secret flows into. This is the plan-time
contract that makes secure behavior an explicit decision instead of a convenient
default the implementer picks under delivery pressure (fail-open auth, plaintext
tokens in `/tmp`, unthrottled admin routes). The downstream code review enforces
the same classes (secure-defaults SD-01…SD-10); deciding them here prevents the
rework loop.

This is NOT an invitation to invent requirements. Ground each decision in
research, the context pack (`security.md` when present), or an explicit
assumption logged to `open_questions`. Keep it technology-agnostic; concrete
per-project specifics (exact secret-manager, header names) belong in the context
pack, not invented here.

```markdown
## security_decisions
| id | concern | decision | fallback_when_config_absent | evidence_ref |
|----|---------|----------|-----------------------------|--------------|
| SEC-01 | auth failure mode | {reject / fail closed; refuse to start in production without OIDC config} | {deny} | {research/context-pack ref or ASM-xx} |
| SEC-02 | secret storage & lifecycle | {where secrets live at rest, permissions, single canonical sink, rotation} | {n/a} | {ref} |
| SEC-03 | session/cookie flags | {HttpOnly + Secure + SameSite; token never script-readable} | {n/a} | {ref} |
| SEC-04 | privileged endpoint protection | {authn + authz + rate limiting on admin/credential routes} | {deny} | {ref} |
| SEC-05 | audit/security log durability | {durable sink reachable by the enforcement path; survives restart} | {n/a} | {ref} |
```

Rules:
- Include a row for every security concern the scope actually raises; omit rows
  for concerns the scope does not touch (do not emit `N/A` filler).
- Every access-gating decision must state a `fallback_when_config_absent` that is
  **deny / fail closed**. A fallback that grants on missing config is a planning
  defect — route it to `open_questions` at `impact: HIGH`, not into this table.
- **When the scope genuinely has no security surface**, do not silently omit the
  section — emit the single line `## security_decisions` / `- none: no security
  surface in scope ({one-line why})` so the absence is a recorded decision the
  verification gate can confirm, not an oversight.
- Unresolved security choices (e.g. "which secret store?") are `open_questions`
  pending inputs with deterministic fail-closed `fallback_behavior`, not blanks.

---

## TASK Scope Sections

Rendered when `scope: TASK`. Omit all FULL_SDLC sections.

### task_summary

```markdown
## task_summary
- task_id: {TASK_CONTEXT.task_id}
- title: {TASK_CONTEXT.title}
- task_type: {BUG_FIX | USER_STORY | ENHANCEMENT}
- priority: {critical | high | medium | low}
- complexity: {LOW | MEDIUM | HIGH}
- risk: {LOW | MEDIUM | HIGH}
- phase_count: {1 | 2 | 3}
- goal: {one sentence - what is done when this task is complete}
- evidence_refs: [{research refs or audit source IDs}]
```

### scope

```markdown
## scope

### in_scope
| file_path | description |
|-----------|-------------|
| {path} | {what changes in this file} |

### out_of_scope
| item | reason |
|------|--------|
| {indirect impact item NOT being fixed} | {rationale} |
```

### tech_stack

```markdown
## tech_stack
| layer | technology | version |
|-------|------------|---------|
| {runtime | framework | database | build | test | ...} | {exact name} | {exact version} |
```

### impact

```markdown
## impact
- direct:
  - file_path: {path}
    component: {name}
    change: {specific implementation impact}
- indirect:
  - component: {name}
    risk_reason: {why}
- risk_level: {LOW | MEDIUM | HIGH}
- risk_rationale: {source-based explanation}
```

### phases (TASK: 1-3 phases)

Phase count by complexity: LOW = 1, MEDIUM = 2, HIGH = 3.

```markdown
## phases

### phase_{N}: {name}
- goal: {one-line - what this phase achieves}
- prerequisites: [{list of dependencies}]
- canonical_values_used: [{CV-XX, ...}]
- evidence_refs: [{research refs or audit source IDs}]

#### files_to_create
| file_path | purpose | pattern_ref | pre_applied |
|-----------|---------|-------------|-------------|
| {path} | {why this file exists} | {design pattern or omitted} | {none | commit/hash + expected marker | existing path + expected marker | passing test name} |

#### files_to_modify
| file_path | changes | pattern_ref | pre_applied |
|-----------|---------|-------------|-------------|
| {path} | {specific changes} | {design pattern or omitted} | {none | commit/hash + expected marker | existing path + expected marker | passing test name} |

#### interface_contracts
| symbol | inputs | outputs | error_handling |
|--------|--------|---------|----------------|
| {function/class/endpoint name} | {exact params/request shape} | {return/response type} | {exact strategy/literals} |

#### implementation_steps
1. {specific executable step with exact identifiers/literals}
2. {specific executable step with exact identifiers/literals}

#### constraints
- {constraint with exact value, identifier, path, predicate, or configuration key}

#### edge_cases
- {edge case and required handling}

#### fix_pattern
```{lang}
{code - max 25 lines - only when research supplied an executable pattern}
```

#### success_criteria
- automated:
  - {criterion with runnable command or observable result}
- manual:
  - {criterion, only when manual verification is unavoidable}
- performance:
  - {criterion, only when source-backed}

#### rollback
1. {rollback step, only when non-trivial}

#### out_of_scope
- {item not addressed in this phase}
```

Omit `files_to_create`, `files_to_modify`, `interface_contracts`, `constraints`,
`edge_cases`, `fix_pattern`, `rollback`, or `out_of_scope` when empty. Do not
emit `N/A` rows. The `pre_applied` column may be omitted when `plan_status` is
`PROCEED`, `CONDITIONAL`, or `BLOCKED`. It is required when `plan_status` is
`VERIFY_ONLY` or `PARTIAL_APPLIED`. In `VERIFY_ONLY`, every file row must have
non-`none` evidence. In `PARTIAL_APPLIED`, pre-applied rows have evidence and
remaining rows use `none`.

If `tdad_mode: true`, implementation steps for files with test coverage must
use Red-Green-Refactor ordering: create/update the failing test first, implement
the minimum source change second, then refactor while tests stay green. This is
intentional and must not be reordered by the executor.

### testing_strategy (TASK)

```markdown
## testing_strategy

### tests_to_write
| test_file | test_cases | type | test_case_id |
|-----------|------------|------|--------------|
| {path} | {case descriptions} | {unit | integration | e2e} | {FTC id(s) e.g. FTC_01_03_02, comma-separated | [derived]} |

**`test_case_id` semantics** — the traceability anchor between the planner (HOW) and
`quality-engineering-design`'s FTCs (WHAT):
- When `test_cases_path` was supplied, cite the FTC id(s) each row satisfies.
- The planner assigns the `type` (level): a `[BE]` FTC typically maps to `unit` or
  `integration`; an `[FE]`/journey FTC is usually deferred to `e2e` — mark those rows
  `type: e2e` and note `covered_by: qe-web-automation` so the downstream automation
  capability owns them (prevents double-automation).
- `[derived]` = no FTC existed; test derived from ACs/research (legacy behavior).
- Every in-scope FTC MUST appear in exactly one row's `test_case_id`, OR be listed under
  `out_of_scope` with reason `deferred-to-e2e` / `covered-elsewhere`. See SV rule.

### tests_to_update
| test_file | changes |
|-----------|---------|
| {path} | {what changes} |

### test_commands
- unit: {command}
- integration: {command}
- e2e: {command}
- coverage_target: {%}

### regression_verification
| id | test | verification |
|----|------|--------------|
| RV-01 | {test description} | {how it proves bug is fixed} |
```

Omit `regression_verification` for non-BUG_FIX tasks. Omit any test subsection
with no entries.

### acceptance_criteria (TASK)

```markdown
## acceptance_criteria

### ticket_ac
| id | criterion | verification |
|----|-----------|--------------|
| TAC-01 | {from ticket/story} | {how to verify} |

### derived_ac
| id | criterion | verification |
|----|-----------|--------------|
| DAC-01 | {inferred from research with literal implementation relevance} | {how to verify} |

### regression_ac
| id | criterion | verification |
|----|-----------|--------------|
| RAC-01 | {regression criterion} | {how to verify} |

### definition_of_done
- [ ] {checklist item}
```

Omit `derived_ac` or `regression_ac` when empty.

---

## FULL_SDLC Scope Sections

Rendered when `scope: FULL_SDLC`. Omit all TASK sections.

### plan_overview

```markdown
## plan_overview
- plan_status: {PROCEED | CONDITIONAL | BLOCKED | VERIFY_ONLY | PARTIAL_APPLIED}
- fr_count: {N}
- story_count: {N}
- phase_count: {N}
- complexity: {LOW | MEDIUM | HIGH}
- risk_level: {LOW | MEDIUM | HIGH}
- evidence_refs: [{research refs or audit source IDs}]
```

### blocker_resolution

This section is a view over `open_questions`, not a second registry.

```markdown
## blocker_resolution
- blockers_from_open_questions: [PI-01, PI-03]
- critical_assumptions: [ASM-01, ASM-02]
- plan_status_impact: {why status is PROCEED | CONDITIONAL | BLOCKED | VERIFY_ONLY | PARTIAL_APPLIED}
```

Every implementability-gating open question must appear here. An unresolved
target the implementer cannot proceed without is a blocker and drives
`plan_status: BLOCKED`.

### current_state

```markdown
## current_state
- build_context: {GREENFIELD | BROWNFIELD}
- summary: {one-line current-state summary}

### brownfield_details
| component | state | gap |
|-----------|-------|-----|
| {Component/module} | {working | partial | missing | deprecated} | {gap vs desired state} |
```

For GREENFIELD, emit only `build_context` and `summary` unless a real existing
artifact constrains implementation. For BROWNFIELD, include only components the
implementer must account for.

### desired_end_state

```markdown
## desired_end_state
- summary: {target implementation state}

### phase_summary
| phase_id | target_capability | change_required |
|----------|-------------------|-----------------|
| phase_1 | {capability/behavior} | {create | modify | replace | remove} |
```

If `phase_summary` would duplicate `implementation_strategy.phase_summary`
exactly, omit this section and keep the detail in `implementation_strategy`.

### implementation_strategy

```markdown
## implementation_strategy
- phasing_approach: {incremental | parallel | sequential}
- total_phases: {N}

### phase_summary
| phase_id | name | stories | files_touched | complexity |
|----------|------|---------|---------------|------------|
| phase_1 | {name} | {N} | {N} | {LOW | MEDIUM | HIGH} |
```

No human-effort fields. Do not emit `estimated_days`, `days`, `effort_hours`,
`sprints`, `weeks`, or any schedule field.

### phases (FULL_SDLC: N phases)

Phase count is derived from research sequencing.

```markdown
## phases

### phase_{N}: {name}
- goal: {one-line}
- story_ids: [{US-XX-XX, ...}]
- prerequisites: [{list}]
- canonical_values_used: [{CV-XX, ...}]
- evidence_refs: [{research refs or audit source IDs}]

#### files_to_create
| file_path | purpose | pattern_ref | pre_applied |
|-----------|---------|-------------|-------------|
| {path} | {why} | {pattern or omitted} | {none | commit/hash + expected marker | existing path + expected marker | passing test name} |

#### files_to_modify
| file_path | changes | pattern_ref | pre_applied |
|-----------|---------|-------------|-------------|
| {path} | {changes} | {pattern or omitted} | {none | commit/hash + expected marker | existing path + expected marker | passing test name} |

#### interface_contracts
| symbol | inputs | outputs | error_handling |
|--------|--------|---------|----------------|
| {function/class/endpoint name} | {exact params/request shape} | {return/response type} | {exact strategy/literals} |

#### implementation_steps
1. {specific executable step with exact identifiers/literals}

#### constraints
- {constraint with exact value, identifier, path, predicate, or configuration key}

#### edge_cases
- {edge case and required handling}

#### fix_pattern
```{lang}
{code - max 25 lines - only when research/ADR supplied an executable pattern}
```

#### pattern_reference
| pattern | adr_ref | example_location |
|---------|---------|------------------|
| {pattern name} | {ADR-XXX} | {existing file showing pattern} |

#### testing_strategy
| test_file | test_cases | type | test_case_id |
|-----------|------------|------|--------------|
| {path} | {cases} | {unit | integration | e2e} | {FTC id(s) | [derived]} |

`test_case_id` carries the upstream FTC id(s) each row satisfies when `test_cases_path`
was supplied (else `[derived]`). The planner owns `type` (level); `[FE]`/journey FTCs
deferred to e2e are marked `type: e2e` + `covered_by: qe-web-automation` and listed under
this phase's `out_of_scope`. Every in-scope FTC maps to exactly one row or an exclusion.

#### success_criteria
- automated:
  - {criterion with runnable command or observable result}
- manual:
  - {criterion, only when manual verification is unavoidable}
- performance:
  - {criterion, only when source-backed}

#### rollback
1. {rollback step, only when non-trivial}

#### out_of_scope
- {item}
```

Omit optional subsections when empty. Do not emit `N/A` rows. The `pre_applied`
column may be omitted when `plan_status` is `PROCEED`, `CONDITIONAL`, or
`BLOCKED`. It is required when `plan_status` is `VERIFY_ONLY` or
`PARTIAL_APPLIED`. In `VERIFY_ONLY`, every file row must have non-`none`
evidence. In `PARTIAL_APPLIED`, pre-applied rows have evidence and remaining
rows use `none`.

If `tdad_mode: true`, implementation steps for files with test coverage must
use Red-Green-Refactor ordering: create/update the failing test first, implement
the minimum source change second, then refactor while tests stay green. This is
intentional and must not be reordered by the executor.

### cross_phase

```markdown
## cross_phase

### dependencies
| source_phase | target_phase | dependency | type |
|--------------|--------------|------------|------|
| phase_{N} | phase_{M} | {description} | {blocking | soft} |

### sequence_constraints
1. {constraint - ordered}

### cross_cutting_concerns
| concern | affected_phases | mitigation |
|---------|-----------------|------------|
| {concern} | {phase_1, phase_2, ...} | {mitigation approach} |
```

### risks

```markdown
## risks

### prd_risks
| risk_id | description | likelihood | impact | mitigation | phase_mapping |
|---------|-------------|------------|--------|------------|---------------|
| RISK-01 | {description} | {HIGH | MEDIUM | LOW} | {HIGH | MEDIUM | LOW} | {mitigation} | {phase_N} |

### planning_risks
| risk_id | description | likelihood | impact | mitigation |
|---------|-------------|------------|--------|------------|
| PRISK-01 | {description} | {HIGH | MEDIUM | LOW} | {HIGH | MEDIUM | LOW} | {mitigation} |
```

### deployment

```markdown
## deployment

### migrations
| migration | phase | type | rollback |
|-----------|-------|------|----------|
| {migration name} | phase_{N} | {schema | data | config} | {rollback approach} |

### feature_flags
| flag | purpose | phase |
|------|---------|-------|
| {flag_name} | {why needed} | phase_{N} |

### env_vars
| var | purpose | phase |
|-----|---------|-------|
| {VAR_NAME} | {why needed} | phase_{N} |

### deployment_sequence
1. {step - ordered}
```

Omit `deployment` entirely for domain-only or local-code-only work with no
deployment effect.

### acceptance_criteria (FULL_SDLC)

```markdown
## acceptance_criteria

### functional_criteria
| id | criterion | verification | phase |
|----|-----------|--------------|-------|
| FAC-01 | {criterion} | {how to verify} | phase_{N} |

### nfr_criteria
| id | criterion | target | verification |
|----|-----------|--------|--------------|
| NFR-01 | {criterion} | {measurable target} | {how to verify} |

### go_no_go_gate
- preconditions:
  - {precondition}
- success_criteria:
  - {criterion}
- gherkin:
  - given: {precondition}
    when: {action}
    then: {outcome}
```

---

## Shared Sections

Present in both TASK and FULL_SDLC scopes.

### validation_summary

```markdown
## validation_summary
- validation_status: {PASS | WARN | FAIL}
- quality_score: {0-100}
- blocking_validation_failures: [{Vxx/SV-xx IDs or empty}]
- audit_ref: PLAN-AUDIT-{SESSION_ID}.md#validation-results
```

Full validation tables, correction logs, and quality narrative live in
`PLAN-AUDIT`, not in `PLAN-SPEC`.

### open_questions

```markdown
## open_questions

### pending_inputs
| id | phase_ref | type | section | item_id | field | impact | question | fallback_behavior | source_ref |
|----|-----------|------|---------|---------|-------|--------|----------|-------------------|------------|
| PI-01 | {phase_1 | phase_1, phase_2 | all} | {missing_data | ambiguity | conflict} | {section name} | {item ID} | {field name} | {HIGH | MEDIUM | LOW} | {needed answer} | {narrowest backward-compatible behavior or BLOCKED} | {upstream ref} |

### implementation_gaps
| id | phase_ref | type | item_id | description | source_ref |
|----|-----------|------|---------|-------------|------------|
| IG-01 | {phase_1 | phase_1, phase_2 | all} | {missing_detail | unclear_requirement | untested_path} | {item ID} | {gap description} | {upstream ref} |

### assumptions_to_validate
| id | phase_ref | assumption | item_id | impact_if_wrong | validation_method | source_ref |
|----|-----------|------------|---------|-----------------|-------------------|------------|
| ASM-01 | {phase_1 | phase_1, phase_2 | all} | {assumption text} | {item ID} | {consequence} | {how to validate} | {upstream ref} |

### upstream_gaps_carried_forward
| id | source_ref | description | local_coverage | recommendation |
|----|------------|-------------|----------------|----------------|
| UG-01 | {upstream artifact ref} | {gap description} | {what this plan does about it} | {action} |

### summary
- total_phases: {N}
- pending_inputs: {N}
- implementation_gaps: {N}
- assumptions: {N}
- upstream_gaps: {N}
- status: {PROCEED | CONDITIONAL | BLOCKED | VERIFY_ONLY | PARTIAL_APPLIED}
```

`impact` is rated by implementability. A pending input may be MEDIUM or LOW only
when `fallback_behavior` gives the executor a deterministic narrowest
backward-compatible action. If `fallback_behavior` is empty or `BLOCKED`, impact
is HIGH and `plan_status` is BLOCKED.

---

## Generation Rules

### Section Ordering with Dependencies

```text
HEADER
  -> required_artifacts
  -> canonical_values
  -> plan_status_semantics
  -> security_decisions   (when scope has a security surface; else the one-line "none" declaration)
  -> scope-specific sections
  -> validation_summary
  -> open_questions
```

Dependency chain:
- `task_summary` / `plan_overview` -> no dependencies.
- `scope`, `tech_stack`, `impact` -> depend on task summary or plan overview.
- `phases` -> depends on scope and impact (TASK) or implementation strategy (FULL_SDLC).
- `testing_strategy` -> depends on phases.
- `acceptance_criteria` -> depends on phases and testing strategy.
- `cross_phase`, `risks`, `deployment` -> depend on all phases (FULL_SDLC only).
- `validation_summary` -> depends on validation results recorded in `PLAN-AUDIT`.
- `open_questions` -> depends on all prior sections and is always last.

### Phase Load Contract

When executing `phase_N`, the harness/implementer loads exactly:
1. The `PLAN-SPEC` header.
2. `required_artifacts` rows where `phases_using` is `all` or includes `phase_N`.
3. `canonical_values` rows where `phases_using` is `all` or includes `phase_N`.
4. `plan_status_semantics`.
5. The phase's row from `implementation_strategy.phase_summary` when present.
6. The full `phase_N` block.
7. `cross_phase.dependencies` and `sequence_constraints` rows involving `phase_N`.
8. `acceptance_criteria` rows whose `phase` is `phase_N`.
9. All `open_questions` rows with `impact: HIGH`, plus MEDIUM/LOW rows whose
   `phase_ref` is `all` or includes `phase_N`.

The executor does not load `RESEARCH-SPEC` or `PLAN-AUDIT` by default.

### Per-Item Rules

1. Executable sections contain only implementation-useful data.
2. Complete executable data does not need per-row `status` or `source`; provenance is recorded in `PLAN-AUDIT`.
3. Unresolved data must not be hidden in executable sections. Register it in `open_questions`.
4. Assumptions must be explicit in `open_questions.assumptions_to_validate`.
5. If a pending input lacks deterministic `fallback_behavior`, set `impact: HIGH` and `plan_status: BLOCKED`.
6. If a section or table has no rows, omit it.
7. If a literal is used across phases, put it in `canonical_values`; if it is phase-local, include it directly in that phase.
8. `research_fingerprint` must be `sha256:<64 lowercase hex chars>` or `N/A`; `mtime:` and bare hashes are invalid. If the fingerprint no longer matches `research_source` at execution launch, refuse execution and require re-planning. Proceed only when an explicit harness/operator override allows stale research, and log that override to `PLAN-AUDIT`.
9. If `plan_status` is `VERIFY_ONLY` or `PARTIAL_APPLIED`, `files_to_create` and `files_to_modify` must include `pre_applied` evidence as defined above.

### Phase Decomposition Rules

**TASK scope:**
| complexity | phase_count | rationale |
|------------|-------------|-----------|
| LOW | 1 | Single atomic change set |
| MEDIUM | 2 | Prepare + implement |
| HIGH | 3 | Prepare + implement + stabilize |

**FULL_SDLC scope:**
- Phase count derived from research sequencing document.
- Each phase maps to one or more user stories via `story_ids`.
- Phase boundaries align with deployment/integration checkpoints from research.

### Consolidation Pass Rules

After generating all sections:
1. Verify every unresolved item appears in `open_questions`.
2. Verify every assumption appears in `open_questions.assumptions_to_validate`.
3. Verify `open_questions.summary` counts match actual counts in sub-tables.
4. Verify no executable instruction requires dereferencing `RESEARCH-SPEC`.
5. Re-rate impact by implementability before deriving `plan_status`.
6. Verify `plan_status` is consistent:
   - `PROCEED`: zero HIGH-impact pending inputs.
   - `CONDITIONAL`: pending inputs exist, none are implementability-gating, and every pending input has deterministic `fallback_behavior`.
   - `BLOCKED`: any HIGH-impact pending input or implementability-gating gap.
   - `VERIFY_ONLY`: all planned file rows have non-`none` `pre_applied` evidence.
   - `PARTIAL_APPLIED`: at least one planned file row has non-`none` `pre_applied` evidence and at least one planned file row has `pre_applied: none`.

### REPAIR Mode Mechanics

When `mode: REPAIR`:
1. Load existing PLAN-SPEC file from the discovered path.
2. Parse `failure_feedback` to identify sections requiring changes.
3. Preserve unaffected executable sections unless feedback contradicts them.
4. Re-generate only affected sections.
5. Increment `version`.
6. Re-run consolidation and validation.
7. Update `open_questions.summary`.
8. Write validation detail to `PLAN-AUDIT`.

### Scaling Rules

- TASK scope: always a single PLAN-SPEC file.
- FULL_SDLC scope: single PLAN-SPEC file for up to 7 phases.
- If research indicates more than 7 phases, split into volume files:
  `PLAN-SPEC-{SESSION_ID}-vol1.md`, `PLAN-SPEC-{SESSION_ID}-vol2.md`.
- Every volume repeats the header, `required_artifacts`, `canonical_values`,
  `plan_status_semantics`, `implementation_strategy.phase_summary`,
  `cross_phase`, and complete HIGH-impact `open_questions`.
- MEDIUM/LOW `open_questions` may be partitioned by `phase_ref`; rows with
  `phase_ref: all` are repeated in every volume.
- Phases are partitioned across volumes; acceptance criteria rows are partitioned
  with the phase they verify.
- Cross-volume dependencies must appear in every affected volume's `cross_phase`
  rows so each volume remains executable without a manifest file.
