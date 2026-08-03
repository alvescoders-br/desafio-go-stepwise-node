# Adversarial Platform Review — Decision Extraction

## Context Contract

- **Inputs:** `REVIEW_INDEX` (from Step 1: session_id, mode, output_path, artifact_path, target_platform); the artifact at `artifact_path`; `declared_stack` / `external_dependencies` params (if provided).
- **Outputs:** `{output_path}/CONFORMANCE-REVIEW-{SESSION_ID}.md` (living tracker with every decision marked "[ ] TO BE VERIFIED"); `REVIEW_INDEX.decisions[]` populated.
- **Carries Forward:** `REVIEW_INDEX.decisions` (id, category, claim, quote, status=pending), `total_decisions`, `completed_decisions = 0`.
- **Flush After:** The raw artifact text — drop after decisions are extracted into `REVIEW_INDEX`. Only the per-decision `quote` snippets survive.
- **Dependency:** Step 1 must be COMPLETE (session initialized, STOP-GATE passed, `_progress.json` written).
- **H1 Title:** `# {project_name} -- Platform Decision Inventory`

## Mode-Specific Behavior

- **BUILD:** Read the artifact in full, extract and bucket every load-bearing external decision from scratch.
- **REPAIR:** If no `REPAIR_DIRECTIVE` targets extraction, load decisions from the prior `CONFORMANCE-FINDINGS-*.json` plus the prior review tracker into `REVIEW_INDEX.decisions` and SKIP re-extraction (preserve prior IDs verbatim). If a directive targets extraction (e.g. "you missed the region decision"), load the existing decisions, add/adjust only the targeted ones, rewrite the tracker IN PLACE, preserve untargeted decisions verbatim.
- **RESUME:** If `_progress.json` shows `status: RUNNING` with decisions already in `REVIEW_INDEX`, do not re-extract — continue to verification from the first `pending` decision.

## Content Generation Instructions

Use structured fields (one row per decision) rather than prose, because the
downstream verification skill reads `decision`, `claim`, and `category`
programmatically. Prose would force natural-language parsing and blur field
boundaries.

GENERATE the decision inventory with the following procedure:

1. **Read the artifact in full.** It is a single bounded input — read it whole, do
   not sample. Load-bearing platform decisions hide in `desired_end_state` tables,
   `implementation_strategy` / `vercel_requirements` prose, `technology_fidelity`
   tables, and inline code blocks (a `setInterval`, a `new Database('./x.db')`, a
   `"transport": "sse"`, a cron string). Read all of them.

2. **Resolve the declared stack and dependencies.** If `declared_stack` /
   `external_dependencies` params are provided, use them as the authoritative
   surface. Otherwise extract them from the artifact's technology tables and
   dependency lists. Record what you used in `REVIEW_INDEX` for the audit.

3. **Extract every load-bearing decision tagged to an external target.** A decision
   is load-bearing-against-the-platform when the artifact's correctness depends on
   it holding on `target_platform`. Bucket each into EXACTLY one category:

   | Category | What it covers | Extraction signals |
   |----------|----------------|--------------------|
   | `persistence` | databases, files, object stores, caches-as-source-of-truth | `new Database(...)`, local file paths, "store messages in", DB driver names |
   | `scheduling` | cron, timers, background jobs, refresh loops | `setInterval`/`setTimeout`, `crons`, cron expressions, "at server boot", "background job" |
   | `transport` | client↔server protocol/transport | "stdio", "SSE", "HTTP", "websocket", protocol names, "remote/hosted ... over ..." |
   | `auth-token-lifecycle` | OAuth/PKCE refresh, token storage, session lifetime | "proactive refresh", "token cache", "session state", "refresh loop", in-memory token |
   | `third-party-api-tier` | managed-service existence/branding, tier/rate limits, quotas | branded managed products ("Vercel KV"), "rate limiting", tier/quota claims |
   | `sdk-package` | package existence & exact naming, driver viability on target | `import X from 'pkg'`, exact package names, "driver", "adapter" |
   | `region-data-residency` | region selection, data-residency / compliance | region codes, "EU/US", "GDPR", "data residency", compliance claims |

   Why bucketing matters: each category has a different *source strategy* in Step 3
   (official docs vs provider changelog vs package registry). The bucket tells the
   verifier where to look.

4. **For EACH decision, capture:**
   - `claim` — the assumption the artifact bakes in, restated plainly (e.g. "An
     in-process timer keeps tokens fresh for the life of the server instance").
   - `quote` — a verbatim snippet from the artifact for provenance (the exact line
     or code fragment). This is the source-of-truth anchor; never paraphrase it.
   - `category` — the single best-fit bucket from the table above.
   - `id` — `DEC-01`, `DEC-02`, ... in document order. Status starts `pending`.

4a. **Existence vs. runtime-behavior split.** Package/service existence and its
   *behavior under the target's process model* are two different verifications. When a
   dependency's **runtime behavior** — not merely its presence — is load-bearing (its
   default store, its concurrency/clustering semantics, where it keeps state, whether
   that state survives the instance lifecycle), emit **TWO** decisions:
   - one in `sdk-package` — *does the exact package exist / resolve / install on the target?*
   - a **second** decision in the behavioral category the behavior belongs to
     (`persistence`, `scheduling`, `auth-token-lifecycle`, or `third-party-api-tier`) —
     *does its default runtime behavior hold under the declared process model (single vs.
     multi-worker / clustered / multi-container)?*

   Signal: any dependency that holds counters, sessions, tokens, caches, or timers
   **in-process by default** while the declared `target_platform` is multi-worker or
   container-scaled. "It installs" is not "it behaves correctly when replicated."

