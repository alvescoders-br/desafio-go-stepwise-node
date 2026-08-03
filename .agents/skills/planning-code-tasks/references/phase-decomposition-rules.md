# Phase Decomposition Rules

Read this reference at Step 3 (Generate Agent-Native Spec). The rules below govern how research is transformed into ordered phases for both TASK and FULL_SDLC scopes.

---

## TASK scope — phase count by complexity

| complexity | phase_count | rationale |
|------------|-------------|-----------|
| LOW | 1 | Single atomic change set |
| MEDIUM | 2 | Prepare + implement |
| HIGH | 3 | Prepare + implement + stabilize |

---

## FULL_SDLC scope — re-interpretation, not pass-through

The research `implementation_sequencing` section defines dependency-ordered story groups. The planning skill re-interprets these into implementation phases by:

1. Splitting phases where ANY of:
   - `total_files > 5` (too many files for one phase)
   - `complexity == HIGH` AND `total_files > 3` (high-complexity phases stay small)
   - `external_integrations > 1` (each external integration is its own phase)
   - Mixed bounded contexts (BC-XX) within one phase
   - Mixed parallel-execution groups from research `implementation_sequencing`
   Do NOT use day/effort/sprint heuristics — this skill produces an
   AI-agent-consumable plan, not a human delivery schedule.
2. Assigning concrete file paths per phase (from research `file_specifications`)
   - **2a. Exception chain tracing:** When research identifies an exception-related fix (e.g., catching or rethrowing an exception), trace the exception propagation chain through all calling methods. Add any methods that need companion exception handling to files_to_modify.
3. Adding tactical implementation steps per phase
   - **3a. BUG_FIX scope — MANDATORY Prove-It sequence per phase:** Every phase's implementation_steps MUST start with a REPRODUCE step and end with a VERIFY step:
     - Step 0 (REPRODUCE): Run the specific test/command that proves the bug exists. The test MUST fail. If it passes, the bug is already fixed — escalate as unexpected. Format: `[REPRODUCE] {test command} — expected: FAIL (confirms bug present)`
     - Steps 1..N: Apply the fix (code changes)
     - Step LAST (VERIFY): Run the same test/command. It MUST now pass. Format: `[VERIFY] {same test command} — expected: PASS (confirms bug fixed)`
     - If the research `tests_to_write` lists a reproduction test, use its exact command. If no reproduction test exists, derive one from the research `root_cause_statement`.
4. Adding per-phase testing strategy with specific test commands
   - **4a. TDAD (Test-Driven Agentic Development) — MANDATORY for TASK scope:** The implementing agent defaults `tdad_mode=true` for TASK scope. The plan MUST emit explicit Red-Green-Refactor instructions per file:
     - **RED:** Write the failing test FIRST (test file path + test name + what it asserts)
     - **GREEN:** Write the minimal production code to make it pass
     - **REFACTOR:** Clean up while keeping tests green
     - Include a `testing_strategy.tdad_mode: true` field in the PLAN-SPEC header.
     - Each phase's `testing` section must list the per-file RED-GREEN-REFACTOR sequence.
     - **FTC-anchored RED (when `test_cases_path` was supplied):** the RED test's
       assertion MUST come from the cited FTC's Gherkin (Given/When/Then), not a
       freely-invented assertion. Put the FTC id(s) in that row's `test_case_id`.
       The planner still chooses the *level* — a `[BE]` FTC becomes a `unit` or
       `integration` RED here; an `[FE]`/journey FTC is NOT turned into a RED test,
       it is marked `type: e2e` + `covered_by: qe-web-automation` and excluded so the
       automation capability owns it (no double-automation). FTCs with no natural
       unit/integration level are deferred, never dropped silently.
   - **4b. Auth security defaults:** When a phase implements authentication,
     OAuth, sessions, identity linking, or password reset, the phase constraints
     and tests MUST include:
     - password-reset tokens persisted to storage are hashed at rest; only the
       one-time raw token is returned/sent to the user;
     - OAuth provider inputs are validated against an explicit allow-list before
       choosing provider-specific columns, scopes, or identity-field mappings;
     - tests cover invalid provider values and reset-token replay/lookup using
       the hashed stored value.
5. Adding per-phase deployment artifacts (migrations, feature flags)
6. Adding per-phase success criteria (build commands, AC verification)

---

## Phase content differs by scope

| Field | TASK | FULL_SDLC |
|-------|------|-----------|
| fix_pattern (inline code block, max 25 lines) | Yes — agent uses for mechanical fix application | No — use pattern_reference instead |
| pattern_reference (table: pattern, adr_ref, example_location) | No | Yes — points to ADR or existing code |
| story_ids | No (single task) | Yes — maps user stories to phase |

---

## Status Protocol

Every item has `status: complete | pending | assumption`:

- `complete`: all fields populated from source evidence
- `pending`: one or more fields missing → item also registered in `open_questions`
- `assumption`: inferred from standard practice → ASM-XX ID assigned

---

## Source Tagging

- Every item has a `source` field pointing to REFERENCE_MAP entry
- No source → status MUST be `pending` or `assumption`

---

## Anti-Fade Rule

Last section must match depth of first section.

---

## Quality Criteria Integration (MANDATORY when quality_criteria_path was provided)

- List ALL REQUIRED items extracted from quality_criteria_path as explicit acceptance criteria
- Tag each with `source: QUALITY_CRITERIA` and `classification: REQUIRED` (or `OPTIONAL`)
- The downstream `implementing-code` step must implement 100% of REQUIRED items before submitting for validation
- REQUIRED items not addressed by any phase MUST be registered in `open_questions` with `phase_ref` and deterministic `fallback_behavior` when non-blocking
- OPTIONAL items SHOULD be addressed where feasible; not addressing them is not a planning gap
