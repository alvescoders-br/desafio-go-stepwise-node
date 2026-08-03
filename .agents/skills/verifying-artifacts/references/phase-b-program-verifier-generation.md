# verifying-artifacts — Program Verifier Generation

## Context Contract

- **Inputs:** `VERIFY_INDEX.items[]` (only items where `verifiability == PROGRAM`), `ARTIFACT_TEXT` fragments those items target
- **Outputs:** one self-contained verifier program per PROGRAM item at `{output_path}/verifiers/verify-{id}.py` or `.js`; updated `VERIFY_INDEX.items[id].verifier_file`; the `program_verifiers` section body of the report
- **Carries Forward:** `verifier_file` paths recorded in `VERIFY_INDEX`; any item demoted PROGRAM→JUDGE
- **Flush After:** each generated program's source text — written immediately, then dropped (one in-flight program at a time)
- **Dependency:** Step 3 (Generate Checklist) must be COMPLETE
- **H1 Title:** `# {project_name} -- Program Verifiers`

## Mode-Specific Behavior

- **BUILD:** Generate a verifier for each PROGRAM item that passes the 100%-sure gate.
- **REPAIR:** Load existing verifiers from the SAME `verifiers/` folder. Regenerate ONLY verifiers whose item id is named in a directive. Preserve untargeted verifier files verbatim. Rewrite in place at the same path.
- **RESUME:** If `_progress.json.sections.program_verifiers == "complete"`, SKIP. Re-author only on a targeting directive.

## Content Generation Instructions

### The RLCF Figure 6 gate (the one rule that keeps this honest)

```
FOR EACH item WHERE verifiability == PROGRAM:
  LOAD the item's question + the exact ARTIFACT_TEXT fragment it targets (Pattern 5).

  Ask: am I 100% sure a small deterministic program checks this criterion EXACTLY?
    - EXACTLY = syntax / format / presence / absence — no judgement, no platform fact.
    - YES (rare, ~5% of items) → generate the verifier (template below).
    - NO  (default, ~95%)      → DEMOTE to verifiability = JUDGE. Do not generate.

  Generate a "probably right" program is WORSE than deferring: it stamps false
  certainty on a semantic call. When in doubt, defer (Principle #6 / Entry Rule #5).
```

Use explanation over prohibition: the gate exists because a verifier program's output
is taken as ground truth (boolean → 0/100). A wrong program silently inverts a correct
judgement. Deferring to a judge sample, which the report shows as a mean with
uncertainty, is recoverable; a confidently-wrong program is not.

### What PASSES the gate (generate a verifier)

| Criterion class | Verifier checks | Example |
|-----------------|-----------------|---------|
| cron-syntax | each field is within its legal range (minute 0-59, hour 0-23, ...) and step values do not exceed the field range | `*/100 * * * *` → minute step 100 > 59 → FAIL |
| package existence | a named package appears (or is absent) in a manifest's dependency map | "dependency X absent from package.json" |
| string/literal presence | a required literal/route/header is present, or a forbidden one is absent | "no `process.env` read outside the auth module" |
| format/shape | a value matches an exact regex/format the spec fixes | a required id format, a fixed file path |

### What FAILS the gate (demote to JUDGE)

- Anything needing a platform fact to decide ("does setTimeout fire on Vercel") —
  that truth came from discovery; this skill does not own it.
- Anything semantic ("is the persistence choice viable", "is the design coherent").
- Anything requiring judgement about intent or completeness.

### Self-contained verifier template (stdlib only)

```
FOR EACH item that PASSES the gate:
  Generate a program that:
    1. Reads its input from the artifact: either a path argument to artifact_path, or the
       exact fragment inlined as a constant (prefer reading the artifact so a human can
       re-run it). STDLIB ONLY — no pip/npm install, no network.
    2. Performs the exact check deterministically.
    3. Prints ONE line: "PASS: {criterion}" or "FAIL: {criterion} -- {reason}".
    4. Exits 0 on PASS, non-zero on FAIL.
  Keep it short and readable — the human gate reads this code.
```

Reference cron-verifier shape (illustrative — generate per the actual finding):
```python
#!/usr/bin/env python3
# verify-CHK-0XX.py — cron field-range check for the OAuth refresh schedule.
import re, sys
EXPR = "*/100 * * * *"   # or read from artifact_path
RANGES = [(0,59),(0,23),(1,31),(1,12),(0,6)]
def field_ok(f, lo, hi):
    for part in f.split(","):
        m = re.fullmatch(r"\*(?:/(\d+))?", part)
        if m:
            step = int(m.group(1) or 1)
            if step < 1 or step > hi: return False   # step must fit the field range
            continue
        m = re.fullmatch(r"(\d+)(?:-(\d+))?(?:/(\d+))?", part)
        if not m: return False
        a = int(m.group(1)); b = int(m.group(2) or a)
        if a < lo or b > hi or a > b: return False
    return True
fields = EXPR.split()
ok = len(fields) == 5 and all(field_ok(f, lo, hi) for f, (lo, hi) in zip(fields, RANGES))
print(("PASS" if ok else "FAIL") + f": cron '{EXPR}'" + ("" if ok else " -- minute step 100 exceeds field range 0-59"))
sys.exit(0 if ok else 1)
```
For `*/100 * * * *` this returns FAIL (exit 1) deterministically — that is the C-cron
ground-truth case. For a valid `*/30 * * * *` it returns PASS (exit 0). The verdict is
NOT a judge guess: the cron item's `verifiability` is PROGRAM and the program runs.

### Per-item write loop

```
FOR EACH PROGRAM item that passed the gate:
  Pre-write fidelity check (Pattern 6):
    - reads from artifact or an inlined fragment, not a hallucinated value
    - stdlib only, deterministic, no network/install
    - exit 0 = PASS, non-zero = FAIL; one-line verdict printed
    - does NOT hardcode a platform fact to decide (if it would → demote to JUDGE now)
  WRITE {output_path}/verifiers/verify-{id}.py|.js — MANDATORY TOOL CALL. Do NOT defer.
  UPDATE VERIFY_INDEX.items[id].verifier_file.
  FLUSH the program source from memory.
  LOG: "{id} verifier written."
  Do NOT stop. Process ALL PROGRAM items.
```

## Source Fidelity Check (before writing)

- [ ] Every generated verifier is stdlib-only, deterministic, no network/install
- [ ] Every verifier reads from the artifact (or an inlined exact fragment), not an invented value
- [ ] No verifier hardcodes a platform fact to reach its verdict
- [ ] Every PROGRAM item either has a verifier_file on disk OR was demoted to JUDGE (no PROGRAM item left without a program)
- [ ] Demotions PROGRAM→JUDGE are recorded in `VERIFY_INDEX.items` and noted in open_questions
- [ ] Verifier file count == count of PROGRAM items that passed the gate

## Post-Section Protocol

1. **Write** each `{output_path}/verifiers/verify-{id}.{ext}` (mandatory) and then the report's `program_verifiers` section via one `Edit`. Do NOT defer.
2. **Update** `VERIFY_INDEX`: `items[id].verifier_file` for each generated program; record demotions.
3. **Update** progress tracker: `_progress.json.sections.program_verifiers` → `"complete"`.
4. **Save** `VERIFY_INDEX` to `_progress.json`.
5. **Flush** all program source text from memory. Retain only `VERIFY_INDEX`.
6. **Verify** each `verifier_file` exists and is non-empty; the report section is written.
7. **Log:** "Program verifiers complete. {N} generated, {M} demoted to JUDGE."
