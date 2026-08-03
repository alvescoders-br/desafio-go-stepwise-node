# Feature Implementation Research Consistency Rules

Read this reference at Step 3 (Generate Spec). The 10 rules below apply to ALL sections.

```
# RULE 1: Codebase Fidelity
# All file references MUST be real paths from SOURCE_CONTEXT.project_structure.
# If source not provided, mark every file reference as [Assumption].
# NEVER invent file paths.

# RULE 2: Story AC Preservation
# Every acceptance criterion from STORY_CONTEXT.ac MUST appear verbatim in
# acceptance_criteria.story_ac table. If story has no AC, derive from
# description and mark as [Derived].

# RULE 3: Technology Fidelity
# Use EXACT technology names and versions from SOURCE_CONTEXT.dependencies
# or ARCH_CONTEXT.tech_stack. Never hallucinate versions.
# If unknown, mark [Unknown — verify in build file].

# RULE 4: API Contract Fidelity (when API_CONTEXT available)
# New/modified endpoints MUST match API_CONTEXT.endpoints.
# Do NOT invent endpoint paths or request/response shapes not in the contract.
# If no contract, infer from codebase patterns and mark [Inferred — no contract provided].

# RULE 5: Design Spec Fidelity (when DESIGN_CONTEXT available)
# Screen names and component names MUST match DESIGN_CONTEXT.
# Do NOT invent UI components not specified.
# If no design specs, infer from existing UI patterns and mark [Inferred — no design spec].

# RULE 6: Architecture Constraint Respect (when ARCH_CONTEXT available)
# Implementation approach MUST respect ARCH_CONTEXT.constraints and patterns.
# Deviations must be explicitly noted with rationale.

# RULE 7: Zero Invention Policy
# Every factual claim must trace to story, source code, design spec, API contract,
# or architecture notes. Research inferences are marked [Inference] with rationale.
# Gaps are surfaced in open_questions — never silently resolved.

# RULE 8: Anti-Fade
# test_strategy section must have the same depth and detail as story_summary.
# Do not degrade quality in later sections.

# RULE 9: Story Contract Mode + Hashes
# Detect story contract_mode automatically: structured, partial, or unstructured.
# Unstructured external inputs are valid. Structured mode requires every
# content_hash/*_source_hash/source_hash value to match
# sha256:<64 lowercase hex chars>. Invalid hash values demote to partial and
# create evidence_gaps. In partial mode, cross-check structured rows against
# prose-derived IDs, literals, and fallbacks.

# RULE 10: Auth Security Defaults
# For auth, session, identity, OAuth, or password-reset stories, persisted
# reset tokens must be hashed at rest and OAuth provider values must come from
# an explicit allow-list. Missing proof becomes evidence_gaps unless a binding
# upstream source explicitly overrides it.
```

## Status Protocol

- Every item has a `status` field: `complete`, `pending`, or `assumption`
- `complete`: all fields populated from source evidence
- `pending`: one or more fields missing -> item also registered in `open_questions`
- `assumption`: inferred from industry standard -> ASM-XX ID assigned

## Source Tagging

- Every item has a `source` field pointing to SOURCE_LOG entry
- No source -> status MUST be `pending` or `assumption`
