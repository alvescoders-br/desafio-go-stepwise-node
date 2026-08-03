<!-- DRAFT — Pending human validation -->
# Design Rationale: researching-bounded-contexts Refactoring

## 1. Architecture Decision: Manifest + Per-Context Files

**Rationale:** Bounded context specs grow linearly with domain complexity. Per-context files (`contexts/bc-NN-{name}.md`) contain substantial structured data (aggregates, entities, events, commands) that would exceed single-file comfort at 10+ contexts. The manifest absorbs all coordination/summary sections while per-context files remain unchanged.

**Before (v2.0.1):** 13 section files + per-context files (~7,000–15,000 lines)
**After (v3.0.0):** BOUNDARIES-SPEC manifest + per-context files + BOUNDARIES-AUDIT (~3,500–7,500 lines)

Multi-file overhead eliminated:
- No 00-index file management
- No Write-Flush-Forget protocol for 13 sections
- No inter-section carry-forward via INDEX object
- No section status tracking across 13 files
- Agent reads manifest + relevant context files only

---

## 2. Structural Changes

### Before (v2.0.1 — Multi-File Architecture)
```
{domain_boundaries_path}/
├── 00-index.md                    ← Progress tracker
├── 01-summary.md                  ← Domain analysis summary
├── 02-catalog-index.md            ← Bounded context catalog
├── 03-context-map.md              ← Context relationships
├── 04-domain-models.md            ← Shared domain model concepts
├── 05-event-storming.md           ← Event storming results
├── 06-services.md                 ← Service decomposition
├── 07-integration.md              ← Integration patterns
├── 08-nfrs.md                     ← NFR allocation per context
├── 09-rationale.md                ← Decision rationale
├── 10-roadmap.md                  ← Implementation roadmap
├── 11-validation.md               ← Consistency validation
├── 12-audit.md                    ← Traceability audit
├── 13-governance.md               ← Process log + assumptions
└── contexts/
    └── bc-NN-{name}.md            ← Per-context detail files
```
**Files:** 14+ | **Estimated lines:** 7,000–15,000 | **Carry-forward state:** INDEX object

### After (v3.0.0 — Manifest + Per-Context Files)
```
{domain_boundaries_path}/
├── BOUNDARIES-SPEC-{SESSION_ID}.md   ← Manifest (catalog, map, services, NFRs, roadmap)
├── BOUNDARIES-AUDIT-{SESSION_ID}.md  ← Session audit trail
└── contexts/
    └── bc-NN-{name}.md               ← Per-context detail files (unchanged)
```
**Files:** 3+ | **Estimated lines:** 3,500–7,500 | **Carry-forward state:** none needed

---

## 3. Content Classification

| Section/File | Classification | Verdict | Reason |
|---|---|---|---|
| 00-index.md (progress tracker) | STRUCTURAL | REMOVED | Single manifest needs no progress tracker |
| 01-summary.md (domain analysis) | HUMAN_ONLY | MOVED TO PROFILE | Prose summary derivable from catalog counts |
| 02-catalog-index.md (BC catalog) | AGENT_ESSENTIAL | KEPT in manifest | Core catalog; downstream contract |
| 03-context-map.md (relationships) | AGENT_ESSENTIAL | KEPT in manifest | Upstream/downstream relationships |
| 04-domain-models.md | AGENT_ESSENTIAL | ABSORBED into per-context files | Model details belong with their context |
| 05-event-storming.md | AGENT_ESSENTIAL | ABSORBED into per-context files | Events belong with their context |
| 06-services.md (decomposition) | AGENT_ESSENTIAL | KEPT in manifest | Service-to-context mapping |
| 07-integration.md (patterns) | AGENT_ESSENTIAL | KEPT in manifest | Integration contracts |
| 08-nfrs.md (NFR allocation) | AGENT_ESSENTIAL | KEPT in manifest | NFR-per-context allocation |
| 09-rationale.md (decisions) | AGENT_ESSENTIAL | KEPT in manifest | Decision records with traceability |
| 10-roadmap.md (implementation) | AGENT_ESSENTIAL | KEPT in manifest | Phase sequencing |
| 11-validation.md (consistency) | VALIDATION | KEPT in manifest | Generation-time gate results |
| 12-audit.md (traceability) | VALIDATION | KEPT in manifest as `validation_summary` | Coverage metrics |
| 13-governance.md | STRUCTURAL | SPLIT | Assumptions → `open_questions`; metadata → AUDIT |
| Per-context files (bc-NN-*.md) | AGENT_ESSENTIAL | KEPT (enriched) | Now include domain models + events |

