# adversarial-platform-review — Engineering Audit
session: ENGINEERING-ADVERSARIALPLATFORMREVIEW-20260622
mode: BUILD
date: 2026-06-22
source: new skill (VERIFICATION-LOOP-DESIGN-PLAN.md §4 Phase 1)
status: complete

## Session Summary
- skill_name: adversarial-platform-review
- output_path: .agents/skills/adversarial-platform-review
- generation_shape: list-shape (single bounded artifact in → one cited findings list + verdict out)
- files_written: 7 (SKILL.md, 4 references, evals.json, audit) + 2 registry edits
- total_lines: ~906 (SKILL.md 451; refs 116+116+89+134)
- pattern_compliance: 9/10 present (P1-P7 universal present; P8 n/a list-shape; P9 present; P10 n/a not exploration-heavy)
- anti_patterns_fixed: 0 (clean on first generation — all gate greps passed)
- evals_generated: 3 (acceptance + negative-clean + REPAIR)

## Architecture Decisions
| Decision | Value | Rationale |
|----------|-------|-----------|
| generation_shape | list-shape | Produces one bounded findings list + verdict, not a multi-section spec from large unstructured inputs. |
| output_pattern | single_file | One findings JSON + one review + one audit per run; bounded list, no manifest tree. |
| reference_file_count | 4 | Grouped by phase: extraction, verification, emission, verdict/sidecar. |
| chunking_needed | false | Decision count per artifact is modest; per-decision write-flush covers any volume. |
| carry_forward_index | REVIEW_INDEX | IDs/verdicts/source_urls/status only — never full web-evidence text. |
| stepwise_invoked | true | Invoked as a capability review step (Phase 3 wires it into code-development). → P9 applies. |
| exploration_heavy | false | Single bounded artifact input; web grounding is THIS agent's load-bearing work, not a delegable cheap repo sweep. → P10 n/a, no §12. |
| non_ascii_fallback_required | false | English output; §10.5 tool discipline still cited for JSON-via-Write. |
| routing_table_entry | §2 → §10.5 → §11 | list-shape, Stepwise-invoked, single-report. |

## Pattern Compliance
| Pattern ID | Pattern Name | Applicability | Status | Evidence |
|------------|-------------|---------------|--------|----------|
| P1 | Write-Flush-Forget | universal | present | Step 3 per-decision "UPDATE ... FLUSH this decision's web-evidence" loop; Phase B Post-Section Protocol "do NOT batch". |
| P2 | Carry-Forward Index | universal | present | `REVIEW_INDEX` struct defined in SKILL.md (IDs/verdicts/paths only). |
| P3 | REPAIR Folder Reuse | universal | present | Step 1 "Never mkdir for REPAIR"; SESSION_ID extracted from PRIOR_FILE filename. |
| P4 | Surgical REPAIR | universal | present | `REPAIR_DIRECTIVES` parse + per-decision skip-if-untargeted; Phase D Repair History entry + version bump self-check. |
| P5 | Mandatory Source Loading | universal | present | Step 3 per-decision LIVE source load ("never reuse a generic memory of the platform"). |
| P6 | Per-Unit Fidelity Check | universal | present | Pre-write fidelity gate in Step 3 + Phase B checklist (source real, CONFORMS needs confirming source, verbatim quote). |
| P7 | Living Progress Tracker | universal | present | CONFORMANCE-REVIEW-{SESSION_ID}.md written in Step 2 with "[ ] TO BE VERIFIED", updated in-place per decision in Step 3. |
| P8 | Section-Shape Protocol | n/a (list-shape) | n/a | No multi-section spec; §10 not applicable. |
| P9 | Harness Output Sidecar | stepwise_invoked | present | Step 5 §11 sidecar: conformance_verdict, conformance_findings_path, blocker_count; §11.1.1 path verification; strict ordering; no tool calls after. |
| P10 | Delegated Exploration | n/a (not exploration-heavy) | n/a | Single bounded artifact; web grounding is core load-bearing work, not delegable. |

## Anti-Patterns Report
| ID | Name | Severity | Found In | Fix Applied |
|----|------|----------|---------|-------------|
| — | (none) | — | — | All 19 checks passed on first generation. |

### Gate evidence (Phase E mandated greps — all zero-match except the prohibition text)
- `grep SESSION_ID = "` → 0 matches (no string-literal/date/UUID assignment).
- `grep SESSION_ID = .*(YYYYMMDD|timestamp|UUID|now()|date())` → 0 matches.
- `grep _shared` → 0 matches.
- `grep {{variable}}` → 0 matches.
- `grep sed/awk/python3<<EOF/cat >` → 1 hit, which is the §10.5 PROHIBITION text in phase-c (instructing NOT to use shell mutation) — not a violation (AP-14 pass).
- `_progress.json` → list-shape schema (`total`/`completed`/`items[]`) matches generation_shape (AP-11 pass).
- Both FOR EACH loops carry "Do NOT stop. Process ALL decisions." (AP-09 pass).

