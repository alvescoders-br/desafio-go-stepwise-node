# researching-adrs — Engineering Audit

session: 20260412-150000
mode: refactor
date: 2026-04-12
source: .agents/skills/researching-adrs/SKILL.md (v3.0.0)
status: complete

## Session Summary

- skill_name: researching-adrs
- output_path: .agents/skills/researching-adrs/
- files_written: 6
- total_lines: ~1,080
- pattern_compliance: 7/7 patterns present
- anti_patterns_fixed: 3
- evals_generated: 3

## Pattern Compliance

| Pattern ID | Pattern Name | Status | Evidence |
|------------|-------------|--------|---------|
| P1 | Write-Flush-Forget | present | "WRITE adrs/adr-{NNN}-{slug}.md — MANDATORY TOOL CALL" in Step 4 loop; "FLUSH all ADR text from memory" |
| P2 | Carry-Forward Index | present | "ADR_INDEX — Carry-Forward Contract" section with full struct definition |
| P3 | REPAIR Folder Reuse | present | "NOTE: output_path MUST already exist. Never mkdir for REPAIR." in Step 1 |
| P4 | Surgical REPAIR | present | "Parse failure_feedback → REPAIR_DIRECTIVES" in Step 1; "IF MODE == REPAIR AND no REPAIR_DIRECTIVE targets this ADR: SKIP" in Step 4 |
| P5 | Mandatory Source Loading | present | Per-ADR "LOAD decision category, scope, affected_bcs" + "LOAD relevant BC details" in Step 4 loop |
| P6 | Per-Unit Fidelity Check | present | "Source Fidelity Check (BEFORE writing)" 7-point gate in phase-b-adr-generation.md |
| P7 | Living Progress Tracker | present | "Write 00-index.md (Living Progress Tracker)" in Step 2; "UPDATE 00-index.md" in Step 4 loop |

## Anti-Patterns Report

| ID | Name | Severity | Found In | Fix Applied |
|----|------|----------|---------|-------------|
| AP-07 | Prose-heavy Nygard template | critical | Original Step 5 Phase 2 (lines 510-642) | Replaced entire per-ADR template with agent-native structured fields: tables for forces, constraints, alternatives, consequences, quality_impact. Context/Decision sections now use key-value pairs. |
| AP-08 | Count verification partial | medium | Original Step 6 (line 827) | Added explicit "VERIFY stated_count == actual_count" gate in phase-c-manifest-assembly.md count_verification section |
| AP-09 | Weak continuation mandate | low | Original Step 5 (line 686) | Strengthened to "Do NOT stop. Process ALL ADRs in REMAINING_ADRS. Continue until all are written." |

## Classification Log (REFACTOR mode)

| Section/Field | Verdict | Reason |
|--------------|---------|--------|
| YAML Frontmatter | STRUCTURAL | Version bumped 3.0.0 → 4.0.0; tags updated |
| Quick Start | AGENT_ESSENTIAL | Kept; condensed |
| Why This Architecture | STRUCTURAL | Motivational prose removed; kept rationale in condensed form under Output Architecture |
| Parameters table | AGENT_ESSENTIAL | Kept verbatim; added source_path convention note |
| Chunked Execution | STRUCTURAL | Kept; condensed |
| Step 1 Persona narration | HUMAN_ONLY | Removed: "ADR Architect Agent — FIC Methodology" persona block. Agent doesn't need identity narration. |
| Step 1 FIC Principles block | GOVERNANCE | Removed: methodology description. Zero Invention Policy kept as one line. |
| Step 1 Context Discipline RPI | STRUCTURAL | Absorbed into write-flush-forget protocol |
| Step 1 Global Conventions (PlantUML rules) | AGENT_ESSENTIAL | Moved to phase-b-adr-generation.md (domain logic for diagram generation) |
| Step 1 Style directive | HUMAN_ONLY | Removed: "Formal third person. Minimal verbosity." — formatting preference for prose output that no longer exists |
| Step 2 ADR_CONTEXT extraction | AGENT_ESSENTIAL | Kept verbatim |
| Step 2 ADR_DECISIONS list | AGENT_ESSENTIAL | Kept: 12 mandatory categories are domain knowledge |
| Step 3 Upstream Consistency Rules | AGENT_ESSENTIAL | Kept inline in SKILL.md — referenced across all phases |
| Step 4 Phase A Tech Stack Eval | AGENT_ESSENTIAL | Extracted to phase-a-tech-stack-evaluation.md |
| Step 5 Phase B Per-ADR Nygard template | HUMAN_ONLY (critical) | Context/Decision/Consequences prose sections replaced with structured tables and key-value pairs |
| Step 5 Phase B PlantUML templates | AGENT_ESSENTIAL | Moved to phase-b-adr-generation.md (domain rules) |
| Step 5 Phase B Diagram validation | VALIDATION | Moved to phase-b reference file as pre-write gate |
| Step 6 Manifest structure | AGENT_ESSENTIAL | Extracted to phase-c-manifest-assembly.md |
| Step 6.5 Quality Validation | VALIDATION | Absorbed into phase-c as pre-write gate |
| Step 7 Audit template | STRUCTURAL | Extracted to phase-d-validation-audit.md |
| Step 7 Memory Bank writes | STRUCTURAL | Kept as thin callout per Pattern 8 |
| Rendering section | HUMAN_ONLY | Kept as one-liner reference to humanize-spec |
| Reference files (listed but missing) | STRUCTURAL | Created all 4 reference files that were listed but never existed |

## Reference Files Gate

| File | Sections Present | Status |
|------|-----------------|--------|
| references/phase-a-tech-stack-evaluation.md | 5/5 (Context Contract, Mode-Specific, Content, Fidelity Check, Post-Section) | pass |
| references/phase-b-adr-generation.md | 5/5 | pass |
| references/phase-c-manifest-assembly.md | 5/5 | pass |
| references/phase-d-validation-audit.md | 5/5 | pass |

## Files Written

| Path | Lines | Status |
|------|-------|--------|
| SKILL.md | ~340 | written |
| references/phase-a-tech-stack-evaluation.md | ~110 | written |
| references/phase-b-adr-generation.md | ~280 | written |
| references/phase-c-manifest-assembly.md | ~190 | written |
| references/phase-d-validation-audit.md | ~100 | written |
| evals/evals.json | ~60 | written |
| ENGINEERING-AUDIT-20260412-150000.md | this file | written |

## Open Questions

| ID | Type | Description | Impact |
|----|------|-------------|--------|
| — | — | None. All three initial OQs reviewed and dismissed: (1) downstream consumers read manifest + YAML frontmatter, not prose body — format change transparent; (2) no `adrs` rendering profile exists in humanize-spec; (3) REPAIR targets sections by heading name which is unchanged between v3 and v4. | — |
