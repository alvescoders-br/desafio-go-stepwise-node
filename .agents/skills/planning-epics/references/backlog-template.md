# Agent-Native Epics Backlog Template

## Template Rules
- **No prose.** Every section is structured data only.
- **No value propositions.** No "why this matters" narrative.
- **No meeting agendas.** Governance content is humanize-spec responsibility.
- **All items carry status.** `complete` | `pending` | `assumption` | `unaligned`.
- **All gaps appear in open_questions.** Single registry, no scatter.
- **PRD traceability gaps carried forward.** Never silently resolved.
- **Language:** Generate in DETECTED_LANGUAGE. Section headers in English always.
- **Single file output.** ALL sections below go into ONE file (EPICS-SPEC-{SESSION_ID}.md).
  Do NOT split sections into separate batch files. Do NOT use Write-Flush-Forget.
  If context is tight, reduce detail density — never split the file.

---

## Spec File Structure

```markdown
# {project_name} — Epics Backlog Spec
version: {NEW_VERSION}
session: {SESSION_ID}
mode: {BUILD | REPAIR}
date: {ISO 8601}
language: {DETECTED_LANGUAGE}
prd_source: {prd_spec_file_path}
contract_format: structured
prd_source_hash: {sha256 from PRD content_hash or computed over PRD-SPEC content}
status: {draft | complete}

---

## prd_id_ownership

Complete projection of PRD IDs into the epic layer. Every PRD ID from
functional requirements, non-functional requirements, JTBDs, KPIs, risks,
assumptions, dependencies, personas, and literal_registry is represented exactly
once as `owned`, `cross_cutting`, or `deferred`.

| prd_id | type | disposition | epic_ids | phase | reason | source_ref |
|--------|------|-------------|----------|-------|--------|------------|
| FR-01 | FR | owned | EPIC-01 | phase_1_mvp | primary deliverable | PRD:FR-01 |
| RSK-01 | risk | cross_cutting | EPIC-01, EPIC-03 | all | risk affects auth and reporting paths | PRD:RSK-01 |
| ASM-02 | assumption | deferred | — | deferred | unresolved upstream assumption blocks delivery | PRD:ASM-02 |
| LIT-01 | literal | owned | EPIC-01 | phase_1_mvp | exact value used by FR-01 ACs | PRD:LIT-01 |

---

## themes

### T-01: {theme_name}
- features:
  - {feature_name} | fr_refs: FR-01, FR-03 | priority: must_have
  - {feature_name} | fr_refs: FR-05 | priority: should_have
- status: {complete | assumption}

### T-02: {theme_name}
- features:
  - {feature_name} | fr_refs: FR-02 | priority: must_have
  - {feature_name} | fr_refs: FR-04, FR-06 | priority: could_have | [ASM: inferred grouping]
- status: assumption

---

## epics

### EPIC-01: {epic_title}
- type: feature
- theme: T-01
- personas: P-01, P-02
- priority_tier: must_have
- complexity: M
- traceability:
  - fr: FR-01, FR-03
  - jtbd: JTBD-01
  - kpi: KPI-01
- nfr_dod:
  - NFR-01: {target}
  - NFR-03: {target}
- rsk_refs: RSK-01
- asm_refs: ASM-01
- scope:
  - in: {what this epic delivers}
  - out: {what is excluded}
- status: complete

### EPIC-02: {epic_title}
- type: feature
- theme: T-01
- personas: P-01
- priority_tier: should_have
- complexity: L
- traceability:
  - fr: FR-05, FR-06
  - jtbd: JTBD-02
  - kpi: —
- nfr_dod:
  - NFR-02: {target}
- rsk_refs: —
- asm_refs: ASM-02
- scope:
  - in: {scope}
  - out: {exclusions}
- status: complete

### EPIC-03: {enabler_title}
- type: enabler
- theme: T-02
- personas: P-03
- priority_tier: must_have
- complexity: S
- traceability:
  - fr: —
  - kpi: KPI-02
- nfr_dod: —
- rsk_refs: —
- asm_refs: —
- scope:
  - in: {scope}
  - out: {exclusions}
- status: unaligned
- unaligned_reason: no FR match

### SPIKE-01: {investigation_title}
- type: spike
- goal: {investigation objective}
- prerequisite_for: EPIC-02
- traceability:
  - fr: FR-05
- complexity: S
- status: complete

---

## dependencies

| blocked | blocker | type | impact | mitigation |
|---------|---------|------|--------|------------|
| EPIC-01 | EPIC-03 | epic_to_epic | {consequence} | {strategy} |
| EPIC-02 | — | none | — | — |
| EPIC-03 | — | none | — | — |
| EPIC-04 | EXT:vendor_api | external | {consequence} | {fallback} |
| SPIKE-01 | EPIC-01 | epic_to_epic | {consequence} | {strategy} |

### circular_resolutions
(If circular dependencies were detected and resolved)

- cycle: EPIC-XX <-> EPIC-YY
  - resolved_by: ENABLER-NNN
  - interface: {shared contract name}
  - new_chain: ENABLER-NNN → EPIC-XX, ENABLER-NNN → EPIC-YY

(If no cycles detected)
- none

---

## sequencing

### topological_order
1. EPIC-03 (enabler, no blockers)
2. ENABLER-NNN (if created by circular resolution)
3. EPIC-01 (blocked by EPIC-03)
4. SPIKE-01 (blocked by EPIC-01)
5. EPIC-02 (blocked by SPIKE-01)

### phase_mapping
(Derived from PRD mvp_phasing + dependency constraints)

- phase_1_mvp: EPIC-03, EPIC-01 (must_have, no/resolved blockers)
- phase_2: EPIC-02, SPIKE-01 (should_have)
- phase_3: EPIC-04 (could_have)
- deferred: {PRD out_of_scope items, wont_have FRs}

### sequencing_validations
- blocked_before_blocker_violations: {0 | N — auto-corrected}
- prd_conflict_notes: {none | list of PRD phasing conflicts}

---

## reclassification_log

| candidate | gate_failed | reclassified_as | redistributed_to | reason |
|-----------|-------------|-----------------|-------------------|--------|
| Logging system | gate_2_nfr | dod_constraint | EPIC-03, EPIC-07 | NFR-04 overlap |
| Tech spike: auth | gate_1_demo | SPIKE-01 | — | Research/exploration |
| API documentation | gate_3_enabler | enabler EPIC-03 | — | Tooling, traces to KPI-02 |

---

## persona_coverage

| persona | epic_count | epic_ids | status |
|---------|-----------|----------|--------|
| P-01 | 3 | EPIC-01, EPIC-02, EPIC-04 | covered |
| P-02 | 1 | EPIC-01 | covered |
| P-03 | 0 | — | uncovered |

---

## goal_coverage

| prd_goal | epic_ids | status |
|----------|----------|--------|
| Goal 1 | EPIC-01, EPIC-02 | covered |
| Goal 2 | EPIC-04 | covered |
| Goal 3 | — | uncovered |

---

## open_questions

### pending_inputs

| id | affected_ids | blocking | type | section | item_id | field | impact | question | fallback_behavior | source_ref |
|----|--------------|----------|------|---------|---------|-------|--------|----------|-------------------|------------|
| PI-01 | {EPIC-02, FR-05} | {yes | no} | missing | epics | EPIC-02 | complexity | {HIGH | MEDIUM | LOW} | {needed answer} | {BLOCKED or narrowest safe behavior} | {stable section/ID anchor} |
| PI-02 | {EPIC-04, DEP-02} | yes | missing | dependencies | EPIC-04 | mitigation | HIGH | {needed fallback} | BLOCKED | {stable section/ID anchor} |

### alignment_gaps

| id | affected_ids | blocking | type | item_id | impact | description | fallback_behavior | source_ref |
|----|--------------|----------|------|---------|--------|-------------|-------------------|------------|
| AG-01 | {EPIC-03, KPI-02} | no | unaligned_epic | EPIC-03 | MEDIUM | No FR match, traces only to KPI-02 | Keep as enabler if KPI-backed | EPICS:EPIC-03 |
| AG-02 | {Goal 3} | {yes | no} | uncovered_goal | Goal 3 | {HIGH | MEDIUM | LOW} | No epic addresses this goal | {defer or BLOCKED} | PRD:goal_3 |
| AG-03 | {P-03} | {yes | no} | uncovered_persona | P-03 | {HIGH | MEDIUM | LOW} | No epics mapped to this persona | {defer or BLOCKED} | PRD:P-03 |

### assumptions_to_validate

| id | affected_ids | blocking | assumption | source | impact_if_wrong | validation_method | fallback_behavior |
|----|--------------|----------|------------|--------|-----------------|-------------------|-------------------|
| ASM-E01 | {T-02, EPIC-XX} | no | T-02 grouping inferred | theme generation | Features may be misgrouped | Review with domain expert | Use current grouping until reviewed |

### prd_gaps_carried_forward

| id | affected_ids | blocking | source | description | epic_coverage | fallback_behavior | recommendation |
|----|--------------|----------|--------|-------------|---------------|-------------------|----------------|
| TG-01 | {FR-02} | {yes | no} | PRD traceability | Orphan FR-02 | EPIC-XX may address | {carry orphan note or BLOCKED} | Update PRD to close gap |
| PI-PRD-03 | {NFR-03, EPIC-01} | yes | PRD pending | NFR-03 target missing | Affects EPIC-01 DoD | BLOCKED | Resolve in PRD first |

### summary
- total_themes: {N}
- total_epics: {N}
- total_enablers: {N}
- total_spikes: {N}
- total_reclassified: {N}
- unaligned_epics: {N}
- uncovered_goals: {N}
- uncovered_personas: {N}
- pending_inputs: {N}
- prd_gaps_carried: {N}
- assumptions: {N}
- status: {draft | complete}
```

