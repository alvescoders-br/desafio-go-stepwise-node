---
name: planning-epics
description: >
  Transforms a validated PRD spec into a delivery-ready epic-level backlog.
  Output is a single strict-markdown file with zero prose — structured epics
  with IDs, FR/NFR mappings, dependency graph, priority tiers, complexity sizing,
  and topological sequencing. Qualification gates (Deliverable, NFR Overlap,
  Enabler) applied during generation. Circular dependencies resolved via
  Enabler extraction. All unresolved items consolidated in `open_questions`.
  Human-readable output generated on demand via `humanize-spec` skill.
  BUILD and REPAIR modes. RPI workflow. FIC context discipline.
license: Proprietary
metadata:
  author: aipods-team
  version: 3.1.0
  category: product-management
  tags: product-definition, automated, agent-native
---

# Planning Epics — Agent-Native Spec

## Quick Start
Generate a structured epic backlog from a PRD spec. Output is a **single file**:
`{epics_output_path}/EPICS-SPEC-{SESSION_ID}.md`.
No prose. No narratives. No meeting agendas. Only structured data for downstream
agents (User Stories, Architecture, Implementation).

## Known Failure Modes
<!-- ACCUMULATING — appended by calibrating-updates (WS6). Newest first. Rules MUST be generic/behavioral (project-agnostic); project-specific fixes go to context packs, never here. Format + entry rules: engineering-skills/references/known-failure-modes-format.md. Read these at pre-flight so a lesson learned once recurs no more. -->

## Anti-Patterns (do NOT)
<!-- ACCUMULATING — appended by calibrating-updates (WS6). One line each: **AP-NNN** (ISO-date, source: REC-NNN): prohibition — why. -->

## Output Architecture

```
{epics_output_path}/
├── EPICS-SPEC-{SESSION_ID}.md     ← Single agent-native backlog spec
└── EPICS-AUDIT-{SESSION_ID}.md    ← Session audit trail (metadata only)
```

**Why single file:** Output is one file because downstream consumers expect one path.
This does **NOT** mean the spec is generated in a single inference call. This skill
applies the **section-shape protocol** defined in `context-pack/execution-protocol.md`
Section 10: skeleton-first + one-section-per-write + source extraction + CONTINUE
on re-entry. The skill-specific contract below (section list, dependency graph)
plugs into that protocol; the tool discipline (use `Write` for skeleton, `Edit`
for sections, never `Bash` heredoc mutations) lives in Section 10.5.

**HARD CONSTRAINT — Single output file.** This skill produces exactly 2 files:
`EPICS-SPEC-{SESSION_ID}.md` and `EPICS-AUDIT-{SESSION_ID}.md`. Do NOT split the
spec into multiple files (e.g., `batch-a-*.md`, per-section files). Per Section 10,
the spec is generated section-by-section *into the single EPICS-SPEC file* via
targeted edits — that is compatible with this constraint and is NOT batching.

**Human-readable output:** Not produced by this skill. Use `humanize-spec` skill
to generate rich backlog documents (story maps, value propositions, meeting agendas)
from this spec on demand.

## Parameters
| Name | Type | Required |
|------|------|----------|
| prd_output_path | string | Yes |
| project_name | string | Yes |
| epics_output_path | string | Yes |
| failure_feedback | string | No |

**If any Required parameter is not defined, ABORT EXECUTION.**

## Workflow

### Step 1: Initialize

