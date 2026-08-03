<!-- DRAFT — Pending human validation -->
# Migration Guide: researching-adrs v2.1.0 → v3.0.0

## 1. Field Mapping

### File-Level Changes
| Original File (v2.1.0) | New Location (v3.0.0) | Notes |
|---|---|---|
| `00-adr-index.md` | Eliminated | Manifest needs no progress tracker |
| `tech-stack-evaluation.md` | `tech_stack_matrix` in ADR-SPEC | Evaluation matrix preserved as structured data |
| `adr-summary.md` | `adr_catalog` in ADR-SPEC | Cross-ADR summary with traceability |
| `adr-validation.md` | `validations` in ADR-SPEC | Consistency checks as generation-time gate |
| `enhancement-protocol.md` | Eliminated | Was optional; governance content → humanize-spec |
| `governance.md` | ADR-AUDIT + `open_questions` | Split: metadata → audit, assumptions → open_questions |
| `adrs/adr-NNN-{slug}.md` | `adrs/adr-NNN-{slug}.md` (unchanged) | Per-ADR files unchanged |

### Section-Level Field Mapping

#### Tech Stack Evaluation → tech_stack_matrix
| Original Field | New Field | Format Change |
|---|---|---|
| Category evaluation tables | `category: {name}` entries | Structured: options, recommended, score, rationale |
| Scoring criteria | `evaluation_criteria` | Same table format |
| Selected stack summary | `selected_stack_summary` | Same table format |
| ADR cross-references | `adr_ref` per category | Inline field instead of separate narrative |

#### ADR Summary → adr_catalog
| Original Field | New Field | Format Change |
|---|---|---|
| ADR listing table | `adr_catalog` table | Same structure; IDs, titles, status, category |
| Cross-ADR traceability | `traceability_matrix` | Context/service impact per ADR |
| Decision timeline | Eliminated | Derivable from per-ADR files |

#### ADR Validation → validations
| Original Field | New Field | Format Change |
|---|---|---|
| Consistency check results | `consistency_checks` | Same structure; results only |
| Coverage analysis | `coverage_summary` | Percentage per decision category |
| Conflict detection | `conflict_checks` | Same structure |

#### Governance → ADR-AUDIT + open_questions
| Original Field | New Field | Format Change |
|---|---|---|
| Session Information | AUDIT file header | Same metadata |
| Sources Referenced | AUDIT file `sources` | Same list |
| Process Log | AUDIT file `decisions_made` | Same table |
| Change Log | AUDIT file `directives_applied` | REPAIR only |
| Engineering Assumptions | `open_questions.assumptions_to_validate` | Consolidated with all gaps |
| Enhancement Suggestions | Eliminated | Derived by humanize-spec from open_questions |

---

## 2. Breaking Changes

### Parameter Changes
| Parameter | Before | After |
|---|---|---|
| `include_enhancement_protocol` | Optional boolean | **REMOVED** (governance content → humanize-spec) |
| `adrs_path` | Required | Unchanged |
| `chunk_size` | Optional | Unchanged (chunking preserved) |
| `resume_from_adr` | Optional | Unchanged (chunking preserved) |

### File Paths Changed
| What | Before | After |
|---|---|---|
| Output structure | Folder with 6+ files + adrs/ | Folder with 2 files + adrs/ |
| Primary artifact | `tech-stack-evaluation.md`, `adr-summary.md` etc. | `ADR-SPEC-{SESSION_ID}.md` |
| Audit trail | `governance.md` | `ADR-AUDIT-{SESSION_ID}.md` |
| Progress tracker | `00-adr-index.md` | Eliminated |
| Enhancement protocol | `enhancement-protocol.md` | Eliminated |

### Format Changes
| What | Before | After |
|---|---|---|
| Prose content | Mixed with structured data | Zero prose in spec; humanize-spec generates prose |
| Gap tracking | Scattered across validation + governance + inline | Single `open_questions` section |
| Status on items | Implicit | Explicit `status` field on every item |

---

## 3. Downstream Consumer Updates

### establishing-architecture-foundation
**Before:** Reads `tech-stack-evaluation.md`, `adr-summary.md`, and individual `adrs/adr-NNN-*.md` files.
**After:** Reads `ADR-SPEC-*.md` for `tech_stack_matrix`, `adr_catalog`. Per-ADR files unchanged.

**Path resolution:**
```
# Before
tech_stack = {adrs_path}/tech-stack-evaluation.md
adr_list = {adrs_path}/adr-summary.md

# After
spec_file = find ADR-SPEC-*.md in {adrs_path}
tech_stack = parse section "tech_stack_matrix" from spec_file
adr_list = parse section "adr_catalog" from spec_file
```

### specifying-architecture
**Before:** Reads `adr-summary.md` for traceability and per-ADR files for technology choices.
**After:** Reads `ADR-SPEC-*.md` for `adr_catalog` and `traceability_matrix`. Per-ADR files unchanged.

---

## 4. Backward Compatibility

For downstream agents consuming structured data, the v3.0.0 manifest contains the same data in a more accessible format. Per-ADR files (`adrs/adr-NNN-*.md`) remain at the same path and are unchanged. Update agent prompts to read from `ADR-SPEC-*.md` instead of individual coordination files.

For human-readable output, use `humanize-spec` with the `researching-adrs` rendering profile.

---

## 5. Rollout Plan

### Phase 1: Deploy Alongside (Week 1)
a. Place new skill file alongside existing `SKILL.md`
b. Run both versions on the same inputs, compare outputs
c. Verify: all ADRs, tech stack evaluations, and validation results present

### Phase 2: Update Downstream (Week 2)
a. Update `establishing-architecture-foundation` to read from ADR-SPEC-*.md
b. Update `specifying-architecture` to read from ADR-SPEC-*.md
c. Verify downstream outputs are equivalent

### Phase 3: Cutover (Week 3)
a. Replace original `SKILL.md` with agent-native version
b. Remove `include_enhancement_protocol` parameter from capability YAMLs
c. Archive original coordination file templates

## Verification Checklist

- [ ] Downstream skills updated to read ADR-SPEC-*.md instead of individual coordination files
- [ ] Per-ADR files verified unchanged at `adrs/adr-NNN-*.md`
- [ ] `include_enhancement_protocol` parameter removed from capability YAMLs
- [ ] REPAIR mode tested with new manifest + per-ADR format
- [ ] Chunking (`chunk_size`, `resume_from_adr`) verified functional
- [ ] Rendering profile tested with humanize-spec
