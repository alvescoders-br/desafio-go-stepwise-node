---
session_id: ENGINEERING-HARVESTINGMEETINGCONTEXT-20260430
mode: BUILD
date: 2026-04-30T13:14:07Z
source: new skill (BUILD mode); inspiration: /Users/guillermo.meyer/.coda/skills/transcribe-meetings/SKILL.md
status: complete
---

# harvesting-meeting-context — Engineering Audit

## Session Summary

| Field | Value |
|-------|-------|
| skill_name | harvesting-meeting-context |
| output_path | /Users/guillermo.meyer/Documents/globai-repos/aipods-agents-skills/.agents/skills/harvesting-meeting-context |
| mode | BUILD |
| inspiration | /Users/guillermo.meyer/.coda/skills/transcribe-meetings/SKILL.md (119-line human-first skill, no chunking, no retry, no REPAIR, no auto-install) |
| files_written | 8 (SKILL.md + 5 references + evals.json + this audit; _progress.json present from Step 1) |
| total_lines | 1,987 (SKILL.md 537 + 5 reference files 1,450) |
| pattern_compliance | 7/7 hardened patterns + Pattern 8 (Domain/Infra Separation) present |
| anti_patterns_fixed | 0 (BUILD from scratch — no anti-patterns introduced) |
| evals_generated | 3 |
| reference_file_count | 5 |
| output_pattern | manifest_per_item |
| carry_forward_index | TRANSCRIPT_INDEX |
| chunking_needed | yes (audio 5-min segments per source file) |

## Intent Extraction (Phase A — BUILD)

