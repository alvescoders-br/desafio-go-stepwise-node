# Quality Gates — Output Guard, Rationalizations, Red Flags, Verification

Read this reference at the **Step 4 → Step 5 boundary** (after the quality validation gate, before writing outputs). The four sections below catch superficial bug-fix research before it ships.

---

## Minimum Output Length Guard

```
AFTER writing the final RESEARCH-SPEC, measure the output:

  SPEC_LENGTH = character count of RESEARCH-SPEC-{SESSION_ID}.md (excluding metadata header)

  IF SPEC_LENGTH < 5000:
    DO NOT mark the spec as complete.
    LOG: "OUTPUT GUARD: Research spec is {SPEC_LENGTH} characters — below 5,000 minimum."
    RETRY with more focused approach:
      1. Re-read the ticket and source code with deeper analysis
      2. Expand root cause analysis with additional file:line evidence
      3. Add more detail to impact assessment and fix approach
      4. Ensure test strategy has concrete test scenarios
    After retry, re-measure. If still < 5,000 after 2 retries:
      Mark spec_status as "shallow" and add to open_questions:
        "Research output below minimum depth threshold after retries.
         Human review recommended before proceeding to planning."

RATIONALE: Bug-fix research specs under 5,000 characters typically indicate
surface-level analysis that produces incomplete plans and missed edge cases
downstream. The threshold is deliberately conservative — most well-analyzed
bugs produce 8,000-15,000 character specs.
```

---

## Common Rationalizations

| Excuse | Why It Fails | Counter |
|--------|-------------|---------|
| "The bug is obvious, I don't need a research spec" | Obvious bugs often have non-obvious root causes. Skipping research leads to symptom-fixing, not root-cause fixing. | Even a 15-minute research pass prevents hours of re-work when the "obvious" fix doesn't hold. |
| "I already know the root cause" | Confirmation bias. Without evidence, you're guessing. The spec forces you to prove it. | Write the root cause analysis anyway. If you're right, it takes 5 minutes. If you're wrong, it saves days. |
| "The ticket has enough detail" | Tickets describe symptoms, not causes. Research bridges the gap between symptom and fix. | Extract what the ticket provides, then investigate what it doesn't: root cause, blast radius, regression risk. |
| "I'll just fix it and write tests" | Without research, you don't know the blast radius. Your fix may break adjacent functionality. | Research identifies impacted files, dependencies, and regression surfaces before you touch code. |
| "This is a one-line fix, no research needed" | One-line fixes with zero research are the #1 source of regressions. The line is easy; knowing WHICH line is hard. | The research spec is proportional to complexity. A one-line fix produces a short spec — that's fine. |

---

## Red Flags

Signs that this skill is being misapplied or circumvented:

- Root cause analysis says "unknown" or "to be determined" but spec is marked complete
- Impact assessment lists zero affected files (every bug affects at least one file)
- Fix approach doesn't reference specific files or line ranges
- No acceptance criteria derived from the bug's reproduction steps
- Test strategy section is empty or says "existing tests sufficient" without evidence
- Source code was not read during research (source_path not provided or not used)
- Spec generated in under 2 minutes for a non-trivial bug (indicates surface-level analysis)

---

## Verification Checklist

Every item requires **evidence**, not assertion. "Seems right" is never sufficient.

- [ ] Root cause identified with code evidence — Evidence: specific file:line references in root_cause section
- [ ] Impact assessment covers direct and transitive dependencies — Evidence: affected_files list with dependency chain
- [ ] Fix approach is actionable — Evidence: specific files to modify, patterns to apply, order of changes
- [ ] Acceptance criteria are testable — Evidence: each AC maps to a concrete test scenario
- [ ] Regression surface identified — Evidence: test_strategy lists existing tests to re-run
- [ ] All ticket acceptance criteria addressed — Evidence: 1:1 mapping from ticket ACs to spec ACs
- [ ] Open questions logged for unknowns — Evidence: open_questions section (may be empty if fully resolved)
- [ ] Source references tagged — Evidence: every item with status:complete has a source tag
