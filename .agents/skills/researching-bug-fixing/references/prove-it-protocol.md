# Prove-It Pattern — Bug Fix Protocol

Read this reference at Step 3 when generating `acceptance_criteria` and `test_strategy`. This protocol governs how reproduction tests are described in the spec so the downstream planning + implementation agents can enforce a failing-first test.

When this research skill feeds into planning-code-tasks and implementing-code, the downstream implementation MUST follow the Prove-It protocol:

```
RESEARCH PHASE (this skill):
  - Identify the exact reproduction steps from the ticket
  - Translate reproduction steps into test scenarios in test_strategy
  - Mark each test scenario as: REPRODUCE (must fail before fix) or GUARD (must pass after fix)
  - Include in acceptance_criteria: "Reproduction test fails before fix, passes after fix"

DOWNSTREAM CONTRACT:
  - planning-code-tasks MUST include a "Write reproduction test" task as Phase 1, Step 1
  - implementing-code MUST execute the reproduction test BEFORE implementing the fix
  - If reproduction test passes before fix → root cause analysis is wrong. Return to research.
```

VIOLATION: A bug-fix research spec without reproduction test scenarios in test_strategy is incomplete. The implementing agent has no way to verify the fix without a failing-first test.
