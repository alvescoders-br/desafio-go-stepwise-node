---
name: generating-toolchain-record
description: >
  Generates a Development Toolchain Record (DTR) from target architecture documentation
  and (for brownfield projects) a project brief / current-state notes. Produces a single
  agent-native DTR file with Backend / Frontend (Web) / Mobile tabs, lifecycle state
  classification (stable / migrating / upgrading / legacy / planned), and a Toolchain
  Notes registry. Optionally derives a runtime command registry (`validation-tools.md`)
  consumed by implementing-code Phase C and reviewing-code. Supports two modes:
  greenfield (ASD-only, decisions being made for the first time) and brownfield (ASD +
  PB, captures what is actually deployed today). Zero Invention Policy. BUILD and REPAIR
  modes. Downstream consumers: validating-architecture-compliance, researching-feature-impl,
  planning-code-tasks (state info); implementing-code, reviewing-code (via derived
  validation-tools.md). Human-readable output via humanize-spec on demand.
license: Proprietary
metadata:
  author: aipods-team
  version: 1.0.0
  category: architecture
  tags: dtr, toolchain, greenfield, brownfield, validation-tools, agent-native, FIC
---

# Generating Toolchain Record — Agent-Native Spec

## SKILL PROTOCOL — ENTRY RULES (read first, do not skip)

1. **The protocol below is internally consistent.** If you perceive a conflict
   between the capability prompt and this skill, the skill wins for execution
   mechanics; the capability wins for paths/parameters. Do NOT exit citing
   "ambiguity" or "internal contradiction".

2. **Begin Step 1 (Initialize) immediately.** Step 1's first action (write
   `_progress.json` to `dtr_output_path`) IS the verification.

3. **Reference files load on demand via `cat`** when each step's `READ`
   pointer says so. They are NOT preloaded. The Reference Files table at the
   bottom of this file is a pointer index.

4. **Zero Invention Policy is non-negotiable.** Every tool entry MUST trace to
   the ASD, the PB (brownfield), or to project inspection (brownfield only,
   `source_path` required). Missing data → `TBD` row + open_questions entry.
   Inferred from architectural pattern → mark `(inferred)` with reasoning.
   Asking the human a clarifying question = task FAILURE.

5. **No final response until DTR-{SESSION_ID}.md + DTR-AUDIT-{SESSION_ID}.md
   exist on disk.** When `derive_validation_tools` is `true`, also verify
   `validation-tools.md` at `validation_tools_output_path`.

---

## Quick Start

Read the target architecture document (and the PB for brownfield), classify each tool
by lifecycle state, write a DTR with only the tabs and fields that apply, and
optionally derive `validation-tools.md` for downstream RPI consumption. Output is a
**single DTR file plus an audit file**:

```
{dtr_output_path}/
├── DTR-{SESSION_ID}.md                  ← The toolchain record (Backend/Frontend/Mobile + Notes)
├── DTR-AUDIT-{SESSION_ID}.md            ← Session metadata, sources, classification log
└── _progress.json                       ← Liveness signal
```

When `derive_validation_tools=true`:

```
{validation_tools_output_path}/validation-tools.md   ← Runtime command registry (optional)
```

**Why single-file DTR:** the entire toolchain record fits comfortably in context;
no batching needed. Write-Flush-Forget applies only if context exceeds 60% during
generation (unlikely for the row counts this skill produces).

**Human-readable output:** Not produced by this skill. Use `humanize-spec` with
profile `dtr` to render the DTR for stakeholder review.

## Pipeline Position

```
Target Architecture (output of specifying-architecture)
       +
[Brownfield only] Project Brief / Current Stack notes
       +
[Brownfield, optional] source_path (build files for inspection)
       ↓
[generating-toolchain-record]            ← YOU ARE HERE
       ↓
   ┌───┴────────────────────────────────┐
   ↓                                     ↓
[validating-architecture-compliance]  [validation-tools.md, if derived]
[researching-feature-impl]                 ↓
[researching-bug-fixing]              [implementing-code Phase C]
[planning-code-tasks]                 [reviewing-code]
```

## Mode Selection

