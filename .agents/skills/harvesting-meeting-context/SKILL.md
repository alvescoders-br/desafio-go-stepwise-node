---
name: harvesting-meeting-context
description: >
  Transcribes meeting audio/video recordings (mp3, m4a, wav, mp4) into structured
  markdown transcripts plus a metadata JSON, with chunking, retry, and a dual
  transcription path: cloud API (omni_parser) for short files and local whisper
  for files that exceed the API's 300s timeout. Auto-installs ffmpeg and
  openai-whisper unattended when missing. Produces per-meeting transcript files,
  per-meeting metadata, an optional aggregate context-pack analysis, and an
  audit. Activate when the task mentions "transcribe meetings", "meeting
  transcription", or references a project root with `artifacts/inputs/meetings/`.
license: Proprietary
metadata:
  author: aipods-team
  version: 1.1.0
  category: tooling
  tags: transcription, meetings, context-pack, audio, utility
compatibility: >
  Supports macOS with Homebrew and Linux with apt-get or dnf best effort.
  Requires python3 with pip3, ffmpeg/ffprobe, and openai-whisper, auto-installed
  when missing. Uses omni_parser MCP when available and falls back to local
  whisper when absent.
---

# harvesting-meeting-context — Agent-Native Skill

## Quick Start

Convert meeting recordings into structured, agent-readable notes. Primary output is
a **set of markdown transcript files plus per-meeting metadata JSON** — not prose
summaries. The skill auto-installs ffmpeg and openai-whisper unattended when those
tools are missing, splits long files into 5-minute audio chunks, transcribes each
chunk via the cloud API (when available and the chunk fits the 300s budget) or
local whisper otherwise, stitches the chunked transcripts back into one file with
correct timestamp offsets, and emits per-meeting metadata plus an aggregate
context-pack analysis.

The skill is the operational hardening of an earlier inspiration skill that failed
on a 17 MB / ~45-minute MP3 because it sent the whole file to a cloud API with a
300-second hard timeout and no chunking. This skill prevents that class of failure
by design: pre-flight checks, chunked uploads, dual-path transcription, retry, and
local fallback.

## Output Architecture

```
{output_path}/
├── _batches.md                                   ← Top-level cross-batch index (one row per batch)
├── _progress.json                                ← Orchestrator anchor (current run state)
└── batches/
    └── {batch_id}/                               ← All per-batch outputs live here
        ├── 00-index.md                            ← Living progress tracker (Pattern 7)
        ├── manifest.md                            ← TRANSCRIPT_INDEX rendered as markdown
        ├── transcripts/
        │   ├── meeting-01-{slug}.md               ← One stitched transcript per source file
        │   └── meeting-NN-{slug}.md
        ├── metadata/
        │   ├── meeting-01-{slug}.json             ← Per-meeting metadata (duration, chunks, model, path)
        │   └── meeting-NN-{slug}.json
        ├── meeting-analysis.md                    ← Aggregate context-pack-targeted extraction (this batch only)
        └── TRANSCRIPT-AUDIT-{batch_id}-{SESSION_ID}.md   ← Session audit
```

**Why manifest + per-item:** Each meeting is independent and large enough (a one-hour
transcript can approach 1,000 lines) that batching them into one file would burn
context and make REPAIR for a single failed meeting expensive. Per-item files let
REPAIR target a specific `meeting-NN-{slug}.md` without rewriting the others.

**Why per-batch subfolder (`batches/{batch_id}/`):** A single `output_path` may
accumulate multiple independent corpora over the engagement (e.g. discovery-q3,
epic-01, stakeholder-interviews). Without per-batch isolation, a second run
overwrites or shadow-merges with the first. The `batch_id` segment makes every
run idempotent within its own namespace, and downstream skills can either target
one batch or fan-out across all batches via `batches/*/meeting-analysis.md`.

**Top-level `_batches.md`:** Cross-batch index. One row per batch with id,
meeting count, total duration, status, and path to its `meeting-analysis.md`.
Downstream skills read this to decide which batches are in scope.