**Command:**
```
# Backlog Generator Agent — Agent-Native Spec
# Persona: Senior Product Manager & Agile Practitioner
# CRITICAL: NON-INTERACTIVE SESSION.
# MISSION: Bridge PRD to actionable epic backlog. Zero invention.

IF failure_feedback NOT empty:
  MODE = REPAIR
  SPEC_FOLDER = resolve_parent_folder(epics_output_path)
  SPEC_FILE = find existing EPICS-SPEC-*.md in SPEC_FOLDER
  IF not found → write Gap Report → EXIT
  Load SPEC_FILE → PREVIOUS_SPEC → SOURCE_LOG
  PREVIOUS_VERSION = extract version
  NEW_VERSION = increment patch
  Parse failure_feedback → REPAIR_DIRECTIVES [{ section, epic_id, instruction, reason }]
ELSE:
  MODE = BUILD
  SPEC_FOLDER = epics_output_path + '/'
  SPEC_FILE = SPEC_FOLDER + 'EPICS-SPEC-' + SESSION_ID + '.md'
  NEW_VERSION = "1.0.0"
  mkdir -p SPEC_FOLDER

  ## SESSION_ID goes in spec FILENAMES only — never in the folder name.
  ## The folder must match the capability YAML path parameter exactly.

  ## FIRST ACTION — MANDATORY: Write _progress.json before any other file write.
  ## This prevents the orchestrator from sending SIGINT.
  ## Section-shape variant — see execution-protocol.md §10.1 for schema and §10.6 for CONTINUE-on-re-entry.
  WRITE {SPEC_FOLDER}/_progress.json:
    { "skill": "planning-epics", "session_id": "<SESSION_ID>",
      "status": "RUNNING", "started_at": "<ISO timestamp>", "completed_at": null,
      "skeleton_written": false,
      "sections": {
        "prd_id_ownership": "pending", "themes": "pending", "epics": "pending",
        "dependencies": "pending", "sequencing": "pending",
        "reclassification_log": "pending", "persona_coverage": "pending",
        "goal_coverage": "pending", "open_questions": "pending"
      } }

SOURCE_LOG = []
CHANGE_LOG = []

## Zero Invention Policy
Every epic must trace to PRD. No invention.
Inferred groupings → status: assumption (with rationale).

## Internal Reasoning: ALL in English regardless of output language.

```
**Execution:** automated


### Step 2: Load PRD Context

**Command:**
```
## PRD Ingestion
Load PRD spec file (or PRD index + batch files if legacy multi-file PRD).
Extract into STRATEGIC_MAP:

  PRD_DATA = {
  contract_format: {structured | absent},
  content_hash: {sha256 | absent},
  fr_ids: {FR-XX → { requirement, priority, acceptance_criteria, source }},
  nfr_ids: {NFR-XX → { category, requirement, target, source }},
  jtbd_ids: {JTBD-XX → { type, situation, motivation, outcome }},
  kpi_ids: {KPI-XX → { description, target, measurement, timeframe }},
  personas: {P-XX → { role, type, goals, pain_points }},
  risks: {RSK-XX → { risk, likelihood, impact, mitigation }},
  assumptions: {ASM-XX → { assumption, impact_if_wrong }},
  dependencies: {DEP-XX → { type, description, impact }},
  literal_registry: {LIT-XX → {name, exact_value, type, applies_to_ids}},
  scope: { in: [...], out: [...] },
  traceability_gaps: [from PRD open_questions],
  pending_inputs: [from PRD open_questions],
  mvp_phasing: { phase_1: [...], phase_2: [...], phase_3: [...], deferred: [...] }
}

Detect language → DETECTED_LANGUAGE

IF MODE == REPAIR:
  Load existing SPEC_FILE sections → identify repair targets
  Apply REPAIR_DIRECTIVES
```
**Execution:** automated

### Step 3: Generate Agent-Native Backlog Spec

**Apply execution-protocol.md Section 10** — Phase A (skeleton-first) then Phase B (one section per `Edit` call). Tool discipline (§10.5) is **mandatory**: skeleton via `Write`, sections via `Edit`, NEVER `Bash + sed/python3/awk` to mutate SPEC_FILE. The non-ASCII fallback (§10.5.1) auto-applies when the spec contains non-English content. NEVER fall back to bulk rewriting when one `Edit` fails — fix the `Edit` call instead.

**Skeleton stub text — must be ASCII:**

> `status: pending - will be generated`

