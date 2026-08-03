---
name: decomposing-sub-goals
description: >
  Converts an approved PRD + Epics (and an optional story-level backlog via
  user_stories_path) into an ordered SUB_GOAL_DECOMPOSITION —
  sprint-planning chunks where each sub-goal is one independently implementable
  slice of the backlog, sized to be digested by the code-development-autoloop
  scope tripwire (one sub-goal = one autoloop iteration). When a story backlog is
  supplied, one-story-per-subgoal emits true per-story sub-goals instead of
  degrading to per-epic. Produces
  SUB-GOAL-DECOMPOSITION-{SESSION_ID}.json (agent-native, zero prose, schema-validated,
  SESSION_ID-stamped so concurrent instances never collide) — the loop_source_artifact
  that drives a Stepwise loopable capability group. Supports
  BUILD and REPAIR. Use when a playlist iteration group needs its sub-goal list,
  when decomposing epics into sprint chunks, or when preparing PRD/Epics for
  looped code development.
license: Proprietary
metadata:
  author: aipods-team
  version: 1.2.0
  category: delivery
  tags: sprint-planning, decomposition, iteration-groups, sub-goals, backlog
---

# decomposing-sub-goals — Agent-Native Skill

## Quick Start

Convert an approved PRD and its Epics into an ordered list of **sprint-planning
sub-goals**. Primary output is **`SUB-GOAL-DECOMPOSITION-{SESSION_ID}.json`** (structured data)
— not a document. Each `sub_goals[]` entry is a self-contained chunk of the
backlog — **one or more epics grouped together**, or a slice of a single
oversized epic — sized so it fits the `code-development-autoloop` **scope
tripwire** and can be completed in one loop iteration. The array order IS the
iteration order. This is the `loop_source_artifact` for a Stepwise loopable
capability group (SPEC_STEPWISE_ITERATION_GROUPS_CONTRACT).

The chunk-sizing rule is a **parameter** (`chunking_criteria`) — it defaults to
the autoloop scope-triage tripwire (group epics up to the tripwire envelope; keep
each chunk within it) and can later be swapped for other strategies without
changing this skill's contract.

Generation shape: **list-shape** (one discrete structured file). Route:
§2 → §10.5 → §11.

## Output Architecture

```
{output_folder}/
├── SUB-GOAL-DECOMPOSITION-{SESSION_ID}.json       ← Primary artifact (SESSION_ID-stamped — the loop source)
└── SUB-GOAL-DECOMPOSITION-AUDIT-{SESSION_ID}.md   ← Session metadata + provenance (lightweight)
```

