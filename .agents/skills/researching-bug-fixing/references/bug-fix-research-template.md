# Agent-Native Bug Fix Research Spec Template

## Template Rules
- **No prose.** Every section is structured data only.
- **No narrative.** No "why this matters", no motivational text, no context paragraphs.
- **No formatting for humans.** No prominent text, no callouts, no visual emphasis.
- **All items carry status.** `complete` | `pending` | `assumption`.
- **All pending items appear in open_questions.** Single registry, no scatter.
- **Source tags are mandatory.** No source → cannot be `complete`.
- **Language:** Generate in DETECTED_LANGUAGE. Section headers in English always.

---

## Spec File Structure

```markdown
# {project_name} — Bug Fix Research Spec
version: {NEW_VERSION}
session: {SESSION_ID}
mode: {BUILD | REPAIR}
date: {ISO 8601}
language: {DETECTED_LANGUAGE}
ticket_path: {ticket_path}
source_path: {source_path | "not provided"}
ticket_id: {TICKET_CONTEXT.id}
severity: {TICKET_CONTEXT.severity}
ticket_contract_mode: {structured | partial | unstructured}
ticket_hashes:
  content_hash: {sha256:<64 lowercase hex> | invalid | N/A}
  hash_status: {match | mismatch_accepted | mismatch_blocked | not_verified | N/A}
status: {draft | complete}

---

## ticket_summary

### overview
- id: {TICKET_CONTEXT.id}
- title: {TICKET_CONTEXT.title}
- severity: {Critical | High | Medium | Low}
- priority: {P0 | P1 | P2 | P3 | P4}
- reporter: {TICKET_CONTEXT.reporter | "[Not provided in ticket]"}
- environment: {TICKET_CONTEXT.environment | "[Not provided in ticket]"}
- source: {ticket_path}
- status: {complete | pending}

### description
{TICKET_CONTEXT.description — verbatim from ticket}

### contract_summary
| field | value | source | status |
|-------|-------|--------|--------|
| contract_mode | {structured | partial | unstructured} | {ticket_path} | complete |
| content_hash | {sha256:<64 lowercase hex> | invalid | N/A} | {ticket_path} | {complete | pending} |
| hash_format | {valid_sha256 | invalid | N/A} | {ticket_path} | {complete | pending} |
| hash_status | {match | mismatch_accepted | mismatch_blocked | not_verified | N/A} | {ticket_path} | {complete | pending} |
| literal_refs | {LIT-XX list | N/A} | {ticket_path} | {complete | pending} |
| fallback_refs | {PI/OQ/ASM list | N/A} | {ticket_path} | {complete | pending} |

### accepted_hash_overrides
| artifact | declared_hash | observed_hash | verification_result | decision |
|----------|---------------|---------------|---------------------|----------|
| {Ticket upstream | N/A} | {sha256:<64 lowercase hex> | N/A} | {sha256:<64 lowercase hex> | N/A} | {all recorded dependencies still present identically | not_verified | N/A} | {accepted in this research audit only | N/A} |

### reproduction_steps
{TICKET_CONTEXT.reproduction — verbatim from ticket, or "[Not provided in ticket]"}
- status: {complete | pending}
- source: {ticket_path}

### expected_behavior
{TICKET_CONTEXT.expected — verbatim from ticket, or "[Not provided in ticket]"}

### actual_behavior
{TICKET_CONTEXT.actual — verbatim from ticket, or "[Not provided in ticket]"}

### affected_areas

| area | type | notes | source | status |
|------|------|-------|--------|--------|
| {area} | [File/Module/Endpoint/Service] | {notes from ticket} | {ticket_path} | {complete | pending} |

### scope_assessment
- complexity: {LOW | MEDIUM | HIGH} | rationale: {based on affected areas}
- regression_risk: {LOW | MEDIUM | HIGH} | rationale: {based on centrality of affected code}
- urgency: {LOW | MEDIUM | HIGH | CRITICAL} | rationale: {based on severity + user impact}

### attachments
- {attachment_name} | type: {log | screenshot | video | trace} | source: {ticket_path}
- [None provided] (if empty)

---

## root_cause

### execution_path_trace

| step | file | function | purpose | source | status |
|------|------|----------|---------|--------|--------|
| 1 (Entry) | `{entry_point_file}` | `{handler/endpoint}` | {request entry / event trigger} | {source_path} | {complete | assumption} |
| 2 | `{next_file}` | `{called_function}` | {processing step} | {source_path} | {complete | assumption} |
| N (Error) | `{error_file:line}` | `{failing_function}` | {where defect manifests} | {source_path} | {complete | assumption} |

scope_constraint: Only files on this execution path were analyzed.
excluded_files: {list of ticket-referenced files NOT on execution path, or "None"}

### tech_stack

| layer | technology | version | source | status |
|-------|------------|---------|--------|--------|
| {layer} | {EXACT from build file} | {EXACT version} | {build file path} | {complete | pending | assumption} |

IF SOURCE_CONTEXT is null:
  - status: pending
  - note: "Technology stack not available — no source code provided"

### affected_files

| path | current_behavior | defect | lines | source | status |
|------|-----------------|--------|-------|--------|--------|
| `{exact/path/file.ext}` | {what it does} | {what's wrong} | {L:N-M} | {source_path} | {complete | assumption} |

### root_cause_statement
- root_cause: {specific cause — traceable to file:line}
- confidence: {HIGH — source evidence | MEDIUM — partial evidence | LOW — hypothesis only}
- evidence:

```{language}
{Relevant code snippet from SOURCE_CONTEXT showing the bug, 5-15 lines max}
```

IF SOURCE_CONTEXT is null:
  - root_cause: {hypothesis — verify in codebase}
  - confidence: LOW
  - evidence: "[No source code available]"
  - likely_location: {TICKET_CONTEXT.affected_areas}

- mechanism: {how the bug manifests — data flow from trigger to failure}
- source: {source_path | ticket_path}
- status: {complete | pending | assumption}

### contributing_factors

| factor | evidence | preventable | source | status |
|--------|----------|-------------|--------|--------|
| {e.g., missing null check, race condition} | {where in code} | {Yes — how | No} | {source_path} | {complete | assumption} |

### existing_patterns

| pattern | location | relevant_to_fix | source | status |
|---------|----------|-----------------|--------|--------|
| {pattern from SOURCE_CONTEXT.existing_patterns} | `{path:L-N}` | {Yes — follow | No} | {source_path} | {complete | assumption} |

---

## impact

### direct_impact

| file | change_type | risk | reason | source | status |
|------|-------------|------|--------|--------|--------|
| `{exact/path/file.ext}` | {Modify | Create | Delete} | {LOW | MED | HIGH} | {why} | {source_path} | {complete | assumption} |

### indirect_impact

| component | how_affected | risk | mitigation | source | status |
|-----------|-------------|------|------------|--------|--------|
| {component/file} | {regression scenario} | {LOW | MED | HIGH} | {how to mitigate} | {source_path} | {complete | assumption} |

### data_impact

| data_store | impact | migration_needed | source | status |
|------------|--------|------------------|--------|--------|
| {DB/Cache/Queue | "None"} | {how affected} | {Yes — details | No} | {source_path} | {complete | pending} |

### api_impact

| interface | change | breaking | consumers | source | status |
|-----------|--------|----------|-----------|--------|--------|
| {endpoint / method signature | "None"} | {what changes} | {Yes | No} | {who calls it} | {source_path} | {complete | pending} |

### risk_summary
- overall: {LOW | MEDIUM | HIGH}
- regression: {LOW | MEDIUM | HIGH}
- data: {LOW | MEDIUM | HIGH}

---

## fix_approach

### strategy
- approach: {what to do — 1 sentence}
- rationale: {why this approach — 1 sentence}
- alternative_considered: {other option | "None"}
- alternative_rejected_reason: {why | "N/A"}

### files_to_modify

| path | change_description | pattern_to_follow | source | status |
|------|-------------------|-------------------|--------|--------|
| `{exact/path/file.ext}` | {specific change} | {existing/pattern:L-N} | {source_path} | {complete | assumption} |

### files_to_create

| path | purpose | pattern_reference | source | status |
|------|---------|-------------------|--------|--------|
| `{exact/path/new-file.ext}` | {purpose} | {existing/pattern} | {source_path} | {complete | assumption} |

IF no files to create: [None]

### implementation_steps
1. {step 1 — specific action with file and location}
2. {step 2 — specific action}
3. {step N — specific action}

### fix_pattern

```{language}
// Fix pattern (max 15 lines)
// Based on existing codebase conventions from SOURCE_CONTEXT
{code example}
```

IF SOURCE_CONTEXT is null:
  [Code pattern is illustrative — verify against actual codebase conventions.]

### edge_cases

| edge_case | handling | source | status |
|-----------|----------|--------|--------|
| {edge case relevant to this bug} | {how to handle} | {source_path | inference} | {complete | assumption} |

### constraints
- {constraint from codebase conventions or context pack} | source: {ref}

---

## acceptance_criteria

### ticket_ac (MANDATORY — preserve verbatim)

| id | criterion | source | verification | status |
|----|-----------|--------|--------------|--------|
| TAC-01 | {AC from TICKET_CONTEXT.ac — verbatim} | {ticket_path} | {how to verify} | complete |
| TAC-NN | {AC from ticket — verbatim} | {ticket_path} | {how to verify} | complete |

IF TICKET_CONTEXT.ac is empty:
  [No acceptance criteria provided in ticket.]
  - status: pending
  - registered in open_questions

### derived_ac

| id | criterion | rationale | verification | source | status |
|----|-----------|-----------|--------------|--------|--------|
| DAC-01 | Bug no longer reproducible via original reproduction steps | Core fix validation | Manual test following repro steps | {ticket_path} | complete |
| DAC-02 | Expected behavior restored: {TICKET_CONTEXT.expected} | Ticket expected behavior | {specific verification} | {ticket_path} | complete |
| DAC-NN | {additional derived criterion} | {why needed} | {how to verify} | {ref} | {complete | assumption} |

### regression_ac

| id | criterion | verification | source | status |
|----|-----------|--------------|--------|--------|
| RAC-01 | All existing tests pass | `{test command from SOURCE_CONTEXT.test_framework}` | {source_path} | {complete | pending} |
| RAC-NN | {specific regression scenario from impact section} | {verification method} | {source_path} | {complete | assumption} |

### definition_of_done
- [ ] All ticket AC verified
- [ ] All derived criteria verified
- [ ] All regression criteria verified
- [ ] No new test failures introduced
- [ ] Code follows existing conventions
- [ ] PR/review ready

---

## test_strategy

### tests_to_write

| test | type | file | covers | source | status |
|------|------|------|--------|--------|--------|
| {test description — specific to bug} | {Unit | Integration | E2E} | `{test/file/path.spec.ext}` | {TAC-XX | DAC-XX | RAC-XX} | {source_path} | {complete | assumption} |

### tests_to_update

| test | file | change_needed | source | status |
|------|------|---------------|--------|--------|
| {existing test name} | `{test/file/path.spec.ext}` | {what to update and why} | {source_path} | {complete | assumption} |

IF no existing tests need updating:
  [No existing tests require changes.]

### test_commands

```bash
# Run affected tests (EXACT command from SOURCE_CONTEXT.test_framework)
{exact test command}

