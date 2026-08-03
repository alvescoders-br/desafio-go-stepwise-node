# Phase C — Manifest Assembly (ADR-SPEC)

## Context Contract

- **Inputs:** ADR_INDEX (completed_adrs, technology_eval, cross_ref_map, all phase_status complete); ADR_CONTEXT (for coverage validation against bounded_contexts, prd_nfr_ids, prd_risks, prd_assumptions)
- **Outputs:** `{adrs_path}/ADR-SPEC-{SESSION_ID}.md` — the manifest downstream agents always load
- **Carries Forward:** ADR_INDEX.phase_status.C = "COMPLETE"
- **Flush After:** Manifest text — WRITE immediately, then flush
- **Dependency:** Phase B must be COMPLETE (ADR_INDEX.phase_status.B = "COMPLETE")
- **H1 Title:** `# {project_name} — ADR Specification`

## Mode-Specific Behavior

- **BUILD:** Generate manifest from scratch using ADR_INDEX data.
- **REPAIR:** If REPAIR_DIRECTIVE targets "manifest" or "global": regenerate from current ADR_INDEX. Otherwise: SKIP — preserve existing manifest.

---

## Manifest Structure

The manifest is the index that downstream agents always load. It contains decision
summaries and cross-references — never full ADR text. Generate each section in order.

### Header

```markdown
# {project_name} — ADR Specification

version: {version}
session: {SESSION_ID}
mode: {MODE}
date: {ISO_DATE}
total_adrs: {count from ADR_INDEX.completed_adrs}
categories_covered: {count of distinct categories}
```

### tech_stack_evaluation

Reproduce the full evaluation from ADR_INDEX.technology_eval:

```markdown
## tech_stack_evaluation

### evaluation_matrix
| Layer | Category | Option A | Option B | Option C | Recommended | Score | ADR Ref |
Source: ADR_INDEX.technology_eval — one row per layer.

### scoring_detail
FOR EACH layer in ADR_INDEX.technology_eval:
  | Criterion | Option A | Option B | Option C |
  Performance, Scalability, Team Expertise, Cost/TCO, Community, Licensing.

### tco_analysis
| Component | Year 1 | Years 2-3 | Training | Total 3Y |

### governance_constraints
| Constraint | Source | Impact on Recommendation |
(Or: status: "No organizational constraints provided.")
```

### adr_catalog

```markdown
## adr_catalog
| ADR | Title | Category | Status | Decision Summary | Affected BCs | File |
```

Source: ADR_INDEX.completed_adrs — one row per ADR.
`Decision Summary` = the `chosen` one-liner from each ADR's decision section.
This table is the primary lookup for downstream agents.

### cross_reference_map

```markdown
## cross_reference_map
| ADR | Related ADRs | Relationship Type |
```

Source: ADR_INDEX.cross_ref_map. Show bidirectional: if ADR-001 → ADR-005,
also show ADR-005 → ADR-001.

### impact_matrix

```markdown
## impact_matrix
| ADR | Performance | Scalability | Reliability | Security | Maintainability | Cost | Complexity |
```

Source: ADR_INDEX.completed_adrs[].quality_impact + cost/complexity from ADR metadata.
Values: positive / negative / neutral for quality attributes. Low/Med/High for cost/complexity.

### Coverage Tables

These tables validate that upstream artifacts are fully addressed by the ADR set.

```markdown
## bc_coverage
| BC-XX | Name | ADRs Addressing It |
```
Source: cross-reference completed_adrs[].affected_bcs against ADR_CONTEXT.bounded_contexts.
Flag any BC with zero ADRs as UNCOVERED → register in open_questions.

```markdown
## nfr_coverage
| NFR-XX | Description | ADRs Addressing It |
```
Source: cross-reference against ADR_CONTEXT.prd_nfr_ids.
Flag any NFR with zero ADRs → open_questions.

```markdown
## category_coverage
| Category | ADR(s) | Status |
```
All 12 mandatory categories must show at least one ADR.
Missing category = gap → open_questions with severity: high.