**Top-level `_progress.json`:** Orchestrator anchor — kept at `output_path` (NOT
inside a batch folder) so the harness FIRST ACTION protocol has one stable path
even when multiple batches accumulate. The active batch's id is stored in the
`current_batch_id` field; batch-level detail lives in the batch's `manifest.md`.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `source_path` | string | Yes | — | Directory containing source recordings. Typically `{BASE_PATH}/artifacts/inputs/meetings/`. The skill discovers all `.mp3`, `.m4a`, `.wav`, `.mp4` files inside. Non-recursive unless `recursive=true`. |
| `output_path` | string | Yes | — | Directory to write outputs. The skill writes the top-level `_batches.md` and `_progress.json` here, and creates `batches/{batch_id}/` for the current run's per-batch artifacts. Multiple batches accumulate under the same `output_path`; each lives in its own `batches/{batch_id}/` namespace and never overwrites a peer. |
| `batch_id` | string | No | derived | Kebab-case identifier that scopes this run's outputs to `{output_path}/batches/{batch_id}/`. When omitted, derived in this order: (1) basename of `source_path` if it's already a kebab-case scope (e.g. `recordings/discovery-q3/` → `discovery-q3`), (2) a `batch_id:` line in `project-brief.md` frontmatter if present, (3) fallback `default-{YYYYMMDD}` (logged as an open_question). REQUIRED when running the skill multiple times against the same `output_path` with different recording corpora. |
| `chunk_seconds` | integer | No | `300` | Audio segment length used when splitting large files. 300 (5 min) is the safe upper bound for the cloud API's 300s timeout. |
| `size_threshold_mb` | integer | No | `5` | Files larger than this are chunked before transcription. Files at or below this are sent to the cloud API in one shot. |
| `duration_threshold_seconds` | integer | No | `360` | Files longer than this are chunked. 360s (6 min) gives the cloud API headroom on its 300s budget. |
| `transcription_preference` | enum | No | `auto` | `auto` (cloud API → fallback to whisper), `cloud_only` (require omni_parser), `local_only` (always use whisper). |
| `whisper_model` | enum | No | `small` | `tiny`, `base`, `small`, `medium`, `large`. `small` is the recommended default for meeting Spanish/English on Apple Silicon. |
| `auto_install` | boolean | No | `true` | When `true`, missing ffmpeg / openai-whisper are installed unattended via Homebrew (macOS) or apt-get/dnf (Linux). When `false`, missing dependencies abort with a clear error. |
| `recursive` | boolean | No | `false` | Traverse subdirectories under `source_path`. |
| `language` | string | No | `auto` | ISO code passed to whisper (`en`, `es`, `pt`, …) or `auto`. |
| `failure_feedback` | string | No | — | When non-empty, enables REPAIR mode. Expected format: lines like `meeting-03 retry transcription`, or `dependency ffmpeg reinstall`, or `analysis regenerate`. |
| `retry_max` | integer | No | `3` | Per-chunk retry attempts on cloud API failure (HTTP 5xx, timeout). Backoff is exponential: 5s → 15s → 45s. |
| `min_free_disk_mb` | integer | No | `2048` | Pre-flight check. Aborts if free disk under `output_path` is below this (chunking + intermediate files require headroom). |

**If any Required parameter is not defined, ABORT EXECUTION.**

## Prerequisites

- [ ] `source_path` exists and contains at least one supported media file
- [ ] `output_path` is writable
- [ ] When `transcription_preference=cloud_only`: omni_parser MCP tool is available
- [ ] When `transcription_preference=local_only`: python3 + pip3 available (whisper auto-install)
- [ ] At least `min_free_disk_mb` of free disk under `output_path`

## TRANSCRIPT_INDEX — Carry-Forward Contract

Initialize at Step 1. Update after every phase. SOLE source of truth between phases.
Never carry transcript text or audio buffers — only IDs, paths, status flags.

