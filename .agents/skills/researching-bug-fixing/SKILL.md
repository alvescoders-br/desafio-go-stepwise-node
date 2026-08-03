---
name: researching-bug-fixing
description: >
  Bug-fix research phase. Analyzes a bug ticket and existing source code to produce
  a single agent-native research spec with zero prose — structured root cause analysis,
  impact assessment, fix approach, acceptance criteria, and test strategy.
  All unresolved items in unified open_questions. Lightweight alternative to
  researching-code-design. Downstream consumer: planning-code-tasks (TASK mode).
  Human-readable output via humanize-spec.
license: Proprietary
metadata:
  author: aipods-team
  version: 4.2.0
  category: engineering
  tags: bug-fix, research, defect, root-cause-analysis, FIC, RPI, agent-native, lightweight
---

# Researching Bug Fix — Agent-Native Spec

## SKILL PROTOCOL — ENTRY RULES (read first, do not skip)

1. **The protocol below is internally consistent.** If you perceive a conflict
   between the capability prompt and this skill, the skill wins for execution
   mechanics; the capability wins for paths/parameters. Do NOT exit citing
   "ambiguity" or "internal contradiction" — every section here has been
   tested in production runs.

2. **Begin Step 1 (Initialize) immediately.** Do NOT re-evaluate the protocol's
   completeness before starting. Step 1's first action (write `_progress.json`
   to `research_output_path`) IS the verification.

3. **Reference files load on demand via `cat`** when each step's `READ`
   pointer says so. They are NOT preloaded. The Reference Files table at the
   bottom of this file is a pointer index.

4. **Zero Invention Policy is non-negotiable.** Every factual claim MUST trace
   to the bug ticket or source code. Missing data → mark `status: pending` and
   register an open_questions entry. Inferred industry standards →
   `status: assumption` with an ASM-XX ID. Asking the human a clarifying
   question = task FAILURE — there is no human watching.

4a. **Host-codebase precondition — its absence is a BLOCKER, not a fillable gap.**
   This scope (bug-fixing) presumes an **existing application** at `source_path`.
   That host codebase is a *precondition* of the task, so Entry Rule #4's "missing
   data → mark pending" does NOT apply to the codebase itself. Before any
   discovery, verify `source_path` exists on disk AND actually contains the host
   application — not empty, not a stub: at minimum the application entry point and
   the component(s) on the bug's execution path are physically present. If
   `source_path` is absent/empty, or lacks the host application the ticket presumes,
   **STOP and escalate as a BLOCKER** (`stepwise session exec-fail` /
   `NEEDS_REPLAN`) naming the missing precondition. Do NOT proceed by marking the
   whole host codebase as `assumption`/`pending`, and do NOT synthesize a
   minimal/stub module — a research spec built on an absent host codebase is not
   "actionable for planning," it is a blocker. (Calibration: CalcService3 cdal-01
   — `./source` was absent; research proceeded on assumptions and implementation
   built a stub that passed code-review yet could not boot.)

5. **No final response until RESEARCH-SPEC + RESEARCH-AUDIT exist on disk.**
   Both files must exist at `research_output_path` and be non-empty before you
   emit a closing summary.

---

## Quick Start
Analyze a bug ticket and source code to produce a structured, agent-consumable
research spec for precise, safe bug fixing. Output is a **single file**:
`{research_output_path}/RESEARCH-SPEC-{SESSION_ID}.md`.
No prose. No narrative. Only structured data the implementing agent needs to
execute Research/Plan/Implement cycles.

## Known Failure Modes
<!-- ACCUMULATING — appended by calibrating-updates (WS6). Newest first. Rules MUST be generic/behavioral (project-agnostic); project-specific fixes go to context packs, never here. Format + entry rules: engineering-skills/references/known-failure-modes-format.md. Read these at pre-flight so a lesson learned once recurs no more. -->

## Anti-Patterns (do NOT)
<!-- ACCUMULATING — appended by calibrating-updates (WS6). One line each: **AP-NNN** (ISO-date, source: REC-NNN): prohibition — why. -->

## Output Architecture

