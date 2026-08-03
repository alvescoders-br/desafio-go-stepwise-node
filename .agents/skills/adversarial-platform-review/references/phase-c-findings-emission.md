# Adversarial Platform Review — Findings Emission

## Context Contract

- **Inputs:** `REVIEW_INDEX.decisions[]` (from Phase B: each with verdict, severity, source_url, claim, quote).
- **Outputs:** `{output_path}/CONFORMANCE-FINDINGS-{SESSION_ID}.json` — a JSON list of finding objects (the frozen contract).
- **Carries Forward:** `REVIEW_INDEX.blocker_count`; the findings file path.
- **Flush After:** Nothing large loaded this phase; the findings list is assembled from `REVIEW_INDEX` fields already in memory.
- **Dependency:** Phase B must be COMPLETE (every decision has a grounded verdict or is registered as UNCONFIRMED/pending).
- **H1 Title:** N/A — this phase writes a JSON file, not a Markdown spec.

## Mode-Specific Behavior

- **BUILD:** Assemble the findings list from scratch over all VIOLATION/UNCONFIRMED decisions.
- **REPAIR:** Re-emit the findings file from the current `REVIEW_INDEX` (which already reflects any repaired decisions). Preserve the SESSION_ID in the filename (reuse, do not regenerate). Rewrite the file IN PLACE.
- **RESUME:** Only run once all decisions are verified; if re-entered after a partial verification, finish Phase B first, then emit.

## Content Generation Instructions

This file is the **HARD CONTRACT** consumed by the sibling skill
`verifying-artifacts`, which inverts each finding into one pass-condition checklist
item and weights it by `severity`. The field names are FROZEN. Do NOT rename, add,
or drop fields — a rename silently breaks the downstream handoff (the consumer reads
fields by exact key).

GENERATE the findings list:

1. **Select findings.** Include one object PER decision whose `verdict` is `VIOLATION`
   or `UNCONFIRMED`. CONFORMS decisions are NOT findings — they appear only in the
   review/audit (a findings list is a list of problems, not a list of all decisions).

2. **Emit each finding as EXACTLY these six keys** (this exact shape is the contract):

   ```json
   {
     "decision":         "<the load-bearing decision, restated>",
     "claim":            "<the assumption the artifact baked in>",
     "platform_reality": "<what the live source says actually happens on the target>",
     "severity":         "BLOCKER",
     "fix":              "<the minimal conforming change>",
     "source_url":       "https://<the live source cited for this verdict>"
   }
   ```

   - `decision` — restate the load-bearing decision (carry from `REVIEW_INDEX`).
   - `claim` — the assumption the artifact baked in (carry from Phase A).
   - `platform_reality` — what the cited source says actually happens on
     `target_platform`. This is the refutation, grounded — not a guess.
   - `severity` — MUST be one of `BLOCKER`, `RISK`, `MINOR` (from Phase B).
   - `fix` — the minimal conforming change (the smallest edit that makes the decision
     hold on the target). Keep it concrete and minimal; do not redesign the system.
   - `source_url` — the live URL consulted this run. A finding with a blank/invented
     `source_url` is INVALID — re-ground it in Phase B or drop it. Never ship a blank source.

3. **The file is a JSON array** of these objects (top-level `[ {...}, {...} ]`), even
   when there is exactly one finding. An empty array (zero findings) is valid and
   means every decision conformed.

4. **Write via the Write tool** (whole-file create). NEVER mutate the JSON via shell
   (`sed`/`awk`/`python3 <<EOF`/`cat >`) — per execution-protocol.md §10.5, structured
   output files are written with Write/Edit only, never bulk shell rewrites.

### Count verification

```
stated_blocker_count = REVIEW_INDEX.blocker_count
actual_blocker_count = count of findings where severity == "BLOCKER"
IF mismatch → fix REVIEW_INDEX.blocker_count before writing the audit.
LOG: "Fixed blocker_count: stated {N}, actual {M}".
```

## Source Fidelity Check (before writing)

- [ ] Every finding object has EXACTLY the six keys: decision, claim, platform_reality, severity, fix, source_url — no extra, none missing, none renamed.
- [ ] `severity` is one of BLOCKER, RISK, MINOR (no other value).
- [ ] Every `source_url` is a real URL consulted this run AND topically about its finding's claim — no blanks, no invented URLs, no "from memory", no real-but-off-topic page (an off-topic source counts as no source).
- [ ] No finding restates a choice the artifact defers AND gates downstream work on — those belong in `open_questions`. (An UNGATED deferral is NOT parked; it remains a VIOLATION/UNCONFIRMED finding.)
- [ ] `platform_reality` describes what the cited source says (grounded), not a guessed fact.
- [ ] Only VIOLATION/UNCONFIRMED decisions appear; no CONFORMS decision leaked in as a finding.
- [ ] The top-level structure is a JSON list (array), valid JSON, parseable.

## Post-Section Protocol

1. **Write** `{output_path}/CONFORMANCE-FINDINGS-{SESSION_ID}.json`. Mandatory tool call (Write, not shell). Do NOT defer.
2. **Update** `REVIEW_INDEX`: `blocker_count` = count of BLOCKER findings.
3. **Update** progress tracker: note "findings emitted ({N})" in the review header.
4. **Save** `REVIEW_INDEX` to `_progress.json`.
5. **Flush** the assembled findings text from memory. Retain only `REVIEW_INDEX`.
6. **Verify** the file exists, is valid JSON, and every object has exactly the six contract keys.
7. **Log:** "Phase C COMPLETE. {N} findings written ({B} BLOCKER, {R} RISK, {M} MINOR)."