```
TRANSCRIPT_INDEX = {
  session_id: string,
  mode: BUILD | REPAIR,
  output_path: string,                // top-level dir (parent of batches/)
  batch_id: string,                   // kebab-case scope; resolved in Step 1
  batch_id_source: "param" | "source_path_basename" | "project_brief" | "default_fallback",
  batch_dir: string,                  // = "{output_path}/batches/{batch_id}"
  source_path: string,
  config: {
    chunk_seconds: integer,
    size_threshold_mb: integer,
    duration_threshold_seconds: integer,
    transcription_preference: auto | cloud_only | local_only,
    whisper_model: string,
    auto_install: boolean,
    language: string,
    retry_max: integer
  },
  dependencies: {
    ffmpeg:    { available: bool, version: string, installed_by_skill: bool, install_log: string },
    ffprobe:   { available: bool, version: string },
    whisper:   { available: bool, version: string, installed_by_skill: bool, install_log: string },
    python3:   { available: bool, version: string },
    omni_parser: { available: bool, reason_unavailable: string | null }
  },
  preflight: {
    free_disk_mb: integer,
    network_reachable_to_api: bool,
    aborted: bool,
    abort_reason: string | null
  },
  items: [{
    id: "meeting-NN",
    source_file: "absolute path",
    slug: "kebab-case slug derived from filename",
    duration_seconds: number,
    file_size_bytes: number,
    container_format: "mp3 | m4a | wav | mp4",
    audio_extracted_from_video: bool,
    chunks_total: number,
    chunks_completed: number,
    transcription_path: "cloud_api | local_whisper | hybrid",
    status: "PENDING | PROCESSING | COMPLETE | FAILED | SKIPPED",
    transcript_file: "transcripts/meeting-NN-slug.md" | null,
    metadata_file: "metadata/meeting-NN-slug.json" | null,
    last_error: string | null,
    retry_attempts: number
  }],
  total_items: number,
  completed_items: number,
  failed_items: number,
  aggregate_analysis_file: "meeting-analysis.md" | null,
  repair_log: [{ directive, target, outcome }],
  blockers: [],
  open_questions: []
}
```

`_progress.json` mirrors `items[]` for RESUME after compaction or external interrupt.

---

## Workflow

### Step 1: Initialize & Environment Setup

Read `references/phase-a-environment-setup.md` before executing this step.

**FIRST ACTION — MANDATORY:** Write `_progress.json` to `output_path` BEFORE any other
file write. This prevents the orchestrator from sending SIGINT during long-running
dependency installs. Inline schema:

```json
{ "skill": "harvesting-meeting-context", "session_id": "initializing",
  "status": "RUNNING", "started_at": "<ISO timestamp>", "completed_at": null,
  "total": 0, "completed": 0, "items": [] }
```

