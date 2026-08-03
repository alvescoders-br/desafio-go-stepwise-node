---
name: formatting-platform-export
description: >
  Generates a platform-specific import file from a validated backlog (epics +
  user stories) for Jira, Azure DevOps, Asana, or a generic CSV.
  Reads the epics folder and stories folder produced by planning-epics and
  implementing-user-stories skills, maps every Epic and User Story to the
  target platform's schema, applies field transformations (priority,
  story-point estimation, labels, hierarchy linking), and writes a
  ready-to-import file to the output path. Supports selective export by
  epic/story IDs. BUILD and REPAIR modes with full audit trail.
  Applies FIC/RPI methodology: research upstream artifacts first, plan the
  EXPORT_INDEX, then generate output atomically per epic batch.
  Use this skill whenever the user asks to export, push, import, or sync a
  backlog to Jira, Azure DevOps, Asana, or CSV; generate an import file;
  or prepare a platform export from the AI Pods SDLC pipeline.
license: Proprietary
metadata:
  author: aipods-team
  version: 2.0.1
  category: product-management
  tags: product-delivery, jira, azure-devops, asana, csv, export, automated
---

# Formatting Platform Export — Multi-Platform

## Quick Start
Generate a platform-specific import file from a validated backlog.
Reads epics and user stories produced by the pipeline; emits a single file
ready to import into the target platform.

## Supported Platforms

| delivery_platform value | Output file | Format |
|---|---|---|
| `jira` | `jira-import-{SESSION_ID}.csv` | CSV (RFC 4180, UTF-8 BOM) |
| `azure-devops` | `azure-import-{SESSION_ID}.csv` | CSV (UTF-8 BOM, Azure schema) |
| `asana` | `asana-import-{SESSION_ID}.csv` | CSV (UTF-8, Asana schema) |
| `csv-file` | `backlog-export-{SESSION_ID}.csv` | Generic CSV (portable) |
| `servicenow` | `servicenow-import-{SESSION_ID}.csv` | CSV (UTF-8 BOM, ServiceNow Import Set schema) |

## Architecture Overview

```
{export_output_path}/
├── EXPORT-INDEX-{SESSION_ID}.md           ← Master index (always current)
├── {platform}-import-{SESSION_ID}.csv     ← Platform import file
└── export-audit-trail.md                  ← Session Audit Trail
```

**Shared core, platform-specific schema:** Steps 1–2 (init + ingestion) and
Step 5 (audit) are identical for all platforms. Step 3 (Plan) loads the
platform-specific schema reference. Step 4 (Implement) uses the shared
row-generation engine with the column definitions already loaded from the schema.
This avoids duplicating loop logic per platform.

**Why atomic generation:** Each epic's stories are loaded, transformed, and
appended to the output file before the next epic is loaded. This prevents
context overflow on large backlogs (Write-Flush-Forget protocol).

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| epics_output_path | string | Yes | Path to epics folder (EPICS-SPEC-*.md or folder) |
| stories_output_path | string | Yes | Path to stories folder (STORIES-MANIFEST-*.md or folder) |
| project_name | string | Yes | Name of the project |
| delivery_platform | string | Yes | Target: `jira`, `azure-devops`, `asana`, `csv-file`, `servicenow` |
| export_output_path | string | No | Output folder. Default: `./outputs/{platform}-export/` |
| export_scope | string | No | `all` (default) or `selected` |
| selected_epics | string | No | Comma-separated EPIC-IDs (used when export_scope=selected) |
| selected_stories | string | No | Comma-separated US-IDs (used when export_scope=selected) |
| jira_project_key | string | No | Required when delivery_platform=jira (e.g. PCMS, BARRIO) |
| azure_area_path | string | No | Azure DevOps Area Path (e.g. `MyProject\Team`). Optional. |
| asana_project_name | string | No | Asana project name to pre-fill on tasks. Optional. |
| servicenow_hierarchy_mode | string | No | `epic_story` (default, 2 levels) or `epic_capability_feature_story` (4 levels, synthetic). Only applies when delivery_platform=servicenow. |
| failure_feedback | string | No | Feedback for REPAIR mode |

**ABORT conditions (write Gap Report and EXIT if any are true):**
- `project_name`, `epics_output_path`, `stories_output_path`, or `delivery_platform` missing.
- `delivery_platform` not one of: `jira`, `azure-devops`, `asana`, `csv-file`, `servicenow`.
- `delivery_platform == jira` AND `jira_project_key` is empty.
- `export_scope == selected` AND both `selected_epics` AND `selected_stories` are empty.

---

## Workflow

Read each reference file ONLY when you reach that step.
Do NOT pre-load all reference files — this defeats context discipline.

### Step 1: Initialize & Environment Setup