```markdown
## risk_coverage
| RSK-XX | Description | ADRs Addressing It |
```
Source: ADR_CONTEXT.prd_risks. Flag uncovered risks.

```markdown
## assumption_coverage
| ASM-XX | Description | ADRs Referencing It |
```
Source: ADR_CONTEXT.prd_assumptions. Flag unreferenced assumptions.

### validations

#### reference_map
FOR EACH completed ADR: map context.forces and context.constraints to source documents.

#### forward_traceability
```markdown
| Check | Expected | Actual | Coverage % | Status |
```
- Every bounded context referenced by >= 1 ADR
- Every NFR-XX addressed by >= 1 ADR
- Every technology constraint acknowledged

#### backward_traceability
```markdown
| ADR | Source References | Status |
```
- Every ADR's context traces to domain analysis or PRD
- Flag orphan ADRs (no source traceability) → open_questions

#### technology_neutrality_audit
```markdown
| ADR | Tech Subject | Violations Found | Corrections Applied | Status |
```
FOR EACH ADR: verify technology_subject scoping was enforced during generation.

#### diagram_validation
```markdown
| ADR | Checks Passed (of 10) | Status |
```
FOR EACH ADR with has_diagram == true: summarize the 10-point PlantUML check.

#### gherkin_validation
```markdown
| ADR | Happy Path | Unhappy Path | Status |
```
FOR EACH ADR with has_gherkin == true.

#### count_verification
```markdown
| Metric | Expected | Actual | Status |
```
- ADR count in adr_catalog == actual file count in adrs/ folder
- Category count >= 12
- All BCs addressed (bc_coverage has no UNCOVERED)
- All NFRs addressed (nfr_coverage has no UNCOVERED)

VERIFY: stated_count == actual_count for EACH metric.
IF mismatch → fix stated_count before writing. LOG the correction.

#### anti_fade_verification

Compare first ADR vs last ADR to detect quality degradation:

```markdown
| Metric | First ADR | Last ADR | Delta | Status |
```
- Section count (number of ## headings)
- Diagram presence (both have or neither has)
- Alternative count (within +/-1)
- Force count (within +/-20%)

Status = PASS if within thresholds. WARN if borderline. FAIL if significant degradation.

#### overall_status
PASS or FAIL with specific reasons.
IF FAIL: list each failure as a row in open_questions.

### open_questions

```markdown
## open_questions
| ID | Category | Description | Severity | Source |
```
All gaps from coverage tables and validations consolidated here — registered exactly once.
Categories: uncovered_bc, uncovered_nfr, uncovered_risk, unreferenced_assumption,
validation_failure, traceability_gap.

### engineering_assumptions

```markdown
## engineering_assumptions
| ASM-ID | Description | ADRs Affected | Rationale | Confidence |
```
Assumptions made during ADR generation that need stakeholder validation.

---

## Source Fidelity Check (before writing manifest)

- [ ] All sections populated (no empty tables — at minimum a "None" row)
- [ ] ADR IDs in adr_catalog match ADR IDs in impact_matrix, cross_reference_map, and coverage tables
- [ ] Every item with status: complete has a source reference
- [ ] Summary counts in count_verification match actual item counts in each table
- [ ] Anti-fade metrics computed from actual first/last ADR data, not estimates
- [ ] open_questions contains every gap flagged in coverage tables (no scatter)

## Post-Section Protocol

1. **Write** `{adrs_path}/ADR-SPEC-{SESSION_ID}.md` — MANDATORY TOOL CALL.
2. **Update** ADR_INDEX.phase_status.C = "COMPLETE"
3. **Update** 00-index.md: add manifest row with "✅ COMPLETE"
4. **Flush** manifest text from memory.
5. **Verify** file exists and is non-empty.
6. **Log:** "Phase C COMPLETE. Manifest written: {N} sections, {M} ADRs cataloged, {K} open questions."