**Command:**
```
1. SESSION_ID is provided by the harness/execution metadata per execution-protocol.md §1.
   REPAIR mode MUST reuse the existing session_id from prior TRANSCRIPT-AUDIT-*.md filenames.

2. RESOLVE batch_id (PRECEDES REPAIR detection — REPAIR needs batch_id to find prior outputs):
   IF batch_id parameter is provided:
     batch_id_source = "param"
   ELIF basename(source_path) matches ^[a-z0-9]+(-[a-z0-9]+)*$ AND length <= 60:
     batch_id = basename(source_path)
     batch_id_source = "source_path_basename"
   ELIF a `project-brief.md` exists in source_path's parent or grandparent AND its YAML
        frontmatter contains a `batch_id:` line that matches the kebab-case rule:
     batch_id = parsed value
     batch_id_source = "project_brief"
   ELSE:
     batch_id = "default-{YYYYMMDD}"
     batch_id_source = "default_fallback"
     REGISTER open_question: { type: "batch_id_unresolved", impact: "outputs land in default-* namespace; consider passing batch_id explicitly to scope this run" }
   batch_dir = "{output_path}/batches/{batch_id}"
   LOG: "batch_id={batch_id} (source: {batch_id_source})"

3. REPAIR detection (Pattern 3 — REPAIR Folder Reuse):
   IF failure_feedback is non-empty:
     MODE = REPAIR
     IF NOT exists(batch_dir):
       ABORT — REPAIR target batch does not exist at {batch_dir}.
     LOAD existing TRANSCRIPT_INDEX from {batch_dir}/manifest.md and {output_path}/_progress.json
     PARSE failure_feedback → REPAIR_DIRECTIVES = [{ target, instruction, reason }]
       Allowed targets: meeting-NN | dependency:{name} | analysis | batch:{batch_id} | global
     NOTE: batch_dir MUST already exist. Never mkdir batch_dir for REPAIR.
   ELSE:
     MODE = BUILD
     CREATE output_path (parent only — top-level _batches.md and _progress.json land here)
     CREATE batch_dir, batch_dir/transcripts/, batch_dir/metadata/
     IF batch_dir already contains transcripts/ from a prior BUILD AND no failure_feedback was passed:
       ABORT with remediation: "batch '{batch_id}' already exists with content; pass failure_feedback to REPAIR, or change batch_id, or delete the batch folder to overwrite."

4. Initialize TRANSCRIPT_INDEX with session_id, mode, output_path, batch_id, batch_id_source,
   batch_dir, source_path, config

4. Zero Invention Policy: every metadata field (duration, language, speaker count) MUST
   come from a probe (ffprobe) or transcription tool output. Do NOT invent values.
   Missing data → status: pending → registered in open_questions.

6. STOP-GATE — abort if:
   - source_path does not exist or contains no supported media file
   - output_path is not writable
   - batch_id does not match `^[a-z0-9]+(-[a-z0-9]+)*$` after derivation
   - MODE == BUILD AND batch_dir already contains transcripts/ (collision protection)
   - transcription_preference == cloud_only AND omni_parser MCP tool is not available
   - free disk under output_path < min_free_disk_mb
   LOG: "Step 1 COMPLETE. Session: {SESSION_ID}, Mode: {MODE}, batch_id: {batch_id} ({batch_id_source}), batch_dir: {batch_dir}."

6. Pattern 7 — Living Progress Tracker:
   WRITE {output_path}/batches/{batch_id}/00-index.md with header (mode, session, started timestamp) and
   an empty items table marked "[ ] TO BE DISCOVERED". This file is rewritten in Step 2
   once items are discovered, and updated in-place after every per-meeting step.

7. Auto-install dependencies (when auto_install=true):
   See references/phase-a-environment-setup.md for OS-detection logic, install commands,
   verification commands, and the full dependency state machine.

   For each of [ffmpeg, ffprobe, whisper, python3]:
     PROBE: command -v {tool}
     IF missing AND auto_install == true:
       RUN install command for current platform UNATTENDED (no prompts)
       VERIFY install with --version probe
       UPDATE TRANSCRIPT_INDEX.dependencies.{tool} = { available: true, installed_by_skill: true, ... }
     IF missing AND auto_install == false:
       FAIL CLEARLY with the exact install command the user should run.
       ABORT.

8. Memory Bank — read prior session state:
   READ context-pack/active-context.md (if exists) for prior transcription sessions.
   See execution-protocol.md §4 for schema.
```

---

### Step 2: Discover & Pre-flight per Source File

Read `references/phase-b-preprocessing.md` before executing this step.

