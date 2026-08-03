# Agent-Native ADR Spec Template

## Template Rules
- **No prose.** Every section is structured data only.
- **No executive summaries.** No "this document provides" paragraphs.
- **No meeting agendas.** Governance content is humanize-spec responsibility.
- **All items carry status.** `complete` | `pending` | `assumption`.
- **All pending items appear in open_questions.** Single registry, no scatter.
- **Source tags are mandatory.** No source → cannot be `complete`.
- **Zero Invention.** Every ADR traces to BCs, NFRs, or FRs. Every tech choice traces to an ADR.
- **Quality attributes use ISO 25010.** No custom quality attribute names.
- **Language:** Generate in DETECTED_LANGUAGE. Section headers in English always.

---

## Architecture: Index + Per-ADR Files

```
ADRS/
├── ADR-SPEC-{SESSION_ID}.md        ← Index: tech stack + catalog + cross-refs + validations (always in context)
├── adrs/
│   ├── adr-001-{category}.md       ← Per-ADR detail: context, options, decision, consequences
│   ├── adr-002-{category}.md
│   └── ...
└── ADR-AUDIT-{SESSION_ID}.md       ← Session metadata
```

**Consumption pattern:**
Downstream agents (architecture, QE) load the INDEX (always) + ONE ADR file (current work).
They never need all ADR details in context simultaneously.

---

## File 1: ADR-SPEC-{SESSION_ID}.md

