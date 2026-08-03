# verifying-artifacts — Checklist Generation

## Context Contract

- **Inputs:** `SPEC_TEXT` (from `output_spec_source`), `CONFORMANCE_FINDINGS` (from `conformance_findings_path`, or `[]`), `ARTIFACT_TEXT`, `VERIFY_INDEX`
- **Outputs:** populated `VERIFY_INDEX.items[]` (ids, source, source_url, verifiability, weight, status: pending); the `checklist` section body of `VERIFICATION-REPORT-{SESSION_ID}.md`
- **Carries Forward:** `VERIFY_INDEX.items[]` metadata and `VERIFY_INDEX.conformance_present`
- **Flush After:** `SPEC_TEXT` and the raw `CONFORMANCE_FINDINGS` JSON once every criterion/finding has been turned into an item — only `VERIFY_INDEX.items[]` survives
- **Dependency:** Step 2 (Load Inputs & Detect Coverage) must be COMPLETE
- **H1 Title:** `# {project_name} -- Verification Checklist`

## Mode-Specific Behavior

- **BUILD:** Generate the full checklist from scratch by merging the three sources.
- **REPAIR:** Load the existing `checklist` section from the SAME report file. Apply ONLY directives that target checklist items (by item id or by source). Preserve untargeted items verbatim. Rewrite the section IN PLACE. Do not renumber surviving ids.
- **RESUME:** If `_progress.json.sections.checklist == "complete"`, SKIP — the checklist is already authored. Re-author only if a directive targets it.

## Content Generation Instructions

The checklist is ONE list of atomic, weighted, yes/no items merging three sources.
Each item is `{ id, question, weight, verifiability ∈ [PROGRAM, JUDGE], source, source_url? }`.

Use structured fields (a table), not prose, because the scoring step and the human gate
read item rows programmatically — `id`, `weight`, and `verifiability` are matched
exactly. Prose would force natural-language parsing and blur item boundaries.

### Source (a): SPEC items — candidate-based generation (RLCF §2)

`source: SPEC`. The candidate-based method produces items that catch *real* failure
modes instead of restating the spec:

```
FOR EACH criterion in SPEC_CRITERIA:
  LOAD the criterion text from SPEC_TEXT (Pattern 5 — per-item source load).
  1. Imagine 2-3 deliberately-flawed drafts of the artifact for THIS criterion
     (a stub, a hand-wave, a wrong-but-plausible value, a missing section).
  2. Enumerate the concrete failure mode each flawed draft exhibits.
  3. Turn EACH distinct failure mode into ONE atomic yes/no item phrased as a
     PASS-condition (true = the artifact is good on that axis).
  4. weight: acceptance-critical criterion → 90-100; supporting → 40-75.
  5. verifiability: default JUDGE. Promote to PROGRAM only per phase-b's 100%-sure gate
     (syntax/format/presence/absence) — NOT for semantic criteria.
  ADD each item to VERIFY_INDEX.items.
  Do NOT stop. Process ALL criteria.
```

WHY candidate-based: a checklist that merely echoes "the artifact has section X" passes
stubs. Enumerating how a flawed draft would fail produces items a stub cannot satisfy —
this is what the universal anti-gaming item generalizes.

**Self-gating expectation (cross-layer contract).** Decisions the artifact defers *and
gates downstream work on* are parked by the discovery layer as open questions and never
arrive here as CONFORMANCE findings. So "did the artifact correctly gate on its own
blocking open question" is checkable ONLY as a SPEC item. The producer spec is expected to
declare a gating-correctness criterion (e.g. `planning-code-tasks` V18 — a plan may not be
PROCEED/CONDITIONAL while an implementability-gating question is unresolved). If
`SPEC_CRITERIA` contains such a criterion, generate its item normally; if it is ABSENT
while the artifact clearly defers-and-gates, record the gap in `open_questions` (Zero
Invention forbids inventing the criterion) so the missing self-gating check is visible,
not silently assumed.

### Source (b): REALITY items — consume conformance findings (the Phase-1 handoff)

`source: CONFORMANCE`. This is the explicit DISCOVERY → VERIFICATION handoff. Consume
the handoff schema EXACTLY: `{decision, claim, platform_reality, severity, fix,
source_url}`, `severity ∈ [BLOCKER, RISK, MINOR]`. Do not read or invent other fields.

