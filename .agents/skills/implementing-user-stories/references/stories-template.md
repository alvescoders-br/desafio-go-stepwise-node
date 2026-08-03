# Agent-Native User Stories — Template Reference

## Architecture: Manifest + Per-Epic Files

The output is ALWAYS split into a manifest and per-epic files.
No single-file mode. This architecture scales from 20 to 400+ stories
with constant context cost at consumption time (~5.5K tokens).

```
STORIES/
├── STORIES-MANIFEST.md       ← Lightweight index (always in context)
├── epics/
│   ├── epic-01.md             ← Story definitions (loaded on demand)
│   ├── epic-02.md
│   └── ...
└── STORIES-AUDIT.md           ← Session metadata
```

**Consumption pattern:**
The implementing agent loads the MANIFEST (always) + ONE epic file (current work).
When it finishes an epic, it drops the file and loads the next.
It never needs the full backlog in context.

---

## File 1: STORIES-MANIFEST-{SESSION_ID}.md

```markdown
# {project_name} — Stories Manifest
version: {NEW_VERSION}
session: {SESSION_ID}
mode: {BUILD | REPAIR}
date: {ISO 8601}
language: {DETECTED_LANGUAGE}
prd_source: {path}
epics_source: {path}
contract_format: structured
prd_source_hash: {sha256 from PRD content_hash or computed over PRD-SPEC content}
epics_source_hash: {sha256 from EPICS-SPEC content_hash or computed over EPICS-SPEC content}
status: {draft | complete}

---

## story_map

### EPIC-01: {epic_title}
- US-01-01-BE: {title}
- US-01-02-FE: {title}
- US-01-03-BE: {title}
- US-01-04-FE: {title}
- file: epics/epic-01.md

### EPIC-02: {epic_title}
- US-02-01-DATA: {title}
- US-02-02-INFRA: {title}
- US-02-03-BE: {title}
- file: epics/epic-02.md

### EPIC-03: {epic_title}
- US-03-01-FS: {title}
- file: epics/epic-03.md

### counts
- total_stories: {N}
- by_tag: BE: {n}, FE: {n}, DATA: {n}, INFRA: {n}, AI: {n}, FS: {n}
- stories_per_epic:
  - EPIC-01: {N}
  - EPIC-02: {N}
- flagged:
  - {EPIC-XX}: >8 stories, possible epic split
  - {EPIC-YY}: 1 story, possible merge

---

## dependencies

| story_id | depends_on | type | risk |
|----------|-----------|------|------|
| US-01-01-BE | — | none | — |
| US-01-02-FE | US-01-01-BE | cross_layer | FE blocked until API ready |
| US-01-03-BE | — | none | — |
| US-01-04-FE | US-01-03-BE | cross_layer | FE blocked until API ready |
| US-02-01-DATA | US-01-01-BE | functional | Needs data model |
| US-02-02-INFRA | — | none | — |
| US-02-03-BE | US-02-01-DATA | functional | Needs data layer |
| US-03-01-FS | — | none | — |

Rules:
- EVERY story ID from story_map has a row. No omissions.
- FE/MOBILE MUST list corresponding BE (cross_layer).
- Types: cross_layer, functional, technical, resource, external, epic_to_epic.

---

## validations

| check | result | details |
|-------|--------|---------|
| completeness | pass | All FRs covered |
| relevance | pass | All stories trace to parent epic |
| id_consistency | pass | Manifest = epic files |
| tech_neutrality | pass | 0 violations |
| nfr_preservation | pass | All NFR IDs match PRD |
| rsk_asm_carryforward | pass | All refs present |
| persona_coverage | fail | P-03 uncovered |
| kpi_coverage | pass | 5/5 KPIs covered |
| api_path_fidelity | pass | All paths match |
| anti_fade | pass | Consistent depth |
| dod_consistency | pass | Tag-appropriate DoD |
| ac_minimum | pass | All ≥4 scenarios |

---

## open_questions

### pending_inputs

| id | affected_ids | blocking | type | epic | story_id | field | impact | question | fallback_behavior | source_ref |
|----|--------------|----------|------|------|----------|-------|--------|----------|-------------------|------------|
| PI-01 | {EPIC-02, US-02-01-DATA, FR-05} | yes | missing | EPIC-02 | US-02-01-DATA | business_rules | HIGH | {needed answer} | BLOCKED | {stable section/ID anchor} |
| PI-02 | {EPIC-03} | no | flagged | — | — | epic_count | LOW | EPIC-03 has 1 story, merge candidate | keep as single-story epic unless reviewer merges | EPICS:EPIC-03 |

### coverage_gaps

| id | affected_ids | blocking | type | item_id | impact | description | fallback_behavior | source_ref |
|----|--------------|----------|------|---------|--------|-------------|-------------------|------------|
| CG-01 | {KPI-04} | {yes | no} | uncovered_kpi | KPI-04 | {HIGH | MEDIUM | LOW} | No implementing story | {defer KPI or BLOCKED} | PRD:KPI-04 |
| CG-02 | {P-03} | {yes | no} | uncovered_persona | P-03 | {HIGH | MEDIUM | LOW} | No stories for this persona | {defer persona or BLOCKED} | PRD:P-03 |

### assumptions_to_validate

| id | affected_ids | blocking | assumption | story_id | impact_if_wrong | validation_method | fallback_behavior | source_ref |
|----|--------------|----------|------------|----------|-----------------|-------------------|-------------------|------------|
| ASM-S01 | {US-02-01-DATA} | no | Schema inferred | US-02-01-DATA | Scope may be wrong | Review data model | use minimal backward-compatible schema | EPICS:ASM-E01 |

### upstream_gaps_carried_forward

| id | affected_ids | blocking | source | description | story_coverage | fallback_behavior | recommendation |
|----|--------------|----------|--------|-------------|----------------|-------------------|----------------|
| TG-01 | {FR-02, US-01-03-BE} | {yes | no} | PRD | Orphan FR-02 | US-01-03-BE may address | {carry orphan note or BLOCKED} | Update PRD |
| PI-PRD-03 | {NFR-03, US-01-01-BE} | yes | PRD | NFR-03 target missing | Affects US-01-01-BE DoD | BLOCKED | Resolve in PRD |
| AG-01 | {EPIC-03} | no | Epics | EPIC-03 unaligned | Carried forward | Keep as KPI-backed enabler | Review |

### summary
- total_stories: {N}
- by_tag: BE: {n}, FE: {n}, DATA: {n}, INFRA: {n}, AI: {n}, FS: {n}
- epics_decomposed: {N}
- pending_inputs: {N}
- coverage_gaps: {N}
- assumptions: {N}
- upstream_gaps: {N}
- validations_passed: {N}/12
- status: {draft | complete}
```

