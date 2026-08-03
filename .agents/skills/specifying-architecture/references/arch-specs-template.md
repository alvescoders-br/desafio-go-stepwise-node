# Agent-Native Architecture Specs Manifest Template

## Template Rules
- **No prose.** Every section is structured data only.
- **No executive summaries.** No "this document provides" paragraphs.
- **No meeting agendas.** Governance content is humanize-spec responsibility.
- **All items carry status.** `complete` | `pending` | `assumption`.
- **All pending items appear in open_questions.** Single registry, no scatter.
- **Source tags are mandatory.** No source → cannot be `complete`.
- **Zero Invention.** Every unit traces to services and ADRs. Every technology traces to an ADR.
- **Language:** Generate in DETECTED_LANGUAGE. Section headers in English always.
- **ASCII punctuation (per execution-protocol §10.5).** In descriptions, catalog entries, and tech rationales use ASCII punctuation: `-`/`--` for dashes, `->` for arrows, straight quotes, `...` for ellipsis. Do NOT decorate style/pattern names with `—` or `→` (e.g. write `MCP Protocol-First + FSD`, not `MCP Protocol-First -> FSD`). Required localized characters in DETECTED_LANGUAGE (accented vowels, `ñ`, etc.) are exempt — they are content and stay as-is.

---

## Architecture: Manifest + Per-Unit Files

```
ARCH-SPECS/
├── ARCH-SPECS-MANIFEST-{SESSION_ID}.md  ← Index: unit catalog + cross-refs + tech fidelity + validations (always in context)
├── units/
│   ├── unit-01-communication.md          ← Communication architecture specification
│   ├── unit-02-data.md                   ← Data architecture specification
│   ├── unit-03-security.md               ← Security architecture specification
│   ├── unit-04-observability.md          ← Observability architecture specification
│   ├── unit-05-infrastructure.md         ← Infrastructure architecture specification
│   ├── unit-06-characteristics.md        ← Architecture characteristics (ISO 25010)
│   ├── unit-07-migration.md              ← Migration roadmap with Gherkin gates
│   └── unit-08-{additional}.md           ← Project-specific units
└── ARCH-SPECS-AUDIT-{SESSION_ID}.md     ← Session metadata
```

**Consumption pattern:**
Downstream agents (code design, QE) load the MANIFEST (always) + ONE unit file (current work).
They never need all specification units in context simultaneously.

---

## File 1: ARCH-SPECS-MANIFEST-{SESSION_ID}.md

