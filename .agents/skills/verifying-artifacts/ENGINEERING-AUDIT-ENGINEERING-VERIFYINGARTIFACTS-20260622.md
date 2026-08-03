# verifying-artifacts — Engineering Audit
session: ENGINEERING-VERIFYINGARTIFACTS-20260622
mode: BUILD
date: 2026-06-22
source: new skill (VERIFICATION-LOOP-DESIGN-PLAN.md §4 Phase 2)
status: complete

## Session Summary
- skill_name: verifying-artifacts
- output_path: .agents/skills/verifying-artifacts
- sdlc_phase: testing
- downstream_consumers: human-quality-gate
- generation_shape: section-shape (one multi-section VERIFICATION-REPORT)
- output_pattern: single_file (+ verifiers/ sidecar for generated programs)
- stepwise_invoked: true
- exploration_heavy: false (consumes bounded artifact + spec + findings JSON; no broad repo sweep)
- non_ascii_fallback_required: true (artifact-under-test may contain codepoints > 127)
- routing_table_entry: §2 → §10 → §10.5 → §11 (+ §7 if REPAIR)
- files_written: 7 (SKILL.md + 4 references + evals.json + this audit) + 2 registry edits
- total_lines: ~1074 (skill + refs + evals)
- pattern_compliance: 9/9 applicable patterns present (P1-P7 universal, P8 section-shape, P9 sidecar; P10 n/a)
- anti_patterns_fixed: 0 (clean generation; all 19 checks passed on first author)
- evals_generated: 4

## Pattern Compliance
| Pattern ID | Pattern Name | Applicability | Status | Evidence |
|------------|-------------|---------------|--------|----------|
| P1 | Write-Flush-Forget | universal | present | Per-item WRITE...MANDATORY TOOL CALL in Step 4 verifier loop + Step 5 scoring loop; "FLUSH ... from memory" after each; Entry Rule #6 forbids re-reading REPORT. |
| P2 | Carry-Forward Index | universal | present | `VERIFY_INDEX` struct defined before Workflow; ids/scores/status only, never full prose. |
| P3 | REPAIR Folder Reuse | universal | present | Step 1 REPAIR branch: "find existing VERIFICATION-REPORT-*.md", "Never mkdir for REPAIR", SESSION_ID from PRIOR_FILE filename. |
| P4 | Surgical REPAIR | universal | present | REPAIR_DIRECTIVES parsing in Step 1; phase-b/c/d REPAIR sub-sections skip untargeted items; phase-d bumps version + appends Repair History (§7). |
| P5 | Mandatory Source Loading | universal | present | "LOAD this item's source" at top of Step 4, Step 5, and each ref-file loop (Pattern 5 callouts). |
| P6 | Per-Unit Fidelity Check | universal | present | Pre-write fidelity checks in phase-a/b/c/d Source Fidelity Check sections (id-uniqueness, source_url presence, stdlib-only, no platform-fact hardcode). |
| P7 | Living Progress Tracker | universal | present | Section-shape `_progress.json` written FIRST ACTION; flipped per section; COMPLETED at LAST ACTION. |
| P8 | Section-Shape Protocol | section-shape | present | Step 6 cites §10 Phase A skeleton-first within 5 tool calls, ASCII stub, §10.4 one-section-per-Edit, §10.5.1 non-ASCII fallback, §10.6 CONTINUE; `_progress.json` uses skeleton_written + sections{}. |
| P9 | Harness Output Sidecar | stepwise_invoked | present | Step 8 cites §11, enumerates verification_verdict / verification_report_path / failed_blocker_count, §11.1.1 path-correctness, strict ordering, no tool calls after sidecar. |
| P10 | Delegated Exploration | exploration_heavy=false | n/a | Skill consumes a bounded input set; no broad read-only codebase sweep at input loading. §12 deliberately omitted from routing row. |

## Anti-Patterns Report
| ID | Name | Severity | Found In | Fix Applied |
|----|------|----------|----------|-------------|
| AP-01..AP-10 | universal checks | — | — | none found — per-item write+flush, no SESSION_ID in folder, per-unit source load, index-before-flush, surgical REPAIR, no {{}}, tech-neutral, count verification, continuation mandates, pre-write fidelity gates all present. |
| AP-11 | wrong _progress schema | — | — | none — section-shape variant (skeleton_written + sections{}); grep for list-shape "items" in runtime schema = 0. |
| AP-12 | missing skeleton-first | — | — | none — Step 6 cites §10 Phase A within 5 tool calls, ASCII stub, skeleton_written flip. |
| AP-13 | missing extraction pass | — | n/a | inputs are small/bounded (one artifact + one spec + one findings JSON); §10.2 extraction-pass trigger not met, so not required. |
| AP-14 | bash-mutation of spec | — | — | none — grep for sed/awk/cat>/python3<< targeting REPORT = 0; Step 6 mandates Write(skeleton)/Edit(sections). |
| AP-15 | non-ASCII fallback missing | non_ascii=true | — | present — §10.5.1 callout in Step 6 (artifact-under-test may carry >127 codepoints). |
| AP-16 | CONTINUE-on-re-entry missing | section-shape | — | none — Step 6 CONTINUE note distinguishes state-driven CONTINUE from directive-driven REPAIR. |
| AP-17 | sidecar missing | stepwise=true | — | none — Step 8 present and final. |
| AP-18 | mechanics duplication | universal | — | none — §10/§11 cited as short callouts + skill-specific contract bits (section list, dependency graph, output param names); mechanics not restated. |

