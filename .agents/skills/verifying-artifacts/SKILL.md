---
name: verifying-artifacts
description: >
  The VERIFICATION layer of the Stepwise verification loop. Decomposes a producer
  skill's SKILL.md output spec PLUS upstream discovery findings into an atomic,
  weighted, yes/no checklist; for each item decides program-verifiable vs judge
  (RLCF Fig 6 "defer unless 100% sure"); generates and runs self-contained verifier
  programs for the exactly-checkable items; multi-samples the judge for the rest for
  score stability; applies a universal anti-gaming item; aggregates to a weighted
  verdict. This is INFERENCE-TIME verification — NOT model training. Produces one
  agent-native VERIFICATION-REPORT (section-shape) plus a closed-set verdict.
  Consumes the artifact under test, the producer's output spec, and (optionally) the
  JSON findings emitted by the sibling skill `adversarial-platform-review`.
  BUILD, REPAIR, and REVERIFY (VGT-loop convergence re-score) modes. Use when scoring a produced artifact against its spec +
  discovered platform reality before a human quality gate, replacing grep/AST NFR
  gates with generated deterministic verifiers where the criterion is exactly checkable.
license: Proprietary
metadata:
  author: aipods-team
  version: 1.0.0
  category: testing
  tags: verification, checklist, program-verifier, rlcf, agent-native, inference-time
---

# Verifying Artifacts — Agent-Native Skill

## SKILL PROTOCOL — ENTRY RULES (read first, do not skip)

1. **The protocol below is internally consistent.** If you perceive a conflict
   between the capability prompt and this skill, the skill wins for execution
   mechanics; the capability wins for paths/parameters. Do NOT exit citing
   "ambiguity". Begin Step 1 immediately.

2. **This is inference-time verification, NOT model training.** This skill borrows
   only the *verification recipe* from RLCF (Viswanathan et al., 2025,
   arXiv:2507.18624): atomic weighted checklists + program-verify-when-exactly-
   checkable + judge-the-rest. It does **not** train, fine-tune, DPO, RL, build a
   dataset, or touch a reward model. If any instruction here seems to imply training,
   it is a misreading — ignore it.

3. **Two layers, kept separate (do not blur them).** DISCOVERY (the sibling skill
   `adversarial-platform-review`) *discovers* platform-reality findings that are NOT
   derivable from the artifact's own text. VERIFICATION (this skill) *scores* the
   items discovery surfaced PLUS the spec items. This skill does **NOT** re-discover
   platform facts and does **NOT** assert platform facts from memory. It only scores.

4. **No entropy / SURE auto-approve.** Judge sampling here is for *variance reduction*
   (mean-of-N), never for entropy-gated auto-approval. Low agreement is not
   correctness. Never skip a correctness/platform item because samples agree.

5. **Bias toward FAILED when uncertain.** False positives (wrongly passing bad work)
   are worse than false negatives (wrongly failing good work). When an item cannot be
   scored confidently, score it DOWN / mark it FAILED and register the uncertainty.
   The human quality gate downstream is the terminal authority.

6. **Write-Flush-Forget — non-negotiable.** After writing the REPORT skeleton in the
   spec-generation step, NEVER re-read the REPORT file in full. Author one section per
   `Edit`, hold at most one in-flight section body, read `_progress.json` (not the
   report) to know what is done.

7. **No final response until VERIFICATION-REPORT exists on disk** at the output folder
   and is non-empty, with the verdict populated. Any closing summary before that is a
   protocol violation.

---

## Quick Start

Score a produced artifact against (a) its producer skill's output spec and (b) the
platform-reality findings discovered upstream, then emit a weighted verdict.

Primary output is a **VERIFICATION-REPORT** (one agent-native, section-shape spec) —
not a narrative review. The report carries the full checklist (each item atomic,
weighted 0–100, yes/no, tagged PROGRAM or JUDGE), the generated verifier programs and
their boolean results, the judge mean-of-N scores, a universal anti-gaming item, the
weighted total, and a closed-set `verification_verdict`.

**Generation shape:** `section-shape` (one multi-section report).

**This skill does NOT:** re-discover platform facts, train any model, entropy-gate
approvals, or replace the human quality gate. It produces an advisory weighted verdict
for the human gate to act on.

**Scope of a PASSED verdict:** it certifies structural / traceability conformance plus
external-platform conformance — NOT the artifact's internal design soundness. The
ANTIGAMING item guards against hollowness, not against a well-formed but questionable
design. Design-quality judgment is the downstream `human-quality-gate`'s job; PASSED does
not short-circuit it.

## Known Failure Modes
<!-- ACCUMULATING — appended by calibrating-updates (WS6). Newest first. Rules MUST be generic/behavioral (project-agnostic); project-specific fixes go to context packs, never here. Format + entry rules: engineering-skills/references/known-failure-modes-format.md. Read these at pre-flight so a lesson learned once recurs no more. -->

