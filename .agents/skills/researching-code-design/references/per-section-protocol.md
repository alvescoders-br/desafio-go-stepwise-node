# Per-Section Protocol & custom_message Processing

Read this reference at Step 3 (Generate Spec). It governs the inner loop that runs once per section.

---

## Per-Section Protocol

```
FOR EACH section:
  1. ZERO INVENTION CHECK: verify source data is in context
     IF missing → status: pending + open_questions entry. Do NOT invent.
  2. Generate structured content per template
  3. Enforce all 15 upstream consistency rules (see consistency-rules.md)
  4. SOURCE FIDELITY CHECK: scan for hallucinated IDs, drifted tech names, wrong counts
     IF violations → correct before proceeding. Log corrections.
```

---

## custom_message Processing

```
IF custom_message is not empty:
  Parse for:
  - Section focus directives ("focus on security") → increase depth in named sections
  - Specific concerns ("worried about migration") → add as assumptions_to_validate
  - Constraint overrides → NEVER override upstream consistency rules
  Log: "custom_message applied: {summary of how it influenced generation}"
```
