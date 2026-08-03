# Engineering Audit — generating-toolchain-record

**Mode:** BUILD
**Source material:** Globant skills `globant-engineering-development-toolchain-create` and `globant-engineering-development-toolchain-extract` (merged into a single agent-native skill with `dtr_mode` parameter).
**SDLC phase:** discovery (sibling to ADRs and target architecture)
**Output pattern:** single-file (DTR) + audit + optional derived runtime registry (validation-tools.md)

## Pattern Compliance

| Pattern | Status | Notes |
|---|---|---|
| Write-Flush-Forget | partial | DTR is single-file; row count is bounded so flushing is unlikely. Activated only if context > 60% during Step 3. |
| Carry-Forward Index (DTR_INDEX) | present | Sole source of truth between Steps 1–6. Tracks rows_classified, states_count, toolchain_notes counts, validation_tools status. |
| REPAIR Folder Reuse | present | Step 1 detects REPAIR via `failure_feedback`; reuses existing DTR_FOLDER and increments version. Orphan archive rule in Step 2F. |
| Surgical REPAIR | present | REPAIR_DIRECTIVES target specific tabs/sections; non-targeted sections preserved verbatim. EVAL-DTR-003 covers this. |
| Mandatory Source Loading | present | STOP-GATE in Step 2 enforces presence of `target_architecture_path`; brownfield warns when PB or source is missing but does NOT block. |
| Source Fidelity Gate | present | Step 4 validation rule #9 (No Phantom Rows) ensures every emitted tool exists in ARCH_CONTEXT, PB_CONTEXT, SOURCE_INSPECTION, or stack reference. Rule #3 enforces source citation for non-stable rows. |
| Living Progress Tracker | present | `_progress.json` written on first action (Step 1) and updated after Steps 1, 3, 5, 6. Memory Bank progress.md row appended at end. |

## Anti-Patterns Avoided

- **Two skills sharing 90% logic:** Globant variant separated greenfield/brownfield into two skills; we merged via `dtr_mode` parameter (KEEP/CONSOLIDATE rule).
- **Asking the human:** removed all "Ask the user" branches from Globant source; missing inputs trigger gap report or open_questions, never interactive prompts.
- **Inferred rows without provenance:** `(inferred)` markers MUST cite an architectural pattern; rule #7 in Step 4.
- **Architecture-time vs runtime conflation:** state classification (DTR) and CLI commands (validation-tools.md) live in two files with explicit source-of-truth contract documented in `references/validation-tools-derivation.md`.

## Reference File Map

| File | Phases consuming it | Complexity |
|---|---|---|
| `references/dtr-template.md` | Step 3 | M (~250 lines, full tab/field catalog + Toolchain Notes) |
| `references/state-classification.md` | Step 3 | S (~75 lines, decision tree + cross-skill contract) |
| `references/validation-tools-derivation.md` | Step 5 (only when derive_validation_tools=true) | M (~95 lines, mapping + drift rules) |
| `references/stacks/*.md` (12 files) | Step 2E (one or more, language-routed) | S each (85–110 lines) |

Total reference surface: 15 files. Stack files are loaded selectively (only the language(s) detected). Average loaded surface per run: 3 stack files + 3 always-loaded references = ~6 files.

## Architecture Decisions

| Decision | Rationale |
|---|---|
| Merge greenfield+brownfield into one skill via `dtr_mode` | Globant's two-skill separation duplicates 90% of workflow. Single skill with mode parameter is the consistent pattern (`planning-code-tasks` TASK/FULL_SDLC, `researching-refactoring` version-upgrade/structural/combined). |
| Keep stack reference files as-is from Globant source | They are pure tool catalogs with no human-first idioms. Direct copy preserves accuracy of canonical tool names and version conventions. |
| Add `derive_validation_tools` flag (default true) | Bridges DTR (architecture-time) to validation-tools.md (runtime) per the source-of-truth contract. Default-on so the integration with code-development capability is automatic; toggle-off available for audit-only DTR runs. |
| Omit legacy/migrating rows from validation-tools.md | Phase C in implementing-code only verifies code that is supposed to be running. Verifying legacy code paths produces noise. |
| `(inferred)` allowed but tagged | Greenfield ASDs do not enumerate every tool; some pairings (e.g., Spring Boot → SLF4J + Logback) are inferred from architectural patterns. Mark + cite preserves zero-invention discipline. |

## Open Questions Registered

- Should the skill emit a separate "human ASD-style narrative" for the DTR, or rely entirely on `humanize-spec` profile `dtr`? — Resolved: rely on humanize-spec (separation of concerns).
- Should brownfield REPAIR overwrite legacy rows or preserve them as historical record? — Resolved: preserve previous DTR's legacy rows when not addressed by REPAIR_DIRECTIVES (surgical REPAIR rule).

## Evals Generated

3 test scenarios in `evals/evals.json`:
- EVAL-DTR-001: greenfield Java + React (no PB, no source)
- EVAL-DTR-002: brownfield Python migration with source inspection
- EVAL-DTR-003: surgical REPAIR (Mobile tab Lint correction only)

## Downstream Consumers (registered)

- `validating-architecture-compliance` (state info)
- `researching-feature-impl`, `researching-bug-fixing` (state info, optional)
- `planning-code-tasks` (state info, optional)
- `implementing-code` Phase C (via derived `validation-tools.md`)
- `reviewing-code` (via derived `validation-tools.md`)
- `humanize-spec` profile `dtr` (rendering layer)

## Capability YAML Placement (decided)

New step `generating-toolchain-record` appended after `target-architecture-specifications-validation` in `capability_software-architecture.yaml`, followed by `toolchain-record-validation` quality gate.