ASCII hyphen (U+002D), not em dash. Non-ASCII characters in the stub create encoding traps if anything later reads or matches the stub via shell tools.

**Section list (template order):**

```
prd_id_ownership -> themes -> epics -> dependencies -> sequencing -> reclassification_log ->
persona_coverage -> goal_coverage -> open_questions
```

**Cross-section dependency graph** (which sections read SPEC_FILE for prior state, per §10.4 step 1):

| Section | Reads from SPEC_FILE |
|---------|----------------------|
| `prd_id_ownership` | none — PRD_DATA is sufficient |
| `dependencies` | `epics` (to detect cycles, build graph) |
| `sequencing` | `epics` + `dependencies` |
| `reclassification_log` | `epics` (consolidates gate decisions) |
| `persona_coverage` | `epics` |
| `goal_coverage` | `epics` |
| `open_questions` | ALL prior populated sections (consolidates pending, gaps, assumptions, traceability gaps carried forward from PRD) |
| `themes` | none — extraction inputs (PRD_DATA) sufficient |
| `epics` | none — extraction inputs (PRD_DATA) sufficient |

Read `references/backlog-template.md` for section structure.

Generate the complete backlog following the template. Apply these rules:

**Structured Contract Rule:**
Native epics emitted by this skill declare `contract_format: structured`, record
`prd_source_hash` as sha256 from PRD `content_hash` when available (otherwise
computed over the loaded PRD content), generate complete `prd_id_ownership`, and
emit enriched `open_questions` with `affected_ids`, `blocking`, and
`fallback_behavior`. Source references must use stable section/ID anchors.

**Epic Qualification Gates (apply to every candidate):**

Gate 1 — Discrete Deliverable Test:
  Can the team demo this independently?
  NO → reclassify as SPIKE-XX (research) or embed as DoD constraint.

Gate 2 — NFR Overlap Test:
  Does this candidate's scope equal a PRD NFR?
  YES → embed as DoD constraint on functional epic(s), not standalone epic.

Gate 3 — Enabler vs Feature Test:
  Is this documentation, infrastructure, or tooling?
  YES → type: enabler. Trace to KPI. No KPI or FR trace → flag unaligned.

**All gate decisions logged in `reclassification_log` section.**

**Circular Dependency Resolution:**
After generating all dependencies, scan for cycles (direct and transitive).
Resolution: extract shared interface into ENABLER-NNN epic.
Both dependent epics implement against the contract independently.
Never leave a cycle unresolved with "build stubs" mitigation.

**Persona Coverage:**
Every PRD persona must be served by ≥1 epic.
Persona with zero epics → registered in open_questions.

**Priority Derivation:**
Combine KPI alignment + dependency position (blockers rank higher) + PRD MoSCoW.

**Sequencing:**
Produce topological order from dependency graph.
Validate: no blocked epic scheduled before its blocker.

**open_questions Consolidation:**
After generating all sections, consolidate:
- Every PRD ID absent from `prd_id_ownership` → validation failure, fix before completion
- Every assumption → assumptions_to_validate
- Every unaligned epic → open_questions
- Every uncovered goal → open_questions
- Every persona with zero epics → open_questions
- PRD traceability gaps → carried forward (never silently resolved)
- PRD pending inputs → carried forward if they affect epics

**Execution:** automated

### Step 4: Quality Validation Gate

