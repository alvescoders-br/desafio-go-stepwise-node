# Engineering Audit — validating-architecture-compliance

**Mode:** BUILD
**Source material:** Globant skill `globant-engineering-technical-feasibility` (converted from human-first conversational shape to agent-native multi-story batch mode).
**SDLC phase:** development (gates user stories before they enter the implementation pipeline)
**Output pattern:** single-file (COMPLIANCE-SPEC) + audit

## Pattern Compliance

| Pattern | Status | Notes |
|---|---|---|
| Write-Flush-Forget | partial | Single file by default; flush activates only if context > 60% during Step 3. For very large backlogs (>200 stories) this becomes load-bearing. |
| Carry-Forward Index (COMPLIANCE_INDEX) | present | Sole source of truth between Steps 1–5. Tracks verdicts by category and gap counts by area. |
| REPAIR Folder Reuse | present | Step 1 detects REPAIR, locates PREVIOUS_SPEC, increments version. |
| Surgical REPAIR | present | REPAIR_DIRECTIVES target individual `story_id`s or compliance areas; non-targeted stories preserved verbatim. EVAL-COMP-003 covers this. |
| Mandatory Source Loading | present | STOP-GATE in Step 2 enforces user_stories_path AND target_architecture_path. |
| Source Fidelity Gate | present | Step 4 rule #3 (every gap cites architecture id), rule #4 (every gap cites story AC/business rule), rule #10 (no phantom UNIT/principle/ADR ids). |
| Living Progress Tracker | present | `_progress.json` written first, updated per story in Step 3, finalized in Step 5. |

## Anti-Patterns Avoided

- **"Generally looks fine":** Step 3 + Step 4 require all 6 areas explicitly assessed for every story. Skipping = quality defect.
- **Designing the architecture:** Step 3 rule #5 (authority guard) rewrites any gap that names a specific replacement technology so it describes the conflict category only. Recommending architecture is out of scope.
- **Performance/Security as one bucket:** validation-framework.md splits NFR into 6a Performance and 6b Security; Step 4 rule #2 enforces both subareas explicitly.
- **Mixed verdicts collapsing to APPROVE:** verdict tree explicitly upgrades any architecture-change gap to INITIATE_ADR even when other gaps are adjustable.
- **Ambiguous AC bypass:** Step 3 + Verdict tree treat resolution-implying ambiguous language ("real-time", "instantly") as RETURN_TO_PRODUCT even when a compliant path exists.

## Reference File Map

| File | Phases consuming it | Complexity |
|---|---|---|
| `references/validation-framework.md` | Step 3 | M (~205 lines, the 6 area definitions + gap calibration + what is NOT a gap) |
| `references/output-templates.md` | Step 3 | S (~80 lines, Templates 1a / 1b / 2 / 3) |

Total reference surface: 2 files, both always loaded once at Step 3.

## Architecture Decisions

| Decision | Rationale |
|---|---|
| Per-story batch evaluation, not interactive | Globant source asked the user to provide ASD + requirements interactively. Agent-native execution requires zero clarifying questions; gate via STOP-GATE in Step 2 + open_questions registry. |
| Three verdicts only (no PARTIAL) | Globant's binary "compliant / not" plus path classification preserves the unidirectional gate. Adding PARTIAL would create ambiguity at platform-export time. |
| DTR cross-check is observational, not gating | Stories that touch legacy/migrating tools are noted in audit but do NOT block the verdict. Phased delivery is a planning concern, not a compliance gap. |
| Authority guard rewrites specific tech recommendations to category language | Preserves the "this skill assesses; ADR process decides" boundary even under pressure to be helpful. |
| `story_scope` parameter (default `all`) | Allows targeted re-runs after architecture updates without re-evaluating the entire backlog (matches the EVAL-COMP-002 + 003 patterns). |
| Output `compliance_feedback` as one-line-per-non-approved-story | Lets the orchestrator's repair loop route stories back to product-delivery (RETURN_TO_PRODUCT) or software-architecture (INITIATE_ADR) without re-reading the spec file. Mirrors `reviewing-code`'s `review_feedback` shape. |

## Open Questions Registered

- Should APPROVE verdicts include "evidence rows" (positive findings per area), or only gaps? — Resolved: evidence rows go in Template 2 as bullet points; required by Step 4 rule for completeness.
- Should the skill emit a separate file per epic (matching implementing-user-stories' per-epic shape) instead of one consolidated file? — Resolved: single file with anchors per story_id is simpler for the gate consumer (platform-export). If volume becomes an issue, split via `story_scope` per epic.

## Evals Generated

3 test scenarios in `evals/evals.json`:
- EVAL-COMP-001: 12-story backlog with mixed verdicts (8/2/2)
- EVAL-COMP-002: scoped re-evaluation (one epic only)
- EVAL-COMP-003: REPAIR after ADR resolves a previously-blocking gap

## Downstream Consumers (registered)

- `formatting-platform-export` (only stories with verdict APPROVE pass through)
- Orchestrator repair loop (RETURN_TO_PRODUCT → product-delivery; INITIATE_ADR → software-architecture)
- `humanize-spec` profile `architecture-compliance` (rendering layer)

## Capability YAML Placement (decided)

New step `validating-architecture-compliance` inserted between `backlog-story-validation` and `platform-export` in `capability_product-delivery.yaml`, followed by `architecture-compliance-validation` quality gate that gates on the verdict counts.