- **KFM-001** (2026-07-21, source: REC-003, CAL-INF-002)
  - Symptom: The verifier applies an artifact schema from a different capability's output to the current capability's artifact (e.g., evaluates a blueprint document against a directory-manifest schema meant for a design artifact), producing FAILED verdicts that are never resolvable by fixing the artifact itself — only by resetting verifier state.
  - Root cause: When multiple capabilities share a workspace, prior capability artifacts remain accessible in context. Without an explicit capability-scope boundary in the step instruction, the verifier may infer the wrong schema from ambient workspace context rather than from the declared output contract of the current capability's producer step.
  - Rule: Before decomposing the checklist, confirm the artifact schema from the current capability's producer step output contract (the `output_spec_source` SKILL.md or the step's `## Artifact shape` instruction). Do NOT infer schema from directory structure of other artifacts present in the workspace. If the step instruction declares a specific artifact type (e.g., "a single Markdown document"), treat any checklist item that contradicts it (e.g., requires a directory) as invalid and discard it. On REPAIR after a spec-mismatch rejection, invalidate and regenerate the verification report from scratch — do not apply the stale report incrementally.

## Anti-Patterns (do NOT)
<!-- ACCUMULATING — appended by calibrating-updates (WS6). One line each: **AP-NNN** (ISO-date, source: REC-NNN): prohibition — why. -->

- **AP-001** (2026-07-21, source: REC-003, CAL-INF-002): Do NOT infer artifact schema from other capabilities' outputs present in the workspace — always derive schema exclusively from the current step's `output_spec_source` and the `## Artifact shape` instruction; cross-capability schema bleed causes FAILED verdicts unresolvable by the producer.

## Output Architecture

```
{output_path}/
├── VERIFICATION-REPORT-{SESSION_ID}.md   ← Single agent-native report (9 sections)
├── verifiers/
│   ├── verify-{item-id}.py|.js            ← Generated self-contained verifier programs (one per PROGRAM item)
│   └── ...
└── VERIFICATION-AUDIT-{SESSION_ID}.md     ← Session audit trail (metadata only)
```

**Why this shape:** The report is one cross-referencing spec — the checklist feeds the
program-verifier section, which feeds scoring, which feeds aggregation, which feeds the
verdict. Cross-section dependencies make it section-shape, not a per-item file set. The
generated verifier programs live in a `verifiers/` sidecar folder so the report can
embed each one by reference and a human can re-run them deterministically.

**Downstream consumer:** `human-quality-gate` (terminal authority; reviews the report,
the failed items, and the verifier code — never the raw platform knowledge).

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `artifact_path` | string | Yes | — | Path to the produced artifact under test (the plan/research/code doc to score). |
| `output_spec_source` | string | Yes | — | Path to the producer skill's SKILL.md output spec OR its `quality_criteria_path`. The declared outputs / acceptance criteria become SPEC checklist items. |
| `conformance_findings_path` | string | No | — | JSON file emitted by the sibling skill `adversarial-platform-review` (the DISCOVERY layer). A list of `{decision, claim, platform_reality, severity, fix, source_url}`, `severity ∈ [BLOCKER, RISK, MINOR]`. Each finding becomes one inverted pass-condition checklist item. When absent → checklist is spec-items-only and the report MUST note reduced coverage. |
| `judge_samples` | integer | No | 5 | Number of times each JUDGE item is sampled; the score is the MEAN of the samples (variance reduction). |
| `model` | string | No | — | The cross-family judge model. Set at the capability step level; the skill stays model-agnostic. Maker ≠ checker: SHOULD differ from the producer's family. |
| `output_path` | string | No | — | Folder where the report, verifiers, and audit are written. This IS the report location — files are written directly here, no subfolder is created (except `verifiers/`). Standalone default: `./verification/`. |
| `failure_feedback` | string | No | — | Feedback from a previous failed run (triggers REPAIR mode). |
| `custom_message` | string | No | — | Optional focus directives. Applied as additional constraints during checklist generation and scoring. Never overrides the bias-toward-FAILED rule or the program-vs-judge decision rule. |

**If any Required parameter is not defined, ABORT EXECUTION.**

## Prerequisites

- [ ] `artifact_path` exists and is readable.
- [ ] `output_spec_source` exists and is readable.
- [ ] A runtime for the generated verifiers (Python 3 stdlib OR Node stdlib) is available on the executor. If neither is available, every PROGRAM item degrades to JUDGE and the report notes the degradation.
- [ ] `output_path` is writable.

## VERIFY_INDEX — Carry-Forward Contract

Initialize at Step 1. Update after every phase. This is the SOLE source of truth
between phases. Never carry full generated text — only IDs, paths, scores, and status
flags.

