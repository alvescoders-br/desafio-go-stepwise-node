<!-- DRAFT — Pending human validation -->
# Design Rationale: specifying-architecture Refactoring

## 1. Architecture Decision: Manifest + Per-UNIT Files

**Rationale:** Architecture specification output is too large for a single file. Per-unit files (units/unit-12 through unit-21) contain substantial structured data (communication matrices, data topologies, security zones, migration phases) that would exceed single-file comfort at any non-trivial service count. The manifest coordinates all units while per-unit files carry the detailed specs. UNIT-21 (old validation) and UNIT-22 (old governance) are merged/split rather than carried forward as separate files.

**Before (v2.1.0):** 11 UNITs + index + JSON files (~16,500-27,500 lines)
**After (v3.0.0):** ARCH-SPECS-MANIFEST + units/ subfolder (10 files) + ARCH-SPECS-AUDIT (~10,000-17,000 lines)

Multi-file overhead eliminated:
- No _progress.json / _spec_index.json file management
- No inter-UNIT carry-forward via index coordination
- No UNIT status tracking across separate JSON files
- Manifest serves as single carry-forward artifact
- Old UNIT-21 (validation) merged into unit-19 tech fidelity checks
- Old UNIT-22 (governance) split into AUDIT + manifest open_questions

---

## 2. Structural Changes

### Before (v2.1.0 — Multi-File Architecture)
```
{target_architecture_path}/
├── 00-specs-index.md              ← Section index
├── _progress.json                 ← Progress tracker
├── _spec_index.json               ← Spec cross-reference index
├── unit-12-communication.md       ← Communication architecture
├── unit-13-data.md                ← Data architecture
├── unit-14-security.md            ← Security architecture
├── unit-15-observability.md       ← Observability architecture
├── unit-16-infrastructure.md      ← Infrastructure architecture
├── unit-17-characteristics.md     ← ISO 25010 characteristics
├── unit-18-migration.md           ← Migration roadmap
├── unit-19-tech-stack.md          ← Technology stack evaluation
├── unit-20-risks.md               ← Risk register
├── unit-21-validation.md          ← Consistency validation
└── unit-22-governance.md          ← Process log + assumptions
```
**Files:** 14 | **Estimated lines:** 16,500-27,500 | **Carry-forward state:** _progress.json + _spec_index.json

### After (v3.0.0 — Manifest + Per-UNIT Files)
```
{target_architecture_path}/
├── ARCH-SPECS-MANIFEST-{SESSION_ID}.md   ← Manifest (catalog, cross-refs, fidelity, validations)
├── ARCH-SPECS-AUDIT-{SESSION_ID}.md      ← Session audit trail
└── units/
    ├── unit-12-communication.md           ← Communication architecture
    ├── unit-13-data.md                    ← Data architecture
    ├── unit-14-security.md                ← Security architecture
    ├── unit-15-observability.md           ← Observability architecture
    ├── unit-16-infrastructure.md          ← Infrastructure architecture
    ├── unit-17-characteristics.md         ← ISO 25010 characteristics
    ├── unit-18-migration.md               ← Migration roadmap (Gherkin gates)
    ├── unit-19-tech-stack.md              ← Technology stack + fidelity checks (merged)
    ├── unit-20-risks.md                   ← Risk register (RSK-XX + ARCH-RSK-XX)
    └── unit-21-traceability.md            ← Validation + traceability (new)
```
**Files:** 13 | **Estimated lines:** 10,000-17,000 | **Carry-forward state:** manifest only

---

## 3. Content Classification