```markdown
# {project_name} — ADR Spec
version: {NEW_VERSION}
session: {SESSION_ID}
mode: {BUILD | REPAIR}
date: {ISO 8601}
language: {DETECTED_LANGUAGE}
status: {draft | complete}
upstream_sources:
  prd: {prd_path}
  epics: {epics_path}
  boundaries: {boundaries_path}
  domain_docs: {domain_docs_path | "not provided"}

---

## tech_stack_matrix

| category | option_a | option_b | recommended | score | rationale | adr_ref | status | source |
|----------|----------|----------|-------------|-------|-----------|---------|--------|--------|
| backend_language | {option} | {option} | {selected} | {N}/5 | {rationale} | ADR-001 | complete | {ref} |
| frontend_framework | {option} | {option} | {selected} | {N}/5 | {rationale} | ADR-002 | complete | {ref} |
| database_primary | {option} | {option} | {selected} | {N}/5 | {rationale} | ADR-003 | complete | {ref} |
| messaging | {option} | {option} | {selected} | {N}/5 | {rationale} | ADR-004 | complete | {ref} |
| container_orchestration | {option} | {option} | {selected} | {N}/5 | {rationale} | ADR-005 | complete | {ref} |
| ci_cd | {option} | {option} | {selected} | {N}/5 | {rationale} | ADR-006 | complete | {ref} |
| monitoring | {option} | {option} | {selected} | {N}/5 | {rationale} | ADR-007 | assumption | {ref} |
| auth_identity | {option} | {option} | {selected} | {N}/5 | {rationale} | ADR-008 | complete | {ref} |
| api_protocol | {option} | {option} | {selected} | {N}/5 | {rationale} | ADR-009 | complete | {ref} |
| caching | {option} | {option} | {selected} | {N}/5 | {rationale} | ADR-010 | complete | {ref} |
| search | {option} | {option} | {selected} | {N}/5 | {rationale} | ADR-011 | assumption | {ref} |
| storage | {option} | {option} | {selected} | {N}/5 | {rationale} | ADR-012 | complete | {ref} |

---

## adr_catalog

### ADR-001: {title}
- adr_id: ADR-001
- category: {backend_language | frontend_framework | database_primary | messaging | container_orchestration | ci_cd | monitoring | auth_identity | api_protocol | caching | search | storage}
- title: {decision_title}
- decision_summary: {one-line decision}
- technologies: {tech_1}, {tech_2}
- affected_bcs: BC-01, BC-02
- cross_refs: ADR-003, ADR-009
- quality_attributes: {performance | security | maintainability | reliability | portability | compatibility | usability | functional_suitability}
- file_ref: adrs/adr-001-{category}.md
- status: complete
- source: boundaries/{ref}, prd/{ref}

### ADR-002: {title}
- adr_id: ADR-002
- category: {category}
- title: {decision_title}
- decision_summary: {one-line decision}
- technologies: {tech_1}
- affected_bcs: BC-01, BC-03
- cross_refs: ADR-001
- quality_attributes: {quality_attributes}
- file_ref: adrs/adr-002-{category}.md
- status: complete
- source: boundaries/{ref}, prd/{ref}

---

## cross_reference_map

| adr_id | related_adrs | relationship_type | description | status |
|--------|-------------|-------------------|-------------|--------|
| ADR-001 | ADR-003, ADR-009 | {constrains | enables | conflicts | supersedes | complements} | {description} | complete |
| ADR-002 | ADR-001 | {relationship_type} | {description} | complete |
| ADR-003 | ADR-001, ADR-004 | {relationship_type} | {description} | complete |

---

## impact_matrix

| adr_id | services_affected | nfr_impact | risk_impact | epic_alignment | status | source |
|--------|-------------------|------------|-------------|----------------|--------|--------|
| ADR-001 | SVC-01, SVC-02, SVC-03 | NFR-01: performance, NFR-03: maintainability | {risk_description} | EPIC-01, EPIC-02 | complete | {ref} |
| ADR-002 | SVC-02, SVC-04 | NFR-02: usability | {risk_description} | EPIC-01, EPIC-03 | complete | {ref} |

---

## validations

| check | expected | actual | status | details |
|-------|----------|--------|--------|---------|
| bc_coverage | all BCs have at least one ADR | {N}/{N} | {PASS | FAIL} | {gaps if any} |
| prd_assumption_carryforward | all PRD assumptions acknowledged | {N}/{N} | {PASS | FAIL} | {gaps if any} |
| prd_risk_carryforward | all PRD risks with tech implications addressed | {N}/{N} | {PASS | FAIL} | {gaps if any} |
| nfr_traceability | all NFRs with tech implications have ADR coverage | {N}/{N} | {PASS | FAIL} | {gaps if any} |
| category_completeness | all 12 decision categories evaluated | {N}/12 | {PASS | FAIL} | {missing categories} |
| cross_reference_integrity | all cross-refs resolve to existing ADRs | {N}/{N} | {PASS | FAIL} | {broken refs} |
| tech_stack_consistency | no conflicting technology choices | 0 conflicts | {N} conflicts | {conflicts if any} |

validations_passed: {N}/7
overall_status: {PASS | FAIL}
fail_reasons: [{reason}]

---

## open_questions

### pending_inputs
| id | description | impact | source |
|----|-------------|--------|--------|
| OQ-XX | {missing input description} | {what ADR sections are affected} | {which upstream artifact} |

### coverage_gaps
| id | type | ref_id | description | affected_section |
|----|------|--------|-------------|------------------|
| GAP-XX | {uncovered_bc | unmapped_nfr | missing_category} | {BC/NFR/category ID} | {what is missing} | {section} |

### alignment_gaps
| id | type | ref_id | description | affected_section |
|----|------|--------|-------------|------------------|
| AG-XX | {tech_conflict | cross_ref_broken | epic_unaligned} | {ADR/SVC/EPIC ID} | {what is misaligned} | {section} |

### assumptions_to_validate
| id | assumption | section | rationale | confidence | validation_needed |
|----|-----------|---------|-----------|------------|-------------------|
| ASM-XX | {assumption text} | {section} | {why assumed} | {high | medium | low} | {what to validate} |

### upstream_gaps_carried_forward
| id | origin | description | impact_on_adrs |
|----|--------|-------------|----------------|
| UG-XX | {PRD | Boundaries | Epics} | {gap description} | {how it affects ADRs} |

### summary
- total_adrs: {N}
- categories_covered: {N}/12
- total_cross_references: {N}
- services_impacted: {N}
- coverage_gaps: {N}
- alignment_gaps: {N}
- pending_inputs: {N}
- assumptions: {N}
- upstream_gaps: {N}
- validations_passed: {N}/7
- status: {draft | complete}
```

