# Adversarial Platform Review — Verdict, Audit & Harness Sidecar

## Context Contract

- **Inputs:** `REVIEW_INDEX` (from Phase C: decisions[] with verdicts, blocker_count, findings file written); the prompt's `## Run metadata` and `## Output parameters` blocks (if Stepwise-invoked).
- **Outputs:** `{output_path}/CONFORMANCE-AUDIT-{SESSION_ID}.md`; updated `CONFORMANCE-REVIEW-{SESSION_ID}.md` header; `_progress.json` flipped to COMPLETED; the harness outputs sidecar JSON (§11).
- **Carries Forward:** Nothing — this is the final phase. All outputs are on disk.
- **Flush After:** All remaining context after the sidecar write. Session complete.
- **Dependency:** Phase C must be COMPLETE (findings JSON written and validated).
- **H1 Title:** `# {project_name} -- Conformance Audit`

## Mode-Specific Behavior

- **BUILD:** Compute the verdict, write the audit, update Memory Bank, emit the sidecar.
- **REPAIR:** Recompute the verdict from the current `REVIEW_INDEX` (reflects repaired decisions). Append a `## Repair History` entry to the audit (directives_applied, decisions_changed, decisions_preserved); bump the review's `version` (semver patch). Re-emit the sidecar with the updated verdict/count. Do NOT overwrite the full audit history — append.
- **RESUME:** Run only after all phases complete; if re-entered, finish earlier phases first.

## Content Generation Instructions

### 1. Compute the conformance verdict (closed set)

```
IF any finding has severity == BLOCKER:        conformance_verdict = VIOLATIONS_FOUND
ELSE IF any finding exists (RISK or MINOR):    conformance_verdict = CONFORMS_WITH_RISKS
ELSE (zero findings):                          conformance_verdict = CONFORMS
```

Bias rule: an `UNCONFIRMED` decision is a VIOLATION (default-to-VIOLATION). NEVER
return `CONFORMS` when any decision lacks a positively-confirming source — that is
precisely the confident-but-wrong pass this skill exists to prevent. If every
decision conformed but one is UNCONFIRMED, the verdict is at least VIOLATIONS_FOUND
(if the UNCONFIRMED item is BLOCKER-severity) or CONFORMS_WITH_RISKS.

