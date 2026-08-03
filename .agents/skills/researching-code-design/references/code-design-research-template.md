# Code Design Research — Agent-Native Spec Template

## Template Rules
- **No prose.** Every section is structured data only.
- **No narrative.** No motivational text, no context paragraphs, no Quick Navigation.
- **All items carry status.** `complete` | `pending` | `assumption`.
- **All gaps in open_questions.** Single registry, no scatter.
- **Source tags mandatory.** No source → cannot be `complete`.
- **Language:** Generate in DETECTED_LANGUAGE. Section headers in English always.
- **Technology Fidelity:** Use EXACT names/versions from ADRs or source code. Never generalize.
- **NFR IDs:** Use PRD ORIGINAL IDs verbatim. Never renumber.
- **Anti-Fade:** Last section must match depth of first section.
- **Paths:** Record every `sources:` value and every `context_inventory` artifact path RELATIVE to the workspace root (strip the workspace-root prefix). Never emit absolute filesystem paths — they are not portable across environments.

---

## Spec File Structure

```markdown
# {project_name} — Code Design Research Spec
version: {version}
session: {session_id}
operation_mode: {BUILD | REPAIR}
build_context: {GREENFIELD | BROWNFIELD}
date: {ISO 8601}
language: {detected_language}
sources:
  prd: {prd_path}
  epics: {epics_path}
  stories: {user_stories_path}
  architecture: {target_architecture}
  adrs: {adr_path}
  domains: {domain_boundaries_path}
  source_code: {source_path | N/A}
  context_pack: {context_pack_path | N/A}
  test_strategy: {test_strategy_path | N/A}
  test_planning: {test_planning_path | N/A}
  test_cases: {test_cases_path | N/A}
  legacy_docs: {legacy_docs_path | N/A}
contract_modes:
  prd: {structured | partial | unstructured | N/A}
  epics: {structured | partial | unstructured | N/A}
  stories: {structured | partial | unstructured | N/A}
upstream_hashes:
  prd_content_hash: {sha256:<64 lowercase hex> | invalid | N/A}
  epics_prd_source_hash: {sha256:<64 lowercase hex> | invalid | N/A}
  stories_prd_source_hash: {sha256:<64 lowercase hex> | invalid | N/A}
  stories_epics_source_hash: {sha256:<64 lowercase hex> | invalid | N/A}
status: {draft | complete}

---

## executive_metrics

- mode: {GREENFIELD | BROWNFIELD | REPAIR}
- overall_complexity: {LOW | MEDIUM | HIGH}
- complexity_rationale: {source-based rationale}
- technical_risk: {LOW | MEDIUM | HIGH}
- integration_risk: {LOW | MEDIUM | HIGH}
- security_risk: {LOW | MEDIUM | HIGH}
- counts:
  - functional_requirements: {N}
  - non_functional_requirements: {N}
  - user_stories: {N}  # ACTUAL count from STORY_CONTEXT
  - bounded_contexts: {N}
  - adrs: {N}
  - epics: {N}
  - personas: {N}
  - kpis: {N}
  - jtbds: {N}
  - risks_prd: {N}
  - risks_architecture: {N}
  - assumptions_prd: {N}
  - assumptions_research: {N}
  - core_files: {N}
  - test_files: {N}

### persona_capability_map
| persona | capabilities | epic_coverage | jtbd_fulfilled | source |
|---------|-------------|---------------|----------------|--------|
| {Persona 1} | {capabilities} | {EPIC-XX, ...} | {JTBD-XX, ...} | {ref} |

---

## context_inventory

### artifact_inventory
| artifact | status | path | extraction_summary |
|----------|--------|------|--------------------|
| PRD | {loaded | missing} | {path} | {N} FRs, {N} NFRs, {N} JTBDs, {N} KPIs |
| Epics | {loaded | missing} | {path} | {N} Epics across {N} tiers |
| User Stories | {loaded | missing} | {path} | {N} stories (ACTUAL COUNT) |
| Architecture | {loaded | missing} | {path} | {N} services, {N} diagrams |
| ADRs | {loaded | missing} | {path} | {N} decisions |
| Domain Boundaries | {loaded | missing} | {path} | {N} bounded contexts |
| Source Code | {present | absent} | {path | N/A} | {summary | N/A} |
| Context Pack | {present | absent} | {path | N/A} | {files found | N/A} |
| Test Strategy | {present | absent} | {path | N/A} | {summary | N/A} |
| Test Planning | {present | absent} | {path | N/A} | {summary | N/A} |
| Test Cases | {present | absent} | {path | N/A} | {summary | N/A} |
| Legacy Docs | {present | absent} | {path | N/A} | {summary | N/A} |

### contract_inventory
| artifact | contract_mode | structured_fields_used | cross_check_required | hash_format | hash_status | notes |
|----------|---------------|------------------------|----------------------|-------------|-------------|-------|
| PRD | {structured | partial | unstructured | N/A} | {literal_registry, open_questions, content_hash | N/A} | {yes | no} | {valid_sha256 | invalid | N/A} | {match | mismatch_accepted | mismatch_blocked | N/A} | {notes} |
| Epics | {structured | partial | unstructured | N/A} | {prd_id_ownership, open_questions, prd_source_hash | N/A} | {yes | no} | {valid_sha256 | invalid | N/A} | {match | mismatch_accepted | mismatch_blocked | N/A} | {notes} |
| User Stories | {structured | partial | unstructured | N/A} | {literal_refs, fallback_refs, open_questions, source_hashes | N/A} | {yes | no} | {valid_sha256 | invalid | N/A} | {match | mismatch_accepted | mismatch_blocked | N/A} | {notes} |

### accepted_hash_overrides
| artifact | declared_hash | observed_hash | verification_result | decision |
|----------|---------------|---------------|---------------------|----------|
| {PRD | Epics | User Stories} | {sha256} | {sha256} | {all recorded dependencies still present identically} | {accepted in this research audit only} |

### build_scope
| component | priority | epic | bounded_context | fr_coverage | status |
|-----------|----------|------|-----------------|-------------|--------|
| {Component 1} | {must_have | should_have} | {EPIC-XX} | {BC-XX} | {FR-XX, FR-YY} | {complete | pending} |

### existing_code_analysis (BROWNFIELD only)
| component | status | location | gap | source |
|-----------|--------|----------|-----|--------|
| {Component} | {complete | partial | missing} | {file path} | {gap description} | {source_path} |

---

## architecture

- architecture_style: {style from ADR-XXX}
- architecture_style_source: {ADR-XXX}

### bc_service_map
| bc_id | bc_name | subdomain_type | responsibility | service_id | source |
|-------|---------|----------------|----------------|------------|--------|
| {BC-XX} | {name} | {core | supporting | generic} | {responsibility} | {SVC-XX} | {ref} |

### technology_stack
| layer | technology | version | adr_ref | purpose | status |
|-------|------------|---------|---------|---------|--------|
| {Layer} | {EXACT name} | {EXACT version} | {ADR-XXX} | {purpose} | {complete | assumption} |

### package_structure
```
{project structure with directories and key files — from ADR/coding standards}
```

### communication_patterns
| source | target | pattern | protocol | adr_ref | status |
|--------|--------|---------|----------|---------|--------|
| {Source} | {Target} | {sync | async} | {protocol} | {ADR-XXX} | {complete | assumption} |

### design_decisions
| decision | rationale | adr_ref |
|----------|-----------|---------|
| {Decision} | {Why} | {ADR-XXX} |

---

## requirements_traceability

### fr_component_matrix
| fr_id | description | priority | component | bounded_context | epic | stories | status |
|-------|-------------|----------|-----------|-----------------|------|---------|--------|
| {FR-XX} | {from PRD} | {priority} | {component} | {BC-XX} | {EPIC-XX} | {US-XX-XX, ...} | {complete | pending} |

### jtbd_capability_map
| jtbd_id | description | capabilities | epics | components | status |
|---------|-------------|-------------|-------|------------|--------|
| {JTBD-XX} | {from PRD} | {capabilities} | {EPIC-XX, ...} | {components} | {complete | pending} |

### kpi_component_map
| kpi_id | description | target | measurement_method | components | status |
|--------|-------------|--------|-------------------|------------|--------|
| {KPI-XX} | {from PRD} | {target} | {method | PENDING} | {components} | {complete | pending} |

---

## nfr_implementation

### nfr_targets (PRD Original IDs — NEVER RENUMBER)
| nfr_id | description | target | implementation_approach | components | adr_ref | status |
|--------|-------------|--------|------------------------|------------|---------|--------|
| {NFR-XX} | {PRD description verbatim} | {target} | {approach} | {components} | {ADR-XXX} | {complete | pending} |

### performance_targets
| component | target | measurement | nfr_ref | status |
|-----------|--------|-------------|---------|--------|
| {Component} | {target} | {how measured} | {NFR-XX} | {complete | pending} |

### availability_targets
| component | target | notes | nfr_ref | status |
|-----------|--------|-------|---------|--------|
| {Component} | {target} | {notes} | {NFR-XX} | {complete | pending} |

---

## implementation_sequencing

### phase_1_mvp
- epics: [{EPIC-XX}, {EPIC-YY}]
- priority: must_have
- story_sequence:
  1. {US-XX-XX} — depends_on: none
  2. {US-XX-XX} — depends_on: {US-YY-YY}
  3. {US-XX-XX} — depends_on: {US-YY-YY}, {US-ZZ-ZZ}

### phase_2
- epics: [{EPIC-XX}, {EPIC-YY}]
- priority: should_have
- story_sequence:
  1. {US-XX-XX} — depends_on: {phase_1 stories}

### phase_N (repeat as needed)

---

## dependencies

### technical_dependencies
| dependency | type | purpose | required_by | adr_ref | status |
|------------|------|---------|-------------|---------|--------|
| {Dependency} | {runtime | build | library} | {purpose} | {component} | {ADR-XXX} | {complete | assumption} |

### internal_dependencies
| component | depends_on | relationship | status |
|-----------|------------|--------------|--------|
| {Component} | {Dependency} | {description} | {complete | assumption} |

### external_dependencies
| dependency | type | purpose | component | status |
|------------|------|---------|-----------|--------|
| {External dep} | {API | service | library} | {purpose} | {component} | {complete | pending} |
(or: "- none" if no external dependencies)

---

## complexity_assessment

### component_complexity
| component | lines_estimate | complexity | risk | bounded_context | source |
|-----------|---------------|------------|------|-----------------|--------|
| {Component} | {estimate} | {LOW | MEDIUM | HIGH} | {LOW | MEDIUM | HIGH} | {BC-XX} | {ref} |

### hotspots
| area | complexity_reason | mitigation | status |
|------|-------------------|------------|--------|
| {Area} | {why complex} | {mitigation approach} | {complete | assumption} |

### implementation_scale
| phase | stories | complexity | risk_level |
|-------|---------|------------|------------|
| phase_1 | {N} | {LOW | MEDIUM | HIGH} | {LOW | MEDIUM | HIGH} |
| phase_N | {N} | {LOW | MEDIUM | HIGH} | {LOW | MEDIUM | HIGH} |
| total | {N} | {overall} | {overall} |

---

## security_assessment

### security_architecture
| layer | control | implementation | adr_ref | status |
|-------|---------|----------------|---------|--------|
| {Layer} | {Control} | {implementation} | {ADR-XXX} | {complete | pending} |

### security_controls
| control | required | notes | status |
|---------|----------|-------|--------|
| {Control} | {yes | no | future} | {notes} | {complete | pending} |

### security_risks
| risk_id | risk | likelihood | impact | mitigation | status |
|---------|------|------------|--------|------------|--------|
| {SEC-RSK-XX} | {risk} | {L | M | H} | {L | M | H} | {mitigation} | {complete | assumption} |

### security_requirements
- {REQ-1}: {requirement} — source: {ADR-XXX}
- {REQ-N}: {requirement} — source: {ref}

---

## patterns_conventions

### coding_conventions
| convention | specification | example | source |
|------------|---------------|---------|--------|
| {Convention} | {spec} | {example} | {coding-standards | ADR-XXX} |

### architecture_patterns
| pattern | usage | source |
|---------|-------|--------|
| {Pattern} | {where/how used} | {arch-standards | ADR-XXX} |

### testing_conventions
| test_type | naming | focus | source |
|-----------|--------|-------|--------|
| {Type} | {convention} | {focus area} | {ref} |

### error_handling
| layer | pattern | example | source |
|-------|---------|---------|--------|
| {Layer} | {pattern} | {example} | {ref} |

---

## acceptance_criteria

### phase_1_criteria
| story_id | ac_summary | nfr_constraints | status |
|-----------|-----------|-----------------|--------|
| {US-XX-XX} | {summary from User Stories AC} | {NFR-XX | none} | {complete | pending} |

### phase_1_gate
- type: go_no_go
- preconditions: [{KPI-XX criteria}]
- success_criteria: [{mapped to KPI-XX}]
- gherkin: |
    Given {preconditions from KPIs}
    When {gate review}
    Then {success criteria mapped to KPI-XX}

### phase_2_criteria (repeat pattern)

---

## risks

### prd_risks (MANDATORY — every RSK-XX from PRD)
| risk_id | description | likelihood | impact | mitigation | mitigating_adrs | status |
|---------|-------------|------------|--------|------------|-----------------|--------|
| {RSK-XX} | {PRD description verbatim} | {PRD value} | {PRD value} | {PRD + research mitigation} | {ADR-XXX, ...} | {complete | pending} |

### architecture_risks
| risk_id | description | likelihood | impact | mitigation | status |
|---------|-------------|------------|--------|------------|--------|
| {ARCH-RSK-XX} | {research-identified risk} | {L | M | H} | {L | M | H} | {mitigation} | {complete | assumption} |

---

## assumptions

### prd_assumptions (MANDATORY — every ASM-XX from PRD)
| asm_id | description | risk_if_wrong | validation_method | status |
|--------|-------------|---------------|-------------------|--------|
| {ASM-XX} | {PRD description verbatim} | {PRD value} | {validation approach} | {active | validated} |

### research_assumptions
| asm_id | description | risk_if_wrong | validation_method | status |
|--------|-------------|---------------|-------------------|--------|
| {RES-ASM-XX} | {research-identified assumption} | {risk} | {how to validate} | {assumption} |

---

## file_specifications

### core_files
| file_path | purpose | bounded_context | stories | design_ref | status |
|-----------|---------|-----------------|---------|------------|--------|
| {exact path per conventions} | {purpose} | {BC-XX} | {US-XX-XX} | {DESIGN_CONTEXT.screens.{name} \| DESIGN_CONTEXT.images.files[{filename}] \| null} | {complete | pending} |

`design_ref` rules:
- UI-bearing file (component, screen, route, layout) → MUST be non-null when DESIGN_CONTEXT is non-null. Use `DESIGN_CONTEXT.screens.{name}` for screen/component files, `DESIGN_CONTEXT.images.files[{filename}]` when a specific image asset is the primary visual source, or both joined with `+` when applicable.
- UI-bearing file AND DESIGN_CONTEXT is null → set `design_ref: null` AND register an open_questions entry: "Design spec missing for {file_path} — implementing from prose".
- Non-UI file (service, repository, controller, migration, config) → `design_ref: null` (always).

### test_files
| file_path | purpose | coverage_target | status |
|-----------|---------|-----------------|--------|
| {exact test file path} | {purpose} | {unit | integration | e2e} | {complete | pending} |

---

## test_strategy

### test_pyramid
| level | coverage_pct | focus | source |
|-------|-------------|-------|--------|
| unit | {%} | {focus} | {ref} |
| integration | {%} | {focus} | {ref} |
| e2e | {%} | {focus} | {ref} |

### test_case_coverage (if test_cases_path provided)
| story_id | test_cases | coverage_status |
|-----------|-----------|-----------------|
| {US-XX-XX} | {TC-XX, TC-YY} | {covered | gap} |

### test_commands
- unit: {exact command per tech stack}
- integration: {exact command}
- e2e: {exact command}
- coverage: {exact command}

---

## recommendations

### key_findings
| finding_id | dimension | value | source | status |
|-----------|-----------|-------|--------|--------|
| KF-01 | mode | {GREENFIELD | BROWNFIELD} | {source_path presence} | complete |
| KF-02 | architecture | {architecture_style} | {ADR-XXX} | {complete | assumption} |
| KF-03 | technology | {primary stack summary} | {ADR refs} | {complete | assumption} |
| KF-04 | security | {security posture summary} | {ADR refs} | {complete | assumption} |
| KF-05 | complexity | {overall_complexity rating} | {analysis refs} | {complete | assumption} |

### implementation_recommendations
| rec_id | recommendation | source | affects | priority | status |
|--------|---------------|--------|---------|----------|--------|
| REC-01 | {recommendation} | {ref} | {sections/components affected} | {high | medium | low} | {complete | assumption} |
| REC-NN | {recommendation} | {ref} | {affected} | {priority} | {status} |

### success_criteria
| criterion | measurement | kpi_ref | status |
|-----------|-------------|---------|--------|
| {Criterion} | {how measured} | {KPI-XX} | {complete | pending} |

---

## sources

| ref_id | document | path | purpose |
|--------|----------|------|---------|
| REF-01 | PRD | {prd_path} | Product requirements, business value |
| REF-02 | Architecture | {target_architecture} | Architecture decisions, service catalog |
| REF-03 | ADRs | {adr_path} | Architecture decision records |
| REF-04 | User Stories | {user_stories_path} | User stories, acceptance criteria |
| REF-05 | Epics | {epics_path} | Epic definitions and priorities |
| REF-06 | Domain Boundaries | {domain_boundaries_path} | Bounded contexts, ubiquitous language |
| REF-07 | Context Pack | {context_pack_path | N/A} | Tech policy, arch standards |
| REF-08 | Test Strategy | {test_strategy_path | N/A} | Test strategy |
| REF-NN | {additional} | {path} | {purpose} |

---

## validations

| check | result | details |
|-------|--------|---------|
| fr_coverage | {pass | fail} | {N}/{total} FRs mapped |
| nfr_id_preservation | {pass | fail} | {N}/{total} NFRs with original IDs |
| jtbd_coverage | {pass | fail} | {N}/{total} JTBDs mapped |
| kpi_coverage | {pass | fail} | {N}/{total} KPIs mapped |
| rsk_carry_forward | {pass | fail} | {N}/{total} PRD risks carried |
| asm_carry_forward | {pass | fail} | {N}/{total} PRD assumptions carried |
| persona_coverage | {pass | fail} | {N}/{total} personas covered |
| technology_fidelity | {pass | fail} | {N} refs checked |
| api_path_fidelity | {pass | fail} | {N} paths checked |
| upstream_gap_surfacing | {pass | fail} | {N} items surfaced |
| story_count | {pass | fail} | actual={N} reported={N} |
| anti_fade | {pass | fail} | depth comparison |
| adr_cross_reference | {pass | fail} | {N}/{total} ADRs referenced |
| section_completeness | {pass | fail} | {N}/19 sections |
| cross_section_consistency | {pass | fail} | IDs, dates consistent |
| id_uniqueness | {pass | fail} | no duplicates |
| source_tags | {pass | fail} | {N}/{total} items with source |
| bias_detection | {pass | fail} | {N} biases found |
| contract_mode_detection | {pass | fail} | PRD={mode}; Epics={mode}; Stories={mode} |
| structured_cross_check | {pass | fail | N/A} | partial-mode discrepancies={N} |
| hash_forward_verification | {pass | fail | N/A} | accepted_hash_overrides={N}; blocked={N} |

---

## open_questions

### pending_inputs
| id | affected_ids | blocking | type | section | item_id | field | impact | fallback_behavior | source_ref |
|----|--------------|----------|------|---------|---------|-------|--------|-------------------|------------|
| PI-{NN} | {FR-XX, US-XX-XX | all | N/A} | {yes | no} | {missing | unclear} | {section_name} | {item_id} | {field} | {impact description} | {fallback or BLOCKED} | {upstream ref} |

### evidence_gaps
| id | affected_ids | type | item_id | description | source_ref | decision |
|----|--------------|------|---------|-------------|------------|----------|
| EG-{NN} | {FR-XX, LIT-XX, US-XX-XX | all | N/A} | {traceability_gap | coverage_gap | orphan_ref | structured_discrepancy | hash_dependency_gap} | {item_id} | {description} | {ref} | {accepted | blocks | carried_forward} |

### assumptions_to_validate
| id | affected_ids | blocking | assumption | item_id | impact_if_wrong | validation_method | fallback_behavior | source_ref |
|----|--------------|----------|------------|---------|-----------------|-------------------|-------------------|------------|
| AV-{NN} | {FR-XX, US-XX-XX | all | N/A} | {yes | no} | {assumption text} | {item_id} | {impact} | {method} | {fallback or BLOCKED} | {ref} |

### upstream_gaps_carried_forward
| id | affected_ids | blocking | source | description | local_coverage | fallback_behavior | recommendation |
|----|--------------|----------|--------|-------------|----------------|-------------------|----------------|
| UG-{NN} | {FR-XX, EPIC-XX, US-XX-XX | all | N/A} | {yes | no} | {PRD | Epics | Stories | Architecture} | {gap description} | {none | partial: explanation} | {fallback or BLOCKED} | {recommendation} |

### summary
- total_sections: 19
- pending_inputs: {N}
- evidence_gaps: {N}
- assumptions_to_validate: {N}
- upstream_gaps: {N}
- status: {draft | complete}
```

