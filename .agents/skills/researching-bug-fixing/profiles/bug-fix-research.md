# Rendering Profile: Bug Fix Research Spec → Human-Readable Bug Fix Research Document Set

## Input
Agent-native Bug Fix Research spec file (RESEARCH-SPEC-*.md).
Single file containing 5 structured sections plus metadata.

## Renderable Sections
(use with `render_scope: section:{name}`)

| Section Name | Source Data | Rendering |
|-------------|------------|-----------|
| index | all sections | Navigation table, quick stats, validation summary, audit trail, "How to Use", "Next Steps" |
| bug_summary | ticket_summary | Ticket overview table, description prose, reproduction steps, expected/actual, affected areas, scope assessment, attachments |
| root_cause | root_cause | Investigation summary prose (derived), execution path table, tech stack table, affected files, root cause evidence block, contributing factors, existing patterns |
| impact_and_fix | impact + fix_approach | Two-part document (Part A: Impact, Part B: Fix), all tables + strategy prose (derived from strategy key-value) |
| acceptance_criteria | acceptance_criteria | Ticket AC, derived AC, regression AC, Definition of Done |
| test_strategy | test_strategy | Tests tables (write + update), commands, coverage, manual verification steps |

## Full Render Order

```
1. BUG SUMMARY (section: bug_summary)
   Generate 01-bug-summary.md
   - Document header with YAML frontmatter (document_id, type, session_id, project, date, mode)
   - "Ticket Overview" table:
     Render ticket_summary fields as key-value rows:
     Ticket ID, Title, Severity, Priority, Reporter, Environment, Source
   - "Description" section:
     Render ticket_summary.description as prose block
     Verbatim from spec — no summarization, no invention
   - "Reproduction Steps" section:
     Render ticket_summary.reproduction verbatim
     IF value is "[Not provided in ticket]" → render as-is with no elaboration
   - "Expected vs Actual Behavior" table:
     | | Behavior |
     | Expected | {ticket_summary.expected} |
     | Actual | {ticket_summary.actual} |
   - "Affected Areas (from ticket)" table:
     Render ticket_summary.affected_areas as: Area | Type | Notes
     Types: File, Module, Endpoint, Service (infer from area name)
   - "Scope Assessment" table:
     Render as: Aspect | Rating | Rationale
     Rows: Fix Complexity, Regression Risk, Urgency
     Derive ratings from severity + affected areas breadth
   - "Attachments / Evidence" section:
     Render ticket_summary.attachments list
     IF empty → "[None provided]"
   - References footer: [REF-01] {ticket_path}
   - Quick Navigation: static links to all 6 documents

2. ROOT CAUSE ANALYSIS (section: root_cause)
   Generate 02-root-cause-analysis.md
   - Document header with YAML frontmatter
   - "Investigation Summary" paragraph:
     Derive from root_cause.execution_path_trace:
     Summarize the trace as 2-3 sentences describing what was investigated
     and what evidence was examined.
     Template: "Investigation traced the execution path from {entry_point} through
     {N} components to the error site at {error_file}. {evidence_summary}."
   - "Execution Path Trace" table:
     Render root_cause.execution_path_trace as:
     Step | File | Function/Method | Purpose
     Row 1 marked "(Entry)", last row marked "(Error)"
     Footer: "Scope constraint: Only files on this execution path were analyzed."
     + list of files referenced but excluded
   - "Technology Stack (from source code)" table:
     Render root_cause.technology_stack as:
     Layer | Technology | Version | Source
     IF no source code → "[Technology stack not available — no source code provided]"
   - "Affected Files" table:
     Render root_cause.affected_files as:
     File Path | Current Behavior | Defect | Lines
     Code-format all file paths
     IF no source → append [Assumption] marker to each path
   - "Root Cause" block:
     Render root_cause.root_cause as:
     **Root Cause:** {cause statement}
     **Confidence:** {HIGH/MEDIUM/LOW} — {rationale}
     **Evidence:** code block with relevant snippet (5-15 lines)
     IF no source → "[Hypothesis — verify in codebase]" with likely location
     **Mechanism:** {data flow explanation from trigger to failure}
   - "Contributing Factors" table:
     Render root_cause.contributing_factors as:
     Factor | Evidence | Preventable?
   - "Existing Patterns Observed" table:
     Render root_cause.existing_patterns as:
     Pattern | Location | Relevant to Fix?
   - References footer
   - Quick Navigation

3. IMPACT ASSESSMENT & FIX APPROACH (section: impact_and_fix)
   Generate 03-impact-and-fix.md
   - Document header with YAML frontmatter
   - Document title: "# Impact Assessment & Fix Approach: {project_name}"
   - Part A header: "## Part A: Impact Assessment"
   - "Direct Impact (files to change)" table:
     Render impact.direct_impact as:
     File | Change Type | Risk | Reason
   - "Indirect Impact (potential regressions)" table:
     Render impact.indirect_impact as:
     Component | How Affected | Risk | Mitigation
   - "Data Impact" table:
     Render impact.data_impact as:
     Data Store | Impact | Migration Needed?
     IF none → "None" row
   - "API / Interface Impact" table:
     Render impact.api_impact as:
     Interface | Change | Breaking? | Consumers
     IF none → "None" row
   - "Risk Summary" table:
     Render impact.risk_summary as:
     Dimension | Rating
     Rows: Overall Risk, Regression Risk, Data Risk
   - Part B header: "## Part B: Fix Approach"
   - "Strategy" paragraph:
     Derive from fix_approach.strategy key-value pairs + fix_approach.files list:
     Generate 1-3 sentences explaining what to do and why this approach.
     Template: "The fix targets {primary_file} by {strategy.action}. This approach
     {strategy.rationale}, following the existing {pattern} pattern at {reference}."
   - "Files to Modify" table:
     Render fix_approach.files_to_modify as:
     File Path | Change Description | Pattern to Follow
   - "Files to Create (if any)" table:
     Render fix_approach.files_to_create as:
     File Path | Purpose | Pattern Reference
     IF none → "[No new files required]"
   - "Implementation Steps" numbered list:
     Render fix_approach.implementation_steps as ordered list
     Each step must reference specific file + location
   - "Fix Pattern Example" code block:
     Render fix_approach.code_example (10-15 lines)
     IF no source → "[Code pattern is illustrative — verify against actual codebase conventions.]"
   - "Edge Cases" table:
     Render fix_approach.edge_cases as:
     Edge Case | Handling
   - "Constraints" bullet list:
     Render fix_approach.constraints
   - References footer
   - Quick Navigation

4. ACCEPTANCE CRITERIA (section: acceptance_criteria)
   Generate 04-acceptance-criteria.md
   - Document header with YAML frontmatter
   - "Criteria from Ticket (MANDATORY — preserve verbatim)" table:
     Render acceptance_criteria.ticket_ac as:
     # | Criterion | Source | Verification
     Source column always "Ticket"
     IF empty → "[No acceptance criteria provided in ticket.]"
   - "Derived Criteria" table:
     Render acceptance_criteria.derived_ac as:
     # | Criterion | Rationale | Verification
     Row 1 always: "Bug no longer reproducible via original reproduction steps"
     Row 2 always: "Expected behavior restored: {expected_behavior}"
   - "Regression Criteria" table:
     Render acceptance_criteria.regression_ac as:
     # | Criterion | Verification
     Row 1 always: "All existing tests pass" with test command
   - "Definition of Done" checklist:
     Render as markdown checklist (unchecked):
     - [ ] All ticket AC verified
     - [ ] All derived criteria verified
     - [ ] All regression criteria verified
     - [ ] No new test failures introduced
     - [ ] Code follows existing conventions
     - [ ] PR/review ready
   - References footer
   - Quick Navigation

5. TEST STRATEGY (section: test_strategy)
   Generate 05-test-strategy.md
   - Document header with YAML frontmatter
   - "Tests to Write" table:
     Render test_strategy.tests_to_write as:
     Test | Type | File | Covers
     Type: Unit, Integration, E2E
     Covers: references AC # or criterion
   - "Tests to Update" table:
     Render test_strategy.tests_to_update as:
     Test | File | Change Needed
     IF none → "[No existing tests require changes.]"
   - "Test Commands" bash code block:
     Render test_strategy.commands:
     # Run affected tests
     {affected_test_command}
     # Run full suite (regression check)
     {full_suite_command}
     IF no source → "[Test commands not available — verify in project build configuration.]"
   - "Coverage" table:
     Render test_strategy.coverage as:
     Area | Current | Target
   - "Manual Verification Steps" numbered list:
     Render test_strategy.manual_steps as ordered list
     Step 1 always: reproduce original bug, verify fixed
     Step 2 always: verify expected behavior restored
     Remaining: regression scenarios from impact assessment
   - References footer
   - Quick Navigation

6. RESEARCH INDEX (section: index) — GENERATED LAST
   Generate 00-research-index.md
   - Document header with YAML frontmatter including total_documents and ticket_id
   - "Session Overview" table:
     Session ID, Mode, Project, Ticket (ID + title), Severity, Date, Document count
   - "Document Navigation" table:
     # | Document | Description | Key Info
     Derive descriptions from section contents (severity, confidence, file counts, AC counts)
     Links to each document as relative markdown links
   - "Quick Stats" table:
     Affected Files | Root Cause Confidence | AC from Ticket | AC Derived |
     Tests to Write | Tests to Update | Overall Risk
     Read from carry-forward index values
   - "Session Audit Trail" section:
     "Sources Referenced" table:
       # | Document | Path | Status
       Bug Ticket → always "Loaded"
       Source Code → "Loaded" or "Not provided"
       Context Pack → "Loaded" or "N/A"
     "Validation Results" table:
       Check | Result
       Codebase Fidelity, Root Cause Traceability, Ticket AC Coverage,
       Technology Fidelity, Anti-Fade, Document Completeness, Count Verification
       Each: PASS or FAIL
     IF REPAIR mode → "Change Log" table:
       Document | Section | Change | Reason
   - "How to Use This Research" section — STATIC CONTENT:
     1. Start here — review this index
     2. Understand the bug — read 01-bug-summary.md
     3. Confirm root cause — read 02-root-cause-analysis.md
     4. Plan the fix — read 03-impact-and-fix.md
     5. Validate criteria — review 04-acceptance-criteria.md
   - "Next Steps" section — STATIC CONTENT:
     APPROVE → Proceed to planning-code-tasks (TASK scope) with this folder
     ITERATE → Provide failure_feedback targeting specific document numbers
     PAUSE → Clarify ticket requirements before proceeding
```

