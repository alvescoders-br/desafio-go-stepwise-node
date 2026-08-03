# Phase A — Tech Stack Evaluation

## Context Contract

- **Inputs:** ADR_CONTEXT (bounded_contexts, prd_nfr_ids, nfrs_by_context, integration_patterns); context packs (if provided)
- **Outputs:** ADR_INDEX.technology_eval populated; evaluation data stored for manifest inclusion in Phase C
- **Carries Forward:** ADR_INDEX.technology_eval with `layer → { category, options, recommended, adr_ref, scoring }`
- **Flush After:** Full evaluation text — only ADR_INDEX.technology_eval survives
- **Dependency:** Step 2 must be COMPLETE (ADR_CONTEXT populated, ADR_DECISIONS defined)
- **H1 Title:** `# {project_name} — Tech Stack Evaluation`

## Mode-Specific Behavior

- **BUILD:** Generate full evaluation from ADR_CONTEXT and context packs.
- **REPAIR:** If REPAIR_DIRECTIVE targets "tech-stack" or "global": regenerate. Otherwise: SKIP — preserve existing technology_eval.
- **RESUME:** SKIP entirely. technology_eval already loaded from _checkpoint.json.

---

## Evaluation Matrix Generation

Build evaluation across architectural layers identified from ADR_CONTEXT.
Not all layers apply to every project — include only layers relevant to the bounded contexts
and NFRs. Each layer maps to one or more ADRs that will make the final technology selection.

### Layer Template

| Layer | Category | Option A | Option B | Option C | Recommended | ADR Ref |
|-------|----------|----------|----------|----------|-------------|---------|
| Presentation | Frontend Framework | ... | ... | ... | ... | ADR-001 |
| Application | Runtime/Framework | ... | ... | ... | ... | ADR-001 |
| Data | Primary Store | ... | ... | ... | ... | ADR-005 |
| Data | Caching | ... | ... | ... | ... | ADR-005 |
| Messaging | Event Bus | ... | ... | ... | ... | ADR-004 |
| Infrastructure | Container/Orchestration | ... | ... | ... | ... | ADR-010 |
| Security | Auth Provider | ... | ... | ... | ... | ADR-007 |
| Observability | Monitoring Stack | ... | ... | ... | ... | ADR-009 |

Derive layers from bounded contexts and NFRs in ADR_CONTEXT. A project with no messaging
requirement has no Messaging layer. A client-only project may have only Presentation +
Application + Data layers.

### Scoring Criteria

Apply to each option in the matrix:

| Criterion | Scale | Description |
|-----------|-------|-------------|
| Performance | 1-5 | Benchmarks, latency, throughput relative to NFR targets |
| Scalability | 1-5 | Horizontal/vertical scaling capability for projected load |
| Team Expertise | 1-5 | Current team proficiency (from context pack or [Assumption]) |
| Cost/TCO | 1-5 | Licensing, infrastructure, operational costs over 3 years |
| Community/Ecosystem | 1-5 | Maturity, support, plugins, hiring pool |
| Licensing/Lock-in | 1-5 | Vendor independence, exit cost, open-source status |

Score each option per criterion. Recommended option = highest weighted total.
If scoring is close (within 10%), note as engineering_assumption and flag for
stakeholder validation.

### TCO Analysis

One row per recommended technology:

| Component | Year 1 (Setup + Licensing) | Years 2-3 (Ops + Maintenance) | Training | Total 3Y |
|-----------|---------------------------|-------------------------------|----------|----------|

Source: context packs (if provided) or industry benchmarks.
Mark estimates from industry benchmarks as `[Assumption]` — these propagate to
engineering_assumptions in the manifest.

### Governance Constraints

IF context packs provided governance/compliance rules:

| Constraint | Source | Impact on Recommendation |
|-----------|--------|--------------------------|
| {rule} | {context-pack file} | {how it narrowed or determined the choice} |

ELSE:

```
status: "No organizational constraints provided. Recommendations based on technical merit."
```

---

## Source Fidelity Check (before storing in ADR_INDEX)

- [ ] Options evaluated relate to capabilities identified in ADR_CONTEXT (no phantom requirements)
- [ ] Every layer traces to a bounded context or NFR
- [ ] TCO assumptions marked [Assumption] when not from context packs
- [ ] ADR Ref column references valid ADR-NNN from ADR_DECISIONS
- [ ] No technology bias: recommended option justified by scoring, not preference
- [ ] Scoring totals verified: stated recommendation matches highest score

## Post-Section Protocol

1. **Store** technology_eval in ADR_INDEX: `{ layer → { category, options: [...], recommended, adr_ref, scoring: { criterion → score } } }`
2. **Write** _checkpoint.json with current ADR_INDEX state.
3. **Update** ADR_INDEX.phase_status.A = "COMPLETE"
4. **Update** 00-index.md: add "Phase A: ✅ Tech Stack Evaluation complete" entry.
5. **Flush** evaluation text from memory. Only ADR_INDEX.technology_eval survives.
6. **Log:** "Phase A complete. {N} layers evaluated. {M} governance constraints applied."
