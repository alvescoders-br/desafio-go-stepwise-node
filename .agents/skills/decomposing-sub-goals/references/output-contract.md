# decomposing-sub-goals — Output Contract

## Context Contract

- **Inputs:** `DECOMPOSITION_INDEX.sub_goals[]` (from Step 3 chunking).
- **Outputs:** `{output_folder}/SUB-GOAL-DECOMPOSITION-{SESSION_ID}.json` (primary,
  SESSION_ID-stamped so concurrent instances in a shared folder never collide) and
  `{output_folder}/SUB-GOAL-DECOMPOSITION-AUDIT-{SESSION_ID}.md`.
- **Carries Forward:** `sub_goal_decomposition_path` (the written JSON path) into
  the §11 sidecar.
- **Flush After:** the JSON string once written and re-read for validation.
- **Dependency:** Step 3 (Chunking) COMPLETE.
- **H1 Title:** `# {project_name} -- Sub-Goal Decomposition`

## Mode-Specific Behavior

- **BUILD:** Serialize `DECOMPOSITION_INDEX.sub_goals[]` to the schema below and
  write `SUB-GOAL-DECOMPOSITION-{SESSION_ID}.json` (full-file `Write`).
- **REPAIR:** reuse the SESSION_ID from the existing `SUB-GOAL-DECOMPOSITION-AUDIT-*.md`
  filename, load THAT session's `SUB-GOAL-DECOMPOSITION-{SESSION_ID}.json` (never merely
  the newest JSON in a possibly-shared folder), apply only the targeted directives,
  preserve untargeted sub-goals verbatim, rewrite IN PLACE (same SESSION_ID-stamped
  path). Bump the audit `version` (semver patch) and append a `## Repair History`
  entry (execution-protocol.md §7).

## The Schema (hard obligation — contract §5.1)

`SUB-GOAL-DECOMPOSITION-{SESSION_ID}.json` MUST validate against:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "SUB_GOAL_DECOMPOSITION",
  "type": "object",
  "required": ["sub_goals"],
  "additionalProperties": false,
  "properties": {
    "sub_goals": {
      "type": "array",
      "minItems": 0,
      "maxItems": 100,
      "items": {
        "type": "object",
        "required": ["title"],
        "additionalProperties": false,
        "properties": {
          "title":        { "type": "string", "minLength": 1, "maxLength": 255 },
          "description":  { "type": "string", "maxLength": 4000 },
          "requirements": { "type": "string", "maxLength": 8000 }
        }
      }
    }
  }
}
```

### Field rules

- `sub_goals` — REQUIRED. Array order = iteration order (index 0 runs first).
  `[]` is valid: it means zero iterations (empty backlog), a legitimate outcome,
  NOT an error.
- `title` — REQUIRED, non-empty, `<= 255` chars, UNIQUE across the array.
  Imperative and traceable to the chunk's epic(s).
- `description` — OPTIONAL, `<= 4000` chars. State what the chunk delivers and
  cite every grouped epic id. Strongly preferred (the autoloop consumes it as
  `sub_goal_description`).
- `requirements` — OPTIONAL, `<= 8000` chars. Acceptance criteria / constraints
  for the whole chunk (the autoloop consumes it as `sub_goal_requirements`).
- No other keys. `additionalProperties: false` is strict — `from_epics`, scores,
  and provenance live in the AUDIT and the INDEX, NOT in the JSON.

## Validation (pre-write gate, Step 4)

Verify BEFORE writing, and re-read from disk AFTER writing:

- [ ] JSON parses.
- [ ] `sub_goals` is an array with `0 <= length <= min(max_sub_goals, 100)`.
- [ ] Every item has a non-empty, unique `title <= 255` chars.
- [ ] `description <= 4000`, `requirements <= 8000` where present.
- [ ] No key outside `title` / `description` / `requirements` on any item.
- [ ] Stated sub-goal count in the AUDIT == `len(sub_goals)` (fix the stated count
      if it drifts — count from the data source, not memory).

If a check fails: correct the object and re-write. If still failing after one
retry, do NOT emit a partial/invalid file — write the AUDIT Gap Report and exit
so the group is not driven by a malformed loop source.

## Audit file

`SUB-GOAL-DECOMPOSITION-AUDIT-{SESSION_ID}.md` records (human-lightweight):
provenance (`prd_path`, `epics_path`, `chunking_criteria`), a chunk→epic mapping
table with per-chunk score + `scope_warning`, the stated sub-goal count,
`open_questions` (deferred chunks, un-sliceable epics), and — in REPAIR — the
version bump + `## Repair History` delta.

## Source Fidelity Check (before writing)

- [ ] Every title traces to at least one real epic id in the INDEX.
- [ ] No invented epic ids, no invented requirements not grounded in PRD/Epics.
- [ ] Deferred chunks (beyond the 20-cap) are logged in `open_questions`, not
      silently dropped.
- [ ] `additionalProperties: false` respected — no stray keys leaked from the INDEX.

## Post-Section Protocol

1. **Write** `{output_folder}/SUB-GOAL-DECOMPOSITION-{SESSION_ID}.json` — mandatory
   tool call (full-file `Write`). Do NOT defer.
2. **Write** `{output_folder}/SUB-GOAL-DECOMPOSITION-AUDIT-{SESSION_ID}.md`.
3. **Update** `DECOMPOSITION_INDEX`: set `sub_goal_decomposition_path` to the
   absolute path actually written.
4. **Verify** the JSON exists and re-parses from disk against the schema.
5. **Flush** the serialized JSON from memory; retain only `DECOMPOSITION_INDEX`.
6. **Log:** "Decomposition written: {N} sub-goals -> {path}."