**Command:**
```
DISCOVER source files:
  Scan source_path for supported extensions (.mp3, .m4a, .wav, .mp4).
  IF recursive=true: traverse subdirectories.
  SORT alphabetically. Assign id = "meeting-{NN}" zero-padded to 2 digits.
  Derive slug from filename (kebab-case, no spaces, no extension, max 60 chars).

FOR EACH discovered file:
  // Pattern 5 — Mandatory Source Loading per unit
  PROBE with ffprobe (do not load file content into memory):
    duration_seconds, container_format, file_size_bytes, audio stream presence
  
  // Pattern 6 — Per-unit fidelity check (pre-write gate for the index entry)
  IF probe fails (corrupt file, no audio stream):
    UPDATE TRANSCRIPT_INDEX.items += { id, source_file, status: SKIPPED, last_error: <reason> }
    LOG: "Skipped {id}: {reason}"
    Do NOT stop. Process ALL files.
    CONTINUE to next file.
  
  DECIDE chunking strategy:
    needs_chunking = (file_size_bytes/1MB > size_threshold_mb)
                     OR (duration_seconds > duration_threshold_seconds)
    IF needs_chunking:
      chunks_total = ceil(duration_seconds / chunk_seconds)
    ELSE:
      chunks_total = 1
  
  DECIDE transcription path:
    IF transcription_preference == local_only:
      transcription_path = "local_whisper"
    ELIF transcription_preference == cloud_only:
      transcription_path = "cloud_api"
      IF chunk duration > 300s for any chunk → register open_question and downgrade to chunked cloud
    ELSE (auto):
      IF chunks_total == 1 AND duration_seconds <= 270 AND omni_parser available:
        transcription_path = "cloud_api"
      ELIF omni_parser available AND chunk_seconds <= 270:
        transcription_path = "cloud_api"  // chunked
      ELSE:
        transcription_path = "local_whisper"
  
  APPEND to TRANSCRIPT_INDEX.items: { id, source_file, slug, duration_seconds,
    file_size_bytes, container_format, chunks_total, chunks_completed: 0,
    transcription_path, status: PENDING, transcript_file: null, metadata_file: null,
    last_error: null, retry_attempts: 0 }
  
  Do NOT stop. Process ALL discovered files.

WRITE {output_path}/batches/{batch_id}/manifest.md as the rendered TRANSCRIPT_INDEX (markdown table of items
with id, source_file, duration, chunks_total, transcription_path, status).
WRITE {output_path}/batches/{batch_id}/00-index.md updated with the discovered items table.
WRITE {output_path}/_progress.json mirror.

VERIFY: total_items == count(supported files in source_path) - count(SKIPPED items).
LOG: "Step 2 COMPLETE. Discovered {N} items. {M} skipped. Chunking required for {K}."
```

---

### Step 3: Transcribe — Per-Meeting Loop

Read `references/phase-c-transcription.md` before executing this step.