**Command:**
```
 1. ID Consistency: EPIC-IDs unique, no gaps, spikes/enablers properly typed
 2. Dependency Integrity: No circular dependencies remain
 3. Sequencing: No blocked epic before its blocker in topological order
 4. Coverage: Every PRD persona has ≥1 epic. Every PRD goal has ≥1 epic.
 5. Traceability: Every epic traces to ≥1 FR or KPI (except unaligned, flagged)
 6. NFR Embedding: Every PRD NFR appears as DoD constraint on ≥1 functional epic
 7. Bias Check: No technology names, vendor names not in PRD sources
 8. open_questions: Every gap/assumption/unaligned item appears exactly once
 9. Won't Have: PRD out_of_scope items appear in deferred section
10. Epic Value-Driven: Every epic defines a discrete, demonstrable business or user
    benefit — not a grouping label. Generic business value (e.g., "improves system")
    is a violation; must be specific and traceable to a PRD JTBD or KPI.
11. Epic Sizing: No epic scoped at "entire project" level. Every epic must be
    decomposable into ≤10 user stories. XL epics that cannot be split → flag in
    open_questions with split recommendation.
12. Strategic Alignment: Every feature epic addresses ≥1 PRD FR or JTBD. Every
    enabler traces to ≥1 PRD KPI. Epics with no FR/JTBD/KPI trace → status: unaligned.
13. Input/Output Count: Count FRs in PRD vs FRs covered by ≥1 epic.
    LOG: "FR coverage: {N} of {M} FRs mapped."
    If N < M → list unmapped FR-IDs in open_questions.pending_inputs.
    STOP-GATE: If coverage < 80% → re-execute Step 3 before writing outputs.
14. Cross-Artifact ID Integrity: Every FR-XX referenced inside any epic MUST exist
    in the PRD lookup table. Every EPIC-ID appearing in dependencies or sequencing
    MUST exist in the epics section.
    MISMATCH → auto-correct (remove phantom ID or add missing epic) and log to CHANGE_LOG.
15. PRD Ownership Map: Every PRD FR/NFR/JTBD/KPI/RSK/ASM/DEP/P/persona and
    literal_registry ID appears exactly once in `prd_id_ownership` with disposition
    `owned`, `cross_cutting`, or `deferred`.
    MISSING → add ownership row or block in open_questions with `blocking: yes`.
16. Structured Contract: `contract_format: structured`, `prd_source_hash`, enriched
    open_questions, and stable ID anchors are present.

IF corrections needed → apply in place, log to CHANGE_LOG

STOP-GATE: IF zero epics qualified → re-execute with relaxed Gate 1. If still zero → ABORT.
```
**Execution:** automated

### Step 5: Write Outputs

**MVP Scope Filter (MANDATORY before writing the canonical backlog):**

Every epic written to SPEC_FILE MUST trace to (a) at least one FR-ID / NFR-ID in PRD-SPEC AND (b) at least one MVP bullet in `project-brief.md` (or its equivalent input). Items that fail either trace MUST move to `deferred_candidates[]` in AUDIT_FILE instead of the canonical SPEC_FILE.

```
mvp_bullets = parse_mvp_section(project_brief_path)   # § "MVP Scope" or equivalent
deferred_markers = collect_deferred_markers(
    PREVIOUS_REVIEW_FEEDBACK,                          # reviewer prior "out of scope" notes
    [PRD_SPEC])                                        # explicit deferred_out_of_mvp / phase-3 markers

CANONICAL_EPICS = []
DEFERRED_CANDIDATES = []
DEFERRED_REASONS = {}

FOR EACH epic in candidate_epics:
  fr_ac_trace = epic.source_refs ∩ {FR-IDs, NFR-IDs in PRD_SPEC}
  brief_trace = any(semantic_overlap(epic, b) > threshold for b in mvp_bullets)
  IF epic.id IN deferred_markers:
    DEFERRED_CANDIDATES.append(epic)
    DEFERRED_REASONS[epic.id] = "marked deferred upstream: " + deferred_markers[epic.id]
  ELIF fr_ac_trace AND brief_trace:
    epic.brief_anchor = matching_bullet.id
    CANONICAL_EPICS.append(epic)
  ELSE:
    DEFERRED_CANDIDATES.append(epic)
    reasons = []
    IF NOT fr_ac_trace: reasons.append("no PRD FR/NFR traceability")
    IF NOT brief_trace: reasons.append("no project-brief MVP bullet match")
    DEFERRED_REASONS[epic.id] = "; ".join(reasons)

## Only CANONICAL_EPICS flow into SPEC_FILE. DEFERRED_CANDIDATES are listed
## in AUDIT_FILE so the reviewer can decide whether to re-include (by
## adjusting project-brief / PRD) or accept the deferral.
```