## Validation Greps (Phase E)
- `SESSION_ID = "` string-literal assignment: 0 matches (re-run contract intact).
- `SESSION_ID = ...(YYYYMMDD|timestamp|UUID|now()|date())`: 0 matches.
- `_shared` references: 0 matches.
- `{{ }}` placeholder syntax: 0 matches.
- bash-mutation of REPORT (sed/awk/cat>/heredoc): 0 matches.

## Reference Files Gate
| File | Sections Present | Status |
|------|-----------------|--------|
| references/phase-a-checklist-generation.md | 5/5 (Context Contract 6/6 sub-fields) | pass |
| references/phase-b-program-verifier-generation.md | 5/5 (Context Contract 6/6) | pass |
| references/phase-c-scoring-aggregation.md | 5/5 (Context Contract 6/6) | pass |
| references/phase-d-report-assembly.md | 5/5 (Context Contract 6/6) | pass |

## Files Written
| Path | Lines | Status |
|------|-------|--------|
| .agents/skills/verifying-artifacts/SKILL.md | 549 | written |
| .agents/skills/verifying-artifacts/references/phase-a-checklist-generation.md | 124 | written |
| .agents/skills/verifying-artifacts/references/phase-b-program-verifier-generation.md | 131 | written |
| .agents/skills/verifying-artifacts/references/phase-c-scoring-aggregation.md | 103 | written |
| .agents/skills/verifying-artifacts/references/phase-d-report-assembly.md | 123 | written |
| .agents/skills/verifying-artifacts/evals/evals.json | 44 | written |
| .agents/skills/verifying-artifacts/ENGINEERING-AUDIT-ENGINEERING-VERIFYINGARTIFACTS-20260622.md | — | written |
| context-pack/execution-protocol.md (Artifact Type Registry row) | +1 | edited |
| context-pack/execution-protocol.md (Skill routing special-route row) | +1 | edited |

## Acceptance / Eval Wiring
- Eval 1 (acceptance) runs the skill on `fixtures/socialmcp-conformance/prefix-plan.md` with `expected-findings.json` fed as `conformance_findings_path`. Expected: C-cron item verifiability=PROGRAM with a generated verifier returning FAIL (exit non-zero) — not a judge guess; B1-B4 consumed as inverted CONFORMANCE items at weight 100 and surfaced FAILED with source_urls; failed_blocker_count >= 5; verdict FAILED. Distractors not raised as false BLOCKERs.
- Eval 2 (clean) runs on the real post-fix plan (absolute path in fixture README); cron verifier PASSes on valid */30; B1-B4 conform; failed_blocker_count = 0; verdict PASSED / PASSED_WITH_FINDINGS, no false BLOCKERs.
- Eval 3 (REPAIR) re-scores only the cron item after a fix, recomputes verdict, preserves untargeted items, bumps version + Repair History.
- Eval 4 (reduced-coverage) omits conformance_findings_path; checklist is spec-only; report flags reduced_coverage: true.

## How the program-verifier path + cron eval are wired
- Step 4 (phase-b) implements the RLCF Fig 6 gate: generate a stdlib-only verifier ONLY when 100% sure the check is exact (syntax/format/presence/absence); default to JUDGE ~95%. A cron-syntax finding is the canonical PASS case: its CONFORMANCE item is promoted PROGRAM, a per-field range-check program is generated under verifiers/, and Step 5 runs it (exit code → 0/100 boolean). For `*/100 * * * *` the program returns FAIL deterministically; for `*/30 * * * *` it returns PASS. phase-b carries the reference cron-verifier shape. This replaces grep/AST NFR gates for exactly-checkable criteria.

## Open Questions
| ID | Type | Description | Impact |
|----|------|-------------|--------|
| OQ-1 | dependency | Eval 1 uses `planning-code-tasks/SKILL.md` as `output_spec_source` (the producer of the SocialMCP plan). If a project supplies a `quality_criteria_path` instead, SPEC items derive from that file — behavior is identical, only the source path differs. | low |
| OQ-2 | runtime | If the executor lacks both python3 and node, every PROGRAM item degrades to JUDGE (status: degraded) and the C-cron determinism guarantee is lost for that run; the report records the degradation. Prerequisites note this. | medium |
| OQ-3 | downstream | Phase 4 VGT engine (separate, stepwise repo) will consume `verification_verdict` to gate flow; until then the verdict is advisory and the human gate is terminal. Out of scope for this skill. | none (by design) |
