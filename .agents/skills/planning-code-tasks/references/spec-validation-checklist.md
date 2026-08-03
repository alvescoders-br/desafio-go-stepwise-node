# Spec Validation Checklist (Step 4 Consolidation + V01-V20)

Read this reference at Step 4. The 20 checks below are the consolidation pass and final-quality validation that gates writing PLAN-SPEC to disk. Apply Common Rationalizations + Red Flags + Verification Checklist at the end before exit.

---

## Step 4A. Consolidation Pass

After generating all sections:

1. Scan every unresolved item → verify it appears in open_questions
2. Scan every assumption → verify it appears in assumptions_to_validate
3. Verify open_questions.summary counts match actual counts in sub-tables
4. Verify no executable section requires RESEARCH-SPEC dereferencing
5. Verify every non-summary open_questions row has `phase_ref` (`all` or explicit phase IDs)
6. Verify plan_status consistency: PROCEED (zero pending_inputs HIGH), CONDITIONAL (pending exist but MEDIUM/LOW with fallback_behavior), BLOCKED (any pending HIGH), VERIFY_ONLY (all file rows have non-none pre_applied), PARTIAL_APPLIED (some file rows have non-none pre_applied and some have pre_applied=none)
7. **Implementability override (REC-009).** Before applying rule 6, re-rate impact by *implementability*, not by subjective severity. For EACH unresolved item in open_questions (pending_inputs, implementation_gaps, assumptions_to_validate, upstream_gaps_carried_forward), ask: **"Can the implementing agent author the planned file(s)/phase deterministically WITHOUT this answer?"**
    - If **NO** (the item gates implementability — an unknown file target, an undecided contract/schema/endpoint, an unresolved dependency or wiring decision, a missing identifier the plan needs), it is **HIGH by definition** — re-tag `impact: HIGH`, set `fallback_behavior: BLOCKED`, and, for FULL_SDLC plans, add its ID to `blocker_resolution.blockers_from_open_questions`. A planner MAY NOT down-rate an implementability-gating item to MEDIUM/LOW to keep the plan shippable.
    - If **YES** (implementation can proceed), MEDIUM/LOW is allowed only when `fallback_behavior` is populated with the narrowest backward-compatible behavior the executor should apply.
    Then apply rule 6 with the corrected impacts. This closes the "deferred silently under CONDITIONAL" gap.
8. Verify phase decomposition matches complexity (TASK) or research sequencing (FULL_SDLC)
9. Verify `research_fingerprint` is either `N/A` or `sha256:<64 lowercase hex chars>`. `mtime:`, bare hashes, mtimes, filenames, and session IDs are invalid.

If corrections needed → apply in place, log to CHANGE_LOG.

---

## Step 4B. Validation Checks (V01-V20)

| ID | Check |
|----|-------|
| V01 | Audit Source Fidelity — every executable section has compact evidence_refs or PLAN-AUDIT source coverage |
| V02 | Zero Invention — no executable item appears without research/source evidence or open_questions coverage |
| V03 | Phase Integrity — phase count matches complexity (TASK) or research sequencing (FULL_SDLC) |
| V04 | File Coverage — every affected file from research appears in at least one phase |
| V05 | AC Traceability — every acceptance criterion maps to a phase or is flagged |
| V06 | Test Coverage — every phase has at least one test strategy entry |
| V07 | Dependency Consistency — no circular dependencies in phase ordering |
| V08 | Rollback Coverage — every non-trivial rollback/deployment risk has a rollback strategy; empty rollback sections are not required |
| V09 | Source Coverage — executable facts have compact evidence_refs or PLAN-AUDIT source coverage |
| V10 | open_questions Completeness — every pending/assumption item registered |
| V11 | ID Uniqueness — no duplicate IDs across sections |
| V12 | Technology Fidelity — EXACT names/versions from research or source code |
| V13 | Anti-Fade — last section depth matches first section depth |
| V14 | Scope Isolation — no TASK sections in FULL_SDLC spec or vice versa |
| V15 | Summary Counts — open_questions.summary counts match actual |
| V16 | plan_status Derivation — status consistent with pending_inputs impact levels after the Step 4A implementability override |
| V17 | Placeholder Resolution — no unblocked phase contains placeholder file targets (`[TBD]`, `[unknown]`, etc.) |
| V18 | CONTRADICTORY_PLAN_STATUS — plan is not PROCEED/CONDITIONAL while any implementability-gating target is unresolved |
| V19 | EXECUTION_SELF_CONTAINMENT — every implementation-relevant fact is literal in PLAN-SPEC or in `required_artifacts`; no RESEARCH-SPEC load is required for normal execution |
| V20 | RESEARCH_FINGERPRINT_SHA256 — `research_fingerprint` is `N/A` or `sha256:<64 lowercase hex chars>` and never `mtime:` |

Run each check → PASS/FAIL. On FAIL → fix in place, log correction, re-run consolidation (max 2 retries).

`quality_score = (PASS_count / 20) * 100`

**V17 detail:** A phase MUST NOT be marked "unblocked" if any entry in files_to_modify or files_to_create contains `[to be identified]`, `[TBD]`, `[unknown]`, or similar placeholder text. Such phases → CONDITIONAL with pre-condition. Flag unresolved file targets in audit as validation failure.