```markdown
# {project_name} — Architecture Specs Manifest
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
  arch_foundation: {arch_foundation_path}

---

## unit_catalog

| unit_id | title | file_ref | status | services_covered | key_decisions |
|---------|-------|----------|--------|------------------|---------------|
| UNIT-01 | Communication Architecture | units/unit-01-communication.md | complete | SVC-01, SVC-02, SVC-03 | ADR-004, ADR-009 |
| UNIT-02 | Data Architecture | units/unit-02-data.md | complete | SVC-01, SVC-03 | ADR-003, ADR-010 |
| UNIT-03 | Security Architecture | units/unit-03-security.md | complete | all | ADR-008 |
| UNIT-04 | Observability Architecture | units/unit-04-observability.md | complete | all | ADR-007 |
| UNIT-05 | Infrastructure Architecture | units/unit-05-infrastructure.md | complete | all | ADR-005, ADR-006 |
| UNIT-06 | Architecture Characteristics | units/unit-06-characteristics.md | complete | all | — |
| UNIT-07 | Migration Roadmap | units/unit-07-migration.md | complete | all | — |

---

## cross_references

| from_unit | to_unit | relationship | status |
|-----------|---------|-------------|--------|
| UNIT-01 | UNIT-03 | {communication security constraints} | complete |
| UNIT-01 | UNIT-04 | {communication observability requirements} | complete |
| UNIT-02 | UNIT-03 | {data security and encryption} | complete |
| UNIT-02 | UNIT-05 | {data infrastructure requirements} | complete |
| UNIT-03 | UNIT-04 | {security event monitoring} | complete |
| UNIT-05 | UNIT-04 | {infrastructure monitoring} | complete |
| UNIT-06 | UNIT-07 | {characteristics drive migration priorities} | complete |

---

## tech_fidelity_summary

| technology | adr_ref | units_using | consistent | notes | status |
|-----------|---------|-------------|------------|-------|--------|
| {tech_1} | ADR-001 | UNIT-01, UNIT-02 | yes | — | complete |
| {tech_2} | ADR-002 | UNIT-01 | yes | — | complete |
| {tech_3} | ADR-003 | UNIT-02 | yes | — | complete |
| {tech_4} | ADR-004 | UNIT-01 | yes | — | complete |
| {tech_5} | ADR-005 | UNIT-05 | yes | — | complete |
| {tech_6} | ADR-007 | UNIT-04 | assumption | {assumption_note} | assumption |
| {tech_7} | ADR-008 | UNIT-03 | yes | — | complete |

---

## validations

| check | expected | actual | status | details |
|-------|----------|--------|--------|---------|
| unit_completeness | 7 standard units | {N}/7 | {PASS | FAIL} | {missing units} |
| service_coverage | all services in at least one unit | {N}/{N} | {PASS | FAIL} | {uncovered services} |
| adr_fidelity | all tech choices match ADR decisions | {N}/{N} | {PASS | FAIL} | {inconsistencies} |
| cross_reference_integrity | all cross-refs resolve to existing units | {N}/{N} | {PASS | FAIL} | {broken refs} |
| tech_consistency | no conflicting tech choices across units | 0 conflicts | {N} conflicts | {conflicts if any} |
| nfr_coverage | all NFRs addressed in characteristics unit | {N}/{N} | {PASS | FAIL} | {gaps if any} |
| migration_completeness | migration covers all services | {N}/{N} | {PASS | FAIL} | {gaps if any} |
| source_fidelity | all complete items have source tags | {N}/{N} | {PASS | FAIL} | {gaps if any} |

validations_passed: {N}/8
overall_status: {PASS | FAIL}
fail_reasons: [{reason}]

---

## open_questions

### pending_inputs
| id | description | impact | source |
|----|-------------|--------|--------|
| OQ-XX | {missing input description} | {what units are affected} | {which upstream artifact} |

### coverage_gaps
| id | type | ref_id | description | affected_unit |
|----|------|--------|-------------|---------------|
| GAP-XX | {uncovered_service | missing_nfr | incomplete_spec} | {SVC/NFR ID} | {what is missing} | {unit} |

### alignment_gaps
| id | type | ref_id | description | affected_unit |
|----|------|--------|-------------|---------------|
| AG-XX | {tech_inconsistency | adr_mismatch | cross_ref_broken} | {tech/ADR/unit ID} | {what is misaligned} | {unit} |

### assumptions_to_validate
| id | assumption | unit | rationale | confidence | validation_needed |
|----|-----------|------|-----------|------------|-------------------|
| ASM-XX | {assumption text} | {unit} | {why assumed} | {high | medium | low} | {what to validate} |

### upstream_gaps_carried_forward
| id | origin | description | impact_on_specs |
|----|--------|-------------|-----------------|
| UG-XX | {Foundation | ADRs | Boundaries} | {gap description} | {how it affects specs} |

### summary
- total_units: {N}
- standard_units: {N}/7
- additional_units: {N}
- total_cross_references: {N}
- technologies_tracked: {N}
- tech_consistent: {N}/{N}
- coverage_gaps: {N}
- alignment_gaps: {N}
- pending_inputs: {N}
- assumptions: {N}
- upstream_gaps: {N}
- validations_passed: {N}/8
- status: {draft | complete}
```

---

## Standard Unit Files

Each unit file follows a consistent structure. The content varies by specification domain.

### Standard Unit IDs
- UNIT-01: Communication Architecture (API design, messaging, integration patterns)
- UNIT-02: Data Architecture (data models, storage, caching, search)
- UNIT-03: Security Architecture (auth, encryption, zones, compliance)
- UNIT-04: Observability Architecture (logging, metrics, tracing, alerting)
- UNIT-05: Infrastructure Architecture (containers, orchestration, CI/CD, environments)
- UNIT-06: Architecture Characteristics (ISO 25010 quality attributes with measurable targets)
- UNIT-07: Migration Roadmap (phased migration with Gherkin gate specifications)

Additional units may be added for project-specific concerns (e.g., AI/ML pipeline, IoT, real-time).

### Unit File Template

