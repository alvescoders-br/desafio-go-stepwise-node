<!-- DRAFT — Pending human validation -->
# Design Rationale: establishing-architecture-foundation Refactoring

## 1. Architecture Decision: Manifest + Per-Service Files

**Rationale:** Architecture foundations contain both compact coordination data (principles, diagrams, traceability) and per-service detail (Gherkin scenarios, tech stacks, NFR targets) that grows linearly with service count. The manifest absorbs all 11 UNIT coordination files while per-service files remain unchanged. C4 PlantUML diagrams stay in the manifest as code blocks.

**Before (v2.0.1):** 13 UNITs + services/ (~13,000-22,000 lines)
**After (v3.0.0):** ARCH-FOUNDATION-SPEC (with C4 PlantUML) + services/ + ARCH-FOUNDATION-AUDIT (~7,000-12,000 lines)

Multi-file overhead eliminated:
- No 00-foundation-index file management
- No Write-Flush-Forget protocol for 13 UNITs
- No inter-UNIT carry-forward via FOUNDATION_INDEX
- No UNIT status tracking across 13 files
- Agent reads manifest + relevant service files only

---

## 2. Structural Changes

### Before (v2.0.1 — Multi-File Architecture)
```
{foundation_folder}/
├── 00-foundation-index.md             <- Progress tracker
├── unit-01-executive-summary.md       <- Executive Summary
├── unit-02-principles.md              <- Architecture Principles
├── services/                          <- Per-service files (chunked catalog)
│   └── svc-NN-{name}.md
├── unit-03-catalog-index.md           <- Service Catalog index
├── unit-04-c1-system-context.md       <- C1 System Context Diagram
├── unit-05-c2-container.md            <- C2 Container Diagram
├── unit-06-c3-component-a.md          <- C3 Component A
├── unit-07-c3-component-b.md          <- C3 Component B
├── unit-08-seq-flow-1.md              <- Sequence Diagram 1
├── unit-09-seq-flow-2.md              <- Sequence Diagram 2
├── unit-10-deployment.md              <- Deployment Diagram
├── unit-11-security-diagram.md        <- Security Architecture Diagram
├── unit-12-traceability.md            <- Traceability Audit
└── unit-13-governance.md              <- Process Log + Enhancements
```
**Files:** 14+ | **Estimated lines:** 13,000-22,000 | **Carry-forward state:** FOUNDATION_INDEX object

### After (v3.0.0 — Manifest + Per-Service Files)
```
{foundation_folder}/
├── ARCH-FOUNDATION-SPEC-{SESSION_ID}.md  <- Manifest (principles, C4 diagrams, traceability)
├── ARCH-FOUNDATION-AUDIT-{SESSION_ID}.md <- Session audit trail
└── services/
    └── svc-NN-{name}.md                  <- Per-service files (unchanged)
```
**Files:** 3+ | **Estimated lines:** 7,000-12,000 | **Carry-forward state:** none needed

---

## 3. Content Classification

| Section/File | Classification | Verdict | Reason |
|---|---|---|---|
| 00-foundation-index.md | STRUCTURAL | REMOVED | Manifest needs no progress tracker |
| unit-01 Executive Summary | HUMAN_ONLY | MOVED TO PROFILE | Prose summary derivable from manifest data |
| unit-02 Principles | AGENT_ESSENTIAL | KEPT in manifest | ADR traceability; downstream contract |
| unit-03 Catalog Index | AGENT_ESSENTIAL | KEPT in manifest | Service-to-context mapping |
| services/svc-NN-*.md | AGENT_ESSENTIAL | KEPT (unchanged) | Per-service Gherkin, tech stack, NFRs |
| unit-04 C1 System Context | AGENT_ESSENTIAL | KEPT in manifest | PlantUML code block |
| unit-05 C2 Container | AGENT_ESSENTIAL | KEPT in manifest | PlantUML code block |
| unit-06 C3 Component A | AGENT_ESSENTIAL | KEPT in manifest | PlantUML code block |
| unit-07 C3 Component B | AGENT_ESSENTIAL | KEPT in manifest | PlantUML code block |
| unit-08 Sequence 1 | AGENT_ESSENTIAL | KEPT in manifest | PlantUML code block |
| unit-09 Sequence 2 | AGENT_ESSENTIAL | KEPT in manifest | PlantUML code block |
| unit-10 Deployment | AGENT_ESSENTIAL | KEPT in manifest | PlantUML code block |
| unit-11 Security Diagram | AGENT_ESSENTIAL | KEPT in manifest | PlantUML code block |
| unit-12 Traceability | VALIDATION | KEPT in manifest as `validation_summary` | Coverage metrics |
| unit-13 Governance | STRUCTURAL | SPLIT | Assumptions → `open_questions`; metadata → AUDIT |

---

## 4. Downstream Contract

### Primary Consumers
| Consumer Skill | What It Reads | Fields Consumed |
|---|---|---|
| `specifying-architecture` | ARCH-FOUNDATION-SPEC + service files | `principles`, `service_catalog`, C4 diagrams, `validation_summary` |
| `humanize-spec` | ARCH-FOUNDATION-SPEC | All sections (via `establishing-architecture-foundation` profile) |

### Contract Guarantees
The manifest MUST provide:
1. Architecture principles with ADR traceability (ADR-NNN references)
2. Service catalog index with context-to-service mapping
3. All 8 C4 PlantUML diagrams as code blocks
4. Validation summary (coverage percentages)
5. All assumptions in `open_questions`

---

## 5. Scaling Analysis

| Scale | Services | Est. Manifest Lines | Est. Per-Service Lines | Verdict |
|---|---|---|---|---|
| Small (3 services) | 3 | ~800 | ~1,500 | Manifest comfortable |
| Medium (8 services) | 8 | ~1,000 | ~4,000 | Manifest comfortable |
| Large (15 services) | 15 | ~1,200 | ~7,500 | Manifest comfortable |
| Enterprise (30+ services) | 30+ | ~1,500 | ~15,000+ | Manifest viable; per-service files essential |

**Decision:** Manifest + per-service files. C4 diagrams are compact PlantUML code blocks (~50-100 lines each, ~600 total). The manifest stays under 1,500 lines because coordination data (principles, catalog index, validation) scales slowly. Per-service files carry the bulk.

---

## 6. Impact Summary

| Metric | Original (v2.0.1) | Refactored (v3.0.0) | Change |
|---|---|---|---|
| Output files (excl. per-service) | 14 (index + 13 UNITs) | 2 (manifest + audit) | -86% |
| Per-service files | Unchanged | Unchanged | No change |
| Carry-forward state | FOUNDATION_INDEX object | None | Eliminated |
| Prose content | Moderate (executive summary, narratives) | Zero | -100% |
| C4 diagrams | 8 separate UNIT files | 8 PlantUML code blocks in manifest | Consolidated |
| include_enhancement_protocol | Optional parameter | Removed | Governance → humanize-spec |
| Gap tracking | Scattered (traceability + governance) | Single open_questions registry | Consolidated |
| Estimated output tokens | ~22K-38K (with prose) | ~12K-20K (structured only) | ~45% reduction |
| Context overhead for downstream | Load 14+ files, parse each | Load manifest + relevant service files | -80% |