| Section/File | Classification | Verdict | Reason |
|---|---|---|---|
| 00-specs-index.md | STRUCTURAL | REMOVED | Manifest replaces index |
| _progress.json | STRUCTURAL | REMOVED | Manifest tracks completion |
| _spec_index.json | STRUCTURAL | REMOVED | Manifest `unit_catalog` replaces |
| unit-12 (communication) | AGENT_ESSENTIAL | KEPT in units/ | Communication specs per service |
| unit-13 (data) | AGENT_ESSENTIAL | KEPT in units/ | Data topology per service |
| unit-14 (security) | AGENT_ESSENTIAL | KEPT in units/ | Security zones, threat model |
| unit-15 (observability) | AGENT_ESSENTIAL | KEPT in units/ | SLI/SLO per service |
| unit-16 (infrastructure) | AGENT_ESSENTIAL | KEPT in units/ | Deployment targets, scaling |
| unit-17 (characteristics) | AGENT_ESSENTIAL | KEPT in units/ | ISO 25010 assessment |
| unit-18 (migration) | AGENT_ESSENTIAL | KEPT in units/ | Migration phases with Gherkin gates |
| unit-19 (tech stack) | AGENT_ESSENTIAL | KEPT in units/ (enriched) | Absorbs old unit-21 fidelity checks |
| unit-20 (risks) | AGENT_ESSENTIAL | KEPT in units/ | RSK-XX + ARCH-RSK-XX entries |
| unit-21 (old validation) | VALIDATION | MERGED into unit-19 | Fidelity checks belong with tech stack |
| unit-22 (old governance) | STRUCTURAL | SPLIT | Assumptions → manifest `open_questions`; metadata → AUDIT |

---

## 4. Downstream Contract

### Primary Consumers
| Consumer Skill | What It Reads | Fields Consumed |
|---|---|---|
| `creating-qe-master-plan` | ARCH-SPECS-MANIFEST + units/ | `unit_catalog`, `tech_fidelity_summary`, unit-14 (security), unit-17 (characteristics) |
| `defining-qe-strategy` | ARCH-SPECS-MANIFEST + units/ | `unit_catalog`, unit-12 (communication), unit-15 (observability), unit-17 (characteristics) |
| `humanize-spec` | ARCH-SPECS-MANIFEST + units/ | All sections (via `arch-specs` profile) |

### Contract Guarantees
The manifest MUST provide:
1. Unit catalog with completion status per unit
2. Cross-references between units (e.g., security ↔ communication)
3. Technology fidelity summary with ADR consistency checks
4. Validation summary (coverage percentages)
5. All assumptions in `open_questions`

---

## 5. Scaling Analysis

| Scale | Services | Est. Manifest Lines | Est. Unit Lines (total) | Verdict |
|---|---|---|---|---|
| Small (3 services) | 3 | ~300 | ~2,500 | Comfortable |
| Medium (8 services) | 8 | ~400 | ~5,500 | Comfortable |
| Large (15 services) | 15 | ~550 | ~10,000 | Comfortable |
| Enterprise (30+ services) | 30+ | ~800 | ~20,000+ | Units essential; manifest stays lean |

**Decision:** Manifest + per-unit files. The manifest contains only catalog/coordination data. Per-unit files carry all specification detail and scale linearly with service count.

---

## 6. Impact Summary

| Metric | Original (v2.1.0) | Refactored (v3.0.0) | Change |
|---|---|---|---|
| Output files | 14 (index + JSON + 11 UNITs) | 13 (manifest + audit + 10 units + traceability) | Reorganized |
| JSON state files | 2 (_progress.json, _spec_index.json) | 0 (manifest serves as state) | Eliminated |
| Carry-forward state | _progress.json + _spec_index.json | Manifest only | Consolidated |
| Prose content | Moderate (index narratives) | Zero | -100% |
| Human-readable content | Inline (mixed with data) | On-demand via humanize-spec | Separated |
| include_enhancement_protocol | Optional parameter | Removed | Governance → humanize-spec |
| output_folder parameter | Explicit parameter | Derived from target_architecture_path | Eliminated |
| UNIT merges | 11 separate UNITs | 10 UNITs (21+22 merged/split) | Reduced redundancy |
| Estimated output tokens | ~28K-47K | ~17K-29K | ~40% reduction |
| Context overhead for downstream | Load 14 files, parse JSON | Load manifest + relevant units | -70% |
