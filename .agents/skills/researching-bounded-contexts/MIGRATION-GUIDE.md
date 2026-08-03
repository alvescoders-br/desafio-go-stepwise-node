<!-- DRAFT — Pending human validation -->
# Migration Guide: researching-bounded-contexts v2.0.1 → v3.0.0

## 1. Field Mapping

### File-Level Changes
| Original File (v2.0.1) | New Location (v3.0.0) | Notes |
|---|---|---|
| `00-index.md` | Eliminated | No batching needed; manifest has no progress tracker |
| `01-summary.md` | `scope_summary` in BOUNDARIES-SPEC | Prose removed; counts preserved |
| `02-catalog-index.md` | `context_catalog` in BOUNDARIES-SPEC | Structure preserved |
| `03-context-map.md` | `context_map` in BOUNDARIES-SPEC | Relationship data preserved |
| `04-domain-models.md` | Absorbed into per-context files | Models belong with their context |
| `05-event-storming.md` | Absorbed into per-context files | Events belong with their context |
| `06-services.md` | `service_decomposition` in BOUNDARIES-SPEC | Structure preserved |
| `07-integration.md` | `integration_patterns` in BOUNDARIES-SPEC | Structure preserved |
| `08-nfrs.md` | `nfr_allocation` in BOUNDARIES-SPEC | Structure preserved |
| `09-rationale.md` | `decision_rationale` in BOUNDARIES-SPEC | Structure preserved |
| `10-roadmap.md` | `implementation_roadmap` in BOUNDARIES-SPEC | Structure preserved |
| `11-validation.md` | `validation_summary` in BOUNDARIES-SPEC | Results only; checks run during generation |
| `12-audit.md` | `validation_summary` in BOUNDARIES-SPEC | Merged with validation results |
| `13-governance.md` | BOUNDARIES-AUDIT + `open_questions` | Split: metadata to audit, assumptions to open_questions |
| `contexts/bc-NN-*.md` | `contexts/bc-NN-*.md` (unchanged path) | Enriched with domain models + events from SEC-04/05 |

### Per-Context File Enrichment
| Original Source | New Location in bc-NN-*.md | Notes |
|---|---|---|
| SEC-04 domain models (per-context entries) | `domain_model` section | Aggregates, entities, value objects |
| SEC-05 event storming (per-context entries) | `events` section | Domain events, commands, policies |

---

## 2. Breaking Changes

### File Paths Changed
| What | Before | After |
|---|---|---|
| Output structure | Folder with 14+ files | Folder with 2 files + contexts/ |
| Primary artifact | `{folder}/02-catalog-index.md` etc. | `BOUNDARIES-SPEC-{SESSION_ID}.md` |
| Audit trail | `{folder}/13-governance.md` | `BOUNDARIES-AUDIT-{SESSION_ID}.md` |
| Progress tracker | `{folder}/00-index.md` | Eliminated |
| Domain models | `{folder}/04-domain-models.md` (global) | Per-context files (`contexts/bc-NN-*.md`) |
| Event storming | `{folder}/05-event-storming.md` (global) | Per-context files (`contexts/bc-NN-*.md`) |

### Format Changes
| What | Before | After |
|---|---|---|
| Section file names | `NN-section-name.md` | Sections within BOUNDARIES-SPEC |
| Prose content | Mixed with structured data | Zero prose in spec; humanize-spec generates prose |
| Gap tracking | Scattered across SEC-11, SEC-12, SEC-13 | Single `open_questions` section |
| Domain models | Centralized in SEC-04 | Distributed to per-context files |
| Event storming | Centralized in SEC-05 | Distributed to per-context files |

### Parameter Changes
No parameter changes. All v2.0.1 parameters remain valid:
- `domain_boundaries_path` — output folder (unchanged semantics)
- `include_enhancement_protocol` — not applicable (skill never had this parameter)

---

## 3. Backward Compatibility

### For downstream consumers reading old multi-file format:
Use `humanize-spec` with the `researching-bounded-contexts` rendering profile to generate a human-readable document that contains all the same information as the v2.0.1 multi-file output.

### For downstream agents (researching-adrs, establishing-architecture-foundation):
These agents consume structured data. The v3.0.0 manifest contains the same structured data in a more accessible format:
- `context_catalog` → same as old "02-catalog-index.md" data
- `context_map` → same as old "03-context-map.md" data
- `service_decomposition` → same as old "06-services.md" data
- `integration_patterns` → same as old "07-integration.md" data

Update agent prompts to read from BOUNDARIES-SPEC-*.md instead of individual section files. Per-context files remain at the same path (`contexts/bc-NN-*.md`) and are now enriched with domain model and event data previously in SEC-04/SEC-05.

---

## 4. Rollout Plan

### Phase 1: Deploy Alongside (Week 1)
a. Place new skill file alongside existing `SKILL.md`
b. Configure capability to use the new skill file
c. Run both versions on the same inputs, compare outputs
d. Verify: all contexts, relationships, service mappings, and NFR allocations present

### Phase 2: Update Downstream (Week 2)
a. Update `researching-adrs` to read from BOUNDARIES-SPEC-*.md
b. Update `establishing-architecture-foundation` to read from BOUNDARIES-SPEC-*.md + enriched per-context files
c. Verify downstream outputs are equivalent

### Phase 3: Register Rendering Profile (Week 2)
a. Copy rendering profile to `humanize-spec/references/profiles/`
b. Verify humanize-spec can render the new spec format
c. Compare rendered output against v2.0.1 multi-file output

### Phase 4: Cutover (Week 3)
a. Replace original `SKILL.md` with agent-native version
b. Archive original section template reference files
c. Remove archived files after validation period

## Verification Checklist

- [ ] Downstream skills updated to read BOUNDARIES-SPEC-*.md instead of individual section files
- [ ] Per-context files verified to include domain model and event sections
- [ ] Capability YAMLs updated if they reference specific section file paths
- [ ] Stakeholder review workflows updated to invoke humanize-spec before review
- [ ] REPAIR mode tested with new manifest + per-context format
- [ ] Rendering profile tested with humanize-spec