```
VERIFY_INDEX = {
  session_id: string,
  mode: BUILD | REPAIR | REVERIFY,
  output_path: string,

  // checklist items (IDs + metadata only, never full prose bodies)
  items: [{
    id,                       // CHK-001 ...
    source,                   // SPEC | CONFORMANCE | ANTIGAMING
    source_url,               // carried from a CONFORMANCE finding, else null
    verifiability,            // PROGRAM | JUDGE
    weight,                   // 0-100
    verifier_file,            // verifiers/verify-{id}.py|.js when PROGRAM, else null
    score,                    // 0-100 (boolean*100 for PROGRAM; mean-of-N for JUDGE)
    status                    // pending | scored
  }],

  total_items: number,
  scored_items: number,
  weighted_total: number,     // computed in aggregation
  verification_verdict: string,        // PASSED | PASSED_WITH_FINDINGS | FAILED
  failed_blocker_count: number,

  conformance_present: boolean,        // false → reduced-coverage note required
  repair_log: [{ directive, target, outcome }],
  // REVERIFY mode only — the lap-over-lap convergence delta (see REVERIFY Mode section)
  reverify_delta: {
    prior_verdict: string,             // PASSED | PASSED_WITH_FINDINGS | FAILED (lap N-1)
    now_passing: [id],                 // previously-failed items that now pass
    regressions: [id],                 // previously-passing items that now fail
    still_failing: [id],               // failed last lap, still failing
    rejudged_ids: [id],                // items actually re-judged this lap (convergence scope)
    carried_ids: [id]                  // items whose prior JUDGE score was carried forward
  },
  blockers: [],
  open_questions: []
}
```

## Workflow

> **Reference precedence:** each Step below summarizes its phase file for orientation, but
> the `references/phase-*.md` file named in that Step is the SINGLE SOURCE OF TRUTH. Where an
> inline Step summary and its phase file differ, the phase file wins — read it before executing.

### Step 1: Initialize & Environment Setup

**Command:**
```
1. SESSION_ID = [Extract from EXECUTION METADATA]
   ## SESSION_ID is provided by the harness/execution metadata per execution-protocol.md §1.
   ## Do NOT generate a new SESSION_ID locally. The harness gives the same ID for every
   ## re-run of the same Stepwise session/step — that enables overwrite-on-re-run.
   ## SESSION_ID goes in FILENAMES only (VERIFICATION-REPORT-{SESSION_ID}.md), never in folders.

2. Mode detection (REPAIR > REVERIFY > BUILD — mutually exclusive):
   IF failure_feedback is non-empty:
     ## REPAIR — this skill's OWN prior report was rejected; surgically fix it.
     MODE = REPAIR
     FOLDER = resolve existing folder from output_path parameter
     PRIOR_FILE = find existing VERIFICATION-REPORT-*.md in FOLDER
     IF PRIOR_FILE not found → write Gap Report to VERIFICATION-AUDIT-*.md → EXIT
     SESSION_ID = extract session_id from PRIOR_FILE filename   # reuse, never the harness ID
     PREVIOUS_VERSION = parse version from PRIOR_FILE header
     NEW_VERSION = increment patch
     PARSE failure_feedback → REPAIR_DIRECTIVES [{ target, instruction, reason }]
     NOTE: output_path MUST already exist. Never mkdir for REPAIR.
     READ references/phase-d-report-assembly.md REPAIR sub-section NOW.
   ELIF the prompt contains a `## Previous verification (lap N-1)` block:
     ## REVERIFY — the PRODUCER's artifact was re-made in a VGT loop; re-score it
     ## with convergence + memory of the prior lap. See "REVERIFY Mode" section below.
     MODE = REVERIFY
     FOLDER = resolve existing folder from output_path parameter
     PRIOR_FILE = find existing VERIFICATION-REPORT-*.md in FOLDER (may be absent if the
                  prior lap's folder was cleaned — then fall back to the prior-report data
                  carried inline in the `## Previous verification (lap N-1)` block)
     SESSION_ID = extract from PRIOR_FILE filename if present, else [Extract from EXECUTION METADATA]
     NEW_VERSION = increment patch of the prior verdict's version (or "1.0.0" if unknown)
     PARSE the `## Previous verification (lap N-1)` block → PRIOR_VERDICT + PRIOR_ITEMS
       (prior per-item pass/fail + the failed-item ids). This is the convergence input.
     REVERIFY_SCOPE = "failed_items" if the block instructs re-verify-only-failed, else "full".
     NOTE: output_path MUST already exist. Never mkdir for REVERIFY.
     READ references/phase-c-scoring-aggregation.md REVERIFY sub-section NOW.
   ELSE:
     MODE = BUILD
     FOLDER = output_path (or "./verification/")
     CREATE FOLDER and FOLDER/verifiers/ (mkdir -p — idempotent)
     SESSION_ID = [Extract from EXECUTION METADATA]
     NEW_VERSION = "1.0.0"

