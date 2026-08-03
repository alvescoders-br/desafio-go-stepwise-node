# verifying-artifacts — Report Assembly, Aggregation & Verdict

## Context Contract

- **Inputs:** `VERIFY_INDEX` (all items scored), the report skeleton on disk, `VERIFY_INDEX.conformance_present`
- **Outputs:** the populated `aggregation`, `verdict`, `findings`, and `open_questions` sections of `VERIFICATION-REPORT-{SESSION_ID}.md`; `VERIFICATION-AUDIT-{SESSION_ID}.md`; final `VERIFY_INDEX.verification_verdict`, `weighted_total`, `failed_blocker_count`
- **Carries Forward:** the closed-set verdict + counts → consumed by the Step 8 harness sidecar
- **Flush After:** all loaded section bodies after each `Edit` — one in-flight section at a time
- **Dependency:** Step 5 (Scoring) must be COMPLETE (every item scored)
- **H1 Title:** `# {project_name} -- Verification Report`

## Mode-Specific Behavior

- **REPAIR:** Load the existing report from the SAME path. Apply ONLY directives targeting `aggregation`/`verdict`/`findings`. Recompute the verdict from the current `VERIFY_INDEX.items[]` scores (a re-scored item changes the total). Preserve untargeted sections verbatim. Rewrite IN PLACE. Bump the report `version` (semver patch) and append a `## Repair History` entry to the audit (directives_applied, sections_changed, sections_preserved) per execution-protocol.md §7.
- **BUILD:** Generate all four closing sections from scratch.
- **RESUME:** If `_progress.json.sections.verdict == "complete"`, the verdict is already authored — SKIP unless a directive targets it.

## Content Generation Instructions

### Report section structure (section-shape; template order)

The report is generated skeleton-first (execution-protocol.md §10 Phase A) then one
section per `Edit` (Phase B). Sections, in template order:

1. `run_metadata` — session, version, date, mode, language; inputs (artifact_path,
   output_spec_source, conformance_findings_path present/absent, judge_samples, model);
   `reduced_coverage: {true|false}`.
2. `checklist` — the full item table: `| id | question | source | source_url | weight | verifiability |` (authored in phase-a).
3. `program_verifiers` — for each PROGRAM item: id, verifier_file path, the one-line verdict, PASS/FAIL, the embedded generated program (by reference to verifiers/). Demoted items noted.
4. `judge_scoring` — for each JUDGE item: id, judge_samples, the per-sample scores summary, the MEAN score (authored in phase-c).
5. `anti_gaming` — the single ANTIGAMING item, its mean score, weight 100.
6. `aggregation` — the weighted-total computation (formula below), per-item `score*weight` contributions, the count check.
7. `verdict` — the closed-set `verification_verdict` + the mapping that produced it + `failed_blocker_count`.
8. `findings` — failed items (score < 50), grouped by source; each CONFORMANCE failure cites its `source_url`; the `reduced_coverage` note when applicable.
9. `open_questions` — ALWAYS LAST: degradations, malformed findings, missing criteria, any item that could not be scored confidently.

Use structured fields throughout — the human gate and any downstream consumer read
`verification_verdict`, `failed_blocker_count`, and the failed-item rows programmatically.

### Aggregation formula (the `aggregation` section)

