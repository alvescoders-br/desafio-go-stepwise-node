---
name: researching-prd
description: >
  Synthesizes agent-consumable PRD specs from project briefs and research inputs.
  Output is a single strict-markdown file with zero prose — structured sections
  containing only IDs, acceptance criteria, constraints, targets, and traceability.
  All unresolved items consolidated in a single `open_questions` registry.
  Enforces Zero Invention Policy. SYNTHESIZE and REPAIR modes.
  Applies RPI workflow. FIC context discipline (Correct > Complete > Concise).
  Human-readable output generated on demand via `humanize-spec` skill (separate).
license: Proprietary
metadata:
  author: aipods-team
  version: 3.3.0
  category: product-management
  tags: product-definition, automated, agent-native
---

# Researching PRD — Agent-Native Spec

## Quick Start
Synthesize a structured, agent-consumable PRD from project brief and research inputs.
Output is a **single file**: `{prd_output_path}/PRD-SPEC-{SESSION_ID}.md`.
No prose. No narrative. No meeting agendas. Only structured data the implementing
agent needs to execute Research/Plan/Implement cycles.

## Known Failure Modes
<!-- ACCUMULATING — appended by calibrating-updates (WS6). Newest first. Rules MUST be generic/behavioral (project-agnostic); project-specific fixes go to context packs, never here. Format + entry rules: engineering-skills/references/known-failure-modes-format.md. Read these at pre-flight so a lesson learned once recurs no more. -->

## Anti-Patterns (do NOT)
<!-- ACCUMULATING — appended by calibrating-updates (WS6). One line each: **AP-NNN** (ISO-date, source: REC-NNN): prohibition — why. -->

## Output Architecture

```
{prd_output_path}/
├── PRD-SPEC-{SESSION_ID}.md     ← Single agent-native spec (all sections)
└── PRD-AUDIT-{SESSION_ID}.md    ← Session audit trail (metadata only)
```

**Why single file:** Output is one file because downstream consumers expect one path.
This does **NOT** mean the spec is generated in a single inference call. This skill
applies the **section-shape protocol** defined in `context-pack/execution-protocol.md`
Section 10: skeleton-first + one-section-per-write + source extraction + CONTINUE
on re-entry. The skill-specific contract below (section list, dependency graph,
extraction schema) plugs into that protocol; the tool discipline (use `Write` for
skeleton, `Edit` for sections, never `Bash` heredoc mutations) lives in Section 10.

**Human-readable output:** Not produced by this skill. Use `humanize-spec` skill
to generate rich PRD from this spec on demand.

## Parameters
| Name | Type | Required | Notes |
|------|------|----------|-------|
| project_brief_path | string | Yes | |
| meeting_recording_path | string | No | |
| transcript_output_path | string | No | |
| prd_template_path | string | No | |
| legacy_docs_path | string | No | Folder produced by `legacy-insights` (knowledge graph, `documentation-final.md`, `analysis-report.md`, diagrams). Present only for **modernization** engagements — absent for greenfield. When set and the folder exists, read the legacy docs as a primary input alongside the project brief. |
| prd_output_path | string | Yes | |
| failure_feedback | string | No | |

**If any Required parameter is not defined, ABORT EXECUTION.**
**Optional-path graceful handling:** if `legacy_docs_path` (or any other optional path) is set but the folder/file does not exist on disk, treat it as absent — do NOT abort. Log the fact in SOURCE_LOG so the mode (greenfield vs modernization) is traceable in the audit.

## Workflow

### Step 1: Initialize