**Surface parked open questions.** The `open_questions` section lists two distinct kinds
of entry: (i) **gated self-deferred** choices the artifact owns and blocks downstream work
on — these legitimately do NOT drive the verdict; and (ii) **ungroundable-UNCONFIRMED**
decisions (a web call failed / returned nothing) — these are VIOLATIONs counted under
findings, listed here only for traceability. `open_questions_count` counts **(i) gated
self-deferred entries ONLY**, so the integer means exactly one thing: how many
artifact-owned, gated platform questions remain open. (In a CONFORMS verdict no
ungroundable-UNCONFIRMED entry can exist anyway — it would be a VIOLATION — but scoping the
count keeps it unambiguous under every verdict.) A clean `CONFORMS` with parked questions
must not read identically to a `CONFORMS` with none: always report `open_questions_count`
alongside the verdict in the audit header and the living-tracker header, so the human gate
sees that unresolved-but-gated platform questions exist. (Keep it in those human-facing
artifacts — do NOT add it to the harness sidecar, which emits only the declared output
parameters.) (Reminder: only GATED deferrals are parked here; an ungated "TBD, proceeding
anyway" is an extracted decision → UNCONFIRMED → VIOLATION, never a parked question.)

### 2. Verify counts before writing

```
VERIFY: blocker_count == number of BLOCKER findings in CONFORMANCE-FINDINGS-{SESSION_ID}.json
VERIFY: total findings == count of VIOLATION + UNCONFIRMED decisions
IF mismatch → fix before writing the audit. LOG the correction.
```

### 3. Write the audit

`CONFORMANCE-AUDIT-{SESSION_ID}.md` contains (structured fields, not prose, so the
provenance chain `artifact_decision -> live_source -> verdict` is machine-traceable):

```
# {project_name} -- Conformance Audit
session: {SESSION_ID}
target_platform: {target_platform}
artifact: {artifact_path}
conformance_verdict: {verdict}
blocker_count: {N}
open_questions_count: {Q}
decisions_total: {total}    findings_total: {F}

## Decisions by category
| category | extracted | conforms | violations |
...

## Per-decision verdict table
| ID | category | verdict | severity | source_url |
| DEC-01 | scheduling | VIOLATION | BLOCKER | https://... |
...

## Sources consulted
- https://...  (DEC-01)
- https://...  (DEC-02)

## open_questions
- {any ungroundable decision: id, why it could not be grounded, treated as VIOLATION}
```

### 4. Update the living tracker header

Set `conformance_verdict`, `blocker_count`, `completed/total` in the
`CONFORMANCE-REVIEW-{SESSION_ID}.md` header. Mandatory tool call.

### 5. Memory Bank (session-end writes)

- Overwrite `context-pack/active-context.md` with session status, the verdict,
  blocker_count, and the findings file path.
- Append one milestone row to `context-pack/progress.md` with the finding count
  (e.g. "4 conformance-findings").

### 6. LAST ACTION — flip `_progress.json` to COMPLETED

Update `_progress.json`: `status: COMPLETED`, `completed == total`, `completed_at` set.

### 7. Emit the Harness Outputs Sidecar (FINAL write)

**Apply execution-protocol.md §11.** Mandatory when the prompt contains a
`## Run metadata` block (Stepwise invocation); skip for standalone runs.

Output parameters this skill produces (one key per row of the prompt's
`## Output parameters` table):
- `conformance_verdict` — `CONFORMS` | `CONFORMS_WITH_RISKS` | `VIOLATIONS_FOUND`.
- `conformance_findings_path` — absolute path to `CONFORMANCE-FINDINGS-{SESSION_ID}.json`.
- `blocker_count` — integer count of BLOCKER findings.

(`open_questions_count` is surfaced in the audit + living-tracker headers, NOT here — the
sidecar carries only declared output parameters.)

Example sidecar contents (values illustrative):

```json
{ "conformance_verdict": "VIOLATIONS_FOUND",
  "conformance_findings_path": "/abs/output/CONFORMANCE-FINDINGS-{SESSION_ID}.json",
  "blocker_count": 4 }
```

**Path Verification Before Write (§11.1.1):** confirm
`CONFORMANCE-FINDINGS-{SESSION_ID}.json` exists at the path you report; report the
ACTUAL on-disk path you wrote to — never a re-derived input parameter or scope-adjusted
path. Reporting an unwritten path is the documented cause of the duplicate-artifact-on-
REPAIR defect.

**Strict ordering (§11.4):** all skill outputs written → Memory Bank writes →
`_progress.json` flipped to COMPLETED → sidecar write (this step) → `final_response`.
NO tool calls after the sidecar write.

## Source Fidelity Check (before writing)

- [ ] `conformance_verdict` is one of CONFORMS, CONFORMS_WITH_RISKS, VIOLATIONS_FOUND — and consistent with the findings (BLOCKER present ⇒ VIOLATIONS_FOUND).
- [ ] No `CONFORMS` verdict when any decision is UNCONFIRMED/pending.
- [ ] `blocker_count` matches the count of BLOCKER findings in the JSON.
- [ ] `conformance_findings_path` points to a file that actually exists on disk.
- [ ] open_questions lists every ungroundable decision (none silently dropped).
- [ ] `open_questions_count` counts gated self-deferred entries ONLY (not ungroundable-UNCONFIRMED ones), and is reported in the audit header and living-tracker header (not the sidecar), even when zero, so a CONFORMS with parked questions is distinguishable from one without.

## Post-Section Protocol

1. **Write** `{output_path}/CONFORMANCE-AUDIT-{SESSION_ID}.md`. Mandatory tool call.
2. **Update** `REVIEW_INDEX`: `conformance_verdict`, `blocker_count` (final).
3. **Update** progress tracker header: verdict + blocker_count + completed/total.
4. **Save** `_progress.json` flipped to COMPLETED (LAST ACTION before sidecar).
5. **Flush** all remaining context after the sidecar write. Session complete.
6. **Verify** audit, review, findings JSON, and the sidecar all exist on disk.
7. **Log:** "Phase D COMPLETE. Verdict: {conformance_verdict}. Blockers: {blocker_count}. Sidecar written. Session {SESSION_ID} done."
