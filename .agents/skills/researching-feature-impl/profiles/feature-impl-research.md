# Rendering Profile: Feature Implementation Research Spec -> Human-Readable Research Document Set

## Input
Agent-native Feature Implementation Research spec file (RESEARCH-SPEC-*.md).
Single file containing 9 structured sections plus metadata.

## Renderable Sections
(use with `render_scope: section:{name}`)

| Section Name | Source Data | Rendering |
|-------------|------------|-----------|
| index | all sections | Navigation table, quick stats, validation summary, "How to Use", "Next Steps" |
| story_summary | story_summary | Story overview table, user story statement (prose from persona/goal/benefit), description, scope, affected areas, dependencies, constraints, complexity |
| codebase_analysis | codebase_analysis | Tech stack table, project structure tree, current state prose (derived), existing capability, gap analysis, similar features, architecture layers, conventions |
| impact_assessment | impact_assessment | Direct/indirect impact, dependencies affected, data/API/UI impact, risk summary |
| integration_mapping | integration_mapping | Integration overview prose (derived), module integration points, data flow diagrams, new data entities, UI/API integration, external services, architecture constraints, integration risk |
| implementation_approach | implementation_approach | Strategy summary prose (derived), implementation phases, files to create/modify, implementation steps, code patterns, edge cases, constraints, out-of-scope improvements |
| acceptance_criteria | acceptance_criteria | Story AC, derived AC, UI/API criteria, regression criteria, Definition of Done |
| test_strategy | test_strategy | Tests tables (write + update), commands, coverage matrix, coverage targets, integration scenarios, manual verification steps |
| audit_trail | AUDIT file + validations | Session metadata, sources, metrics, validation results, change log |

## Full Render Order