**Command:**
```
1. Write SPEC_FILE (EPICS-SPEC-{SESSION_ID}.md) — ALL sections in ONE file
   (only CANONICAL_EPICS — see MVP Scope Filter above).
   - Set the SPEC front-matter `version:` to NEW_VERSION. On REPAIR this MUST be the
     incremented patch (Step 1: PREVIOUS_VERSION → NEW_VERSION) — editing the content
     in place without bumping `version` is a §7 violation. See execution-protocol §7.2 step 8.
2. Write AUDIT_FILE (EPICS-AUDIT-{SESSION_ID}.md):
   - Session metadata (version=NEW_VERSION, mode, session_id, timestamp, language)
   - Sources referenced (SOURCE_LOG)
   - Reclassification log (all gate decisions)
   - deferred_candidates[]: list of DEFERRED_CANDIDATES with DEFERRED_REASONS
   - Decisions made (CHANGE_LOG)
   - Summary counts: themes, epics, enablers, spikes, deferred_candidates, open_questions
   - Structured contract validation result, `prd_source_hash`, and PRD ownership counts
   - REPAIR-only: set `mode: REPAIR` and APPEND (do not overwrite) a `## Repair History`
     entry — version, timestamp, directives_applied, sections_changed, sections_preserved,
     repair_delta (per execution-protocol §7.2 step 8).
3. REPAIR self-check (execution-protocol §7.2 step 9): before final_response, confirm the
   SPEC `version` is strictly greater than PREVIOUS_VERSION AND the AUDIT has the new
   `## Repair History` entry. If not, fix the bookkeeping now — do not finish.
4. Verify EXACTLY 2 files exist and are non-empty
5. Verify NO other files were written (no batch-*.md, no per-section splits)

VIOLATION: Writing batch-a-*.md, batch-b-*.md, per-section files, or any file
other than EPICS-SPEC and EPICS-AUDIT is a contract violation. If this happens,
consolidate all content into the single SPEC_FILE before completing.


Memory Bank artifact type: `"{N} epics"` (e.g., `"15 epics"`).

**Memory Bank — MANDATORY session-end writes:**
1. Overwrite `context-pack/active-context.md` with session status, decisions, blockers, key artifacts (see execution-protocol.md Section 4 for schema).
2. Append one milestone row to `context-pack/progress.md` with artifact count above.

**LAST ACTION — MANDATORY:** Update `_progress.json` status to `COMPLETED` with `completed_at` timestamp.
If the session failed, set status to `FAILED` instead.

Ready for downstream consumption (User Stories, Architecture, Implementation).
```
**Execution:** automated

### Step 6: Emit Harness Outputs Sidecar

**Apply execution-protocol.md Section 11.** Mandatory when the prompt contains a `## Run metadata` block (Stepwise invocation); skip otherwise (standalone invocation).