**Why the SESSION_ID-stamped JSON filename:** two loop instances can run at the
same time and write into the **same** `{output_folder}`; a fixed
`sub-goal-decomposition.json` would collide. Stamping the SESSION_ID into the
filename (mirroring the AUDIT) makes each instance's loop source unique, so
concurrent runs never overwrite each other. The playlist loop expander does **not**
match this artifact by filename — it resolves the produced `sub_goal_decomposition_path`
output to the **actual path this skill reports via the §11 sidecar** (§11.1.1: report
the path you wrote to, never a re-derived name), so a SESSION_ID-stamped filename is
transparent to every downstream consumer. A re-run of the **same** Stepwise session
reuses that session's id (REPAIR reuses it from the AUDIT filename), so it overwrites
its own JSON in place — never a sibling's.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project_name` | string | Yes | — | Project/account/ticket identifier used for SESSION_ID and audit organization. |
| `prd_path` | string | Yes | — | Path to the approved PRD artifact (the product intent + scope the epics realize). |
| `epics_path` | string | Yes | — | Path to the Epics artifact/folder (the backlog units to chunk into sub-goals). |
| `user_stories_path` | string | No | — | Optional STORY-LEVEL backlog (the user-stories artifact/folder from product-delivery / backlog-story-generation). When present it is the **authoritative** source of user stories, each mapped to its parent epic — enabling true `one-story-per-subgoal`, real-story `quickchange-scope-tripwire` slicing, and real US counts for the autoloop tripwire. When absent, fall back to stories inline in `epics_path` (prior behavior). Never overload `epics_path` with the stories artifact. |
| `architecture_path` | string | No | — | Optional ARCHITECTURE artifact whose bounded contexts define the decomposition boundaries (e.g. a detailed-agent-design `manifest.json` with a `pbcs[]` array, a domain model, or a microservice/module inventory). Required for `one-bounded-context-per-subgoal`, where it is the authoritative chunk source (one sub-goal per bounded context). Ignored by the epic/story strategies. |
| `output_folder` | string | No | `./artifacts/outputs/sprint-planning` | Folder where `SUB-GOAL-DECOMPOSITION-{SESSION_ID}.json` and the audit are written. |
| `chunking_criteria` | string | No | `autoloop-scope-tripwire` | Chunking strategy: `autoloop-scope-tripwire` (greedy grouping up to the code-dev scope-triage envelope, split oversized epics) \| `quickchange-scope-tripwire` (slice down to the quick-change envelope — one small shippable change per sub-goal, routes to quick-change-implementation) \| `one-epic-per-subgoal` (one epic per iteration) \| `one-story-per-subgoal` (one user story per iteration) \| `one-bounded-context-per-subgoal` (one bounded context per iteration, from `architecture_path`). See `references/chunking-rules.md`. |
| `included_unit_types` | string | No | `bounded-context` | `one-bounded-context-per-subgoal` only — comma-separated backlog unit types to emit. Default emits only bounded contexts; add `spike`, `enabler`, and/or `delivery-shell` to also emit those (type-prefixed, dependency-ordered) when they must be tracked as goals. |
| `max_chunk_score` | string | No | `30` | `autoloop-scope-tripwire` only — max scope-complexity SCORE per chunk. Higher ⇒ larger chunks. |
| `max_user_stories_per_chunk` | string | No | `3` | `autoloop-scope-tripwire` only — hard cap on user stories per chunk. |
| `max_bounded_contexts_per_chunk` | string | No | `1` | Tripwire strategies — hard cap on bounded contexts per chunk. |
| `max_acceptance_checks_per_chunk` | string | No | `7` | `quickchange-scope-tripwire` only — quick-change size ceiling; split any behaviour whose acceptance criteria exceed this into shippable slices. |
| `max_sub_goals` | string | No | `20` | Upper bound on sub-goals (hard contract ceiling is 100). Use to cap iteration count. |
| `sub_goal_decomposition_path` | string | Yes (output) | `SUB-GOAL-DECOMPOSITION-{SESSION_ID}.json` | Resolved path to the written decomposition JSON (SESSION_ID-stamped). Populated by the skill and reported via the §11 sidecar — this is what the loop group resolves as its `loop_source_artifact`. |
| `failure_feedback` | string | No | — | Feedback from a rejected decomposition gate. When present, the skill enters REPAIR mode and applies targeted corrections. |

**If any Required parameter is not defined, ABORT EXECUTION.**

## Prerequisites

- [ ] `prd_path` exists and is readable.
- [ ] `epics_path` exists and is readable (file or folder of epic definitions).
- [ ] IF `user_stories_path` is provided: it exists and is readable (file or folder of user stories). If provided but missing/unreadable → do NOT silently ignore: log a blocker and treat as the no-stories fallback with a loud audit note.
- [ ] `output_folder` is writable.

## DECOMPOSITION_INDEX — Carry-Forward Contract

Initialize at Step 1. Update after every phase. This is the SOLE source of truth
between phases. Never carry full source text — only IDs, titles, and status flags.

