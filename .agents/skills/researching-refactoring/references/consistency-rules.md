# Refactoring Research Consistency Rules

Read this reference at Step 3 (Generate Spec). The 11 rules below apply to ALL sections.

```
# RULE 1: Codebase Fidelity
# All file references MUST be real paths from SOURCE_CONTEXT.project_structure.
# NEVER invent file paths. Every affected file must be verified against the tree.

# RULE 2: Version Fidelity
# Use EXACT version numbers from SOURCE_CONTEXT.dependencies and build files.
# Never hallucinate library versions. If undetectable, mark [Unknown — verify in build file].

# RULE 3: Breaking Change Traceability
# Every breaking change in compatibility_analysis MUST trace to one of:
#   - GUIDE_CONTEXT.breaking_changes (official migration guide)
#   - SOURCE_CONTEXT.deprecated_api_usage (detected in code)
#   - Known platform changelog (cite version and change ID if available)
# Do NOT invent breaking changes not supported by evidence.
# If unsure, mark [Needs verification — not confirmed in migration guide].

# RULE 4: Dependency Version Accuracy
# Every library in dependency_migration_matrix MUST match SOURCE_CONTEXT.dependencies exactly.
# Target-compatible versions MUST come from GUIDE_CONTEXT or known compatibility matrices.
# If unknown, mark [Compatibility unknown — test required].

# RULE 5: Migration Guide Fidelity (when GUIDE_CONTEXT available)
# Migration steps in migration_sequence MUST respect official recommended sequence.
# Deviations must be explicitly noted with rationale.

# RULE 6: Architecture Constraint Respect (when ARCH_CONTEXT available)
# Migration approach MUST respect ARCH_CONTEXT.constraints.
# If migration requires architectural changes, document them explicitly.

# RULE 7: Zero Invention Policy
# Every factual claim must trace to source code, migration spec, migration guide,
# or architecture notes. Research inferences are marked [Inference] with rationale.
# Gaps are surfaced in open_questions — never silently resolved.

# RULE 8: Anti-Fade
# test_strategy section must have the same depth and detail as scope_summary.
# Do not degrade quality in later sections.

# RULE 9: Refactor Contract Mode + Hashes
# Detect migration/refactoring spec contract_mode automatically: structured,
# partial, or unstructured. Unstructured external inputs are valid. Structured
# mode requires every content_hash/*_source_hash/source_hash value to match
# sha256:<64 lowercase hex chars>. Invalid hash values demote to partial and
# create evidence_gaps. In partial mode, cross-check structured rows against
# prose-derived IDs, literals, and fallbacks.

# RULE 10: Auth Security Defaults
# For auth, session, identity, OAuth, or password-reset refactors, persisted
# reset tokens must be hashed at rest and OAuth provider values must come from
# an explicit allow-list. Missing proof becomes evidence_gaps unless a binding
# upstream source explicitly overrides it.

# RULE 11: Non-Blocking Gap Fallbacks
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

## Refactoring Type Gating

- If `refactoring_type == version_upgrade`: skip `coupling_analysis` section (mark N/A)
- If `refactoring_type == structural`: skip `compatibility_analysis.version_map`, reduce `dependency_migration_matrix` to structural deps only
- If `refactoring_type == combined`: all sections fully populated
