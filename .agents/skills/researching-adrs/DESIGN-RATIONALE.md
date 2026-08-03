<!-- DRAFT — Pending human validation -->
# Design Rationale: researching-adrs Refactoring

## 1. Architecture Decision: Manifest + Per-ADR Files

**Rationale:** ADR collections grow linearly with architectural complexity. Each ADR (tech stack, authentication, data storage, etc.) is a substantial self-contained document (~500–1,000 lines). A single file would exceed comfort at 12+ ADRs. The manifest absorbs coordination files while per-ADR files remain unchanged.

**Before (v2.1.0):** 6 coordination files + per-ADR files (~12,000–16,000 lines)
**After (v3.0.0):** ADR-SPEC manifest + per-ADR files + ADR-AUDIT (~6,000–9,000 lines)

Multi-file overhead eliminated:
- No 00-index file management
- No tech-stack-evaluation as separate file (absorbed into manifest)
- No adr-summary as separate file (absorbed into manifest)
- No adr-validation as separate file (absorbed into manifest)
- Agent reads manifest for overview + relevant ADR files only
- Chunking support preserved (`chunk_size`, `resume_from_adr`)

---

## 2. Structural Changes

### Before (v2.1.0 — Multi-File Architecture)
```
{adrs_path}/
├── 00-adr-index.md                ← Progress tracker
├── tech-stack-evaluation.md       ← Technology evaluation matrix
├── adr-summary.md                 ← Cross-ADR summary and traceability
├── adr-validation.md              ← Consistency validation results
├── enhancement-protocol.md        ← Enhancement suggestions (optional)
├── governance.md                  ← Process log + assumptions
└── adrs/
    └── adr-NNN-{slug}.md          ← Per-ADR detail files
```
**Files:** 6+ | **Estimated lines:** 12,000–16,000 | **Carry-forward state:** ADR_INDEX object

### After (v3.0.0 — Manifest + Per-ADR Files)
```
{adrs_path}/
├── ADR-SPEC-{SESSION_ID}.md      ← Manifest (tech stack, catalog, traceability, validation)
├── ADR-AUDIT-{SESSION_ID}.md     ← Session audit trail
└── adrs/
    └── adr-NNN-{slug}.md         ← Per-ADR detail files (unchanged)
```
**Files:** 3+ | **Estimated lines:** 6,000–9,000 | **Carry-forward state:** none needed

---

## 3. Content Classification

| Section/File | Classification | Verdict | Reason |
|---|---|---|---|
| 00-adr-index.md (progress tracker) | STRUCTURAL | REMOVED | Manifest needs no progress tracker |
| tech-stack-evaluation.md | AGENT_ESSENTIAL | KEPT in manifest | Core evaluation matrix; downstream contract |
| adr-summary.md (cross-ADR summary) | AGENT_ESSENTIAL | KEPT in manifest | ADR catalog with traceability |
| adr-validation.md (consistency) | VALIDATION | KEPT in manifest as `validation_summary` | Generation-time gate results |
| enhancement-protocol.md | GOVERNANCE | REMOVED | Was optional; governance → humanize-spec |
| governance.md | STRUCTURAL | SPLIT | Assumptions → `open_questions`; metadata → AUDIT |
| Per-ADR files (adr-NNN-*.md) | AGENT_ESSENTIAL | KEPT (unchanged) | Self-contained decision records |

---

## 4. Downstream Contract

### Primary Consumers
| Consumer Skill | What It Reads | Fields Consumed |
|---|---|---|
| `establishing-architecture-foundation` | ADR-SPEC + per-ADR files | `tech_stack_evaluation`, `adr_catalog`, per-ADR decisions and constraints |
| `specifying-architecture` | ADR-SPEC + per-ADR files | `adr_catalog` (for traceability), per-ADR technology choices |
| `humanize-spec` | ADR-SPEC | All sections (via `researching-adrs` profile) |

### Contract Guarantees
The manifest MUST provide:
1. Tech stack evaluation matrix with scoring per category
2. ADR catalog with IDs, titles, status, and category classification
3. Cross-ADR traceability (which ADRs affect which bounded contexts/services)
4. Validation summary (consistency checks, coverage percentages)
5. All assumptions in `open_questions`

---

## 5. Scaling Analysis

| Scale | ADRs | Est. Manifest Lines | Est. Per-ADR Lines | Verdict |
|---|---|---|---|---|
| Small (5 ADRs) | 5 | ~300 | ~3,500 | Manifest comfortable |
| Medium (12 ADRs) | 12 | ~500 | ~8,000 | Manifest comfortable |
| Large (20 ADRs) | 20 | ~700 | ~14,000 | Manifest comfortable |
| Enterprise (30+ ADRs) | 30+ | ~1,000 | ~21,000+ | Manifest viable; chunking essential |

**Decision:** Manifest + per-ADR files. The manifest is a lightweight catalog/index (~40 lines per ADR entry). Chunking support (`chunk_size`, `resume_from_adr`) handles enterprise scale by generating ADR batches across multiple sessions.

---

## 6. open_questions Consolidation

### Before (v2.1.0)
Gaps scattered across: adr-validation.md (consistency gaps), governance.md (assumptions, enhancement suggestions), inline `[Assumption]` markers in per-ADR files.

### After (v3.0.0)
Single `open_questions` section in ADR-SPEC:
- `pending_inputs` — missing upstream data (domain boundaries gaps, PRD gaps)
- `coverage_gaps` — decision categories without ADRs
- `assumptions_to_validate` — all `[Assumption]` entries with ASM-XX IDs
- `upstream_gaps_carried_forward` — boundary/PRD open questions affecting decisions
- `summary` — counts + overall status

---

## 7. Impact Summary

| Metric | Original (v2.1.0) | Refactored (v3.0.0) | Change |
|---|---|---|---|
| Output files (excl. per-ADR) | 6 (index + 5 coordination files) | 2 (manifest + audit) | -67% |
| Per-ADR files | Unchanged | Unchanged | No change |
| Carry-forward state | ADR_INDEX object | None | Eliminated |
| Prose content | Moderate (summaries, enhancement protocol) | Zero | -100% |
| Human-readable content | Inline (mixed with data) | On-demand via humanize-spec | Separated |
| Governance content | Inline (governance.md) | Audit file + rendering profile | Separated |
| include_enhancement_protocol | Optional parameter | Removed | Governance → humanize-spec |
| Gap tracking | Scattered (validation + governance + inline) | Single open_questions registry | Consolidated |
| Estimated output tokens | ~20K–28K (with prose) | ~10K–15K (structured only) | ~50% reduction |
| Context overhead for downstream | Load 6+ files, parse each | Load manifest + relevant ADR files | -70% |