3. Initialize VERIFY_INDEX with session_id, mode, output_path.

4. Zero Invention Policy: every checklist item MUST trace to the producer output spec,
   a consumed conformance finding, or the fixed universal anti-gaming item. Do NOT
   invent platform facts (Entry Rule #3). Do NOT invent acceptance criteria not present
   in output_spec_source — missing criteria → status: pending in open_questions.

5. Memory Bank:
   READ context-pack/active-context.md → prior session state (if exists).
   APPEND to context-pack/progress.md → "Session {SESSION_ID} started: {date} | verifying-artifacts | BUILD/REPAIR/REVERIFY".

6. STOP-GATE — abort if:
   - artifact_path is empty or the file does not exist
   - output_spec_source is empty or the file does not exist
   - output_path (resolved) is not writable
   LOG: "Step 1 COMPLETE. Session: {SESSION_ID}, Mode: {MODE}, conformance: {present|absent}."
```

**FIRST ACTION — MANDATORY:** Write `_progress.json` to FOLDER before any other file
write (prevents orchestrator SIGINT). Use the section-shape schema (see
execution-protocol.md §10.1 / §2). Section keys: `run_metadata`, `checklist`,
`program_verifiers`, `judge_scoring`, `anti_gaming`, `aggregation`, `verdict`,
`findings`, `open_questions`.

**Execution:** automated

---

### Step 2: Load Inputs & Detect Coverage

Read `references/phase-a-checklist-generation.md` before executing this step and Step 3.

**Command:**
```
## 2A. STOP-GATE: Validate Required Inputs
REQUIRED = [ {name: "artifact", path: artifact_path},
             {name: "output_spec", path: output_spec_source} ]
FOR EACH input IN REQUIRED:
  IF path empty OR file missing → WRITE Gap Report to VERIFICATION-AUDIT-{SESSION_ID}.md → EXIT.

## 2B. Load the artifact under test (full content; this is the scored object).
READ artifact_path → ARTIFACT_TEXT.

## 2C. Load the producer output spec.
READ output_spec_source → SPEC_TEXT.
  Extract SPEC_CRITERIA: each declared output / acceptance criterion → one candidate item.
  (No platform facts are read here — only what the producer declared it must produce.)

## 2D. Detect conformance coverage (the Phase-1 → Phase-2 handoff).
IF conformance_findings_path is non-empty AND file exists:
  READ conformance_findings_path → CONFORMANCE_FINDINGS (JSON list).
  VALIDATE each element has EXACTLY the handoff schema fields
    {decision, claim, platform_reality, severity, fix, source_url}, severity ∈ [BLOCKER, RISK, MINOR].
  Do NOT invent fields not in this schema. Malformed elements → register in open_questions, skip.
  VERIFY_INDEX.conformance_present = true
ELSE:
  CONFORMANCE_FINDINGS = []
  VERIFY_INDEX.conformance_present = false
  ## Reduced-coverage path. The report MUST carry a `reduced_coverage: true` note in
  ## run_metadata and findings: the checklist is spec-items-only and is BLIND to platform
  ## reality items by construction (Entry Rule #3). This is expected when no discovery
  ## step ran upstream — it is not an error, but it is a documented coverage gap.

## 2E. Detect Language.
DETECTED_LANGUAGE = detect from ARTIFACT_TEXT. Default: English.
```

**Execution:** automated

---

### Step 3: Generate Checklist (three sources → one weighted list)

Read `references/phase-a-checklist-generation.md` NOW for the candidate-based method,
the severity→weight map, and the inversion template.

> **REVERIFY mode:** SKIP this candidate-generation pass. Rebuild the checklist from
> `PRIOR_ITEMS` (reuse ids / weights / sources / verifiability so the lap-over-lap
> delta is stable); add an item only if the producer's output spec gained a genuinely
> new criterion. See the **REVERIFY Mode** section for the full convergence contract.

**Command:**
```
Build ONE list of atomic, weighted (0-100), yes/no items, each:
  { id, question, weight, verifiability ∈ [PROGRAM, JUDGE], source, source_url? }

Merge THREE sources (Do NOT stop. Process ALL items from ALL three sources):

(a) SPEC items (source: SPEC). FOR EACH criterion in SPEC_CRITERIA:
    Use the candidate-based method (RLCF §2): imagine a few deliberately-flawed drafts
    of this artifact, enumerate their failure modes for this criterion, turn each failure
    mode into ONE atomic yes/no item phrased as a pass-condition. weight by criterion
    importance (acceptance-critical → 90-100; supporting → 40-75). Default verifiability
    = JUDGE; promote to PROGRAM only per the Step 4 100%-sure rule.

(b) REALITY items (source: CONFORMANCE). FOR EACH finding in CONFORMANCE_FINDINGS:
    Transform the finding into ONE item by INVERTING it into a pass-condition question:
      question = "Does the artifact's {decision} conform to {platform_reality}?"
      weight   = severity→weight: BLOCKER→100, RISK→75, MINOR→40
      verifiability = JUDGE by default; promote to PROGRAM when the finding is EXACTLY
                      checkable (e.g. a cron-syntax finding → a cron-syntax verifier).
      source = CONFORMANCE; source_url = the finding's source_url (carry for traceability).
    Phrase inversions per phase-a-checklist — in particular, a currency/version finding's
    pass-condition is "uses a SUPPORTED, SECURE version of X" (not "the latest major").
    These items are why the checklist can catch reality gaps it did not derive itself.

(c) Universal anti-gaming item (source: ANTIGAMING) — append EXACTLY ONE, weight 100:
    question = "Does the artifact actually satisfy the spec rather than a high-level
                overview / stub / hand-wave?"
    verifiability = JUDGE.

FOR EACH item: assign id (CHK-001, CHK-002, ...) and add to VERIFY_INDEX.items
  (id, source, source_url, verifiability, weight, status: pending). Do NOT carry the
  question prose in the INDEX — it lives in the report's `checklist` section only.

Do NOT stop. Process ALL SPEC_CRITERIA and ALL CONFORMANCE_FINDINGS. Continue until
every criterion and every finding has produced at least one item and the single
anti-gaming item is appended.
```

**Execution:** automated

---

### Step 4: Generate Program Verifiers (RLCF Fig 6 — defer unless 100% sure)

Read `references/phase-b-program-verifier-generation.md` NOW for the 100%-sure gate,
the self-contained-program template, and the cron/package-existence/string-presence
recipes.

**Command:**
```
FOR EACH item in VERIFY_INDEX.items WHERE verifiability == PROGRAM:
  ## Pattern 5: load THIS item's source — its question + the exact artifact fragment it targets.
  LOAD the item's question and the relevant ARTIFACT_TEXT fragment (e.g. the cron string).

  ## RLCF Fig 6 GATE (the decision that keeps this honest):
  Generate a self-contained verifier (Python OR Node, STDLIB ONLY) ONLY IF you are
  100% sure the program checks the criterion EXACTLY (syntax / format / presence /
  absence). Examples that PASS the gate: invalid cron expression, package-name
  existence in a manifest, "no process.env outside the auth module", "dependency X
  absent from package.json", a required literal/route present.
  IF NOT 100% sure → DEMOTE this item to verifiability = JUDGE and skip verifier
  generation. Default to JUDGE/defer ~95% of the time. A program that is "probably
  right" is worse than a judge sample (it gives false certainty).

  ## Pattern 6: pre-write fidelity check on the generated program:
    - reads its input from the artifact (path or inlined fragment), not from a guess
    - stdlib only, no network, no install step, deterministic
    - exits 0 = PASS (criterion holds), non-zero = FAIL (criterion violated)
    - prints a one-line verdict the report can quote
  IF the program would need a hardcoded platform fact to decide → it is NOT exactly
  checkable → DEMOTE to JUDGE (platform facts come from discovery, not from this skill).

  WRITE verifiers/verify-{id}.py|.js — MANDATORY TOOL CALL. Do NOT defer.
  UPDATE VERIFY_INDEX.items[id].verifier_file = "verifiers/verify-{id}.{ext}".
  FLUSH the program text from memory.
  LOG: "{id} verifier written ({lang})."
  Do NOT stop. Process ALL PROGRAM items.
```

**Execution:** automated

---

### Step 5: Score Items (run programs; sample the judge)

Read `references/phase-c-scoring-aggregation.md` NOW for the run mechanics, the
mean-of-N judge protocol, and the no-entropy rule.

> **REVERIFY mode:** re-run ALL PROGRAM verifiers (regression net); judge only the
> convergence set (previously-failed + regression-suspect items) when
> `REVERIFY_SCOPE == "failed_items"`, and carry forward prior JUDGE scores for
> previously-passing, unchanged items (record ids in `reverify_delta`). The
> anti-gaming item is always re-judged. When `REVERIFY_SCOPE == "full"`, re-judge
> everything. See the **REVERIFY Mode** section for the full contract + delta rules.

**Command:**
```
FOR EACH item in VERIFY_INDEX.items:
  IF item.verifiability == PROGRAM:
    RUN verifiers/verify-{id}.{ext} against the artifact.
    score = 100 IF exit 0 (PASS) ELSE 0 (FAIL). Boolean → 0/100.
    RETAIN only the one-line verdict + exit code (§10.5.3 tool-output retention) —
      do NOT paste full program stdout into the report.
    IF the runtime is unavailable (no python/node) → DEMOTE to JUDGE for this run and
      note the degradation in open_questions.
  ELSE (JUDGE):
    Sample the judge `judge_samples` times on this single yes/no question against
    ARTIFACT_TEXT. Each sample returns a 0-100 confidence-of-PASS.
    score = MEAN of the samples.  ## variance reduction — NOT entropy routing, NOT auto-approve.
    When samples are split or the item is unanswerable from the artifact → bias the
    score DOWN (Entry Rule #5), do not round up.

  UPDATE VERIFY_INDEX.items[id].score and status = scored.
  Do NOT stop. Process ALL items until scored_items == total_items.
```

> **Parallel fan-out — DISPATCH DECISION (execution-protocol.md Section 14). Decide BEFORE scoring.**
> - **IF the harness can dispatch multiple workers in a SINGLE turn AND there are >= 3 checklist items to score → fan out BY DEFAULT.** Concurrent foreground workers alone qualify — background/detached tasks are NOT required, and an absent `Parallel delegation:` advertisement does NOT force inline (execution-protocol.md §14 Applicability). Dispatch one worker per checklist item, emitting **all item workers in ONE turn (§14.3 step 2) — one-worker-per-turn serializes them.** Do NOT fall back to the sequential scoring loop. Each worker scores ONLY its own item — a JUDGE item's `judge_samples` runs, or a PROGRAM item's verifier run — and returns one compact `{id, score}` (JUDGE workers may return the raw sample array). **Workers never aggregate, never decide the verdict, and never write `_progress.json` or the §11 sidecar.**
> - **ELSE (the harness is genuinely single-dispatch, or < 3 items) → run the inline per-item loop below.**
>
> Independence proof: each item is scored only against `ARTIFACT_TEXT` + its own question; no item reads another item's score (the §10.4 dependency graph shows `judge_scoring` / `program_verifiers` read the checklist, never a sibling item). Merge contract (coordinator, serial): collect each worker's per-item score, then YOU compute `score = MEAN(samples)` for JUDGE items, apply the bias-DOWN rule (Entry Rule #5) and the anti-gaming item, and run the weighted aggregation in Step 6. Output — the mean-of-N scores and the verdict — is IDENTICAL whether you fanned out or ran inline. Verify a PROGRAM item's runtime availability before trusting its worker result (Zero-Invention).

**Execution:** automated

---

### Step 6: Generate Verification Report (Phase A skeleton + Phase B sections)

Read `references/phase-d-report-assembly.md` NOW for the section structure, the
aggregation formula, and the verdict mapping.

**Apply execution-protocol.md §10** — Phase A (skeleton-first, within 5 tool calls)
then Phase B (one section per `Edit` call). Tool discipline (§10.5) is mandatory:
skeleton via `Write`, sections via `Edit`, **NEVER** `Bash + sed/awk/python3<<EOF/cat >`
to mutate REPORT_FILE. If an `Edit` fails on a section, fix the `Edit` call — do not
fall back to bulk-rewrite scripts.

**Skeleton stub text — must be ASCII:**
> `status: pending - will be generated`

ASCII hyphen (U+002D), not em dash.

**Section list (template order):**
run_metadata → checklist → program_verifiers → judge_scoring → anti_gaming → aggregation → verdict → findings → open_questions

**Cross-section dependency graph** (which sections read REPORT_FILE for prior state, per §10.4):

| Section | Reads from REPORT_FILE |
|---------|------------------------|
| run_metadata | none |
| checklist | none (from VERIFY_INDEX.items + report-only question prose) |
| program_verifiers | checklist (which items are PROGRAM) |
| judge_scoring | checklist (which items are JUDGE) |
| anti_gaming | none (the single ANTIGAMING item) |
| aggregation | checklist + program_verifiers + judge_scoring + anti_gaming (all scores) |
| verdict | aggregation (weighted_total + failed_blocker_count) |
| findings | checklist + verdict (failed items, CONFORMANCE source_urls, reduced-coverage note) |
| open_questions | all prior sections (accumulated gaps) |

**Aggregation + verdict (computed in the `aggregation`/`verdict` sections):**
```
weighted_total = round( sum(item.score * item.weight) / sum(item.weight) )   ## 0-100
failed_blocker_count = count(items WHERE weight == 100 AND score < 50)
verdict:
  FAILED                 IF failed_blocker_count > 0 OR weighted_total < 60
  PASSED_WITH_FINDINGS   IF failed_blocker_count == 0 AND 60 <= weighted_total < 85
  PASSED                 IF failed_blocker_count == 0 AND weighted_total >= 85
At the end of aggregation, VERIFY: stated item counts == count(VERIFY_INDEX.items).
IF mismatch → fix stated count before writing.
```

**Non-ASCII output fallback:** Apply execution-protocol.md §10.5.1. If the detected
output language is not English, OR ARTIFACT_TEXT / SPEC_TEXT / CONFORMANCE_FINDINGS
contains a character with codepoint > 127, use full-file `Write` for every section
write in this run (instead of `Edit`). Per-section discipline is unchanged — one
section populated per call.

**CONTINUE on re-entry:** If invoked while `_progress.json` shows `status: RUNNING`
+ `skeleton_written: true` + partial `sections` map, this is a CONTINUE invocation
(execution-protocol.md §10.6). Resume from the first `pending` section in template
order; the skeleton is already on disk — do NOT rewrite it. Distinct from REPAIR
(which requires `failure_feedback`) and from REVERIFY (which is a fresh lap re-score
triggered by a `## Previous verification (lap N-1)` block — a new run, not a mid-run
resume).

After the skeleton write, flip `_progress.json.skeleton_written: true`.

**Reduced-coverage rule:** when VERIFY_INDEX.conformance_present == false, the
`findings` section MUST state `reduced_coverage: true` and that the verdict reflects
spec items only and is blind to platform-reality items.

**Execution:** automated

---

### Step 7: Write Audit & Finalize

**Command:**
```
WRITE VERIFICATION-AUDIT-{SESSION_ID}.md with:
  - header: version, session, mode, date, language, conformance_present
  - inputs: artifact_path, output_spec_source, conformance_findings_path (loaded|absent), judge_samples, model
  - generation_summary: per-section status
  - checklist_summary: total items, by source (SPEC/CONFORMANCE/ANTIGAMING), by verifiability (PROGRAM/JUDGE)
  - verifier_index: each PROGRAM item → verifier_file → PASS/FAIL
  - aggregation: weighted_total, failed_blocker_count, verification_verdict
  - repair_changes (REPAIR mode only): directive | target | outcome
VERIFY REPORT and AUDIT exist and are non-empty.

Memory Bank artifact type: "{N} verification-reports" (exact count of report files written).

Memory Bank — MANDATORY session-end writes:
  1. Overwrite context-pack/active-context.md with session status, decisions, blockers, key artifacts.
  2. Append one milestone row to context-pack/progress.md with the artifact count above.
  (Schema: execution-protocol.md §4.)

LAST ACTION — MANDATORY: Read _progress.json; verify no section is still `pending`;
set status: COMPLETED and completed_at; write _progress.json. If the run failed, set
status: FAILED with completed_at instead.
```

**Execution:** automated

---

### Step 8: Emit Harness Outputs Sidecar

**Apply execution-protocol.md §11.** Mandatory when the prompt contains a
`## Run metadata` block (Stepwise invocation); skip otherwise (standalone).

**Output parameters this skill produces** (one key per row of the prompt's
`## Output parameters` table):

- `verification_verdict` — the closed-set verdict. values: [PASSED, PASSED_WITH_FINDINGS, FAILED]. required: true. Read from VERIFY_INDEX.verification_verdict.
- `verification_report_path` — the actual on-disk path of `VERIFICATION-REPORT-{SESSION_ID}.md` written in Step 6.
- `failed_blocker_count` — integer; VERIFY_INDEX.failed_blocker_count.

**Path Verification Before Write (§11.1.1):** for `verification_report_path`, confirm
the file exists at the path you are about to report, and report the **actual on-disk
path you wrote to** — never a re-derived input parameter or template substitution.

**Strict ordering (§11.4):** all skill outputs written → Memory Bank writes →
`_progress.json` flipped to COMPLETED → **sidecar write (this step)** → `final_response`.
No tool calls after the sidecar write.

**Execution:** automated

---

## REVERIFY Mode (verification-loop convergence)

**When:** the prompt carries a `## Previous verification (lap N-1)` block and NO
`failure_feedback` (Step 1 sets `MODE = REVERIFY`). This is the automated
Verdict-Gated-Transition loop re-running the gate after the PRODUCER re-made the
artifact — NOT a REPAIR of this skill's own report. The harness threads the prior
lap's verification report + verdict into that block (and, when the gate's
`gate_policy.reverify_scope: failed_items` is set, an instruction to re-verify only
the failed/changed items). REVERIFY makes the lap-2+ gate cheaper and memoryful
without changing accept-verdict semantics.