**V18 detail (REC-009 — the named status-vs-open-questions consistency check):** After the Step 4A implementability override has corrected impacts, FAIL if `plan_status` is `PROCEED` or `CONDITIONAL` while ANY unresolved open_questions item is implementability-gating (i.e., re-tagged HIGH by Step 4A, or present in `blocker_resolution.blockers_from_open_questions` for FULL_SDLC). Such a plan MUST be `BLOCKED` — an unresolved target the implementer cannot proceed without is a blocker, never a silently-deferred open question. On FAIL: re-derive `plan_status = BLOCKED`, surface the gating IDs in the audit, and log the correction. This is the loophole REC-009 identified: registration in open_questions does not permit shipping. **Bounded, no loop:** like every V-check this is a one-pass fix-in-place (max 2 consolidation retries) — it re-rates and re-derives status from existing data, it does not re-plan.

**V19 detail:** FAIL if a phase, acceptance criterion, interface contract, constraint, test strategy, required artifact, or canonical value requires the implementer to load RESEARCH-SPEC to know an exact path, literal, signature, enum member, error code, default, range, or command. Fix by inlining the literal in PLAN-SPEC, adding a row to `canonical_values`, or listing a non-research file in `required_artifacts`. `PLAN-AUDIT` and `RESEARCH-SPEC` may be consulted only as repair/forensics fallback, not as normal execution context.

**V20 detail / Research fingerprint detail:** FAIL if `research_fingerprint` starts with `mtime:`, is a bare hash without the `sha256:` prefix, contains uppercase hex, is not 64 hex chars after the prefix, or uses any session/file identifier. Fix by computing the SHA-256 content hash of the selected RESEARCH-SPEC bytes and writing `research_fingerprint: sha256:<hash>`. If the fingerprint does not match the current `research_source` fingerprint at execution launch, refuse execution and require re-planning unless an explicit stale-research override is supplied. Log any override to PLAN-AUDIT.

**Pre-applied detail:** If `plan_status` is `VERIFY_ONLY`, every `files_to_create` and `files_to_modify` row must have non-`none` `pre_applied` evidence. If `plan_status` is `PARTIAL_APPLIED`, at least one row must have non-`none` evidence and at least one row must have `pre_applied: none`.

---

## Common Rationalizations (and counters)

| Excuse | Why It Fails | Counter |
|--------|-------------|---------|
| "The research is clear enough, I don't need a detailed plan" | Without explicit phases, file lists, and acceptance criteria, the implementing agent guesses. Guesses become deviations. | The plan is the contract between research and implementation. Vague plans produce vague code. |
| "I'll keep it high-level and let the implementer figure out details" | High-level plans force the implementer to make architectural decisions that belong in planning. | Every phase must specify: files to create/modify, patterns to use, test approach, and acceptance criteria. |
| "This is a small fix, one phase is enough" | Even small fixes need: reproduction test, fix, regression verification. That's 2-3 logical steps minimum. | Use TASK scope with appropriate phase count (LOW=1, MEDIUM=2, HIGH=3 based on complexity). |
| "I'll add the test phase later" | Plans without test phases produce implementations without tests. Testing is not optional or deferred. | Every phase includes test expectations. TDAD mode requires explicit Red-Green-Refactor sequencing per file. |
| "The research already specifies the approach, the plan is redundant" | Research identifies WHAT to do. Planning specifies HOW and IN WHAT ORDER. Different concerns. | Transform research findings into ordered, verifiable implementation steps with explicit dependencies. |

---

## Red Flags

Signs that this plan is insufficient or being generated superficially:

- Phase has no file list (implementer doesn't know what to create)
- Phase has no acceptance criteria (no way to verify phase completion)
- Plan lacks compact evidence_refs or PLAN-AUDIT source coverage (disconnected from analysis)
- All phases have identical structure (copy-paste, not tailored)
- No dependency ordering between phases (parallel execution assumed without justification)
- Test approach says "unit tests" without specifying what to test
- `test_cases_path` was supplied but a `testing_strategy` row has no `test_case_id` (neither an FTC id nor `[derived]`) — traceability to QE design broken
- An in-scope FTC is neither in a `testing_strategy` row nor in a phase's `out_of_scope` exclusion (see SV-09) — silent coverage drop
- A `type: e2e` row derived from an FTC lacks `covered_by: qe-web-automation` — risks double-automation downstream
- TASK scope used for work requiring >3 phases (should be FULL_SDLC)
- Plan file lists don't match research's affected_files analysis
- Zero open_questions on a complex multi-phase plan (indicates insufficient scrutiny)
- MEDIUM/LOW pending input without fallback_behavior (headless executor has no deterministic action)
- open_questions row without phase_ref (harness cannot determine phase load set)
- VERIFY_ONLY/PARTIAL_APPLIED plan without file-row pre_applied evidence
- Shared literals repeated across phases instead of centralized in canonical_values
- Auth/OAuth/password-reset phase without explicit reset-token hash-at-rest and
  provider allow-list constraints plus matching tests

---

## Verification Checklist

Every item requires **evidence**, not assertion. "Seems right" is never sufficient.

- [ ] Every phase has explicit file lists — Evidence: files_to_create and files_to_modify arrays are non-empty
- [ ] Every phase has acceptance criteria — Evidence: AC section with testable conditions per phase
- [ ] Research traceability maintained — Evidence: each phase has evidence_refs or PLAN-AUDIT source coverage
- [ ] Phase ordering respects dependencies — Evidence: no phase references files created in a later phase
- [ ] Test expectations specified per phase — Evidence: test approach section with framework, location, and coverage targets
- [ ] Scope matches complexity — Evidence: TASK scope for ≤3 phases, FULL_SDLC for larger work
- [ ] Zero Invention Policy respected — Evidence: no file or pattern appears that isn't traceable to research
- [ ] Execution self-contained — Evidence: no executable section says "see research" for a needed value; shared literals are in canonical_values; external files are in required_artifacts
- [ ] PLAN-SPEC validates against template — Evidence: all required sections present per references/code-task-planning-template.md
