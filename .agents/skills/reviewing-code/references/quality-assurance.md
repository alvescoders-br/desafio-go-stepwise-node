# Quality Assurance — Rationalizations, Red Flags, Verification

Read this reference at the **Step 8 → Step 9 boundary** (after generating REVIEW-SPEC, before writing outputs). The three sections below catch superficial reviews and surface evidence gaps before the spec is written to disk.

---

## Common Rationalizations (and counters)

| Excuse | Why It Fails | Counter |
|--------|-------------|---------|
| "The code works, so it passes review" | Working code can still have security holes, readability issues, and architectural violations. "Works" is necessary but not sufficient. | Apply all 6 adversarial principles. A passing build is evidence of compilation, not compliance. |
| "The deviation is minor, not worth flagging" | Minor undocumented deviations accumulate into major architectural drift. Principle 4 requires ALL deviations to be challenged. | Flag it. Severity classification (LOW/MEDIUM) exists for this purpose. Minor ≠ ignorable. |
| "I don't have the full context to review this" | The plan, research, and IMPL-STATE provide all context. If something is missing, that's a finding, not an excuse. | Use what's available. Missing context is itself a BLOCKING finding (incomplete documentation). |
| "The tests pass, so test quality is fine" | Principle 5: "Tests pass" means nothing without seeing test quality. Passing trivial tests proves nothing. | Review test assertions, edge case coverage, and meaningful failure messages. Count assertions per test. |
| "This is a REPAIR round, I only need to check the fixes" | REPAIR reviews must re-verify ALL previous findings plus new ones. Regression during repair is common. | Stable checklist across ALL rounds. Re-verify every finding from prior rounds. |
| "The author explained the code verbally, so I understand the intent" | Verbal explanations don't persist. If the code needs explanation, it needs refactoring or documentation. | If intent isn't clear from code + comments + plan, flag as readability finding. |

---

## Red Flags

Signs that this review is being conducted superficially or incorrectly:

- Review completed in under 5 minutes for >100 lines of code (indicates skimming, not reviewing)
- Zero findings on a non-trivial implementation (statistical improbability — even good code has suggestions)
- All findings are LOW severity (avoiding confrontation, not reviewing critically)
- No BLOCKING findings despite missing files or failing tests
- Findings don't reference specific file:line locations (vague criticism, not actionable review)
- Tool verification skipped because "the build passed locally"
- REPAIR round doesn't re-verify previous findings (assumes fixes are correct without evidence)
- Review doesn't reference the plan or research specs (reviewing code in isolation, not against contract)
- Acceptance criteria marked as MET without citing verification method

---

## Verification Checklist

Every item requires **evidence**, not assertion. "Seems right" is never sufficient.

- [ ] Every planned file verified to exist — Evidence: file list comparison output (plan vs actual)
- [ ] Every finding cites file:line and evidence — Evidence: REVIEW-SPEC findings section with specific locations
- [ ] Severity classifications applied consistently — Evidence: no HIGH finding without code-level proof, no BLOCKING without impact analysis
- [ ] All acceptance criteria evaluated — Evidence: AC traceability matrix in REVIEW-SPEC with PASS/FAIL per criterion
- [ ] Tool results included — Evidence: build/test/lint command output captured in tool_results section
- [ ] Deviations challenged — Evidence: every IMPL-STATE deviation has a corresponding review finding (even if ACCEPTED)
- [ ] REPAIR findings re-verified — Evidence: prior findings listed with current status (FIXED/STILL_OPEN/REGRESSED)
- [ ] Review verdict justified — Evidence: PROCEED requires zero BLOCKING findings; REVISE cites specific blockers