---

## 4. Downstream Contract

### Primary Consumers
| Consumer Skill | What It Reads | Fields Consumed |
|---|---|---|
| `researching-adrs` | BOUNDARIES-SPEC | `context_catalog`, `context_map`, `service_decomposition`, `integration_patterns` |
| `establishing-architecture-foundation` | BOUNDARIES-SPEC + context files | `context_catalog`, `service_decomposition`, `nfr_allocation`, `integration_patterns`, per-context aggregates |
| `humanize-spec` | BOUNDARIES-SPEC | All sections (via `researching-bounded-contexts` profile) |

### Contract Guarantees
The manifest MUST provide:
1. Every bounded context with ID, name, classification (core/supporting/generic), and responsibility
2. Context map with all upstream/downstream relationships and pattern types
3. Service decomposition with context-to-service mapping
4. Integration patterns per context boundary
5. NFR allocation per context
6. Validation summary (coverage percentages)
7. All assumptions in `open_questions`

---

## 5. Scaling Analysis

| Scale | Contexts | Est. Manifest Lines | Est. Per-Context Lines | Verdict |
|---|---|---|---|---|
| Small (3 contexts) | 3 | ~400 | ~600 | Manifest comfortable |
| Medium (8 contexts) | 8 | ~600 | ~1,600 | Manifest comfortable |
| Large (15 contexts) | 15 | ~900 | ~3,000 | Manifest comfortable |
| Enterprise (30+ contexts) | 30+ | ~1,400 | ~6,000+ | Manifest still viable; per-context files essential |

**Decision:** Manifest + per-context files. The manifest stays under 1,500 lines even at enterprise scale because it contains catalog/summary data (one row per context), not the detailed domain models. Per-context files carry the bulk.

---

## 6. open_questions Consolidation

### Before (v2.0.1)
Gaps scattered across: 11-validation.md (gap entries), 12-audit.md (coverage gaps), 13-governance.md (assumptions, suggestions), inline `[Assumption]` markers in section files.

### After (v3.0.0)
Single `open_questions` section in BOUNDARIES-SPEC:
- `pending_inputs` — missing upstream data (PRD gaps, missing epics)
- `coverage_gaps` — contexts without full model coverage
- `assumptions_to_validate` — all `[Assumption]` entries with ASM-XX IDs
- `upstream_gaps_carried_forward` — PRD/epic open questions affecting boundaries
- `summary` — counts + overall status

---

## 7. Impact Summary

| Metric | Original (v2.0.1) | Refactored (v3.0.0) | Change |
|---|---|---|---|
| Output files (excl. per-context) | 14 (index + 13 sections) | 2 (manifest + audit) | -86% |
| Per-context files | Unchanged | Unchanged (enriched) | Domain models + events absorbed |
| Carry-forward state | INDEX object | None | Eliminated |
| Prose content | Moderate (summary, rationale narratives) | Zero | -100% |
| Human-readable content | Inline (mixed with data) | On-demand via humanize-spec | Separated |
| Governance content | Inline (SEC-13) | Audit file + rendering profile | Separated |
| Reference files | Multiple section templates | 1 template file | Consolidated |
| Gap tracking | Scattered (validation + audit + governance) | Single open_questions registry | Consolidated |
| Estimated output tokens | ~12K–25K (with prose) | ~6K–12K (structured only) | ~50% reduction |
| Context overhead for downstream | Load 14+ files, parse each | Load manifest + relevant context files | -80% |