---

## Generation Rules

### Section Ordering
Generate sections in this order:
prd_id_ownership → themes → epics (with qualification gates) → dependencies (with circular resolution) →
sequencing → reclassification_log → persona_coverage → goal_coverage → open_questions.

Dependencies MUST come after all epics are qualified (including enablers created
by reclassification). Sequencing MUST come after dependencies (uses the graph).
`prd_id_ownership` is generated before themes/epics and is the authoritative
projection map for downstream research. open_questions is ALWAYS LAST —
consolidates from all prior sections.

### Epic Qualification (During Generation)

Process every FR-derived candidate through gates sequentially.
A candidate that fails a gate is reclassified, NOT discarded.

**Gate 1 — Discrete Deliverable:**
Can the team demo this independently?
- NO + research/exploration → SPIKE-XX
- NO + quality/process → DoD constraint on parent epic

**Gate 2 — NFR Overlap:**
Does candidate scope equal a PRD NFR?
- YES → DoD constraint on the functional epic(s) it supports
- Add NFR-XX and target to the functional epic's nfr_dod field

**Gate 3 — Enabler vs Feature:**
Is this documentation, infrastructure, or tooling?
- YES → type: enabler. Trace to KPI (not FR).
- No KPI or FR traceability → status: unaligned

**All decisions → reclassification_log entry.**

