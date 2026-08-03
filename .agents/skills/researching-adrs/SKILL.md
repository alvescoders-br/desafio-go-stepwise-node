---
name: researching-adrs
description: >
  Generates Architecture Decision Records from domain boundaries, PRD, epics, and
  context packs. Output is a manifest (ADR-SPEC) plus one structured file per ADR
  under an adrs/ subfolder. Each ADR uses agent-native structured fields (tables,
  key-value pairs) — not prose paragraphs. Nygard sections (Context, Decision,
  Alternatives, Consequences) are expressed as typed fields for downstream agent
  consumption. Uses ADR_INDEX as the sole carry-forward contract. Enforces upstream
  consistency: technology-neutral language scoped per ADR, carries forward PRD
  risks/assumptions with ADR-level impact mapping. BUILD, REPAIR, and RESUME modes
  with chunked execution support. Human-readable output via humanize-spec on demand.
license: Proprietary
metadata:
  author: aipods-team
  version: 4.1.0
  category: discovery
  tags: software-architecture, agent-native, adr, zero-prose
compatibility: ""
---

# Researching ADRs — Agent-Native Spec

## Quick Start

Generate Architecture Decision Records from domain boundary analysis and technical
inputs. Output is a **manifest + per-ADR structured files** — not prose documents.
Downstream agents read fields programmatically. Human-readable output via `humanize-spec`.

## Known Failure Modes
<!-- ACCUMULATING — appended by calibrating-updates (WS6). Newest first. Rules MUST be generic/behavioral (project-agnostic); project-specific fixes go to context packs, never here. Format + entry rules: engineering-skills/references/known-failure-modes-format.md. Read these at pre-flight so a lesson learned once recurs no more. -->

- **KFM-001** (2026-07-11, source: run-1783807409427-2ifhmm8i)
  - Symptom: `00-index.md` marks ADRs (and `ADR-SPEC`) as `✅ COMPLETE` for which no file exists on disk. After a mid-run stop the tracker overstates progress — it claimed 12 ADRs + manifest done when only 7 `adr-*.md` files were written.
  - Root cause: the tracker was written at Step 2 with `✅ COMPLETE` rows (and invented summary rows) instead of all-pending, and the per-ADR index/checkpoint updates in Step 4 were skipped — so the index was never reconciled to what was actually on disk.
  - Rule: a tracker row may show `✅ COMPLETE` ONLY after that ADR's file is verified non-empty on disk. The tracker at init is 100% `⬜ TO BE GENERATED`. Never pre-mark, never batch-mark, never add rows the template does not define.

- **KFM-002** (2026-07-11, source: run-1783807409427-2ifhmm8i)
  - Symptom: after an executor crash, valid `adr-*.md` files remain on disk but neither REPAIR nor RESUME can proceed — REPAIR writes a Gap Report and exits ("manifest not found"), RESUME aborts ("cannot resume without checkpoint").
  - Root cause: `_checkpoint.json` is only durable if written after each ADR (it was skipped), and the manifest is only written at the very end — so a crash before Step 5 leaves recovery with no state file even though the real work survives on disk.
  - Rule: write `_checkpoint.json` after EVERY ADR write. Recovery (REPAIR/RESUME) MUST reconstruct state by scanning `adrs/adr-*.md` on disk when checkpoint and manifest are both absent — the ADR files are the source of truth, never a stale tracker.

## Anti-Patterns (do NOT)
<!-- ACCUMULATING — appended by calibrating-updates (WS6). One line each: **AP-NNN** (ISO-date, source: REC-NNN): prohibition — why. -->