| Mode | When to use | Required inputs | TBD semantics |
|---|---|---|---|
| `greenfield` | New project, no deployed system, ASD captures intended decisions | `target_architecture_path` | TBD = open architectural decision (normal) |
| `brownfield` | Existing/deployed system, ASD describes target, PB describes current state | `target_architecture_path`, `project_brief_path` (recommended), `source_path` (recommended) | TBD = documentation gap (log to Toolchain Notes > Gaps) |

If `dtr_mode` is `brownfield` but neither `project_brief_path` nor `source_path` are
provided, log a high-severity entry in DTR-AUDIT and downgrade brownfield-specific
sections (Migration / Upgrade / Legacy) to "no evidence" rather than inferring them.

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project_name` | string | Yes | Project identifier (used in session_id) |
| `dtr_mode` | enum | Yes | `greenfield` or `brownfield` |
| `target_architecture_path` | string | Yes | Path to target architecture folder OR ASD file (greenfield/brownfield) |
| `project_brief_path` | string | Recommended (brownfield) | Path to PB / current-state notes describing what is deployed today |
| `source_path` | string | Optional (brownfield) | Path to source code repository for build-file inspection (pom.xml, package.json, etc.) |
| `dtr_output_path` | string | Yes | Output folder for DTR-{SESSION_ID}.md and DTR-AUDIT-{SESSION_ID}.md |
| `derive_validation_tools` | boolean | No (default `true`) | When true, also write a runtime command registry derived from the DTR |
| `validation_tools_output_path` | string | Conditional | Required when `derive_validation_tools=true`; typically `./context-pack/` |
| `failure_feedback` | string | No | Present only in REPAIR mode — targeted fix directives |
| `custom_message` | string | No | Optional focus areas / scope hints |

**If any Required parameter is not defined, ABORT EXECUTION via `stepwise session exec-fail`.**

## DTR_INDEX — Carry-Forward Contract

Initialize at Step 1. Update after every step. This is the SOLE source of truth
between steps. Never carry full row content — only IDs, states, and status flags.

```
DTR_INDEX = {
  session_id: string,
  mode: greenfield | brownfield,
  project_name: string,
  output_path: string,
  inputs_loaded: { asd: bool, pb: bool, source: bool, context_pack: bool },
  tabs_selected: [backend, frontend_web, mobile],     # only those that apply
  backend_variants: [{ label, language }],            # multiple if multi-stack
  rows_classified: [{ tab, field, tool, version, state, source_ref }],
  states_count: { stable, migrating, upgrading, legacy, planned, tbd },
  toolchain_notes: { migration: N, upgrade: N, legacy: N, planned: N, tbd: N, inferred: N, gaps: N, omitted: N },
  validation_tools: { derived: bool, rows: N, drift_detected: bool },
  files_written: [{ path, status, line_count }],
  blockers: [],
  open_questions: []
}
```

---

## Workflow

### Step 1: Initialize

**Command:**
```
# DTR Generation Agent — Toolchain Record Synthesizer
# Persona: Senior Architect & Toolchain Auditor
# CRITICAL: NON-INTERACTIVE SESSION.
# MISSION: Extract structured toolchain catalog from architecture + (brownfield) PB.
#          Zero invention. Tool state classification governs every row.

SESSION_ID = [Extract from EXECUTION METADATA]

## SESSION_ID is provided by the harness/execution metadata per execution-protocol.md §1.
## REPAIR mode MUST reuse the existing session_id from prior DTR-* filenames.
## BUILD mode MUST also use the harness-provided SESSION_ID — never generate a
## date-based or project-based session_id locally. A re-run of the same Stepwise
## session/step produces the same SESSION_ID and therefore the same filenames,
## which is what enables overwrite-on-re-run instead of duplicate-file-on-re-run.
## SESSION_ID goes in filenames only (e.g. DTR-{SESSION_ID}.md), never in folder names.

## Engagement-Mode Consistency Check
##
## When invoked from a Stepwise pipeline that ran researching-prd first, this
## skill MUST verify that the dtr_mode parameter is consistent with the PRD's
## engagement_mode. If they conflict, the PRD wins (it is the most upstream
## source-of-truth artifact) and the override is logged. Operators wanting to
## force a value can run this skill standalone (without prd_path).