---

## Generation Rules

### Section Ordering (with dependencies)
```
executive_metrics         ← needs all contexts for counts
context_inventory         ← needs all input paths, contract_modes, upstream_hash decisions
architecture              ← needs ARCH, ADR, DOMAIN contexts
requirements_traceability ← needs PRD_CONTEXT (FR, JTBD, KPI) + prd_id_ownership when available
nfr_implementation        ← needs PRD nfr_ids + ARCH_CONTEXT
implementation_sequencing ← needs EPIC tiers + STORY_CONTEXT
dependencies              ← needs ARCH communication + ADR
complexity_assessment     ← needs all sections above
security_assessment       ← needs ARCH + ADR
patterns_conventions      ← needs ADR + SOURCE + context_pack
acceptance_criteria       ← needs STORY_CONTEXT + KPI mappings
risks                     ← needs PRD rsk_ids + research analysis
assumptions               ← needs PRD asm_ids + research analysis
file_specifications       ← needs architecture + patterns + STORY
test_strategy             ← needs TEST contexts + file_specs
recommendations           ← needs all sections above
sources                   ← needs all input paths
validations               ← needs all sections (runs checks)
open_questions            ← ALWAYS LAST
```

### Per-Item Rules
- Every item MUST have `status`: `complete` | `pending` | `assumption`
- Every item with `status: complete` MUST have `source` tag
- Contract mode is detected automatically per artifact. `unstructured` is valid
  and uses prose derivation; `partial` uses declared structured rows plus a
  prose cross-check; `structured` may skip prose cross-check only when upstream
  completeness is certified.