```
{research_output_path}/
├── RESEARCH-SPEC-{SESSION_ID}.md     ← Single agent-native spec (all sections)
└── RESEARCH-AUDIT-{SESSION_ID}.md    ← Session audit trail (metadata only)
```

**Why single file:** Agent-native specs are 60-70% smaller than multi-document
research sets. No batching needed — the entire spec fits comfortably in context.
The Write-Flush-Forget protocol applies only if context exceeds 60% mid-generation
(unlikely with zero-prose output).

**Human-readable output:** Not produced by this skill. Use `humanize-spec` skill
to generate rich research report from this spec on demand.

**Pipeline Position:**

```
Bug Ticket (Jira / GitHub / file)
            ↓
  [Source Code Repository]  (strongly recommended)
            ↓
  [researching-bug-fixing]  ← YOU ARE HERE
            ↓
  [planning-code-tasks]     (TASK mode)
            ↓
  [implementing-code]
```

## Parameters
| Name | Type | Required | Description |
|------|------|----------|-------------|
| project_name | string | Yes | Project identifier |
| ticket_path | string | Yes | Path to bug ticket file (Markdown, JSON, or plain text) |
| source_path | string | Recommended | Path to source code repository |
| context_pack_path | string | No | Tech-policy, arch-standards, coding-standards |
| research_output_path | string | No | Output folder. When invoked via capability, the resolved path includes `feature_id` scope when set: `{output_folder}/{project_name}/{feature_id}/research-output`. Without `feature_id`: `{output_folder}/{project_name}/research-output`. Standalone default: `./research/` |
| failure_feedback | string | No | Present only in REPAIR mode — targeted fix directives |
| custom_message | string | No | Optional user instructions |
| research_depth | string | No | `targeted` (FAST_PATH) \| `standard` \| `deep`. Default = `targeted` for any ticket where TICKET_CONTEXT.affected_areas names a concrete class or file that can be resolved in the source tree. Auto-escalates to `standard` if the fast path yields insufficient root cause evidence. Use `deep` only for cross-cutting bugs (concurrency, performance, security regressions). |

**If any Required parameter is not defined, ABORT EXECUTION.**

## Workflow

### Step 1: Initialize

**Command:**
```
# Bug Fix Research Agent — Agent-Native Spec Generator
# Persona: Senior Defect Analyst & Root Cause Investigator
# CRITICAL: NON-INTERACTIVE SESSION.
# MISSION: Extract structured root cause analysis from ticket + source. Zero invention.

## SESSION_ID — generate own typed id; never inherit from execution metadata
PROJECT_NAME_UPPER = {project_name}.toUpperCase(), replace spaces with '_' (preserve existing hyphens)
YYYYMMDD = current date formatted as YYYYMMDD

IF failure_feedback NOT empty:
  MODE = REPAIR
  SPEC_FOLDER = research_output_path
  SCAN SPEC_FOLDER for existing RESEARCH-SPEC-*.md:
    IF found: SESSION_ID = extract from most recent filename (REPAIR continuity)
    ELSE: write Gap Report → EXIT
  SPEC_FILE = find existing RESEARCH-SPEC-*.md in SPEC_FOLDER
  Load SPEC_FILE → PREVIOUS_SPEC → SOURCE_LOG
  PREVIOUS_VERSION = extract version
  NEW_VERSION = increment patch
  Parse failure_feedback → REPAIR_DIRECTIVES [{ section, instruction, reason }]
ELSE:
  MODE = BUILD
  SESSION_ID = "BUGFIX-" + PROJECT_NAME_UPPER + "-" + YYYYMMDD
  SPEC_FOLDER = research_output_path
  SPEC_FILE = SPEC_FOLDER + '/RESEARCH-SPEC-' + SESSION_ID + '.md'
  NEW_VERSION = "1.0.0"
  mkdir -p SPEC_FOLDER

  ## EARLY SIGNAL — FIRST action after mkdir (MANDATORY)
  ## Section-shape variant — see execution-protocol.md §10.1 for schema and §10.6 for CONTINUE-on-re-entry.
  WRITE SPEC_FOLDER + '_progress.json':
    { "skill": "researching-bug-fixing", "session_id": "<SESSION_ID>",
      "status": "RUNNING", "started_at": "<ISO timestamp>", "completed_at": null,
      "skeleton_written": false,
      "sections": {
        "ticket_summary": "pending", "root_cause": "pending",
        "impact": "pending", "fix_approach": "pending",
        "acceptance_criteria": "pending", "test_strategy": "pending",
        "validations": "pending", "open_questions": "pending"
      } }
  ## Coordinator output-check finds _progress.json and will NOT send SIGINT.

SOURCE_LOG = []
CHANGE_LOG = []

## Memory Bank — Cross-Session Continuity
Read `_shared/references/memory-bank.md` for the full protocol.
At session start: read context-pack/active-context.md and progress.md.
Write active-context.md with status: STARTING (crash recovery).
Use prior session context to avoid re-discovering known blockers and respect prior decisions.

## Zero Invention Policy
Not in source → status: pending. Never infer, assume, or create information.
Inferred industry standards → status: assumption (with ASM-XX ID).

## Internal Reasoning: ALL in English regardless of output language.
```
**Execution:** automated

