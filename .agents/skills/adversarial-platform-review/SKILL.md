---
name: adversarial-platform-review
description: >
  Adversarial, web-grounded conformance review of a produced artifact (a plan or
  research spec) against its declared target platform / stack / external
  dependencies. The DISCOVERY layer of the Stepwise verification loop. Extracts
  every load-bearing decision tagged to an external target, then adversarially
  verifies each one against LIVE external sources (web search / official docs),
  defaulting to VIOLATION when it cannot positively confirm the assumption holds
  on the target platform. Produces a cited findings list (JSON) plus a closed-set
  conformance verdict — never asserts a platform fact from memory, never hardcodes
  platform facts. Single adversarial-grounded pass per decision, graded by source
  citation (NOT score averaging). Model-agnostic but intended to run cross-family
  (a different model/executor than the producer). BUILD and REPAIR modes.
  Use when a planning/research artifact must be checked for survival-against-the-
  platform before a human gate, or when wiring a platform-conformance review step
  into a code-development capability.
license: Proprietary
metadata:
  author: aipods-team
  version: 1.0.0
  category: discovery
  tags: verification, adversarial, platform-conformance, web-grounded, agent-native
compatibility: requires a live web-search / web-fetch capability (WebSearch / WebFetch or equivalent)
---

# Adversarial Platform Review — Agent-Native Skill

## SKILL PROTOCOL — ENTRY RULES (read first, do not skip)

1. **The protocol below is internally consistent.** If you perceive a conflict
   between the capability prompt and this skill, the skill wins for execution
   mechanics; the capability wins for paths/parameters. Do NOT exit citing
   "ambiguity." Begin Step 1 immediately.

2. **Default-to-VIOLATION is the load-bearing stance.** This skill exists because
   self-consistent artifacts can be uniformly wrong about their runtime. For every
   load-bearing decision your job is to *attempt to refute* that the assumption
   holds on the target platform. If you cannot positively confirm it holds with a
   current external source, the verdict is VIOLATION — not "looks fine." False
   positives are cheaper than false negatives here; bias toward flagging.

