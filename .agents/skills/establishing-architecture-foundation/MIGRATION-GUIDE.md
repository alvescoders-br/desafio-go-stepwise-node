<!-- DRAFT — Pending human validation -->
# Migration Guide: establishing-architecture-foundation v2.0.1 → v3.0.0

## 1. Field Mapping

### File-Level Changes
| Original File (v2.0.1) | New Location (v3.0.0) | Notes |
|---|---|---|
| `UNIT-00-index.md` | Eliminated | Manifest needs no progress tracker |
| `UNIT-01-executive-summary.md` | `scope_summary` in ARCH-FOUNDATION-SPEC | Prose removed; counts preserved |
| `UNIT-02-principles.md` | `architecture_principles` in ARCH-FOUNDATION-SPEC | Structure preserved with ADR traceability |
| `UNIT-03-service-catalog.md` | `service_catalog` in ARCH-FOUNDATION-SPEC | Structure preserved with context mapping |
| `UNIT-04-c4-context.md` | `c4_diagrams.context` in ARCH-FOUNDATION-SPEC | PlantUML inline code block |
| `UNIT-05-c4-container.md` | `c4_diagrams.container` in ARCH-FOUNDATION-SPEC | PlantUML inline code block |
| `UNIT-06-c4-component.md` | `c4_diagrams.components` in ARCH-FOUNDATION-SPEC | PlantUML inline code blocks (one per service) |
| `UNIT-07-integration.md` | `integration_patterns` in ARCH-FOUNDATION-SPEC | Structure preserved |
| `UNIT-08-nfr-allocation.md` | `nfr_allocation` in ARCH-FOUNDATION-SPEC | Structure preserved |
| `UNIT-09-deployment.md` | `deployment_topology` in ARCH-FOUNDATION-SPEC | Structure preserved |
| `UNIT-10-traceability.md` | `traceability` in ARCH-FOUNDATION-SPEC | ADR-to-service matrix preserved |
| `UNIT-11-validation.md` | `validation_summary` in ARCH-FOUNDATION-SPEC | Results only; checks run during generation |
| `UNIT-12-governance.md` | ARCH-FOUNDATION-AUDIT + `open_questions` | Split: metadata → audit, assumptions → open_questions |
| `services/svc-NN-*.md` | `services/svc-NN-*.md` (unchanged path) | Per-service files unchanged |

---

## 2. Breaking Changes

### File Paths Changed
| What | Before | After |
|---|---|---|
| Output structure | Folder with 13+ UNIT files | Folder with 2 files + services/ |
| Primary artifact | `{folder}/UNIT-03-service-catalog.md` etc. | `ARCH-FOUNDATION-SPEC-{SESSION_ID}.md` |
| Audit trail | `{folder}/UNIT-12-governance.md` | `ARCH-FOUNDATION-AUDIT-{SESSION_ID}.md` |
| Progress tracker | `{folder}/UNIT-00-index.md` | Eliminated |
| C4 diagrams | Separate UNIT files (04, 05, 06) | Inline code blocks in manifest |

### Parameter Changes
| Parameter | Before | After |
|---|---|---|
| `include_enhancement_protocol` | Optional boolean | REMOVED — governance rendered via humanize-spec |
| `target_architecture_path` | Output folder | Unchanged |

### Format Changes
| What | Before | After |
|---|---|---|
| UNIT file names | `UNIT-NN-section-name.md` | Sections within ARCH-FOUNDATION-SPEC |
| Prose content | Mixed with structured data | Zero prose; humanize-spec generates prose |
| C4 PlantUML | Separate files with rendering metadata | Inline code blocks with structured metadata |
| Gap tracking | Scattered across UNIT-11, UNIT-12, inline markers | Single `open_questions` section |

---

## 3. Backward Compatibility

### For downstream consumers reading old multi-file format:
Use `humanize-spec` with the `arch-foundation` rendering profile to generate human-readable output containing all information from the v2.0.1 multi-file output.

### For downstream agents (specifying-architecture, defining-qe-strategy):
Update agent prompts to read from `ARCH-FOUNDATION-SPEC-*.md` instead of individual UNIT files:
- `architecture_principles` → same as old UNIT-02 data
- `service_catalog` → same as old UNIT-03 data
- `c4_diagrams` → same as old UNIT-04/05/06 data (now inline)
- `integration_patterns` → same as old UNIT-07 data

Per-service files remain at `services/svc-NN-*.md` unchanged.

---

## 4. Rollout Plan

### Phase 1: Deploy Alongside (Week 1)
a. Place new skill file alongside existing `SKILL.md`
b. Run both versions on the same inputs, compare outputs
c. Verify: all principles, services, C4 diagrams, NFR allocations, traceability present
d. Validate C4 PlantUML code blocks render correctly from manifest

### Phase 2: Validate Rendering (Week 1-2)
a. Register `arch-foundation` rendering profile in humanize-spec
b. Verify humanize-spec renders the new manifest format correctly
c. Compare rendered output against v2.0.1 multi-file output

### Phase 3: Update Downstream (Week 2)
a. Update `specifying-architecture` to read from ARCH-FOUNDATION-SPEC-*.md
b. Update `defining-qe-strategy` to read from ARCH-FOUNDATION-SPEC-*.md
c. Verify downstream outputs are equivalent

### Phase 4: Cutover (Week 3)
a. Replace original `SKILL.md` with agent-native version
b. Archive original UNIT template reference files
c. Remove `include_enhancement_protocol` parameter from capability YAMLs
d. Remove archived files after validation period

## Verification Checklist

- [ ] Downstream skills updated to read ARCH-FOUNDATION-SPEC-*.md instead of UNIT files
- [ ] C4 PlantUML diagrams verified as inline code blocks in manifest
- [ ] Per-service files verified unchanged at `services/svc-NN-*.md`
- [ ] Capability YAMLs updated: `include_enhancement_protocol` removed
- [ ] Stakeholder review workflows updated to invoke humanize-spec before review
- [ ] REPAIR mode tested with new manifest format
- [ ] Rendering profile tested with humanize-spec
