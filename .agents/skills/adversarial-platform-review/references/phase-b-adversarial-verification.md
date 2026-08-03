# Adversarial Platform Review — Adversarial Verification

## Context Contract

- **Inputs:** `REVIEW_INDEX.decisions[]` (from Phase A: id, category, claim, quote, status=pending); `target_platform`; a live web-search / web-fetch capability.
- **Outputs:** Per-decision verdict written into `REVIEW_INDEX.decisions[]` (verdict, severity, source_url, status=complete); `{output_path}/CONFORMANCE-REVIEW-{SESSION_ID}.md` updated in-place per decision.
- **Carries Forward:** Each decision's `verdict`, `severity`, `source_url`, `status` in `REVIEW_INDEX`; `completed_decisions`.
- **Flush After:** Each decision's web-evidence text — drop after the verdict is recorded. Only the verdict fields + `source_url` survive.
- **Dependency:** Phase A must be COMPLETE (decisions extracted, tracker written).
- **H1 Title:** `# {project_name} -- Adversarial Verification Log`

## Mode-Specific Behavior

- **BUILD:** Verify every decision against live sources from scratch.
- **REPAIR:** For each decision, if no `REPAIR_DIRECTIVE` targets it, preserve its prior verdict/severity/source_url verbatim and skip re-verification. If a directive targets a decision (e.g. "re-check DEC-03 against the current changelog"), re-ground only that decision, rewrite its tracker row in place, leave the rest untouched.
- **RESUME:** On re-entry with a partial run, continue from the first decision whose `status` is `pending`; do not re-verify completed decisions.

## Content Generation Instructions

This is the load-bearing phase. The whole skill exists to do ONE thing well per
decision: attempt to refute it against a live source, and default to VIOLATION when
refutation-or-confirmation cannot be grounded.

This is a **single adversarial-grounded pass per decision**, graded by source
citation. Do NOT multi-sample, do NOT average scores, do NOT build a weighted
checklist — those are the sibling skill's job (`verifying-artifacts`). Here the
grade is binary: did you cite a current source.

```
FOR EACH decision in REVIEW_INDEX.decisions:

  IF mode == REPAIR AND no REPAIR_DIRECTIVE targets this decision:
    PRESERVE prior verdict/severity/source_url verbatim. CONTINUE.

  // Pattern 5: per-decision LIVE source load — never reuse a generic memory of the platform.
  FORMULATE the adversarial query. The stance, stated literally:
    "Attempt to refute that this assumption holds on {target_platform}. Default to
     VIOLATION if you cannot positively confirm it holds with a current source."

  RUN a live web search / fetch scoped by category (next section). Capture the
  source_url ACTUALLY consulted.

  DECIDE the verdict from grounded evidence ONLY:
    - CONFORMS    — a current source positively confirms the assumption holds on the target.
    - VIOLATION   — a current source refutes it.
    - UNCONFIRMED — no current source positively confirms it → treated as VIOLATION.

  ASSIGN severity to any VIOLATION/UNCONFIRMED (CONFORMS → severity null):
    - BLOCKER — will not function / provisions a non-existent product / data loss / non-conformant transport.
    - RISK    — works but fragile, deprecated, EOL, known-CVE, or limit-bound under realistic load.
    - MINOR   — cosmetic or low-impact non-conformance, INCLUDING currency drift: a newer
                major version exists but the declared pin is still supported and secure on
                the target runtime. ("Not the latest" is MINOR; "unsafe/unsupported" is RISK
                or BLOCKER.)

  // Pattern 6: pre-write fidelity gate
  FIDELITY CHECK before recording (see checklist below).

  UPDATE REVIEW_INDEX: verdict, severity, source_url, status=complete; completed_decisions += 1.
  UPDATE CONFORMANCE-REVIEW-{SESSION_ID}.md IN-PLACE: "[x] {verdict} ({severity}) -- {source_url}".
  FLUSH this decision's web-evidence text from memory.
  LOG: "DEC-{nn} ({category}): {verdict} {severity}."

  Do NOT stop. Process ALL decisions. Continue until completed_decisions == total_decisions.
```