**Manifest size per project scale:**
- 20 stories: ~230 lines (~700 tokens)
- 60 stories: ~490 lines (~1,500 tokens)
- 120 stories: ~850 lines (~2,600 tokens)
- 400 stories: ~1,850 lines (~5,600 tokens)

All fit comfortably in the implementing agent's context alongside its
own instructions, code context, and working files.

---

## File 2: epics/epic-{NN}.md (Per-Epic Story Definitions)

```markdown
# {project_name} — EPIC-{NN}: {epic_title}
epic: EPIC-{NN}
priority: {must_have | should_have | could_have}
complexity: {S | M | L | XL}
personas: P-01, P-02
rsk_refs: RSK-01
asm_refs: ASM-01
source_frs: FR-01, FR-03
nfr_dod: NFR-01 ({target}), NFR-03 ({target})
literal_refs: LIT-01, LIT-03
fallback_refs: PI-PRD-03

---

## US-01-01-BE: {story_title}
- tag: BE
- personas: P-01
- scope:
  - in: {what this story delivers}
  - out: {what is excluded}
- business_rules:
  - BR-01: given: {precondition} | when: {action} | then: {outcome}
  - BR-02: given: {precondition} | when: {action} | then: {outcome}
- sourced_constraints:
  - {constraint text} | source_ref: {ADR-XXX | tech-policy | PRD:LIT-XX | ARCH:UNIT-XX}
- acceptance_criteria:
  - US-01-01-AC-01 [happy_path]: given: {x} | when: {y} | then: {z}
  - US-01-01-AC-02 [validation_error]: given: {x} | when: {y} | then: {z}
  - US-01-01-AC-03 [system_failure]: given: {x} | when: {y} | then: {z}
  - US-01-01-AC-04 [auth_unauthorized]: given: {x} | when: {y} | then: {z}
- fallback_behavior:
  - {affected_id}: {behavior inherited from upstream open_questions or none}
- dod: code_review, unit_tests, integration_tests, security_scan, error_handling
- traceability:
  - fr: FR-01, FR-03
  - nfr: NFR-01
  - jtbd: JTBD-01
  - rsk: RSK-01
  - asm: ASM-01
  - kpi: KPI-01
- assumptions: none
- status: complete

---

## US-01-02-FE: {story_title}
- tag: FE
- personas: P-01, P-02
- scope:
  - in: {scope}
  - out: {exclusions}
- business_rules:
  - BR-01: given: {precondition} | when: {action} | then: {outcome}
- sourced_constraints:
  - {constraint text} | source_ref: {ADR-XXX | tech-policy | PRD:LIT-XX | ARCH:UNIT-XX}
- acceptance_criteria:
  - US-01-02-AC-01 [happy_path]: given: {x} | when: {y} | then: {z}
  - US-01-02-AC-02 [validation_error]: given: {x} | when: {y} | then: {z}
  - US-01-02-AC-03 [api_network_error]: given: {x} | when: {y} | then: {z}
  - US-01-02-AC-04 [visual_states]: given: {x} | when: {y} | then: {z}
- fallback_behavior:
  - {affected_id}: {behavior inherited from upstream open_questions or none}
- dod: code_review, visual_qa, responsive, accessibility
- traceability:
  - fr: FR-01
  - nfr: NFR-02
  - jtbd: JTBD-01
  - rsk: RSK-01
  - asm: —
  - kpi: —
- assumptions: none
- status: complete
```

