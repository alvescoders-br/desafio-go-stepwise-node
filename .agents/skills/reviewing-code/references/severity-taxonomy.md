# Severity Taxonomy & Repair Feedback Quality

Read this reference at Step 2 (Load Verification Context) — every finding you generate uses these severity levels and the actionable-feedback rule.

---

## Severity Classification

```
BLOCKING (Must fix before merge)
  - Missing required functionality
  - Failing tests
  - Security vulnerabilities (critical/high)
  - Secure-default defects SD-01..SD-06 (see references/secure-defaults-taxonomy.md):
    auth/authz fails open, dev/mock bypass reachable in production, secrets
    written unencrypted/world-readable, secret duplicated across sinks, secret
    written without owner-only permissions, secrets committed/not ignored.
    These are BLOCKING by class — do NOT downgrade on a "dev only / mock /
    temporary" rationalization.
  - Research constraint violations
  - Undocumented deviations from plan
  - Acceptance criteria not met

HIGH (Should fix before merge)
  - Partial implementations
  - Missing edge case handling
  - Test coverage below threshold
  - Performance concerns
  - Security vulnerabilities (medium)
  - Secure-default defects SD-07..SD-10 (see references/secure-defaults-taxonomy.md):
    auth-bearing cookie/token without protective flags, privileged endpoint
    without authn/authz or rate limiting, non-durable audit log that claims
    durability, generated secret with no rotation/canonical source. Escalate to
    BLOCKING when the same finding also satisfies an SD-01..SD-06 class.

MEDIUM (Fix soon after merge)
  - Code quality issues
  - Documentation gaps
  - Minor deviations with justification
  - Technical debt introduced

LOW (Track for future)
  - Style inconsistencies
  - Optimization opportunities
  - Nice-to-have improvements
```

---

## REPAIR Feedback Quality Rule

```
RULE: ACTIONABLE REPAIR FEEDBACK

Each blocking/high issue MUST include:
  1. Exact file path and line range (e.g., header.html:29-51)
  2. BEFORE snippet — the current code that is wrong (5-15 lines)
  3. AFTER snippet — the corrected code the implementation agent should produce
  4. Verification hint — how to confirm the fix worked

Feedback that only describes WHAT is wrong without showing HOW to fix it
causes unnecessary repair cycles. The implementation agent should be able
to apply the fix mechanically from the feedback alone.
```