**The convergence contract:**

1. **Rebuild the checklist from the prior report — do NOT regenerate candidates.**
   Reuse the prior lap's item ids, weights, sources, and verifiability flags
   (parsed into `PRIOR_ITEMS` in Step 1). Item identity MUST be stable across laps
   so the delta is meaningful. Skip the Step 3 candidate-generation pass entirely;
   only add an item if the producer's output spec genuinely gained a new criterion.

2. **Re-run ALL PROGRAM verifiers in full (always).** They are deterministic and
   cheap, and they are the regression net — a fix elsewhere must not silently break
   a previously-passing exactly-checkable item. Never skip a PROGRAM re-run.

3. **Judge-sample only the convergence set (when `reverify_scope: failed_items`).**
   Re-judge: (a) every item that FAILED last lap, plus (b) any item whose targeted
   artifact region changed since last lap (regression-suspect — inspect the artifact
   diff/section the item points at). For previously-passing, unchanged items, CARRY
   FORWARD the prior JUDGE score (record their ids in `reverify_delta.carried_ids`).
   When `reverify_scope: full` (or the scope is unstated), re-judge every JUDGE item
   as in BUILD — the block is still consumed as memory, but no sampling is skipped.
   The anti-gaming item is ALWAYS re-judged (never carried).

4. **Aggregate + verdict — semantics UNCHANGED.** Same weighted formula, same
   bias-toward-FAILED rule, same closed-set verdict (Step 6). Carried-forward scores
   participate in the weighted total exactly as re-judged ones do.