dtr_mode_input = dtr_mode    # original parameter value

IF prd_path is set AND exists(prd_path):
  prd_spec = find PRD-SPEC-*.md in prd_path
  IF prd_spec:
    prd_engagement_mode = parse_yaml_field(prd_spec, "engagement_mode")
    ## Mapping: PRD engagement_mode → DTR mode
    ##   "modernization" → "brownfield"
    ##   "brownfield"    → "brownfield"
    ##   "greenfield"    → "greenfield"
    derived_dtr_mode = "brownfield" if prd_engagement_mode in
                       ("modernization", "brownfield") else "greenfield"

    IF dtr_mode_input != derived_dtr_mode:
      LOG to CHANGE_LOG:
        "Override: dtr_mode parameter '" + dtr_mode_input +
        "' replaced by PRD-derived '" + derived_dtr_mode +
        "' (engagement_mode='" + prd_engagement_mode + "')."
      dtr_mode = derived_dtr_mode

## Brownfield mode WITHOUT a current_architecture file is a hard error.
IF dtr_mode == "brownfield" AND
   (current_architecture is empty OR NOT exists(current_architecture)):
  WRITE Gap Report to DTR_FOLDER:
    "Brownfield engagement detected but no current_architecture file provided.
     Either provide current_architecture (path to existing arch docs or to the
     context-pack architecture standards file) or override dtr_mode=greenfield
     with explicit justification."
  EXIT with status BLOCKED

IF failure_feedback NOT empty:
  MODE = REPAIR
  DTR_FOLDER = resolve_parent_folder(dtr_output_path)
  DTR_FILE = find existing DTR-*.md in DTR_FOLDER
  IF not found -> write Gap Report at DTR_FOLDER/DTR-GAP-REPORT.md -> EXIT
  Load DTR_FILE -> PREVIOUS_DTR -> SOURCE_LOG
  ## REPAIR MUST reuse the SESSION_ID embedded in the prior DTR filename (not the
  ## harness session_id — it may differ if the prior run was in a different session).
  SESSION_ID = extract session_id from PREVIOUS_DTR filename (DTR-{SESSION_ID}.md)
  PREVIOUS_VERSION = extract version from PREVIOUS_DTR header
  NEW_VERSION = increment patch
  Parse failure_feedback -> REPAIR_DIRECTIVES [{ section, instruction, reason }]
ELSE:
  ## BUILD mode — auto-detect prior artifacts BEFORE creating new ones.
  ## If a DTR with the SAME harness SESSION_ID already exists, this is a clean
  ## re-run of the same session — overwrite that file (preserves continuity).
  ## If a DTR with a DIFFERENT session_id exists, the operator is rebuilding from
  ## scratch in a new session; log the prior file path for traceability and proceed
  ## with the new SESSION_ID (do NOT delete prior files automatically).
  MODE = BUILD
  DTR_FOLDER = dtr_output_path
  DTR_FILE = DTR_FOLDER + '/DTR-' + SESSION_ID + '.md'
  AUDIT_FILE = DTR_FOLDER + '/DTR-AUDIT-' + SESSION_ID + '.md'
  NEW_VERSION = "1.0.0"
  mkdir -p DTR_FOLDER

  ## Surface prior artifacts (if any) for the audit log — informational, non-blocking.
  PRIOR_DTRS = list DTR-*.md in DTR_FOLDER excluding DTR_FILE itself
  IF PRIOR_DTRS not empty:
    LOG to CHANGE_LOG: "Prior DTR artifacts present in output folder: {PRIOR_DTRS}.
                       This run produces a new artifact with SESSION_ID={SESSION_ID}.
                       To repair the prior DTR instead, re-run this skill with
                       failure_feedback specifying which sections to revise."

  ## EARLY SIGNAL — FIRST action after mkdir (MANDATORY)
  WRITE DTR_FOLDER + '/_progress.json':
    { "status": "IN_PROGRESS", "started_at": "<ISO timestamp>",
      "skill": "generating-toolchain-record", "session_id": SESSION_ID }