5. **Distractor discipline.** Do NOT extract a purely internal choice as a platform
   decision. A language version, a linter, a monorepo tool, a validation library, a
   CI matrix — these are not load-bearing-against-the-platform unless the artifact
   explicitly ties them to a platform constraint. Over-extraction produces false
   positives downstream; only extract what the source actually couples to the target.
   When unsure whether a choice is platform-coupled, record it but mark its claim as
   the narrow platform-coupling assertion only — not the whole tool choice.

   **Self-deferred decisions (gated only).** Route a choice to `open_questions` ONLY when
   the artifact BOTH (a) marks it unresolved/open/deferred (an open-question entry, a
   "TBD", a "to be selected in a later phase") AND (b) gates or blocks downstream work on
   resolving it (e.g. the plan blocks a later phase until it is decided). Then the artifact
   genuinely owns it — it is not a platform-reality refutation, so record it in
   `open_questions` with an honest *no-source*; emitting it as a finding would manufacture
   a false positive the producer skill already accounts for.
   If the deferral is **UNGATED** — the artifact says "TBD" but proceeds on the assumption
   anyway — do NOT park it. Extract it as a normal decision so verification defaults it to
   UNCONFIRMED → VIOLATION. An ungated deferral is exactly the proceeding-on-an-unconfirmed-
   assumption case that default-to-VIOLATION exists to catch; parking it would let a clean
   verdict hide an unresolved platform question.
   **Tie-breaker:** when you cannot tell whether a deferral is genuinely gated, treat it as
   UNGATED — extract → UNCONFIRMED → VIOLATION. Default-to-VIOLATION governs the judgment
   call: the cost of an unnecessary finding is recoverable at the human gate; a wrongly-parked
   ungated assumption is not.
   **Hand-off dependency (be aware):** a gated parked question never becomes a CONFORMANCE
   finding, so "did the artifact correctly gate on its own open question" is verified ONLY on
   the SPEC side — it relies on the producer spec carrying a self-gating-correctness criterion
   (e.g. `planning-code-tasks` V18 / CONTRADICTORY_PLAN_STATUS). A future producer lacking such
   a criterion would leave a gated deferral parked (conformance) AND unchecked (verification),
   surfaced only as the `open_questions_count` integer for the human.

6. **Mandatory source loading (anti-hallucination).** Every `claim` and `quote` must
   trace to a specific location in the artifact. If you cannot point to a line, you
   are inventing — do not add the decision.

At the end of this step, write the living progress tracker
`CONFORMANCE-REVIEW-{SESSION_ID}.md` with one row per decision marked
"[ ] TO BE VERIFIED":

```
# {project_name} -- Platform Decision Inventory
session: {SESSION_ID}
target_platform: {target_platform}
status: extracting

| ID | Category | Claim | Status |
|----|----------|-------|--------|
| DEC-01 | scheduling | in-process setInterval keeps tokens fresh | [ ] TO BE VERIFIED |
| DEC-02 | persistence | better-sqlite3 local file persists WhatsApp data | [ ] TO BE VERIFIED |
```

Verify the table row count equals the number of decisions in `REVIEW_INDEX`:
```
stated_count = rows in tracker table
actual_count = len(REVIEW_INDEX.decisions)
IF mismatch → fix stated_count before writing. LOG: "Fixed count: stated {N}, actual {M}".
```

## Source Fidelity Check (before writing)

- [ ] Every decision has a verbatim `quote` traceable to a specific artifact location — no invented snippets.
- [ ] Every decision sits in exactly one category from the seven-bucket table.
- [ ] Domain drift check: each `claim` is about platform-conformance, not a generic feature description.
- [ ] No distractors extracted (internal-only choices not coupled to the platform).
- [ ] Any dependency whose *runtime behavior* (not just existence) is load-bearing has a second decision in its behavioral category — not only an `sdk-package` row.
- [ ] Self-deferred choices are parked in `open_questions` ONLY when the artifact gates downstream work on them; ungated "TBD, proceeding anyway" deferrals remain extracted decisions (→ UNCONFIRMED → VIOLATION).
- [ ] Decision IDs are sequential `DEC-NN` in document order.
- [ ] Tracker table row count matches `len(REVIEW_INDEX.decisions)`.

## Post-Section Protocol

1. **Write** `{output_path}/CONFORMANCE-REVIEW-{SESSION_ID}.md`. Mandatory tool call. Do NOT defer.
2. **Update** `REVIEW_INDEX`: `decisions[]` (id, category, claim, quote, status=pending), `total_decisions`, `completed_decisions = 0`.
3. **Update** progress tracker: header `status: extracting`; every decision row "[ ] TO BE VERIFIED".
4. **Save** `REVIEW_INDEX` to `_progress.json` (RESUME support).
5. **Flush** the raw artifact text from memory. Retain only `REVIEW_INDEX`.
6. **Verify** `{output_path}/CONFORMANCE-REVIEW-{SESSION_ID}.md` exists and is non-empty.
7. **Log:** "Phase A COMPLETE. {N} load-bearing decisions extracted across {K} categories."