**Command:**
```
FOR EACH item in TRANSCRIPT_INDEX.items WHERE status == PENDING:

  IF mode == REPAIR AND no REPAIR_DIRECTIVE targets this meeting (target != item.id AND target != "global"):
    SKIP — preserve existing transcript_file and metadata_file unchanged.
    LOG: "{item.id} skipped (REPAIR, no directive)."
    CONTINUE to next item.
  
  // Pattern 5 — Mandatory Source Loading per unit
  RELOAD item.source_file metadata from disk via ffprobe (do not assume Step 2 cache).
  IF source_file no longer exists:
    UPDATE item.status = FAILED, last_error = "source file moved/deleted"
    Do NOT stop. CONTINUE.
  
  UPDATE item.status = PROCESSING. WRITE _progress.json.
  
  STAGE A — Audio extraction (if mp4 or non-mp3 source):
    Run ffmpeg to extract audio to a temp .mp3 (mono, 16kHz, 64kbps — keeps file small,
    matches whisper's expected input). Store under {output_path}/batches/{batch_id}/.tmp/{item.id}/source.mp3.
  
  STAGE B — Chunking (if item.chunks_total > 1):
    ffmpeg -i source.mp3 -f segment -segment_time {chunk_seconds} -c copy
           {output_path}/batches/{batch_id}/.tmp/{item.id}/chunk_%03d.mp3
    chunk_files = sorted listing of chunk_*.mp3 (chunks_total entries expected)
    VERIFY count(chunk_files) == item.chunks_total. If mismatch: UPDATE item.last_error,
    item.status = FAILED. Do NOT stop. CONTINUE to next item.
  ELSE:
    chunk_files = [source.mp3]
  
  STAGE C — Transcribe each chunk:
    transcript_segments = []  // in-memory list of {chunk_index, text, start_offset_seconds}
    
    FOR EACH chunk_index, chunk_file in chunk_files:
      start_offset_seconds = chunk_index * chunk_seconds
      
      IF item.transcription_path == "cloud_api":
        CALL omni_parser tool on chunk_file with retry/backoff:
          attempt = 0
          WHILE attempt <= retry_max:
            try: result = omni_parser(chunk_file, language=config.language)
                 BREAK on success
            on timeout|5xx|network: attempt += 1; sleep(5 * 3^(attempt-1)); CONTINUE
            on 4xx (file format / size): BREAK with permanent failure
          IF still failing AND transcription_preference == auto:
            FALLBACK to local whisper for THIS chunk only (mark item.transcription_path = "hybrid")
          IF still failing AND no fallback allowed:
            UPDATE item.status = FAILED, last_error = "cloud api exhausted retries"
            BREAK out of chunk loop.
      
      ELSE (local_whisper):
        RUN whisper {chunk_file} --model {config.whisper_model} --language {config.language}
            --output_format md --output_dir {output_path}/batches/{batch_id}/.tmp/{item.id}/whisper_out
            with --no-prompts. Read the resulting .md file.
      
      APPEND transcript_segments += { chunk_index, text, start_offset_seconds }
      UPDATE item.chunks_completed += 1
      WRITE _progress.json. (Pattern 7 — living tracker per chunk)
      Do NOT stop. Process ALL chunks for this meeting.
    
    IF item.status == FAILED:
      WRITE _progress.json with FAILED state. CONTINUE to next item.
  
  STAGE D — Stitch:
    See references/phase-c-transcription.md for the stitching algorithm (timestamp
    offset preservation, deduplication of overlap, Markdown frontmatter assembly).
  
  // Pattern 6 — Per-unit Source Fidelity Check (PRE-WRITE GATE)
  FIDELITY CHECK before writing transcript_file:
    - Sum of chunk durations matches item.duration_seconds within ±5s tolerance
    - No chunk text contains placeholder strings ("[TRANSCRIPTION FAILED]" without explicit chunk failure)
    - Stitched timestamps are monotonically increasing
    - Speaker turns (if returned by tool) are tagged consistently
    IF violation: log to item.last_error, attempt 1 retry; if still failing, write transcript with
    a "## Quality Notes" section listing the violation, status remains COMPLETE_WITH_GAPS.
  
  STAGE E — Write outputs:
    WRITE {output_path}/batches/{batch_id}/transcripts/{item.id}-{slug}.md (mandatory tool call, do NOT defer)
    WRITE {output_path}/batches/{batch_id}/metadata/{item.id}-{slug}.json (mandatory tool call)
    See references/phase-c-transcription.md for both output schemas.
  
  // Pattern 1 — Write-Flush-Forget
  UPDATE TRANSCRIPT_INDEX:
    item.status = COMPLETE | COMPLETE_WITH_GAPS
    item.transcript_file = "transcripts/{item.id}-{slug}.md"
    item.metadata_file = "metadata/{item.id}-{slug}.json"
    completed_items += 1
  WRITE {output_path}/_progress.json
  WRITE {output_path}/batches/{batch_id}/00-index.md (in-place update of this row only)
  REMOVE {output_path}/batches/{batch_id}/.tmp/{item.id}/  (clean intermediate audio chunks)
  FLUSH transcript_segments and full transcript text from memory.
  
  LOG: "{item.id} complete. Path: {transcription_path}. Chunks: {chunks_completed}/{chunks_total}. Lines: {N}."
  Do NOT stop. Process ALL items. Continue until completed_items + failed_items + skipped_items == total_items.
```

---

### Step 4: Aggregate Context-Pack Analysis (optional, on by default)

Read `references/phase-d-extraction-analysis.md` before executing this step.

**Command:**
```
IF mode == REPAIR AND no REPAIR_DIRECTIVE targets "analysis" or "global":
  SKIP. LOG: "Step 4 skipped (REPAIR, no analysis directive)."

PURPOSE: extract structured signals targeted at the standard 13 context-pack files
(domain.md, arch-standards.md, tech-policy.md, security.md, constraints.md,
customer-background.md, test-standards.md, env-config.md, best-practices.md,
coding-standards.md, plus decisions log and open questions).

FOR EACH item in TRANSCRIPT_INDEX.items WHERE status starts with COMPLETE:
  // Pattern 5 — load THIS transcript only, not the full set
  LOAD {output_path}/batches/{batch_id}/transcripts/{item.transcript_file}
  EXTRACT structured signals (see phase-d-extraction-analysis.md for the field map and
  the "decision keyword" detection rules).
  APPEND to extraction_buffer (this is per-section, not full text — only structured
  bullets keyed to context-pack file names).
  FLUSH transcript text from memory.

WRITE {output_path}/batches/{batch_id}/meeting-analysis.md with the standard sections (For domain.md,
For arch-standards.md, …, Decisions Log, Open Questions, Meeting Sources). Each
bullet must cite the source meeting id and timestamp (when extracted from a
timestamped chunk).

UPDATE TRANSCRIPT_INDEX.aggregate_analysis_file = "meeting-analysis.md"
WRITE _progress.json.
LOG: "Step 4 COMPLETE. meeting-analysis.md written."
```

