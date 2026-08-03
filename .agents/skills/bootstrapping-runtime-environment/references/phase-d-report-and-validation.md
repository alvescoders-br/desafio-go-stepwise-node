# bootstrapping-runtime-environment — Phase D: Report Generation & Validation

## Context Contract

- **Inputs:** Fully populated `BOOT_INDEX` (stack, services_running, env_file_path, env_keys_synthesized, env_blockers, migrations_applied, db_ready, decisions_log, port_collisions)
- **Outputs:** `{output_folder}/BOOT-SPEC-{SESSION_ID}.md` (bootstrap report) and `{output_folder}/BOOT-AUDIT-{SESSION_ID}.md` (session metadata)
- **Carries Forward:** `BOOT_INDEX.spec_path`, `BOOT_INDEX.audit_path`, `BOOT_INDEX.env_status`
- **Flush After:** Generated report text — write immediately, do not retain. Memory Bank writes happen in Step 6 (Finalize), not here.
- **Dependency:** Phases A, B, C must be COMPLETE
- **H1 Title:** `# Phase D — Report & Validation`

## Mode-Specific Behavior

- **BUILD:** Generate both files from `BOOT_INDEX`.
- **REPAIR:** Re-load `PRIOR_SPEC`, apply only the changes from REPAIR_DIRECTIVES, rewrite `BOOT-SPEC-*.md` in place (same path, same filename, same SESSION_ID). Append a `## Repair Pass {N}` section at the end of the BOOT-AUDIT documenting what was changed and why.
- **RESUME:** Not applicable.

---

## env_status Derivation

```
env_status = "READY"   IF len(env_blockers) == 0 AND db_ready == true
env_status = "BLOCKED" otherwise
```

Set this on `BOOT_INDEX.env_status` BEFORE generating the report — the report's Section 1
displays this value.

---

## BOOT-SPEC Template

Generate `BOOT-SPEC-{SESSION_ID}.md` with EXACTLY these 8 sections, in this order, with
these headings. Zero prose. Tables and lists only.

```markdown
# Bootstrap Report — {project_name}
session: {SESSION_ID}
generated_at: {ISO 8601}

## 1. Session

| Field | Value |
|---|---|
| session_id | {SESSION_ID} |
| mode | BUILD | REPAIR |
| started_at | {ISO} |
| completed_at | {ISO} |
| env_status | READY | BLOCKED |
| spec_path | {output_folder}/BOOT-SPEC-{SESSION_ID}.md |
| audit_path | {output_folder}/BOOT-AUDIT-{SESSION_ID}.md |

## 2. Stack

| Field | Value | Source |
|---|---|---|
| language | {stack.language} | {first source_evidence.file_path for language} |
| framework | {stack.framework} | {evidence} |
| package_manager | {stack.package_manager} | {evidence} |
| orm | {stack.orm} | {evidence} |
| db_engine | {stack.db_engine} | {evidence} |
| needs_redis | {stack.needs_redis} | {evidence} |
| needs_queue | {stack.needs_queue or "no"} | {evidence} |

Total source_evidence rows: {N}

## 3. Services Running

| name | kind | host | port | container | reused |
|---|---|---|---|---|---|
| {row per services_running entry} | | | | | |

Count: {N} services ({M} reused, {K} spun-up)

## 4. Env Synthesis

### 4a. Keys synthesized ({N})

| key | source | classification |
|---|---|---|
| DATABASE_URL | services_running[db] | synthesized |
| REDIS_URL | services_running[cache] | synthesized |
| AWS_REGION | default eu-west-1 | assumption |
| ... | ... | ... |

### 4b. Blockers ({M})

| kind | key | description | suggested_remediation |
|---|---|---|---|
| missing_secret | SECRET_API_KEY | (description) | (remediation) |
| ... | ... | ... | ... |

### 4c. .env file

Path: {env_file_path}
Total keys written: {N + M}

## 5. Migrations

| tool | command | duration_ms | exit_code | stderr_excerpt |
|---|---|---|---|---|
| prisma | npx prisma db push --accept-data-loss --skip-generate | 4230 | 0 | — |
| ... | ... | ... | ... | ... |

db_ready: {true | false}

## 6. Decisions Log

| phase | decision | evidence |
|---|---|---|
| phase-a | language=node | {source_path}/package.json |
| phase-a | DTR override: source said typeorm, DTR said prisma, using DTR | dtr_path:#Backend.ORM |
| phase-b | reused {kind} container {name} | docker ps {timestamp} |
| phase-c | AWS_REGION assumption: eu-west-1 default | assumption |
| ... | ... | ... |

Count: {N} decisions, {M} assumptions

## 7. Port Collisions

| port | occupying_process | resolved_to |
|---|---|---|
| 5432 | postgres (host) | 5433 |
| ... | ... | ... |

Count: {N} collisions (may be empty)

## 8. Open Questions

| id | type | description | impact |
|---|---|---|---|
| OQ-01 | stack_unknown | could not detect framework | (impact) |
| ... | ... | ... | ... |

Count: {N} open questions
```

### Section-by-section count verification

Before writing, for each section that has a count claim, verify:
```
stated_count == actual_row_count(BOOT_INDEX.{field})
IF mismatch → fix stated_count before writing
LOG: "Fixed summary count in section {N}: stated {X}, actual {Y}"
```