**Output parameters this skill produces** (one key per row of the prompt's `## Output parameters` table):

- `epics_output_path`: the resolved `epics_output_path` parameter — the SPEC_FOLDER you wrote into in Steps 1–5.

**Example sidecar contents** (values illustrative):

```json
{ "epics_output_path": "/abs/path/to/artifacts/outputs/<capability>/epics" }
```

**Execution:** automated

## FR ID Consistency Validation (MANDATORY)

Before generating acceptance criteria for any epic, build a complete FR reference table from the PRD:

```
1. Extract every FR from the PRD: FR-ID, title, description, phase, status
2. Build a lookup table: { "FR-01": {title, description}, "FR-02": {...}, ... }
3. For every FR reference in your epics output:
   - Verify the FR-ID matches the lookup table exactly
   - Use the exact title from the PRD — no paraphrasing or abbreviation
   - If an FR is deferred or out of scope, use its exact PRD ID and title to document the exclusion
4. If an FR ID is referenced but not found in the PRD: flag as ASSUMPTION in open_questions
```

VIOLATION: Referencing an FR ID with a title that does not match the PRD is a traceability failure. All FR references must be verified against the PRD lookup table before writing.

## Common Rationalizations

| Excuse | Why It Fails | Counter |
|--------|-------------|---------|
| "This FR is too small for its own epic, I'll merge it with another" | Merged FRs lose traceability. Downstream stories can't map back to individual requirements. | Use the Qualification Gates (Deliverable, NFR Overlap, Enabler) to classify. Small FRs become enablers, not merged epics. |
| "The dependency graph is obvious, I don't need to formalize it" | Informal dependencies become circular dependencies at implementation time. Topological sort catches what intuition misses. | Build the explicit dependency graph. Run cycle detection. Document the ordering rationale. |
| "I'll estimate complexity later during story decomposition" | Epics without complexity sizing produce unbalanced sprints. Stories inherit undefined scope. | Size every epic: XS/S/M/L/XL. XL epics must be split before proceeding. |
| "All epics are Must Have priority" | If everything is priority 1, nothing is. The implementing agent has no sequencing guidance. | Apply MoSCoW rigorously. At least 20% of epics should be Should Have or Could Have. |
| "The PRD already defines the epics" | PRDs define requirements, not delivery units. Epics add: dependencies, sizing, acceptance criteria, priority tiers. | Transform, don't transcribe. Every epic must add value beyond what the PRD already states. |

## Red Flags

Signs that this epic backlog is being generated superficially or incorrectly:

- All epics have identical complexity sizing (indicates no actual estimation)
- Zero enabler or spike epics (complex projects always have technical prerequisites)
- Dependency graph has no edges (unrealistic — epics almost always have dependencies)
- FR IDs referenced don't match PRD lookup table (traceability failure)
- Epic titles are just FR titles copied verbatim (no decomposition happened)
- All epics assigned same priority tier (no prioritization analysis)
- Acceptance criteria are generic ("epic is complete when all stories are done")
- Open questions section is empty on a 10+ epic backlog

## Verification Checklist

Every item requires **evidence**, not assertion. "Seems right" is never sufficient.

- [ ] Every FR from PRD maps to at least one epic — Evidence: FR-to-epic traceability matrix; FR coverage ≥ 80%
- [ ] FR IDs match PRD exactly — Evidence: lookup table comparison (FR-ID + title match)
- [ ] Dependency graph is acyclic — Evidence: topological sort completes without cycle detection errors
- [ ] Complexity sizing applied to every epic — Evidence: size field populated (XS/S/M/L/XL), no XL remaining
- [ ] Priority tiers distributed — Evidence: at least 2 different priority levels used across epics
- [ ] Qualification gates applied — Evidence: reclassification log in AUDIT file shows gate decisions
- [ ] Acceptance criteria are testable — Evidence: each epic AC contains specific, measurable conditions
- [ ] Epic value is specific — Evidence: every epic business_value field references a JTBD or KPI, not generic prose
- [ ] No over-scoped epics — Evidence: every epic estimated at ≤10 stories (or flagged in open_questions)
- [ ] PRD ownership complete — Evidence: every PRD ID has one `prd_id_ownership` row
- [ ] Structured contract emitted — Evidence: `contract_format: structured`, `prd_source_hash`, enriched open_questions
- [ ] Strategic alignment verified — Evidence: every feature epic has ≥1 FR/JTBD ref; every enabler has ≥1 KPI ref
- [ ] Input/Output count logged — Evidence: "FR coverage: N of M FRs mapped" appears in AUDIT file
- [ ] Cross-artifact IDs clean — Evidence: zero phantom FR-IDs or EPIC-IDs detected in CHANGE_LOG check
- [ ] Single output file produced — Evidence: exactly 2 files (EPICS-SPEC + EPICS-AUDIT), no batch splits

## Reference Files
- `references/backlog-template.md` — Agent-native backlog spec structure
