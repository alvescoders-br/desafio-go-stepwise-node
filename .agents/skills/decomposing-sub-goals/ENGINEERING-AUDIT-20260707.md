# ENGINEERING-AUDIT — decomposing-sub-goals

## 1. Session metadata

| Field | Value |
|-------|-------|
| session_id | ENGINEERING-DECOMPOSINGSUBGOALS-20260707 |
| mode | build |
| skill_name | decomposing-sub-goals |
| date | 2026-07-07 |
| source | SPEC_STEPWISE_ITERATION_GROUPS_CONTRACT.md §5.1; researching-code-design Step 1.5 (Scope Triage Gate); code-development-autoloop scope_type contract |
| generation_shape | list-shape (one discrete structured file: sub-goal-decomposition.json) |
| stepwise_invoked | true |
| exploration_heavy | false (bounded inputs: one PRD + one Epics artifact; no broad repo sweep) |
| routing | catch-all list-shape: §2 → §10.5 → §11 |

## 2. Purpose

Produces `sub-goal-decomposition.json` — the `loop_source_artifact` that drives a
Stepwise loopable capability group (SPEC_STEPWISE_ITERATION_GROUPS_CONTRACT). It
converts an approved PRD + Epics into ordered sprint-planning chunks; each chunk
(one or more epics grouped together, or a slice of an oversized epic) is one
`code-development-autoloop` iteration. Chunk sizing is governed by the
`chunking_criteria` parameter, defaulting to the autoloop scope-triage tripwire.

## 3. Pattern compliance

| Pattern | Applicability | Status | Evidence |
|---------|---------------|--------|----------|
| P1 Write-Flush-Forget | universal | present | Step 3/4 write JSON immediately, flush source text; chunking loop flushes epic bodies. |
| P2 Carry-forward index | universal | present | DECOMPOSITION_INDEX is the sole cross-phase contract. |
| P3 REPAIR folder reuse + harness SESSION_ID | universal | present | Fixed output_folder; SESSION_ID from metadata (BUILD) / prior AUDIT filename (REPAIR); no local SESSION_ID formula. |
| P4 Surgical REPAIR | universal | present | chunking-rules + output-contract REPAIR sections re-chunk only targeted span, preserve rest verbatim. |
| P5 Mandatory source loading | universal | present | Step 2 loads PRD+Epics; Zero-Invention: un-sourced backlog dropped, not invented. |
| P6 Source fidelity gate | universal | present | Pre-write fidelity checklists in both reference files and Step 4. |
| P7 Living progress tracker | universal | partial (n/a) | Single-file output — _progress.json (§2) is the tracker; no per-item 00-index needed for one JSON file. |
| P8 Section-shape protocol | gated (section-shape) | n/a | list-shape — §10 does not apply. |
| P9 Harness output sidecar | gated (stepwise_invoked) | present | Step 5 cites §11, names `sub_goal_decomposition_path`, §11.1.1 path-correctness + §11.4 ordering. |
| P10 Delegated exploration | gated (exploration_heavy) | n/a | exploration_heavy=false — bounded inputs. |

Overall: 8/8 applicable patterns present (P7 satisfied via §2 for a single-file output; P8/P10 n/a by shape).

## 4. Anti-patterns checked

| ID | Check | Result |
|----|-------|--------|
| AP-06 | No `{{variable}}` control syntax in prose | pass |
| AP-11 | `_progress.json` schema matches shape (list-shape total/completed/items) | pass |
| AP-14 | No shell-mutation of the output file (JSON via full-file Write, not sed/awk/cat>) | pass |
| AP-17 | Stepwise-invoked → final §11 sidecar step present with named param | pass |
| AP-18 | No mechanics duplication — §2/§10.5/§11 cited, not restated | pass |
| SESSION_ID formula | grep `SESSION_ID = "` returns zero matches | pass |

## 5. Files written

| Path | Status |
|------|--------|
| .agents/skills/decomposing-sub-goals/SKILL.md | written |
| .agents/skills/decomposing-sub-goals/references/chunking-rules.md | written |
| .agents/skills/decomposing-sub-goals/references/output-contract.md | written |
| .agents/skills/decomposing-sub-goals/evals/evals.json | written |
| .agents/skills/decomposing-sub-goals/ENGINEERING-AUDIT-20260707.md | written |

## 6. Registry updates (execution-protocol.md) — decision

- **Routing table:** NOT modified. This repo's `## Skill → Required Sections`
  routes by generation shape with an explicit **catch-all** (`§2 → §10.5 → §11`)
  for any skill not otherwise classified. `decomposing-sub-goals` is a plain
  list-shape, non-exploration, non-section skill → the catch-all already covers
  it. Adding a bespoke row would duplicate the catch-all. The SKILL.md declares
  its shape + route inline (self-routing), as the protocol requires.
- **Artifact Type Registry (Memory Bank §4):** NOT modified. The skill does not
  opt into Memory Bank session-end writes (single-artifact, single-session,
  stateless), and the universal rule makes §4 opt-in only. No registry row needed.

Both omissions are intentional and consistent with this repo's structure, not
skipped work.

## 7. Open questions

- OQ: the pilot offering that wires `sprint-planning` (this skill's capability) →
  `dev-cycle` group → `code-development-autoloop` is still open
  (SPEC_STEPWISE_ITERATION_GROUPS_CONTRACT OQ-02 / OQ-04, owner AI Pods). The
  skill + capability are ready; the offering-level `capability_groups` wiring is a
  separate authoring decision.

## 8. Generation summary

Skill built: list-shape, Stepwise-invoked, 8/8 applicable patterns present,
0 anti-patterns outstanding. Reference files: 2 (chunking-rules, output-contract).
Evals: 3 (group, split, repair). Sole skill of the new `sprint-planning`
capability.
