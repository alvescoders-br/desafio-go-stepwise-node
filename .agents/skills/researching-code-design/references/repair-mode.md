# REPAIR Mode

Read this reference at Step 1 **only when** `failure_feedback` is non-empty (OPERATION_MODE == REPAIR). In BUILD mode, this file does not apply — skip it.

```
IF OPERATION_MODE == REPAIR:
  0. Read `loading_strategy` from existing RESEARCH-SPEC header:
     - IF loading_strategy == "two-tier" → use the Two-Tier Context Loading model (Step 2B).
       Tier 1 must be re-loaded for targeted sections; Tier 2 is loaded on-demand per section.
     - IF loading_strategy is absent or "legacy" → load all inputs as full context (pre-two-tier model).
  1. Load existing RESEARCH-SPEC from SPEC_FILE
  2. Match REPAIR_DIRECTIVES to sections
  3. Regenerate ONLY targeted sections
  4. Preserve untargeted content verbatim
  5. Preserve existing IDs. New items: max(existing) + 1. Retired IDs: never reuse.
  6. ALWAYS rebuild open_questions and validations from scratch (reflect current state)
  7. Increment version, log all changes in AUDIT file
```