| Field | Value |
|-------|-------|
| Primary action | Transcribe meeting audio/video files into structured markdown notes |
| Input artifacts | mp3, m4a, wav, mp4 files from a meetings input folder |
| Output artifacts | per-meeting transcripts/*.md, per-meeting metadata/*.json, manifest.md, 00-index.md, meeting-analysis.md, TRANSCRIPT-AUDIT-*.md |
| SDLC pipeline position | utility / cross-cutting (discovery phase). Upstream: human meetings. Downstream consumers: researching-prd, scaffolding-aipod-repository, researching-bounded-contexts |
| Estimated output size | SKILL.md ~500 lines, references 1,400 lines (matches actual: 537 + 1,450 = 1,987 — one-off prediction, no chunking required for the SKILL.md generation itself) |

## Architecture Decisions (Phase B)

| Decision | Value | Why |
|----------|-------|-----|
| output_pattern | manifest_per_item | Each meeting is independent; long meetings produce 600–1,500 line transcripts; per-item REPAIR is essential |
| reference_file_count | 5 | Phase A (env), B (preprocessing), C (transcription — heaviest), D (analysis), E (validation/audit). Each <300 lines target |
| chunking_needed | yes | Audio chunked into 5-min segments to fit cloud API's 300s timeout (the original failure mode the user reported) |
| chunk_seconds | 300 (configurable) | 30s safety margin under the API's 300s read timeout |
| carry_forward_index | TRANSCRIPT_INDEX | Specific name reflects domain (audio inventory + dependency state + per-item progress) |
| progress_json_needed | yes | Long runs (10+ meetings × 5+ chunks) easily exceed 30 min — RESUME support is required |
| upstream_id_namespaces | (none) | Utility skill; consumes audio files, not pipeline IDs |

## Reference File Map

| File | Phases | Estimated lines | Actual lines | Complexity |
|------|--------|----------------|--------------|-----------|
| phase-a-environment-setup.md | dependency detection + auto-install + pre-flight | 220 | 209 | medium |
| phase-b-preprocessing.md | discovery + ffprobe + chunking decision tree | 240 | 213 | medium |
| phase-c-transcription.md | dual-path orchestration + retry/backoff + stitching + per-item output schemas | 300 | 446 | high (the most complex phase — encodes the entire fix for the user's reported timeout failure) |
| phase-d-extraction-analysis.md | context-pack signal extraction + decision detection | 220 | 316 | medium |
| phase-e-output-assembly.md | validation gate + audit template + LAST ACTION | 220 | 266 | medium |

phase-c overran the estimate intentionally — the file encodes the dual-path
fallback, exponential backoff, error classification, and stitching algorithm.
Splitting it would have separated tightly-coupled logic (e.g., the cloud-fallback
path needs the chunk index and the retry classifier in the same place).

## Pattern Compliance

| Pattern ID | Pattern Name | Status | Evidence |
|------------|-------------|--------|---------|
| P1 | Write-Flush-Forget | ✅ present | SKILL.md Step 3 per-chunk flushes (`WRITE _progress.json` + `del transcript_segments`); per-item `rm -rf .tmp/{item.id}/`; phase-c.md "FLUSH per-chunk whisper temp output" inside chunk loop |
| P2 | Carry-Forward Index | ✅ present | `TRANSCRIPT_INDEX = {...}` defined in SKILL.md "Carry-Forward Contract" section with 11 top-level fields; all phases update specific fields, no full text carried |
| P3 | REPAIR Folder Reuse | ✅ present | SKILL.md Step 1: "NOTE: output_path MUST already exist. Never mkdir for REPAIR." Each phase reference file's Mode-Specific Behavior also explicitly states this |
| P4 | Surgical REPAIR | ✅ present | SKILL.md Step 1: "PARSE failure_feedback → REPAIR_DIRECTIVES = [{ target, instruction, reason }]". Step 3 loop: "IF mode == REPAIR AND no REPAIR_DIRECTIVE targets this meeting (target != item.id AND target != 'global'): SKIP". REPAIR target reference table at SKILL.md tail |
| P5 | Mandatory Source Loading | ✅ present | phase-b: ffprobe per file inside loop; phase-c Stage 0 "RELOAD item.source_file metadata from disk via ffprobe (do not assume Step 2 cache)"; phase-d "LOAD '{output_path}/batches/{batch_id}/transcripts/{item.transcript_file}' inside loop" |
| P6 | Per-Unit Fidelity Check | ✅ present | phase-b: pre-write check before appending item; phase-c Stage E.2: 7-item pre-write checklist before WRITE; phase-d: 6-item pre-write checklist before meeting-analysis.md; phase-e: 6-check Validation Gate |
| P7 | Living Progress Tracker | ✅ present | SKILL.md Step 1.6 writes 00-index.md "with header (mode, session, started timestamp) and an empty items table marked '[ ] TO BE DISCOVERED'"; updated per-item in Step 3; updated again in Step 4 and Step 5 |
| P8 | Domain/Infra Separation | ✅ present | FIRST ACTION block with inline _progress.json schema; LAST ACTION block at phase-e tail; Memory Bank session-end writes block in phase-e Post-Section Protocol step 4. Skill does NOT include SESSION_ID construction formula (delegates to execution-protocol.md §1) — verified by grep returning zero matches |

## Anti-Patterns Report (BUILD-time scan)

| ID | Name | Severity | Found In | Fix Applied |
|----|------|----------|---------|-------------|
| AP-01 | TEMP_BUFFER accumulation | — | none | n/a — every loop body in SKILL.md Step 3 and phase-c writes immediately after chunk transcription; phase-d uses `extraction_buffer` only as a section-keyed registry of bullet strings (per-meeting payload is small + flushed before next meeting) |
| AP-02 | Session ID in REPAIR folder | — | none | n/a — SKILL.md explicitly states folder is reused, session id only in audit filename |
| AP-03 | Lightweight Phase 1 | — | none | n/a — every loop body has a per-unit LOAD step; phase-c Stage 0 explicitly re-probes |
| AP-04 | Flush without index update | — | none | n/a — every loop ends with: WRITE → UPDATE INDEX → UPDATE tracker → FLUSH |
| AP-05 | Global REPAIR | — | none | n/a — REPAIR_DIRECTIVES parsing + per-item skip |
| AP-06 | `{{variable}}` syntax | — | none | grep returned 0 matches across SKILL.md and references/ |
| AP-07 | Hardcoded tool/framework names | low | (allowed locations) | Tool names (ffmpeg, ffprobe, openai-whisper, omni_parser, brew, apt-get, dnf, pip3, sha256sum) appear by design — this is a tooling skill that orchestrates these specific binaries. Their use is scoped to dependency tables, install matrices, and probe commands. They do NOT appear in the meeting-analysis.md output (which is technology-neutral by detector design — see phase-d "tech-policy.md" detector that *forwards* tool names from meetings without adding more) |
| AP-08 | Summary counts not verified | — | none | phase-b Post-Section Protocol step 6 verifies count from disk, phase-c Step 3 final verify, phase-e Validation Gate Check 5 |
| AP-09 | FOR EACH without continuation | — | none | grep: 11 FOR EACH loops across SKILL.md+references, 14 "Do NOT stop" mandates (some loops have multiple) |
| AP-10 | Fidelity check only in audit | — | none | Pre-write fidelity gates in phase-b, phase-c Stage E.2, phase-d. Phase-e Validation Gate is the *additional* post-disk gate, not the only one |
| AP-11 | SESSION_ID construction formula | — | none | grep `SESSION_ID = "` returned 0 matches |
| AP-12 | _shared/references | — | none | grep `_shared` returned 0 matches |
| AP-13 | Pattern 8 callouts missing | — | none | FIRST ACTION (SKILL.md Step 1), LAST ACTION (phase-e tail), Memory Bank session-end writes (phase-e Post-Section Protocol step 4) all present |

## Reference Files Gate

| File | Sections Present | Status |
|------|-----------------|--------|
| references/phase-a-environment-setup.md | 5/5 (Context Contract / Mode-Specific / Content / Source Fidelity / Post-Section Protocol) | ✅ pass |
| references/phase-b-preprocessing.md | 5/5 | ✅ pass |
| references/phase-c-transcription.md | 5/5 + per-item Post-Section Protocol + post-loop Post-Section Protocol | ✅ pass |
| references/phase-d-extraction-analysis.md | 5/5 | ✅ pass |
| references/phase-e-output-assembly.md | 5/5 | ✅ pass |

All Context Contract sub-fields (Inputs, Outputs, Carries Forward, Flush After, Dependency, H1 Title) present in every reference file.

## Files Written

| Path | Lines | Status |
|------|-------|--------|
| SKILL.md | 537 | ✅ written |
| references/phase-a-environment-setup.md | 209 | ✅ written |
| references/phase-b-preprocessing.md | 213 | ✅ written |
| references/phase-c-transcription.md | 446 | ✅ written |
| references/phase-d-extraction-analysis.md | 316 | ✅ written |
| references/phase-e-output-assembly.md | 266 | ✅ written |
| evals/evals.json | (3 evals) | ✅ written |
| ENGINEERING-AUDIT-ENGINEERING-HARVESTINGMEETINGCONTEXT-20260430.md | (this file) | ✅ written |
| _progress.json | (initial bootstrap from Step 1; orchestrator updates as the engineering session progresses) | ✅ written |

## Open Questions

| ID | Type | Description | Impact |
|----|------|-------------|--------|
| OQ-01 | runtime-binding | The skill assumes `omni_parser` is bound as an MCP tool in the Stepwise harness when present. Naming and call shape may vary across deployments. The skill records `dependencies.omni_parser.reason_unavailable` when it cannot find the tool, which is enough for graceful degradation, but a Stepwise capability YAML wrapping this skill should document which MCP server provides omni_parser | medium |
| OQ-02 | install-permissions | Auto-install on Linux requires sudo for apt-get/dnf. In non-interactive runtimes without sudo, the skill aborts cleanly with a blocker. A future enhancement could attempt `pip3 install --user` and `conda install -c conda-forge ffmpeg` as sudo-free fallbacks for restricted environments | low |
| OQ-03 | speaker-diarization | Local whisper does not provide speaker labels by default. Hybrid items (some chunks via cloud_api with speakers, some via whisper without) will have inconsistent speaker fields. The metadata's `speaker_diarization` flag should be added in v1.1 to make the inconsistency machine-readable | low |
| OQ-04 | catalog-registration | execution-protocol.md Artifact Type Registry does not yet include `transcripts` count for `harvesting-meeting-context`. Need to add an entry so the Memory Bank progress.md row uses the specific count rather than a generic count | medium |

## Generation Summary

- skill type: tooling utility (not in main SDLC pipeline)
- output pattern: manifest + per-item (transcripts/, metadata/) + aggregate analysis
- index name: TRANSCRIPT_INDEX
- _progress.json: yes (RESUME support for long runs)
- modes supported: BUILD, REPAIR (REPAIR_DIRECTIVES targets: meeting-NN, dependency:{name}, analysis, global)
- platform support: macOS (brew) + Linux (apt-get, dnf); auto_install can be disabled
- failure mode the skill prevents: cloud API 300s timeout on long audio (the original user-reported failure on a 17 MB MP3) — addressed via chunking, retry, and dual-path fallback to local whisper
- overall status: complete; ready for Stepwise deployment (no capability YAML wrapping it yet — that is a separate task via `create-capability`)