- **AP-001** (2026-07-11, source: run-1783807409427-2ifhmm8i): never write a `00-index.md` row as `✅ COMPLETE` before that ADR's file exists non-empty on disk — a crash then leaves the tracker lying about progress.
- **AP-002** (2026-07-11, source: run-1783807409427-2ifhmm8i): never skip the per-ADR `_checkpoint.json` write — without it a crashed run cannot be resumed or repaired even though the ADR files survive.
- **AP-003** (2026-07-11, source: run-1783807409427-2ifhmm8i): never add rows or summary lines to `00-index.md` beyond the one-row-per-decision the template defines — extra `Phase A: ✅` / `ADR-SPEC: ✅` lines fabricate completion signal.

## Output Architecture

```
{adrs_path}/
├── ADR-SPEC-{SESSION_ID}.md          ← Manifest: tech stack matrix, ADR catalog,
│                                        cross-ref map, impact matrix, validations,
│                                        open_questions
├── 00-index.md                        ← Living progress tracker
├── adrs/                              ← Per-ADR structured files
│   ├── adr-001-{slug}.md             ← Agent-native structured ADR
│   ├── adr-002-{slug}.md
│   └── ...
├── _progress.json                     ← Orchestrator checkpoint
└── ADR-AUDIT-{SESSION_ID}.md         ← Session metadata + governance log
```

**Why manifest + per-ADR files:** Downstream agents (`establishing-architecture-foundation`,
`specifying-architecture`, `researching-code-design`) load the manifest for decision
summaries and cross-references (~500-800 lines, always loadable). They load individual
ADR files on demand when they need full decision detail. 12+ full ADRs would exceed
1,500 lines — too large for a single context load.

## Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| prd_path | string | Yes | — | Path to PRD document |
| domain_boundaries_path | string | Yes | — | Path to domain boundary analysis |
| project_name | string | Yes | — | Project identifier |
| technical_interview_path | string | No | — | Path to technical interview documentation |
| meeting_recording_path | string | No | — | Path to technical interview recording |
| current_architecture_path | string | No | — | Path to current architecture documentation |
| epics_path | string | No | — | Path to epics document |
| adrs_path | string | Yes | — | Output path for ADR collection. This IS the output location — files are written directly here. |
| chunk_size | integer | No | 12 | Max ADRs to generate per invocation. Set to 3 when model output budget is constrained. |
| resume_from_adr | integer | No | 0 | Resume Phase B from this ADR number (1-based). Use when a previous chunk completed partially. |
| failure_feedback | string | No | — | REPAIR mode directives |

**If any Required parameter is not defined, ABORT EXECUTION.**

## Chunked Execution

When `chunk_size` < total ADRs, the skill generates only that many ADRs per invocation
and exits without writing the manifest. On next invocation, set `resume_from_adr` to
the count of already-completed ADRs. The manifest is written on the final invocation
when all ADRs are complete.

The ADR_INDEX is the durable checkpoint. Each invocation writes `_checkpoint.json`.
The folder is reused across all chunk invocations — never recreated.
SESSION_ID must be identical across all chunk invocations for the same project.

## ADR_INDEX — Carry-Forward Contract

Initialize at Step 1. Update after every ADR write. This is the SOLE source of truth
between phases. Never carry full generated text — only IDs, paths, and status flags.

```
ADR_INDEX = {
  session_id: string,
  mode: BUILD | REPAIR,
  output_path: string,
  decisions: [{ seq, category, scope, affected_bcs }],
  completed_adrs: {
    ADR-NNN: {
      title, category, decision_summary, affected_bcs,
      quality_impact: { performance, scalability, reliability, security, maintainability },
      cross_refs: [ADR-NNN],
      file: "adr-{NNN}-{slug}.md",
      has_diagram: boolean,
      has_gherkin: boolean
    }
  },
  technology_eval: { layer: { category, options, recommended, adr_ref, scoring } },
  cross_ref_map: { ADR-NNN: [related ADR-NNN] },
  phase_status: { A: null|COMPLETE, B: null|PARTIAL|COMPLETE, C: null|COMPLETE },
  chunk_meta: { chunk_size, resume_from, total_adrs },
  engineering_assumptions: [],
  open_questions: []
}
```

## Upstream Consistency Rules