# Run full suite (regression check)
{full test command}
```

IF SOURCE_CONTEXT is null:
  [Test commands not available — verify in project build configuration.]
  - status: pending

### coverage

| area | current | target | source | status |
|------|---------|--------|--------|--------|
| {modified file/module} | {current % | "Unknown"} | {target %} | {source_path} | {complete | pending} |

### manual_verification_steps
1. {reproduce original bug using ticket repro steps, verify fixed}
2. {verify expected behavior restored}
3. {check regression scenarios from impact section}

---

## validations

| check | result | notes |
|-------|--------|-------|
| codebase_fidelity | {PASS | FAIL} | {details if FAIL} |
| root_cause_traceability | {PASS | FAIL} | {details if FAIL} |
| ticket_ac_coverage | {PASS | FAIL} | {details if FAIL} |
| technology_fidelity | {PASS | FAIL} | {details if FAIL} |
| anti_fade | {PASS | FAIL} | {details if FAIL} |
| section_completeness | {PASS | FAIL} | {details if FAIL} |
| count_verification | {PASS | FAIL} | {details if FAIL} |
| source_tags | {PASS | FAIL} | {details if FAIL} |
| ticket_contract_mode | {PASS | FAIL} | mode={structured | partial | unstructured}; unstructured accepted |
| partial_cross_check | {PASS | FAIL | N/A} | discrepancies={N} |
| hash_forward_verification | {PASS | FAIL | N/A} | valid_sha256={yes | no}; accepted_hash_overrides={N}; blocked={N} |
| auth_security_defaults | {PASS | FAIL | N/A} | reset_tokens_hashed={yes | no | N/A}; oauth_provider_allow_list={yes | no | N/A} |

---

## open_questions

This section is the **single consolidated registry** of all unresolved items.
Every `pending` status, every `assumption` that needs validation — all appear
here once. Downstream skills (planning-code-tasks) read ONLY this section to
understand what is unresolved.

### pending_inputs

| id | affected_ids | blocking | type | section | item_id | field | impact | fallback_behavior | source_ref |
|----|--------------|----------|------|---------|---------|-------|--------|-------------------|------------|
| PI-01 | {TAC-XX | DAC-XX | RAC-XX | all | N/A} | {yes | no} | missing | {section} | {item_id} | {field} | {impact on downstream} | {fallback or BLOCKED} | {ticket_path} |

### evidence_gaps

| id | affected_ids | type | section | claim | evidence_needed | impact | decision |
|----|--------------|------|---------|-------|-----------------|--------|----------|
| EG-01 | {TAC-XX | DAC-XX | RAC-XX | LIT-XX | all | N/A} | {missing_source | structured_discrepancy | invalid_hash | hash_dependency_gap | auth_security_gap} | {section} | {claim made without full evidence} | {what evidence would confirm} | {impact if wrong} | {accepted | carried_forward | blocks} |

### assumptions_to_validate

| id | affected_ids | blocking | assumption | impact_if_wrong | validation_method | fallback_behavior | source_ref |
|----|--------------|----------|------------|-----------------|-------------------|-------------------|------------|
| ASM-01 | {TAC-XX | DAC-XX | RAC-XX | all | N/A} | {yes | no} | {assumption statement} | {consequence} | {how to confirm/deny} | {fallback or BLOCKED} | {ticket_path} |

### upstream_gaps_carried_forward

| id | affected_ids | blocking | source | gap | impact_on_spec | fallback_behavior |
|----|--------------|----------|--------|-----|----------------|-------------------|
| UG-01 | {TAC-XX | DAC-XX | RAC-XX | all | N/A} | {yes | no} | {ticket_path} | {what was missing from ticket} | {which sections affected} | {fallback or BLOCKED} |

### summary
- total_affected_files: {N}
- total_ticket_ac: {N}
- total_derived_ac: {N}
- total_regression_ac: {N}
- total_tests_to_write: {N}
- total_tests_to_update: {N}
- pending_inputs: {N}
- evidence_gaps: {N}
- assumptions: {N}
- overall_risk: {LOW | MEDIUM | HIGH}
- root_cause_confidence: {HIGH | MEDIUM | LOW}
- status: {draft | complete}
```

