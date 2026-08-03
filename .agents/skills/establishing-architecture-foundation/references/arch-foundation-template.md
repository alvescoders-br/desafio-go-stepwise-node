# Agent-Native Architecture Foundation Spec Template

## Template Rules
- **No prose.** Every section is structured data only.
- **No executive summaries.** No "this document provides" paragraphs.
- **No meeting agendas.** Governance content is humanize-spec responsibility.
- **All items carry status.** `complete` | `pending` | `assumption`.
- **All pending items appear in open_questions.** Single registry, no scatter.
- **Source tags are mandatory.** No source → cannot be `complete`.
- **Zero Invention.** Every principle traces to an ADR. Every service traces to a BC.
- **C4 diagrams use PlantUML.** All diagram code blocks are valid PlantUML syntax.
- **Language:** Generate in DETECTED_LANGUAGE. Section headers in English always.

---

## Architecture: Index + Per-Service Files

```
ARCH-FOUNDATION/
├── ARCH-FOUNDATION-SPEC-{SESSION_ID}.md  ← Index: principles + catalog + diagrams + validations (always in context)
├── services/
│   ├── svc-01-{name}.md                  ← Per-service detail: interfaces, dependencies, NFR targets
│   ├── svc-02-{name}.md
│   └── ...
├── diagrams/
│   ├── c1-system-context.puml
│   ├── c2-container.puml
│   ├── c3-component-{svc}.puml
│   ├── seq-{flow-name}.puml
│   ├── deployment.puml
│   └── security.puml
└── ARCH-FOUNDATION-AUDIT-{SESSION_ID}.md ← Session metadata
```

**Consumption pattern:**
Downstream agents load the INDEX (always) + ONE service file or diagram (current work).
They never need all service details and diagrams in context simultaneously.

---

## File 1: ARCH-FOUNDATION-SPEC-{SESSION_ID}.md