**Per-epic file size:**
- 4 stories × 28 lines = ~112 lines (~340 tokens)
- 8 stories × 28 lines = ~224 lines (~670 tokens)

Each file includes an epic-level header with context the implementing
agent needs: priority, complexity, personas, RSK/ASM refs, source FRs,
NFR DoD targets. This header means the agent has full context for ALL
stories in the epic without loading any other file except the manifest.

---

## Story Definition Rules

### Fields (9 per story, ~28 lines)
| Field | Purpose | Required |
|-------|---------|----------|
| tag | Domain routing (BE/FE/DATA/INFRA/AI/FS) | Always |
| personas | Who this story serves | Always |
| scope.in | What to build — explicit boundaries | Always |
| scope.out | What NOT to build — where to stop | Always |
| business_rules | Domain logic (Gherkin given/when/then) | If available |
| sourced_constraints | Source-backed positive/negative constraints from ADR, tech-policy, PRD, architecture, or context pack | If any |
| acceptance_criteria | Test contract (min 4 scenarios) | Always |
| dod | Completion checklist (per tag) | Always |
| traceability | FR/NFR/JTBD/RSK/ASM/KPI refs | Always |
| assumptions | Inferred items needing validation | If any |

### Fields NOT included (human-only, humanize-spec generates these)
| Field | Reason for Exclusion |
|-------|---------------------|
| Description (prose) | Agent has scope + business_rules |
| Narrative (As a...) | Human communication device, agent has JTBD ref |
| Context (prose) | Source refs in traceability field |
| Goal/Desire | Redundant with JTBD traceability |
| Benefit/Reason | Redundant with KPI traceability |
| Notes (prose) | Constraints in scope + business_rules |
| Definition of Ready | Sprint planning governance, not implementation |

### Architecture Authority
Stories own behavior, acceptance criteria, source-backed constraints, inherited
literals, and fallback behavior. Stories do NOT own architecture.

Allowed:
- Behavioral requirements.
- Positive or negative constraints sourced to ADRs, tech-policy, context-pack,
  PRD literal_registry, or architecture artifacts.

Flag as a generation defect unless sourced to architecture/ADR/context-pack:
- File paths, package names, layer assignments, framework choices, storage tools,
  runtime topology, deployment structure, or module placement.

Sourcing is the discriminator. A sourced negative technology constraint passes;
an unsourced path/layer mandate fails.

### Acceptance Criteria — Destructive QA Mindset
Minimum 4 scenarios. Tag each scenario for machine parsing:

| Tag | When to Use |
|-----|------------|
| [happy_path] | Always — first scenario |
| [validation_error] | Always — second scenario |
| [system_failure] | BE, DATA, INFRA — DB down, timeout, disk full |
| [auth_unauthorized] | BE, DATA, INFRA — invalid/expired token |
| [api_network_error] | FE, MOBILE — API unreachable |
| [visual_states] | FE, MOBILE — loading, empty, skeleton, error |
| [model_failure] | AI — timeout, degraded output |
| [data_quality] | AI — missing features, drift, bias |
| [edge_case] | Domain-specific boundary condition |
| [boundary] | Limit values, max/min, overflow |
| [concurrency] | Race conditions, parallel access |

### Technical Matrix (mandatory per domain tag)
| Tag | Required Scenarios (in addition to happy + validation) |
|-----|------------------------------------------------------|
| FE, MOBILE | api_network_error + visual_states |
| BE, DATA, INFRA | system_failure + auth_unauthorized |
| AI | model_failure + data_quality |

A BE story without system_failure = generation defect. Auto-add.

### Definition of Done (per tag, not per story)
| Tag | DoD |
|-----|-----|
| FE, MOBILE | code_review, visual_qa, responsive, accessibility |
| BE, DATA | code_review, unit_tests, integration_tests, security_scan, error_handling |
| INFRA | code_review, plan_apply_verified, monitoring, rollback_tested |
| AI | code_review, accuracy_check, bias_audit, performance, fallback_verified |

### Anti-Fade Protocol
Compare first epic vs last epic:
- AC scenario count (within ±1)
- Business rule count
- Scope boundary detail
If degradation → regenerate affected stories.