---

### Step 5: Validation, Audit & LAST ACTION

Read `references/phase-e-output-assembly.md` before executing this step.

**Command:**
```
VALIDATION GATE — load final outputs from disk (do NOT use memory):
  1. Every item with status COMPLETE/COMPLETE_WITH_GAPS has a transcript_file and a metadata_file on disk.
  2. count(transcripts/*.md) == count(items WHERE status starts with COMPLETE).
  3. Each metadata JSON parses cleanly and contains the required fields
     (duration_seconds, chunks_total, chunks_completed, transcription_path,
     model_used, language, source_file, created_at, file_hashes).
  4. meeting-analysis.md exists and contains the standard sections IF Step 4 ran.
  5. Summary counts in 00-index.md match TRANSCRIPT_INDEX.completed_items
     (verify by counting actual rows; do NOT take stated counts on faith).
  IF mismatch: fix in place, then re-verify.

WRITE {output_path}/batches/{batch_id}/TRANSCRIPT-AUDIT-{batch_id}-{SESSION_ID}.md with:
  - Session metadata (session_id, mode, started, completed, source_path, output_path, batch_id, batch_id_source)
  - Dependencies report (which were already installed, which the skill installed)
  - Pre-flight report (disk, network, omni_parser availability)
  - Per-item table (id, source_file, duration, transcription_path, status, retry_attempts, last_error)
  - Failure analysis (any FAILED items with the specific failure category)
  - REPAIR log (if mode == REPAIR)
  - Open questions (e.g., low-confidence chunks, missing audio streams, batch_id_unresolved)
  See references/phase-e-output-assembly.md for the exact template.

WRITE {output_path}/_batches.md (top-level cross-batch index):
  IF the file does not exist: create with header (`| batch_id | meetings | duration | status | analysis | last_run |`).
  Compute the row for THIS batch from on-disk artifacts (count of transcripts/*.md,
  sum of metadata.duration_seconds, status from TRANSCRIPT_INDEX, path to
  meeting-analysis.md, current ISO timestamp).
  IF a row for {batch_id} already exists: replace it in place. Do NOT duplicate.
  Preserve all other rows verbatim. The row format:
    | {batch_id} | {N transcripts} | {HH:MM:SS total} | {COMPLETE | COMPLETE_WITH_GAPS | PARTIAL | FAILED} | batches/{batch_id}/meeting-analysis.md | {ISO} |
  Downstream skills read this file to enumerate batches without scanning the tree.

LAST ACTION — MANDATORY:
  WRITE _progress.json with status=COMPLETED, completed_at timestamp, and
  current_batch_id={batch_id}. The orchestrator anchor stays at {output_path}/_progress.json.

Memory Bank — MANDATORY session-end writes:
  Overwrite context-pack/active-context.md with this session's status, batch_id,
  batch_id_source, key decisions (e.g., dependency auto-installs), blockers, and
  the list of transcripts produced (qualified with batch_id).
  Append one milestone row to context-pack/progress.md:
    | {SESSION_ID} | {date} | harvesting-meeting-context | {mode} | COMPLETE | **batch={batch_id}: {N} transcripts ({W} with gaps), 1 analysis** | {summary} |
  See execution-protocol.md §4 for schema.

LOG: "Step 5 COMPLETE. batch={batch_id}: {N} transcripts, {M} metadata files, {Q} failed. Audit + _batches.md updated."
```

---

## Status Protocol

Every item in TRANSCRIPT_INDEX.items carries one of these statuses:

| Status | Meaning |
|--------|---------|
| `PENDING` | Discovered in Step 2, not yet transcribed |
| `PROCESSING` | Step 3 is currently working on this item |
| `COMPLETE` | Transcript and metadata both written; fidelity check passed |
| `COMPLETE_WITH_GAPS` | Outputs written but fidelity check found a tolerable issue (logged in transcript "Quality Notes") |
| `FAILED` | Transcription exhausted retries / fallback not allowed; no transcript file written |
| `SKIPPED` | Pre-flight skip (corrupt, no audio stream, REPAIR-not-targeted) |