```markdown
# {project_name} — Architecture Foundation Spec
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
  adrs: {adrs_path}

---

## architecture_principles

| principle_id | principle | adr_source | rationale | status | source |
|-------------|-----------|------------|-----------|--------|--------|
| AP-01 | {principle_statement} | ADR-001, ADR-003 | {rationale} | complete | {ref} |
| AP-02 | {principle_statement} | ADR-002 | {rationale} | complete | {ref} |
| AP-03 | {principle_statement} | ADR-005, ADR-006 | {rationale} | complete | {ref} |
| AP-04 | {principle_statement} | ADR-004 | {rationale} | assumption | {ref} |

---

## service_catalog

| svc_id | name | bc_ref | tech_stack | nfr_targets | file_ref | status | source |
|--------|------|--------|------------|-------------|----------|--------|--------|
| SVC-01 | {service_name} | BC-01 | {language}, {framework}, {db} | NFR-01, NFR-03 | services/svc-01-{name}.md | complete | {ref} |
| SVC-02 | {service_name} | BC-01 | {language}, {framework} | NFR-02 | services/svc-02-{name}.md | complete | {ref} |
| SVC-03 | {service_name} | BC-02 | {language}, {framework}, {db} | NFR-01, NFR-04 | services/svc-03-{name}.md | complete | {ref} |

---

## c4_diagrams

### c1_system_context
- description: {system_context_description}
- actors: {actor_1}, {actor_2}
- external_systems: {system_1}, {system_2}
- file_ref: diagrams/c1-system-context.puml
- status: complete
- source: boundaries/{ref}

### c2_container
- description: {container_diagram_description}
- containers: SVC-01, SVC-02, SVC-03, {database_1}, {message_broker}
- file_ref: diagrams/c2-container.puml
- status: complete
- source: boundaries/{ref}, adrs/{ref}

### c3_component_a
- description: {component_diagram_description}
- target_service: SVC-01
- components: {component_1}, {component_2}, {component_3}
- file_ref: diagrams/c3-component-svc-01.puml
- status: complete
- source: boundaries/{ref}

### c3_component_b
- description: {component_diagram_description}
- target_service: SVC-03
- components: {component_1}, {component_2}
- file_ref: diagrams/c3-component-svc-03.puml
- status: complete
- source: boundaries/{ref}

### seq_critical_flow_1
- description: {sequence_description}
- flow_name: {flow_name}
- participants: SVC-01, SVC-02, SVC-03
- trigger: {trigger_description}
- file_ref: diagrams/seq-{flow-name}.puml
- status: complete
- source: boundaries/{ref}

### seq_critical_flow_2
- description: {sequence_description}
- flow_name: {flow_name}
- participants: SVC-01, SVC-03, {external_system}
- trigger: {trigger_description}
- file_ref: diagrams/seq-{flow-name}.puml
- status: complete
- source: boundaries/{ref}

### deployment
- description: {deployment_diagram_description}
- environments: {env_1}, {env_2}, {env_3}
- infrastructure: {infra_components}
- file_ref: diagrams/deployment.puml
- status: complete
- source: adrs/{ref}

### security
- description: {security_diagram_description}
- zones: {zone_1}, {zone_2}, {zone_3}
- auth_flows: {flow_1}, {flow_2}
- file_ref: diagrams/security.puml
- status: complete
- source: adrs/{ref}

---

## tech_decisions

| layer | technology | version | adr_ref | services_using | status | source |
|-------|-----------|---------|---------|----------------|--------|--------|
| backend | {technology} | {version} | ADR-001 | SVC-01, SVC-03 | complete | {ref} |
| frontend | {technology} | {version} | ADR-002 | SVC-02, SVC-04 | complete | {ref} |
| data | {technology} | {version} | ADR-003 | SVC-01, SVC-03 | complete | {ref} |
| messaging | {technology} | {version} | ADR-004 | SVC-01, SVC-03 | complete | {ref} |
| infrastructure | {technology} | {version} | ADR-005 | all | complete | {ref} |
| cicd | {technology} | {version} | ADR-006 | all | complete | {ref} |
| monitoring | {technology} | {version} | ADR-007 | all | assumption | {ref} |
| security | {technology} | {version} | ADR-008 | all | complete | {ref} |

---

## traceability

### service_adr_tech_mapping

| svc_id | adr_refs | technologies | bc_ref | status |
|--------|----------|-------------|--------|--------|
| SVC-01 | ADR-001, ADR-003, ADR-004 | {tech_1}, {tech_2}, {tech_3} | BC-01 | complete |
| SVC-02 | ADR-002 | {tech_1} | BC-01 | complete |
| SVC-03 | ADR-001, ADR-003, ADR-004 | {tech_1}, {tech_2}, {tech_3} | BC-02 | complete |

---

## validations

| check | expected | actual | status | details |
|-------|----------|--------|--------|---------|
| principle_adr_coverage | all principles trace to ADRs | {N}/{N} | {PASS | FAIL} | {gaps if any} |
| service_bc_mapping | all services map to BCs | {N}/{N} | {PASS | FAIL} | {gaps if any} |
| service_tech_consistency | all services use ADR-decided tech | {N}/{N} | {PASS | FAIL} | {inconsistencies} |
| c4_completeness | C1 + C2 + at least 1 C3 + at least 1 seq | {N}/{N} | {PASS | FAIL} | {missing diagrams} |
| nfr_service_coverage | all NFRs assigned to services | {N}/{N} | {PASS | FAIL} | {gaps if any} |
| deployment_env_alignment | deployment diagram matches environments | {match | mismatch} | {PASS | FAIL} | {details} |
| tech_decision_completeness | all layers have tech decisions | {N}/{N} | {PASS | FAIL} | {missing layers} |
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
| GAP-XX | {unmapped_service | missing_diagram | uncovered_nfr} | {SVC/NFR ID} | {what is missing} | {section} |

### alignment_gaps
| id | type | ref_id | description | affected_section |
|----|------|--------|-------------|------------------|
| AG-XX | {tech_inconsistency | adr_mismatch | bc_orphan} | {SVC/ADR/BC ID} | {what is misaligned} | {section} |

### assumptions_to_validate
| id | assumption | section | rationale | confidence | validation_needed |
|----|-----------|---------|-----------|------------|-------------------|
| ASM-XX | {assumption text} | {section} | {why assumed} | {high | medium | low} | {what to validate} |

### upstream_gaps_carried_forward
| id | origin | description | impact_on_architecture |
|----|--------|-------------|------------------------|
| UG-XX | {Boundaries | ADRs | PRD} | {gap description} | {how it affects architecture} |

### summary
- total_principles: {N}
- total_services: {N}
- total_diagrams: {N}
- total_tech_decisions: {N}
- coverage_gaps: {N}
- alignment_gaps: {N}
- pending_inputs: {N}
- assumptions: {N}
- upstream_gaps: {N}
- validations_passed: {N}/8
- status: {draft | complete}
```

