# verifying-artifacts — Scoring (Program Runs + Judge Sampling)

## Context Contract

- **Inputs:** `VERIFY_INDEX.items[]` (all items, with `verifier_file` set for PROGRAM items), `ARTIFACT_TEXT`, `judge_samples`, `model`
- **Outputs:** per-item `score` (0-100) and `status: scored` in `VERIFY_INDEX`; the `judge_scoring` section body (and the score columns the `program_verifiers` and `anti_gaming` sections reference)
- **Carries Forward:** all per-item scores in `VERIFY_INDEX.items[]` — the input to aggregation
- **Flush After:** full program stdout and individual judge-sample transcripts — retain only the per-item final score + the one-line program verdict
- **Dependency:** Step 4 (Generate Program Verifiers) must be COMPLETE
- **H1 Title:** `# {project_name} -- Item Scoring`

## Mode-Specific Behavior

- **BUILD:** Score every item — run PROGRAM verifiers, sample JUDGE items.
- **REPAIR:** Re-score ONLY items named in a directive (e.g. a verifier was regenerated, or `judge_samples` changed). Preserve untargeted scores verbatim.
- **REVERIFY:** VGT-loop convergence re-score (see the SKILL.md "REVERIFY Mode" section). Re-run ALL PROGRAM verifiers (deterministic regression net — never skipped). Judge only the **convergence set** when `REVERIFY_SCOPE == "failed_items"`: every item that FAILED last lap + any item whose targeted artifact region changed (regression-suspect); CARRY FORWARD the prior JUDGE score for previously-passing, unchanged items (record their ids in `reverify_delta.carried_ids`, re-judged ids in `rejudged_ids`). The anti-gaming item is ALWAYS re-judged. When `REVERIFY_SCOPE == "full"`, re-judge every JUDGE item as in BUILD. Aggregation + verdict semantics are UNCHANGED; a **regression** (previously-passing item now failing) forces FAILED regardless of the weighted total. The verdict/findings MUST state the lap-over-lap delta from `reverify_delta`.
- **RESUME:** If `_progress.json.sections.judge_scoring == "complete"`, SKIP unless a directive targets scoring.

## Content Generation Instructions

Use structured fields (a score table keyed by item id), not prose, because aggregation
reads `score` and `weight` per row exactly.

### PROGRAM items — run the verifier, boolean → 0/100

```
FOR EACH item WHERE verifiability == PROGRAM:
  LOAD verifier_file path from VERIFY_INDEX (Pattern 5).
  RUN the verifier against the artifact (python3 verify-{id}.py {artifact_path}, or node ...).
  score = 100 IF exit code == 0 (PASS) ELSE 0 (FAIL).   ## boolean, deterministic
  Tool-output retention (§10.5.3): keep ONLY the one-line verdict + exit code. Do NOT
    paste full stdout into the report — the report cites the verdict line and the
    verifier_file path so a human can re-run it.
  IF no runtime (no python/node) available for this run:
    score = JUDGE fallback (sample as below) AND mark item.status = degraded;
    register the degradation in open_questions ("PROGRAM item {id} ran as JUDGE: no runtime").
  UPDATE VERIFY_INDEX.items[id].score, status = scored (or degraded).
  Do NOT stop. Process ALL PROGRAM items.
```

WHY boolean→0/100: a deterministic verifier is either satisfied or not. Mapping its
exit code straight to 0/100 keeps the weighted aggregation interpretable and gives the
C-cron-class item a hard, non-judge score.

### JUDGE items — mean-of-N (variance reduction, NOT entropy)

```
FOR EACH item WHERE verifiability == JUDGE:
  LOAD the item's question + ARTIFACT_TEXT (Pattern 5).
  Sample the judge `judge_samples` times (default 5) on this SINGLE yes/no question.
    Each sample returns a 0-100 confidence that the artifact PASSES this item.
    Samples should be independent reads of the same question against the artifact.
  score = MEAN of the samples.
  Bias rule (Entry Rule #5): if the samples are split, or the item cannot be answered
    from the artifact alone, bias the score DOWN — do NOT round up, do NOT auto-pass.
  UPDATE VERIFY_INDEX.items[id].score, status = scored.
  Do NOT stop. Process ALL JUDGE items.
```

**Explicitly NOT done here (forbidden):**
- NO entropy / agreement gating. Sample agreement measures *consensus*, not
  *correctness* — low entropy is exactly the confident-but-wrong failure mode. The mean
  is used ONLY to reduce sampling variance.
- NO SURE-style auto-approve: a high mean never *skips* a correctness/platform item; it
  only sets that item's score, which the human gate still reviews.
- NO model training. `judge_samples` is repeated inference, nothing is fit or stored.

WHY mean-of-N: a single judge read is noisy; the mean of N independent reads is a more
stable point estimate of the same yes/no, with no auto-approval semantics attached.

### Anti-gaming item

The single ANTIGAMING item is a JUDGE item — sample it the same way (mean-of-N) at
weight 100. A stub/hand-wave artifact scores low here regardless of per-criterion
scores, which is the point.

### Score sanity check

```
At the end of scoring, VERIFY:
  scored_items = count(items WHERE status IN {scored, degraded})
  IF scored_items != total_items → some item was missed; complete it before aggregation.
  Every score is an integer/float in 0-100.
LOG: "Scoring complete. {N}/{total} items scored, {D} degraded."
```

## Source Fidelity Check (before writing)

- [ ] Every PROGRAM item ran its verifier (or is marked `degraded` with an open_questions entry) — no PROGRAM score is a judge guess unless degraded
- [ ] Every JUDGE item is a mean of exactly `judge_samples` samples
- [ ] No entropy/agreement value was used to gate or skip any item
- [ ] Split/unanswerable items biased DOWN, not up
- [ ] All scores in 0-100; `scored_items == total_items`
- [ ] Full program stdout / per-sample transcripts flushed; only final scores + verdict lines retained

## Post-Section Protocol

1. **Write** the `judge_scoring` section (and fill the score columns referenced by `program_verifiers` / `anti_gaming`) into the report via targeted `Edit` calls. Mandatory. Do NOT defer.
2. **Update** `VERIFY_INDEX`: per-item `score`, `status`, `scored_items`.
3. **Update** progress tracker: `_progress.json.sections.judge_scoring` → `"complete"`.
4. **Save** `VERIFY_INDEX` to `_progress.json`.
5. **Flush** program stdout and judge-sample transcripts from memory. Retain only `VERIFY_INDEX`.
6. **Verify** the report sections are written and every item has a score.
7. **Log:** "Scoring complete. {N} scored, {D} degraded."