---

## BOOT-AUDIT Template

Generate `BOOT-AUDIT-{SESSION_ID}.md` — lightweight session metadata only, NOT a full
operational report.

```markdown
# Bootstrap Audit — {project_name}
session: {SESSION_ID}
mode: {BUILD | REPAIR}
date: {ISO}
status: {COMPLETE | BLOCKED}

## Pattern Compliance (8 patterns)

| Pattern | Status | Evidence |
|---|---|---|
| P1 Write-Flush-Forget | ✅ | BOOT-SPEC written before BOOT-AUDIT |
| P2 Carry-forward index | ✅ | BOOT_INDEX used across all phases |
| P3 REPAIR folder reuse | ✅ | output_folder used as-is; SESSION_ID in filenames only |
| P4 Surgical REPAIR | ✅ | REPAIR_DIRECTIVES parsed; untargeted phases skipped |
| P5 Mandatory source loading | ✅ | per-phase source loads; no global pre-load |
| P6 Pre-write fidelity check | ✅ | Phase D check ran before BOOT-SPEC write |
| P7 Living progress tracker | ✅ | _progress.json updated per phase |
| P8 Domain/infra separation | ✅ | execution-protocol.md mechanics delegated, not inlined |

## Files Written

| Path | Lines | Status |
|---|---|---|
| BOOT-SPEC-{SESSION_ID}.md | {N} | ✅ written |
| .env | {M} | ✅ written |
| BOOT-AUDIT-{SESSION_ID}.md | {K} | ✅ written |

## Phase Timing

| Phase | Duration ms | Skipped (REPAIR) |
|---|---|---|
| A — Stack detection | {ms} | no |
| B — Service provisioning | {ms} | no |
| C — Env + migrations | {ms} | no |
| D — Report + validation | {ms} | no |

## REPAIR Pass (if applicable)

(One section per repair pass — append, do not overwrite)

### Repair Pass {N} — {ISO}

| Directive | Target | Outcome |
|---|---|---|
| (row per REPAIR_DIRECTIVE) | | |

Changed sections of BOOT-SPEC: {list}
Preserved sections: {list}

## Open Issues

(Carry-forward from BOOT-SPEC Section 8 — same rows, no additional analysis)
```

---

## REPAIR Mode: Surgical Rewrite

When `MODE == REPAIR`:

```
LOAD PRIOR_SPEC from disk (BOOT-SPEC-{SESSION_ID}.md — SESSION_ID extracted in Step 1)
PARSE PRIOR_SPEC sections into a map { section_heading → content }

FOR EACH REPAIR_DIRECTIVE:
  CASE directive.target:
    "stack" | "phase-a"        → replace Section 2 from current BOOT_INDEX
    "services" | "phase-b"      → replace Section 3 from current BOOT_INDEX
    "env" | "phase-c"           → replace Section 4 from current BOOT_INDEX
    "migrations"                → replace Section 5 from current BOOT_INDEX
    "env_keys_synthesized.{K}"  → edit one row in Section 4a (preserve all others)
    "decisions"                 → replace Section 6 from current BOOT_INDEX
    "global"                    → replace ALL sections from current BOOT_INDEX

REGENERATE Section 1 (Session) — always (env_status and completed_at change)
PRESERVE every other section's content VERBATIM (do not touch it)

WRITE rewritten BOOT-SPEC-{SESSION_ID}.md (overwrite same path)

APPEND `## Repair Pass {N}` to BOOT-AUDIT-{SESSION_ID}.md (do not overwrite the audit)
```

---

## Source Fidelity Check (before writing BOOT-SPEC)

- [ ] All 8 section headings are present (Session, Stack, Services Running, Env Synthesis, Migrations, Decisions Log, Port Collisions, Open Questions)
- [ ] Section 1's `env_status` matches the derivation rule (READY iff zero env_blockers AND db_ready)
- [ ] Every count claim in section headers matches the actual row count
- [ ] No prose paragraphs — every section is a table or bulleted list
- [ ] Every row in Section 4a has a `source` column populated
- [ ] Every row in Section 6 has an `evidence` column populated
- [ ] REPAIR mode: preserved sections are byte-identical to PRIOR_SPEC where applicable

## Post-Section Protocol

1. **Write** `{output_folder}/BOOT-SPEC-{SESSION_ID}.md`. MANDATORY TOOL CALL.
2. **Write** `{output_folder}/BOOT-AUDIT-{SESSION_ID}.md`. MANDATORY TOOL CALL.
3. **Update** `BOOT_INDEX.spec_path`, `BOOT_INDEX.audit_path`, `BOOT_INDEX.env_status`
4. **Update** `_progress.json`: `completed: 4`, `items[3] = { phase: "report-and-validation", status: "COMPLETE" }`
5. **Flush** generated report text from memory — only `BOOT_INDEX` survives for Step 6 Finalize
6. **Verify** both files exist at the recorded paths and are non-empty; re-parse BOOT-SPEC to confirm Section 1 env_status matches `BOOT_INDEX.env_status`
7. **Log:** `"Phase D COMPLETE. BOOT-SPEC: {N} lines, env_status: {env_status}. Audit: {M} lines."`