```
DECOMPOSITION_INDEX = {
  session_id: string,
  mode: BUILD | REPAIR,
  output_folder: string,
  prd_summary: string,                       // one-line intent, sourced from PRD
  epics: [{ id, title, source_ref }],        // parsed epic inventory
  stories_source: "user_stories_path" | "inline_epics" | "none",  // where stories came from
  stories: [{ id, title, epic_id, source_ref }],  // parsed story inventory (empty when stories_source=none)
  sub_goals: [{ index, title, from_epics: [id], from_stories: [id], status }],
  total_sub_goals: number,
  repair_log: [{ directive, target, outcome }],
  blockers: [],
  open_questions: []
}
```

## Workflow

### Step 1: Initialize & Environment Setup

**FIRST ACTION — MANDATORY:** apply execution-protocol.md §2. Write
`{output_folder}/_progress.json` before any other file write:

```json
{ "skill": "decomposing-sub-goals", "session_id": "{SESSION_ID}", "status": "RUNNING",
  "started_at": "<ISO timestamp>", "completed_at": null,
  "total": 0, "completed": 0, "items": [] }
```

**Command:**
```
1. SESSION_ID = [Extract from EXECUTION METADATA] (execution-protocol.md §1).
   Do NOT generate a SESSION_ID locally. It goes in the AUDIT filename AND the
   JSON filename (both SESSION_ID-stamped so concurrent instances never collide),
   never in the folder name.

2. REPAIR detection (Pattern 3):
   IF failure_feedback is non-empty:
     MODE = REPAIR
     FOLDER = output_folder (must already exist — never mkdir for REPAIR)
     SESSION_ID = extract from the existing SUB-GOAL-DECOMPOSITION-AUDIT-*.md filename
     PRIOR_FILE = {FOLDER}/SUB-GOAL-DECOMPOSITION-{SESSION_ID}.json (the JSON for THIS
       session — match it by the reused SESSION_ID, never merely "the newest JSON",
       since a shared folder may hold a sibling instance's decomposition)
     IF PRIOR_FILE not found → write Gap Report to AUDIT → EXIT
     LOAD PRIOR_FILE → PREVIOUS_DECOMPOSITION
     PARSE failure_feedback → REPAIR_DIRECTIVES [{ target, instruction, reason }]
   ELSE:
     MODE = BUILD
     CREATE output_folder (mkdir -p — idempotent)

3. Initialize DECOMPOSITION_INDEX with session_id, mode, output_folder.

4. Zero Invention Policy: every sub-goal must trace to PRD/Epics evidence. A
   backlog unit with no source basis is NOT invented — it is dropped and its
   absence noted in open_questions.

5. STOP-GATE — abort if:
   - project_name is empty
   - prd_path does not exist
   - epics_path does not exist
   - output_folder is not writable
   LOG: "Step 1 COMPLETE. Session: {SESSION_ID}, Mode: {MODE}."
```

### Step 2: Load PRD + Epics (+ optional User Stories)