DTR_INDEX = { session_id: SESSION_ID, mode: dtr_mode, project_name: project_name,
              output_path: DTR_FOLDER, inputs_loaded: {}, tabs_selected: [],
              backend_variants: [], rows_classified: [],
              states_count: {stable: 0, migrating: 0, upgrading: 0, legacy: 0,
                             planned: 0, tbd: 0},
              toolchain_notes: {migration: 0, upgrade: 0, legacy: 0, planned: 0,
                                tbd: 0, inferred: 0, gaps: 0, omitted: 0},
              validation_tools: {derived: false, rows: 0, drift_detected: false},
              files_written: [], blockers: [], open_questions: [] }

SOURCE_LOG = []
CHANGE_LOG = []

## Internal Reasoning: ALL in English regardless of output language.
```
**Execution:** automated

### Step 2: Input Loading

**Command:**
```
## STOP-GATE — Mandatory Inputs

REQUIRED = [
  { name: "Target Architecture", path: target_architecture_path }
]

IF dtr_mode == "brownfield":
  RECOMMENDED = [
    { name: "Project Brief", path: project_brief_path },
    { name: "Source Code", path: source_path }
  ]

FOR EACH input IN REQUIRED:
  IF input.path is empty OR file/folder does not exist:
    WRITE {DTR_FOLDER}/DTR-GAP-REPORT.md:
      session_id: {SESSION_ID}
      status: BLOCKED
      reason: Missing target_architecture
      expected_at: {target_architecture_path}
      action: Provide a valid target architecture path and re-run.
    Call stepwise session exec-fail with the same reason.
    EXIT — Do not proceed.

## 2A. Load Target Architecture -> ARCH_CONTEXT

Read target_architecture_path (folder or file). If a folder, read every *.md inside.
Extract:

ARCH_CONTEXT = {
  project_type:        # backend / frontend_web / mobile / multi (from arch overview)
  architecture_style:  # monolith / microservices / event-driven / BFF / mobile-only
  backend_languages:   # [list from tech stack section]
  frontend_languages:  # [list]
  mobile_platforms:    # [list]
  data_stores:         # [list with vendor/version where stated]
  cloud_provider:      # GCP / AWS / Azure / on-prem / hybrid
  containers:          # Kubernetes / ECS / on-VM / none
  cicd_platform:       # GitHub Actions / GitLab CI / Jenkins / Azure DevOps
  auth_strategy:       # OAuth2 / OIDC / SAML / mTLS / custom
  api_design:          # REST / GraphQL / gRPC / mixed
  testing_frameworks:  # named in arch
  monitoring_tools:    # named in arch
  build_tools:         # named in arch
  package_managers:    # named in arch
  explicit_exclusions: # technologies explicitly ruled out
  migration_intent:    # [brownfield] target-state vs current-state markers
}

## 2B. Load Project Brief (brownfield) -> PB_CONTEXT

IF dtr_mode == "brownfield" AND project_brief_path exists:
  PB_CONTEXT = {
    deployed_versions:    # tools and versions actually running today
    stable_tools:         # not changing in this scope
    changing_tools:       # being replaced or upgraded
    enterprise_mandates:  # version locks, vendor contracts, compliance constraints
    phase_scope:          # which migration phase this DTR covers
  }
  inputs_loaded.pb = true
ELSE:
  PB_CONTEXT = null
  IF dtr_mode == "brownfield":
    LOG to DTR-AUDIT: "WARNING: brownfield mode without PB — current-state accuracy reduced"

## 2C. Inspect Source Code (brownfield, if available) -> SOURCE_INSPECTION