```
# Formatting Platform Export Agent - FIC Methodology
# Persona: Backlog Integration Specialist
# CRITICAL: NON-INTERACTIVE SESSION. PROCEED AUTONOMOUSLY.

## Platform Router — resolve constants from delivery_platform
PLATFORM_SLUG = delivery_platform

OUTPUT_FILENAME_PREFIX = {
  "jira":         "jira-import",
  "azure-devops": "azure-import",
  "asana":        "asana-import",
  "csv-file":     "backlog-export",
  "servicenow":   "servicenow-import"
}[PLATFORM_SLUG]

SCHEMA_REF = {
  "jira":         "references/jira-csv-schema.md",
  "azure-devops": "references/azure-devops-schema.md",
  "asana":        "references/asana-csv-schema.md",
  "csv-file":     "references/generic-csv-schema.md",
  "servicenow":   "references/servicenow-csv-schema.md"
}[PLATFORM_SLUG]

# Platform key: the platform-specific project/area identifier used in field mapping
PLATFORM_KEY = {
  "jira":         jira_project_key,
  "azure-devops": azure_area_path,     # may be empty — schema handles default
  "asana":        asana_project_name,  # may be empty — schema handles default
  "csv-file":     "",
  "servicenow":   ""                  # hierarchy mode is threaded separately, not a project/area key
}[PLATFORM_SLUG]

## Folder Resolution (BUILD vs REPAIR)
IF failure_feedback NOT empty (REPAIR detected):
  EXPORT_FOLDER = resolve_parent_folder(export_output_path)
  # If export_output_path is a file → use parent dir. If folder → use as-is.
  IF EXPORT_FOLDER does not exist or is empty → write Gap Report → EXIT.
  INDEX_FILE  = find existing EXPORT-INDEX-*.md in EXPORT_FOLDER
  OUTPUT_FILE = find existing {OUTPUT_FILENAME_PREFIX}-*.csv in EXPORT_FOLDER
  AUDIT_FILE  = EXPORT_FOLDER + 'export-audit-trail.md'
  # Keep ALL existing filenames. Do NOT rename with new SESSION_ID.
ELSE (BUILD):
  EXPORT_FOLDER = export_output_path + '/'
  ## SESSION_ID goes in spec FILENAMES only — never in the folder name.
  ## The folder must match the capability YAML path parameter exactly.
  INDEX_FILE    = EXPORT_FOLDER + 'EXPORT-INDEX-' + SESSION_ID + '.md'
  OUTPUT_FILE   = EXPORT_FOLDER + OUTPUT_FILENAME_PREFIX + '-' + SESSION_ID + '.csv'
  AUDIT_FILE    = EXPORT_FOLDER + 'export-audit-trail.md'
  mkdir -p EXPORT_FOLDER

**FIRST ACTION — MANDATORY:** Write `_progress.json` to the output folder before any other file write.
This prevents the orchestrator from sending SIGINT.

```json
{ "skill": "formatting-platform-export", "session_id": "initializing",
  "status": "RUNNING", "started_at": "<ISO timestamp>", "completed_at": null }
```

## State Initialization
EXPORT_INDEX = {
  project_name:      project_name,
  delivery_platform: delivery_platform,
  platform_key:      PLATFORM_KEY,
  export_scope:      export_scope | "all",
  selected_epic_ids:  [],
  selected_story_ids: [],
  epic_ids:          [],   # populated in Step 2
  story_ids:         [],   # populated in Step 2
  rows_written:      0,
  epics_exported:    [],
  stories_exported:  [],
  skipped_items:     [],
  assumptions:       [],
  gaps:              [],
  batch_status: { research: null, header: null, rows: null, audit: null }
}

## FIC Principles
1. Foundational: No invented epics, stories, or field values. Source-only.
   Missing field → emit platform schema default. Never invent data.
2. Instructional: RPI — Research → Plan (header + schema) → Implement (rows).
3. Contextual: Write-Flush-Forget per epic. EXPORT_INDEX + PLATFORM_SCHEMA
   are the sole carry-forward contracts.

## Internal Reasoning: ALL in English regardless of output language.
```

---

### Step 1.5: Input Validation STOP-GATE

```
## STOP-GATE — Check all ABORT conditions listed in Parameters.
IF any condition is true → write Gap Report to INDEX_FILE → EXIT.

## Validate upstream artifacts:
  1. Epics artifact at epics_output_path:
     MUST contain EPICS-SPEC-*.md (or folder containing it).
  2. Stories artifact at stories_output_path:
     MUST contain STORIES-MANIFEST-*.md and epics/ subfolder.

IF epics artifact missing/unreadable → Gap Report → EXIT.
IF stories artifact missing/unreadable → Gap Report → EXIT.
IF MODE == REPAIR AND OUTPUT_FILE not found → Gap Report → EXIT.
```

---