**Command:**
```
# PRD Agent — Agent-Native Spec Generator
# Persona: Senior Product Manager & Technical Business Analyst
# CRITICAL: NON-INTERACTIVE SESSION.
# MISSION: Extract structured spec data from unstructured inputs. Zero invention.

IF failure_feedback NOT empty:
  MODE = REPAIR
  SPEC_FOLDER = resolve_parent_folder(prd_output_path)
  SPEC_FILE = find existing PRD-SPEC-*.md in SPEC_FOLDER
  IF not found → write Gap Report → EXIT
  Load SPEC_FILE → PREVIOUS_SPEC → SOURCE_LOG
  PREVIOUS_VERSION = extract version
  NEW_VERSION = increment patch
  Parse failure_feedback → REPAIR_DIRECTIVES [{ section, instruction, reason }]
ELSE:
  MODE = SYNTHESIZE
  SPEC_FOLDER = prd_output_path + '/'
  SPEC_FILE = SPEC_FOLDER + 'PRD-SPEC-' + SESSION_ID + '.md'
  NEW_VERSION = "1.0.0"
  mkdir -p SPEC_FOLDER

  ## SESSION_ID goes in spec FILENAMES only — never in the folder name.
  ## The folder must match the capability YAML path parameter exactly.

SOURCE_LOG = []
CHANGE_LOG = []
```

**FIRST ACTION — MANDATORY:** Write `_progress.json` to SPEC_FOLDER before any other file write.
This prevents the orchestrator from sending SIGINT.

```json
{ "skill": "researching-prd", "session_id": "<SESSION_ID>",
  "status": "RUNNING", "started_at": "<ISO timestamp>", "completed_at": null,
  "skeleton_written": false,
  "sections": {
    "scope": "pending", "personas": "pending",
    "functional_requirements": "pending", "non_functional_requirements": "pending",
    "kpis": "pending", "jtbd": "pending", "traceability": "pending",
    "dependencies": "pending", "risks": "pending", "assumptions": "pending",
    "constraints": "pending", "mvp_phasing": "pending", "literal_registry": "pending", "glossary": "pending",
    "open_questions": "pending"
  } }
```

This is the **section-shape** `_progress.json` variant — see execution-protocol.md
Section 10.1 for the schema and Section 10.6 for CONTINUE-on-re-entry semantics.

Memory Bank artifact type: `"{N} requirements"` (e.g., `"24 requirements"`).

**Memory Bank — MANDATORY session-end writes:**
1. Overwrite `context-pack/active-context.md` with session status, decisions, blockers, key artifacts (see execution-protocol.md Section 4 for schema).
2. Append one milestone row to `context-pack/progress.md` with artifact count above.

**LAST ACTION — MANDATORY:** Update `_progress.json` status to `COMPLETED` with `completed_at` timestamp.
If the session failed, set status to `FAILED` instead.

## Zero Invention Policy
Not in source → status: pending. Never infer, assume, or create information.
Inferred industry standards → status: assumption (with ASM-XX ID).

## Internal Reasoning: ALL in English regardless of output language.
```
**Execution:** automated

### Step 1.5: Input Validation Gate

**Command:**
```
REQUIRED = {
  "Project Brief": "Problem statement, target users, 2+ features/requirements.",
  "Minimum Scope": "Sufficient to generate 3+ functional requirements."
}
IF any required input missing → write Gap Report to SPEC_FILE → EXIT
```
**Execution:** automated

### Step 2: Input Synthesis

> **During input synthesis — apply execution-protocol.md Section 12 (Delegated Exploration) if your harness supports it.** Broad read-only sweeps for this skill (e.g. sweeping the brief plus research inputs to find which artifacts cover each requirement, locating conflicting or duplicate source statements) MAY be delegated to a read-only exploration subagent on a cheap/fast model, which returns conclusions + source pointers (not file dumps). Synthesis, requirement framing, and all writing stay with this agent, which verifies any delegated pointer before using it (Zero-Invention still applies). With no subagent capability, explore inline under the usual scope constraint — output quality is identical either way.

**Command:**
```
Initialize REFERENCE_MAP = []
ENGAGEMENT_MODE = "greenfield"    # default; flipped by the triggers below

FOR EACH source in [project_brief_path, prd_template_path]:
  IF exists: Read → SOURCE_LOG → extract all requirements → REFERENCE_MAP

IF transcript_output_path exists:
  FOR EACH transcript: SOURCE_LOG → extract pain points/features → REFERENCE_MAP