**Command:**
```
LOAD prd_path → extract the product intent, scope boundaries, and any explicit
  sequencing/priority signals. Record a one-line prd_summary in the INDEX.
LOAD epics_path → parse the epic inventory. For each epic capture { id, title,
  source_ref } into DECOMPOSITION_INDEX.epics.

RESOLVE the story-level backlog (sets DECOMPOSITION_INDEX.stories_source + stories):
  IF user_stories_path is provided AND readable:
    stories_source = "user_stories_path"  (AUTHORITATIVE)
    LOAD user_stories_path → parse each user story into
      DECOMPOSITION_INDEX.stories as { id, title, epic_id, source_ref }.
      Map each story to its parent epic by the story's epic reference
      (e.g. epic_id / parent_epic / a US-<epic>-<n> id convention). A story
      whose parent epic is not in DECOMPOSITION_INDEX.epics is kept with
      epic_id=null and noted in open_questions (do NOT drop silently, do NOT
      invent an epic).
    LOG: "Loaded {N} user stories from user_stories_path across {M} epics."
  ELSE IF epics_path already contains inline user stories (product-delivery
       story-level backlog passed as epics_path — legacy path):
    stories_source = "inline_epics"
    Parse those inline stories into DECOMPOSITION_INDEX.stories the same way.
  ELSE:
    stories_source = "none"   (epic-level backlog only — no user stories)

  Precedence is fixed: user_stories_path WINS over inline epic stories when both
  exist (the explicit backlog is authoritative). Never merge or invent stories.

RESOLVE the bounded-context inventory (only needed for
`one-bounded-context-per-subgoal`; harmless otherwise):
  IF architecture_path is provided AND readable:
    LOAD architecture_path → parse the bounded-context / PBC inventory into
      DECOMPOSITION_INDEX.bounded_contexts as
      { id, name, source_ref, from_epics? }. A manifest that lists PBCs (e.g.
      detailed-agent-design manifest.json with a `pbcs[]` array) is the canonical
      shape; each PBC is one bounded context. Where the artifact links a PBC to its
      agents/epics, capture that for traceability.
    LOG: "Loaded {K} bounded contexts from architecture_path."
  ELSE:
    DECOMPOSITION_INDEX.bounded_contexts = []   (none available)

IF the epics artifact is empty or contains no parseable epic:
  WRITE an empty decomposition (sub_goals: []) per Step 4, note the gap in
  open_questions, and proceed to the sidecar. An empty loop source is a VALID
  contract outcome (0 iterations), not a failure.

Read references/chunking-rules.md before Step 3.
```

### Step 3: Chunk Epics into Sub-Goals

Read `references/chunking-rules.md` before executing this step.