### Step 2: Input Loading

> **Before any discovery scan — apply execution-protocol.md Section 13 (Code-Location Discipline).** Read `context-pack/codebase-map.md` (and `project-inventory.md` if present) to locate the files on the bug's execution path BEFORE running a repository-wide `grep`/`glob`/`find` to discover where they live — **consult before scan, not never scan**. Read the specific files the map names directly; fall back to a scoped scan only where the map is absent or insufficient (finding every call site of a failing symbol often needs a real `grep` — allowed when the map cannot answer it), and flag that gap in the research output so the map can be corrected. Map first (§13), then delegate the residual sweep (§12).
>
> **During input loading — apply execution-protocol.md Section 12 (Delegated Exploration) if your harness supports it.** Broad read-only sweeps for this skill (e.g. locating the files on the bug's execution path, finding every call site of the failing symbol) MAY be delegated to a read-only exploration subagent on a cheap/fast model, which returns conclusions + `file:line` pointers (not file dumps). Synthesis, root-cause reasoning, and all writing stay with this agent, which verifies any delegated `file:line` before using it (Zero-Invention still applies). With no subagent capability, explore inline under the execution-path constraint — output quality is identical either way.

**Command:**
```
## STOP-GATE — Mandatory Inputs

REQUIRED = [
  { name: "Bug Ticket", path: ticket_path }
]

FOR EACH input IN REQUIRED:
  IF input.path is empty OR file does not exist:
    WRITE {SPEC_FOLDER}/RESEARCH-SPEC-GAP-REPORT.md:
      session_id: {SESSION_ID}
      status: BLOCKED
      reason: Missing bug ticket
      expected_at: {ticket_path}
      action: Provide a bug ticket file (Markdown, JSON, or plain text) and re-run.
    EXIT — Do not proceed.

## 2A. Load Bug Ticket → TICKET_CONTEXT

Read ticket_path completely. Extract:

TICKET_CONTEXT = {
  contract_mode:    # auto-detected: structured | partial | unstructured
  content_hash:     # sha256:<64 lowercase hex> if declared by ticket artifact; else N/A
  hash_status:      # match | mismatch_accepted | mismatch_blocked | not_verified | N/A
  id:             # Jira key (e.g., PROJ-1234), GitHub issue # or "N/A"
  title:          # Summary / title line
  severity:       # Critical / High / Medium / Low (infer if not stated)
  priority:       # P0-P4 (infer if not stated)
  reporter:       # Who reported (if present)
  environment:    # Environment details (browser, OS, version — if present)
  description:    # Full description text
  reproduction:   # Steps to reproduce (if present)
  expected:       # Expected behavior
  actual:         # Actual behavior
  ac:             # Acceptance criteria from ticket (may be empty)
  affected_areas: # Files, modules, endpoints mentioned
  labels:         # Tags / labels (if present)
  attachments:    # Logs, screenshots referenced (if present)
  literal_refs:    # LIT-XX references and exact values if present
  fallback_refs:   # pending input / assumption fallback IDs if present
  evidence_gaps:  # structured/prose discrepancies, invalid hashes, missing proof
}

# Zero Invention Policy: If a field is absent → set to "[Not provided in ticket]".
# Never infer reproduction steps or expected behavior that the ticket does not state.

Detect `contract_mode` automatically:
- `structured`: ticket declares `contract_format: structured`, globally scoped
  ticket/AC IDs, enriched open_questions if gaps exist, valid SHA-256 hashes for
  declared source fields, and upstream completeness is certified.
- `partial`: some structured fields exist, or a declared-structured ticket fails
  its own contract during WARN-mode rollout. Use available structured rows, but
  still derive IDs/literals/fallbacks from ticket prose as a cross-check.
- `unstructured`: no structured contract fields. This is valid for external
  tickets; use the current prose parsing behavior.

Hash format gate:
- Treat only `sha256:<64 lowercase hex chars>` as a valid hash value.
- Any field named `content_hash`, `*_source_hash`, or `source_hash` with a
  missing value, bare hash, mtime, session ID, filename, or placeholder is
  invalid for structured mode.
- Invalid hash fields demote the ticket to `partial`, require prose cross-check,
  and create an `evidence_gaps` row. Do not emit `hash_status: match` for a
  non-SHA value.

If upstream artifacts are loaded and a valid declared ticket hash mismatches,
forward-verify the ticket's recorded dependencies (IDs, literals, fallbacks). If
unchanged, proceed and log the acceptance in the audit only; never edit upstream
artifacts. If upstream files are not provided, set `hash_status: not_verified`
and do not block solely because verification is impossible.

Authentication security defaults:
- If the ticket touches auth, sessions, identity, OAuth, or password reset,
  persisted password-reset tokens are secrets and must be hashed at rest. Raw
  reset-token storage is an `evidence_gaps` row unless a binding upstream source
  explicitly requires it.
- OAuth provider values must come from an explicit allow-list before selecting
  provider columns, scopes, or identity fields. A fallback such as "non-google
  means github" is an `evidence_gaps` row.

## 2B. Load Source Code → SOURCE_CONTEXT (if available)

IF source_path exists:
  SOURCE_CONTEXT = {
    project_structure: directory tree (relevant areas only)
    affected_files:    files matching TICKET_CONTEXT.affected_areas
    execution_path_trace: entry point → call chain → error site
    existing_patterns: [pattern → file:lines] in affected area
    conventions:       naming, structure, error handling near affected files
    test_framework:    framework name, test commands, test conventions
    dependencies:      library → version from build file
  }

  ## 2B-0. FAST_PATH Resolution
  ##
  ## When the ticket names a concrete artifact, resolve it in one targeted pass and
  ## prune scope before any wider scan. This avoids reading the entire codebase
  ## just to confirm what the ticket already pointed at.
  ##
  ## ELIGIBILITY (all must be true to enter FAST_PATH):
  ##   - research_depth = "targeted" (or unset, with auto-detect heuristic below)
  ##   - TICKET_CONTEXT.affected_areas names ≥1 concrete class/file/symbol
  ##   - The named artifact resolves to ≤3 candidate files in the source tree
  ##   - REPAIR mode is OFF (REPAIR uses the previous research's scope)
  ##
  ## AUTO-DETECT (when research_depth is unset):
  ##   - LOW indicator (use targeted): ticket names a class with PascalCase identifier
  ##     OR a file path OR a method signature that grep finds in ≤3 files.
  ##   - HIGH indicator (use standard): ticket describes symptom only ("crash on
  ##     login"), or names a generic concept ("auth flow"), or affected_areas is empty.
  ##   - When in doubt, use standard.
  ##
  ## PROCEDURE (FAST_PATH):
  ##   1. Resolve each named artifact via grep/find. Limit to ≤3 candidates per name.
  ##      LOG: "FAST_PATH resolved {name} to {file}:{line}"
  ##   2. Build EXECUTION_PATH_FILES from:
  ##      - The resolved files
  ##      - Their direct callers (grep for class/method invocations, depth=1)
  ##      - Their direct dependencies (grep for the imports the resolved files use, depth=1)
  ##   3. Read EACH file in EXECUTION_PATH_FILES in full.
  ##   4. Skip the wider repository structure scan that "standard" mode performs.
  ##   5. Run section 2B-1 (Execution Path Constraint) on the FAST_PATH file set.
  ##
  ## ESCALATION (FAST_PATH → standard):
  ##   IF the resolved files do not contain a plausible root cause after a full read:
  ##     LOG: "FAST_PATH insufficient — escalating to standard depth."
  ##     SET research_depth = "standard"
  ##     CONTINUE with section 2B-1 (full execution path trace).
  ##
  ## DEEP MODE:
  ##   research_depth = "deep" forces a full architectural read regardless of ticket
  ##   specificity. Use only for cross-cutting bugs (concurrency, performance,
  ##   security regressions) where a wide read is required.

  ## 2B-1. Execution Path Constraint (RPI Mandate)
  ##
  ## Bug-fix research MUST be constrained to the execution path.
  ## Do NOT grant the agent unrestricted read access to the entire repository.
  ## Providing unrelated files overwhelms the context and causes the model to
  ## attempt rewrites of unrelated components (Stanford 2025 finding).

  TRACE execution path from entry point to error site:
    - Identify entry point (API endpoint, CLI command, event handler, test)
      from TICKET_CONTEXT.reproduction or TICKET_CONTEXT.affected_areas
    - Follow call chain from entry point to the error location
    - EXECUTION_PATH_FILES = files on the call chain (entry → error)

  ## 2B-2. User-Flow Entry Point Tracing (Mandatory for UI/presentation bugs)
  ##
  ## For bug fixes involving error handling or UI presentation: identify not just
  ## the service/API layer where the error occurs, but also the user-flow entry
  ## point — the component/view that initiates the action from the user's
  ## perspective. Trace backwards from the error to the user action. Document both
  ## the error origin AND the user-facing entry point in the research spec.
  ##
  ## SOURCE_CONTEXT.execution_path_trace MUST include:
  ##   - error_origin: { file, line, description }
  ##   - user_entry_point: { component/view, action, description }
  ##   - If user_entry_point cannot be identified → register in open_questions

  CONSTRAIN SOURCE_CONTEXT.affected_files to EXECUTION_PATH_FILES:
    - Any file NOT on the execution path is OUT OF SCOPE for root cause analysis
    - If TICKET_CONTEXT mentions a file not on the execution path, LOG it as
      "referenced but not on execution path — excluded from analysis scope"

ELSE:
  SOURCE_CONTEXT = null

## 2C. Load Context Pack (if available)

IF context_pack_path exists:
  Read tech-policy, arch-standards, coding-standards → SOURCE_LOG

## 2D. REPAIR Mode — Parse Directives

IF MODE == REPAIR:
  Parse failure_feedback into:
  REPAIR_DIRECTIVES = [
    { target: "ticket_summary"|"root_cause"|"impact"|"fix_approach"|
              "acceptance_criteria"|"test_strategy"|"global",
      instruction, reason }
  ]
  Sections WITHOUT directives → PRESERVE (keep from PREVIOUS_SPEC).
  "global" → regenerate entire spec.

## CHECKPOINT 1 — Write skeleton spec after input loading (BUILD mode only)
## Purpose: Preserve extracted contexts if killed during Step 3 generation.
IF MODE == BUILD:
  WRITE SPEC_FILE with:
    - Header metadata (version: NEW_VERSION, session: SESSION_ID, mode: BUILD,
      date: today, language: DETECTED_LANGUAGE, source_path)
    - ticket_summary section: populated from TICKET_CONTEXT
    - root_cause section: populated from SOURCE_CONTEXT (partial — execution path trace if available)
    - All remaining sections as stubs:
      ## {section_name}
      status: pending - will be generated in Step 3
    - Top-level spec_status: draft
  LOG: "CHECKPOINT 1: skeleton spec written with ticket_summary + root_cause (partial)"
```
**Execution:** automated

### Step 3: Generate Spec

**Apply execution-protocol.md Section 10** — Phase A (skeleton-first within 5 tool calls of entering Step 3) then Phase B (one section per `Edit` call). Tool discipline (§10.5) is **mandatory**: skeleton via `Write`, sections via `Edit`, NEVER `Bash + sed/python3/awk` to mutate SPEC_FILE. The non-ASCII fallback (§10.5.1) auto-applies when content is non-English. NEVER fall back to bulk rewriting when one `Edit` fails — fix the `Edit` call instead.

**Skeleton stub text — must be ASCII:** `status: pending - will be generated` (ASCII hyphen U+002D, not em dash).

**Section list (template order):** `ticket_summary -> root_cause -> impact -> fix_approach -> acceptance_criteria -> test_strategy -> validations -> open_questions`. See `references/bug-fix-research-template.md` for full structure.

**READ** `references/bug-fix-research-template.md` **NOW** for section structure.
**READ** `references/rules-and-constraints.md` **NOW** for the 9 consistency rules
(Codebase Fidelity, Root Cause Traceability, Checked Exception Constraint, Ticket
AC Preservation, Technology Fidelity, Zero Invention, Anti-Fade) plus Status
Protocol and Source Tagging.

When generating the test_strategy section, **READ** `references/prove-it-protocol.md`
to ensure each test scenario is marked REPRODUCE or GUARD per the downstream
contract with planning-code-tasks and implementing-code.

Generate the complete spec following the template, applying all rules from
the references above.

## CHECKPOINT 2 — Write complete draft spec after generation
## Purpose: Preserve full draft if killed during Step 4 validation.
WRITE SPEC_FILE with all generated sections (overwrite skeleton from Checkpoint 1).
  - Top-level spec_status: draft
LOG: "CHECKPOINT 2: complete draft spec written (pre-validation)"

**Execution:** automated

### Step 4: Quality Validation Gate

**Command:**
```
1. Codebase Fidelity: Every file path references a real path from
   SOURCE_CONTEXT or is marked [Assumption]
2. Root Cause Traceability: root_cause section contains file:line or [Hypothesis]
3. Ticket AC Coverage: Every item from TICKET_CONTEXT.ac appears verbatim in
   acceptance_criteria.ticket_ac
4. Technology Fidelity: All technology references match SOURCE_CONTEXT.dependencies
   or are marked [Unknown]
5. Anti-Fade: test_strategy depth matches ticket_summary depth
6. Section Completeness: All 7 mandatory sections present
   (ticket_summary, root_cause, impact, fix_approach, acceptance_criteria,
    test_strategy, open_questions)
7. Count Verification: Summary counts match actual item counts in each section
8. Source Tags: Every item with status:complete has a source reference
9. Ticket Contract Mode: TICKET_CONTEXT.contract_mode is recorded as structured,
   partial, or unstructured; unstructured is valid for external ticket inputs
10. Partial Cross-Check: In partial mode, prose-derived IDs/literals/fallbacks
    are checked against structured rows and discrepancies become evidence_gaps
11. Hash Forward Verification: source hashes are valid `sha256:<64 lowercase hex>`
    values or marked invalid; valid mismatches are forward-verified against
    recorded dependencies and accepted only in the audit
12. Auth Security Defaults: auth/OAuth/password-reset tickets carry reset-token
    hash-at-rest and provider allow-list constraints or evidence_gaps

IF corrections needed → apply in place, log to CHANGE_LOG

## CHECKPOINT 3 — Write validated spec after quality gate
WRITE SPEC_FILE with validated content (overwrite draft from Checkpoint 2).
  - Top-level spec_status: complete (or draft if validation failures exist)
LOG: "CHECKPOINT 3: validated spec written"
```
**Execution:** automated

### Step 5: Write Outputs

**Command:**
```
1. Write SPEC_FILE (RESEARCH-SPEC-{SESSION_ID}.md)
   - Set the SPEC front-matter `version:` to NEW_VERSION. On REPAIR this MUST be the
     incremented patch (Step 1: PREVIOUS_VERSION → NEW_VERSION) — editing the content
     in place without bumping `version` is a §7 violation. See execution-protocol §7.2 step 8.
2. Write AUDIT_FILE (RESEARCH-AUDIT-{SESSION_ID}.md):
   - Session metadata (version=NEW_VERSION, mode, session_id, timestamp)
   - Sources referenced (numbered list from SOURCE_LOG)
   - Ticket contract: contract_mode, hashes, hash_status,
     accepted_hash_overrides, partial-mode evidence_gaps
   - Decisions made (from CHANGE_LOG)
   - Summary counts: affected_files, ticket_ac, derived_ac, regression_ac,
     tests_to_write, tests_to_update, open_questions
   - REPAIR-only: set `mode: REPAIR` and APPEND (do not overwrite) a `## Repair History`
     entry — version, timestamp, directives_applied, sections_changed, sections_preserved,
     repair_delta (per execution-protocol §7.2 step 8).
3. REPAIR self-check (execution-protocol §7.2 step 9): before final_response, confirm the
   SPEC `version` is strictly greater than PREVIOUS_VERSION AND the AUDIT has the new
   `## Repair History` entry. If not, fix the bookkeeping now — do not finish.
4. Verify both files exist and are non-empty
5. UPDATE SPEC_FOLDER + '_progress.json':
   { "status": "COMPLETED", "completed_at": "<ISO timestamp>",
     "skill": "researching-bug-fixing", "session_id": SESSION_ID }

Ready for downstream consumption (planning-code-tasks in TASK mode).
```
**Execution:** automated

### Step N: Emit Harness Outputs Sidecar

**Apply execution-protocol.md Section 11.** Mandatory when the prompt contains a `## Run metadata` block (Stepwise invocation); skip otherwise. FINAL file write of the run (after Memory Bank, after `_progress.json` set to COMPLETED).

**Output parameters this skill produces** (one key per row of the prompt's `## Output parameters` table):

- `research_output_path`: the SPEC_FOLDER you actually wrote the RESEARCH-SPEC into, reported VERBATIM. SPEC_FOLDER is already bound to the received (feature-scoped) `research_output_path` param — do NOT re-prepend `{output_folder}`/`{project_name}`/`{feature_id}` or re-derive it from a `{% if feature_id %}` formula (that would drop the feature scope).

**Implementation:** the harness here accepts Bash heredoc for the sidecar write (the sidecar is NOT the SPEC_FILE, so §10.5's anti-Bash rule does not apply). Execute:

```
cat > {stepwise_outputs_file} << 'OUTPUTS_EOF'
{ "research_output_path": "{SPEC_FOLDER}" }
OUTPUTS_EOF
```

## Memory Bank — Update Cross-Session State
Read `_shared/references/memory-bank.md` for the full protocol.
1. Overwrite context-pack/active-context.md with final session state (status, decisions, blockers, key artifacts).
2. Append one milestone row to context-pack/progress.md: `| {session_id} | {date} | {capability} | researching-bug-fixing | {STATUS} | **{N} research-docs** | {1-line summary} |`
   Artifact count MUST be the exact number of research document files written (e.g., `"2 research-docs"`). See _shared/references/memory-bank.md Artifact Type Registry.
Both writes are MANDATORY — even on failure, record the failure.
After writing, VERIFY exists(context-pack/progress.md) and that the last row contains the research-docs count. LOG: "Memory Bank: progress.md updated — {N} research-docs recorded."

## Quality Gates (before Step 5 final write)

**READ** `references/quality-gates.md` **NOW** for the Minimum Output Length
Guard, Common Rationalizations, Red Flags, and Verification Checklist. Apply
each item before writing outputs to disk — these catch superficial bug-fix
research before it ships.

## Reference Files

| File | Load when | Purpose |
|------|-----------|---------|
| `references/bug-fix-research-template.md` | Step 3 | RESEARCH-SPEC section structure |
| `references/rules-and-constraints.md` | Step 3 — once at start | The 9 consistency rules + Status Protocol + Source Tagging |
| `references/prove-it-protocol.md` | Step 3 — when generating test_strategy | REPRODUCE/GUARD test marking + downstream Prove-It contract |
| `references/quality-gates.md` | Before Step 5 final write | Minimum Output Length Guard, Common Rationalizations, Red Flags, Verification Checklist |