## Engagement-Mode Detection (runs BEFORE the legacy-docs check)
##
## Greenfield is the default ONLY when no brownfield/modernization signal is
## found. The heuristic scans the project brief and every context-pack file
## already loaded into the agent context. Do NOT hardcode context-pack
## filenames here — iterate over the files that the harness surfaced in the
## system prompt at session start (capability.context_pack.required_files).
## If any trigger phrase matches, flip ENGAGEMENT_MODE to "brownfield"
## (the legacy-docs block below may further escalate it to "modernization").

BROWNFIELD_TRIGGER_PHRASES = [
  "current system", "current platform", "current application", "current product",
  "existing system", "existing platform", "existing application", "existing product",
  "add a feature to", "new feature on top of",
  "modernization", "modernisation",
  "enhancement to", "extend the existing",
  "brownfield", "legacy system", "legacy platform"
]

SOURCES_TO_SCAN = [project_brief_path] +
                  <context-pack files surfaced in the system prompt at
                   session start (loaded by the harness)>
FOR EACH src in SOURCES_TO_SCAN:
  IF NOT exists(src): continue
  text = read(src).lower()
  FOR phrase in BROWNFIELD_TRIGGER_PHRASES:
    IF phrase in text:
      ENGAGEMENT_MODE = "brownfield"
      LOG to SOURCE_LOG:
        "Engagement-mode flipped to 'brownfield' — trigger '" + phrase +
        "' matched in " + src
      break_both_loops

## Legacy-insights ingestion (modernization engagements only)
IF legacy_docs_path set AND directory exists:
  ENGAGEMENT_MODE = "modernization"    # supersedes brownfield when legacy docs exist
  LOG to SOURCE_LOG: "Modernization engagement — reading legacy-insights from {legacy_docs_path}"

  ## Prefer the final, human-reviewed documentation. Fall back to the draft when final
  ## is missing (legacy-insights still running or skipped the refinement phase).
  LEGACY_DOC = first_existing([
    legacy_docs_path + '/documentation-final.md',
    legacy_docs_path + '/documentation-draft.md'
  ])
  IF LEGACY_DOC:
    Read LEGACY_DOC → SOURCE_LOG (tag: "legacy:doc")
    Extract → REFERENCE_MAP:
      - Business rules and calculation logic (evidence for FR acceptance criteria)
      - Domain terminology and entity names (use verbatim — do not paraphrase)
      - Constraints inherited from the legacy system (feed into NFR candidates)
      - Behavior that MUST be preserved in the new system (tag as PRESERVE-XX)
      - Behavior identified as legacy-specific / to be dropped (tag as DEPRECATE-XX)

  ## Analysis report (optional — carries structured gaps and assumptions from legacy-insights).
  IF exists(legacy_docs_path + '/analysis-report.md'):
    Read → SOURCE_LOG (tag: "legacy:analysis")
    Extract open questions and assumptions → register under open_questions with source
    tag "legacy-insights.analysis-report" so the provenance is traceable back.

  ## Diagrams folder (optional — referenced, not parsed).
  IF exists(legacy_docs_path + '/diagrams/'):
    Record folder path in SOURCE_LOG for PRD to cross-reference visuals; do NOT inline them.

ELSE:
  IF ENGAGEMENT_MODE == "brownfield":
    LOG to SOURCE_LOG: "Brownfield engagement — no legacy_docs_path provided; engagement detected from project-brief / context-pack trigger phrases"
  ELSE:
    LOG to SOURCE_LOG: "Greenfield engagement — no brownfield signals detected and no legacy_docs_path provided"

Detect language from input → DETECTED_LANGUAGE