5. **The verdict MUST state the delta.** The `verdict` + `findings` sections report,
   from `VERIFY_INDEX.reverify_delta`: how many previously-failed items now pass,
   how many regressions appeared (previously-passing now failing — these are BLOCKING
   regardless of weight), and how many are still failing. Example line:
   `Delta vs lap N-1: 3 previously-failed now pass, 0 regressions, 1 still failing.`
   A REVERIFY report with no delta statement is a protocol violation.

**Guardrails (unchanged from BUILD):** Zero-Invention (every item still traces to a
source), no entropy auto-approve, bias DOWN when uncertain, human gate remains the
terminal authority. Convergence narrows *what is re-sampled*, never *what may pass*.
A regression flips the verdict to FAILED even if the weighted total looks healthy.

**Fallback:** if the `## Previous verification (lap N-1)` block is malformed or the
prior items cannot be parsed, degrade to a full BUILD-shape re-score (regenerate the
checklist), note the degradation in `open_questions`, and re-judge everything — never
carry a score you could not tie to a prior item.

---

## Upstream Consistency Rules

### 1. Zero Invention Policy
Every SPEC item traces to a declared output / acceptance criterion in
`output_spec_source`. Every CONFORMANCE item traces to one finding in
`conformance_findings_path`. The single ANTIGAMING item is fixed text. No item is
invented from the verifier's own platform knowledge (Entry Rule #3).