**Command:**
```
IF MODE == REPAIR AND no REPAIR_DIRECTIVE targets the sub_goal set:
  PRESERVE PREVIOUS_DECOMPOSITION verbatim. SKIP to Step 4.

SELECT the strategy from `chunking_criteria` (default `autoloop-scope-tripwire`).
Full rules per strategy live in references/chunking-rules.md; the summary:

  CASE `one-epic-per-subgoal`:
    Emit exactly one sub-goal per epic, in execution order. No grouping, no
    splitting. (Thresholds are ignored.)

  CASE `one-story-per-subgoal`:
    Emit one sub-goal per user story across all epics, in execution order. Finest
    granularity. (Thresholds are ignored.)
    REQUIRES a STORY-LEVEL backlog. Source the stories from
    DECOMPOSITION_INDEX.stories (resolved in Step 2 — from `user_stories_path`
    when supplied, else inline epic stories).
    IF DECOMPOSITION_INDEX.stories is NON-EMPTY (stories_source != "none"):
      Emit one sub-goal per story: title = the story; from_stories = [story.id];
      from_epics = [story.epic_id] (its parent epic); requirements = the story's
      acceptance criteria. NO degradation — this is the intended path.
    ELSE (stories_source == "none" — epic-level backlog, no user_stories_path):
      DEGRADE to one sub-goal per epic (the epic is the finest available unit) and
      set DECOMPOSITION_INDEX.degraded = { requested: "one-story-per-subgoal",
      produced: "one-epic-per-subgoal", reason: "backlog is epic-level; no user
      stories present and no user_stories_path supplied" }. This drives the audit's
      `## ⚠️ Strategy Degraded` section and a top-level open_question — do NOT hide
      it in a footnote, and do NOT invent stories to hit the requested granularity.
      The remedy in that open_question is: "supply user_stories_path with a
      story-level backlog (product-delivery output) and re-run."

  CASE `one-bounded-context-per-subgoal`:
    Emit one sub-goal per bounded context (PBC), in dependency/execution order.
    Source the contexts from DECOMPOSITION_INDEX.bounded_contexts (resolved in
    Step 2 from `architecture_path`). Thresholds are ignored.
    IF DECOMPOSITION_INDEX.bounded_contexts is NON-EMPTY:
      Emit one sub-goal per bounded context: title = the context name; description
      = its responsibility/scope from the artifact; requirements = the concrete
      contracts/agents/tools the context owns (drawn from the artifact, never
      invented); from_epics = the epics traceably linked to that context when the
      artifact provides the mapping, else []. This is the intended path — it aligns
      the loop to the solution architecture the build capabilities implement.
      Cross-cutting bounded contexts (e.g. security, auditability) ARE contexts and
      ARE emitted.
      Non-context backlog units (infrastructure enablers, research spikes, delivery
      shells) are governed by `included_unit_types` (default `bounded-context`):
        - If a unit's type is NOT in `included_unit_types`: do NOT emit it as a
          sub-goal; record it in open_questions so the omission is explicit.
        - If a unit's type IS in `included_unit_types` (e.g. the operator added
          `spike` because a research spike must run and validate before the contexts
          that depend on it): emit it as a sub-goal titled with its type prefix
          (`[SPIKE] ...`, `[ENABLER] ...`, `[SHELL] ...`), description/requirements
          from the source (never invented), ordered by dependency — prerequisites
          (spikes/enablers) BEFORE the contexts that consume them. The type prefix is
          what lets a downstream type-aware step or gate route it to the right lane
          instead of blind per-context agent build. Still respect the max_sub_goals /
          20-item ceiling; overflow → open_questions.
    ELSE (no architecture_path / empty inventory):
      DEGRADE to one sub-goal per epic and set DECOMPOSITION_INDEX.degraded =
      { requested: "one-bounded-context-per-subgoal", produced:
      "one-epic-per-subgoal", reason: "no architecture_path supplied or it carries
      no bounded-context inventory" }. Surface it in the `## ⚠️ Strategy Degraded`
      audit section and a top-level open_question with remedy: "supply
      architecture_path pointing at an architecture artifact whose bounded contexts
      are enumerated (e.g. a detailed-agent-design manifest) and re-run." Do NOT
      invent contexts.

  CASE `autoloop-scope-tripwire` (default):
    GREEDY GROUPING under the tripwire — a sub-goal may span MORE THAN ONE epic.
    When DECOMPOSITION_INDEX.stories is non-empty, US (user-story count) for the
    SCORE and the US cap is the count of real stories mapped to the chunk's epics;
    otherwise use the epics' inline story estimate as before.
    - Walk the epics in execution order and accumulate them into the current chunk
      while it stays WITHIN the envelope: SCORE ≤ {max_chunk_score} AND
      NOT (US > {max_user_stories_per_chunk} AND BC > {max_bounded_contexts_per_chunk}).
      Adding an epic that would breach the envelope starts a NEW chunk.
    - SPLIT a single epic that ALONE breaches the envelope into ordered slices,
      each an independently implementable sub-goal (chunking-rules.md sizing gate).

  CASE `quickchange-scope-tripwire`:
    SLICE DOWN to the quick-change envelope — the opposite of autoloop; NEVER group.
    Each sub-goal = ONE small, independently-shippable behaviour change so it routes
    to quick-change-implementation. For each epic, take its user stories — from
    DECOMPOSITION_INDEX.stories when present (real story-level backlog), else the
    shippable behaviour changes derivable from its acceptance criteria (do NOT
    invent) — and for each unit:
    - IF quick-change-sized — ONE behaviour, acceptance criteria ≤
      {max_acceptance_checks_per_chunk} checks, single bounded context
      (≤ {max_bounded_contexts_per_chunk}), NO schema/arch/data-model/cross-service
      or auth/security work — EMIT it as one sub-goal.
    - ELSE IF it splits into independently-shippable slices that are each
      quick-change-sized — EMIT each slice, in order.
    - ELSE (inherently heavy: schema/auth/arch/multi-context) — EMIT the smallest
      independently-shippable sub-goal; do NOT fragment below shippability. It will
      route to the heavy lane (product-delivery → code-dev) at run time — that is
      correct, not a failure. This strategy maximises quick-lane coverage, it does
      not guarantee it. (chunking-rules.md `quickchange-scope-tripwire`.)

Rules common to every strategy:
  - Each resulting sub-goal is the unit a single loop iteration can complete
    end-to-end without waiting on a sibling sub-goal.
  - ORDER the array by execution order: dependencies first, then PRD priority.
    Keep grouped epics/stories contiguous. The array index IS the iteration index.
  - CAP the list at min(max_sub_goals, 100). If more chunks exist, keep the
    highest-priority 100 in order and register the remainder in open_questions
    (do NOT silently drop — log the deferred chunks and their epics/stories).

FOR EACH sub-goal (in order):
  title        = imperative, <=255 chars, unique, traceable to its epic(s).
  description  = <=4000 chars: what this chunk delivers + which epic(s) it groups
                 (cite every epic id in the chunk). Optional but strongly preferred.
  requirements = <=8000 chars: acceptance criteria / constraints the autoloop
                 must satisfy for the whole chunk. Optional.
  from_epics   = the list of epic ids grouped into this chunk (INDEX only).
  from_stories = the list of user-story ids in this chunk when a story-level
                 backlog was resolved, else [] (INDEX only).
  status: complete (fully sourced) | pending (a field is missing from source).
  Do NOT stop. Process ALL sub-goals, then continue to Step 4.

UPDATE DECOMPOSITION_INDEX.sub_goals and total_sub_goals.
```

### Step 4: Write & Validate the Decomposition JSON

**CO-WRITE INVARIANT (never violate):** the JSON and its audit are ONE unit. Any
change to `sub_goals` — a fresh BUILD, a REPAIR, or a targeted add/remove/reorder/
rename of a single sub-goal — MUST re-enter this step and REGENERATE the audit in
full from the final `sub_goals`. Never write or edit the decomposition JSON in
isolation and never patch the audit incrementally; the audit is always a complete
re-render of the current `sub_goals`. The consistency gate in Step 5 is the backstop
that catches any drift.

**Command:**
```
BUILD the JSON object conforming to the Output Contract schema below.
FIDELITY CHECK before writing:
  - Every sub_goal.title is non-empty and unique.
  - Every from_epics id exists in DECOMPOSITION_INDEX.epics (no invented ids).
  - sub_goals length <= min(max_sub_goals, 100).
  - No field exceeds its max length (title 255 / description 4000 / requirements 8000).
  - stated count in the audit == actual len(sub_goals).

WRITE {output_folder}/SUB-GOAL-DECOMPOSITION-{SESSION_ID}.json — MANDATORY TOOL CALL.
  Use Write (full-file). Apply §10.5.1: if any sub-goal field contains a
  codepoint > 127, this is already a full-file Write so no fallback change is
  needed.
VERIFY the file parses as JSON and satisfies the schema (re-read from disk).

WRITE {output_folder}/SUB-GOAL-DECOMPOSITION-AUDIT-{SESSION_ID}.md — MANDATORY
  TOOL CALL, co-equal with the JSON (NOT optional). The run is INCOMPLETE until
  BOTH files exist on disk. Contents:
  - `## Provenance`: resolved prd_path + epics_path AND the actual source files
    read (e.g. the EPICS-SPEC path when the given epics_path was empty/missing —
    always report what you actually read, not just the input params).
  - `## ⚠️ Strategy Degraded` (ONLY when the requested chunking_criteria could not
    be applied at the requested granularity — see Step 3): state the requested
    strategy, what was produced instead, and why (e.g. "one-story-per-subgoal
    requested but the backlog is epic-level; produced one sub-goal per epic").
    Put this section FIRST so it is impossible to miss.
  - `## Chunking Strategy`: the strategy + (tripwire) per-chunk scores.
  - `## Mapping`: epic/story → sub_goal table.
  - `## Open Questions`: deferred chunks, un-sliceable epics, degradation notes.
  - (REPAIR) a `## Repair History` entry + version bump.
VERIFY the audit file exists on disk (re-read it).
FLUSH source text from memory. Retain only DECOMPOSITION_INDEX.
LOG: "Step 4 COMPLETE. {N} sub-goals + audit written."
```

### Step 5: Emit Harness Outputs Sidecar

> **Emit harness outputs sidecar — apply execution-protocol.md §11.** Mandatory
> under Stepwise (a `## Run metadata` block is present); skip when standalone.

**Output parameters this skill produces:**
- `sub_goal_decomposition_path` — the absolute on-disk path to the written
  `SUB-GOAL-DECOMPOSITION-{SESSION_ID}.json` (§11.1.1: report the actual
  SESSION_ID-stamped path you wrote to, after verifying the file exists there —
  never a re-derived input path and never the un-stamped `sub-goal-decomposition.json`).
  This reported path is how the loop group resolves its `loop_source_artifact`; a
  wrong or un-stamped path here breaks the loop expander for concurrent instances.

**Both-files CONSISTENCY gate (mandatory, before the sidecar):** VERIFY that BOTH
`{output_folder}/SUB-GOAL-DECOMPOSITION-{SESSION_ID}.json` AND
`{output_folder}/SUB-GOAL-DECOMPOSITION-AUDIT-{SESSION_ID}.md` exist on disk **AND
describe the SAME decomposition.** Re-read both and check the audit against the JSON
just written:
  - audit `sub_goal_count` == `len(sub_goals)`;
  - the `## Mapping` table has exactly one row per sub-goal, in the same order;
  - each mapping row's title/type matches the corresponding `sub_goals[i]`.
If the audit is missing **OR STALE** (ANY mismatch — a sub-goal was added, removed,
reordered, or renamed after the audit was last written), **REGENERATE the audit IN
FULL** from the current `sub_goals` (Step 4 contents) — never patch it incrementally,
and never let an existing-but-stale audit pass this gate. When regenerating because
of a detected drift (not a fresh BUILD), add/extend the `## Repair History` note and
bump the audit `version`. Never emit the sidecar / `final_response` while the two
files disagree — they are co-equal outputs and MUST always describe the same
decomposition.

**Strict ordering (§11.4):** JSON written → audit written → **both-files gate** →
`_progress.json` flipped to COMPLETED (LAST ACTION) → **sidecar write (this step)**
→ `final_response`. No tool calls after the sidecar write.

## Output Contract

`SUB-GOAL-DECOMPOSITION-{SESSION_ID}.json` MUST conform to this schema (contract §5.1). This is
a **hard output obligation** — the file is the loop source; a malformed or missing
file fails the whole iteration group.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "SUB_GOAL_DECOMPOSITION",
  "type": "object",
  "required": ["sub_goals"],
  "additionalProperties": false,
  "properties": {
    "sub_goals": {
      "type": "array",
      "minItems": 0,
      "maxItems": 100,
      "items": {
        "type": "object",
        "required": ["title"],
        "additionalProperties": false,
        "properties": {
          "title":        { "type": "string", "minLength": 1, "maxLength": 255 },
          "description":  { "type": "string", "maxLength": 4000 },
          "requirements": { "type": "string", "maxLength": 8000 }
        }
      }
    }
  }
}
```

Example (2 sub-goals — order = iteration order):

```json
{
  "sub_goals": [
    { "title": "Auth service", "description": "Covers EPIC-001. User signup, login, session issuance.", "requirements": "OAuth2 + email/password; sessions expire in 24h; rate-limit login." },
    { "title": "Payment gateway", "description": "Covers EPIC-002. Checkout + provider integration.", "requirements": "Idempotent charge; webhook reconciliation; PCI-safe token handling." }
  ]
}
```

**Status Protocol:** every sub-goal in the INDEX carries `complete` (all fields
sourced) or `pending` (a field missing from source → registered in
open_questions). Never `assumption` — a sub-goal without a real backlog basis is
dropped, not invented.

## Reference Files

- `references/chunking-rules.md` — Epic→sub-goal sizing gate, ordering, splitting/merging, and autoloop-tripwire alignment.
- `references/output-contract.md` — Field-by-field JSON contract, validation, and REPAIR behavior.