## Derivation Table

Fields that exist only in the human-readable output (not present in the agent-native spec):

| Human Field | Agent-Native Source | Derivation Rule |
|-------------|-------------------|-----------------|
| Investigation Summary (02) | root_cause.execution_path_trace | Summarize the trace: "Investigation traced from {entry} through {N} components to {error_site}. {evidence_summary}." |
| Strategy paragraph (03-B) | fix_approach.strategy key-value + fix_approach.files list | "The fix targets {file} by {action}. This approach {rationale}, following {pattern} at {reference}." |
| "How to Use This Research" (00) | N/A — static content | Fixed instructional text (5 numbered steps) |
| "Next Steps" (00) | N/A — static content | APPROVE / ITERATE / PAUSE options |
| Document Navigation descriptions (00) | All sections' key metrics | "{severity}, {urgency}" / "{confidence}" / "{N} files, {risk}" / "{N} ticket + {N} derived" / "{N} write, {N} update" |
| Quick Navigation (all docs) | Static links based on document structure | Fixed 6-document link set per document |
| Session Audit Trail (00) | Audit file sources + validation results | Sources table + validation results table from Step 5 audit |
| Scope Assessment ratings (01) | ticket_summary.severity + affected_areas | Derive Fix Complexity, Regression Risk, Urgency from severity level and affected area breadth |

