# REPAIR Mode

Read this reference at Phase A **only when** `failure_feedback` is non-empty. In STANDARD mode (no failure_feedback), this file does not apply — skip it.

REPAIR mode replaces the normal Phase B "implement everything" loop with a surgical-fix loop driven by the rejection feedback from a previous run.

REPAIR has three triggers:

| Trigger | Source | Reference |
|---------|--------|-----------|
| Phase C verification failure | `failure_feedback` references a build/test failure | This file (rest of document) |
| Human rejection at quality gate | `failure_feedback` references a REVIEW-SPEC | This file (rest of document) |
| **Integrity break** during Phase B | A file the agent wrote in this run is now wiped, truncated, or unreadable | `references/recovery-protocol.md` (read it first), then this file |

The integrity-break trigger is mid-session and does NOT come from `failure_feedback`. It is detected by the Phase B integrity self-check (file size collapsed, diff --stat shows full replacement, or an Edit tool returned success but the file is now empty). When it fires, do NOT call `exec-fail` immediately — first execute the protocol in `references/recovery-protocol.md`. Only fall through to fail-fast if recovery is impossible (no git baseline AND no IMPL-STATE record).

---

## MANDATORY FIRST STEP — Build Cumulative Rejection Checklist

Before touching any code, execute this sequence:

0. **Resolve the authoritative repair report before touching code.** If
   `failure_feedback` references `VALIDATION_REPORT.md`, `REVIEW-SPEC-*.md`, or
   `REVIEW-AUDIT-*.md`, read that file IN FULL before anything else. If
   `failure_feedback` is generic human text with no structured finding rows
   (for example "there are some fails to fix"), locate the latest
   `VALIDATION_REPORT.md` from `review_output_path`, the sibling
   `code-review-output` folder, or the capability `output_folder`, in that
   order. Build the rejection checklist below from the report's blocking/high
   findings, not from the summary alone. If no report can be found, fall back to
   `failure_feedback` content and log `repair_feedback_source:
   generic_text_no_report` in `repair_log[current].notes`.

1. Read the current normalized feedback/report in full.

2. Read the IMPL-STATE `repair_log` entries to retrieve ALL prior rejection reasons in order.

3. Build a numbered REJECTION CHECKLIST combining ALL rejections (prior + current):
   ```
   REJECTION CHECKLIST (built before repair begins):
   #1: {description from rejection 1} — STATUS: {RESOLVED ✓ / NOT RESOLVED}
   #2: {description from rejection 2} — STATUS: {RESOLVED ✓ / NOT RESOLVED}
   ...
   #N: {description from current rejection} — STATUS: NOT RESOLVED
   ```

4. For each item marked RESOLVED ✓ in prior repair logs, confirm it is still passing
   by running the relevant verification command. If it regressed, update status to "REGRESSED".

5. DO NOT begin code changes until the checklist is complete and persisted to IMPL-STATE
   under `repair_log[current].rejection_checklist`.

6. DO NOT submit for validation until ALL items on the checklist show RESOLVED ✓.

This checklist complements the pre-repair baseline + 3-way failure classification below
(baseline / fallout / regression). The checklist tracks WHAT must be fixed across the
full repair history; the baseline tracks the test-suite delta of THIS repair iteration.
Both are required.

---

## REPAIR Mechanics

Follow execution-protocol.md Section 7 for REPAIR mechanics. After building the checklist:

1. Load existing IMPL-STATE — do NOT reset progress
2. Parse failure_feedback → identify affected phases/files
3. Apply targeted fixes to flagged sections only
4. Re-run Phase C verification for repaired files
5. REGRESSION CHECK: Execute the project's full verification command (test suite, build, lint).
   Confirm pass before reporting completion. IF verification fails on NON-TARGETED files,
   treat as a repair regression — log in repair_delta as "regression" and escalate.
   Do NOT attempt to fix regressions silently — they indicate the repair touched
   shared state or adjacent code.
6. Produce repair_delta: fixed / still_failing / regressions
7. Append repair_log entry to IMPL-STATE (including the rejection_checklist with final statuses)

Sections not mentioned in feedback are unchanged.

---

## REPAIR Mode — Full Test Suite Verification

Before applying any listed repair, capture a full-suite baseline and record it in IMPL-STATE:
- Test command used (from context-pack `validation-tools.md` or detected from package.json / build tool)
- Timestamp / commit reference (if available)
- Pass/fail counts
- List of failing tests and error messages

After applying all listed repairs, ALWAYS run the full test suite:

1. Execute the project's configured test command again (from context-pack `validation-tools.md` or detected from package.json / build tool).
2. Compare results against the recorded pre-repair baseline in IMPL-STATE.
3. Confirm that the targeted failures are resolved and classify any remaining failures as one of:
   - **Pre-existing baseline failures:** present before the repair and still present after it.
   - **Direct repair fallout:** newly exposed/introduced by the targeted repair and clearly in the same code path.
   - **Unrelated new regressions:** not present in the baseline and not clearly caused by the targeted repair.

If failures remain beyond the listed repairs:
- **If the fix is trivial (1-5 lines) AND it resolves either a pre-existing baseline failure or direct repair fallout:** Apply it. Document it explicitly as a "bonus fix" in the repair summary.
- **If the failure is an unrelated new regression, or the fix requires understanding new code:** Do NOT fix silently. Instead:
  1. List the residual failures in a `## Residual Blockers` section in the repair summary.
  2. For each blocker: filename, test name, error message, whether it is baseline/fallout/regression, and suspected fix.
  3. **Fail the step** — do NOT mark repair as complete with known unrelated regressions or other known failures requiring non-trivial work.

Completing a repair step with known test failures wastes the next cycle detecting them again.
