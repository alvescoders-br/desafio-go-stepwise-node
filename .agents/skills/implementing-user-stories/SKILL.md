---
name: implementing-user-stories
description: >
  Decomposes validated epics into agent-consumable user stories with layered domain
  tags (BE/FE/DATA/INFRA/AI), structured acceptance criteria (Given/When/Then),
  mandatory technical matrix scenarios per domain tag, and full traceability.
  Output is a manifest file (story_map + dependencies + open_questions) plus
  one story-definition file per epic. The manifest is lightweight (~5K tokens
  for 400-story projects) and always loadable. Per-epic files are loaded on
  demand by the implementing agent — only the epic currently being worked on
  needs to be in context. This architecture scales to any project size without
  context overflow at either generation or consumption time.
  Human-readable output via `humanize-spec` skill on demand.
license: Proprietary
metadata:
  author: aipods-team
  version: 3.0.0
  category: product-management
  tags: product-delivery, automated, agent-native
---

# Implementing User Stories — Agent-Native Spec

## Quick Start
Decompose epics into sprint-ready user stories. Output is a **manifest + per-epic files**:

```
{stories_output_path}/
├── STORIES-MANIFEST-{SESSION_ID}.md     ← Story map + deps + open_questions (~5K tokens)
├── epics/
│   ├── epic-01.md                       ← Story definitions for EPIC-01 (~500 tokens)
│   ├── epic-02.md                       ← Story definitions for EPIC-02
│   └── ...
└── STORIES-AUDIT-{SESSION_ID}.md        ← Session metadata
```

## Known Failure Modes
<!-- ACCUMULATING — appended by calibrating-updates (WS6). Newest first. Rules MUST be generic/behavioral (project-agnostic); project-specific fixes go to context packs, never here. Format + entry rules: engineering-skills/references/known-failure-modes-format.md. Read these at pre-flight so a lesson learned once recurs no more. -->

## Anti-Patterns (do NOT)
<!-- ACCUMULATING — appended by calibrating-updates (WS6). One line each: **AP-NNN** (ISO-date, source: REC-NNN): prohibition — why. -->

## Why This Architecture

The implementing agent processes ONE story at a time in its RPI cycle.
It does not need 400 stories in context to implement one.

**Manifest (always loaded):** Story IDs, dependency graph, open_questions.
~4 lines per story. Even 400-story projects = ~5K tokens. Cheap to keep in context.

**Per-epic files (loaded on demand):** Full story definitions.
~28 lines per story, 4-8 stories per epic = ~200 lines per file.
The implementing agent loads the current epic, works through its stories,
drops it, loads the next. Context consumption: ~5,500 tokens regardless
of project size.