These rules apply to ALL ADR generation. Loaded at Step 2, referenced throughout.

### 1. Technology Neutrality (Scoped per ADR)
ADR `context.forces` and `context.constraints` MUST use capability-level language.
Technology names are ONLY allowed in:
- The `decision` section of the ADR that IS making that technology choice
- The `alternatives` table (comparing options)
- The `compliance` table (referencing governance mandates)
Technology names in any other section of an ADR that is NOT about that technology = BIAS VIOLATION.

### 2. PRD Assumption Carry-Forward
ALL ASM-XX from upstream MUST be referenced by at least one ADR in `context.assumptions_referenced`.

### 3. PRD Risk Carry-Forward
ALL RSK-XX from upstream MUST be referenced by at least one ADR in `context.risks_referenced`.

### 4. Epic Alignment
When an ADR impacts implementation sequencing, cross-reference EPIC-XX IDs.
Must Have epics must not be blocked by late-phase ADR decisions.

### 5. Domain Boundary Fidelity
Every ADR must reference which bounded contexts it affects from upstream `bounded_contexts`.
ADRs must not reference contexts that don't exist in the domain analysis.

### 6. NFR Traceability
ADR decisions addressing NFRs must reference the original NFR-XX ID. Exact format.

### 7. Source Fidelity Check (Per ADR, before writing)
Scan for: (a) technology names outside decision/alternatives/compliance of THIS ADR,
(b) BC references not in upstream, (c) FR/NFR IDs not in upstream,
(d) invented alternatives with no basis in domain analysis or context packs.

## Workflow

Read reference files from `references/` ONLY when you reach that phase.
Do NOT pre-load all reference files.

### Step 1: Initialize & Environment Setup