## Source Tagging

Every bullet in `meeting-analysis.md` cites its source: `(meeting-03 @ 12:34)`.
Every metadata JSON includes `source_file` (absolute path) and `source_sha256`.

## Upstream Consistency Rules

This skill is a utility — it does not consume PRD/Epic/ADR IDs. The only upstream
consistency rule is:

1. **Source file integrity:** every transcript file's `source_sha256` in metadata
   must match a re-hash of the source file at audit time. If the source moved or
   was edited mid-run, mark the item as `COMPLETE_WITH_GAPS` and log a quality note.

2. **Tool fidelity:** the `model_used` field in metadata must reflect the actual
   tool that produced each chunk's text. For hybrid items (cloud + whisper
   fallback), the metadata records both, per chunk.

3. **Zero Invention:** never synthesize content that wasn't in the audio. If a
   chunk fails after retries and fallback, write a `[CHUNK NN UNAVAILABLE]`
   placeholder — do NOT paraphrase from neighboring chunks.

## REPAIR Targets — Reference

All REPAIR directives operate within the resolved `batch_id` namespace; pass
`batch_id` explicitly when running REPAIR against a specific batch.

| Target form | Effect |
|-------------|--------|
| `meeting-NN <directive>` | Re-run Step 3 for that meeting only (within the resolved batch) |
| `dependency:{name} reinstall` | Force-reinstall a dependency (ffmpeg, whisper) and re-run from Step 2 for items that failed due to that dep |
| `analysis regenerate` | Re-run Step 4 only (regenerate `meeting-analysis.md` for this batch) |
| `batch:{batch_id} <directive>` | Scope a directive to a specific batch when multiple batches share an `output_path`. Useful in playlists running cross-batch repairs |
| `global` | Re-run all steps for this batch (rare; equivalent to BUILD with the existing batch folder) |

## Downstream Integration Contract

Downstream skills (`researching-prd`, `scaffolding-aipod-repository`,
`researching-bounded-contexts`) consume `meeting-analysis.md`. They MAY operate in
two modes:

**Single-batch mode** — receive an explicit `meeting_analysis_path`:
```
{output_path}/batches/{batch_id}/meeting-analysis.md
```

**Multi-batch fan-out mode** — read `{output_path}/_batches.md` to enumerate
batches in scope, then load each batch's `meeting-analysis.md` and merge bullets
deduplicated by content (citations remain qualified with `(batch={batch_id},
meeting-NN @ HH:MM:SS)` so traceability survives the merge).

Each `meeting-analysis.md` frontmatter includes `batch_id:` and `source_meetings:`
fields, enabling downstream filtering without path coupling. Each per-meeting
metadata JSON also includes `batch_id` so downstream traceability tools can join
across batches.

## Reference Files

- `references/phase-a-environment-setup.md` — Dependency detection state machine, OS-aware install commands, pre-flight checks
- `references/phase-b-preprocessing.md` — File discovery, ffprobe parsing, chunking decision tree, slug derivation
- `references/phase-c-transcription.md` — Dual-path orchestration, retry/backoff, fallback rules, stitching algorithm, per-meeting output schemas
- `references/phase-d-extraction-analysis.md` — Context-pack signal extraction rules, decision-keyword detection, citation format
- `references/phase-e-output-assembly.md` — Audit template, validation checks, summary count verification

## Related Skills

- `humanize-spec` — Renders `meeting-analysis.md` and `TRANSCRIPT-AUDIT` for stakeholder review
- `researching-prd` / `scaffolding-aipod-repository` — Common downstream consumers of `meeting-analysis.md`

## Open Questions

Registered at run time in `TRANSCRIPT_INDEX.open_questions` and rendered in the audit. Examples:
- Items with `COMPLETE_WITH_GAPS` should be reviewed for the specific quality note.
- If `omni_parser` is unavailable on a `cloud_only` preference, the run aborts in Step 1
  STOP-GATE rather than silently falling back; the user's preference is respected.