---

## Generation Rules

### Section Ordering
Generate sections in the order shown above. This order reflects dependency flow:
ticket_summary → root_cause → impact → fix_approach → acceptance_criteria →
test_strategy → validations → open_questions.

The validations section MUST come after all content sections are generated.
The open_questions section is ALWAYS LAST — it consolidates from all prior sections.

### Per-Item Rules
- Every table row MUST have `status` and `source` columns.
- `status: complete` requires a non-empty `source` value.
- `status: pending` → item MUST also appear in `open_questions.pending_inputs`.
- `status: assumption` → item MUST also appear in `open_questions.assumptions_to_validate`
  with an ASM-XX ID.

### REPAIR Mode
- Load existing spec file.
- Apply REPAIR_DIRECTIVES to targeted sections only.
- Sections without directives → preserve verbatim from previous spec.
- "global" directive → regenerate entire spec.
- Rebuild open_questions from scratch (always reflects current state).
- Increment version, log changes in CHANGE_LOG.
- Recalculate all summary counts after repair.

### Scaling
Always single file. Bug-fix research specs are scoped to one defect.
No batching, no multi-file splitting. If context exceeds 60% mid-generation
(unlikely), apply Write-Flush-Forget to the single file.

### Consolidation Pass (Before Writing)
After generating all sections, perform a single consolidation pass:
1. Scan every section for items with status: pending → create PI-XX in open_questions
2. Scan every section for items with status: assumption → create ASM-XX in open_questions
3. Scan for evidence gaps (claims without full source backing) → create EG-XX
4. Carry forward upstream gaps from ticket → create UG-XX
5. In partial contract mode, cross-check structured refs against prose-derived
   IDs/literals/fallbacks; create EG-XX for discrepancies
6. Enforce hash format: only `sha256:<64 lowercase hex>` is valid; invalid
   hash fields demote structured tickets to partial and create EG-XX
7. For auth/OAuth/session/password-reset tickets, create EG-XX unless reset
   tokens are hashed at rest and OAuth provider values use an explicit allow-list
8. Compute summary counts
9. Set top-level status: `complete` if zero pending_inputs AND zero blocking evidence_gaps.
   Otherwise: `draft`.