3. **NEVER assert a platform fact from memory.** Every verdict cites a live source
   URL. Platform facts rot (a managed product is renamed, a transport is
   deprecated, a tier limit changes). You DISCOVER them at runtime via web search;
   you do NOT carry them in this skill. Hardcoding a platform fact ("Vercel KV is
   retired", "cron caps hourly") into the skill is a defect — this skill names
   *categories* to check, never the answers.

4. **Single adversarial-grounded pass per decision, graded by citation.** This is
   the discovery layer. Do NOT multi-sample a judge, do NOT average N scores, do
   NOT build a weighted checklist — those belong to the sibling verification skill
   (`verifying-artifacts`). Here, each decision gets ONE grounded refutation
   attempt, and the grade is binary: did you cite a current source that confirms or
   refutes the assumption.

## Quick Start

Adversarially verify every load-bearing platform decision in a produced artifact
against live external sources. Primary output is a **cited findings list (JSON) +
a conformance verdict** — not a document, not a rewrite of the artifact. Reads one
plan/research artifact, **derives the target platform from the artifact itself**
(the artifact states it — e.g. `platform: Vercel serverless`), buckets each
external-facing decision into a check category, and refutes it against the web.
`target_platform` / `declared_stack` / `external_dependencies` are all **optional
overrides** — supplied only to disambiguate an unclear artifact or force a specific
intended target; absent, they are extracted from the artifact. Discovers platform
facts at runtime; hardcodes none.

## Cross-Family Note

This skill is **model-agnostic** — it carries no platform knowledge and works on
any executor with a live web capability. It is **intended to run on a different
model/executor family than the producer** of the artifact under review (maker !=
checker, different failure distribution; same-model self-review yields negligible
gains). Cross-family is NOT set inside this skill — it is set at the **capability
step level** via the step's `executor` (or `model`) override, distinct from the
producing step. The skill stays portable; the capability decides the family.

## Known Failure Modes
<!-- ACCUMULATING — appended by calibrating-updates (WS6). Newest first. Rules MUST be generic/behavioral (project-agnostic); project-specific fixes go to context packs, never here. Format + entry rules: engineering-skills/references/known-failure-modes-format.md. Read these at pre-flight so a lesson learned once recurs no more. -->

## Anti-Patterns (do NOT)
<!-- ACCUMULATING — appended by calibrating-updates (WS6). One line each: **AP-NNN** (ISO-date, source: REC-NNN): prohibition — why. -->

## Output Architecture

```
{output_path}/
├── CONFORMANCE-FINDINGS-{SESSION_ID}.json   ← cited findings list (the hard contract)
├── CONFORMANCE-REVIEW-{SESSION_ID}.md       ← living progress tracker + human-readable review
└── CONFORMANCE-AUDIT-{SESSION_ID}.md        ← session metadata (decisions extracted, sources hit)
```

**Why this architecture.** The findings JSON is a **machine contract** consumed
verbatim by the sibling skill `verifying-artifacts` (it inverts each finding into a
checklist item). Its field shape is frozen (see Step 4). The `.md` review is the
living progress tracker (Pattern 7) and the human-readable surface; the audit holds
session metadata. One bounded findings list per run → single-file (list-shape), not
a manifest-per-item tree.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `artifact_path` | string | Yes | — | Absolute path to the plan/research doc under review. |
| `target_platform` | string | No | — | **Optional override** of the deployment target (e.g. "Vercel serverless"). If omitted, DERIVE it from the artifact (the artifact declares it). Supply only to disambiguate an unclear artifact or to force verification against a specific intended target. |
| `declared_stack` | string | No | — | Declared languages/runtimes/frameworks. If omitted, extract from the artifact. |
| `external_dependencies` | string | No | — | Declared third-party services/SDKs/packages. If omitted, extract from the artifact. |
| `output_path` | string | Yes | — | Directory where the findings JSON, review, and audit are written. This IS the output location — files are written directly here, no subfolder is created. |
| `failure_feedback` | string | No | — | REPAIR-mode directives. Non-empty → REPAIR. |

**If any Required parameter is not defined, ABORT EXECUTION.**

## Prerequisites

- [ ] A live web-search / web-fetch capability is available (WebSearch / WebFetch or equivalent). Without it the skill cannot ground a single verdict — abort and register a blocker rather than asserting facts from memory.
- [ ] `artifact_path` exists and is readable.
- [ ] `output_path` is writable.

## REVIEW_INDEX — Carry-Forward Contract

Initialize at Step 1. Update after every phase. This is the SOLE source of truth
between phases. Never carry full generated text — only IDs, paths, verdicts, and
status flags.

```
REVIEW_INDEX = {
  session_id: string,
  mode: BUILD | REPAIR,
  output_path: string,
  artifact_path: string,
  target_platform: string,
  decisions: [{
    id,                    // DEC-01, DEC-02, ...
    category,              // persistence | scheduling | transport | auth-token-lifecycle |
                           //   third-party-api-tier | sdk-package | region-data-residency
    claim,                 // the assumption the artifact bakes in (quoted/paraphrased)
    quote,                 // verbatim snippet from the artifact (provenance)
    verdict,               // CONFORMS | VIOLATION | UNCONFIRMED (UNCONFIRMED => treated as VIOLATION)
    severity,              // BLOCKER | RISK | MINOR  (null until verified)
    source_url,            // live source cited for the verdict (null until verified)
    status                 // complete | pending | assumption
  }],
  total_decisions: number,
  completed_decisions: number,
  blocker_count: number,
  conformance_verdict: null,   // CONFORMS | CONFORMS_WITH_RISKS | VIOLATIONS_FOUND
  repair_log: [{ directive, target, outcome }],
  blockers: [],
  open_questions: []
}
```

## FIC Context Management

Monitor context usage during execution:
- At 60% context capacity → COMPACTION TRIGGER:
  1. Write current REVIEW_INDEX state to disk as `_progress.json`.
  2. Complete the current decision's verification if mid-flight (write its finding first).
  3. Log the compaction event to the audit file.
  4. Signal orchestrator for context reset.
  5. On resume: load `_progress.json`, continue from the first decision whose `status` is `pending`.

## Status Protocol

Every decision and every finding carries a status:
- `status: complete` — verdict reached and a live source cited.
- `status: pending` — decision extracted but verification not yet grounded (e.g. web call failed) → registered in open_questions and treated as VIOLATION (default-to-VIOLATION) until grounded.
- `status: assumption` — verdict inferred without a current source → NOT allowed as a CONFORMS verdict; an un-sourced "it's fine" is recorded as UNCONFIRMED → VIOLATION.

## Workflow

> **Reference precedence:** each Step below summarizes its phase file for orientation, but
> the `references/phase-*.md` file named in that Step is the SINGLE SOURCE OF TRUTH. Where an
> inline Step summary and its phase file differ, the phase file wins — read it before executing.

### Step 1: Initialize & Environment Setup

**Command:**
```
1. SESSION_ID = [Extract from EXECUTION METADATA]
   ## SESSION_ID is provided by the harness/execution metadata per execution-protocol.md §1.
   ## Do NOT generate a new SESSION_ID locally (no timestamps, UUIDs, or date-string
   ## formulas). The harness gives the same ID for every re-run of the same Stepwise
   ## session/step — that is what enables overwrite-on-re-run. SESSION_ID goes in
   ## FILENAMES only (CONFORMANCE-FINDINGS-{SESSION_ID}.json), never in folder names.

   **FIRST ACTION — MANDATORY:** Write `_progress.json` to output_path before any
   other file write (prevents the orchestrator from sending SIGINT). Use the
   list-shape schema (this skill produces one bounded findings list):
     { "skill": "adversarial-platform-review", "session_id": "{SESSION_ID}",
       "status": "RUNNING", "started_at": "<ISO timestamp>", "completed_at": null,
       "total": 0, "completed": 0, "items": [] }

2. REPAIR detection (Pattern 3 — REPAIR Folder Reuse):
   IF failure_feedback is non-empty:
     MODE = REPAIR
     FOLDER = resolve existing folder from output_path parameter
     PRIOR_FILE = find existing CONFORMANCE-FINDINGS-*.json in FOLDER
     IF PRIOR_FILE not found → write Gap Report → EXIT (REPAIR has nothing to repair)
     LOAD PRIOR_FILE → PREVIOUS_FINDINGS; LOAD CONFORMANCE-REVIEW-*.md → PREVIOUS_REVIEW
     SESSION_ID = extract session_id from PRIOR_FILE filename   ## reuse, do NOT regenerate
     PARSE failure_feedback → REPAIR_DIRECTIVES [{ target, instruction, reason }]
     NOTE: output_path MUST already exist. Never mkdir for REPAIR.
   ELSE:
     MODE = BUILD
     CREATE output_path (mkdir -p)   ## idempotent — safe on re-run

3. Initialize REVIEW_INDEX with session_id, mode, output_path, artifact_path, target_platform.
   RESOLVE target_platform: if the `target_platform` param is provided, use it (an
   explicit override). OTHERWISE **derive it from the artifact** — read the
   artifact's stated target (e.g. `platform:` in plan_overview / research metadata,
   the deployment section, or the technology_fidelity table) and set
   REVIEW_INDEX.target_platform to that. Record in the audit whether the target was
   given (override) or derived (and the source line). If, after reading the
   artifact, NO external runtime target can be identified, set target_platform =
   "(none declared)" and proceed: the artifact has nothing external to verify
   against, so the run will yield CONFORMS with zero findings + an open-question
   note — NOT an abort.

4. Zero Invention Policy: every verdict MUST cite a live external source. A decision
   with no grounded source → status: pending → UNCONFIRMED → treated as VIOLATION.
   Do NOT invent platform facts. Do NOT assert from memory.

5. Memory Bank:
   READ context-pack/active-context.md → prior session state (if exists).
   APPEND to context-pack/progress.md → "Session {SESSION_ID} started: {date} | adversarial-platform-review | BUILD/REPAIR".

6. STOP-GATE — abort if:
   - artifact_path is empty or does not exist
   - output_path is not writable
   - no live web-search/web-fetch capability is available (cannot ground verdicts)
   (NOTE: an empty target_platform is NOT an abort — it is derived from the
   artifact in step 3, or set to "(none declared)" when the artifact has no
   external target.)
   LOG: "Step 1 COMPLETE. Session: {SESSION_ID}, Mode: {MODE}, Target: {target_platform}."
```

### Step 2: Extract Load-Bearing Decisions

Read `references/phase-a-decision-extraction.md` before executing this step.

**Command:**
```
IF mode == REPAIR AND no REPAIR_DIRECTIVE targets extraction:
  LOAD decisions from PREVIOUS_FINDINGS into REVIEW_INDEX.decisions. SKIP re-extraction.
  LOG: "Step 2 skipped (REPAIR, no directive). Loaded {N} prior decisions."

ELSE:
  LOAD artifact_path → ARTIFACT (single bounded input — read in full).
  RESOLVE declared_stack and external_dependencies: use the params if provided;
    otherwise extract them from ARTIFACT (technology_fidelity tables, desired_end_state,
    implementation_strategy, vercel_requirements, code blocks, dependency lists).

  EXTRACT every load-bearing decision that is tagged to an external target, and
  bucket each into exactly one category:
    - persistence            (databases, files, object stores, caches-as-source-of-truth)
    - scheduling             (cron, timers, background jobs, refresh loops)
    - transport              (protocol/transport between client and server)
    - auth-token-lifecycle   (OAuth/PKCE refresh, token storage, session lifetime)
    - third-party-api-tier   (managed-service existence/branding, tier/rate limits, quotas)
    - sdk-package            (package existence & exact naming, driver viability on target)
    - region-data-residency  (region selection, data-residency/compliance constraints)

  A decision is "load-bearing" if the artifact's correctness depends on it holding
  on the target platform (Pattern 5: only extract what the source actually states).
  For EACH decision capture: claim (the baked-in assumption) + quote (verbatim
  snippet for provenance) + category. Assign IDs DEC-01, DEC-02, ... in document order.

  Extract per phase-a — phase-a is the single source of truth for the extraction rules,
  including: the existence-vs-runtime-behavior split (emit a SECOND decision in the
  behavioral category when a dependency's default runtime behavior, not just its
  existence, is load-bearing); self-deferred handling (park in open_questions ONLY when
  the artifact gates downstream work on the deferral — ungated "TBD" stays an extracted
  decision; when unsure whether it is gated, treat as ungated → VIOLATION); and distractor
  discipline (a purely internal choice — language version,
  linter, monorepo tool — is not platform-coupled unless the artifact ties it to a
  platform constraint). Do NOT verify yet.

WRITE the living progress tracker CONFORMANCE-REVIEW-{SESSION_ID}.md with EVERY
extracted decision marked "[ ] TO BE VERIFIED" (Pattern 7) — MANDATORY TOOL CALL.
UPDATE REVIEW_INDEX: decisions[], total_decisions, completed_decisions = 0.
LOG: "Step 2 COMPLETE. {N} load-bearing decisions extracted across {K} categories."
```

### Step 3: Adversarially Verify Each Decision Against Live Sources

Read `references/phase-b-adversarial-verification.md` before executing this step.

> **Parallel fan-out — DISPATCH DECISION (execution-protocol.md Section 14). Decide BEFORE verifying.**
> - **Fan out BY DEFAULT whenever the harness can dispatch multiple workers in a single turn AND there are >= 3 decisions in `REVIEW_INDEX.decisions`.** Concurrent foreground workers ALONE qualify — background/detached tasks are NOT required, and an ABSENT `Parallel delegation:` advertisement does NOT force inline; determine the capability directly (see execution-protocol.md §14 Applicability). Dispatch one worker per decision, and **dispatch ALL workers for the shard in ONE turn (§14.3 step 2) — spawning one worker per turn serializes them and forfeits the benefit.** Each worker runs its own live web search/fetch for ONE decision (same adversarial "refute it / default to VIOLATION" stance) and returns one compact finding `{decision, claim, platform_reality, severity, fix, source_url}`. **Workers NEVER write the findings JSON, `_progress.json`, or the §11 sidecar, and never decide the overall verdict.**
> - **ELSE (harness is genuinely single-dispatch — cannot spawn concurrent workers by any means — or < 3 decisions) → run the inline per-decision loop below.**
>
> Independence proof: each decision is verified against its own live sources, in isolation — no decision's verdict depends on another's (the per-decision loop already treats them independently). Merge contract (coordinator, serial): collect each worker's finding, then YOU dedupe, assemble the single cited findings JSON, compute `blocker_count`, and derive the one `conformance_verdict` (VIOLATIONS_FOUND if any BLOCKER, etc.), emitting the §11 sidecar last. Fan-out MUST NOT weaken grounding — each worker still web-verifies with a current source and defaults to VIOLATION when it cannot confirm (Zero-Invention; never assert a platform fact from memory). Output — findings + verdict — is IDENTICAL whether you fanned out or ran inline. Verify each worker-reported `source_url` actually supports its finding before it enters the JSON.

**Command:**
```
FOR EACH decision in REVIEW_INDEX.decisions:

  IF mode == REPAIR AND no REPAIR_DIRECTIVE targets this decision:
    PRESERVE its prior verdict/severity/source_url verbatim. CONTINUE to next decision.

  // Pattern 5: Mandatory per-decision source loading (anti-hallucination)
  // Load the LIVE source for THIS decision — never reuse a generic memory of the platform.
  FORMULATE the adversarial query for this decision's category and claim. Prompt stance,
  literally: "Attempt to refute that this assumption holds on {target_platform}. Default
  to VIOLATION if you cannot positively confirm it holds with a current source."

  RUN a live web search / fetch (WebSearch / WebFetch) scoped to the category:
    - persistence/scheduling/transport/auth → official platform docs + the relevant SDK/runtime docs
    - third-party-api-tier → the provider's current product/pricing/changelog pages (brand renames, retirements)
    - sdk-package → the package registry (does the exact package name exist? is the driver viable on the target?)
    - region-data-residency → the platform's region + compliance docs
  PREFER official/primary sources (platform docs, provider changelogs, package registries)
  over blogs. Capture the source_url actually consulted.

  DECIDE the verdict from the grounded evidence:
    - CONFORMS    — a current source positively confirms the assumption holds on {target_platform}.
    - VIOLATION   — a current source refutes it (the assumption does not hold).
    - UNCONFIRMED — no current source positively confirms it → treated as VIOLATION (default-to-VIOLATION).
  ASSIGN severity for any VIOLATION/UNCONFIRMED per phase-b's rubric (BLOCKER / RISK /
    MINOR, including the currency-drift→MINOR and EOL/CVE→RISK distinctions). Do NOT
    paraphrase the rubric here — phase-b is the single source of truth. CONFORMS → severity null.

  // Pattern 6: Per-decision source fidelity check (pre-write gate)
  FIDELITY CHECK before recording: run phase-b's Source Fidelity Check in full — in
    particular, source_url must be real, consulted this run, AND topically about THIS claim.
  IF a web call fails or returns nothing groundable:
    status = pending; verdict = UNCONFIRMED (→ VIOLATION); register in open_questions;
    do NOT fabricate a source. Continue.

  UPDATE REVIEW_INDEX: this decision's verdict, severity, source_url, status=complete; completed_decisions += 1.
  UPDATE CONFORMANCE-REVIEW-{SESSION_ID}.md IN-PLACE: replace "[ ] TO BE VERIFIED" with
    "[x] {verdict} ({severity}) — {source_url}" for this decision (Pattern 7).
  FLUSH this decision's web-evidence text from memory; retain only the index fields.
  LOG: "DEC-{nn} ({category}): {verdict} {severity}."

  Do NOT stop. Process ALL decisions. Continue until completed_decisions == total_decisions.
```

### Step 4: Emit the Cited Findings List (JSON)

Read `references/phase-c-findings-emission.md` before executing this step.

**Command:**
```
This file is the HARD CONTRACT consumed by `verifying-artifacts`. Field names are
FROZEN — do NOT rename, add, or drop fields.

BUILD the findings list: one object PER decision whose verdict is VIOLATION or
UNCONFIRMED (CONFORMS decisions are NOT findings — they are recorded only in the
review/audit). Each finding object is EXACTLY these six keys:

  {
    "decision":        "<the load-bearing decision, restated>",
    "claim":           "<the assumption the artifact baked in>",
    "platform_reality":"<what the live source says actually happens on the target platform>",
    "severity":        "BLOCKER | RISK | MINOR",
    "fix":             "<the minimal conforming change>",
    "source_url":      "<the live source URL cited for this verdict>"
  }

  severity MUST be one of BLOCKER, RISK, MINOR.
  source_url MUST be a real URL consulted this run (Step 3 fidelity gate). A finding
  without a source_url is invalid — fix it (re-ground) or drop it; never ship a blank source.

WRITE {output_path}/CONFORMANCE-FINDINGS-{SESSION_ID}.json as a JSON list of these
objects — MANDATORY TOOL CALL. Use the Write tool (whole-file create); never mutate
JSON via shell (sed/awk/python3<<EOF/cat >) — execution-protocol.md §10.5.
VERIFY the file exists, is valid JSON, and every object has exactly the six keys.
UPDATE REVIEW_INDEX: blocker_count = count of findings with severity == BLOCKER.
LOG: "Step 4 COMPLETE. {N} findings written ({B} BLOCKER, {R} RISK, {M} MINOR)."
```

### Step 5: Compute Verdict, Audit, and Emit Harness Outputs Sidecar

Read `references/phase-d-verdict-and-sidecar.md` before executing this step.

**Command:**
```
COMPUTE conformance_verdict from the findings (closed set):
  - VIOLATIONS_FOUND       — at least one BLOCKER finding.
  - CONFORMS_WITH_RISKS    — no BLOCKER, but at least one RISK or MINOR finding.
  - CONFORMS               — zero findings (every decision CONFORMS with a cited source).
  Bias note: an UNCONFIRMED decision is a VIOLATION (default-to-VIOLATION). Never
  return CONFORMS when any decision lacks a positively-confirming source.

VERIFY counts: blocker_count == number of BLOCKER findings in the JSON; total findings
  == VIOLATION+UNCONFIRMED decisions. IF mismatch → fix before writing.

WRITE CONFORMANCE-AUDIT-{SESSION_ID}.md: session metadata — decisions extracted per
  category, sources consulted (URLs), per-decision verdict table, the computed verdict,
  blocker_count, open_questions_count, and any open_questions (gated self-deferred
  decisions). MANDATORY TOOL CALL.

UPDATE the living tracker CONFORMANCE-REVIEW-{SESSION_ID}.md header: conformance_verdict,
  blocker_count, open_questions_count, completed/total. MANDATORY TOOL CALL.
  (open_questions_count stays in these human-facing headers — NOT the sidecar, which
  emits only declared output parameters.)

LAST ACTION — MANDATORY: update `_progress.json` to status COMPLETED (completed == total).

=== Emit Harness Outputs Sidecar (FINAL write) ===
Apply execution-protocol.md §11. Mandatory when the prompt contains a `## Run metadata`
block (Stepwise invocation); skip otherwise (standalone). Output parameters this skill
produces (one key per row of the prompt's `## Output parameters` table):
  - conformance_verdict        — CONFORMS | CONFORMS_WITH_RISKS | VIOLATIONS_FOUND
  - conformance_findings_path  — absolute path to CONFORMANCE-FINDINGS-{SESSION_ID}.json
  - blocker_count              — integer count of BLOCKER findings

Path Verification Before Write (§11.1.1): confirm CONFORMANCE-FINDINGS-{SESSION_ID}.json
exists at the path you report; report the ACTUAL on-disk path you wrote to, never a
re-derived parameter.
Strict ordering (§11.4): all skill outputs written → Memory Bank writes → `_progress.json`
flipped to COMPLETED → sidecar write (this step) → `final_response`. NO tool calls after
the sidecar write.
LOG: "Step 5 COMPLETE. Verdict: {conformance_verdict}. Blockers: {blocker_count}. Sidecar written."
```

## Output Parameters

| Parameter | Type | Required | Values | Description |
|-----------|------|----------|--------|-------------|
| `conformance_verdict` | enum | Yes | `CONFORMS`, `CONFORMS_WITH_RISKS`, `VIOLATIONS_FOUND` | Overall conformance of the artifact against its declared target platform. |
| `conformance_findings_path` | path | Yes | — | Absolute path to the findings JSON (the frozen-shape contract consumed by `verifying-artifacts`). |
| `blocker_count` | integer | Yes | — | Number of BLOCKER-severity findings. |

Outputs that are verdicts/statuses declare an exhaustive closed-set `Values` column in
UPPER_SNAKE_CASE (repo convention); paths and counts declare none.

### Findings JSON contract (frozen shape — consumed by `verifying-artifacts`)

The file at `conformance_findings_path` is a JSON **list**; each element is EXACTLY:

```json
{ "decision": "...", "claim": "...", "platform_reality": "...",
  "severity": "BLOCKER | RISK | MINOR", "fix": "...", "source_url": "https://..." }
```

Do NOT rename these fields. `verifying-artifacts` inverts each finding into one
pass-condition checklist item and weights it by `severity` — a field rename breaks
that handoff.

## Upstream Consistency Rules

### 1. Zero Invention Policy
Every verdict MUST cite a live external source consulted this run. No platform fact is
asserted from memory. An un-sourced "it conforms" is recorded as UNCONFIRMED → VIOLATION.

### 2. No Hardcoded Platform Facts
This skill names check *categories* only (persistence, scheduling, transport,
auth-token-lifecycle, third-party-api-tier, sdk-package, region-data-residency). It
encodes ZERO platform answers. Platform facts are discovered at runtime and rot fast;
baking them in (product retirements, cron caps, transport deprecations) is a defect.

### 3. Provenance Fidelity
Every decision carries a verbatim `quote` from the artifact; every finding carries the
`source_url` actually consulted. No invented quotes, no invented URLs.

### 4. Default-to-VIOLATION
When a current source cannot positively confirm an assumption holds, the verdict is
VIOLATION (false positives are cheaper than false negatives in this layer).

### 5. Source Fidelity Check (Per Decision)
Before recording each verdict: source_url is real and consulted this run; a CONFORMS
verdict has a positively-confirming source (else demote to UNCONFIRMED → VIOLATION); the
quote is verbatim; the category is the single best-fit bucket.

## open_questions

Any decision that could not be grounded (web call failed, source ambiguous) is recorded
here AND treated as VIOLATION. This registry is the last section of the audit — it never
silently disappears.

## Reference Files

- `references/phase-a-decision-extraction.md` — extracting and bucketing load-bearing decisions; distractor discipline.
- `references/phase-b-adversarial-verification.md` — the adversarial stance, per-category source strategy, verdict + severity rules.
- `references/phase-c-findings-emission.md` — the frozen findings JSON contract and validation.
- `references/phase-d-verdict-and-sidecar.md` — verdict computation, audit, Memory Bank, and §11 sidecar.

## Related Skills

- `verifying-artifacts` — downstream consumer: inverts each finding into a weighted checklist item, adds program verifiers, and scores. This skill DISCOVERS; that skill SCORES.
- `human-quality-gate` — terminal authority: a human reviews these findings (and the verification report), not raw platform knowledge.
