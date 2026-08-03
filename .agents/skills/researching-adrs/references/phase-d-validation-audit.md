# Phase D — Validation & Audit

## Context Contract

- **Inputs:** ADR_INDEX (all phases complete); files at `{adrs_path}/` — load from disk, NOT from memory
- **Outputs:** `{adrs_path}/ADR-AUDIT-{SESSION_ID}.md`
- **Carries Forward:** Nothing — this is the final phase. All outputs written to disk.
- **Flush After:** All loaded file content after writing audit
- **Dependency:** Phase C must be COMPLETE (manifest written and verified)
- **H1 Title:** `# {project_name} — ADR Session Audit`

## Mode-Specific Behavior

- **BUILD:** Generate full audit from ADR_INDEX and output files.
- **REPAIR:** Append repair section to existing audit file. Do NOT overwrite the full audit — add a `## repair_session` section with the new SESSION_ID, directives applied, and outcomes.

---

## Audit File Structure

```markdown
# {project_name} — ADR Session Audit

session: {SESSION_ID}
version: {version}
mode: {MODE}
date: {ISO 8601}

## sources
| Source | Path | Status |
|--------|------|--------|
| PRD | {prd_path} | Loaded |
| Domain Boundaries | {domain_boundaries_path} | Loaded |
| Epics | {epics_path} | {Loaded / Not provided} |
| Current Architecture | {current_architecture_path} | {Loaded / Not provided} |
| Technical Interview | {technical_interview_path} | {Loaded / Not provided} |
| Meeting Recording | {meeting_recording_path} | {Loaded / Not provided} |

## generation_log
| ADR | Category | Affected BCs | Diagram | Gherkin | Fidelity Corrections |
|-----|----------|-------------|---------|---------|---------------------|
```

One row per ADR from ADR_INDEX.completed_adrs.
`Fidelity Corrections` = count of corrections applied during source fidelity check.

```markdown
## chunk_execution_log
| Invocation | resume_from_adr | chunk_size | ADRs Generated | Status |
```

Include only if chunk_size < total_adrs. Otherwise omit this section.

```markdown
## validation_summary
| Check | Result | Details |
|-------|--------|---------|
| Forward traceability | {PASS/FAIL} | {coverage %} |
| Backward traceability | {PASS/FAIL} | {orphan count} |
| Technology neutrality | {PASS/FAIL} | {violation count after corrections} |
| Diagram validation | {PASS/FAIL} | {pass rate} |
| Gherkin validation | {PASS/FAIL} | {pass rate} |
| Count verification | {PASS/FAIL} | {mismatches found} |
| Anti-fade | {PASS/WARN/FAIL} | {delta details} |
```

Source: extract from manifest's validations section.

```markdown
## change_log
| Version | Directive | Target ADR | Change Applied | Impact |
```

REPAIR mode only. One row per REPAIR_DIRECTIVE applied.

---

## Output Verification (mandatory before exit)

Run these checks AFTER writing the audit file, BEFORE reporting completion.

| # | Check | Action on Failure |
|---|-------|-------------------|
| 1 | Manifest (ADR-SPEC-*.md) exists and is non-empty | Regenerate manifest (return to Phase C) |
| 2 | All expected ADR files in adrs/ present (count == TOTAL_ADRS) | List missing ADRs, regenerate each |
| 3 | Audit file (ADR-AUDIT-*.md) exists | This write must succeed — retry once |
| 4 | 00-index.md shows all ADRs as complete | Fix any discrepancies in-place |
| 5 | _progress.json exists | Write if missing |

---

## Source Fidelity Check (before writing audit)

- [ ] Generation log has one row per ADR (count matches TOTAL_ADRS)
- [ ] Validation summary results are consistent with manifest's validations section
- [ ] Sources table matches actual parameters provided (no invented paths)
- [ ] Chunk execution log present only if CHUNK_MODE was used
- [ ] Change log present only if MODE == REPAIR

## Post-Section Protocol

1. **Write** `{adrs_path}/ADR-AUDIT-{SESSION_ID}.md` — MANDATORY TOOL CALL.
2. **Verify** file exists and is non-empty.
3. **Delete** _checkpoint.json (manifest is now the source of truth).
4. **Write** context-pack/active-context.md with session status, key artifacts, blockers.
5. **Append** to context-pack/progress.md: `| {SESSION_ID} | {date} | researching-adrs | {mode} | COMPLETE | **{N} ADRs** | ADR generation complete |`
6. **Update** _progress.json: status = "COMPLETED", completed_at = ISO timestamp.
7. **Log:** "Phase D COMPLETE. Audit written. Session {SESSION_ID} done. {N} ADRs, {M} open questions."