IF dtr_mode == "brownfield" AND source_path exists:
  SOURCE_INSPECTION = {
    build_files: [pom.xml | package.json | build.gradle | pyproject.toml | go.mod | …]
    detected_versions: { tool -> version_from_build_file }
    ci_workflows: [.github/workflows/*.yml | .gitlab-ci.yml | Jenkinsfile]
    detected_commands: { build, test, lint, typecheck, security, coverage }
  }
  inputs_loaded.source = true
ELSE:
  SOURCE_INSPECTION = null

## 2D. Determine Applicable Tabs (DTR_INDEX.tabs_selected)

backend_required   = (ARCH_CONTEXT.backend_languages is not empty)
frontend_required  = (ARCH_CONTEXT.frontend_languages is not empty)
mobile_required    = (ARCH_CONTEXT.mobile_platforms is not empty)

DTR_INDEX.tabs_selected = filter([
  ("backend", backend_required),
  ("frontend_web", frontend_required),
  ("mobile", mobile_required),
])

# Multi-backend: if backend_languages has > 1 entry, create one variant per language
IF len(ARCH_CONTEXT.backend_languages) > 1:
  DTR_INDEX.backend_variants = [{label, language} for each]

## 2E. Load Stack References (per detected language)

FOR EACH language IN union(backend_languages, frontend_languages, mobile_platforms):
  load_stack_reference(language)
  # Map language -> file in references/stacks/<file>.md (see Reference Files table)

## 2F. REPAIR Mode — Parse Directives

IF MODE == REPAIR:
  REPAIR_DIRECTIVES = [{ target: "tabs"|"states"|"notes"|"validation_tools"|"global",
                         instruction, reason }]
  Sections WITHOUT directives -> PRESERVE.
  Before regenerating: archive any orphaned files (different SESSION_ID) to /repair-archive/.

## CHECKPOINT 1 — Write skeleton DTR after input loading
WRITE DTR_FILE with:
  - Header (project, mode, generated_from, session_id, version, date)
  - Tab placeholders for each entry in DTR_INDEX.tabs_selected
  - Toolchain Notes section with subsection placeholders
  - Top-level dtr_status: draft
LOG: "CHECKPOINT 1: skeleton DTR written; tabs={tabs_selected}"
```
**Execution:** automated

### Step 3: Classify and Populate Rows

**EARLY-WRITE RULE — MANDATORY (silent-failure prevention).**
You MUST write a skeleton DTR_FILE with the header and tab placeholders within
**5 tool calls** after entering Step 3. Then populate row by row with subsequent
edits. Do NOT compose all tabs in memory before the first write.
Update `_progress.json` after the skeleton write and after each tab is populated.

**READ** `references/dtr-template.md` **NOW** for the exact tab/field/Toolchain-Notes structure.
**READ** `references/state-classification.md` **NOW** for the 5-state lifecycle rules and the classification decision tree.

For each tab in `DTR_INDEX.tabs_selected`:

1. **Always-include fields:** populate the "never N/A" fields for that tab (see template).
2. **Optional fields (`†`):** include only if the tab's stack reference or ARCH_CONTEXT names them.
3. **For each row, run the classification decision tree** from `state-classification.md`. Record:
   - `tool` (canonical name from stack reference or ARCH_CONTEXT)
   - `version` (per state: deployed for stable/upgrading/legacy; target for migrating/planned; `TBD` if undecided)
   - `state` (one of stable / migrating / upgrading / legacy / planned)
   - `source_ref` (ASD section, PB section, or build-file path with line)
4. Append to `DTR_INDEX.rows_classified`. Increment `DTR_INDEX.states_count`.

**Multi-backend handling:** if `DTR_INDEX.backend_variants` has > 1 entry, repeat the
Backend tab once per variant with the label suffix (e.g., `## Backend — Java`).

**Inferred entries:** any value not directly stated — append `(inferred)` and add to
DTR_INDEX.toolchain_notes.inferred. Cite the architectural pattern that led to the inference.

**Omitted fields:** any field whose category is explicitly excluded by ARCH_CONTEXT or PB —
do NOT write the row; instead append to DTR_INDEX.toolchain_notes.omitted.

## CHECKPOINT 2 — Write complete draft DTR after row population
WRITE DTR_FILE with all rows populated and Toolchain Notes draft.
  - dtr_status: draft
LOG: "CHECKPOINT 2: complete draft DTR written (pre-validation)"

**Execution:** automated

### Step 4: Quality Validation Gate

**Command:**
```
1. Tab Completeness: every selected tab has all "never N/A" fields populated or
   explicitly TBD with reason in Toolchain Notes.
2. State Coverage: states_count totals match the row count; no row missing a state.
3. Source Tag Coverage: every non-stable row cites a source reference (ASD / PB / source).
4. Brownfield Discipline: in brownfield mode with PB available, count of TBD rows
   for never-N/A fields ≤ 2 — anything beyond that is a documentation gap.
5. Migration Symmetry: every Migration Entry has both a current and target tool.
   Every Upgrade Entry has both a current and target version.
6. Legacy Decommission: every Legacy entry has a decommission plan or rationale.
7. Inferred Tagging: every (inferred) row has reasoning in Toolchain Notes > Inferred Entries.
8. Multi-Backend Disambiguation: if backend_variants > 1, every Backend section has a label.
9. No Phantom Rows: every row's tool name appears in either ARCH_CONTEXT, PB_CONTEXT,
   SOURCE_INSPECTION, or the corresponding stack reference.
10. Mode/Field Consistency: greenfield rows must NOT use legacy/migrating/upgrading
    (they require evidence that does not exist for brand-new projects).

IF corrections needed -> apply in place, log to CHANGE_LOG.
IF validation cannot pass -> set dtr_status: needs_repair, list failures in
    Toolchain Notes > Gaps, register open_questions, and STILL write the file.

## CHECKPOINT 3 — Write validated DTR after quality gate
WRITE DTR_FILE with validated content.
  - dtr_status: complete (or needs_repair if validations remain)
  - Set the DTR front-matter `version:` to NEW_VERSION. On REPAIR this MUST be the
    incremented patch (Step 1: PREVIOUS_VERSION → NEW_VERSION) — editing content in place
    without bumping `version` is a §7 violation. See execution-protocol §7.2 step 8.
LOG: "CHECKPOINT 3: validated DTR written"
```
**Execution:** automated

### Step 5: Derive validation-tools.md (when enabled)

**Command:**
```
IF derive_validation_tools is FALSE:
  SKIP this step.

IF validation_tools_output_path is empty:
  blockers.append("derive_validation_tools=true requires validation_tools_output_path")
  SKIP derivation; LOG to DTR-AUDIT.

**READ** `references/validation-tools-derivation.md` NOW for the source-of-truth
contract, DTR-field-to-category mapping, command discovery order, and output format.

For each DTR row with state IN (stable, upgrading):
  category = map_field_to_category(row.field)
  IF category is None: SKIP (informational field).
  command = discover_command(row.tool, SOURCE_INSPECTION, stack_reference)
  parser, fail_on, timeout = stack_defaults(category, row.tool)
  required = NOT row.field.endswith("†")
  emit_row({tool, category, command, parser, required, fail_on, timeout, working_dir})

DRIFT DETECTION (REPAIR mode):
  IF existing validation-tools.md found at validation_tools_output_path:
    diff_rows(old, new) -> drift_log
    DTR_INDEX.validation_tools.drift_detected = (drift_log not empty)
    LOG drift entries to DTR-AUDIT.

WRITE {validation_tools_output_path}/validation-tools.md using the format in
references/validation-tools-derivation.md.

DTR_INDEX.validation_tools = { derived: true, rows: <count>, drift_detected: <bool> }
```
**Execution:** automated

### Step 6: Write Outputs

**Command:**
```
1. Verify DTR_FILE (DTR-{SESSION_ID}.md) exists and is non-empty.
2. Write AUDIT_FILE (DTR-AUDIT-{SESSION_ID}.md):
   - Session metadata (session_id, mode, version, timestamp, project_name)
   - Sources referenced (numbered list from SOURCE_LOG):
     Target Architecture, Project Brief (brownfield), Source Code (brownfield),
     Context Pack — each with load status
   - DTR_INDEX summary:
     tabs_selected, backend_variants, rows_classified.length, states_count,
     toolchain_notes counts, validation_tools status
   - Decisions made (from CHANGE_LOG)
   - REPAIR-only: set `mode: REPAIR` and APPEND (do not overwrite) a `## Repair History`
     entry — version, timestamp, directives_applied, sections_changed, sections_preserved,
     repair_delta (per execution-protocol §7.2 step 8).
   - Validation results from Step 4
   - open_questions registry
2b. REPAIR self-check (execution-protocol §7.2 step 9): before final_response, confirm the
   DTR `version` is strictly greater than PREVIOUS_VERSION AND the AUDIT has the new
   `## Repair History` entry. If not, fix the bookkeeping now — do not finish.
3. IF derive_validation_tools=true: verify validation-tools.md exists and is parseable.
4. UPDATE DTR_FOLDER + '/_progress.json':
   { "status": "COMPLETED", "completed_at": "<ISO timestamp>",
     "skill": "generating-toolchain-record", "session_id": SESSION_ID,
     "validation_tools_derived": <bool> }

CRITICAL — Output Registration MUST be a Bash Tool Call (execution-protocol.md Section 11 — Harness Output Sidecar):
1. Execute output registration as a bash tool call:
   `cat > {stepwise_outputs_file} << 'OUTPUTS_EOF'\n{json}\nOUTPUTS_EOF`
   The JSON MUST include: dtr_path, dtr_audit_path, dtr_status,
                          validation_tools_path (if derived), validation_tools_drift (if applicable).
   PATH CORRECTNESS (§11.1.1) — MANDATORY: report `dtr_path` as the **actual folder you
   wrote DTR-{SESSION_ID}.md into** (the resolved `dtr_output_path` parameter as received in
   the prompt's `## Parameters` table). Do NOT re-derive it and do NOT re-prepend
   `{output_folder}`. Without this, the orchestrator falls back to the capability
   `value_template` (`{{output_folder}}/{{dtr}}`); when `dtr_output_path` was already
   pre-resolved to an absolute path, that fallback doubly-nests it under the session scope
   dir (producing a mirrored `.../software-architecture-autoloop/Users/.../dtr` tree).
2. Self-check: `cat {stepwise_outputs_file}` — verify file is non-empty.
3. If empty or missing: re-execute the write command.
4. DO NOT describe output registration in response text — EXECUTE it.
```
**Execution:** automated

## Memory Bank — Update Cross-Session State
Read `_shared/references/memory-bank.md` for the full protocol.
1. Overwrite context-pack/active-context.md with final session state (status, decisions, blockers, key artifacts).
2. Append one milestone row to context-pack/progress.md:
   `| {session_id} | {date} | {capability} | generating-toolchain-record | {STATUS} | **1 dtr-record + N rows** | {1-line summary} |`
   Artifact count format MUST be `"1 dtr-record"` (and `+ 1 validation-tools` when derived).
Both writes are MANDATORY — even on failure, record the failure.
After writing, VERIFY exists(context-pack/progress.md). LOG: "Memory Bank: progress.md updated — {N} dtr-records recorded."

## Reference Files

| File | Load when | Purpose |
|------|-----------|---------|
| `references/dtr-template.md` | Step 3 | DTR tab/field structure and Toolchain Notes layout |
| `references/state-classification.md` | Step 3 — once at start | 5-state lifecycle rules, decision tree, source tagging |
| `references/validation-tools-derivation.md` | Step 5 (only when `derive_validation_tools=true`) | DTR→validation-tools.md mapping, command discovery, drift detection |
| `references/stacks/node-typescript.md` | Step 2E if Node.js / TypeScript backend detected | Canonical Node/TS toolchain catalog |
| `references/stacks/dotnet-csharp.md` | Step 2E if .NET / C# detected | Canonical .NET toolchain catalog |
| `references/stacks/java.md` | Step 2E if Java detected | Canonical Java toolchain catalog |
| `references/stacks/python.md` | Step 2E if Python detected | Canonical Python toolchain catalog |
| `references/stacks/go.md` | Step 2E if Go detected | Canonical Go toolchain catalog |
| `references/stacks/react-nextjs.md` | Step 2E if React / Next.js detected | Canonical React/Next.js frontend catalog |
| `references/stacks/angular.md` | Step 2E if Angular detected | Canonical Angular frontend catalog |
| `references/stacks/vue-nuxt.md` | Step 2E if Vue / Nuxt detected | Canonical Vue/Nuxt frontend catalog |
| `references/stacks/flutter.md` | Step 2E if Flutter / Dart mobile detected | Canonical Flutter mobile catalog |
| `references/stacks/react-native.md` | Step 2E if React Native mobile detected | Canonical RN mobile catalog |
| `references/stacks/kotlin-android.md` | Step 2E if Kotlin / Android native detected | Canonical Kotlin/Android catalog |
| `references/stacks/swift-ios.md` | Step 2E if Swift / iOS native detected | Canonical Swift/iOS catalog |
