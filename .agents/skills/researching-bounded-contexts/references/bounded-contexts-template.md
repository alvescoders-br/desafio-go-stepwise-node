# Agent-Native Bounded Contexts Spec Template

## Template Rules
- **No prose.** Every section is structured data only.
- **No executive summaries.** No "this document provides" paragraphs.
- **No meeting agendas.** Governance content is humanize-spec responsibility.
- **All items carry status.** `complete` | `pending` | `assumption`.
- **All pending items appear in open_questions.** Single registry, no scatter.
- **Source tags are mandatory.** No source → cannot be `complete`.
- **Zero Invention.** Every BC traces to FRs. Every service traces to a BC.
- **Language:** Generate in DETECTED_LANGUAGE. Section headers in English always.

---

## Architecture: Index + Per-Context Files

```
BOUNDARIES/
├── BOUNDARIES-SPEC-{SESSION_ID}.md   ← Index: catalog + relationships + maps + validations (always in context)
├── contexts/
│   ├── bc-01-{name}.md               ← Per-BC detail: aggregates, entities, events, rules
│   ├── bc-02-{name}.md
│   └── ...
└── BOUNDARIES-AUDIT-{SESSION_ID}.md  ← Session metadata
```

**Consumption pattern:**
Downstream agents (ADR, architecture) load the INDEX (always) + ONE context file (current work).
They never need all BC details in context simultaneously.

---

## File 1: BOUNDARIES-SPEC-{SESSION_ID}.md