- SHA-256 mismatches are handled by forward-verifying recorded dependencies
  (IDs, literals, fallbacks, ownership rows). Accepted mismatches are recorded
  in this research run only, never written back to upstream artifacts.
- Every `pending` item → registered in open_questions.pending_inputs
- Every `assumption` item → registered in open_questions.assumptions_to_validate
- IDs from PRD (FR-XX, NFR-XX, RSK-XX, ASM-XX, JTBD-XX, KPI-XX) MUST be preserved verbatim

### Consolidation Pass (before open_questions)
After all sections are generated:
1. Scan ALL sections for items with status: pending → collect into pending_inputs
2. Scan ALL sections for items with status: assumption → collect into assumptions_to_validate
3. Scan for orphan references (IDs referenced but not defined) → collect into evidence_gaps
4. Load upstream open_questions from PRD, Epics, Stories, Architecture specs (if agent-native) → collect into upstream_gaps_carried_forward
5. Compute summary counts
6. Derive spec header status: `complete` if all counts are zero, else `draft`

### REPAIR Mode
- Load existing spec file
- Apply REPAIR_DIRECTIVES to targeted sections/item IDs
- Preserve untargeted content verbatim
- Preserve existing IDs. New items: max(existing) + 1. Retired IDs: never reuse.
- IF upstream data changed → rebuild affected downstream sections
- ALWAYS rebuild open_questions from scratch (reflects current state)
- ALWAYS rebuild validations from scratch
- Increment version, log changes in audit trail

### Scaling
- Estimated items: 15-80 FRs, 5-50 epics, 20-400 stories, 5-30 ADRs, 5-15 BCs
- Lines per item: ~2-3 (structured table row)
- Typical output: 600-2,000 lines
- Threshold: 150+ stories OR estimated output > 3,000 lines → consider manifest + per-section files
- Single file sufficient at all expected scales for typical SDLC projects

### Progressive Input Loading
Due to massive input context (6+ required artifacts):
- PHASE A: Load all contexts → generate sections 1-10
- PHASE B: Reload flushed data as needed → generate sections 11-19
- IF context < 60% at PHASE A end → skip PHASE B split, continue in single pass