### Dependency Graph Construction
1. For each EPIC-XX: identify all blockers (epic-to-epic, technical, external, resource)
2. Every epic MUST appear in the table (including "none" dependencies)
3. Circular detection: scan for A→B AND B→A (direct) and A→B→C→A (transitive)
4. Resolution: extract shared interface into ENABLER-NNN
   - Scope: contract/interface definition ONLY (no business logic)
   - Both dependents implement against the contract independently
   - Add ENABLER-NNN to epics section with type: enabler, complexity: S
   - Log in circular_resolutions

### Topological Sequencing
1. Compute topological order from dependency graph (post circular resolution)
2. Map to phases using PRD mvp_phasing + dependency constraints
3. Validate: no blocked epic's phase starts before blocker's phase ends
4. If violation → auto-correct and log
5. If PRD execution plan conflicts with dependency-aware sequencing →
   dependency-aware takes precedence, note conflict for PRD update

### Consolidation Pass (Before Writing)
After generating all sections:
1. Verify every PRD ID appears exactly once in `prd_id_ownership` with disposition
   `owned`, `cross_cutting`, or `deferred`.
2. Every epic with status: unaligned → alignment_gaps in open_questions
3. Every persona with 0 epics → alignment_gaps
4. Every goal with 0 epics → alignment_gaps
5. Every assumption → assumptions_to_validate
6. Every PRD traceability gap → prd_gaps_carried_forward
7. Every PRD pending input affecting epics → prd_gaps_carried_forward
8. Compute summary counts
9. Set top-level status: `complete` if zero pending_inputs AND zero alignment_gaps.
   Otherwise: `draft`.

### Structured Contract Rules
- Native epics emitted by this skill declare `contract_format: structured`.
- `prd_source_hash` is sha256 from PRD `content_hash` when present; otherwise compute
  sha256 over the loaded PRD content for this run. Do not use mtime.
- `prd_id_ownership` covers every PRD ID from FR/NFR/JTBD/KPI/RSK/ASM/DEP/P/persona
  and PRD `literal_registry`.
- `open_questions` rows use `affected_ids`, `blocking`, and `fallback_behavior`.
- Source references use stable section/ID anchors, not line numbers.

### REPAIR Mode
- Load existing spec file
- Apply REPAIR_DIRECTIVES to targeted sections/epic IDs
- Preserve existing EPIC IDs. New epics continue from max(existing) + 1.
- Retired IDs never reused.
- If upstream PRD changed (new/removed FRs): rebuild affected epics
- Rebuild dependencies from scratch if any epic added/removed
- Rebuild sequencing from updated dependency graph
- Rebuild open_questions from scratch (always reflects current state)
- Increment version, log changes

### Won't Have / Deferred
PRD out_of_scope items and wont_have FRs MUST appear in sequencing.deferred.
This prevents scope creep by making exclusions explicit and traceable.
If PRD has no out-of-scope → note in open_questions.