```markdown
# {project_name} — Bounded Contexts Spec
version: {NEW_VERSION}
session: {SESSION_ID}
mode: {BUILD | REPAIR}
date: {ISO 8601}
language: {DETECTED_LANGUAGE}
status: {draft | complete}
upstream_sources:
  prd: {prd_path}
  epics: {epics_path}
  architecture: {architecture_path | "not provided"}
  domain_docs: {domain_docs_path | "not provided"}

---

## context_catalog

### BC-01: {bounded_context_name}
- bc_id: BC-01
- name: {bounded_context_name}
- classification: {core | supporting | generic}
- aggregate_count: {N}
- entity_count: {N}
- event_count: {N}
- source_frs: FR-XX, FR-YY
- file_ref: contexts/bc-01-{name}.md
- status: complete
- source: prd/{ref}, epics/{ref}

### BC-02: {bounded_context_name}
- bc_id: BC-02
- name: {bounded_context_name}
- classification: {core | supporting | generic}
- aggregate_count: {N}
- entity_count: {N}
- event_count: {N}
- source_frs: FR-XX
- file_ref: contexts/bc-02-{name}.md
- status: complete
- source: prd/{ref}, epics/{ref}

---

## context_relationships

| from_bc | to_bc | relationship_type | description | status | source |
|---------|-------|-------------------|-------------|--------|--------|
| BC-01 | BC-02 | {partnership | customer-supplier | conformist | ACL | shared-kernel | published-language | separate-ways} | {description} | complete | {ref} |
| BC-02 | BC-03 | {relationship_type} | {description} | complete | {ref} |

---

## service_map

| svc_id | name | bounded_context | slice | technology_category | status | source |
|--------|------|-----------------|-------|---------------------|--------|--------|
| SVC-01 | {service_name} | BC-01 | BE | {api | worker | gateway | etc.} | complete | {ref} |
| SVC-02 | {service_name} | BC-01 | FE | {spa | micro-frontend | etc.} | complete | {ref} |
| SVC-03 | {service_name} | BC-02 | BE | {api | worker} | complete | {ref} |

---

## integration_patterns

| from_svc | to_svc | pattern | protocol | data_contract | status | source |
|----------|--------|---------|----------|---------------|--------|--------|
| SVC-01 | SVC-03 | {sync-rest | async-event | saga | cqrs} | {HTTP | gRPC | AMQP | Kafka | etc.} | {contract_ref} | complete | {ref} |
| SVC-02 | SVC-01 | {pattern} | {protocol} | {contract_ref} | complete | {ref} |

---

## event_flows

| event_name | producer_bc | consumer_bcs | trigger | saga | gherkin_ref | status | source |
|------------|-------------|--------------|---------|------|-------------|--------|--------|
| {EventName} | BC-01 | BC-02, BC-03 | {trigger_description} | {yes | no} | {gherkin_ref | —} | complete | {ref} |
| {EventName} | BC-02 | BC-01 | {trigger_description} | {yes | no} | {gherkin_ref | —} | complete | {ref} |

---

## nfr_by_context

| bc_id | nfr_id | target | measurement | status | source |
|-------|--------|--------|-------------|--------|--------|
| BC-01 | NFR-01 | {quantitative_target} | {measurement_method} | complete | {ref} |
| BC-01 | NFR-02 | {quantitative_target} | {measurement_method} | complete | {ref} |
| BC-02 | NFR-01 | {quantitative_target} | {measurement_method} | pending | {ref} |

---

## implementation_roadmap

| phase | epic_ids | contexts_targeted | rationale | dependencies | status | source |
|-------|----------|-------------------|-----------|--------------|--------|--------|
| 1 | EPIC-01, EPIC-02 | BC-01, BC-02 | {rationale} | — | complete | {ref} |
| 2 | EPIC-03, EPIC-04 | BC-03 | {rationale} | phase_1 | complete | {ref} |
| 3 | EPIC-05 | BC-01, BC-04 | {rationale} | phase_1, phase_2 | complete | {ref} |

---

## validations

| check | expected | actual | status | details |
|-------|----------|--------|--------|---------|
| bc_coverage | all FRs mapped to at least one BC | {N}/{N} | {PASS | FAIL} | {gaps if any} |
| fr_traceability | all BCs trace to source FRs | {N}/{N} | {PASS | FAIL} | {gaps if any} |
| nfr_coverage | all NFRs assigned to at least one BC | {N}/{N} | {PASS | FAIL} | {gaps if any} |
| relationship_completeness | all cross-BC dependencies have relationship type | {N}/{N} | {PASS | FAIL} | {gaps if any} |
| service_mapping | all BCs have at least one service | {N}/{N} | {PASS | FAIL} | {gaps if any} |
| event_flow_completeness | all async integrations have event flows | {N}/{N} | {PASS | FAIL} | {gaps if any} |
| epic_alignment | all epics map to at least one BC via roadmap | {N}/{N} | {PASS | FAIL} | {gaps if any} |
| source_fidelity | all complete items have source tags | {N}/{N} | {PASS | FAIL} | {gaps if any} |

validations_passed: {N}/8
overall_status: {PASS | FAIL}
fail_reasons: [{reason}]

---

## open_questions

### pending_inputs
| id | description | impact | source |
|----|-------------|--------|--------|
| OQ-XX | {missing input description} | {what sections are affected} | {which upstream artifact} |

### coverage_gaps
| id | type | ref_id | description | affected_section |
|----|------|--------|-------------|------------------|
| GAP-XX | {uncovered_fr | unmapped_nfr | missing_relationship} | {FR/NFR/BC ID} | {what is missing} | {section} |

### alignment_gaps
| id | type | ref_id | description | affected_section |
|----|------|--------|-------------|------------------|
| AG-XX | {epic_unaligned | service_orphan | event_unmapped} | {EPIC/SVC/EVENT ID} | {what is misaligned} | {section} |

### assumptions_to_validate
| id | assumption | section | rationale | confidence | validation_needed |
|----|-----------|---------|-----------|------------|-------------------|
| ASM-XX | {assumption text} | {section} | {why assumed} | {high | medium | low} | {what to validate} |

### upstream_gaps_carried_forward
| id | origin | description | impact_on_boundaries |
|----|--------|-------------|----------------------|
| UG-XX | {PRD | Epics} | {gap description} | {how it affects domain boundaries} |

### summary
- total_contexts: {N}
- core_contexts: {N}
- supporting_contexts: {N}
- generic_contexts: {N}
- total_services: {N}
- total_relationships: {N}
- total_events: {N}
- coverage_gaps: {N}
- alignment_gaps: {N}
- pending_inputs: {N}
- assumptions: {N}
- upstream_gaps: {N}
- validations_passed: {N}/8
- status: {draft | complete}
```

---

## File 2: contexts/bc-{NN}-{name}.md (Per-Context Detail)