**Command:**
```
1. SESSION_ID:
     - BUILD: generate per execution-protocol.md §1 — `ADR-{PROJECT_NAME_UPPER}-{FEATURE_SLUG|SESSION_NAME}-{YYYYMMDD}` (NOT a bare timestamp).
     - REPAIR: do NOT generate. Recover it by parsing the existing `ADR-SPEC-{SESSION_ID}.md` filename in ADRS_FOLDER (§1 recovery algorithm). Never recompute a date in REPAIR.
   CHUNK_SIZE  = chunk_size parameter (default: 12)
   RESUME_FROM = resume_from_adr parameter (default: 0)

2. STATE RECOVERY HELPER — reconstruct_from_disk(ADRS_FOLDER)  (see KFM-002):
   Use this whenever the manifest or checkpoint is absent but ADR files survive
   (e.g. a prior run crashed mid-Phase-B before writing either). The `adr-*.md`
   files on disk are the source of truth — NEVER trust a stale 00-index.md, which
   may overstate progress (KFM-001).
     existing = sorted list of ADRS_FOLDER/adrs/adr-*.md
     FOR EACH file: parse ADR-NNN, title, category → ADR_INDEX.completed_adrs[ADR-NNN]
       (read only the header/decision fields needed to rebuild metadata; do not
        regenerate the ADR)
     REBUILD ADR_INDEX.decisions from the standard decision catalog (Step 2) so the
       full intended set is known, mark those with a file present as complete.
     REWRITE 00-index.md honestly from disk: ✅ COMPLETE only for ADRs whose file
       exists non-empty; ⬜ TO BE GENERATED for the rest.
     WRITE _checkpoint.json from the rebuilt ADR_INDEX.
     RETURN count of recovered ADRs.

3. REPAIR detection:
   IF failure_feedback is non-empty:
     MODE = REPAIR
     ADRS_FOLDER = resolve adrs_path
     IF ADRS_FOLDER does not exist or is empty → write Gap Report → EXIT
     MANIFEST = find existing ADR-SPEC-*.md in ADRS_FOLDER
     IF found:
       Load MANIFEST → PREVIOUS_MANIFEST
     ELSE IF adrs/adr-*.md files exist:
       ## Crash-before-manifest recovery (KFM-002). Do NOT Gap-Report-and-EXIT here.
       reconstruct_from_disk(ADRS_FOLDER)
       LOG "REPAIR: no manifest found; reconstructed ADR_INDEX from {N} ADR files on disk."
       IF failure_feedback asks only to COMPLETE/CONTINUE the run (no per-ADR fix):
         Treat remaining ⬜ ADRs as the work set — regenerate ONLY the missing ADRs,
         then write the manifest in Step 5 (i.e. finish the interrupted BUILD).
     ELSE (no manifest AND no ADR files) → write Gap Report → EXIT
     Parse failure_feedback → REPAIR_DIRECTIVES [{
       target_adr: "ADR-NNN" | "global" | "tech-stack" | "manifest" | "continue",
       instruction, reason
     }]
     NOTE: output_path MUST already exist. Never mkdir for REPAIR.

   ELSE IF RESUME_FROM > 0 (resuming a chunked BUILD):
     MODE = BUILD
     ADRS_FOLDER = resolve adrs_path
     IF ADRS_FOLDER does not exist → ABORT "resume_from_adr set but folder not found"
     CHECKPOINT = ADRS_FOLDER + '_checkpoint.json'
     IF CHECKPOINT exists:
       Load CHECKPOINT → rebuild ADR_INDEX
     ELSE IF adrs/adr-*.md files exist:
       ## Crash-before-checkpoint recovery (KFM-002). Do NOT ABORT here.
       reconstruct_from_disk(ADRS_FOLDER)
       LOG "RESUME: no checkpoint found; reconstructed ADR_INDEX from {N} ADR files on disk."
     ELSE → ABORT "Cannot resume: no checkpoint and no ADR files on disk"

   ELSE (fresh BUILD):
     MODE = BUILD
     ADRS_FOLDER = adrs_path + '/'
     mkdir -p ADRS_FOLDER
     mkdir -p ADRS_FOLDER + 'adrs/'

4. **FIRST ACTION — MANDATORY:** Write _progress.json before any other file:
   { "skill": "researching-adrs", "session_id": "initializing",
     "status": "RUNNING", "started_at": "<ISO timestamp>", "completed_at": null }

5. Initialize ADR_INDEX with session_id, mode, output_path

6. Zero Invention Policy: every claim in ADR output MUST trace to source evidence.
   Missing data → status: pending → registered in open_questions. Do NOT invent.

7. STOP-GATE — abort if:
   - prd_path missing or file not found
   - domain_boundaries_path missing or file not found
   - project_name empty
   - adrs_path empty
   LOG: "Step 1 COMPLETE. Session: {SESSION_ID}, Mode: {MODE}"
```

### Step 2: Input Validation & Source Loading

> **During source loading — apply execution-protocol.md Section 12 (Delegated Exploration) if your harness supports it.** Broad read-only sweeps for this skill (e.g. surveying the domain boundaries, PRD, and epics for the decisions each ADR must capture, locating where a technology choice already appears) MAY be delegated to a read-only exploration subagent on a cheap/fast model, which returns conclusions + source pointers (not file dumps). Synthesis, decision framing, and all writing stay with this agent, which verifies any delegated pointer before using it (Zero-Invention still applies). With no subagent capability, explore inline under the usual scope constraint — output quality is identical either way.