**Contrast with single-file approach:**
- 60 stories → ~6K tokens (fine)
- 120 stories → ~12K tokens (tight)
- 400 stories → ~39K tokens (unusable — consumes the implementing agent's entire context budget)

**Contrast with original human-readable approach:**
- 60 stories × 90 lines = 5,400 lines → ~16K tokens per epic file
- Plus the implementing agent must "digest" prose into actionable instructions
- Plus the per-epic atomic loop with 3-story chunking was needed to GENERATE

This architecture eliminates both the generation bottleneck (per-epic write-flush
is trivial with 28-line stories) and the consumption bottleneck (on-demand loading).

## Parameters
| Name | Type | Required |
|------|------|----------|
| epics_output_path | string | No |
| prd_path | string | No |
| project_name | string | Yes |
| user_stories_output_path | string | Yes |
| meeting_recording_path | string | No |
| transcript_output_path | string | No |
| failure_feedback | string | No |

**At least one of epics_output_path or prd_path MUST be provided.**

## Workflow

### Step 0: Silent Pre-Computation

```
# User Story Agent — Agent-Native Spec Generator
# NON-INTERACTIVE SESSION. PROCEED AUTONOMOUSLY.

Pre-Computation (DO NOT OUTPUT):
1. Deconstruct each Epic into atomic functional requirements.
2. Story vs Task Filter: Merge technical tasks into functional stories.
3. Layer Strategy: Determine domain per requirement (FE, BE, DATA, INFRA, AI).
4. Scenario Storming per story: Integrity, Duplicity, Security, Limits.
5. Gap Check: Identify missing inputs.
```
**Execution:** automated


### Step 1: Initialize

```
IF failure_feedback NOT empty:
  MODE = REPAIR
  SPEC_FOLDER = resolve_parent_folder(user_stories_output_path)
  MANIFEST = find existing STORIES-MANIFEST-*.md
  IF not found → Gap Report → EXIT

  ## REPAIR FILENAME CONTRACT — MANDATORY
  ## 1. Extract ORIGINAL_SESSION_ID from the found manifest filename.
  ##    Example: STORIES-MANIFEST-20260423-140000.md → ORIGINAL_SESSION_ID = "20260423-140000".
  ## 2. REUSE ORIGINAL_SESSION_ID for ALL file writes in REPAIR mode:
  ##      SESSION_ID = ORIGINAL_SESSION_ID
  ##      MANIFEST   = SPEC_FOLDER + 'STORIES-MANIFEST-' + SESSION_ID + '.md'
  ##      AUDIT_FILE = SPEC_FOLDER + 'STORIES-AUDIT-'    + SESSION_ID + '.md'
  ## 3. OVERWRITE the original manifest and audit in place. Epic files in epics/
  ##    remain under their existing names (epic-NN.md) and are edited in place.
  ## 4. FORBIDDEN in REPAIR mode:
  ##      - generating a new SESSION_ID
  ##      - creating STORIES-MANIFEST-<NEW>.md / STORIES-AUDIT-<NEW>.md alongside originals
  ##      - renaming or duplicating epic-NN.md files
  ## 5. Versioning lives in the manifest's `version:` field, NEVER in the filename.
  ##    Bump patch (e.g., 1.0.1 → 1.0.2) inside the file content only.

  SESSION_ID = ORIGINAL_SESSION_ID
  Load MANIFEST → PREVIOUS_MANIFEST → SOURCE_LOG
  PREVIOUS_VERSION = extract version → NEW_VERSION = increment patch
  Parse failure_feedback → REPAIR_DIRECTIVES [{ epic_id, story_id, instruction }]

  ## Open-Question Resolution Pass (MANDATORY before regeneration)
  ##
  ## Convert PREVIOUS_MANIFEST.open_questions entries that the reviewer
  ## answered into STORIES_INDEX.decisions_confirmed before regenerating any
  ## epic or story. Re-emitting a question the reviewer already answered is a
  ## protocol violation.
  FOR EACH oq in PREVIOUS_MANIFEST.open_questions:
    FOR EACH directive in REPAIR_DIRECTIVES:
      IF directive references oq.id OR
         directive.instruction semantically answers oq.question:
        decision = {
          id: derive_decision_id(oq.id),
          topic: oq.topic,
          decision: extract_answer(directive.instruction),
          source: "reviewer-feedback@" + directive.timestamp,
          confidence: "confirmed"
        }
        STORIES_INDEX.decisions_confirmed.append(decision)
        PREVIOUS_MANIFEST.open_questions.remove(oq)
        LOG to SOURCE_LOG: "OQ resolved by reviewer: " + oq.id + " → " + decision.id
        break

  ## Zero Re-Ask Rule: in the regenerated MANIFEST and epic files, NEVER
  ## emit an open_question that shares topic / epic_id / story_id / AC anchor
  ## with any entry in STORIES_INDEX.decisions_confirmed.
ELSE:
  MODE = BUILD
  SPEC_FOLDER = user_stories_output_path + '/'
  ## SESSION_ID goes in spec FILENAMES only — never in the folder name.
  ## The folder must match the capability YAML path parameter exactly.
  MANIFEST = SPEC_FOLDER + 'STORIES-MANIFEST-' + SESSION_ID + '.md'
  NEW_VERSION = "1.0.0"
  mkdir -p SPEC_FOLDER
  mkdir -p SPEC_FOLDER/epics/

  **FIRST ACTION — MANDATORY:** Write `_progress.json` to the output folder before any other file write.
  This prevents the orchestrator from sending SIGINT. See execution-protocol.md Section 2 for the schema.

  CHECKPOINT_FILE = SPEC_FOLDER + 'epics/_checkpoint.json'

  ## Resume from checkpoint (if interrupted mid-epic-generation)
  IF CHECKPOINT_FILE exists:
    Load CHECKPOINT_FILE → STORY_INDEX (includes completed_epics, story_counts, traceability)
    LOG: "RESUME: loaded checkpoint. Epics completed: {completed count}."
    # The Write-Flush-Forget loop will skip already-completed epics.

SOURCE_LOG = []
CHANGE_LOG = []

## Zero Invention Policy
Every story must trace to an epic and PRD requirement. No invention.
Inferred groupings or scenarios → status: assumption (with rationale).
Never fabricate story IDs, acceptance criteria, or domain tags not supported by upstream artifacts.

```
**Execution:** automated

### Step 1.5: Input Validation Gate

```
REQUIRED:
  1. Epics backlog at epics_output_path — prioritized epics with FR mappings
  2. PRD at prd_path — FR-XX, NFR-XX, ASM-XX, RSK-XX, JTBD-XX

IF missing → Gap Report → EXIT

PRD_CONTEXT = {
  contract_format, content_hash,
  fr_descriptions: {FR-XX → { description, acceptance_criteria, priority }},
  nfr_ids: {NFR-XX → { category, target }},
  literal_registry: {LIT-XX → {name, exact_value, type, applies_to_ids}},
  asm_ids, rsk_ids, jtbd_ids, kpi_ids, personas,
  traceability_gaps, pending_inputs, api_paths, enriched_open_questions
}

EPIC_CONTEXT = {
  contract_format, prd_source_hash,
  epic_list: [ordered EPIC-IDs],
  epic_scope: {EPIC-XX → { title, fr_ids, nfr_ids, jtbd_ids, kpi_ids,
    priority_tier, complexity, personas, rsk_refs, asm_refs }},
  prd_id_ownership: {prd_id → disposition, epic_ids, phase},
  persona_coverage: {EPIC-XX → [personas]},
  enhancement_gaps: [from Epics open_questions],
  enriched_open_questions
}
```
**Execution:** automated

### Step 2: Upstream Consistency Rules (Loaded Once)

```
1. Technology Neutrality — no specific tech names, capability-level language
2. NFR ID Preservation — PRD's NFR-XX IDs verbatim
3. RSK Carry-Forward — epic RSK-XX refs mandatory in story traceability
4. ASM Carry-Forward — epic ASM-XX refs mandatory in story traceability
5. Persona Coverage — multi-persona epics acknowledged in stories
6. Upstream Gap Surfacing — PRD/Epics gaps carried forward
7. PRD Fidelity — API paths, field names preserved. Changes = assumption
8. KPI Traceability — each KPI-XX referenced by implementing story
9. Epic Scope Fidelity — stories decompose ONLY in-scope FRs (anti-hallucination)
10. FR ID Format Fidelity — exact format from PRD, never invent IDs
11. Literal/Fallback Inheritance — PRD literal_registry and upstream
    fallback_behavior rows affecting an epic/story are copied by ID, not rewritten.
12. Architecture Authority — stories may include behavior and sourced constraints;
    unsourced paths, packages, layers, framework choices, storage tools, runtime
    topology, or module placement are forbidden.
```
**Execution:** automated (loaded into context)

### Step 3: Generate Manifest + Per-Epic Files

**EARLY-WRITE RULE — MANDATORY (silent-failure prevention).**
Within **5 tool calls** of entering Step 3 — counting ANY tool call — you MUST
write the MANIFEST file to disk with header metadata + story_map skeleton +
section stubs. Then enter the per-epic Write-Flush-Forget loop in Phase B —
one epic file per edit. Multi-minute thinking loops with no on-disk progress
trigger orchestrator SIGINT or context overflow and lose 100% of the work.
Update `_progress.json` after the manifest write and after each epic file is
committed.

Read `references/stories-template.md` for structures.

**Pattern Reuse Search (MANDATORY before declaring a story that proposes a NEW component / integration / runtime):**

When a story implies a new system element (e.g., a new sync job, a new background worker, a new gateway), the agent MUST search the context-pack for an existing pattern. Inventing a new element when one is documented is a protocol violation.

```
CP_FILES = <context-pack files surfaced in the system prompt at
            session start (loaded by the harness)>

FOR EACH proposed in candidate_components_implied_by_stories:
  search_terms = derive_search_terms(proposed)   # nouns + stems from name/purpose
  matched = false
  FOR EACH file in CP_FILES:
    IF exists(file):
      hits = grep_case_insensitive(file, search_terms)
      IF hits:
        proposed.pattern_source = file + "#" + hits[0].line
        proposed.classification = "reuse"
        record_in_audit:
          "Pattern reuse: story-implied '" + proposed.name + "' grounded in " + file
        matched = true; break
  IF NOT matched:
    proposed.classification = "new"
    record_in_audit:
      "Pattern reuse search: no existing pattern for story-implied '" +
      proposed.name + "'. Searched " + len(CP_FILES) + " context-pack files."

## Reuse-classified items MUST appear verbatim in story titles, ACs, and
## technical-matrix scenarios — do NOT rename or paraphrase the existing pattern.
```

**Generation is a two-phase process:**

**PHASE A — Story Map + Dependencies (→ MANIFEST)**
1. Decompose ALL epics into story IDs with domain tags and titles.
   Apply Layered Decomposition rules. Assign IDs (source of truth).
2. Map ALL story-to-story dependencies. Cross-layer mandatory.
3. Write story_map and dependencies sections to MANIFEST (partial write).

**PHASE B — Story Definitions (→ per-epic files, sequential loop)**

> **Parallel fan-out — DISPATCH DECISION (execution-protocol.md Section 14). Make this
> decision BEFORE writing any epic file.**
>
> At Phase B entry, choose the dispatch mode:
> - **IF the harness can dispatch multiple workers in a single turn AND
>   `len(EPIC_CONTEXT.epic_list) >= 3` → fan out BY DEFAULT.** Concurrent foreground workers
>   alone qualify — background/detached tasks are NOT required, and an ABSENT
>   `Parallel delegation:` advertisement does NOT force inline (execution-protocol.md §14
>   Applicability); fall back only when the harness is genuinely single-dispatch. Dispatch one
>   parallel worker per epic, and **emit all epic workers in ONE turn (§14.3 step 2) —
>   one-worker-per-turn serializes them.** Do NOT fall back to the sequential loop. Each worker
>   generates and writes ONLY its own `epics/epic-{NN}.md` (running that epic's per-story
>   fidelity checks) and returns a compact result (epic id + story ids/count). **Workers NEVER
>   write the MANIFEST, `_checkpoint.json`, `_progress.json`, or the §11 sidecar** — those are
>   yours.
> - **ELSE (harness is genuinely single-dispatch, or < 3 epics) → run the inline `FOR EACH
>   epic` loop below.**
>
> Independence proof: Phase A already produced the full `story_map` + cross-story
> `dependencies` in the MANIFEST (coordinator-serial), so each epic's file generates from its
> own `epic_scope` + FR descriptions + the manifest and does NOT read another epic's file.
> Every cross-epic concern (Anti-Fade Check 10, Input/Output counts Check 16, Cross-Artifact
> ID integrity Check 17, consolidated open_questions) is Phase C coordinator work. Merge
> contract (coordinator, serial): after the workers finish, YOU run Phase C (17 validations +
> anti-fade + counts + open_questions), finalize the MANIFEST, and emit the §11 sidecar last.
> No worktree isolation is needed — each worker writes a distinct epic file, not shared source.
> The manifest, epic files, and validations are IDENTICAL whether you fanned out or ran inline.
> Verify any worker-reported story/FR id against the manifest before it enters Phase C
> (Zero-Invention).

FOR EACH epic in EPIC_CONTEXT.epic_list (ordered by priority):   ## inline path — used per the dispatch decision above when the harness is genuinely single-dispatch or there are < 3 epics

  LOAD: epic_scope, FR descriptions, personas, RSK/ASM refs
  IF any missing → log gap, skip epic

  GENERATE: All stories for this epic using template
  PER-STORY FIDELITY CHECK:
    - Title relates to epic domain? If not → regenerate
    - Traceability references ONLY in-scope FR-XX? If not → fix
    - Content matches loaded FR descriptions? If not → regenerate
    - Acceptance criteria use globally stable IDs (`US-XX-YY-AC-ZZ` or the story
      ID prefix plus `-AC-ZZ` when the story ID includes a domain tag)
    - Inherited literals/fallbacks affecting the story are present by upstream ID
    - Sourced constraints include a source_ref; unsourced structural mandates are
      moved to open_questions or removed

  WRITE: epics/epic-{NN}.md (IMMEDIATE tool call)
  FLUSH: Drop story content from memory
  WRITE CHECKPOINT: Serialize STORY_INDEX to CHECKPOINT_FILE (_checkpoint.json).
  CONTINUE to next epic (do NOT stop)

**PHASE C — Validations + Open Questions (→ append to MANIFEST)**
After all epics complete:
1. Run 17 validation checks
2. Consolidate open_questions
3. Capacity Alert: If total story count × average complexity (S=2, M=3, L=5 pts)
   exceeds EPIC_CONTEXT total complexity budget (sum of epic complexity scores):
   Add capacity_overflow entry to open_questions listing stories that exceed budget.
   This is informational — do NOT remove stories, only flag the overflow.
4. Append validations + open_questions to MANIFEST
5. Set top-level status

**Execution:** automated

### Step 4: Quality Validation Gate

```
17 checks:
 1. Completeness — every FR covered by ≥1 story
 2. Relevance — every story traces to parent epic FR/JTBD
 3. ID Consistency — manifest IDs = epic file IDs
 4. Technology Neutrality — no tech names
 5. NFR Preservation — PRD IDs used
 6. RSK/ASM Carry-Forward — all epic refs in stories
 7. Persona Coverage — multi-persona epics acknowledged
 8. KPI Coverage — every KPI referenced
 9. API Path Fidelity — PRD paths preserved
10. Anti-Fade — STOP-GATE: last epic file AC count per story must be ≥50% of
    first epic's (adjusted for complexity). If violated → mark ANTI-FADE VIOLATION
    and regenerate affected stories before completing.
11. DoD Consistency — tag-appropriate DoD on every story
12. AC Minimum — ≥4 scenarios per story
13. Domain Technical Matrix — domain-specific mandatory scenarios enforced per tag:
    [FE] / [MOBILE]: MUST include ≥1 API/network error scenario (timeout, HTTP 500)
      AND ≥1 visual state scenario (loading state, empty state, skeleton screen).
    [BE] / [DATA] / [INFRA]: MUST include ≥1 system failure scenario (DB down,
      external API timeout) AND ≥1 security/auth scenario (invalid token, unauthorized
      scope, rate limiting).
    Violation: tag-required scenarios absent → flag story ID in open_questions.
14. INVEST Compliance — every story must satisfy all 6 dimensions:
    I — Independent: no overlapping logic with a sibling story in same epic
    N — Negotiable: specifies what/why, not how (no implementation mandates)
    V — Valuable: articulates a specific business or user benefit (even BE stories)
    E — Estimable: scope clear enough to size in story points
    S — Small: fits within a single sprint
    T — Testable: all ACs are binary pass/fail
    Violations → flag story ID + dimension in open_questions.
15. Story vs Task — zero pure-technical tasks exist as standalone stories. A task
    delivers no user value and has no acceptance criteria. Technical tasks MUST be
    merged into a parent functional story's in_scope list or DoD constraints.
    Violation → merge task into nearest functional story and log to CHANGE_LOG.
16. Input/Output Count — epic_file_count MUST equal manifest.story_map epic count.
    Total story IDs across all epic files MUST equal total story IDs in manifest.
    LOG: "Coverage: {N} epic files / {M} epics in manifest; {P} stories in files /
    {Q} story IDs in manifest."
    MISMATCH → regenerate missing files or remove orphan IDs before completing.
17. Cross-Artifact ID Integrity — every story ID in manifest appears in exactly one
    epic file; every EPIC-ID in manifest.story_map has a corresponding epics/epic-NN.md.
    MISMATCH → auto-correct (regenerate missing file or remove orphan entry) and log.
18. Structured Contract — native stories include `contract_format: structured`,
    `prd_source_hash`, `epics_source_hash`, global AC IDs, enriched open_questions,
    and inherited literal/fallback refs when present upstream.
19. Architecture Authority — sourced positive/negative constraints pass; unsourced
    paths, packages, layer assignments, framework choices, storage tools, runtime
    topology, or module placement are flagged.

Auto-correct where possible. Unfixable → open_questions.
STOP-GATE: zero stories → re-execute. Still zero → ABORT.
```
**Execution:** automated

### Step 5: Write Final Outputs

**MVP Scope Filter (MANDATORY before finalizing the canonical backlog):**

Every story written to MANIFEST + epic files MUST trace to (a) at least one FR-ID / AC-ID in PRD-SPEC AND (b) at least one MVP bullet in `project-brief.md` (or its equivalent input). Stories that fail either trace MUST move to `deferred_candidates[]` in AUDIT_FILE instead of the canonical MANIFEST + epic files.

```
mvp_bullets = parse_mvp_section(project_brief_path)
deferred_markers = collect_deferred_markers(
    PREVIOUS_REVIEW_FEEDBACK, [PRD_SPEC, EPICS_MANIFEST])

CANONICAL_STORIES = []
DEFERRED_CANDIDATES = []
DEFERRED_REASONS = {}

FOR EACH story in candidate_stories:
  fr_ac_trace = story.source_refs ∩ {FR-IDs, AC-IDs in PRD_SPEC}
  brief_trace = any(semantic_overlap(story, b) > threshold for b in mvp_bullets)
  IF story.id IN deferred_markers:
    DEFERRED_CANDIDATES.append(story)
    DEFERRED_REASONS[story.id] = "marked deferred upstream: " + deferred_markers[story.id]
  ELIF fr_ac_trace AND brief_trace:
    story.brief_anchor = matching_bullet.id
    CANONICAL_STORIES.append(story)
  ELSE:
    DEFERRED_CANDIDATES.append(story)
    reasons = []
    IF NOT fr_ac_trace: reasons.append("no PRD FR/AC traceability")
    IF NOT brief_trace: reasons.append("no project-brief MVP bullet match")
    DEFERRED_REASONS[story.id] = "; ".join(reasons)

## Only CANONICAL_STORIES flow into MANIFEST.story_map and per-epic files.
## DEFERRED_CANDIDATES are listed in AUDIT_FILE with DEFERRED_REASONS so the
## reviewer can decide whether to re-include or accept the deferral.
```

```
1. Finalize MANIFEST (story_map + dependencies + validations + open_questions
   + deferred_candidates summary count)
   - Only CANONICAL_STORIES appear in story_map and per-epic files.
   - REPAIR mode: overwrite the ORIGINAL STORIES-MANIFEST-{SESSION_ID}.md file in place.
     Do NOT write to a new session-ID filename.
   - Set the manifest front-matter `version:` to NEW_VERSION. On REPAIR this MUST be the
     incremented patch (Step 1: PREVIOUS_VERSION → NEW_VERSION) — editing content in place
     without bumping `version` is a §7 violation. See execution-protocol §7.2 step 8.
1b. Delete CHECKPOINT_FILE (epics/_checkpoint.json) — no longer needed after successful completion.
2. Verify all epic files exist and are non-empty
3. Write AUDIT_FILE = SPEC_FOLDER + 'STORIES-AUDIT-' + SESSION_ID + '.md':
   - Session metadata, sources, per-epic log, validation summary, CHANGE_LOG
   - deferred_candidates[]: list of DEFERRED_CANDIDATES with DEFERRED_REASONS (from MVP Scope Filter)
   - Structured contract validation result, upstream hashes, inherited literal/fallback counts,
     and any architecture-authority violations
   - REPAIR-only: set `mode: REPAIR` and APPEND (do not overwrite) a `## Repair History`
     entry — version, timestamp, directives_applied, sections_changed, sections_preserved,
     repair_delta (per execution-protocol §7.2 step 8). Overwrite the original audit in place;
     do NOT create a parallel STORIES-AUDIT-<NEW_SESSION_ID>.md.
3b. REPAIR self-check (execution-protocol §7.2 step 9): before final_response, confirm the
   manifest `version` is strictly greater than PREVIOUS_VERSION AND the AUDIT has the new
   `## Repair History` entry. If not, fix the bookkeeping now — do not finish.
4. Verify all files


Memory Bank artifact type: `"{N} user-stories"` (e.g., `"48 user-stories"`).

**Memory Bank — MANDATORY session-end writes:**
1. Overwrite `context-pack/active-context.md` with session status, decisions, blockers, key artifacts (see execution-protocol.md Section 4 for schema).
2. Append one milestone row to `context-pack/progress.md` with artifact count above.

**LAST ACTION — MANDATORY:** Update `_progress.json` status to `COMPLETED` with `completed_at` timestamp.
If the session failed, set status to `FAILED` instead.

## Harness Output Sidecar - MANDATORY
When the prompt includes `output_file = '<path>'`, write that exact JSON file as the final file write before final_response:
  { "user_stories_output_path": "<resolved user_stories_output_path>" }
Use the resolved output folder that contains `STORIES-MANIFEST-*.md`, `STORIES-AUDIT-*.md`, and `epics/`. Do not emit final_response until this sidecar exists.

Ready for Implementation (RPI cycles).
```
**Execution:** automated

## Domain Tag Taxonomy
```
[FE] Frontend/Web | [BE] Backend/API | [MOBILE] Mobile
[DATA] Data/Pipelines | [INFRA] DevOps/Cloud | [AI] AI/ML
[DESIGN] UX/UI | [QA] Test Automation
[FS] Full Stack (Trivial Exception ONLY — < 4 hours total)
```

## Layered Decomposition Rules
1. No Hybrid Tags. FORBIDDEN to combine (e.g., [FE/BE]).
2. Auto-Split: Interface + Backend → [ID]-BE + [ID]-FE.
3. Trivial Exception: < 4 hours → single [ID]-FS.
4. Cross-Layer Deps: FE/MOBILE MUST list corresponding BE in dependencies.

## Domain Technical Matrix — Mandatory Scenario Types per Tag

These scenarios are REQUIRED in addition to the ≥4 AC minimum. Their absence is a
validation failure (Check 13), not a suggestion.

| Tag | Required Scenario Type | Examples |
|-----|----------------------|---------|
| [FE] [MOBILE] | API/network error | Timeout, HTTP 500, connection lost |
| [FE] [MOBILE] | Visual state | Loading indicator, empty state, skeleton screen |
| [BE] [DATA] [INFRA] | System failure | DB down, external API timeout, queue full |
| [BE] [DATA] [INFRA] | Security/auth | Invalid token, unauthorized scope, rate limiting |
| [AI] | Model failure | Model unavailable, low-confidence fallback, latency spike |
| [QA] | Coverage boundary | Edge case at input limits, concurrent execution |

**Adversarial generation mindset:** Generate scenarios by asking "what breaks this?"
before "what succeeds?" Happy-path scenarios are necessary but insufficient.

## Common Rationalizations (Anti-Rationalization Table)

| Excuse | Why It Fails | Counter |
|--------|-------------|---------|
| "This story spans FE and BE, a single [FS] tag is simpler" | Hybrid tags are FORBIDDEN (Rule 1). They hide complexity and prevent accurate domain-specific estimation. | Auto-Split: Interface + Backend → [ID]-BE + [ID]-FE. Only use [FS] for trivial < 4 hour work. |
| "4 acceptance criteria per story is excessive for simple stories" | AC Minimum rule (Check 12) exists because under-specified stories produce under-tested implementations. | 4 scenarios is the minimum: happy path + error case + boundary + edge case. Simple stories have simple ACs — they're still 4+. |
| "The epic AC already covers this, I don't need story-level AC" | Epics and stories serve different consumers. The implementing agent reads stories, not epics. | Every story must be self-contained. Copy and refine epic ACs into story-level Given/When/Then format. |
| "I'll let the implementer decide the domain tag" | Domain tags drive technical matrix scenarios. Without tags, the implementer skips domain-specific validation. | Assign tags during decomposition. Cross-Layer Deps rule: FE/MOBILE MUST list corresponding BE in dependencies. |
| "These stories are too granular, I'll merge some" | Merged stories lose traceability to epics and FRs. They also exceed single-sprint sizing. | If stories feel too granular, the epic may be too small. Check epic qualification gates before merging stories. |
| "The happy path covers the main flow, error scenarios are edge cases" | [FE]/[MOBILE] stories without API error scenarios and visual states produce UIs that silently fail. [BE] stories without auth scenarios leave security holes. | Domain Technical Matrix (Check 13) is mandatory. Error/failure scenarios are not optional edge cases — they are first-class requirements. |
| "This is a BE task, it doesn't need a business value statement" | INVEST-V applies to all tags. A story the implementing agent can't justify is a story that may get deprioritized incorrectly. | Every story, including infrastructure BE stories, must articulate why the system/user benefits. "Enables FR-03 by providing the data persistence layer" is sufficient. |
| "I'll track story-to-manifest consistency manually" | Manual tracking breaks silently under REPAIR mode and context compaction. | Check 16 and 17 are automated gates. Manifest counts are the source of truth — mismatches trigger regeneration, not manual review. |

## Red Flags

Signs that user story decomposition is being done superficially:

- All stories have the same domain tag (indicates no real decomposition)
- Stories have fewer than 4 acceptance criteria (violates AC Minimum rule)
- No domain technical matrix scenarios present (Check 13 skipped)
- [FE]/[MOBILE] stories have no error or visual-state scenarios
- [BE]/[DATA]/[INFRA] stories have no failure or auth scenarios
- Cross-layer dependencies not declared (FE stories without BE dependencies)
- Story titles are just epic titles with numbers appended ("Epic-01 Story 1")
- Given/When/Then format not used in acceptance criteria
- Zero stories flagged with open questions on a large epic
- Anti-Fade violation: last epic's stories are noticeably thinner than first epic's
- Stories that contain no user value statement (pure technical tasks disguised as stories)
- INVEST dimension missing: story has no articulated benefit (V), is implementation-prescriptive (N), or has non-binary ACs (T)
- Manifest story count differs from total stories across epic files (Input/Output mismatch)

## Verification Checklist with Evidence

Every item requires **evidence**, not assertion. "Seems right" is never sufficient.

- [ ] Every epic has at least one story — Evidence: manifest story_map covers all epic IDs
- [ ] No hybrid domain tags — Evidence: grep for combined tags (FE/BE, etc.) returns zero
- [ ] AC Minimum met (≥4 per story) — Evidence: count of scenarios per story ≥ 4
- [ ] Domain technical matrix satisfied — Evidence: each tag's required scenario types present (Check 13 table)
- [ ] INVEST compliance — Evidence: each story's I/N/V/E/S/T dimensions explicitly satisfied or flagged
- [ ] No standalone technical tasks — Evidence: zero stories with no user value statement in manifest
- [ ] Cross-layer dependencies declared — Evidence: FE/MOBILE stories reference BE dependencies
- [ ] Given/When/Then format used — Evidence: every AC follows structured format
- [ ] Anti-Fade STOP-GATE passed — Evidence: last epic AC count per story ≥50% of first (proportional)
- [ ] Traceability maintained — Evidence: every story traces to epic ID and FR IDs
- [ ] DoD consistent per domain tag — Evidence: tag-appropriate Definition of Done on every story
- [ ] Global AC IDs used — Evidence: every AC ID is story-scoped and globally unique
- [ ] Inherited literals/fallbacks preserved — Evidence: upstream LIT/OQ IDs appear where applicable
- [ ] Architecture authority respected — Evidence: no unsourced structural mandates; sourced constraints have source_ref
- [ ] Input/Output count logged — Evidence: "Coverage: N epic files / M epics; P stories / Q IDs" in AUDIT
- [ ] Cross-artifact IDs clean — Evidence: zero orphan story IDs or missing epic files reported

## Reference Files
- `references/stories-template.md` — Manifest + per-epic file structures
