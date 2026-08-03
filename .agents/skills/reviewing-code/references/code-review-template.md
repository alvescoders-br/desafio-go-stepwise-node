<!-- DRAFT — Pending human validation -->
<!-- Source: reviewing-code skill, code-review-template reference -->

# Code Review Spec Template

Template for `REVIEW-SPEC-{session_id}.md` produced by the reviewing-code skill.
Consolidates findings, tool results, traceability, and repair feedback into a single structured spec.

---

## Template Rules

- No prose. Structured data only.
- All findings carry severity: blocking | high | medium | low
- All findings carry evidence and source references
- Source tags mandatory on every verification
- REPAIR Feedback Quality Rule: blocking/high findings MUST include before_snippet, after_snippet, verification_hint

---

## Spec File Structure

```markdown
# {project_name} — Code Review Spec
version: {version}
previous_version: {previous_version | N/A}
session: {session_id}
mode: {FRESH | REPAIR}
date: {ISO 8601}
overall_status: {passed | partial | failed}
source: {source_path}
plan: {plan_folder_path}
research: {research_folder_path}
status: {passed | partial | failed}

---

## summary
- blocking_count: {N}
- high_count: {N}
- medium_count: {N}
- low_count: {N}
- warning_count: {N}
- passed_count: {N}
- tools_executed: {N}
- tools_passed: {N}
- ac_passed: {N}/{total}
- files_verified: {N}
- coverage: {%}
- recommendation: {ready_to_merge | needs_fixes | blocked}

## findings

### blocking
| id | phase | category | file | line_range | description | expected | actual | fix_instruction | before_snippet | after_snippet | verification_hint | evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
(One row per blocking finding. before_snippet and after_snippet are MANDATORY for blocking.)

### high
| id | phase | category | file | line_range | description | fix_instruction | before_snippet | after_snippet | verification_hint | evidence |
|---|---|---|---|---|---|---|---|---|---|---|
(before/after MANDATORY for high findings too.)

### medium
| id | category | file | description | evidence |
|---|---|---|---|---|

### low
| id | category | file | description |
|---|---|---|---|

### warnings
| id | category | tool | description |
|---|---|---|---|

### passed
| id | category | check | evidence |
|---|---|---|---|

## repair_delta (REPAIR mode only)

### fixed
| issue | category | previous_status | evidence |
|---|---|---|---|

### still_failing
| issue | category | evidence |
|---|---|---|

### regressions
| issue | category | evidence |
|---|---|---|

### repair_summary
- fixed_count: {N}
- still_failing_count: {N}
- regression_count: {N}

## tool_results
| tool | category | status | execution_time | command | exit_code | summary | issues_found |
|---|---|---|---|---|---|---|---|
(status: pass | fail | timeout | unavailable)

## acceptance_criteria
| ac_id | description | verification_method | status | evidence | phase |
|---|---|---|---|---|---|
(status: pass | fail | manual_required)

### manual_verification_required
| ac_id | description | steps |
|---|---|---|
(List items needing human verification)

## traceability
| story_id | phase | files_expected | files_found | tests_expected | tests_found | ac_passed | ac_failed | patterns_verified | status |
|---|---|---|---|---|---|---|---|---|---|
(status: pass | fail | partial)

## research_compliance

### adr_compliance
| adr_id | decision | status | evidence |
|---|---|---|---|

### landmine_avoidance
| landmine | status | evidence |
|---|---|---|

### nfr_compliance
| nfr_id | requirement | status | evidence |
|---|---|---|---|

## deviation_analysis

### documented_deviations
| phase | deviation | justification | review_status |
|---|---|---|---|
(review_status: accepted | rejected | unjustified)

### undocumented_deviations
| file | expected | actual | severity |
|---|---|---|---|

## implementation_feedback
- feedback_string: |
    {Pre-formatted multi-line string ready for use as failure_feedback parameter.
     Contains: issue IDs, file:line, BEFORE/AFTER snippets, verification hints.
     Max 5 blocking + 3 high issues. References full spec for remainder.}

## validations
| check | result | details |
|---|---|---|
| file_existence | {pass &#124; fail} | {N}/{total} files found |
| test_existence | {pass &#124; fail} | {N}/{total} test files found |
| test_quality | {pass &#124; fail} | {N} quality concerns |
| pattern_compliance | {pass &#124; fail} | {N}/{total} patterns verified |
| adr_compliance | {pass &#124; fail} | {N}/{total} ADRs respected |
| landmine_avoidance | {pass &#124; fail} | {N} landmines avoided |
| deviation_audit | {pass &#124; fail} | {N} undocumented deviations |
| ac_verification | {pass &#124; fail} | {N}/{total} ACs passed |
| tool_build | {pass &#124; fail &#124; skipped} | {details} |
| tool_test | {pass &#124; fail &#124; skipped} | {details} |
| tool_lint | {pass &#124; fail &#124; warn &#124; skipped} | {details} |
| tool_typecheck | {pass &#124; fail &#124; warn &#124; skipped} | {details} |
| tool_security | {pass &#124; fail &#124; warn &#124; skipped} | {details} |
| tool_coverage | {pass &#124; fail &#124; warn &#124; skipped} | {details} |
| traceability | {pass &#124; fail} | {N}/{total} stories fully traced |

## open_questions
### pending_inputs
| id | type | section | item_id | field | impact |
|---|---|---|---|---|---|

### review_gaps
| id | type | item_id | description |
|---|---|---|---|

### assumptions_to_validate
| id | assumption | impact_if_wrong | validation_method |
|---|---|---|---|

### upstream_gaps_carried_forward
| id | source | description | local_coverage | recommendation |
|---|---|---|---|---|

### summary
- findings_total: {N}
- blocking: {N}
- high: {N}
- pending_inputs: {N}
- review_gaps: {N}
- assumptions: {N}
- upstream_gaps: {N}
- status: {passed | partial | failed}
```

---

## Generation Rules

- Findings generated during Steps 3-7 of the review
- implementation_feedback generated in Step 8 following REPAIR Feedback Quality Rule
- validations consolidated from all verification steps
- open_questions consolidated from all gaps found during review
- REPAIR mode: include repair_delta section, compare against previous spec
- Single file always (findings are compact)
