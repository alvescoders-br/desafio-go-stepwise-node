# Output Templates

Use these templates when reporting compliance results.

---

## Template 1a: Return to Product (Adjustable)

Use when gaps exist but can be resolved by adjusting the requirement — not the architecture.

```markdown
## [ID — Title]

**Compliance Status: 🔄 Return to Product — Requirement adjustment needed**

| # | What doesn't comply | Where in the ASD |
|---|---------------------|------------------|
| 1 | [Specific description of the violation] | [ASD section, e.g., "Software Architecture > Technology Stack"] |
| 2 | [Specific description of the violation] | [ASD section] |

> ⚠️ **This requirement cannot proceed to implementation as written.**
> The gaps above can be resolved by refining the requirement to fit within existing ASD constraints.
> Return to Product for adjustment before continuing.
```

---

## Template 1b: Initiate ADR (Architecture Change Required)

Use when gaps cannot be resolved by adjusting the requirement — the ASD itself needs to change.

```markdown
## [ID — Title]

**Compliance Status: 📋 Initiate ADR — Architecture change required**

| # | What doesn't comply | Where in the ASD |
|---|---------------------|------------------|
| 1 | [Specific description of the violation] | [ASD section] |
| 2 | [Specific description of the violation] | [ASD section] |

> ⚠️ **This requirement cannot proceed to implementation.**
> The gaps above require a formal change to the Architecture Specification Document.
> Initiate the ADR process before this requirement can be approved.
```

---

## Template 2: Approved (Compliant)

Use when a requirement fully aligns with the ASD.

```markdown
## [ID — Title]

**Compliance Status: ✅ Approved — Compliant with ASD**

- [Brief compliance point, e.g., "Fits within the OrderManagement PBC — Software Architecture > PBC Diagram"]
- [Brief compliance point, e.g., "Uses Kafka event-driven pattern — Architecture Patterns"]
- [Brief compliance point, e.g., "Meets <200ms SLO — NFR > Performance and Scalability"]
```

---

## Template 3: Overall Summary (multiple requirements)

Append this at the end when more than one requirement was assessed.

```markdown
## Summary

| ID | Title | Decision |
|----|-------|----------|
| [US-101] | [Title] | 📋 Initiate ADR |
| [US-102] | [Title] | 🔄 Return to Product |
| [US-103] | [Title] | ✅ Approved |

**Total reviewed:** [n] | **Approved:** [n] | **Return to Product:** [n] | **Initiate ADR:** [n]
```