```
1. STORY SUMMARY (section: story_summary)
   Generate 01-story-summary.md
   - Document header with YAML frontmatter (document_id, type, session_id, project, date, mode)
   - "Story Overview" table:
     Render story_summary.overview fields as key-value rows:
     Story ID, Title, Format, Priority, Parent Epic, Source
   - "User Story Statement" section:
     IF story_summary.overview.format == "user_story":
       **As a** {persona} **I want** {goal} **So that** {benefit}
     ELSE:
       ## Feature Description
       {goal}
   - "Full Description" section:
     Render story_summary.description verbatim — no summarization, no invention
   - "Scope" section:
     "What this story covers:" — bullet list from story_summary.scope.in_scope
     "What this story does NOT cover:" — bullet list from story_summary.scope.out_of_scope
   - "Affected Areas (from story)" table:
     Render story_summary.affected_areas as: Area | Type | Notes
   - "Dependencies (from story)" table:
     Render story_summary.dependencies as: Dependency | Type | Status
   - "Constraints" table:
     Render story_summary.constraints as: Constraint | Source
   - "Complexity Assessment" table:
     Render as: Aspect | Rating | Rationale
     Rows: Overall Complexity, Regression Risk, Integration Complexity, Implementation Complexity
   - "Optional Inputs Provided" table:
     Source Code, Design Specs, API Contract, Architecture Notes, Context Pack — load status
     Derive from AUDIT file sources
   - References footer: [REF-01] {story_path}
   - Quick Navigation: static links to all 9 documents

2. CODEBASE ANALYSIS (section: codebase_analysis)
   Generate 02-codebase-analysis.md
   - Document header with YAML frontmatter
   - "Technology Stack (from source code)" table:
     Render codebase_analysis.tech_stack as: Layer | Technology | Version | Source
     IF no source -> "[Technology stack not available — no source code provided]"
   - "Project Structure (relevant areas)" section:
     Render codebase_analysis.project_structure as indented tree code block
   - "Current State — What Exists" paragraph:
     Derive from codebase_analysis.existing_capability + gap_analysis:
     "The codebase currently provides {capabilities}. To fulfill the story,
     the following gaps must be addressed: {gaps}."
   - "Existing Capability" table:
     Render as: Capability | Location | Relevant to Story?
   - "Gap Analysis" table:
     Render as: Gap | Impact on Feature | Severity
   - "Similar Features (Pattern Reference)" table:
     Render as: Feature | Location | Pattern | Reuse Potential
   - "Architecture Layers" subsections:
     Data Layer, API Layer, UI Layer — each as: Aspect | Current State | Feature Impact
   - "Conventions to Follow" table:
     Render as: Convention | Example Location | Apply To
   - References footer
   - Quick Navigation

3. IMPACT ASSESSMENT (section: impact_assessment)
   Generate 03-impact-assessment.md
   - Document header with YAML frontmatter
   - "Direct Impact (Files to Change)" table:
     Render impact_assessment.direct_impact as: File | Change Type | Risk | Reason
   - "Indirect Impact (Potential Regressions)" table:
     Render impact_assessment.indirect_impact as: Component | How Affected | Risk | Mitigation
   - "Dependencies Affected" table:
     Render as: Dependency | Type | Impact | Action Required
   - "Data Impact" table:
     Render as: Data Store | Impact | Migration Needed? | Rollback Strategy
     IF none -> "None" row
   - "API / Interface Impact" table:
     Render as: Interface | Change | Breaking? | Consumers | Migration Path
     IF none -> "None" row
   - "UI Impact" table:
     Render as: Screen / Component | Change | Risk | Notes
     IF none -> "None" row
   - "Risk Summary" table:
     Render as: Dimension | Rating | Rationale
     Rows: Overall Risk, Regression Risk, Data Risk, API Risk, UI Risk
   - References footer
   - Quick Navigation

4. INTEGRATION MAPPING (section: integration_mapping)
   Generate 04-integration-mapping.md
   - Document header with YAML frontmatter
   - "Integration Overview" paragraph:
     Derive from integration_mapping.module_integration_points:
     "This feature integrates with {N} existing modules: {module_list}.
     Primary integration pattern: {dominant integration_type}."
   - "Module Integration Points" table:
     Render as: # | Existing Module | Integration Type | Feature Interaction | Files Involved
   - "Data Flow" sections:
     "Current Data Flow" — render current_flow as diagram block
     "Data Flow After Feature" — render flow_after_feature as diagram block
   - "New Data Entities" table:
     Render as: Entity | Store | Relationships | Notes
   - "UI Integration" subsections:
     Navigation / Routing Changes table
     Component Hierarchy diagram block
     Screen / View Mapping table (if DESIGN_CONTEXT)
   - "API Integration" subsections:
     New Endpoints table
     Modified Endpoints table
   - "External Service Integration" table
   - "Architecture Constraint Compliance" table
   - "Integration Risk Assessment" table
   - References footer
   - Quick Navigation

5. IMPLEMENTATION APPROACH (section: implementation_approach)
   Generate 05-implementation-approach.md
   - Document header with YAML frontmatter
   - "Strategy Summary" paragraph:
     Derive from implementation_approach.strategy:
     "The implementation targets {approach} following the {primary_pattern}
     pattern at {pattern_location}. {rationale}."
   - "Implementation Phases" table:
     Render as: Phase | Description | Files | Dependency
   - "Files to Create" table:
     Render as: File Path | Purpose | Pattern Reference | Phase
   - "Files to Modify" table:
     Render as: File Path | Change | Pattern Reference | Phase
   - "Implementation Steps" — phased numbered list
   - "Code Patterns" — code blocks with comments
   - "Edge Cases" table:
     Render as: Edge Case | Handling | Phase
   - "Constraints" bullet list
   - "Suggested Improvements (Out of Scope)" table
   - References footer
   - Quick Navigation

6. ACCEPTANCE CRITERIA (section: acceptance_criteria)
   Generate 06-acceptance-criteria.md
   - Document header with YAML frontmatter
   - "Criteria from Story (MANDATORY — preserve verbatim)" table:
     Render acceptance_criteria.story_ac as: # | Criterion | Source | Verification
     IF empty -> "[No acceptance criteria provided in story.]"
   - "Derived Criteria" table:
     Render acceptance_criteria.derived_ac as: # | Criterion | Rationale | Verification
   - "UI Criteria" table (if DESIGN_CONTEXT):
     Render acceptance_criteria.ui_ac as: # | Criterion | Design Reference | Verification
   - "API Criteria" table (if API_CONTEXT):
     Render acceptance_criteria.api_ac as: # | Criterion | Contract Reference | Verification
   - "Regression Criteria" table:
     Render acceptance_criteria.regression_ac as: # | Criterion | Verification
   - "Definition of Done" checklist (unchecked)
   - References footer
   - Quick Navigation

7. TEST STRATEGY (section: test_strategy)
   Generate 07-test-strategy.md
   - Document header with YAML frontmatter
   - "Tests to Write" table:
     Render test_strategy.tests_to_write as: Test | Type | File | Covers | Phase
   - "Tests to Update" table:
     Render test_strategy.tests_to_update as: Test | File | Change Needed | Reason
   - "Test Commands" bash code block
   - "Test Coverage Matrix" table:
     Render as: AC / Criterion | Test Type | Test File | Status
   - "Coverage Targets" table:
     Render as: Area | Current | Target | Notes
   - "Integration Test Scenarios" table:
     Render as: Scenario | Modules Involved | Expected Outcome
   - "Manual Verification Steps" numbered list
   - References footer
   - Quick Navigation

8. SESSION AUDIT TRAIL (section: audit_trail)
   Generate 08-session-audit-trail.md
   - Document header with YAML frontmatter
   - "Session Metadata" table (from AUDIT file)
   - "Sources Referenced" table (from AUDIT file)
   - "Research Metrics" table (from AUDIT file summary counts)
   - "Validation Audit Results" table (from spec validations section)
   - IF REPAIR mode -> "Change Log" table
   - Quick Navigation

9. RESEARCH INDEX (section: index) — GENERATED LAST
   Generate 00-research-index.md
   - Document header with YAML frontmatter including total_documents and story_id
   - "Session Overview" table:
     Session ID, Mode, Project, Story (ID + title), Format, Persona, Date, Document count
   - "Document Navigation" table:
     # | Document | Description | Key Info
     Derive descriptions from section contents
     Links as relative markdown links
   - "Quick Stats" table:
     Story Format, Overall Complexity, Overall Risk, Integration Points,
     Affected Files, New Files, Data Model Changes, API Changes, UI Changes,
     AC from Story, AC Derived, Tests to Write, Tests to Update
   - "Validation Summary" table:
     All 10 checks with PASS/FAIL/N/A
   - "How to Use This Research" section — STATIC CONTENT:
     1. Start here — review this index
     2. Understand the story — read 01-story-summary.md
     3. Understand the codebase — read 02-codebase-analysis.md
     4. Check integration — read 04-integration-mapping.md
     5. Plan implementation — use 05-implementation-approach.md
     6. Validate criteria — review 06-acceptance-criteria.md
     7. Review audit — check 08-session-audit-trail.md
   - "Next Steps" section — STATIC CONTENT:
     APPROVE -> Proceed to planning-code-tasks with this folder
     ITERATE -> Provide failure_feedback targeting specific sections
     PAUSE -> Clarify story requirements before proceeding
```