**Command:**
```
## Skip full validation on resume invocations
IF RESUME_FROM > 0:
  READ domain_boundaries and prd_content (minimum required for Phase B)
  REBUILD ADR_CONTEXT
  LOG "Resume: ADR_CONTEXT rebuilt. ADR_INDEX loaded from checkpoint."
  SKIP to Step 4.

## Critical Gate (first invocation only)
READ domain_boundaries FROM domain_boundaries_path
IF missing or empty → WRITE Gap Report → EXIT

READ prd_content FROM prd_path
IF missing or empty → WRITE Gap Report → EXIT

## Load & Extract Upstream Data
FROM domain_boundaries EXTRACT:
  ADR_CONTEXT = {
    bounded_contexts: [BC-XX with names, subdomains, capabilities],
    context_relationships: [relationship pairs with types],
    services: [SVC-XX with slices],
    integration_patterns: [pattern descriptions],
    nfrs_by_context: {BC-XX → NFR targets},
    event_flows: [event chains],
    engineering_decisions: [ED-XX from domain analysis]
  }

FROM prd_content EXTRACT:
  ADR_CONTEXT += {
    prd_fr_ids: {FR-XX → description},
    prd_nfr_ids: {NFR-XX → description, target},
    prd_assumptions: [ASM-XX entries],
    prd_risks: [RSK-XX entries],
    prd_traceability_gaps: [],
    api_paths: [concrete API paths from PRD]
  }

IF epics_path exists:
  FROM epics EXTRACT: ADR_CONTEXT += { epic_priorities, epic_dependencies }
ELSE:
  Log "Proceeding without epics."

IF current_architecture_path exists: READ → log "Loaded existing architecture"
IF technical_interview_path exists: READ → extract → ADR_CONTEXT.interview_context
IF meeting_recording_path exists: Transcribe → extract → ADR_CONTEXT.meeting_context

## Determine ADR Decision List
Parse bounded contexts and requirements to build the catalog.
Start from the standard decision categories below and include the ones supported by
bounded contexts, PRD requirements, current architecture, and explicit constraints.
Do not force categories that have no evidence in upstream artifacts.

ADR_DECISION_CANDIDATES = [
  { seq: 1,  category: "Technology Stack",            scope: "global",      affected_bcs: [...] },
  { seq: 2,  category: "Architecture Style",          scope: "global",      affected_bcs: [...] },
  { seq: 3,  category: "Service Decomposition",       scope: "per-context", affected_bcs: [...] },
  { seq: 4,  category: "Communication Patterns",      scope: "global",      affected_bcs: [...] },
  { seq: 5,  category: "Data Management",             scope: "per-context", affected_bcs: [...] },
  { seq: 6,  category: "API Design",                  scope: "global",      affected_bcs: [...] },
  { seq: 7,  category: "Authentication Strategy",     scope: "global",      affected_bcs: [...] },
  { seq: 8,  category: "Security Architecture",       scope: "global",      affected_bcs: [...] },
  { seq: 9,  category: "Observability",               scope: "global",      affected_bcs: [...] },
  { seq: 10, category: "Deployment & Infrastructure", scope: "global",      affected_bcs: [...] },
  { seq: 11, category: "API Gateway / Service Mesh",  scope: "global",      affected_bcs: [...] },
  { seq: 12, category: "Data Integration",            scope: "global",      affected_bcs: [...] }
]
ADR_DECISIONS = evidence-supported subset of ADR_DECISION_CANDIDATES
TOTAL_ADRS = len(ADR_DECISIONS)
Add ADRs beyond this candidate list only when domain-specific needs are evidenced upstream.

## Initialize ADR_INDEX fields
ADR_INDEX.decisions = ADR_DECISIONS
ADR_INDEX.chunk_meta = { chunk_size: CHUNK_SIZE, resume_from: RESUME_FROM,
                         total_adrs: TOTAL_ADRS }

## Write 00-index.md (Living Progress Tracker)
## HONEST-TRACKER INVARIANT (see AP-001, AP-003): at init EVERY row is pending.
## No row may read ✅ COMPLETE here — a status flips to ✅ ONLY in Step 4, and ONLY
## after that ADR's file is verified non-empty on disk. Emit EXACTLY the rows below —
## one per decision — and NOTHING else. Do NOT add "Phase A: ✅", "ADR-SPEC: ✅",
## or any other summary/completion line.
WRITE adrs_path/00-index.md:

  # {project_name} — ADR Progress
  session: {SESSION_ID}
  started: {date}
  mode: {MODE}

  | ADR | Category | Status | File |
  |-----|----------|--------|------|
  FOR EACH decision in ADR_DECISIONS:
    | ADR-{seq:03d} | {category} | ⬜ TO BE GENERATED | — |

## Self-check before proceeding: the file just written contains ZERO occurrences of
## "✅" and ZERO occurrences of "COMPLETE". If it does not, rewrite it correctly.
LOG: "Step 2 COMPLETE. {TOTAL_ADRS} decisions identified."
```