---

## File 2: adrs/adr-{NNN}-{category}.md (Per-ADR Detail)

```markdown
# {project_name} — ADR-{NNN}: {Title}
adr_id: ADR-{NNN}
category: {category}
date: {ISO 8601}
status: {proposed | accepted | deprecated | superseded}

---

## context
- problem: {problem_statement}
- constraints: {constraint_1}, {constraint_2}
- affected_bcs: BC-XX, BC-YY
- affected_nfrs: NFR-XX, NFR-YY
- source: {ref}

---

## options

### Option A: {option_name}
- technology: {tech_name}
- version: {version | latest}
- pros: {pro_1}, {pro_2}, {pro_3}
- cons: {con_1}, {con_2}
- score: {N}/5
- status: rejected

### Option B: {option_name}
- technology: {tech_name}
- version: {version | latest}
- pros: {pro_1}, {pro_2}, {pro_3}
- cons: {con_1}, {con_2}
- score: {N}/5
- status: accepted

---

## decision
- chosen: Option {X}: {option_name}
- rationale: {detailed_rationale}
- quality_attributes: {ISO 25010 attributes affected}
- tradeoffs: {tradeoff_1}, {tradeoff_2}
- reversibility: {low | medium | high}

---

## consequences

### positive
- {positive_consequence_1}
- {positive_consequence_2}

### negative
- {negative_consequence_1}
- {negative_consequence_2}

### risks
- {risk_1} | mitigation: {mitigation_approach}
- {risk_2} | mitigation: {mitigation_approach}

---

## compliance
- nfr_alignment: NFR-XX ({how_addressed}), NFR-YY ({how_addressed})
- bc_alignment: BC-XX ({how_it_serves}), BC-YY ({how_it_serves})
- epic_alignment: EPIC-XX, EPIC-YY
- source: {ref}
```

---

## File 3: ADR-AUDIT-{SESSION_ID}.md

```markdown
# {project_name} — ADR Session Audit
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
| Boundaries | {boundaries_path} | Loaded |
| Domain Docs | {domain_docs_path} | Loaded / Not provided |

---

## generation_log

| adr_id | category | title | options_evaluated | decision | status |
|--------|----------|-------|-------------------|----------|--------|

---

## validation_summary

| check | result | details |
|-------|--------|---------|
(7 checks)

---

## change_log

(REPAIR mode only)

| version | directive | target | change | impact |
|---------|-----------|--------|--------|--------|
```

---

## Generation Rules

### Section Ordering
Generate sections in this order (matches dependency chain):
1. `tech_stack_matrix` — evaluate all 12 categories
2. `adr_catalog` — create per-ADR entries with cross-refs
3. `cross_reference_map` — map inter-ADR relationships
4. `impact_matrix` — map ADR impact on services, NFRs, risks, epics
5. `validations` — verify completeness (audit consumer)
6. `open_questions` — consolidation pass (always last)

### Per-ADR Generation
For each decision category:
- Create `adrs/adr-{NNN}-{category}.md` with context, options, decision, consequences
- Update `adr_catalog` with summary and file_ref
- Each ADR must trace to affected BCs and quality attributes
- Cross-references must be bidirectional

### Decision Categories (12 standard)
backend_language, frontend_framework, database_primary, messaging,
container_orchestration, ci_cd, monitoring, auth_identity,
api_protocol, caching, search, storage.
Add project-specific categories if domain requires them.

### REPAIR Mode Mechanics
- Load existing spec → identify sections targeted by REPAIR_DIRECTIVES
- Apply directives surgically to targeted ADRs only
- Preserve untargeted ADR files exactly
- Re-run validations after all repairs
- Re-consolidate open_questions
- Increment patch version

### Quality Attribute Mapping (ISO 25010)
- performance, security, maintainability, reliability, portability,
  compatibility, usability, functional_suitability
- Every ADR must list affected quality attributes from this set
