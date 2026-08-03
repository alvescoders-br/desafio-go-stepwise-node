# Adversarial Review Principles

Read this reference at the start of Step 1 (Initialize Session). The six principles below govern every finding, every PASS, every FAIL.

```
PRINCIPLE 1: Assume Non-Compliance
  - Start with assumption that implementation deviates from plan
  - Burden of proof is on the code to demonstrate compliance
  - Document evidence FOR compliance, not just absence of issues
  - Empty evidence = FAIL, not PASS

PRINCIPLE 2: Seek Discrepancies Actively
  - Compare plan file lists vs actual files created
  - Compare plan patterns vs actual patterns used
  - Compare research constraints vs actual implementation
  - Look for what's MISSING, not just what's WRONG

PRINCIPLE 3: Verify Completeness
  - Every story assigned to phase must have corresponding implementation
  - Every file specified must exist with correct content
  - Every test specified must exist and pass
  - Every acceptance criterion must be demonstrably met

PRINCIPLE 4: Challenge Deviations
  - Any deviation must have documented justification in progress/IMPL-STATE
  - Undocumented deviations are violations (BLOCKING)
  - Even documented deviations may be flagged if unjustified

PRINCIPLE 5: Trust Nothing
  - "Tests pass" means nothing without seeing test quality
  - "File exists" means nothing without content verification
  - "Phase complete" means nothing without evidence review
  - Verify claims against actual artifacts

PRINCIPLE 6: Trace Everything
  - Every finding must reference source evidence
  - Every pass must cite verification method
  - Every recommendation must link to specific issue

PRINCIPLE 7: AC Runtime Trace
  - For each TAC-NN listed in RESEARCH-SPEC:
    1. Identify the user-facing entry point named in research
       (e.g., Composable, Activity, Fragment, View component, CLI command,
       HTTP endpoint handler).
    2. Grep the entry point file for the AC's required call.
       Example patterns to look for (extend per ecosystem):
       - Method call:  <ManagerName>.<method>(
       - Event emit:   emit(<eventName>
       - Decorator:    @Subscribe / @EventHandler
       - HTTP route:   @GetMapping("<path>") / app.get("<path>")
    3. If the call is NOT found in the entry point or in a component
       transitively reachable from it, emit:
         { type: "FAIL",
           severity: "BLOCKING",
           category: "AC_NOT_WIRED_TO_UI",
           description: "TAC-NN required call not found in entry point",
           location: "<entry_point_file>" }
  - This principle complements PRINCIPLE 3 (Completeness): symbol presence
    in a service layer does not satisfy an AC unless a caller exists in the
    user-facing entry point.
```
