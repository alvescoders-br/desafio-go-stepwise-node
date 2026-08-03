# REPAIR Mode

Read this reference at Step 1 **only when** `failure_feedback` is non-empty OR a previous REVIEW-SPEC with status FAILED exists OR the prompt carries a `## Previous verification (lap N-1)` block (REVERIFY). In FRESH mode, this file does not apply — skip it.

This file consolidates the rules that govern how repair-cycle reviews (REPAIR and REVERIFY) differ from fresh reviews.

---

## Review Consistency Rule — Stable Checklist Across Rounds

```
RULE: STABLE CHECKLIST ACROSS ROUNDS

For code-development, feature-impl, and refactoring scopes:
  - Apply the COMPLETE verification checklist categories to every phase that was
    in scope on the prior round, including REPAIR rounds.
  - REPAIR_FOCUS narrows the INITIAL LOAD SET and which findings to prioritize
    in the report, not which verification categories to run.
  - Initial repair/reverify load set = prior validation report or threaded
    prior-verdict block + current IMPL-STATE + files from prior findings +
    current-lap changed files + their tests/direct imports.
  - Expand to full plan/research/source only when a required checklist category
    cannot be answered from the initial load set. Record each expansion in
    REVIEW-AUDIT with `load_mode`, `reason`, and files added.
  - Every verification category applied in R1 must also be applied in R2 and R3.
  - Do NOT introduce new issue categories in R(N+1) that were not checked in R(N).
    If a check was not performed in R1, it should not appear as a new finding in R2.
  - The delta analysis (Step 7) tracks what changed — the verification scope must
    remain constant so the delta is meaningful.
```

---

## Fresh Review Spec Rule (MANDATORY)

```
RULE: EVERY REVIEW PRODUCES A FRESH REVIEW-SPEC

Each review round (including REPAIR rounds) MUST produce a FRESH REVIEW-SPEC
that reflects the CURRENT code state. Do NOT carry over findings from previous
reviews.

PROTOCOL:
1. START from scratch — read the CURRENT source files, not the previous REVIEW-SPEC
2. RUN all verification checks against the CURRENT code state
3. PRODUCE findings based ONLY on what you observe NOW
4. DO NOT copy findings from a previous REVIEW-SPEC — if an issue was fixed,
   it must NOT appear in the new spec
5. INCLUDE a repair_delta section when in REPAIR mode:
   repair_delta:
     previous_review_id: "{previous REVIEW-SPEC session_id}"
     fixed: [{ finding_id, description }]
     still_failing: [{ finding_id, description, evidence }]
     regressions: [{ finding_id, description, evidence }]
6. The repair_delta is INFORMATIONAL — the verdict (PASSED/PARTIAL/FAILED)
   is computed from CURRENT findings only, never from previous findings

RATIONALE: Carrying over stale findings causes false FAILED verdicts on fixed code,
wasting repair cycles. Fresh review with delta tracking provides both accuracy and
repair progress visibility.

For bug-fixing scope:
  - REPAIR mode MAY narrow scope to REPAIR_FOCUS (feedback files + dependencies).
    The change surface is small and the codebase may be very large — full-scope
    review would waste tokens on unrelated files.
  - FRESH mode still uses full scope (all phases in the plan).

RATIONALE: Narrowing checklist categories between rounds causes oscillation; loading
the entire source tree every round causes token blowups. Stable categories with
evidence-indexed loading preserve convergence while reducing repeated context.
Bug-fixing remains allowed to narrow both checklist and load set when the plan is
already narrowly scoped to the fix.
```

---

## REPAIR Mode Mechanics

Triggered when `failure_feedback` is provided. Follow execution-protocol.md Section 7.

In summary: load existing REVIEW-SPEC, apply directives to flagged findings only,
produce fresh review of affected files, generate repair_delta (fixed/still_failing/regressions).

---

## REPAIR Cycle Review Mode (scoped repair reads)

When triggered from a repair cycle (failure_feedback references prior repair or contains file-specific feedback):

1. **Prioritize** reading only the files listed in the failure_feedback.
2. After confirming the listed issues are resolved, **scan adjacent files** for similar patterns (e.g., other test files importing the same module, other services using the same interface).
3. Do NOT re-read the entire codebase unless a new architectural concern is raised in the failure_feedback.
4. Log: "REPAIR-scoped review: {N} files targeted vs {M} total source files"

This scoped approach reduces per-repair review cost without sacrificing regression detection on related files.

---

## REVERIFY Mode (VGT-loop verdict memory)

REVERIFY is a repair-cycle review driven by the automated Verdict-Gated-Transition loop, NOT by `failure_feedback`. It triggers when the prompt carries a `## Previous verification (lap N-1)` block: this gate returned FAILED on the prior lap, the producer (`implementation`) was re-run in REPAIR, and now the gate re-reviews the updated code. The harness threads the prior review report + verdict into that block (verdict memory).

REVERIFY runs the **same review as REPAIR** — the differences are only:

1. **Prior-report source = the threaded block.** Parse `PRIOR_VERDICT` + `PRIOR_FINDINGS` from the `## Previous verification (lap N-1)` block, and use them as the authoritative prior report for the `repair_delta`. This is robust even if the prior lap's REVIEW-SPEC file was cleaned from `OUTPUT_DIR`. If a `PREVIOUS_SPEC` file is also present, prefer the block.

2. **No `failure_feedback`.** There is no per-file feedback string on a VGT gate re-run. Derive `REPAIR_FOCUS` (report-priority files) from `PRIOR_FINDINGS` + this lap's `IMPL-STATE.modified_files`.

3. **Delta stated against the prior lap's verdict.** The `repair_delta` (fixed / still_failing / regressions) is computed against `PRIOR_FINDINGS`; the verdict is computed from CURRENT findings only (Fresh Review Spec Rule). State the delta explicitly (e.g. "3 blocking findings fixed, 0 regressions, 1 still failing").

**Scope does NOT narrow to "failed items" for full-implementation reviews, but
the load set may start there.** The Stable Checklist Across Rounds rule still
governs: for `code-development` / `feature-impl` / `refactoring`, the same
verification categories must run every lap. The first files loaded should be
the failed-item files, current changed files, their tests, direct imports, and
the current IMPL-STATE; then expand only where a checklist category lacks
evidence. Therefore a gate `gate_policy.reverify_scope: failed_items` is
interpreted as initial-load guidance, not as permission to skip categories.
Only **bug-fixing** scope may narrow the actual checklist to `REPAIR_FOCUS`.

**Regressions are blocking.** A previously-passing check that now fails is a regression: it must appear in `repair_delta.regressions` and forces the verdict toward FAILED regardless of how the weighted picture looks.

**Fallback:** if the block is malformed / unparseable, fall back to REPAIR detection (same-folder `PREVIOUS_SPEC` scan) or, absent that, FRESH — never fabricate a delta against a prior report you could not read.
