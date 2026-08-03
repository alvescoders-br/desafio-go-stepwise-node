# Findings Classification Protocols

Read this reference at Step 4 (Adversarial Code Review) — these three protocols govern how to classify findings during constraint verification, deviation analysis, and tool-status checks. They apply on every review round (FRESH and REPAIR).

---

## ADR Binding Protocol (resolve before 4.4 constraint verification)

Classify each ADR before applying section 4.4:

```
FOR each adr_decision in research.adrs:
  1. Check context-pack/adr-enforcement-rules.md (if exists):
     - BINDING section → classify as BINDING
     - ADVISORY section → classify as ADVISORY

  2. If adr-enforcement-rules.md does not exist, use the ADR's own status field:
     - status: Accepted → BINDING
     - status: Proposed, Superseded, Deprecated → ADVISORY

  3. If no status field, scan ADR content for explicit markers:
     - "MUST", "mandatory", "required", "binding" → BINDING
     - "SHOULD", "preferred", "recommended", "advisory" → ADVISORY
     - No marker → default ADVISORY; log as assumption
```

BINDING ADR violations → `severity: "BLOCKING"`, `category: "ADR_VIOLATION"`
ADVISORY ADR deviations (undocumented) → `severity: "HIGH"`, `category: "ADR_DEVIATION_UNDOCUMENTED"`

---

## Functional Equivalence Check — Plan Deviation Classification

Before marking any plan deviation as HIGH or BLOCKING:

1. Verify whether the EXPECTED BEHAVIOR (not the exact mechanism) is achieved:
   - If the plan requires a build task: check if the task exists in the build output
   - If the plan requires a class/method: check if it exists and compiles
   - If the plan requires a config value: check the effective configuration
2. If the expected behavior IS achieved via an alternative mechanism:
   - Downgrade severity to MEDIUM or LOW
   - Document: "Functionally achieved via [alternative] — plan mechanism not
     required and would [cause X issue if applied literally]"
   - Do NOT flag as HIGH or BLOCKING
3. If the expected behavior is NOT achieved:
   - Flag at the severity specified by the plan (HIGH/BLOCKING as appropriate)
4. LOG each equivalence check: "PLAN-DEV-{N}: {plan item} — {ACHIEVED|NOT_ACHIEVED} via {mechanism}"

---

## MTP Tool Classification Honor Protocol (MANDATORY)

Before flagging a missing test tool as BLOCKING:

1. Locate the MTP-SPEC for this project (path: `{{master_test_plan_path}}`, or scan `artifacts/outputs` for `MTP-SPEC-*.md`)
2. Find the tool in the MTP's tool classification table
3. Check its `blocking_status` field:
   - `blocking` → flagging as BLOCKING is correct
   - `optional` or `desirable_not_blocking` → flag as ADVISORY only, NOT BLOCKING
4. If the MTP cannot be located → flag as ASSUMPTION and note "MTP not found; blocking status unverified"

VIOLATION: Flagging a tool as BLOCKING when the MTP defines it as `desirable_not_blocking` or `optional` is an incorrect review verdict. The MTP-SPEC `blocking_status` is the authoritative source.