### Step 2: Research — Load & Index Upstream Artifacts

```
## RPI Phase 1: Research (shared across all platforms)

Read reference file: references/01-artifact-ingestion.md
Follow its instructions to:
  1. Load epics artifact → populate EXPORT_INDEX.epic_ids
     (id, title, priority_tier, complexity, kpi_ids, rsk_ids, theme).
  2. Lightweight-scan stories artifact → build STORY_REGISTRY
     { EPIC-XX → { file_path, story_ids[], story_count } }.
  3. Apply scope filter (all / selected).
  4. Log all artifact paths to SOURCE_LOG.
  5. Mark batch_status.research = "COMPLETE".

After Step 2:
  FLUSH loaded artifact text from memory.
  RETAIN: EXPORT_INDEX, STORY_REGISTRY, SOURCE_LOG.
```

---

### Step 3: Plan — Load Platform Schema & Write File Header

```
## RPI Phase 2: Plan

## 3a. Load the platform schema
Read reference file: {SCHEMA_REF}
  (resolved in Step 1 — one of jira / azure-devops / asana / generic)

Store the following in PLATFORM_SCHEMA (do NOT flush — needed through Step 4):
  PLATFORM_SCHEMA = {
    COLUMN_HEADERS:  [...],   # exact CSV header row
    EPIC_FIELD_MAP:  {...},   # AI Pods epic fields → platform columns
    STORY_FIELD_MAP: {...},   # AI Pods story fields → platform columns
    DEFAULTS:        {...},   # column → default value when source is absent
    ENCODING:        {...},   # BOM, line endings, quoting rules
    IMPORT_STEPS:    "..."    # post-export instructions (verbatim for INDEX_FILE)
  }

## 3b. Write file header (tool call — mandatory before any row generation)
Write PLATFORM_SCHEMA.COLUMN_HEADERS as first row of OUTPUT_FILE.
  Apply PLATFORM_SCHEMA.ENCODING (BOM prefix if required, correct line endings).
Write INDEX_FILE stub (WRITE tool call):
  - Header: project, platform, SESSION_ID, mode, scope, date
  - Placeholder counts (overwritten in Step 5)
Mark batch_status.header = "COMPLETE".
LOG: "Header written for platform={delivery_platform}."
```

---

### Step 4: Implement — Generate Rows (Bundled Helper)

This step is fully deterministic. Invoke the bundled Python helper rather
than running the per-epic loop in-prompt. The helper handles markdown
parsing, scope filtering, field mapping, transforms (priority, story
points, labels, AC text), CSV encoding (BOM, CRLF, RFC 4180 quoting), and
the Write-Flush-Forget loop.

```
## RPI Phase 3: Implement (helper-driven)

# 1) Run the bundled helper. It writes the header row + all data rows
#    atomically. Schemas for jira / azure-devops / asana / csv-file / servicenow
#    are bundled in the script; you do NOT need to load any reference file
#    here.
python3 scripts/render_csv_rows.py \
  --platform {delivery_platform} \
  --epics-index {EPICS_INDEX_FILE} \
  --stories-folder {STORIES_EPICS_SUBFOLDER} \
  --output {OUTPUT_FILE} \
  --scope {export_scope} \
  $( [ "{export_scope}" = "selected" ] && echo "--selected-epics {selected_epics} --selected-stories {selected_stories}" ) \
  $( [ "{delivery_platform}" = "jira" ] && echo "--jira-project-key {jira_project_key}" ) \
  $( [ "{delivery_platform}" = "azure-devops" ] && [ -n "{azure_area_path}" ] && echo "--azure-area-path \"{azure_area_path}\"" ) \
  $( [ "{delivery_platform}" = "asana" ] && [ -n "{asana_project_name}" ] && echo "--asana-project-name \"{asana_project_name}\"" ) \
  $( [ "{delivery_platform}" = "servicenow" ] && [ -n "{servicenow_hierarchy_mode}" ] && echo "--servicenow-hierarchy-mode \"{servicenow_hierarchy_mode}\"" )
# The helper prints a JSON summary to stdout. Capture it.

# Alternative: if you have already pre-parsed epics/stories into JSON
# (faster for large backlogs or when re-running), pass them directly:
#   --epics-json {path-to-epics.json} --stories-json {path-to-stories.json}

# 2) Parse the JSON summary and update EXPORT_INDEX in place:
EXPORT_INDEX.epics_exported    = summary.epics_exported
EXPORT_INDEX.stories_exported  = summary.stories_exported
EXPORT_INDEX.rows_written      = summary.rows_written
EXPORT_INDEX.skipped_items     = summary.skipped
EXPORT_INDEX.gaps              = summary.gaps
EXPORT_INDEX.assumptions       = summary.assumptions
EXPORT_INDEX.batch_status.rows = "COMPLETE"

# 3) Verify OUTPUT_FILE exists and is non-empty.
#    If the script exited non-zero or the file is empty → REPAIR the run.

LOG: "Row generation complete. Rows: {rows_written} + 1 header."
```

