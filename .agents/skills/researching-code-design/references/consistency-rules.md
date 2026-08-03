# Upstream Consistency Rules

Read this reference at the start of Step 3 (Generate Spec). The 15 rules below are enforced for every section, every entry, every claim. They are non-negotiable.

```
RULE 1  — Technology Fidelity: EXACT names/versions from ADRs or source. Never generalize.
  Why: Generalized names ("a cache layer") prevent the planner from generating correct
  dependency/config files. Specificity ("Redis 7.2") enables correct implementation.

RULE 2  — NFR ID Preservation: PRD ORIGINAL NFR IDs verbatim. Never renumber.
  Why: Renumbered IDs break traceability chains — downstream consumers can't match
  NFR-03 in the plan back to the PRD. Compliance audits fail.

RULE 3  — PRD Risk Carry-Forward: Every RSK-XX from PRD MUST appear in risks.
  Why: Dropped risks aren't "resolved" — they're invisible. The implementing agent
  assumes silence means "no risk here" and skips mitigation.

RULE 4  — PRD Assumption Carry-Forward: Every ASM-XX from PRD MUST appear in assumptions.
  Why: Uncarried assumptions become silent dependencies. If ASM-05 ("third-party API
  is stable") fails, nobody tracks the blast radius.

RULE 5  — Persona Coverage: Every persona from PRD MUST be referenced.
  Why: Uncovered personas mean missing user journeys. Epics/stories traced to that
  persona lack research backing, producing incomplete plans.

RULE 6  — Upstream Gap Surfacing: Every PENDING INPUT, traceability gap MUST appear in open_questions.
  Why: Gaps buried in upstream docs become silent unknowns. Surfacing them forces
  explicit decisions before implementation begins.

RULE 7  — API Path Fidelity: PRD API paths VERBATIM. No drift.
  Why: Even minor path drift ("/users/{id}" → "/user/{id}") causes integration
  failures with documented API consumers and contract tests.

RULE 8  — Integration Notes for Discovered Artifacts:
  For each constant, configuration value, behavioral flag, or reusable pattern
  discovered in existing source code, produce an integration_note:
    | artifact | defined_in | applied_in | usage_pattern | status |
  If the application site cannot be determined from source analysis: status = pending,
  register in open_questions.
  Why: Research that reports WHAT exists but not WHERE it connects produces planning
  gaps. The planner receives a constant value but no call-site context, leading to
  orphaned definitions and missing wiring in the implementation plan.

RULE 9  — KPI Traceability: Every KPI-XX MUST be mapped.
  Why: Unmapped KPIs have no measurement implementation. The feature ships without
  the instrumentation to prove it works.

RULE 10 — JTBD Traceability: Every JTBD-XX MUST be referenced.
  Why: Unreferenced Jobs-To-Be-Done mean the research doesn't cover the user's core
  motivation. Planning produces features nobody needs.

RULE 11 — FR Coverage: Every FR-XX MUST be mapped to implementation components.
  Why: Unmapped FRs are unimplemented requirements. The planning agent won't generate
  tasks for them — they silently disappear from the build.

RULE 12 — Story Count Validation: Actual count must match reported count.
  Why: Count mismatches indicate dropped stories. If PRD says 48 stories but research
  covers 42, six stories get no implementation plan.

RULE 13 — Anti-Fade: Last section MUST match depth of first.
  Why: LLM attention fades toward the end. If section 1 has 50 items and section 19
  has 5, the later sections are incomplete — planner inherits the gaps.

RULE 14 — Cross-Section Consistency: session_id, project name, date consistent.
  Why: Inconsistent metadata breaks automation. If section 3 references a different
  session_id, the planner can't link artifacts across sections.

RULE 15 — Schema Literal Preservation (from acceptance criteria):
  Whenever a story's acceptance criteria reference a deeplink, query parameter,
  enum, URL fragment, response field name, or any literal string that the
  implementation must produce verbatim, you MUST extract these literals into a
  dedicated `## Parameter Schema` section of the research spec.

  This section is MANDATORY when ANY of the following appear in the story:
    - A URL or deeplink example (e.g., `https://app.example/foo?source=bar`)
    - Query parameter names with sample values
    - Enum literals quoted in the AC text (e.g., "values: 'pending', 'accepted'")
    - Fixed response field names (e.g., a JSON example in the AC)
    - Identifier formats with examples (e.g., "id format: cust_<uuid>")

  For each such literal, record:
    | source_story | parameter | canonical_values | producer | consumer |
    |---|---|---|---|---|
    | US-XX-YY | source | sit_with_friends_invite, accepted, cancelled, expired | DeeplinkParser | OriginEnum |

  Why: When research records "the deeplink takes a `source` parameter" without
  the canonical values, the planning and implementation skills are forced to
  invent values that compile but do not match the story. The mismatch is only
  caught at code-review (or in production), at high cost. A prior calibration
  (LAC-Android Chapter 2, RC-003) traced 3 repair cycles and a forced approval
  to a `SitWithFriendsOrigin` schema mismatch caused by missing literal capture.

  Where the section appears in the spec: place `## Parameter Schema` AFTER
  `## acceptance_criteria` and BEFORE `## file_specifications`. Reference the
  schema rows from `## acceptance_criteria` traceability columns and from
  `## file_specifications` data contracts.
```