```markdown
# {project_name} — BC-{NN}: {Bounded Context Name}
bc_id: BC-{NN}
classification: {core | supporting | generic}

---

## aggregates

### AGG-{NN}-01: {aggregate_name}
- aggregate_root: {entity_name}
- entities: {entity_1}, {entity_2}
- value_objects: {vo_1}, {vo_2}
- invariants:
  - {business_rule_1}
  - {business_rule_2}
- source_frs: FR-XX, FR-YY
- status: complete

### AGG-{NN}-02: {aggregate_name}
- aggregate_root: {entity_name}
- entities: {entity_1}
- value_objects: {vo_1}
- invariants:
  - {business_rule_1}
- source_frs: FR-XX
- status: complete

---

## entities

| entity_id | name | aggregate | attributes | status | source |
|-----------|------|-----------|------------|--------|--------|
| ENT-{NN}-01 | {entity_name} | AGG-{NN}-01 | {attr_1}, {attr_2}, {attr_3} | complete | {ref} |
| ENT-{NN}-02 | {entity_name} | AGG-{NN}-01 | {attr_1}, {attr_2} | complete | {ref} |

---

## domain_events

### EVT-{NN}-01: {EventName}
- trigger: {what causes the event}
- payload: {key_field_1}, {key_field_2}
- consumers: BC-XX, BC-YY
- saga: {yes | no}
- status: complete
- source: {ref}

### EVT-{NN}-02: {EventName}
- trigger: {what causes the event}
- payload: {key_field_1}
- consumers: BC-XX
- saga: {yes | no}
- status: complete
- source: {ref}

---

## domain_rules

| rule_id | description | enforced_by | source_frs | status | source |
|---------|-------------|-------------|------------|--------|--------|
| RULE-{NN}-01 | {business rule description} | AGG-{NN}-01 | FR-XX | complete | {ref} |
| RULE-{NN}-02 | {business rule description} | AGG-{NN}-02 | FR-YY | complete | {ref} |

---

## ubiquitous_language

| term | definition | aliases | status |
|------|-----------|---------|--------|
| {term} | {domain-specific definition} | {alias_1}, {alias_2} | complete |
| {term} | {domain-specific definition} | — | complete |
```

---

## File 3: BOUNDARIES-AUDIT-{SESSION_ID}.md

```markdown
# {project_name} — Bounded Contexts Session Audit
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
| Architecture | {architecture_path} | Loaded / Not provided |
| Domain Docs | {domain_docs_path} | Loaded / Not provided |

---

## generation_log

| bc_id | name | classification | aggregates | entities | events | status |
|-------|------|----------------|------------|----------|--------|--------|

---

## validation_summary

| check | result | details |
|-------|--------|---------|
(8 checks)

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
1. `context_catalog` — discover and classify BCs from PRD + epics
2. `context_relationships` — map relationships between discovered BCs
3. `service_map` — map services to BCs (from architecture or derived)
4. `integration_patterns` — map service-to-service integrations
5. `event_flows` — map domain events across BCs
6. `nfr_by_context` — assign NFRs to BCs
7. `implementation_roadmap` — phase contexts by epic delivery order
8. `validations` — verify completeness (audit consumer)
9. `open_questions` — consolidation pass (always last)

### Per-Context Generation
For each discovered BC:
- Create `contexts/bc-{NN}-{name}.md` with aggregates, entities, events, rules, language
- Update `context_catalog` with counts and file_ref
- Each aggregate must trace to source FRs
- Each event must list consumer BCs

### REPAIR Mode Mechanics
- Load existing spec → identify sections targeted by REPAIR_DIRECTIVES
- Apply directives surgically to targeted sections only
- Preserve untargeted sections and context files exactly
- Re-run validations after all repairs
- Re-consolidate open_questions
- Increment patch version

### Classification Rules
- **core**: Differentiating business capability, competitive advantage
- **supporting**: Necessary but not differentiating
- **generic**: Commodity, could be off-the-shelf

### Relationship Type Definitions
- **partnership**: Two BCs cooperate, no upstream/downstream
- **customer-supplier**: Upstream serves downstream, downstream requests
- **conformist**: Downstream conforms to upstream model without translation
- **ACL**: Anti-corruption layer translates between models
- **shared-kernel**: Two BCs share a subset of the model
- **published-language**: Well-documented interchange format
- **separate-ways**: No integration, independent evolution