```
weighted_total = round( sum(item.score * item.weight) / sum(item.weight) )   ## 0-100, weighted mean
failed_blocker_count = count(items WHERE weight == 100 AND score < 50)
```
Weight-100 items are the blockers: every CONFORMANCE BLOCKER finding (weight 100) and
the ANTIGAMING item (weight 100). A blocker scoring below 50 fails the whole verdict —
this is the bias-toward-FAILED rule made arithmetic (Entry Rule #5).

Count verification before writing:
```
stated_item_count = rows in the checklist table
actual_item_count = count(VERIFY_INDEX.items)
IF mismatch → fix the stated count before writing the aggregation section.
LOG: "Aggregation: weighted_total {W}, failed_blockers {B}, items {N}."
```

### Verdict mapping (the `verdict` section)

```
verification_verdict =
  FAILED                 IF failed_blocker_count > 0  OR  weighted_total < 60
  PASSED_WITH_FINDINGS   IF failed_blocker_count == 0  AND 60 <= weighted_total < 85
  PASSED                 IF failed_blocker_count == 0  AND weighted_total >= 85
```
`verification_verdict` is a closed-set output: values: [PASSED, PASSED_WITH_FINDINGS,
FAILED] (UPPER_SNAKE). Record `failed_blocker_count` (integer, no values:).

**What the verdict certifies (scope statement — emit verbatim in the `verdict` section).**
A PASSED verdict certifies **structural / traceability conformance** (the artifact meets
its spec criteria) **plus external-platform conformance** (the consumed discovery
findings). It does **NOT** certify the artifact's **internal design soundness** — whether
the choices it makes are good ones for the problem. The single ANTIGAMING item guards
against hollowness (stub / hand-wave), not against a well-formed but questionable design.
Design-quality judgment remains the downstream `human-quality-gate`'s responsibility; a
PASSED must not be read as short-circuiting it.

### Findings section

- List every item with score < 50 as a finding, grouped by `source` (SPEC / CONFORMANCE / ANTIGAMING).
- For each CONFORMANCE finding, cite the carried `source_url` so the human can trace it to the discovery source.
- When `VERIFY_INDEX.conformance_present == false`, state `reduced_coverage: true` and:
  "Checklist is spec-items-only; no discovery step supplied platform-reality findings,
  so this verdict is BLIND to platform reality items by construction."

### Audit file

Write `VERIFICATION-AUDIT-{SESSION_ID}.md`:
```
# {project_name} -- Verification Audit Trail
version: {NEW_VERSION}
session: {SESSION_ID}
mode: {BUILD | REPAIR}
date: {ISO 8601}
language: {DETECTED_LANGUAGE}
conformance_present: {true | false}

## inputs
artifact_path / output_spec_source / conformance_findings_path (loaded|absent) / judge_samples / model

## checklist_summary
total {N} | SPEC {a} | CONFORMANCE {b} | ANTIGAMING 1 | PROGRAM {p} | JUDGE {j}

## verifier_index
| item id | verifier_file | PASS/FAIL |

## aggregation
weighted_total {W} | failed_blocker_count {B} | verification_verdict {V}

## repair_changes (REPAIR mode only)
| directive | target | outcome |
```

## Source Fidelity Check (before writing)

- [ ] weighted_total recomputed from current `VERIFY_INDEX.items[]` scores (not stale / from memory)
- [ ] failed_blocker_count counts weight-100 items scoring < 50 — no other definition
- [ ] verdict matches the mapping exactly (FAILED when any blocker failed, regardless of total)
- [ ] every failed item appears in `findings`; CONFORMANCE failures cite `source_url`
- [ ] `reduced_coverage: true` present iff `conformance_present == false`
- [ ] stated item counts match actual `VERIFY_INDEX.items`
- [ ] REPAIR: report `version` bumped + `## Repair History` appended (per §7)

## Post-Section Protocol

1. **Write** the `aggregation`, `verdict`, `findings`, `open_questions` sections into `{output_path}/VERIFICATION-REPORT-{SESSION_ID}.md` via targeted `Edit` calls, then write `{output_path}/VERIFICATION-AUDIT-{SESSION_ID}.md`. Mandatory. Do NOT defer.
2. **Update** `VERIFY_INDEX`: `weighted_total`, `failed_blocker_count`, `verification_verdict`.
3. **Update** progress tracker: `_progress.json.sections.aggregation/verdict/findings/open_questions` → `"complete"`.
4. **Save** `VERIFY_INDEX` to `_progress.json`.
5. **Flush** all section bodies from memory. Retain only `VERIFY_INDEX` (verdict + counts) for the Step 8 sidecar.
6. **Verify** REPORT and AUDIT exist at `{output_path}` and are non-empty; verdict populated.
7. **Log:** "Report complete. verdict {V}, weighted_total {W}, failed_blockers {B}."
