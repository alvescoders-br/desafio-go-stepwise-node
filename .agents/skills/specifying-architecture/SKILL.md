---
name: specifying-architecture
description: >
  Completes the target architecture by producing structured specification UNIT files
  for communication, data, security, observability, infrastructure, architecture
  characteristics (ISO 25010), migration roadmap with Gherkin gate criteria, technology
  stack summary with ADR cross-references, risk analysis, and governance+validation.
  Output is a manifest plus per-UNIT structured files (zero prose). Uses Write-Flush-Forget
  with SPEC_INDEX as sole carry-forward. Enforces ADR technology fidelity, PRD risk
  carry-forward, and service coverage across all UNITs. BUILD, CONTINUATION REPAIR,
  and SURGICAL REPAIR modes. Supports chunked execution via chunk_size and resume_from_unit.
  Human-readable output via humanize-spec on demand.
license: Globant
metadata:
  author: aipods-team
  version: 3.0.0
  category: architecture
  tags: software-architecture, automated, agent-native, multi-file
---

# Specifying Architecture — Agent-Native Spec

## Quick Start

Complete the target architecture with infrastructure, security, observability, migration,
and risk specifications. Output is a **manifest + per-UNIT structured files**:

```
{target_architecture_path}/specs/
├── ARCH-SPECS-MANIFEST-{SESSION_ID}.md    ← UNIT catalog, cross-references, tech fidelity summary, validations, open_questions
├── units/                                  ← Per-UNIT files (structured, zero-prose)
│   ├── unit-12-communication.md
│   ├── unit-13-data.md
│   ├── unit-14-security.md
│   ├── unit-15-observability.md
│   ├── unit-16-infrastructure.md
│   ├── unit-17-characteristics.md
│   ├── unit-18-migration.md
│   ├── unit-19-tech-stack.md
│   ├── unit-20-risks.md
│   └── unit-21-governance-validation.md
└── ARCH-SPECS-AUDIT-{SESSION_ID}.md       ← Session metadata
```

## Why This Architecture

Each UNIT generates 1,500-2,500 lines of structured data (tables, Gherkin gates,
SLI/SLO tables, migration phases). Total output: 16,500-27,500 lines. Single file
is not viable — per-UNIT files stay.

**Manifest (always loaded):** UNIT catalog with completion status, cross-reference map
linking services/ADRs/risks across UNITs, tech fidelity summary, validation results,
open_questions. ~300-500 lines. Cheap to keep in context.

**Per-UNIT files (loaded on demand):** Structured data only — tables, matrices, Gherkin
gates. Zero prose. Downstream consumers load the manifest always, then one UNIT at a time.

**Consumption pattern:**
- `defining-qe-strategy` reads manifest for environment mapping and service catalog
- `creating-qe-master-plan` reads manifest for risk assessment + UNIT-20 for risk details
- `humanize-spec` renders on demand for human-readable output

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| target_architecture_path | string | Yes | Path to foundation document (Part 1 output) |
| adrs_path | string | Yes | Path to ADR collection (folder or summary) |
| prd_path | string | Yes | Path to PRD document |
| project_name | string | Yes | Project identifier |
| epics_path | string | No | Path to epics document |
| domain_boundaries_path | string | No | Path to domain boundary analysis |
| current_architecture_path | string | No | Path to current architecture documentation |
| chunk_size | integer | No | Max UNITs to generate per invocation. Default: 10 (all). Set to 3-4 when model output budget is constrained. |
| resume_from_unit | integer | No | Resume from this UNIT number (12-based, inclusive). Use when a previous chunk completed partially. Default: 0 (start from beginning). |
| failure_feedback | string | No | Feedback for REPAIR mode |

**If any Required parameter is not defined, ABORT EXECUTION.**

## Workflow

Read reference files from `references/` ONLY when you reach that UNIT group.

### Step 1: Initialize & Session Setup