```
FOR EACH finding in CONFORMANCE_FINDINGS:
  LOAD the finding (Pattern 5).
  Invert it into ONE pass-condition item:
    question = "Does the artifact's {finding.decision} conform to {finding.platform_reality}?"
    weight   = severity→weight: BLOCKER → 100, RISK → 75, MINOR → 40   (no other mapping)
    verifiability = JUDGE by default; promote to PROGRAM ONLY when the finding is
                    exactly checkable (e.g. a cron-syntax finding → a cron verifier;
                    a package-existence finding → a manifest-presence verifier).
    source = CONFORMANCE; source_url = finding.source_url (carry for traceability).
  ADD to VERIFY_INDEX.items.
  Do NOT stop. Process ALL findings.
```

When inverting a **currency/version** finding, phrase the pass-condition around
*"uses a supported, secure version of X on the target runtime"* — not *"uses the latest
major of X."* Being current is not the acceptance bar; being supported and secure is, so
a supported-but-not-latest pin scores honestly instead of being forced low.

WHY inversion: discovery emits a *violation* statement; the checklist scores a
*pass-condition*. Inverting once, at intake, lets scoring treat CONFORMANCE and SPEC
items uniformly. These items are the ONLY way platform-reality gaps enter the
checklist — they are not derivable from the artifact's own text.

**Reduced coverage:** when `CONFORMANCE_FINDINGS == []` (no discovery step ran), the
checklist is spec-items-only. Set `VERIFY_INDEX.conformance_present = false` and ensure
the `findings` section will carry `reduced_coverage: true`. This is a documented
coverage gap, not an error.

### Source (c): Universal anti-gaming item

`source: ANTIGAMING`. Append EXACTLY ONE, always, every checklist:
```
question = "Does the artifact actually satisfy the spec rather than a high-level
            overview / stub / hand-wave?"
weight = 100
verifiability = JUDGE
```
This is the anti-"Ralph Wiggum" guard: it fails artifacts that look complete but are
hollow, independent of any single criterion.

### Item id assignment & count verification

Assign ids `CHK-001, CHK-002, ...` in generation order (SPEC items, then CONFORMANCE
items, then the single ANTIGAMING item). At the end of this section, verify:
```
stated_count   = count in the checklist table
actual_count   = count(VERIFY_INDEX.items)
expected_count = count(SPEC items) + count(CONFORMANCE_FINDINGS-derived items) + 1
IF stated_count != actual_count OR actual_count < expected_count → fix before writing.
LOG: "Checklist: stated {N}, actual {M} (SPEC {a} / CONFORMANCE {b} / ANTIGAMING 1)."
```

## Source Fidelity Check (before writing)

- [ ] Every SPEC item traces to a criterion in `SPEC_TEXT` — no invented acceptance criteria
- [ ] Every CONFORMANCE item traces to exactly one finding; carries that finding's `source_url`
- [ ] No CONFORMANCE item asserts a platform fact from the verifier's own memory (it only inverts the finding)
- [ ] Exactly one ANTIGAMING item, weight 100
- [ ] Every weight is in 0-100; CONFORMANCE weights follow the severity map exactly
- [ ] Every item id is unique; `verifiability ∈ {PROGRAM, JUDGE}`
- [ ] `reduced_coverage` flagged when no findings were supplied
- [ ] All gaps (malformed findings, missing criteria) registered in open_questions, not silently dropped

## Post-Section Protocol

1. **Write** the `checklist` section into `{output_path}/VERIFICATION-REPORT-{SESSION_ID}.md` via one targeted `Edit`. Mandatory tool call. Do NOT defer.
2. **Update** `VERIFY_INDEX`: `items[]` (each with id, source, source_url, verifiability, weight, status: pending), `total_items`, `conformance_present`.
3. **Update** progress tracker: `_progress.json.sections.checklist` → `"complete"`.
4. **Save** `VERIFY_INDEX` to `_progress.json`.
5. **Flush** `SPEC_TEXT` and raw `CONFORMANCE_FINDINGS` from memory. Retain only `VERIFY_INDEX`.
6. **Verify** the file exists at `{output_path}/VERIFICATION-REPORT-{SESSION_ID}.md` and is non-empty.
7. **Log:** "Checklist complete. {N} items ({a} SPEC / {b} CONFORMANCE / 1 ANTIGAMING)."
