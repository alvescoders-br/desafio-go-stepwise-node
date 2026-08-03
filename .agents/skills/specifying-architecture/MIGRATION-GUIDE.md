<!-- DRAFT — Pending human validation -->
# Migration Guide: specifying-architecture v2.1.0 → v3.0.0

## 1. Field Mapping

### File-Level Changes
| Original File (v2.1.0) | New Location (v3.0.0) | Notes |
|---|---|---|
| `00-specs-index.md` | ARCH-SPECS-MANIFEST | Manifest replaces index; structured catalog |
| `_progress.json` | Eliminated | Manifest `unit_catalog` tracks completion |
| `_spec_index.json` | Eliminated | Manifest `cross_references` replaces |
| `unit-12-communication.md` | `units/unit-12-communication.md` | Moved to subfolder; content unchanged |
| `unit-13-data.md` | `units/unit-13-data.md` | Moved to subfolder; content unchanged |
| `unit-14-security.md` | `units/unit-14-security.md` | Moved to subfolder; content unchanged |
| `unit-15-observability.md` | `units/unit-15-observability.md` | Moved to subfolder; content unchanged |
| `unit-16-infrastructure.md` | `units/unit-16-infrastructure.md` | Moved to subfolder; content unchanged |
| `unit-17-characteristics.md` | `units/unit-17-characteristics.md` | Moved to subfolder; content unchanged |
| `unit-18-migration.md` | `units/unit-18-migration.md` | Moved to subfolder; content unchanged |
| `unit-19-tech-stack.md` | `units/unit-19-tech-stack.md` | Absorbs old unit-21 fidelity checks |
| `unit-20-risks.md` | `units/unit-20-risks.md` | Content unchanged; RSK-XX + ARCH-RSK-XX |
| `unit-21-validation.md` | Merged into `units/unit-19-tech-stack.md` | Fidelity checks consolidated with tech stack |
| `unit-22-governance.md` | ARCH-SPECS-AUDIT + manifest `open_questions` | Split: metadata → audit, assumptions → open_questions |

### New Files
| File | Purpose |
|---|---|
| `ARCH-SPECS-MANIFEST-{SESSION_ID}.md` | Unit catalog, cross-references, tech fidelity summary, validations, open questions |
| `ARCH-SPECS-AUDIT-{SESSION_ID}.md` | Session audit trail (sources, timing, metadata) |
| `units/unit-21-traceability.md` | New: consolidated traceability and validation results |

---

## 2. Breaking Changes

### File Paths Changed
| What | Before | After |
|---|---|---|
| Unit file location | `{folder}/unit-NN-*.md` (flat) | `{folder}/units/unit-NN-*.md` (subfolder) |
| Primary artifact | `{folder}/00-specs-index.md` | `ARCH-SPECS-MANIFEST-{SESSION_ID}.md` |
| Progress tracking | `{folder}/_progress.json` | Eliminated (manifest) |
| Spec index | `{folder}/_spec_index.json` | Eliminated (manifest `cross_references`) |
| Audit trail | `{folder}/unit-22-governance.md` | `ARCH-SPECS-AUDIT-{SESSION_ID}.md` |

### Parameter Changes
| Parameter | Before | After |
|---|---|---|
| `output_folder` | Explicit parameter for output path | REMOVED — derived from `target_architecture_path` |
| `include_enhancement_protocol` | Optional boolean | REMOVED — governance rendered via humanize-spec |

### UNIT Merges
| Before | After | Rationale |
|---|---|---|
| unit-21-validation.md | Merged into unit-19-tech-stack.md | Tech fidelity checks belong with tech stack |
| unit-22-governance.md | Split: AUDIT + manifest open_questions | Governance is structural, not spec content |

### Format Changes
| What | Before | After |
|---|---|---|
| State tracking | JSON files (_progress.json, _spec_index.json) | Manifest sections (unit_catalog, cross_references) |
| Prose content | Mixed with structured data in index | Zero prose; humanize-spec generates prose |
| Gap tracking | Scattered across unit-21, unit-22, inline markers | Single `open_questions` section in manifest |

---

## 3. Backward Compatibility

### For downstream consumers reading old flat-file format:
Use `humanize-spec` with the `arch-specs` rendering profile to generate human-readable output from the new manifest + units/ structure.

### For downstream agents (creating-qe-master-plan, defining-qe-strategy):
Update agent prompts to read from `ARCH-SPECS-MANIFEST-*.md` + `units/` subfolder:
- `unit_catalog` → replaces old `00-specs-index.md` + `_spec_index.json`
- `cross_references` → replaces old `_spec_index.json` linkages
- `tech_fidelity_summary` → replaces old `unit-21-validation.md` checks
- Unit files at `units/unit-NN-*.md` → same content, new path

---

## 4. Rollout Plan

### Phase 1: Deploy Alongside (Week 1)
a. Place new skill file alongside existing `SKILL.md`
b. Run both versions on the same inputs, compare outputs
c. Verify: all unit content preserved, cross-references intact, tech fidelity checks pass
d. Validate unit-19 correctly includes merged validation data

### Phase 2: Validate Rendering (Week 1-2)
a. Update `arch-specs` rendering profile in humanize-spec for new unit numbering
b. Verify humanize-spec renders the manifest + units/ format correctly
c. Compare rendered output against v2.1.0 flat-file output

### Phase 3: Update Downstream (Week 2)
a. Update `creating-qe-master-plan` to read from ARCH-SPECS-MANIFEST + units/
b. Update `defining-qe-strategy` to read from ARCH-SPECS-MANIFEST + units/
c. Verify downstream outputs are equivalent

### Phase 4: Cutover (Week 3)
a. Replace original `SKILL.md` with agent-native version
b. Remove `output_folder` and `include_enhancement_protocol` from capability YAMLs
c. Archive original template reference files
d. Remove archived files after validation period

## Verification Checklist

- [ ] Downstream skills updated to read ARCH-SPECS-MANIFEST + units/ subfolder
- [ ] Unit files verified at new `units/` path
- [ ] unit-19 includes merged tech fidelity validation data
- [ ] unit-21-traceability.md verified as new consolidated traceability file
- [ ] Capability YAMLs updated: `output_folder` and `include_enhancement_protocol` removed
- [ ] `_progress.json` and `_spec_index.json` no longer generated
- [ ] Stakeholder review workflows updated to invoke humanize-spec before review
- [ ] REPAIR mode tested with new manifest + units/ format
- [ ] Rendering profile tested with humanize-spec