**Command:**
```
# Target Architecture Specifications Architect - FIC Methodology / Agent-Native Architecture
# Persona: Senior Software Architect -- infrastructure, security, migration planning.
#   Formal third person. Minimal verbosity. No jargon.
# CRITICAL: NON-INTERACTIVE SESSION. PROCEED AUTONOMOUSLY.

## Folder Resolution (BUILD vs REPAIR)
## The foundation folder is at {target_architecture_path}/ (no SESSION_ID suffix).
## SESSION_ID goes in filenames only, never in the folder name.
FOUNDATION_FOLDER = {target_architecture_path}
IF FOUNDATION_FOLDER not found or empty:
  ABORT with "No architecture foundation found at {target_architecture_path}"
IF failure_feedback NOT empty (REPAIR detected):
  SPECS_FOLDER = FOUNDATION_FOLDER + '/specs/'
  UNITS_SUBFOLDER = SPECS_FOLDER + 'units/'
  IF SPECS_FOLDER does not exist or is empty -> write Gap Report -> EXIT.
  MANIFEST = find existing ARCH-SPECS-MANIFEST-*.md in SPECS_FOLDER
  IF not found -> write Gap Report -> EXIT.
  Load MANIFEST -> PREVIOUS_MANIFEST -> SOURCE_LOG
  PREVIOUS_VERSION = extract version -> NEW_VERSION = increment patch (CONTINUATION) or minor (SURGICAL)
  Parse failure_feedback -> REPAIR_TYPE + REPAIR_DIRECTIVES (see Step 2)
ELSE (BUILD or RESUME):
  SPECS_FOLDER = FOUNDATION_FOLDER + '/specs/'
  UNITS_SUBFOLDER = SPECS_FOLDER + 'units/'
  MANIFEST = SPECS_FOLDER + 'ARCH-SPECS-MANIFEST-' + SESSION_ID + '.md'
  CHECKPOINT_FILE = UNITS_SUBFOLDER + '_checkpoint.json'
  mkdir -p SPECS_FOLDER
  mkdir -p UNITS_SUBFOLDER

  ## SESSION_ID is provided by the harness/execution metadata per execution-protocol.md §1.
  ## REPAIR/RESUME MUST reuse the existing session_id from prior ARCH-SPECS-MANIFEST-* filenames.
  ## SESSION_ID goes in filenames only (e.g. ARCH-SPECS-MANIFEST-{SESSION_ID}.md), never in folder names.

  **FIRST ACTION — MANDATORY:** Write `_progress.json` to the output folder before any other file write.
  This prevents the orchestrator from sending SIGINT.
  WRITE SPECS_FOLDER + '/_progress.json':
    { "skill": "specifying-architecture", "session_id": "initializing",
      "status": "RUNNING", "started_at": "<ISO timestamp>", "completed_at": null,
      "total": 0, "completed": 0, "items": [] }

  ## Chunking & Resume Setup
  ALL_UNITS = [12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
  CHUNK_SIZE = chunk_size OR 10  # default: all units
  RESUME_FROM = resume_from_unit OR 0  # default: start from beginning

  IF CHECKPOINT_FILE exists AND RESUME_FROM > 0:
    # Resuming a previous chunk — load checkpoint state
    Load CHECKPOINT_FILE → SPEC_INDEX (includes tech_decisions, services,
      completed_units, fidelity_corrections, unit_status, cross_references)
    COMPLETED_UNITS = SPEC_INDEX.completed_units  # e.g., [12, 13, 14]
    REMAINING_UNITS = [u for u in ALL_UNITS if u >= RESUME_FROM and u not in COMPLETED_UNITS]
    NEW_VERSION = SPEC_INDEX.version OR "1.0.0"
    LOG: "RESUME: loaded checkpoint. Completed: {COMPLETED_UNITS}. Resuming from UNIT-{RESUME_FROM}."
  ELSE:
    # Fresh BUILD
    COMPLETED_UNITS = []
    REMAINING_UNITS = ALL_UNITS
    NEW_VERSION = "1.0.0"

  # Apply chunk_size: limit this invocation to at most CHUNK_SIZE units
  UNITS_THIS_CHUNK = REMAINING_UNITS[:CHUNK_SIZE]
  IS_FINAL_CHUNK = (len(UNITS_THIS_CHUNK) == len(REMAINING_UNITS))

  LOG: "Chunk plan: generating UNITs {UNITS_THIS_CHUNK}. Final chunk: {IS_FINAL_CHUNK}."

## State Initialization
SOURCE_LOG = []
CHANGE_LOG = []

## FIC Principles
1. Foundational: Zero Invention. ADR Technology Fidelity: versions MUST match ADR decisions.
2. Instructional: Atomic UNIT execution. ONE UNIT -> write file -> flush -> next.
   Carry forward ONLY SPEC_INDEX, NOT full UNIT text.
3. Contextual: Each UNIT writes its own file under units/. Manifest provides coordination.

**ANTI-BATCHING RULE — CRITICAL:**
Write ONE file per tool call. Do NOT batch multiple UNIT files or manifest sections
into a single bash heredoc. Batching exhausts context and kills the session before
completion writes (LAST ACTION, Memory Bank, stepwise outputs).

**Context Budget Rule:**
When reading upstream artifacts (ADRs, domain boundaries, architecture foundation),
read ONLY manifest/index files (ADR-SPEC-*.md, BOUNDARIES-SPEC-*.md,
ARCH-FOUNDATION-SPEC-*.md). Do NOT open individual per-item files. The catalog
tables in the manifest contain all traceability data needed.

## Write-Flush-Forget Protocol (Per UNIT)
After each UNIT is generated:
  1. WRITE NOW: Save to UNITS_SUBFOLDER/unit-{NN}-{slug}.md. Mandatory tool call.
  2. UPDATE: Merge UNIT metadata into SPEC_INDEX. Add UNIT number to completed_units.
  3. SERIALIZE INDEX: Write SPEC_INDEX to UNITS_SUBFOLDER/_spec_index.json.
  4. WRITE CHECKPOINT: Write SPEC_INDEX (including completed_units, version, chunk_meta)
     to CHECKPOINT_FILE (_checkpoint.json). This enables resumption if interrupted.
  5. FORGET: Drop UNIT text from memory. Only SPEC_INDEX survives.
  6. VERIFY: Confirm UNIT file exists and is non-empty.

Before generating the NEXT UNIT:
  1. READ SPEC_INDEX from UNITS_SUBFOLDER/_spec_index.json (fresh state).
  2. This is the ONLY carry-forward state. All prior UNIT text is gone.

## Chunk Completion
After processing all UNITs in UNITS_THIS_CHUNK:
  IF IS_FINAL_CHUNK:
    → Proceed to manifest + audit generation (Steps 5-6).
    → Delete CHECKPOINT_FILE after manifest is written.
  ELSE:
    → Write final checkpoint with completed_units updated.
    → LOG: "Chunk complete. Generated UNITs {UNITS_THIS_CHUNK}. Next: resume_from_unit={next_unit}."
    → EXIT. Do NOT write manifest or audit — they require all UNITs.
    → The next invocation will resume with resume_from_unit={next_unit}.

## Token Budget Guidance
Target tokens per UNIT. Later UNITs MUST NOT be truncated because earlier UNITs
consumed too many output tokens.

| UNIT | Priority | Target Tokens | Notes |
|------|----------|---------------|-------|
| 12   | High     | 2500          | Communication matrix is table-heavy |
| 13   | High     | 2500          | Data topology tables |
| 14   | High     | 3000          | Security zones, threat model, auth tables |
| 15   | Medium   | 2500          | SLI/SLO table per service + observability |
| 16   | Medium   | 2000          | Infrastructure deployment tables |
| 17   | Medium   | 2000          | ISO 25010 characteristics assessment table |
| 18   | High     | 3000          | Migration phases + Gherkin gate criteria (critical) |
| 19   | High     | 2000          | Tech stack fidelity checkpoint (critical) |
| 20   | Medium   | 2000          | Risk table with mitigations |
| 21   | Medium   | 2500          | Merged governance + validation audit |

## Global Conventions
- H1 Title Rule: `# {project_name} -- UNIT-{NN}: {Title}`
- PlantUML Colors: Core=#1168bd, Supporting=#6db33f, Generic=#999999,
  External=#f39c12, DB=#darkblue
