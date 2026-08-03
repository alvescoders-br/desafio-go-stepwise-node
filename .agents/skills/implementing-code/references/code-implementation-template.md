<!-- DRAFT — Pending human validation -->
<!-- Source: implementing-code skill — IMPL-STATE template spec -->

# Code Implementation State Template (IMPL-STATE-{session_id}.md)

## Purpose

Single structured tracking file for the implementing-code skill. Consolidates implementation progress and audit into one artifact. Updated in real-time during execution.

## Template Rules

- No prose. Structured data only.
- All items carry status: `complete` | `in_progress` | `pending` | `failed` | `blocked` | `architecture_flaw`
- Source tags where applicable.
- Updated in real-time during execution (not generated once at end).
- Always single file. Tracking data is compact (~100-600 lines depending on project size).

## Update Lifecycle

| Phase | Actions |
|-------|---------|
| Phase A | Create with session metadata, phase table (all PENDING), empty sections |
| Phase B | Update current_work, files_touched after each file write |
| Phase C | Update tech_stack_detected, build_commands, tool_results, scaffolding_results, plan_adherence, ac_coverage_matrix |
| Phase D | Update phase_status, metrics, execution_log, open_questions, validations |
| REPAIR | Append to repair_log, update files_touched with modified files |

- `open_questions` is rebuilt from scratch at each Phase D (reflects current state).
- `validations` is rebuilt from scratch at each Phase D.
- Empty final sections are still complete sections. When `blockers`,
  `deviations`, or `execution_log` have no substantive rows at finalization,
  write one explicit `none` row and mark the WFF section `complete`; never leave
  a final `WFF-SECTION:*:pending` marker in a completed IMPL-STATE.

---

## File Structure

````markdown
# {project_name} — Implementation State
version: {version}
session: {session_id}
mode: {STANDARD | REPAIR}
date: {ISO 8601}
plan_session: {plan_session_id}
research_session: {research_session_id | N/A}
source_path: {source_path}
plan_path: {plan_folder_path}
research_path: {research_folder_path | N/A}
scope: {TASK | FULL_SDLC}
execution_scope: {all | single}
status: {in_progress | completed | completed_with_warnings | failed | blocked | architecture_flaw}

---

## session_metadata
- project: {project_name}
- session_id: {session_id}
- source_path: {source_path}
- project_root: {source_path}
- plan_folder: {plan_folder_path}
- research_folder: {research_folder_path | N/A}
- started_at: {ISO timestamp}
- last_updated: {ISO timestamp}
- tdad_mode: {true | false}
- execution_scope: {all | single}

## phase_status
| phase_id | name | status | started_at | completed_at | files_count | tests_count | notes |
|----------|------|--------|------------|--------------|-------------|-------------|-------|
| {phase_id} | {name} | {pending | in_progress | completed | completed_with_warnings | failed | blocked | architecture_flaw} | {timestamp | -} | {timestamp | -} | {N} | {N} | {notes | -} |

## current_work
- active_phase: {phase_id | none}
- current_file: {path | none}
- current_file_status: {in_progress | completed | failed | architecture_flaw}

## files_touched
| phase | file_path | action | status | test_file |
|-------|-----------|--------|--------|-----------|
| {phase_id} | {path} | {create | modify} | {completed | failed} | {test_path | N/A} |

## tech_stack_detected
- languages: [{language}]
- build_tools: [{tool}]
- frameworks: [{framework}]
- services: [{ name, type, path }]
- container_orchestration: {docker-compose | docker | none}

## build_commands
- build: [{command}]
- test: [{command}]
- lint: [{command}]
- typecheck: [{command}]

## tool_results
| tool | category | status | details |
|------|----------|--------|---------|
| {tool_name} | {build | test | lint | typecheck} | {pass | fail | warn | unavailable | skipped} | {details} |

## scaffolding_results
| check | status | details |
|-------|--------|---------|
| {check_type} | {pass | fail | auto_fixed} | {details} |

## plan_adherence
| item | type | status | details |
|------|------|--------|---------|
| {planned_item} | {file | ac} | {implemented | incomplete | known_limitation} | {details} |

## ac_coverage_matrix (if task description available)
| ac_id | description | test_file | status |
|-------|-------------|-----------|--------|
| {AC-XX} | {description} | {test_path | -} | {covered | generated | uncovered} |

## blockers
| phase | description | timestamp | resolution | status |
|-------|-------------|-----------|------------|--------|
| {phase_id} | {description} | {ISO timestamp} | {resolution | pending} | {open | resolved} |
| none | none | - | none | resolved |

## deviations
| phase | description | reason | impact |
|-------|-------------|--------|--------|
| {phase_id} | {deviation} | {reason} | {impact} |
| none | none | none | none |

## repair_log
| iteration | phase | feedback_summary | files_modified | changes |
|-----------|-------|------------------|----------------|---------|
| {N} | {phase_id} | {summary} | {file_list} | {change_descriptions} |

## execution_log
| timestamp | phase | action | status | details |
|-----------|-------|--------|--------|---------|
| {ISO timestamp} | {phase_id | -} | {action} | {ok | fail | warn} | {details} |
| {ISO timestamp} | all | final_state_written | ok | no additional execution events |

## metrics
| metric | value |
|--------|-------|
| total_execution_time | {duration} |
| phases_completed | {N} |
| phases_failed | {N} |
| files_created | {N} |
| files_modified | {N} |
| tests_created | {N} |
| self_corrections | {N} |
| repair_iterations | {N} |
| build_verifications | {N} |
| plan_adherence_returns | {N} |

## validations
| check | result | details |
|-------|--------|---------|
| scaffolding_completeness | {pass | fail} | {details} |
| plan_adherence | {pass | fail} | {N}/{total} items |
| ac_coverage | {pass | fail | skipped} | {N}/{total} ACs |
| tool_build | {pass | fail | skipped} | {details} |
| tool_test | {pass | fail | skipped} | {details} |
| tool_lint | {pass | fail | warn | skipped} | {details} |
| tool_typecheck | {pass | fail | warn | skipped} | {details} |
| readme_generated | {pass | fail} | {path} |
| agents_md_generated | {pass | fail | not_final_phase} | {path} |
| phase_c_completion_gate | {pass | fail} | {details} |

## open_questions
### pending_inputs
| id | type | section | item_id | field | impact |
|----|------|---------|---------|-------|--------|

### implementation_gaps
| id | type | item_id | description |
|----|------|---------|-------------|

### assumptions_to_validate
| id | assumption | item_id | impact_if_wrong | validation_method |
|----|------------|---------|-----------------|-------------------|

### upstream_gaps_carried_forward
| id | source | description | local_coverage | recommendation |
|----|--------|-------------|----------------|----------------|

### summary
- phases_total: {N}
- phases_completed: {N}
- pending_inputs: {N}
- implementation_gaps: {N}
- assumptions: {N}
- upstream_gaps: {N}
- status: {in_progress | completed | failed | blocked}
````