IF MODE == REPAIR:
  Parse PREVIOUS_SPEC sections → identify repair targets
  Apply REPAIR_DIRECTIVES to REFERENCE_MAP

  ## Open-Question Resolution Pass (MANDATORY before regeneration)
  ##
  ## Reviewer feedback that arrives via failure_feedback may answer one or more
  ## OQ-XX entries that were emitted in the previous spec. Those entries MUST
  ## be converted into confirmed decisions and DELETED from open_questions[]
  ## before regeneration — otherwise the next quality gate will re-reject for the
  ## same "you keep asking what I already answered" reason.

  FOR EACH oq in PREVIOUS_SPEC.open_questions:
    FOR EACH directive in REPAIR_DIRECTIVES:
      ## Match by id reference in the directive text OR by semantic equivalence
      ## between the directive's instruction and oq.question.
      IF directive references oq.id OR
         directive.instruction semantically answers oq.question:
        decision = {
          id: derive_decision_id(oq.id),               # e.g. OQ-03 → DEC-03
          topic: oq.topic,
          decision: extract_answer(directive.instruction),
          source: "reviewer-feedback@" + directive.timestamp,
          confidence: "confirmed"
        }
        REFERENCE_MAP.decisions_confirmed.append(decision)
        PREVIOUS_SPEC.open_questions.remove(oq)
        LOG to SOURCE_LOG:
          "OQ resolved by reviewer: " + oq.id + " → " + decision.id
        break

  ## After the pass, only genuinely unresolved questions remain in open_questions.
  ## The regenerated spec MUST NOT re-emit a question with the same topic as any
  ## entry in decisions_confirmed (see Zero Re-Ask Rule in Step 3).
```
**Execution:** automated

**Modernization-specific rules (apply only when ENGAGEMENT_MODE == "modernization"):**

1. **Zero Invention still wins.** Legacy docs are a source like any other — a business rule must appear in `documentation-final.md`, the project brief, or a transcript to make it into an FR with `status: complete`. Inferred rules remain `status: assumption` with ASM-XX IDs.
2. **Preserve vs. deprecate.** Every PRESERVE-XX behavior extracted from the legacy docs MUST be represented as an FR (or explicit NFR) in the PRD. Every DEPRECATE-XX must appear in the "Out of scope" / "Not in scope" section with the legacy-behavior ID so reviewers can audit what was intentionally dropped.
3. **Terminology fidelity.** When the legacy docs name a concept (e.g., "loan term", "amortization schedule"), reuse that exact term in FR titles and acceptance criteria. Renames belong in a glossary entry tagged `rename: {legacy_term} → {new_term}` so the traceability is explicit.
4. **Audit footprint.** The PRD-AUDIT must record `engagement_mode: {greenfield|brownfield|modernization}` plus, for non-greenfield modes, the trigger phrases and/or legacy source files consumed, so downstream capabilities (software-architecture, code-development) can verify the engagement context was actually used.

### Step 2.5: Source Extraction Pass

**Apply execution-protocol.md Section 10.2** (trigger thresholds, mechanism, REPAIR reuse, audit). This step provides the PRD-specific extraction schema — everything else is in Section 10.2.

**Schema for each `_extractions/{name}.md` file** (omit empty sections):

```
functional_requirements:
  - statement: {verbatim or near-verbatim} | line: {N} | priority_hint: {if present}
business_rules:
  - rule: {verbatim} | line: {N}
non_functional_hints:
  - hint: {what + measurable target if stated} | line: {N}
jtbd_signals:
  - who: {role} | what: {goal} | why: {motivation} | line: {N}
kpis:
  - metric: {name} | target: {value if stated, else [PENDING]} | line: {N}
risks:
  - risk: {statement} | likelihood_hint: {if present} | line: {N}
terminology:
  - term: {name} | definition: {from source} | line: {N}
personas:
  - role: {name} | attributes: {bullet list} | line: {N}
constraints:
  - constraint: {statement} | type: {regulatory|organizational|technical} | line: {N}
preserve_behaviors (modernization only):
  - behavior: {statement} | line: {N} | tag: PRESERVE-XX
deprecate_behaviors (modernization only):
  - behavior: {statement} | line: {N} | tag: DEPRECATE-XX
```

The PRD-AUDIT must list extraction files alongside raw sources so the provenance chain is complete: `raw_source -> extraction -> spec_item`.

**Execution:** automated

### Step 3: Generate Agent-Native Spec

**Pattern Reuse Search (MANDATORY before proposing new components / integrations / capabilities / FRs that imply system behavior):**

Before adding any candidate that names or implies a system component (e.g., a scheduler, a sync job, a worker, a runtime, a delivery surface), the agent MUST search the context-pack for an existing pattern that solves the same problem. Inventing a new pattern when one is documented in the context-pack is a protocol violation.

```
CP_FILES = <context-pack files surfaced in the system prompt at
            session start (loaded by the harness)>