**What is NOT in-prompt anymore:** per-epic loops, story parsing regex,
field-by-field mapping, encoding rules, BOM/CRLF handling. The script
is the source of truth — see `scripts/render_csv_rows.py` (bundled
inside this skill) for the platform schemas and transforms. The legacy reference files
(`02-csv-row-generation.md`, `01-artifact-ingestion.md`, and the per-platform
schema docs) remain as human-readable documentation but are no longer
required reading for execution.

---

### Step 5: Audit Trail & Final Index

```
## Write Audit Trail
Read reference file: references/03-audit-trail.md
Write export-audit-trail.md with:
  - Session metadata (SESSION_ID, platform, mode, version, timestamp)
  - SOURCE_LOG entries (all artifacts loaded)
  - Scope applied (all / selected with IDs)
  - Counts: epics exported, stories exported, rows written, skipped, assumptions, gaps
  - REPAIR change log (if mode == REPAIR)
Mark batch_status.audit = "COMPLETE".

## Finalize INDEX_FILE
Overwrite INDEX_FILE with final content:
  1. Header: project, platform, version (NEW_VERSION), SESSION_ID, mode, date
  2. Quick Navigation:
     | File | Description | Status |
     | {OUTPUT_FILENAME_PREFIX}-{SESSION_ID}.csv | Platform import file | ✅ |
     | export-audit-trail.md | Audit Trail | ✅ |
  3. Export Summary:
     - Platform: {delivery_platform}
     - Epics Exported: {count}
     - Stories Exported: {count}
     - Total CSV Rows (excl. header): {rows_written}
     - Skipped Items: {count}
     - Assumptions: {count}
     - Gaps: {count}
  4. Import Instructions: paste PLATFORM_SCHEMA.IMPORT_STEPS verbatim.

## Post-Write Verification (MANDATORY — HARD FAIL)
Verify ALL 3 expected files exist inside EXPORT_FOLDER and are non-empty:
  1. INDEX_FILE  (EXPORT-INDEX-{SESSION_ID}.md)
  2. OUTPUT_FILE ({PLATFORM_SLUG}-import-{SESSION_ID}.csv or
                  backlog-export-{SESSION_ID}.csv) — must contain header + ≥ 1 data row
  3. AUDIT_FILE  (export-audit-trail.md)

If ANY of the three checks fails:
  - Set `_progress.json` status = FAILED with reason "output_missing"
  - Do NOT write the harness sidecar (execution-protocol §11)
  - Abort the step. Do NOT silently auto-generate the missing file —
    a missing artifact is an EXECUTION_FAILED signal, not a recoverable case.

VIOLATION: All 3 files must live inside EXPORT_FOLDER (the session-scoped
subfolder), NOT at the parent export_output_path level. A step that emits no
artifact MUST NOT be allowed to flow into a passing quality gate.

## Metadata
Append to "./artifacts/outputs/artifact-tracking.md":
  session, artifact_type: platform_export, platform: delivery_platform,
  mode, version, epics_exported, stories_exported, total_rows, timestamp


Memory Bank artifact type: `"{N} work-items"` (e.g., `"63 work-items"`).

**Memory Bank — MANDATORY session-end writes:**
1. Overwrite `context-pack/active-context.md` with session status, decisions, blockers, key artifacts (see execution-protocol.md Section 4 for schema).
2. Append one milestone row to `context-pack/progress.md` with artifact count above.

**LAST ACTION — MANDATORY:** Update `_progress.json` status to `COMPLETED` with `completed_at` timestamp.
If the session failed, set status to `FAILED` instead.

Ready for {delivery_platform} import.
```

---

## Reference Files

Load ONLY the reference file you are currently executing.

**Shared (all platforms):**
- `references/01-artifact-ingestion.md` — Load epics/stories artifacts, build STORY_REGISTRY
- `references/02-csv-row-generation.md` — Shared row-generation engine + transformation helpers
- `references/03-audit-trail.md` — Audit trail template and REPAIR change-log format

**Platform schemas (load only the one matching delivery_platform):**
- `references/jira-csv-schema.md` — Jira: columns, field map, encoding, import steps
- `references/azure-devops-schema.md` — Azure DevOps: columns, field map, encoding, import steps
- `references/asana-csv-schema.md` — Asana: columns, field map, encoding, import steps
- `references/generic-csv-schema.md` — Generic CSV: columns, field map, portable defaults
- `references/servicenow-csv-schema.md` — ServiceNow: columns, field map, encoding, Import Set/Transform Map import steps, optional 4-level hierarchy mode