## Binding-contract conformance (graded items from the build prompt)
| Requirement | Status | Where |
|-------------|--------|-------|
| Inputs: artifact_path (req), target_platform (req), declared_stack/external_dependencies (opt, else extract) | present | Parameters table; Step 2 extraction fallback. |
| Behavior 1: extract + 7-category buckets | present | Step 2 + phase-a table (persistence, scheduling, transport, auth-token-lifecycle, third-party-api-tier, sdk-package, region-data-residency). |
| Behavior 2: adversarial verify; literal refute-stance prompt; default-to-VIOLATION | present | Step 3 + phase-b (stance quoted verbatim). |
| Behavior 3: cite a source_url per verdict; never assert from memory (Principle #9) | present | Entry Rule 3; Upstream Rules 1-2; per-decision fidelity gate. |
| Behavior 4: single adversarial-grounded pass, graded by citation; NO judge_samples/mean-of-N | present | Entry Rule 4 explicitly excludes sampling and defers it to verifying-artifacts. |
| Output conformance_verdict: [CONFORMS, CONFORMS_WITH_RISKS, VIOLATIONS_FOUND], required | present | Output Parameters table (closed-set Values column). |
| Output conformance_findings_path: JSON list of EXACTLY {decision, claim, platform_reality, severity∈[BLOCKER,RISK,MINOR], fix, source_url} — frozen shape | present | Step 4 + phase-c (fields FROZEN, six-key validation). |
| Output blocker_count: integer | present | Output Parameters table. |
| Cross-family note: model-agnostic but intended to run on a different family, set at step level | present | "Cross-Family Note" section in SKILL.md. |
| No live web run during authoring; no hardcoded platform facts | honored | Skill names categories only; zero platform answers baked in. |

## Reference Files Gate
| File | Sections Present | Status |
|------|-----------------|--------|
| references/phase-a-decision-extraction.md | 5/5 (Context Contract 6/6 fields) | pass |
| references/phase-b-adversarial-verification.md | 5/5 (Context Contract 6/6 fields) | pass |
| references/phase-c-findings-emission.md | 5/5 (Context Contract 6/6; H1 N/A — JSON output, noted) | pass |
| references/phase-d-verdict-and-sidecar.md | 5/5 (Context Contract 6/6 fields) | pass |

## Files Written
| Path | Lines | Status |
|------|-------|--------|
| .agents/skills/adversarial-platform-review/SKILL.md | 451 | written |
| .agents/skills/adversarial-platform-review/references/phase-a-decision-extraction.md | 116 | written |
| .agents/skills/adversarial-platform-review/references/phase-b-adversarial-verification.md | 116 | written |
| .agents/skills/adversarial-platform-review/references/phase-c-findings-emission.md | 89 | written |
| .agents/skills/adversarial-platform-review/references/phase-d-verdict-and-sidecar.md | 134 | written |
| .agents/skills/adversarial-platform-review/evals/evals.json | — (valid JSON, 3 evals) | written |
| .agents/skills/adversarial-platform-review/ENGINEERING-AUDIT-ENGINEERING-ADVERSARIALPLATFORMREVIEW-20260622.md | — | written |
| context-pack/execution-protocol.md (Artifact Type Registry row) | +1 row | edited |
| context-pack/execution-protocol.md (Skill → Required Sections routing row) | +1 row | edited |

## Fixture wiring (evals)
- Eval 1 (acceptance): runs on `fixtures/socialmcp-conformance/prefix-plan.md`, target_platform="Vercel serverless"; expects VIOLATIONS_FOUND reproducing B1-B4 (per `expected-findings.json`) with cited sources; MUST NOT flag any `distractors_must_not_flag` item.
- Eval 2 (negative/clean): runs on the real post-fix plan (absolute path from fixture README); expects CONFORMS / CONFORMS_WITH_RISKS, blocker_count 0.
- Eval 3 (REPAIR): adds a missed region-data-residency decision + re-grounds B3 source; expects surgical repair, SESSION_ID reuse, Repair History + version bump.

## Open Questions
| ID | Type | Description | Impact |
|----|------|-------------|--------|
| OQ-1 | scope | C-cron (program-verifiable) MAY surface here but is formally the sibling skill's job; this skill is not penalized for catching or missing it. | low — by design (plan §4 Phase 1). |
| OQ-2 | integration | Cross-family executor is set at the capability step level (Phase 3), not in this skill; if a run lacks a second executor family it falls back to a different `model` (documented in plan risk register). | low — handled at wiring time. |

## Generation Summary
9/10 patterns present (P8, P10 n/a by shape). 0 anti-patterns required fixing. 3 evals generated. 2 registry updates applied via Edit. Binding contract fully encoded and graded above. Status: COMPLETE.
