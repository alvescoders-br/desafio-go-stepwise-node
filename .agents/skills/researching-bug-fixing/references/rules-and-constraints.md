# Bug-Fix Research Consistency Rules

Read this reference at Step 3 (Generate Spec). The 9 rules below apply to ALL sections.

```
# RULE 1: Codebase Fidelity
# All file references MUST be real paths from SOURCE_CONTEXT.project_structure.
# If source not provided, mark every file reference as [Assumption].
# NEVER invent file paths.

# RULE 2: Root Cause Traceability
# Root cause MUST reference a specific file:line from SOURCE_CONTEXT.
# If source not provided, state root cause as [Hypothesis — verify in codebase].

# RULE 2a: Checked Exception Constraint Analysis
# When a fix involves throwing or catching checked exceptions, identify the
# interface contracts that constrain the fix. Note any checked exception
# constraints in the implementation_landmines section.

# RULE 3: Ticket AC Preservation
# Every acceptance criterion from TICKET_CONTEXT.ac MUST appear verbatim in
# acceptance_criteria.ticket_ac table. If ticket has no AC, derive from
# description and mark as [Derived].

# RULE 4: Technology Fidelity
# Use EXACT technology names and versions from SOURCE_CONTEXT.dependencies.
# Never hallucinate versions. If unknown, mark [Unknown — verify in build file].

# RULE 5: Zero Invention Policy
# Every factual claim must trace to ticket or source code.
# Research inferences are marked [Inference] with rationale.
# Gaps are surfaced in open_questions — never silently resolved.

# RULE 6: Anti-Fade
# test_strategy section must have the same depth and detail as ticket_summary.
# Do not degrade quality in later sections.

# RULE 7: Ticket Contract Mode + Hashes
# Detect ticket contract_mode automatically: structured, partial, or
# unstructured. Unstructured external tickets are valid. Structured mode
# requires every content_hash/*_source_hash/source_hash value to match
# sha256:<64 lowercase hex chars>. Invalid hash values demote to partial and
# create evidence_gaps. In partial mode, cross-check structured rows against
# prose-derived IDs, literals, and fallbacks.

# RULE 8: Auth Security Defaults
# For auth, session, identity, OAuth, or password-reset defects, persisted reset
# tokens must be hashed at rest and OAuth provider values must come from an
# explicit allow-list. Missing proof becomes evidence_gaps unless a binding
# upstream source explicitly overrides it.

# RULE 9: Non-Blocking Gap Fallbacks
# Every non-blocking pending input or assumption must include fallback_behavior.
# If no safe fallback exists, mark blocking=yes.
```

## Status Protocol

- Every item has a `status` field: `complete`, `pending`, or `assumption`
- `complete`: all fields populated from source evidence
- `pending`: one or more fields missing → item also registered in `open_questions`
- `assumption`: inferred from industry standard → ASM-XX ID assigned

## Source Tagging

- Every item has a `source` field pointing to SOURCE_LOG entry
- No source → status MUST be `pending` or `assumption`