### Step 3: Phase A — Tech Stack Evaluation

Read `references/phase-a-tech-stack-evaluation.md` before executing this step.

**Command:**
```
IF MODE == REPAIR AND REPAIR_DIRECTIVES target "tech-stack" or "global":
  Regenerate tech stack evaluation.
ELSE IF MODE == REPAIR:
  SKIP (preserve existing technology_eval from manifest).
IF RESUME_FROM > 0:
  SKIP. technology_eval already loaded from checkpoint.
  PROCEED to Step 4.

GENERATE tech stack evaluation matrix following reference file instructions.
Store result in ADR_INDEX.technology_eval.
Write checkpoint: _checkpoint.json with ADR_INDEX state.
FLUSH evaluation text from memory. Only ADR_INDEX.technology_eval survives.
ADR_INDEX.phase_status.A = "COMPLETE"
LOG: "Step 3 COMPLETE. Tech stack evaluation ready."
```

### Step 4: Phase B — Per-ADR Generation (Atomic Loop)

**EARLY-WRITE RULE — MANDATORY (silent-failure prevention).**
You MUST write the FIRST ADR file in the chunk to disk within **5 tool calls**
after entering Step 4 — counting ANY tool call (think, view, bash, edit). Do
NOT compose all ADRs in memory before writing any of them. Multi-minute
thinking loops with no on-disk progress are the #1 silent-failure pattern:
they trigger orchestrator SIGINT or context overflow and lose 100% of the
work. The atomic per-ADR Write-Flush-Forget loop below already enforces this
once you start; the EARLY-WRITE rule guards the boundary between context
loading (Step 3) and the first per-ADR write.

Read `references/phase-b-adr-generation.md` before executing this step.