---

## File 2: services/svc-{NN}-{name}.md (Per-Service Detail)

```markdown
# {project_name} — SVC-{NN}: {Service Name}
svc_id: SVC-{NN}
bc_ref: BC-{NN}
slice: {BE | FE}

---

## interfaces

### API-{NN}-01: {interface_name}
- type: {REST | gRPC | GraphQL | WebSocket}
- method: {GET | POST | PUT | DELETE | STREAM}
- path: {endpoint_path}
- request: {request_schema_ref}
- response: {response_schema_ref}
- auth: {auth_mechanism}
- status: complete
- source: {ref}

### API-{NN}-02: {interface_name}
- type: {type}
- method: {method}
- path: {endpoint_path}
- request: {request_schema_ref}
- response: {response_schema_ref}
- auth: {auth_mechanism}
- status: complete
- source: {ref}

---

## dependencies

| dependency_type | target | protocol | pattern | data_contract | status | source |
|----------------|--------|----------|---------|---------------|--------|--------|
| service | SVC-XX | {HTTP | gRPC | AMQP} | {sync | async} | {contract_ref} | complete | {ref} |
| database | {db_name} | {protocol} | {sync} | {schema_ref} | complete | {ref} |
| external | {system_name} | {protocol} | {sync | async} | {contract_ref} | complete | {ref} |

---

## nfr_targets

| nfr_id | target | measurement | slo | status | source |
|--------|--------|-------------|-----|--------|--------|
| NFR-01 | {target} | {measurement_method} | {slo_value} | complete | {ref} |
| NFR-03 | {target} | {measurement_method} | {slo_value} | complete | {ref} |

---

## tech_stack

| layer | technology | version | adr_ref | status |
|-------|-----------|---------|---------|--------|
| language | {tech} | {version} | ADR-001 | complete |
| framework | {tech} | {version} | ADR-001 | complete |
| database | {tech} | {version} | ADR-003 | complete |

---

## components

| component_id | name | responsibility | dependencies | status |
|-------------|------|----------------|--------------|--------|
| COMP-{NN}-01 | {component_name} | {responsibility} | {dep_1}, {dep_2} | complete |
| COMP-{NN}-02 | {component_name} | {responsibility} | {dep_1} | complete |
```

---

## File 3: ARCH-FOUNDATION-AUDIT-{SESSION_ID}.md

```markdown
# {project_name} — Architecture Foundation Session Audit
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
| ADRs | {adrs_path} | Loaded |

---

## generation_log

| artifact | type | target | status |
|----------|------|--------|--------|
| AP-01..AP-NN | principles | — | complete |
| SVC-01..SVC-NN | service_files | services/ | complete |
| C1..C2..C3..seq | diagrams | diagrams/ | complete |

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
1. `architecture_principles` — derive from ADRs
2. `service_catalog` — map services from boundaries + ADR tech decisions
3. `c4_diagrams` — generate diagram metadata and PlantUML files
4. `tech_decisions` — consolidate tech stack by layer
5. `traceability` — build service→ADR→tech mapping
6. `validations` — verify completeness (audit consumer)
7. `open_questions` — consolidation pass (always last)

### Per-Service Generation
For each service in the boundaries service_map:
- Create `services/svc-{NN}-{name}.md` with interfaces, dependencies, NFRs, tech stack, components
- Update `service_catalog` with summary and file_ref
- Each service must trace to a BC and use ADR-decided technologies

### C4 Diagram Generation
- C1 System Context: always generated (one per system)
- C2 Container: always generated (one per system)
- C3 Component: one per core-BC service (minimum 1)
- Sequence: one per critical flow (minimum 2)
- Deployment: always generated
- Security: always generated
- All diagrams as PlantUML files in diagrams/ subfolder

### REPAIR Mode Mechanics
- Load existing spec → identify sections targeted by REPAIR_DIRECTIVES
- Apply directives surgically to targeted sections only
- Preserve untargeted service files and diagrams exactly
- Re-run validations after all repairs
- Re-consolidate open_questions
- Increment patch version