## Partial Rendering Notes

- `full` — Generate all 6 documents (00-05) in order (content docs first, index last)
- `section:{name}` — Generate ONLY that document:
  - `section:index` → 00-research-index.md
  - `section:bug_summary` → 01-bug-summary.md
  - `section:root_cause` → 02-root-cause-analysis.md
  - `section:impact_and_fix` → 03-impact-and-fix.md
  - `section:acceptance_criteria` → 04-acceptance-criteria.md
  - `section:test_strategy` → 05-test-strategy.md
- `agenda_only` — Not applicable (no meeting agenda in bug-fix research)
- `review_package` — Generate: 00-research-index.md, 02-root-cause-analysis.md, 03-impact-and-fix.md (reviewer's fast path — understand cause, assess risk, review fix plan)

## Status Markers

| Status | Rendering |
|--------|-----------|
| complete | No marker (clean rendering) |
| pending | ⚠️ [PENDING INPUT — {field}] |
| assumption | [Assumption] |
| hypothesis | [Hypothesis — verify in codebase] |
| unknown | [Unknown — verify in build file] |
| inference | [Inference — {rationale}] |
| draft (spec-level) | Banner: "⚠️ DRAFT — Contains {N} pending inputs and {N} assumptions requiring validation" |
| complete (spec-level) | Banner: "✅ COMPLETE — All items validated, no pending inputs" |
