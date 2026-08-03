# decomposing-sub-goals — Chunking Rules (Epic → Sub-Goal)

## Context Contract

- **Inputs:** `DECOMPOSITION_INDEX.epics[]` (parsed epic inventory), the PRD
  summary, and the `chunking_criteria` parameter (default
  `autoloop-scope-tripwire`).
- **Outputs:** the ordered `DECOMPOSITION_INDEX.sub_goals[]` set (consumed by
  Step 4, which writes `SUB-GOAL-DECOMPOSITION-{SESSION_ID}.json`). This file writes
  nothing itself — it is the sizing logic for Step 3.
- **Carries Forward:** `sub_goals[].from_epics`, `total_sub_goals`.
- **Flush After:** raw epic bodies once each chunk's fields are written.
- **Dependency:** Step 2 (Load PRD + Epics) COMPLETE.
- **H1 Title:** `# {project_name} -- Sub-Goal Chunking`

## Mode-Specific Behavior

- **BUILD:** Group the full epic inventory into chunks per the criteria below.
- **REPAIR:** If a `REPAIR_DIRECTIVE` targets chunking (e.g. "chunk 3 is too
  large", "merge chunks 2 and 3"), re-chunk ONLY the affected span and preserve
  every untargeted sub-goal verbatim (same title, same order). Rewrite
  the same session's `SUB-GOAL-DECOMPOSITION-{SESSION_ID}.json` in place. If no directive targets chunking,
  preserve the previous decomposition unchanged.

## Why a chunk may span multiple epics

A `code-development-autoloop` iteration is bounded by the same **scope-triage
tripwire** the `researching-code-design` skill enforces before it authors. Small
epics individually waste an iteration; a single large epic can blow the
iteration budget. So the chunk — not the epic — is the iteration unit: group
small related epics together up to the tripwire ceiling, and split an oversized
epic below it. One sub-goal = one chunk = one autoloop iteration.

## Strategies (`chunking_criteria`)

| Value | Behaviour | Thresholds used |
|-------|-----------|-----------------|
| `autoloop-scope-tripwire` (default) | Greedy-group epics up to the code-dev scope-triage envelope; split any epic that alone exceeds it. Chunks may span multiple epics. | `max_chunk_score`, `max_user_stories_per_chunk`, `max_bounded_contexts_per_chunk` |
| `quickchange-scope-tripwire` | The opposite of autoloop: **slice DOWN** to the much smaller quick-change envelope so each sub-goal is one small, independently-shippable behaviour change that routes to `quick-change-implementation`. NEVER groups; splits aggressively. Work that cannot be quick-change-sized is emitted as its smallest shippable sub-goal (routes to the heavy lane at run time). | `max_acceptance_checks_per_chunk`, `max_bounded_contexts_per_chunk` |
| `one-epic-per-subgoal` | Exactly one epic per sub-goal, in execution order. No grouping, no splitting. | none |
| `one-story-per-subgoal` | One user story per sub-goal (finest granularity), in execution order. | none |
| `one-bounded-context-per-subgoal` | One sub-goal per bounded context (PBC) from the `architecture_path` artifact. Aligns the loop to the solution architecture the build capabilities implement. Optionally also emits spikes/enablers/shells via `included_unit_types`. | `architecture_path` (required), `included_unit_types` (optional) |

All strategies still: yield independently-implementable sub-goals, order by
dependency then PRD priority, and respect `min(max_sub_goals, 20)` (log overflow
to `open_questions`). Pick with the `chunking_criteria` parameter; the tripwire is
the default. The two simple strategies below are self-explanatory — the rest of
this file details the tripwire.

## `autoloop-scope-tripwire`

This mirrors `researching-code-design` Step 1.5 (Scope Triage Gate). Compute the
score for a **candidate chunk** (the epics currently accumulated) from cheap
signals only — counts, not LLM reasoning:

```
US_COUNT   = user stories across the chunk's epics
BC_COUNT   = distinct bounded contexts the chunk touches
ADR_COUNT  = ADRs the chunk depends on (0 if none)
OPEN_Q     = count of "[TBD]" / "[?]" / "[to be identified]" tokens in the chunk
EPIC_HEAVY = 1 if any single epic in the chunk > 800 lines OR > 25 KB, else 0

SCORE = (US_COUNT*3) + (BC_COUNT*5) + (ADR_COUNT*1) + (OPEN_Q*2) + (EPIC_HEAVY*10)
```

**Envelope (a chunk is admissible when BOTH hold) — thresholds are tunable params:**

| Rule | Admissible chunk |
|------|------------------|
| Score gate | `SCORE <= {max_chunk_score}` (default 30). Aim for `<= half` of it (SAFE); the upper half is BORDERLINE — allowed but note `scope_warning` in the audit. |
| Hard rule | NOT (`US_COUNT > {max_user_stories_per_chunk}` AND `BC_COUNT > {max_bounded_contexts_per_chunk}`) (defaults 3 and 1) |

Coerce the three threshold params to integers, falling back to the defaults
(30 / 3 / 1) when unset. Raising `max_chunk_score` (and/or the caps) yields larger
chunks and fewer iterations; lowering them yields smaller chunks and more.

**Greedy grouping algorithm:**

```
current = []            # epics in the chunk being built
FOR EACH epic in execution order:
  candidate = current + [epic]
  IF admissible(candidate):        # both envelope rules pass
    current = candidate            # keep accumulating
  ELSE:
    IF current is empty:           # this single epic alone breaches the envelope
      EMIT split_epic(epic)        # see "Splitting one oversized epic" below
    ELSE:
      EMIT sub_goal(current)       # close the chunk
      current = [epic]             # start a new chunk with this epic
IF current not empty: EMIT sub_goal(current)
```

`admissible(candidate)` = `SCORE(candidate) <= {max_chunk_score} AND NOT (US > {max_user_stories_per_chunk} AND BC > {max_bounded_contexts_per_chunk})`.

## `quickchange-scope-tripwire`

The mirror image of the autoloop tripwire: instead of grouping epics UP to the
code-dev envelope, **slice everything DOWN** to the quick-change envelope so each
sub-goal is the smallest independently-shippable, user-visible behaviour change.
Sized this way, `quick-story-definition` fires none of its S1–S5 readiness
tripwires and routes the sub-goal to `quick-change-implementation` (the quick lane)
rather than product-delivery → code-development-autoloop (the heavy lane).

**The quick-change envelope (a sub-goal is quick-change-sized when ALL hold).**
This mirrors `defining-quick-story`'s `READY_FOR_QUICK_CHANGE` bar — judge it from
cheap signals, not deep reasoning:

| Rule | Quick-change-sized sub-goal |
|------|-----------------------------|
| One behaviour | Exactly ONE user-visible behaviour change (one story's worth), independently shippable and valuable on its own. |
| Acceptance size | Acceptance criteria fit in `<= {max_acceptance_checks_per_chunk}` checks (default 7; the READY_FOR_QUICK_CHANGE bar is 3–7). |
| Single context | Touches a single bounded context (`BC == {max_bounded_contexts_per_chunk}`, default 1). |
| No heavy work | No architecture / schema / data-model / cross-service change, and no auth / session / security-sensitive behaviour. Such work can't be quick-change-sized. |

**Slicing algorithm (never group; split aggressively):**

```
FOR EACH epic in execution order:
  units = the epic's user stories from DECOMPOSITION_INDEX.stories when a
          story-level backlog was resolved (via user_stories_path, else inline
          epic stories), else the independently-shippable behaviour changes
          derivable from the epic's acceptance criteria (do NOT invent behaviours)
  FOR EACH unit in dependency-then-priority order:
    IF unit is quick-change-sized (all four rules pass):
      EMIT sub_goal(unit)                       # one atomic change → quick lane
    ELSE IF unit splits into independently-shippable sub-slices,
            each quick-change-sized:
      EMIT sub_goal(slice) for each slice, in order
    ELSE:
      # inherently heavy (schema/auth/arch/multi-context) — the "emit smallest
      # slice, let routing decide" rule: do NOT fragment below shippability.
      EMIT sub_goal(smallest independently-shippable unit)
      # quick-story-definition will fire a tripwire → it routes to the heavy lane
```

**Never group.** Unlike the autoloop tripwire, two units are never combined into one
sub-goal — the whole point is maximal granularity toward the quick lane.

**Honesty rules.**
- Do NOT force work below independent shippability just to fit the envelope — a
  fragment that only makes sense once a sibling lands is worse than a slightly
  larger, coherent sub-goal.
- Do NOT invent acceptance criteria or behaviours to manufacture small stories; slice
  only what the source supports. A missing fact is a non-blocking assumption or an
  `open_questions` entry, never an invented requirement.
- This strategy does not GUARANTEE every sub-goal reaches the quick lane — it
  maximises how many do. Genuinely heavy sub-goals route to the heavy lane at run
  time, and that is correct.

`{max_acceptance_checks_per_chunk}` and `{max_bounded_contexts_per_chunk}` coerce to
integers, falling back to 7 and 1. Lowering the acceptance ceiling yields smaller,
more numerous quick-change sub-goals (watch the 20-item cap — log overflow to
`open_questions`).

## Splitting one oversized epic

When a single epic alone breaches the envelope (typically `US_COUNT > 3 AND
BC_COUNT > 1`, or `EPIC_HEAVY` pushing `SCORE > 30`), split it into ordered
slices, each an independently shippable sub-goal:

1. Prefer splitting along **bounded-context** lines (one context per slice → drives
   `BC_COUNT` to 1 per slice).
2. Then split by **user-story cluster** so each slice holds `<= 3` stories.
3. Each slice must be independently implementable — no slice depends on a later
   slice. If a clean independent split is impossible, keep the epic whole, mark
   the sub-goal `status: pending`, and register the risk in `open_questions`
   ("epic {id} exceeds the tripwire and could not be cleanly sliced").

## Ordering

- Dependencies first: if chunk B needs an artifact chunk A produces, A precedes B.
- Then PRD priority.
- Grouped epics stay contiguous within their chunk; chunks never interleave.
- The final array index IS the loop iteration index — order is load-bearing.

## `one-epic-per-subgoal`

Emit exactly one sub-goal per epic, in execution order — no grouping, no
splitting. `from_epics` is a single id per sub-goal. Threshold params are ignored.
Use when epics are already right-sized for one iteration and you want a 1:1 map.
Still capped at `min(max_sub_goals, 20)`; overflow epics go to `open_questions`.

## `one-story-per-subgoal`

Emit one sub-goal per user story across all epics, in execution order (finest
granularity). Each sub-goal's `title` is the story; `from_epics` carries the
parent epic id; `requirements` the story's acceptance criteria. Threshold params
are ignored. Use for tight per-story loops. This granularity hits the 20-item
ceiling fast — when there are more than 20 stories, keep the highest-priority 20
in order and log the rest to `open_questions` (they are NOT silently dropped).

**Input requirement — this strategy needs a STORY-LEVEL backlog.** User stories
are produced by `product-delivery` (backlog-story-generation), NOT by
`product-definition`. A product-definition **EPICS-SPEC** is epic-level only
(epics + FR/NFR/JTBD mapping); it contains no user stories. Supply the story
backlog the proper way: pass **`user_stories_path`** pointing at the user-stories
artifact/folder. Stories resolved in Step 2 (`DECOMPOSITION_INDEX.stories`) are
the units — one sub-goal per story, `from_stories`/`from_epics` set. Do NOT
overload `epics_path` with the stories artifact; `user_stories_path` is the
dedicated channel (inline stories inside `epics_path` still work as a legacy
fallback when `user_stories_path` is absent).

**Degradation (mandatory, loud) — only when NO story backlog is available.** If
`user_stories_path` is absent AND the epics source carries no inline stories
(`stories_source == "none"`), you cannot produce story-level sub-goals — do NOT
invent stories. Produce one sub-goal per epic (the finest available unit) and
make the mismatch impossible to miss:

- Add a `## ⚠️ Strategy Degraded` section at the TOP of the audit: requested
  `one-story-per-subgoal`, produced `one-epic-per-subgoal`, reason "backlog is
  epic-level; no user stories present and no user_stories_path supplied. Run
  product-delivery to get stories, then re-run supplying user_stories_path."
- Add a top-level `open_questions` entry with the same message.

When a story backlog IS resolved there is NO degradation — every story becomes a
sub-goal. This is the only strategy that can silently under-deliver granularity;
the loud degradation is what keeps the operator informed (see the demo-energy run
where an EPICS-SPEC was passed and 6 epics became 6 sub-goals).

## `one-bounded-context-per-subgoal`

Emit one sub-goal per bounded context (PBC) enumerated in the `architecture_path`
architecture artifact (resolved in Step 2 into
`DECOMPOSITION_INDEX.bounded_contexts`). `title` is the context name, `description`
its responsibility, `requirements` the contracts/agents/tools it owns (from the
artifact — never invented), `from_epics` the epics linked to it when the artifact
maps them. Threshold params are ignored; still capped at `min(max_sub_goals, 20)`
with overflow logged to `open_questions`.

Use when the loop's downstream build capabilities implement **per bounded context**
(e.g. an agent graph + its tools + its UX per PBC) and you want the decomposition
axis to match the architecture instead of the epic/process backlog. This avoids the
axis mismatch where a process/epic decomposition forces heterogeneous work
(enablers, research spikes, delivery shells) through an agent-build loop that only
makes sense for real bounded contexts.

**Input requirement — needs a bounded-context inventory.** Supply
`architecture_path` pointing at an artifact that enumerates the contexts (canonical
shape: a detailed-agent-design `manifest.json` with a `pbcs[]` array). Cross-cutting
contexts (security, auditability) are still contexts and ARE emitted. Backlog units
that are NOT bounded contexts — infrastructure enablers, spikes, web/iOS/Android
delivery shells — are excluded **by default** and logged to `open_questions` so the
exclusion is explicit.

To include them **when needed**, set `included_unit_types` (default
`bounded-context`) to add `spike`, `enabler`, and/or `delivery-shell`. Included
units are emitted as sub-goals titled with a type prefix (`[SPIKE]` / `[ENABLER]` /
`[SHELL]`), ordered by dependency (prerequisites first — a spike that must validate
before its dependent contexts comes before them). The prefix is a routing signal:
these units are NOT per-context agent-build work, so a downstream type-aware step or
gate should send them to the right lane (a one-time pre-loop phase, a research
capability, etc.) rather than through blind per-context agent build.

**Degradation (mandatory, loud) — when no inventory is available.** If
`architecture_path` is absent or carries no parseable bounded contexts, do NOT
invent contexts. Produce one sub-goal per epic and surface the mismatch: a
`## ⚠️ Strategy Degraded` audit section (requested
`one-bounded-context-per-subgoal`, produced `one-epic-per-subgoal`) plus a
top-level `open_questions` entry with remedy "supply architecture_path pointing at
an architecture artifact whose bounded contexts are enumerated and re-run."

## Adding another strategy

`chunking_criteria` is an enum on the capability. To add a value: document its
rule here, add it to the capability's `values:` list, and branch on it in SKILL.md
Step 3. Any strategy MUST yield independently-implementable sub-goals and respect
`max_sub_goals` and the 20-item ceiling.

## Source Fidelity Check (before Step 4 writes)

- [ ] Every `from_epics` id exists in `DECOMPOSITION_INDEX.epics` — no invented ids.
- [ ] Every epic in the inventory appears in exactly one chunk (or is an explicit,
      logged deferral in `open_questions` when the 20-cap is hit).
- [ ] No chunk breaches the envelope (or, if BORDERLINE, the audit records
      `scope_warning: true` for that chunk).
- [ ] Chunk order respects declared dependencies, then PRD priority.
- [ ] `total_sub_goals == len(sub_goals)` and `<= min(max_sub_goals, 20)`.

## Post-Section Protocol

1. Update `DECOMPOSITION_INDEX.sub_goals` and `total_sub_goals` — do NOT write a
   file here; Step 4 owns the JSON write.
2. Record the per-chunk score + epic grouping in the audit's mapping table.
3. Flush raw epic bodies once each chunk's fields are captured in the INDEX.
4. Log: "Chunking complete. {N} sub-goals from {M} epics (criteria: {chunking_criteria})."