FOR EACH proposed in candidate_components:
  search_terms = derive_search_terms(proposed)   # nouns + stems from name/purpose
  matched = false
  FOR EACH file in CP_FILES:
    IF exists(file):
      hits = grep_case_insensitive(file, search_terms)
      IF hits:
        proposed.pattern_source = file + "#" + hits[0].line
        proposed.classification = "reuse"
        record_in_audit:
          "Pattern reuse: '" + proposed.name + "' grounded in " + file
        matched = true; break
  IF NOT matched:
    proposed.classification = "new"
    record_in_audit:
      "Pattern reuse search: no existing pattern for '" + proposed.name +
      "'. Searched " + len(CP_FILES) + " context-pack files."

## Reuse-classified items MUST reference pattern_source verbatim downstream
## (do NOT rename or paraphrase the existing pattern in FR titles / glossary).
```

**Apply execution-protocol.md Section 10** — Phase A (skeleton-first) then Phase B (one section per `Edit` call). Tool discipline (Section 10.5) is **mandatory**: skeleton via `Write`, sections via `Edit`, NEVER `Bash + sed/python3/awk` to mutate SPEC_FILE. NEVER fall back to bulk rewriting when one `Edit` fails — fix the `Edit` call instead.

**Resume Discipline (CONTINUE/REPAIR re-entry) — MANDATORY:**

If `_progress.json` exists on disk with `skeleton_written: true` and any `sections.{name}: complete`, this is a re-entry. Apply execution-protocol.md §10.6 verbatim:

1. Read `_progress.json` first — nothing else.
2. Pick the first `pending` section in template order — call it `N`.
3. Read SPEC_FILE once.
4. For section `N` ONLY, load the `_extractions/*.md` files whose schema contains entries this section consumes (use the extraction-to-section map below). Then `Edit` SPEC_FILE for section `N`. Then update `_progress.json`. Then drop and advance.

**Do NOT** open every `_extractions/*.md` file on entry. **Do NOT** compose a `think` block planning all remaining sections. **Do NOT** re-run Step 2 / Step 2.5 — extractions and SOURCE_LOG are already on disk. The prior run already paid for those reads; reading them again is the failure mode §10.4.1 and §10.6 exist to prevent.

**Extraction → section map** (load only these files for each section iteration):

| Section | Extraction schemas to load |
|---------|-----------------------------|
| `scope` | `functional_requirements`, `constraints` from project-brief extraction |
| `personas` | `personas`, `jtbd_signals` |
| `functional_requirements` | `functional_requirements`, `business_rules`, `preserve_behaviors` |
| `non_functional_requirements` | `non_functional_hints`, `constraints` (`type: technical|regulatory`) |
| `kpis` | `kpis` |
| `jtbd` | `jtbd_signals` |
| `traceability` | SPEC_FILE cross-section (FR + JTBD) — no extraction read |
| `dependencies` | `non_functional_hints`, `constraints` (`type: organizational|technical`) |
| `risks` | `risks` |
| `assumptions` | SPEC_FILE cross-section (consolidate ASM-XX) — no extraction read |
| `constraints` | `constraints` |
| `mvp_phasing` | SPEC_FILE cross-section (FR priority) — no extraction read |
| `literal_registry` | `terminology`, `functional_requirements`, `business_rules`, `constraints` + SPEC_FILE cross-section |
| `glossary` | `terminology` + SPEC_FILE cross-section |
| `open_questions` | SPEC_FILE cross-section (consolidate pending/orphan/ASM-XX) — no extraction read |

If an extraction file does not contain entries for the section's schema, do NOT open it for that section.

**Skeleton stub text — must be ASCII:**

> `status: pending - will be generated`

ASCII hyphen (U+002D), not em dash. Non-ASCII characters in the stub create encoding traps if anything later reads or matches the stub via shell tools.

**Section list (template order):**

```
scope -> personas -> functional_requirements -> non_functional_requirements ->
kpis -> jtbd -> traceability -> dependencies -> risks -> assumptions ->
constraints -> mvp_phasing -> literal_registry -> glossary -> open_questions
```

**Cross-section dependency graph** (which sections read SPEC_FILE for prior state, per Section 10.4 step 1):

| Section | Reads from SPEC_FILE |
|---------|----------------------|
| `traceability` | `functional_requirements` + `jtbd` |
| `assumptions` | ALL prior populated sections (consolidates ASM-XX entries) |
| `mvp_phasing` | `functional_requirements` |
| `literal_registry` | ALL prior populated sections (extracts exact source-backed literals, enum members, ranges, IDs, route strings, field names, and positive/negative constraints) |
| `glossary` | ALL prior populated sections (consolidates terms; also reads `terminology` from extractions) |
| `open_questions` | ALL prior populated sections (consolidates PI-XX / TG-XX / ASM-XX) |
| all other sections | none — extraction inputs are sufficient |

**Zero Re-Ask Rule (REPAIR mode):**
Before emitting an entry into `open_questions`, check `REFERENCE_MAP.decisions_confirmed[]`
(populated by the Step 2 Open-Question Resolution Pass). If any confirmed decision shares
the same topic, FR-ID, NFR-ID, or line anchor as the candidate question, DO NOT emit the
question — use the decision instead. Re-emitting a question the reviewer already answered
is a protocol violation.

Read `references/spec-template.md` for section structure.

Generate the complete spec following the template. Apply these rules to ALL sections:

**Structured Contract Rule:**
Native PRDs emitted by this skill declare `contract_format: structured`, use
globally stable AC IDs (`FR-XX-AC-YY`), include a typed `literal_registry`, and
emit enriched `open_questions` with `affected_ids`, `blocking`, and
`fallback_behavior`. Source references must use stable section/ID anchors instead
of line numbers.

**Status Protocol:**
- Every item has a `status` field: `complete`, `pending`, or `assumption`
- `complete`: all fields populated from source evidence
- `pending`: one or more fields missing → item also registered in `open_questions`
- `assumption`: inferred from industry standard → ASM-XX ID assigned

**Source Tagging:**
- Every item has a `source` field pointing to REFERENCE_MAP entry
- No source → status MUST be `pending` or `assumption`

**Consolidation Rules (FRs):**
- Group trivially similar FRs (same JTBD, same source, differ by variant) as sub-items
- Otherwise unique IDs: FR-01, FR-02, etc.

**NFR Targets:**
- MUST be numeric/measurable. "Fast" or "Secure" → status: pending
- Inferred targets → append ASM-XX ID

**Acceptance Criteria:**
- Extract ONLY from source evidence
- Format: `given: / when: / then:` (structured, no prose)
- Missing → status: pending, registered in open_questions

**Traceability Table:**
- Bidirectional: FR→JTBD (forward) and JTBD→FR (reverse)
- status: `mapped` or `orphan` or `unsatisfied`
- Every non-mapped entry → registered in open_questions

**Bias Detection (apply during generation):**
- Technology names not in sources → reframe as capability need
- Architecture decisions without source evidence → flag as assumption
- Implementation details in FRs → extract to notes, keep FR behavioral

**Execution:** automated

### Step 4: Quality Validation Gate

**Reads SPEC_FILE from disk, section by section.** Phase B flushed per-section content
from working memory by design — do not assume in-memory state. Each check below is a
targeted disk read of the section(s) it covers. If a correction is needed, edit SPEC_FILE
in place (one section per Edit call, same discipline as Phase B).

**Command:**
```
1. Source Fidelity: Every FR/NFR has a source or is marked pending/assumption
2. Zero Invention: No item with status:complete lacks source evidence
3. Traceability: Every FR maps to a JTBD or is flagged orphan in open_questions
4. NFR Targets: All numeric or pending. No qualitative targets allowed
5. Acceptance Criteria: Every FR has ≥1 AC or is registered in open_questions
6. Bias Check: No technology names, vendor names, or implementation details
   not explicitly in sources
7. open_questions: Every pending/orphan/assumption item appears exactly once
8. ID Consistency: No duplicate IDs, no gaps in numbering
9. Structured Contract: `contract_format: structured` present, AC IDs use
   `FR-XX-AC-YY`, open_questions use enriched columns, and every source-backed
   literal in requirements/ACs/constraints appears in `literal_registry`.
10. Hash Contract: `content_hash` is sha256 over canonical PRD-SPEC content with
    the `content_hash:` line omitted. Do not use mtime.

IF corrections needed → apply in place, log to CHANGE_LOG
```
**Execution:** automated

### Step 5: Write Outputs

**Command:**
```
1. Write SPEC_FILE (PRD-SPEC-{SESSION_ID}.md) inside SPEC_FOLDER.
   - Set the SPEC front-matter `version:` to NEW_VERSION. On REPAIR this MUST be the
     incremented patch (Step 1: PREVIOUS_VERSION → NEW_VERSION) — editing the content
     in place without bumping `version` is a §7 violation. See execution-protocol §7.2 step 8.
2. Write AUDIT_FILE (PRD-AUDIT-{SESSION_ID}.md) inside SPEC_FOLDER:
   - Session metadata (version=NEW_VERSION, mode, session_id, timestamp, language)
   - Sources referenced (numbered list from SOURCE_LOG)
   - Decisions made (from CHANGE_LOG)
   - Summary counts: FRs, NFRs, JTBDs, KPIs, open_questions
   - Structured contract validation result and final `content_hash`
   - REPAIR-only: set `mode: REPAIR` and APPEND (do not overwrite) a `## Repair History`
     entry — version, timestamp, directives_applied, sections_changed, sections_preserved,
     repair_delta (per execution-protocol §7.2 step 8).
3. REPAIR self-check (execution-protocol §7.2 step 9): before final_response, confirm the
   SPEC `version` is strictly greater than PREVIOUS_VERSION AND the AUDIT has the new
   `## Repair History` entry. If not, fix the bookkeeping now — do not finish.
4. Verify EXACTLY 2 files exist inside SPEC_FOLDER and are non-empty
5. Verify files are INSIDE SPEC_FOLDER (the session-scoped subfolder),
   NOT at the parent output_folder level. If files were written to the
   wrong location, move them into SPEC_FOLDER before completing.

VIOLATION: Writing PRD-SPEC or PRD-AUDIT outside of SPEC_FOLDER
(e.g., directly in the outputs root) breaks the folder naming contract.
Downstream capabilities expect files inside {prd_output_path}/.

Ready for downstream consumption (Epics, Architecture, Implementation).
```
**Execution:** automated

### Step 6: Emit Harness Outputs Sidecar

**Apply execution-protocol.md Section 11.** Mandatory when the prompt contains a `## Run metadata` block (Stepwise invocation); skip otherwise (standalone invocation).

**Output parameters this skill produces** (one key per row of the prompt's `## Output parameters` table):

- `prd_output_path`: the resolved `prd_output_path` parameter — the SPEC_FOLDER you wrote into in Steps 1–5.

**Example sidecar contents** (values illustrative):

```json
{ "prd_output_path": "/abs/path/to/artifacts/outputs/<capability>/prd" }
```

**Execution:** automated

## Agentic-First Output Contract — No Calendar Time

PRD artifacts are agentic-first: they are consumed by downstream AI agents, not human project managers. Do NOT include calendar-time references in any generated content.

**PROHIBITED in all PRD output:**
- Week numbers or ranges (e.g., "Weeks 1-4", "Week 3")
- Month names or numbers (e.g., "Month 2", "Q1")
- Calendar dates (e.g., "by March", "2026-06-01")
- Sprint numbers tied to calendar (e.g., "Sprint 3" = "3 weeks")
- Duration estimates in calendar units (e.g., "4-6 weeks", "2 months")

**USE INSTEAD:**
- Phase identifiers: Phase 0, Phase 1, Phase 2
- Priority tiers: Must Have, Should Have, Could Have, Won't Have
- Epic dependency ordering: EPIC-01 before EPIC-02
- Relative sequencing: "before production", "after Phase 0 gate passes"

VIOLATION: Any week/month/date reference in PRD output is a format violation. Apply auto-correct: replace with phase name or priority tier.

## Common Rationalizations

| Excuse | Why It Fails | Counter |
|--------|-------------|---------|
| "The brief is vague, so I'll fill in the gaps with reasonable assumptions" | Inventing requirements violates the Zero Invention Policy. Assumptions become facts downstream. | Mark unknowns as `status: assumption` with ASM-XX IDs. Never present assumptions as confirmed requirements. |
| "The stakeholder will clarify later, I'll put a placeholder" | Placeholders propagate as literal text into epics and stories. Downstream agents treat them as requirements. | Use `status: pending` with explicit open_questions. Pending items are visible; placeholders are invisible traps. |
| "This NFR is obvious, everyone knows it should be secure/performant" | Obvious NFRs without measurable targets are unverifiable. "Secure" means nothing without criteria. | Every NFR needs: metric, target value, measurement method. "Secure" → "OWASP Top 10 compliance verified by SAST scan." |
| "I'll add more detail in the epics phase" | PRD is the single source of truth for requirements. Epics decompose; they don't invent. | If it's a requirement, it belongs in the PRD. If it's a decomposition detail, it belongs in epics. Don't defer requirements. |
| "The brief already covers this, I'm just reformatting" | Reformatting without validation propagates errors. The PRD must verify, not just transcribe. | Cross-reference every requirement against the brief. Flag contradictions. Verify completeness against JTBD framework. |
| "The spec is small enough to generate in one inference call" | This was the original assumption. It produced a 1.3M-token prompt and a gateway 504 on a real engagement. Single-call generation does not scale with input size. | Always emit one section per Write/Edit call (Step 3 Phase B). The cost on small briefs is negligible; the cost on large ones is the difference between completing and timing out. |
| "I'll re-read the brief whenever I need to remember a fact" | Re-reading raw sources on every section is what causes the input-token explosion. 14 sections × full source re-read = the failure mode. | Read raw sources ONCE in Step 2. Distill to `_extractions/` in Step 2.5. Phase B reads extractions only. |

## Red Flags

Signs that this PRD spec is being generated superficially or incorrectly:

- FRs or NFRs have no acceptance criteria (unverifiable requirements)
- All items marked `status: complete` but no source tags present (untraced claims)
- Zero open_questions on a complex brief (indicates insufficient scrutiny)
- NFRs without measurable targets ("fast", "secure", "scalable" without numbers)
- Calendar dates or week numbers in output (violates Agentic-First Output Contract)
- Assumptions not tagged with ASM-XX IDs (invisible assumptions propagate as facts)
- FR count doesn't match brief scope (too few = missed requirements, too many = invented requirements)
- JTBDs missing or generic ("user wants to do things efficiently")

## Verification Checklist

Every item requires **evidence**, not assertion. "Seems right" is never sufficient.

- [ ] Every FR has acceptance criteria — Evidence: each FR entry contains testable conditions
- [ ] Every NFR has measurable target — Evidence: metric + target value + measurement method per NFR
- [ ] Zero Invention Policy respected — Evidence: every item traces to brief, meeting transcript, or research input via source tag
- [ ] All assumptions tagged — Evidence: ASM-XX IDs on every `status: assumption` item
- [ ] Open questions captured — Evidence: open_questions section addresses gaps found during synthesis
- [ ] Literal registry complete — Evidence: every source-backed literal/enum/range/route/constraint in FRs/NFRs/ACs appears in `literal_registry`
- [ ] Structured contract emitted — Evidence: `contract_format: structured`, global AC IDs, enriched open_questions, and sha256 `content_hash`
- [ ] No calendar references — Evidence: grep for week/month/date patterns returns zero matches
- [ ] JTBD framework applied — Evidence: at least one Job-To-Be-Done per major user segment
- [ ] Spec validates against template — Evidence: all required sections from references/spec-template.md present

## Reference Files
- `references/spec-template.md` — Agent-native spec structure

## Required Tools
- **meeting-transcription** (`^1.0.0`): operation `transcribe`