### 2. Handoff Schema Fidelity (hard contract)
`conformance_findings_path` is consumed EXACTLY as `{decision, claim, platform_reality,
severity, fix, source_url}` with `severity ∈ [BLOCKER, RISK, MINOR]`. Do NOT read,
require, or invent any other field. Map severity→weight as BLOCKER→100 / RISK→75 /
MINOR→40 with no other mapping.

### 3. Program-vs-Judge Decision Fidelity (RLCF Fig 6)
Mark PROGRAM only when 100% sure the program checks the criterion exactly. Default to
JUDGE ~95% of the time. A criterion that needs a platform fact to decide is NOT exactly
checkable here → JUDGE (its truth came from discovery).

### 4. Closed-Set Verdict Values
`verification_verdict` declares an exhaustive `values:` array in UPPER_SNAKE_CASE:
[PASSED, PASSED_WITH_FINDINGS, FAILED]. Paths and counts get NO `values:`.

### 5. Bias & Human-Terminal
When uncertain, score DOWN / mark FAILED. The verdict is advisory; the human quality
gate is the terminal authority. Never entropy-gate an approval (Entry Rules #4, #5).

### 6. Source Fidelity Check (per item, pre-write)
Before writing each checklist/scoring row: verify the item id is unique, the source is
one of {SPEC, CONFORMANCE, ANTIGAMING}, CONFORMANCE items carry a source_url, PROGRAM
items carry a verifier_file that exists on disk, and the score is in 0-100.

## Status Protocol

Every report item carries a status: `scored` (program ran or judge sampled),
`pending` (could not be scored from available inputs → registered in open_questions),
`degraded` (a PROGRAM item fell back to JUDGE because no runtime was available).

## Reference Files

| File | Load when | Purpose |
|------|-----------|---------|
| `references/phase-a-checklist-generation.md` | Steps 2–3 | Candidate-based generation, three-source merge, severity→weight map, finding-inversion template, anti-gaming item. |
| `references/phase-b-program-verifier-generation.md` | Step 4 | RLCF Fig 6 100%-sure gate, self-contained verifier template, cron/package/presence recipes, demotion-to-JUDGE rule. |
| `references/phase-c-scoring-aggregation.md` | Step 5 | Program run mechanics, mean-of-N judge sampling (no entropy), tool-output retention, bias-down rule. |
| `references/phase-d-report-assembly.md` | Step 6–7 | Report section structure, aggregation formula, verdict mapping, reduced-coverage note, REPAIR mechanics. |
| `context-pack/execution-protocol.md` | As referenced | SESSION_ID, _progress.json lifecycle, §10 section generation, §11 sidecar, Memory Bank. |