**Command:**
```
## Chunk Window
CHUNK_START = RESUME_FROM + 1
CHUNK_END   = min(RESUME_FROM + CHUNK_SIZE, TOTAL_ADRS)

REMAINING_ADRS = [d for d in ADR_INDEX.decisions
  if d.seq >= CHUNK_START AND d.seq <= CHUNK_END
  AND d.seq NOT IN already_complete_seqs]

ADR_COUNTER = RESUME_FROM

## CRITICAL: each ADR is a self-contained generate → write → flush cycle.
## The file-write tool MUST be invoked after EACH ADR.
## Do NOT accumulate multiple ADRs in memory.

FOR EACH current_decision in REMAINING_ADRS:
  ADR_COUNTER += 1
  ADR_ID = "ADR-{ADR_COUNTER:03d}"

  ## Pattern 5: Per-ADR Source Loading
  LOAD decision category, scope, affected_bcs from current_decision
  LOAD relevant BC details from ADR_CONTEXT for affected_bcs
  LOAD relevant NFRs, RSK-XX, ASM-XX for this category
  LOAD tech stack recommendation from ADR_INDEX.technology_eval
  DETERMINE technology_subject (which tech this ADR decides on)

  IF MODE == REPAIR AND no REPAIR_DIRECTIVE targets this ADR:
    SKIP. CONTINUE to next ADR.

  ## Zero Invention Checkpoint
  Context forces MUST derive from ADR_CONTEXT data.
  Alternatives MUST be real options (from tech eval, context packs, industry knowledge).
  Missing info → document as engineering_assumption, not as fact.

  ## Generate agent-native structured ADR
  ## Uses structured template from phase-b-adr-generation.md:
  ## all sections are tables and key-value pairs, NOT prose paragraphs.
  GENERATE ADR content using structured template.

  ## Pattern 6: Source Fidelity Check (BEFORE writing)
  SCAN for:
    a. Technology names outside decision/alternatives/compliance of THIS ADR → VIOLATION
    b. BC-XX references not in ADR_CONTEXT.bounded_contexts → hallucination
    c. NFR/FR IDs not in ADR_CONTEXT → hallucination
    d. Fewer than 2 alternatives → add from tech eval
    e. Prose paragraph where a table row would work → convert to table
  IF violations → correct before writing. Log corrections.

  ## Pattern 1: Write-Flush-Forget
  ## AFTER EACH ADR — NON-NEGOTIABLE, IN THIS ORDER (see AP-001, AP-002, KFM-002).
  ## These are three separate tool calls per ADR. Do NOT batch them across ADRs and
  ## do NOT skip the checkpoint — a crash with no checkpoint is unrecoverable.
  1. WRITE adrs/adr-{NNN}-{slug}.md — MANDATORY TOOL CALL.
  2. VERIFY the file now exists and is non-empty. If not, STOP and re-write it.
     Only after this verification may {ADR_ID} be considered done.
  3. UPDATE ADR_INDEX.completed_adrs[ADR_ID] with metadata + cross_ref_map[ADR_ID].
  4. UPDATE 00-index.md: replace this row's "⬜ TO BE GENERATED" with "✅ COMPLETE"
     and set its File cell to the real path. Flip ONLY this ADR's row, ONLY now that
     step 2 verified the file — never ahead of the write, never for other ADRs.
  5. WRITE _checkpoint.json with current ADR_INDEX state — MANDATORY TOOL CALL every
     iteration. This is the sole durable resume point if the run crashes next.
  6. FLUSH all ADR text from memory. Only ADR_INDEX survives.

  LOG: "{ADR_ID} complete. Progress: {completed}/{total}."
  Do NOT stop. Process ALL ADRs in REMAINING_ADRS. Continue until all are written.

## Loop Completion Gate
CHUNK_DONE = (len(REMAINING_ADRS) == 0)
ALL_DONE   = (len(ADR_INDEX.completed_adrs) == TOTAL_ADRS)

IF CHUNK_DONE AND NOT ALL_DONE:
  NEXT_RESUME = len(ADR_INDEX.completed_adrs)
  LOG "Chunk complete. Re-invoke with resume_from_adr={NEXT_RESUME}."
  ADR_INDEX.phase_status.B = "PARTIAL"
  EXIT. Do NOT proceed to Step 5.

IF ALL_DONE:
  ## Category Coverage Check
  covered = set of categories from ADR_INDEX.completed_adrs
  required = categories selected into ADR_INDEX.decisions during Step 2
  missing = required - covered
  IF missing:
    LOG "Missing categories: {missing}. Generating supplementary ADRs."
    FOR EACH missing_category:
      Generate supplementary ADR → write → flush → update index.
      Do NOT stop. Process ALL missing categories.

  ADR_INDEX.phase_status.B = "COMPLETE"
  LOG "Phase B complete. {total} ADRs generated."
  PROCEED to Step 5.
```

### Step 5: Phase C — Manifest Assembly

Read `references/phase-c-manifest-assembly.md` before executing this step.