## Derivation Table

Fields that exist only in the human-readable output (not present in the agent-native spec):

| Human Field | Agent-Native Source | Derivation Rule |
|-------------|-------------------|-----------------|
| Current State prose (02) | codebase_analysis.existing_capability + gap_analysis | "The codebase currently provides {capabilities}. To fulfill the story, the following gaps must be addressed: {gaps}." |
| Integration Overview prose (04) | integration_mapping.module_integration_points | "This feature integrates with {N} existing modules: {module_list}. Primary integration pattern: {dominant type}." |
| Strategy Summary prose (05) | implementation_approach.strategy key-value | "The implementation targets {approach} following the {primary_pattern} pattern at {pattern_location}. {rationale}." |
| User Story Statement (01) | story_summary.persona_goal_benefit | "As a {persona} I want {goal} So that {benefit}" (or Feature Description for non-story formats) |
| "How to Use This Research" (00) | N/A — static content | Fixed instructional text (7 numbered steps) |
| "Next Steps" (00) | N/A — static content | APPROVE / ITERATE / PAUSE options |
| Document Navigation descriptions (00) | All sections' key metrics | "{format}, {priority}" / "{N} affected files" / "{risk}" / "{N} integration points" / "{N} files" / "{N} story + {N} derived" / "{N} write, {N} update" / "All checks" |
| Quick Navigation (all docs) | Static links based on document structure | Fixed 9-document link set per document |
| Optional Inputs table (01) | AUDIT file sources | Derive load status from source references |
| Session Audit Trail (08) | AUDIT file + spec validations | Session metadata + sources + metrics + validation results |

## Partial Rendering Notes

- `full` — Generate all 9 documents (00-08) in order (content docs first, index last)
- `section:{name}` — Generate ONLY that document:
  - `section:index` -> 00-research-index.md
  - `section:story_summary` -> 01-story-summary.md
  - `section:codebase_analysis` -> 02-codebase-analysis.md
  - `section:impact_assessment` -> 03-impact-assessment.md
  - `section:integration_mapping` -> 04-integration-mapping.md
  - `section:implementation_approach` -> 05-implementation-approach.md
  - `section:acceptance_criteria` -> 06-acceptance-criteria.md
  - `section:test_strategy` -> 07-test-strategy.md
  - `section:audit_trail` -> 08-session-audit-trail.md
- `review_package` — Generate: 00-research-index.md, 04-integration-mapping.md, 05-implementation-approach.md, 06-acceptance-criteria.md (reviewer's fast path — understand integration, review approach, validate criteria)

## Status Markers

| Status | Rendering |
|--------|-----------|
| complete | No marker (clean rendering) |
| pending | [PENDING INPUT — {field}] |
| assumption | [Assumption] |
| unknown | [Unknown — verify in build file] |
| inference | [Inference — {rationale}] |
| draft (spec-level) | Banner: "DRAFT — Contains {N} pending inputs and {N} assumptions requiring validation" |
| complete (spec-level) | Banner: "COMPLETE — All items validated, no pending inputs" |