### Per-category source strategy

Explain over prohibition: the category tells you *which kind of source is
authoritative*, so a confident-but-wrong memory cannot stand in for it.

| Category | Where the truth lives | What to refute |
|----------|----------------------|----------------|
| `persistence` | platform runtime/filesystem docs + the DB driver's docs | "does a local-file / in-instance store survive across invocations on this runtime?" |
| `scheduling` | platform scheduling/cron docs + runtime lifecycle docs | "does an in-process timer / this cron expression actually fire on this runtime?" |
| `transport` | platform's hosting docs + the protocol's current transport spec | "is this transport current/supported for hosted use on this platform, or legacy?" |
| `auth-token-lifecycle` | runtime lifecycle docs + the auth provider's token docs | "does an in-memory/in-process token survive the runtime's instance lifecycle?" |
| `third-party-api-tier` | the provider's CURRENT product / pricing / changelog pages | "does this branded product still exist under this name? are the claimed tier/limits current?" |
| `sdk-package` | the package registry (npm/PyPI/etc.) + the package's own docs | "does the exact package name exist? is this driver viable on the target runtime?" |
| `region-data-residency` | the platform's region list + compliance docs | "are the claimed regions/residency guarantees real and current?" |

PREFER official/primary sources (platform docs, provider changelogs, package
registries) over blogs and forum posts. A blog may surface a lead, but the cited
`source_url` should be the authoritative page when one exists.

### Why default-to-VIOLATION

Self-consistent artifacts can be uniformly wrong about their runtime (the motivating
failure). Low confidence that you *can* confirm something is exactly the
confident-but-wrong failure mode. So absence of a confirming source is not "probably
fine" — it is UNCONFIRMED, which is a VIOLATION. False positives (flagging a
conformant decision) are recoverable at the human gate; false negatives (passing a
broken decision) are the failure this skill exists to prevent.

### Handling ungroundable decisions

IF a web call fails, times out, or returns nothing groundable:
- `status = pending`; `verdict = UNCONFIRMED` (→ VIOLATION); register in `open_questions`.
- Do NOT fabricate a `source_url`. An empty or invented source is worse than an honest gap.
- Continue to the next decision. Do not abort the run for one ungroundable item.

## Source Fidelity Check (before writing each decision's verdict)

- [ ] `source_url` is real, consulted THIS run, AND topically about THIS claim — the page actually discusses the decision being verified, not an adjacent artifact (e.g. a driver's package page does not substantiate a managed-hosting / region / tier claim). A real-but-off-topic source counts as no source → demote to UNCONFIRMED.
- [ ] A `CONFORMS` verdict is backed by a positively-confirming source. If not, demote to `UNCONFIRMED` → VIOLATION.
- [ ] Severity separates currency drift (newer major exists but pin is supported & secure → MINOR) from fragility/EOL/CVE (→ RISK).
- [ ] `platform_reality` (to be written in Phase C) describes what the cited source says, not a guessed fact.
- [ ] Severity reflects impact (BLOCKER = broken/non-existent; RISK = fragile/deprecated; MINOR = cosmetic).
- [ ] The decision's `quote` is still the verbatim artifact snippet (unchanged from Phase A).
- [ ] No platform fact asserted from memory anywhere in the verdict.

## Post-Section Protocol

1. **Write** the in-place update to `{output_path}/CONFORMANCE-REVIEW-{SESSION_ID}.md` after EACH decision. Mandatory tool call. Do NOT batch.
2. **Update** `REVIEW_INDEX`: this decision's `verdict`, `severity`, `source_url`, `status=complete`; `completed_decisions += 1`.
3. **Update** progress tracker row: "[ ] TO BE VERIFIED" → "[x] {verdict} ({severity}) -- {source_url}".
4. **Save** `REVIEW_INDEX` to `_progress.json` after each decision (RESUME support).
5. **Flush** this decision's web-evidence text from memory. Retain only `REVIEW_INDEX`.
6. **Verify** the tracker row for this decision now shows a verdict and a source_url.
7. **Log:** "DEC-{nn} ({category}): {verdict} {severity}. {completed}/{total} verified."
