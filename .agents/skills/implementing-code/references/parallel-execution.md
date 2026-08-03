# implementing-code — Parallel Scope Fan-Out (opt-in)

This contract governs `Step 0: Fan-Out Coordinator Mode`. It is **inert unless the
caller passes `parallel_scopes`** — every existing invocation is unaffected.

## Purpose & non-goals

Speed up implementation when the work splits into **genuinely independent units**
by running them concurrently. The mechanism is **domain-agnostic**: it knows nothing
about agents, microservices, or components — the caller partitions the work into
`parallel_scopes`, and this skill only ever parallelizes **disjoint source subtrees
with their own plans**.

**Non-goals (never do these):**
- NEVER parallelize files *within* a single plan/scope. Files in one scope import
  and depend on each other; concurrent writers corrupt them. Within a scope,
  execution stays strictly sequential (the normal Step 1→5).
- NEVER let two scopes write the same file, directory, package manifest, lockfile,
  git index, or root README/AGENTS.md at the same time.
- NEVER hardcode a domain unit (e.g. "one agent per scope"). That partition is the
  caller's decision, expressed in `parallel_scopes`.

## `parallel_scopes` shape

```
parallel_scopes: [
  { "id": "<unique>",
    "plan_folder_path": "<own PLAN-SPEC folder>",
    "source_path": "<own NON-OVERLAPPING subtree>",
    "progress_folder_path": "<own progress folder>"   // optional; derived per scope if absent
  },
  ...
]
```

Shared read-only inputs (research, design specs, test cases, context pack) are
passed through to every scope unchanged.

## Safety gate (run BEFORE any parallel work)

All conditions must hold. If ANY fails, **abort fan-out and run the scopes
sequentially** (ordinary single-scope execution, one after another), logging
`FANOUT_DEGRADED_SEQUENTIAL` with the offending pair. Degrading is always correct;
it just forgoes the speed-up.

1. **Pairwise-disjoint subtrees.** For every pair `(a, b)`, `a.source_path` must not
   equal, contain, or be contained by `b.source_path`. Normalize (resolve `.`/`..`,
   trailing slash) before comparing. Nested or equal paths ⇒ FAIL.
2. **No shared mutable root written in parallel.** If the scopes live under a common
   parent that carries a **single** package manifest, lockfile, git repository, build
   config, or root README/AGENTS.md, those files are NOT written by any scope — they
   belong to coordinator finalization (below). A scope's plan that writes above its
   own `source_path`, or into a sibling's subtree, ⇒ FAIL.
3. **Independent tracking.** Each scope has its own `plan_folder_path` and
   `progress_folder_path`; no two share a progress file or IMPL-STATE.
4. **Bounded concurrency.** Cap concurrent scopes at a sane limit (≈ number of CPU
   cores − 2, or an orchestrator-provided ceiling); queue the rest. Excess scopes
   still run — just not all at once.

> Why the gate matters: a caller may *believe* its units are independent when they
> are not — e.g. multiple agents in ONE agent-graph share the graph scaffold, the
> framework `package.json`, and the shared state schema. Those scopes are NOT
> pairwise-disjoint, so the gate catches it and degrades to sequential rather than
> letting parallel writers clobber the shared graph. The safe partition granularity
> is whatever yields disjoint subtrees (often per bounded-context, not per agent).

## Coordinator protocol

1. Run the safety gate. Degrade to sequential on any failure.
2. Write the coordinator `_progress.json` (heartbeat) with `mode=fanout`,
   `total = len(parallel_scopes)`.
3. Fan out: spawn one isolated implementing-code sub-agent per scope, each with its
   own `{ plan_folder_path, source_path, progress_folder_path }` and the shared
   read-only inputs. Each sub-agent executes the ordinary sequential skill confined
   to its subtree. **Barrier** — await all.
4. **Coordinator finalization (single-writer, sequential):** exactly once, after the
   barrier —
   - Aggregate a root README / AGENTS.md across scopes if the tree needs one.
   - Perform any single shared dependency install / lockfile resolution.
   - Make one git commit spanning the tree (individual scopes do NOT commit to a
     shared index).
   - Merge each scope's IMPL-STATE into one consolidated report and emit the §11
     sidecar with per-scope `impl_output_path`s.
5. **Partial success:** a scope that BLOCKS or FAILS does not abort its siblings.
   Record its status; the consolidated report lists completed vs. blocked scopes so
   the orchestrator can REPAIR only the failures.

## Caller guidance

- Provide scopes only at a granularity that is **actually disjoint on disk**. When
  in doubt, partition coarser (e.g. per bounded context / independent package), not
  finer (per file/agent sharing a module).
- Keep all cross-scope/shared wiring (graph scaffold, shared schema, root manifest)
  in a **single** scope or a one-time pre-step, not duplicated across parallel
  scopes — otherwise the gate will (correctly) refuse to fan out.