```markdown
# {project_name} — UNIT-{NN}: {Unit Title}
unit_id: UNIT-{NN}
services_covered: SVC-XX, SVC-YY
adr_refs: ADR-NNN, ADR-MMM

---

## specifications

### SPEC-{NN}-01: {specification_name}
- scope: {what this specification covers}
- services: SVC-XX, SVC-YY
- technology: {technology} | adr_ref: ADR-NNN
- configuration:
  - {config_key_1}: {config_value_1}
  - {config_key_2}: {config_value_2}
- nfr_refs: NFR-XX
- status: complete
- source: {ref}

### SPEC-{NN}-02: {specification_name}
- scope: {what this specification covers}
- services: SVC-XX
- technology: {technology} | adr_ref: ADR-NNN
- configuration:
  - {config_key_1}: {config_value_1}
- nfr_refs: NFR-YY
- status: complete
- source: {ref}

---

## patterns

| pattern_id | name | description | services | status | source |
|-----------|------|-------------|----------|--------|--------|
| PAT-{NN}-01 | {pattern_name} | {description} | SVC-XX, SVC-YY | complete | {ref} |
| PAT-{NN}-02 | {pattern_name} | {description} | SVC-XX | complete | {ref} |

---

## risks

| risk_id | description | likelihood | impact | mitigation | status |
|---------|-------------|------------|--------|------------|--------|
| RSK-{NN}-01 | {risk_description} | {H | M | L} | {H | M | L} | {mitigation_approach} | complete |
```

### UNIT-07 Migration Roadmap — Additional Sections

```markdown
---

## migration_phases

### PHASE-01: {phase_name}
- services: SVC-XX, SVC-YY
- scope: {migration_scope}
- dependencies: —
- complexity: low | medium | high
- epic_count: {N epics in scope}
- status: complete
- source: {ref}

#### gherkin_gate: phase_01

```gherkin
Feature: Phase 1 Migration Gate

  Scenario: Phase 1 gate passes
    Given all Phase 1 services have been migrated
    And integration tests pass for SVC-XX and SVC-YY
    And performance benchmarks meet SLO thresholds
    When the migration gate is evaluated
    Then Phase 2 migration is authorized to proceed

  Scenario: Phase 1 gate fails
    Given Phase 1 migration has completed
    But integration tests fail for {N} service(s)
    When the migration gate is evaluated
    Then migration is paused
    And rollback procedures are initiated for failed services
```

### PHASE-02: {phase_name}
- services: SVC-XX
- scope: {migration_scope}
- dependencies: PHASE-01
- complexity: low | medium | high
- epic_count: {N epics in scope}
- status: complete
- source: {ref}
```

---

## File 3: ARCH-SPECS-AUDIT-{SESSION_ID}.md

```markdown
# {project_name} — Architecture Specs Session Audit
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
| Architecture Foundation | {arch_foundation_path} | Loaded |

---

## generation_log

| unit_id | title | specs_count | patterns_count | risks_count | status |
|---------|-------|-------------|----------------|-------------|--------|

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
1. `unit_catalog` — list all units to be generated
2. Per-unit files — generate each unit specification
3. `cross_references` — map inter-unit relationships
4. `tech_fidelity_summary` — verify technology consistency across units
5. `validations` — verify completeness (audit consumer)
6. `open_questions` — consolidation pass (always last)

### Unit Generation Order
1. UNIT-01: Communication (needs: service_map, integration_patterns from boundaries)
2. UNIT-02: Data (needs: service_catalog tech_stack, ADR data decisions)
3. UNIT-03: Security (needs: UNIT-01 communication patterns, ADR security decisions)
4. UNIT-04: Observability (needs: UNIT-01, UNIT-02, UNIT-03 for monitoring targets)
5. UNIT-05: Infrastructure (needs: all prior units for deployment requirements)
6. UNIT-06: Characteristics (needs: NFRs, all prior units for measurable targets)
7. UNIT-07: Migration (needs: all prior units for phasing, Gherkin gates)

### REPAIR Mode Mechanics
- Load existing manifest → identify units targeted by REPAIR_DIRECTIVES
- Apply directives surgically to targeted unit files only
- Preserve untargeted unit files exactly
- Re-run validations after all repairs
- Re-consolidate open_questions
- Increment patch version

### Tech Fidelity Rules
- Every technology referenced in a unit must trace to an ADR
- If a unit uses a technology not in ADR decisions → flag as `assumption`
- Cross-unit technology references must be consistent (same version, same config)
- `consistent: no` entries must appear in alignment_gaps