**Command:**
```
## Entry Guard
ADR_INDEX.phase_status.B MUST be "COMPLETE". If not → EXIT.

IF MODE == REPAIR AND REPAIR_DIRECTIVES target "manifest" or "global":
  Regenerate manifest.
ELSE IF MODE == REPAIR AND no directive targets manifest:
  SKIP (manifest preserved).

GENERATE ADR-SPEC-{SESSION_ID}.md manifest following reference file structure.
Manifest sections: tech_stack_evaluation, adr_catalog, cross_reference_map,
impact_matrix, bc_coverage, nfr_coverage, category_coverage, risk_coverage,
assumption_coverage, validations, open_questions, engineering_assumptions.

## Quality Validation Gate (before writing)
1. All sections populated (no empty stubs)
2. Cross-reference integrity: ADR IDs match across sections
3. Count verification: VERIFY stated_count == actual_count for each metric
   IF mismatch → fix stated_count before writing
4. Status protocol: every item has status (complete | pending | assumption)
5. Anti-fade: last section depth matches first section depth (+/-20%)

WRITE ADR-SPEC-{SESSION_ID}.md — MANDATORY TOOL CALL.
VERIFY file exists and is non-empty.
FLUSH manifest text from memory.
ADR_INDEX.phase_status.C = "COMPLETE"
LOG: "Step 5 COMPLETE. Manifest written."
```

### Step 6: Finalize — Audit & Session End

Read `references/phase-d-validation-audit.md` before executing this step.

**Command:**
```
## Write ADR-AUDIT-{SESSION_ID}.md
Generate audit file following reference file template:
sources table, generation_log, chunk_execution_log (if used),
validation_summary, change_log (REPAIR only).

WRITE ADR-AUDIT-{SESSION_ID}.md — MANDATORY TOOL CALL.

## Output Verification (mandatory before exit)
1. CONFIRM manifest (ADR-SPEC-*.md) exists and is non-empty
2. CONFIRM all expected ADR files in adrs/ present (count matches TOTAL_ADRS)
3. CONFIRM audit file exists
4. TRACKER RECONCILIATION (see KFM-001, AP-001): count ✅ COMPLETE rows in
   00-index.md and count adr-*.md files actually on disk. These two counts AND
   TOTAL_ADRS MUST all be equal. If 00-index.md marks any ADR ✅ whose file is
   absent (or leaves ⬜ for a file that exists), the tracker is lying — REBUILD
   00-index.md from disk (✅ only for files present non-empty) before exit.
IF any expected ADR file is missing → regenerate it before completing (do NOT
   just flip its tracker row).

## Clean up checkpoint
DELETE _checkpoint.json (manifest is now the source of truth)

## Memory Bank — MANDATORY session-end writes
1. Overwrite context-pack/active-context.md with session status, decisions, blockers,
   key artifacts (see execution-protocol.md Section 4 for schema).
2. Append one milestone row to context-pack/progress.md with artifact count.

Memory Bank artifact type: "{N} ADRs" (e.g., "12 ADRs").

## LAST ACTION — MANDATORY
Update _progress.json status to COMPLETED with completed_at timestamp.
If the session failed, set status to FAILED instead.

## Harness Output Sidecar - MANDATORY
When the prompt includes `output_file = '<path>'`, write that exact JSON file as the final file write before final_response:
  { "adrs_path": "<resolved adrs_path>" }
Use the resolved output folder that contains `ADR-SPEC-*.md`, `ADR-AUDIT-*.md`, `00-index.md`, and `adrs/`. Do not emit final_response until this sidecar exists.
LOG: "Step 6 COMPLETE. Session {SESSION_ID} done. {TOTAL_ADRS} ADRs generated."
```

## Reference Files

- `references/phase-a-tech-stack-evaluation.md` — Evaluation matrix, scoring criteria, TCO analysis, governance constraints
- `references/phase-b-adr-generation.md` — Agent-native structured ADR template, PlantUML rules, diagram/Gherkin generation, per-ADR fidelity checks
- `references/phase-c-manifest-assembly.md` — Manifest section structure, coverage tables, cross-reference assembly, validation gates
- `references/phase-d-validation-audit.md` — Audit file template, output verification, count verification, anti-fade check

## Required Tools

- **coda-cli** (`^1.0.0`): operation `generate-documentation`
- **meeting-transcription** (`^1.0.0`): operation `transcribe`

## Rendering

For human-readable output, use `humanize-spec` with the `adrs` rendering profile.