- Horizontal Slicing: [SVC-ID]-BE / [SVC-ID]-FE. No hybrids.
- Gherkin: Happy + Unhappy per service in catalog. Strict Given/When/Then.
- Style: Formal third person. Minimal verbosity. Zero prose.
- Max 3000 tokens per file. If larger, split.

## PATH GUARD — MANDATORY
target_architecture_path is the FINAL folder path as resolved by the capability (the
foundation folder; this skill writes under `{target_architecture_path}/specs/`).
Use it EXACTLY as provided — do NOT prepend artifacts/outputs/ or any other prefix.
Do NOT infer a parent folder from sibling parameters (e.g. adrs_path, domain_boundaries_path, prd_path).
  Wrong: artifacts/outputs/product-delivery/ + target-architecture/specs
         (stealing prefix from a sibling's path)
  Right: target-architecture/specs (derive from parameter value, relative to execution_dir)
If target_architecture_path is a bare segment (no `/` or `./`), treat it as relative to CWD.
If a sibling parameter has a full path and yours is bare, that is an UPSTREAM BUG —
abort with a Gap Report instead of adopting the sibling's parent.

## EARLY-WRITE RULE — MANDATORY
Silent-failure prevention. You MUST write the FIRST UNIT file (UNIT-12 or RESUME_FROM
UNIT) within 5 tool calls after entering the per-UNIT generation loop. "Read more, think
more" before the first UNIT write is the #1 silent-failure pattern — multi-minute
thinking loops that never produce output. If you cannot produce the first UNIT after 5
reads, ABORT with a Gap Report identifying which inputs were missing. Each subsequent
UNIT uses Write-Flush-Forget (one tool call per UNIT), NOT a single final dump.

## Internal Reasoning: ALL in English regardless of output language.
```

**Execution:** automated


### Step 2: Input Validation (STOP-GATE)

**Command:**
```
## Foundation Document Validation (CRITICAL GATE)
READ foundation FROM target_architecture_path
REQUIRED content in foundation:
  - Executive Summary (UNIT_01) with technology stack overview
  - Service Catalog (UNIT_03) with at least 1 service defined
  - At least 1 C4 diagram
  - Traceability section mapping services -> ADRs -> technologies

IF foundation missing or empty -> write Gap Report to MANIFEST -> EXIT.
IF Service Catalog empty -> write Gap Report to MANIFEST -> EXIT.

## ADR Technology Extraction
Extract from foundation's Traceability section + ADR files:
  TECH_DECISIONS = {
    "ADR-001": { technology: "...", version: "...", layer: "..." },
    "ADR-005": { technology: "...", version: "...", layer: "Data" },
    ...
  }

IF foundation Executive Summary tech stack contradicts Traceability:
  -> Flag as INHERITED FIDELITY VIOLATION.
  -> Use Traceability values (ADR-validated) as ground truth.
  -> Log correction in SOURCE_LOG.

## Extract Service Catalog
SERVICES = [SVC-XX with names, slices, contexts, tech stack from foundation]

## Load Upstream Data
FROM prd EXTRACT:
  ARCH_CONTEXT = {
    prd_nfr_ids: {NFR-XX -> description, target},
    prd_risks: [RSK-XX entries],
    prd_assumptions: [ASM-XX entries],
    prd_traceability_gaps: [gap items]
  }

FROM epics (if available) EXTRACT:
  ARCH_CONTEXT += {
    epic_priorities: [EPIC-XX with tiers],
    epic_dependencies: [dependency pairs]
  }

FROM domain_boundaries (if available) EXTRACT:
  ARCH_CONTEXT += {
    bounded_contexts: [BC-XX],
    integration_patterns: [patterns],
    event_flows: [flows]
  }

## Initialize SPEC_INDEX
SPEC_INDEX = {
  tech_decisions: TECH_DECISIONS,
  services: SERVICES,
  completed_units: {},         # {UNIT-NN -> {title, file, services_covered, adrs_referenced}}
  fidelity_corrections: [],    # tech name/version corrections logged
  arch_risks: [],              # ARCH-RSK-XX accumulated
  prd_risks_mapped: [],        # RSK-XX -> UNIT mapping
  assumptions_mapped: [],      # ASM-XX -> UNIT mapping
  epic_phase_mapping: {},      # EPIC-XX -> phase from UNIT-18
  cross_references: {},        # service-to-UNIT, ADR-to-UNIT, risk-to-UNIT maps
  unit_status: {
    "12": "PENDING", "13": "PENDING", "14": "PENDING", "15": "PENDING",
    "16": "PENDING", "17": "PENDING", "18": "PENDING", "19": "PENDING",
    "20": "PENDING", "21": "PENDING"
  }
}

## Mode Detection
IF failure_feedback NOT empty:
  MODE = REPAIR

  IF failure_feedback contains "REPAIR:" AND references missing UNITs or item counts:
    # CONTINUATION REPAIR — resume from partial completion
    REPAIR_TYPE = CONTINUATION
    1. Load SPEC_INDEX from UNITS_SUBFOLDER/_spec_index.json
       IF _spec_index.json missing -> fall back to scanning existing UNIT files
    2. MISSING_UNITS = UNITs with status != "COMPLETE" in SPEC_INDEX.unit_status
       (or UNITs whose files don't exist in UNITS_SUBFOLDER)
    3. FOR EACH UNIT in 12-21:
         IF UNIT in MISSING_UNITS -> mark for generation
         ELSE -> SKIP (file already exists, preserve verbatim)
    4. Resume UNIT Execution Loop from first missing UNIT
    5. NEW_VERSION = increment PATCH from existing version

  ELSE:
    # SURGICAL REPAIR — targeted fixes to specific UNITs
    REPAIR_TYPE = SURGICAL
    1. Load existing UNIT files from UNITS_SUBFOLDER -> SOURCE_LOG
    2. Load SPEC_INDEX from UNITS_SUBFOLDER/_spec_index.json
    3. Extract version -> NEW_VERSION = increment MINOR
    4. Parse feedback -> REPAIR_DIRECTIVES [{ target_unit: "UNIT-NN"|"global", instruction, reason }]
    5. REPAIR Contract: Load specific UNIT file -> apply directive -> rewrite IN PLACE.
       Preserve unchanged UNITs verbatim.

    ## Open-Question Resolution Pass (MANDATORY before regeneration)
    ##
    ## Convert SPEC_INDEX.open_questions entries that the reviewer answered into
    ## SPEC_INDEX.decisions_confirmed before regenerating any UNIT. Re-emitting
    ## a question the reviewer already answered is a protocol violation.
    FOR EACH oq in SPEC_INDEX.open_questions:
      FOR EACH directive in REPAIR_DIRECTIVES:
        IF directive references oq.id OR
           directive.instruction semantically answers oq.question:
          decision = {
            id: derive_decision_id(oq.id),
            topic: oq.topic,
            decision: extract_answer(directive.instruction),
            source: "reviewer-feedback@" + directive.timestamp,
            confidence: "confirmed"
          }
          SPEC_INDEX.decisions_confirmed.append(decision)
          SPEC_INDEX.open_questions.remove(oq)
          LOG: "OQ resolved by reviewer: " + oq.id + " → " + decision.id
          break

    ## Zero Re-Ask Rule: in regenerated UNITs and the manifest, NEVER emit an
    ## open_question that shares topic / UNIT-ID with any entry in
    ## SPEC_INDEX.decisions_confirmed.

ELSE:
  MODE = BUILD, NEW_VERSION = "1.0.0"
```

**Execution:** automated

### Step 3: Upstream Consistency Rules

**These rules apply to ALL UNIT generation. Loaded once, referenced throughout.**

```
## UPSTREAM CONSISTENCY RULES (Mandatory)

# 1. ADR Technology Fidelity (CRITICAL)
Every technology name and version in this document MUST exactly match the decision
in the referenced ADR. Before writing ANY technology reference, verify against
SPEC_INDEX.tech_decisions. Mismatch -> correct to match ADR, log correction.
UNIT-19 (Tech Stack Summary) is the FINAL FIDELITY CHECKPOINT.

# 2. Technology Neutrality (Scoped per UNIT)
Technology names allowed ONLY in the UNIT whose topic IS that technology decision.
UNIT-13 (Data) may name the database (ADR-005). UNIT-12 (Communication) must say
"persistence layer" not the database name. UNIT-20 (Risks) uses tech names only
in specific mitigation context for that risk.

# 3. PRD Risk Carry-Forward (Mandatory)
ALL RSK-XX from ARCH_CONTEXT.prd_risks MUST appear in UNIT-20 with architecture-level
mitigations. PRD risks keep original RSK-XX IDs. Architecture-specific risks get
ARCH-RSK-XX IDs (no collision with PRD IDs).

# 4. PRD Assumption Carry-Forward (Mandatory)
ALL ASM-XX from ARCH_CONTEXT.prd_assumptions MUST be referenced where they affect
targets (e.g., SLO table in UNIT-15, characteristics in UNIT-17).
IF an SLO target does not trace to a PRD NFR with a numeric value:
  Assign new ASM-XX ID, document assumption, surface in open_questions.

# 5. Epic Alignment (UNIT-18 Migration Roadmap)
Migration phases MUST reference EPIC-XX IDs.
Must Have epics -> Phase 1. Should Have -> Phase 2.
Phase sequence must not conflict with epic dependency graph.

# 6. Architecture Unit Coverage
When SPEC_INDEX.services identifies service boundaries, those services MUST appear in the
architecture UNITs where those service boundaries are relevant, including UNIT-13 (data topology),
UNIT-15 (SLO table), and UNIT-18 (migration phases), plus UNIT-12 when communication
architecture is service-to-service.
When the architecture uses non-service runtime or module boundaries, those architecture units
MUST appear in the applicable UNITs for data, observability, migration, and communication.
Missing required architecture unit in any applicable UNIT -> flag in open_questions.

# 7. Source Fidelity Check (Per UNIT, before writing)
After generating each UNIT:
  a. Technology names: only allowed if this UNIT's topic covers that tech -> else VIOLATION
  b. Service references: all SVC-XX exist in SPEC_INDEX.services -> else hallucination
  c. ADR references: all ADR-NNN exist in SPEC_INDEX.tech_decisions -> else hallucination
  d. Version numbers: match SPEC_INDEX.tech_decisions exactly -> else FIDELITY VIOLATION
  IF violations -> correct before writing. Log to SPEC_INDEX.fidelity_corrections.

# 8. Mid-Execution Checkpoint (After UNIT-17, Before UNIT-18)
UNITs 18-21 depend on complete SPEC_INDEX from UNITs 12-17. Checkpoint validates
completeness before proceeding. Details in Step 4.
```

**Execution:** automated (loaded into context)

### Step 4: Per-UNIT Generation Loop

**Pattern Reuse Search (MANDATORY before each UNIT's component/integration synthesis):**

Before adding any NEW component, integration, runtime, or service inside a UNIT, the agent MUST search the context-pack for an existing pattern that solves the same problem. Inventing a new pattern when one is documented in the context-pack is a protocol violation.

```
CP_FILES = <context-pack files surfaced in the system prompt at
            session start (loaded by the harness)>

FOR EACH proposed in candidate_components_for_this_UNIT:
  search_terms = derive_search_terms(proposed)   # nouns + stems from name/purpose
  matched = false
  FOR EACH file in CP_FILES:
    IF exists(file):
      hits = grep_case_insensitive(file, search_terms)
      IF hits:
        proposed.pattern_source = file + "#" + hits[0].line
        proposed.classification = "reuse"
        record_in_audit:
          "Pattern reuse (UNIT-NN): '" + proposed.name + "' grounded in " + file
        matched = true; break
  IF NOT matched:
    proposed.classification = "new"
    record_in_audit:
      "Pattern reuse search (UNIT-NN): no existing pattern for '" +
      proposed.name + "'. Searched " + len(CP_FILES) + " context-pack files."

## Reuse-classified items MUST appear in the UNIT file using pattern_source
## verbatim — do NOT rename or paraphrase the existing pattern.
```

**For each UNIT (12 through 21), execute the atomic loop:**

1. **REPAIR skip check:**
   - If CONTINUATION REPAIR and this UNIT is already COMPLETE -> SKIP.
   - If SURGICAL REPAIR and no directive targets this UNIT -> SKIP (preserve).
2. **Reference file management (load only what's needed):**
   - IF this is the FIRST UNIT in a reference group (12, 15, 18, 20):
     READ the corresponding reference file from `references/` NOW.
     DO NOT read reference files for later groups.
   - ELSE: Reference file for this group is already loaded.
3. **State reload:** READ SPEC_INDEX from UNITS_SUBFOLDER/_spec_index.json (skip for UNIT-12 in BUILD mode — index was just created).
4. Execute UNIT instructions using SPEC_INDEX + ARCH_CONTEXT.
5. Run Source Fidelity Check (Step 3, Rule 7).
6. **Write-Flush-Forget Protocol (all 5 steps from Step 1):**
   - Write UNIT file, serialize SPEC_INDEX, forget, verify.
7. **Reference file flush:**
   - IF this is the LAST UNIT in a reference group (14, 17, 19, 21):
     FLUSH the reference file text. It will not be needed again.

**INTER-UNIT CONTRACTS:**
- UNIT-12 (Communication): needs architecture interaction boundaries in scope, ARCH_CONTEXT.integration_patterns
- UNIT-13 (Data): needs architecture data boundaries in scope, TECH_DECISIONS for data layer
- UNIT-14 (Security): needs architecture trust boundaries in scope, ADR auth/security decisions
- UNIT-15 (Observability): needs architecture runtime units in scope, prd_nfr_ids, prd_assumptions
- UNIT-16 (Infrastructure): needs deployment/runtime boundaries in scope, ADR deployment decisions
- UNIT-17 (Characteristics): needs prd_nfr_ids, all prior UNIT metadata
- UNIT-18 (Migration): needs architecture units in scope, epic_priorities, prd_risks
- UNIT-19 (Tech Stack): needs TECH_DECISIONS (FINAL FIDELITY CHECKPOINT)
- UNIT-20 (Risks): needs prd_risks, all prior UNIT metadata for arch risks
- UNIT-21 (Governance+Validation): needs SPEC_INDEX (complete), SOURCE_LOG, CHANGE_LOG

**Reference file groups (load at group start, flush at group end):**
- UNIT 12-14: `references/units-12-14-comm-data-security.md`
- UNIT 15-17: `references/units-15-17-obs-infra-chars.md`
- UNIT 18-19: `references/units-18-19-migration-techstack.md`
- UNIT 20-21: `references/units-20-22-risks-governance-validation.md`

**Domain logic per UNIT:**
- UNIT-12: Communication architecture for the interaction patterns in scope (service-to-service when applicable, sync/async, protocols, ADR refs), API design standards, event schema registry when event-driven interactions exist, error handling patterns
- UNIT-13: Data topology for the architecture units in scope (database per service/module when applicable, ownership, replication), consistency model per bounded context, data migration strategy
- UNIT-14: Security zones and trust boundaries in scope, threat model table, auth/authz matrix, encryption standards, compliance mapping
- UNIT-15: SLI/SLO table for the runtime units in scope (traces to PRD NFRs), logging strategy, metrics catalog, distributed tracing when applicable
- UNIT-16: Deployment targets for the runtime units in scope, scaling policies (horizontal/vertical when applicable), resource specifications, cost projections
- UNIT-17: ISO 25010 characteristics assessment table (performance, reliability, security, maintainability, etc.), NFR-to-characteristic mapping
- UNIT-18: Migration roadmap with phases (Must Have -> Phase 1, Should Have -> Phase 2), Gherkin gate criteria per phase (CRITICAL — strict Given/When/Then go/no-go), rollback strategy per phase
- UNIT-19: Technology stack summary — FINAL FIDELITY CHECKPOINT. Every tech/version cross-referenced against SPEC_INDEX.tech_decisions. Any mismatch -> correct + log
- UNIT-20: Risk table (RSK-XX from PRD + ARCH-RSK-XX from architecture decisions), probability/impact/mitigation per risk, no ID collisions
- UNIT-21: Merged governance + validation. Governance: session info, fidelity corrections applied, change log (REPAIR). Validation: ADR fidelity audit, service coverage check, upstream consistency check, risk ID collision check, internal consistency check, summary count verification, overall audit status (PASS/FAIL)

### Mid-Execution Checkpoint (After UNIT-17, Before UNIT-18)

```
UNITs 18-21 depend on a complete SPEC_INDEX from UNITs 12-17. Before proceeding:
1. Re-read SPEC_INDEX from UNITS_SUBFOLDER/_spec_index.json (fresh state).
2. Verify required architecture units from SPEC_INDEX.services or equivalent runtime/module boundaries appear in completed_units for the applicable UNITs (including UNITs 12, 13, 15 when relevant).
3. Verify tech_decisions has no unresolved references.
4. Check SPEC_INDEX.unit_status shows UNITs 12-17 all COMPLETE.
5. Log checkpoint status to SOURCE_LOG.

IF any verification fails:
  -> Log failure details to SOURCE_LOG.
  -> Continue with warnings (do NOT abort — partial output is better than none).
  -> Surface failures in open_questions in the manifest.
```

**REPAIR Mode:**
- CONTINUATION: detect missing UNITs from SPEC_INDEX.unit_status, regenerate only missing.
- SURGICAL: targeted fixes per directive, preserve completed UNITs verbatim.
- Epics/UNITs without directives -> SKIP (preserve).

**Execution:** automated (sequential, one UNIT at a time)

### Step 4.5: Quality Validation Gate

**Command:**
```
1. Source Fidelity: All UNIT file references trace to real ADRs, architecture units, and upstream artifacts
2. Completeness: All required and applicable sections populated (no empty stubs in any UNIT file)
3. Cross-Reference Integrity: UNIT IDs, architecture-unit mappings, ADR references, and architecture specs cross-reference correctly
4. Status Protocol Compliance: Every item has status (complete|pending|assumption)
5. Source Tags: Every item with status:complete has a source reference
6. Count Verification: Summary counts match actual item counts in each section
7. Anti-Fade: Last UNIT's specification depth matches first UNIT's depth

IF corrections needed → apply in place, log to CHANGE_LOG
```
**Execution:** automated

### Step 5: Generate ARCH-SPECS-MANIFEST

**Command:**
```
## Build manifest from SPEC_INDEX (accumulated during UNIT generation)

WRITE to MANIFEST:
## Set the manifest front-matter `version:` to NEW_VERSION. On REPAIR this MUST be the
## incremented patch/minor (Step 1: PREVIOUS_VERSION → NEW_VERSION) — editing content in
## place without bumping `version` is a §7 violation. See execution-protocol §7.2 step 8.

  # {project_name} — Architecture Specifications Manifest
  version: {NEW_VERSION}
  session: {SESSION_ID}
  mode: {BUILD | REPAIR}
  date: {ISO 8601}
  foundation: {target_architecture_path}
  status: {draft | complete}

  ---

  ## unit_catalog

  | unit | title | file | architecture_units_covered | adrs_referenced | status |
  |------|-------|------|----------------------------|-----------------|--------|
  | 12 | Communication Architecture | units/unit-12-communication.md | SVC-01,MOD-01,... | ADR-001,ADR-003 | complete |
  | 13 | Data Architecture | units/unit-13-data.md | SVC-01,MOD-01,... | ADR-005 | complete |
  | ... | ... | ... | ... | ... | ... |
  | 21 | Governance & Validation | units/unit-21-governance-validation.md | — | — | complete |

  ---

  ## cross_reference_map

  ### architecture_unit_to_units
  | architecture_unit | unit_12 | unit_13 | unit_14 | unit_15 | unit_16 | unit_17 | unit_18 | unit_19 | unit_20 |
  |-------------------|---------|---------|---------|---------|---------|---------|---------|---------|---------|
  | SVC-01 / MOD-01   | Y       | Y       | Y       | Y       | Y       | —       | Y       | —       | —       |
  (All architecture units in scope from SPEC_INDEX.services or equivalent runtime/module boundaries. Missing = flag.)

  ### adr_to_units
  | adr | decision | units_referenced_in | fidelity_status |
  |-----|----------|---------------------|-----------------|
  | ADR-001 | {tech} {version} | 12, 19 | PASS |
  (All ADRs from SPEC_INDEX.tech_decisions.)

  ### risk_to_units
  | risk_id | source | unit_20_present | mitigation_status |
  |---------|--------|-----------------|-------------------|
  | RSK-01  | PRD    | Y               | complete          |
  | ARCH-RSK-01 | UNIT-13 | Y          | complete          |

  ---

  ## tech_fidelity_summary

  | adr | technology | version | fidelity_status | corrections_applied |
  |-----|-----------|---------|-----------------|---------------------|
  | ADR-001 | {tech} | {version} | PASS | 0 |
  (From SPEC_INDEX.tech_decisions + fidelity_corrections.)

  total_corrections: {N}
  final_checkpoint_unit19: {PASS | FAIL}

  ---

  ## validations

  | check | expected | actual | status | details |
  |-------|----------|--------|--------|---------|
  | ADR Fidelity Audit | All versions match | {result} | PASS/FAIL | {details} |
  | Service Coverage (UNIT-12, when applicable) | {N} services | {N} | PASS/FAIL | {missing} |
  | Service Coverage (UNIT-13) | {N} services | {N} | PASS/FAIL | {missing} |
  | Service Coverage (UNIT-15) | {N} services | {N} | PASS/FAIL | {missing} |
  | Service Coverage (UNIT-18) | {N} services | {N} | PASS/FAIL | {missing} |
  | PRD Risk Carry-Forward | {N} RSK-XX | {N} in UNIT-20 | PASS/FAIL | {missing} |
  | Assumption Carry-Forward | {N} ASM-XX | {N} referenced | PASS/FAIL | {missing} |
  | Epic Alignment (UNIT-18) | {N} EPIC-XX | {N} in phases | PASS/FAIL | {missing} |
  | Risk ID Collision | No overlap | {result} | PASS/FAIL | {collisions} |
  | Internal Consistency | Foundation phases = UNIT-18 | {result} | PASS/FAIL | {details} |
  | Mid-Execution Checkpoint | UNITs 12-17 complete | {result} | PASS/FAIL | {details} |
  | Count Verification | Consistent counts | {result} | PASS/FAIL | {details} |

  overall_status: {PASS | FAIL}

  ---

  ## open_questions

  | id | source_unit | question | impact | suggested_resolution |
  |----|-------------|----------|--------|---------------------|
  (All gaps, missing data, assumptions, inherited issues. Single registry.)
```

**Execution:** automated

### Step 6: Write Audit File & Finalize

**Command:**
```
## Write ARCH-SPECS-AUDIT-{SESSION_ID}.md
AUDIT_FILE = SPECS_FOLDER + 'ARCH-SPECS-AUDIT-' + SESSION_ID + '.md'

WRITE to AUDIT_FILE:
  # {project_name} — Architecture Specifications Session Audit
  session: {SESSION_ID}
  version: {NEW_VERSION}
  mode: {MODE}
  date: {ISO 8601}

  ## sources
  | source | path | status |
  |--------|------|--------|
  | Foundation | {target_architecture_path} | Loaded |
  | PRD | {prd_path} | Loaded |
  | ADRs | {adrs_path} | Loaded |
  | Epics | {epics_path} | Loaded / Not provided |
  | Domain Boundaries | {domain_boundaries_path} | Loaded / Not provided |
  | Current Architecture | {current_architecture_path} | Loaded / Not provided |

  ## generation_log
  | unit | title | tokens_est | services | adrs | fidelity_corrections | timestamp |
  |------|-------|------------|----------|------|---------------------|-----------|
  (One row per UNIT generated in this session.)

  ## fidelity_corrections
  | unit | original | corrected_to | adr_reference |
  |------|----------|-------------|---------------|
  (From SPEC_INDEX.fidelity_corrections.)

  ## validation_summary
  | check | result | details |
  |-------|--------|---------|
  (12 checks from Step 5 validations.)

  ## change_log (REPAIR only)
  | version | directive | target_unit | change | impact |
  |---------|-----------|-------------|--------|--------|

  ## REPAIR-only: set `mode: REPAIR` and APPEND (do not overwrite) a `## Repair History`
  ## entry — version, timestamp, directives_applied, sections_changed, sections_preserved,
  ## repair_delta (per execution-protocol §7.2 step 8).

## REPAIR self-check (execution-protocol §7.2 step 9): before final_response, confirm the
## manifest `version` is strictly greater than PREVIOUS_VERSION AND the AUDIT has the new
## `## Repair History` entry. If not, fix the bookkeeping now — do not finish.

## Output Verification (mandatory before exit)
Before reporting completion, verify all output files exist on disk:
1. CONFIRM MANIFEST exists and is non-empty
2. CONFIRM all expected UNIT files in UNITS_SUBFOLDER/ are present (10 files)
3. CONFIRM AUDIT_FILE exists
IF any file is missing or empty:
  LOG "OUTPUT VERIFICATION FAILED: {missing_file}"
  DO NOT exit — regenerate the missing file before completing

## Metadata
APPEND to ./artifacts/outputs/artifact-tracking.md:
  session, artifact_type: target_architecture_specifications, mode, version,
  units_generated, services_covered, adrs_referenced, fidelity_corrections,
  prd_risks_mapped, overall_validation_status, timestamp

Memory Bank artifact type: `"{N} architecture-docs"` (e.g., `"3 architecture-docs"`).

**Memory Bank — MANDATORY session-end writes:**
1. Overwrite `context-pack/active-context.md` with session status, decisions, blockers, key artifacts (see execution-protocol.md Section 4 for schema).
2. Append one milestone row to `context-pack/progress.md` with artifact count above.

**Section 2 LAST ACTION — MANDATORY:** Update `_progress.json` status to `COMPLETED` with `completed_at` timestamp.
If the session failed, set status to `FAILED` instead.

Ready for Architecture Review.
```

**Execution:** automated

### Step 7: Emit Harness Outputs Sidecar

**Apply execution-protocol.md Section 11** — Harness Output Sidecar. Mandatory when the prompt contains a `## Run metadata` block. FINAL file write of the run (after Output Verification, ADR Summary Synthesis, Memory Bank, and `_progress.json` set to COMPLETED). Without it, the orchestrator falls back to the capability `value_template` (`{{output_folder}}/{{target_architecture}}`), which corrupts `target_architecture_path` into a doubly-nested folder when the parameter has already been pre-resolved to an absolute path. Downstream consumers (defining-qe-strategy, validating-architecture-compliance, generating-toolchain-record) then cannot locate the architecture spec.

**Output parameters this skill produces** (one key per row of the prompt's `## Output parameters` table):

- `target_architecture_path`: the **actual SPECS_FOLDER you wrote the manifest, UNIT files, and audit into** (§11.1.1 path-correctness). This skill writes directly to the resolved `target_architecture_path` parameter, so report that parameter as received in the prompt's `## Parameters` table — do NOT re-prepend `{output_folder}` (that causes the doubly-nested corruption). If your own logic ever diverged from the parameter, report the path you actually wrote to, not the parameter.

**Implementation:** the harness here accepts Bash heredoc for the sidecar write (the sidecar is NOT the SPEC_FILE, so §10.5's anti-Bash rule does not apply). Execute:

```
cat > {stepwise_outputs_file} << 'OUTPUTS_EOF'
{ "target_architecture_path": "{target_architecture_path}" }
OUTPUTS_EOF
```

`{stepwise_outputs_file}` is the path from the prompt's `## Run metadata` block's `output_file = '...'` line — copy it verbatim, do NOT reconstruct it.

Self-check: `cat {stepwise_outputs_file}` — verify non-empty. If empty or missing, re-execute. DO NOT describe output registration in response text — EXECUTE it. No tool calls after this; the next event is `final_response`.

**Execution:** automated

## ADR Summary Synthesis (MANDATORY after generating all ADRs)

After generating individual ADR files:
1. WRITE artifacts/outputs/adrs/adrs-summary.md:
   - Table: `| ADR-ID | Title | Decision | Status |` for each ADR
   - Links to individual ADR files
   - Technology decisions index
2. VERIFY adrs-summary.md exists and contains all ADR IDs
3. LOG: "ADR summary: {N} ADRs indexed at adrs/adrs-summary.md"

## Agentic-First Output Contract — No Calendar Time

Architecture artifacts are agentic-first: consumed by downstream AI agents and implementation skills, not human project managers. Do NOT include calendar-time references in any generated content.

**PROHIBITED in all architecture output (UNIT-18 migration roadmap and all other UNITs):**
- Week numbers or ranges (e.g., "Weeks 1-4", "4-6 weeks")
- Month or quarter references (e.g., "Q1", "Month 2")
- Calendar dates (e.g., "by March", "2026-06-01")
- Duration estimates in calendar units within `duration_estimate` fields

**For UNIT-18 migration phases, use instead:**
- `complexity: low | medium | high` — implementation complexity of this phase
- `scope: {N} epics, {M} services` — measurable scope
- `gate: {Gherkin gate criteria}` — machine-verifiable completion signal
- Phase ordering: dependencies on prior phases (not calendar)

**For all phasing references throughout the architecture spec:**
- Use phase names (Phase 0, Phase 1) and epic priority tiers (Must Have → Phase 1)
- Use epic dependency ordering, not calendar sequencing

VIOLATION: Any week/month/date or calendar-unit duration in architecture output is a format violation. Auto-correct by replacing with complexity, scope, or phase reference.

## Reference Files

- `references/units-12-14-comm-data-security.md` — Communication, Data, Security UNIT templates and context contracts
- `references/units-15-17-obs-infra-chars.md` — Observability, Infrastructure, Characteristics UNIT templates and context contracts
- `references/units-18-19-migration-techstack.md` — Migration Roadmap (with Gherkin gates), Tech Stack Summary UNIT templates
- `references/units-20-22-risks-governance-validation.md` — Risks, Governance+Validation UNIT templates (UNIT-21 merges old UNIT-21 governance + UNIT-22 validation)

## Rendering

This skill produces **agent-native structured data**. Human-readable output is NOT
generated here. Use `humanize-spec` skill with the appropriate architecture rendering
profile to produce formatted documents on demand.
