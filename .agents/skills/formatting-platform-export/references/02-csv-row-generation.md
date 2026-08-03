# CSV Row Generation — Shared Platform Engine

## Context Contract
- **Called from:** SKILL.md Step 4 (Implement — Atomic Per-Epic Loop)
- **Inputs per iteration:** Epic metadata from EXPORT_INDEX, full story file
  from disk, PLATFORM_SCHEMA loaded in Step 3.
- **Outputs per iteration:** Rows appended to OUTPUT_FILE.
- **Carries forward:** EXPORT_INDEX + PLATFORM_SCHEMA (never flushed).
- **Flush after each epic:** Story file content and row buffers only.
- **Dependencies:** Platform schema MUST be loaded before this file is used.

> This file contains the shared loop protocol and transformation helpers.
> It does NOT contain column definitions — those come from PLATFORM_SCHEMA.
> When this file says "PLATFORM_SCHEMA.EPIC_FIELD_MAP", it means the map
> loaded from whichever platform schema reference was read in Step 3.

---

## Atomic Per-Epic Loop — Full Protocol

### Performance Configuration

```
# ── Batch Size Control ────────────────────────────────────────────────────
MAX_EPICS_PER_BATCH = 50  # Maximum epics processed in a single run
                          # Adjust based on platform limits and backlog size

# ── Resume Capability ─────────────────────────────────────────────────────
# EXPORT_INDEX tracks:
#   - last_processed_epic_index: int (default: 0)
#   - batch_start_time: timestamp
#   - batch_end_time: timestamp (null during processing)
```

### Main Loop with Pagination

```
# ── PHASE 0: Batch Setup ──────────────────────────────────────────────────
start_index = EXPORT_INDEX.get("last_processed_epic_index", 0)
total_epics = len(EXPORT_INDEX.epic_ids)
end_index = min(start_index + MAX_EPICS_PER_BATCH, total_epics)

LOG: "Processing epics {start_index + 1} to {end_index} of {total_epics}"
EXPORT_INDEX.batch_start_time = current_timestamp()
processed_count = 0

FOR epic_index in range(start_index, end_index):
  epic_entry = EXPORT_INDEX.epic_ids[epic_index]

  # ── PHASE 1: Source Loading ──────────────────────────────────────────────
  epic_id    = epic_entry.id
  epic_title = epic_entry.title
  epic_tier  = epic_entry.priority_tier
  epic_kpis  = epic_entry.kpi_ids
  epic_rsks  = epic_entry.rsk_ids
  epic_theme = epic_entry.theme

  story_file = STORY_REGISTRY[epic_id].file_path
  IF story_file does not exist on disk:
    LOG gap: "Story file not found for {epic_id}: {story_file}"
    EXPORT_INDEX.gaps.append({ epic: epic_id, reason: "story file missing" })
    CONTINUE

  READ story_file in full.
  LOG: "Loaded {epic_id} from {story_file} ({epic_index + 1}/{total_epics})"

  # ── ZERO INVENTION CHECKPOINT ────────────────────────────────────────────
  IF epic_title is empty:
    LOG gap: "Epic title missing for {epic_id}" → SKIP → CONTINUE
  story_entries = parse_stories(story_file)
  IF story_entries is empty:
    LOG gap: "No stories parsed from {story_file}" → SKIP → CONTINUE

  # ── PHASE 2: Story-level scope filter ────────────────────────────────────
  IF export_scope == "selected" AND EXPORT_INDEX.selected_story_ids not empty:
    story_entries = [s for s in story_entries
                     if s.id in EXPORT_INDEX.selected_story_ids]
    IF story_entries is empty:
      LOG: "{epic_id}: no selected stories — exporting Epic row only."

  # ── PHASE 3: Generate Epic row ───────────────────────────────────────────
  epic_key = build_epic_key(epic_entry, PLATFORM_SCHEMA, EXPORT_INDEX.platform_key)
  # epic_key is the platform-specific identifier stored for child story linking.
  # Its meaning differs per platform (see § Epic Key below).
  epic_entry.platform_key = epic_key   # store for story rows to reference

  epic_row = build_row(
    field_map:  PLATFORM_SCHEMA.EPIC_FIELD_MAP,
    source:     epic_entry,
    defaults:   PLATFORM_SCHEMA.DEFAULTS,
    epic_key:   epic_key,
    platform:   delivery_platform
  )

  # ── PHASE 4: Generate Story rows ─────────────────────────────────────────
  story_rows = []
  FOR EACH story in story_entries:
    row = build_row(
      field_map:  PLATFORM_SCHEMA.STORY_FIELD_MAP,
      source:     story,
      defaults:   PLATFORM_SCHEMA.DEFAULTS,
      epic_entry: epic_entry,   # for inherited fields (priority, epic_key)
      platform:   delivery_platform
    )
    story_rows.append(row)

  # ── PHASE 5: Pre-Write Fidelity Check ────────────────────────────────────
  n_cols = len(PLATFORM_SCHEMA.COLUMN_HEADERS)
  FOR EACH row in [epic_row] + story_rows:
    IF len(row) != n_cols:
      LOG violation: "Column count {len(row)} != expected {n_cols} for {epic_id}"
      Pad with PLATFORM_SCHEMA.DEFAULTS[""] or trim to n_cols.
  FOR EACH story_row in story_rows:
    IF story_row[epic_link_col] != epic_key:
      LOG violation: "Epic link mismatch for {story.id} — correcting."
      story_row[epic_link_col] = epic_key
  IF any story.id not in STORY_REGISTRY[epic_id].story_ids:
    LOG violation: "Invented story ID detected — discard row."
    Remove offending row from story_rows.

  # ── PHASE 6: Write ───────────────────────────────────────────────────────
  APPEND encode_row(epic_row)  to OUTPUT_FILE  (TOOL CALL)
  FOR EACH story_row in story_rows:
    APPEND encode_row(story_row) to OUTPUT_FILE (TOOL CALL or bulk append)
  LOG: "Appended {epic_id}: 1 epic row + {len(story_rows)} story rows."

  # ── PHASE 7: Update EXPORT_INDEX ─────────────────────────────────────────
  EXPORT_INDEX.epics_exported.append(epic_id)
  EXPORT_INDEX.stories_exported.extend([s.id for s in story_entries])
  EXPORT_INDEX.rows_written += 1 + len(story_rows)
  EXPORT_INDEX.assumptions.extend(
    [s.id + ": " + a for s in story_entries for a in s.assumptions]
  )
  EXPORT_INDEX.gaps.extend([gap detected during row building])

  # ── PHASE 8: Flush ───────────────────────────────────────────────────────
  FLUSH: story_file content, story_entries, epic_row buffer, story_rows buffer.
  RETAIN: EXPORT_INDEX, PLATFORM_SCHEMA, STORY_REGISTRY.
  VERIFY: OUTPUT_FILE size increased since previous write.
  
  # ── PHASE 9: Progress Tracking ───────────────────────────────────────────
  processed_count += 1
  EXPORT_INDEX.last_processed_epic_index = epic_index + 1

# ── End of Batch ────────────────────────────────────────────────────────────
EXPORT_INDEX.batch_end_time = current_timestamp()
batch_duration = EXPORT_INDEX.batch_end_time - EXPORT_INDEX.batch_start_time

IF end_index >= total_epics:
  # All epics processed
  EXPORT_INDEX.batch_status.rows = "COMPLETE @ {timestamp}"
  EXPORT_INDEX.last_processed_epic_index = 0  # Reset for next full export
  LOG: "Row generation COMPLETE. Total rows: {EXPORT_INDEX.rows_written}"
  LOG: "Processed {total_epics} epics in {batch_duration}"
ELSE:
  # Partial batch complete, more epics remain
  remaining_epics = total_epics - end_index
  EXPORT_INDEX.batch_status.rows = "PARTIAL @ {timestamp}"
  LOG: "Batch complete. Processed {processed_count} epics ({end_index}/{total_epics})"
  LOG: "Rows written so far: {EXPORT_INDEX.rows_written}"
  LOG: "Remaining epics: {remaining_epics}"
  LOG: "Resume from index {EXPORT_INDEX.last_processed_epic_index} in next batch"
  LOG: "To continue, re-run this skill with the same EXPORT_INDEX"
```

---

## § Story Parsing

Parse each story block from the loaded story file. A story block is delimited
by a heading containing a US-XX-NN-TAG pattern (`### US-01-03-BE`, `## US-01-03-BE`).

```
parse_stories(file_content):
  stories = []
  FOR EACH story block (split on `### US-` or `## US-` headings):
    story = {
      id:          extract_id(block),          # e.g. US-01-03-BE
      tag:         extract_tag(block),         # BE | FE | DATA | INFRA | AI | etc.
      narrative:   extract_narrative(block),   # "As a ... I want ... so that ..."
      ac_list:     extract_ac(block),          # [str, ...] Given/When/Then items
      fr_ids:      extract_refs(block, "FR-"),
      nfr_ids:     extract_refs(block, "NFR-"),
      rsk_ids:     extract_refs(block, "RSK-"),
      kpi_ids:     extract_refs(block, "KPI-"),
      asm_ids:     extract_refs(block, "ASM-"),
      complexity:  extract_complexity(block),  # XS|S|M|L|XL|XXL or ""
      notes:       extract_notes(block),
      has_assumption: "[Assumption]" in block,
      assumptions: []                          # populated if has_assumption
    }
    IF story.has_assumption:
      story.assumptions = extract_assumption_texts(block)
    stories.append(story)
  RETURN stories
```

---

## § Epic Key Builder

The "epic key" is the value stored in EXPORT_INDEX and echoed in child story rows
to create the parent-child hierarchy link. Its format differs per platform:

```
build_epic_key(epic_entry, PLATFORM_SCHEMA, platform_key):
  platform = EXPORT_INDEX.delivery_platform

  IF platform == "jira":
    # Jira links via matching Epic Name / Summary string
    key = "[{platform_key}] {epic_entry.title}"
    IF len(key) > 60: key = key[:57] + "…"
    RETURN key

  IF platform == "azure-devops":
    # Azure DevOps uses a sequential integer for parent ID linking.
    # Since we don't have real ADO IDs pre-import, use epic sequence number.
    # The schema stores this as a pseudo-ID that ADO resolves on import
    # when "Parent" column contains the Title of the parent work item.
    RETURN epic_entry.title   # ADO links by parent Title string

  IF platform == "asana":
    # Asana uses project name + section as hierarchy signal.
    # Epics become sections; stories are tasks within those sections.
    RETURN epic_entry.title   # Asana links task to section by name

  IF platform == "csv-file":
    # Generic: use the EPIC-XX ID as the link key
    RETURN epic_entry.id
```

---

## § Shared Field Transformation Helpers

These helpers are called from `build_row()` and are identical regardless of platform.
The platform schema's FIELD_MAP specifies WHICH column each transformed value goes into;
these helpers define HOW values are transformed.

### map_priority(tier, story_override)
```
tier_map = {
  "Must Have":   "1",    # platforms normalize their own labels in schema
  "Should Have": "2",
  "Could Have":  "3",
  "Won't Have":  "4"
}
IF story_override == "[CRITICAL]": RETURN "0"  # highest signal
RETURN tier_map.get(tier, "3")  # default: medium
# The platform schema maps "0"→"Highest", "1"→"High", etc. per its label set.
```

### map_story_points(complexity)
```
sp_map = { "XS": "1", "S": "2", "M": "3", "L": "5", "XL": "8", "XXL": "13" }
RETURN sp_map.get(complexity, "")  # "" if no complexity tag
```

### build_domain_tag_label(tag)
```
tag_label_map = {
  "BE": "backend", "FE": "frontend", "MOBILE": "mobile",
  "DATA": "data", "INFRA": "infra", "AI": "ai",
  "QA": "qa", "DESIGN": "design", "FS": "fullstack"
}
RETURN tag_label_map.get(tag, tag.lower())
```

### build_labels(story, platform)
```
labels = [build_domain_tag_label(story.tag)]
IF "SPIKE" in story.id:  labels.append("spike")
IF "ENABLER" in story.id: labels.append("enabler")
IF story.has_assumption: labels.append("assumption-present")
IF story.rsk_ids:        labels.append("risk-flagged")
# Join character depends on platform (schema defines LABEL_SEPARATOR):
RETURN join(labels, PLATFORM_SCHEMA.DEFAULTS["label_separator"])
```

### build_story_summary(story)
```
first_line = first non-empty line of story.narrative
IF len(first_line) > 255: first_line = truncate_at_word(first_line, 255) + "…"
RETURN first_line
```

### build_description(source, type)
```
IF type == "epic":
  text = source.title + "\n\n" + (source.description or "")
  IF source.kpi_ids: text += "\nKPIs: " + join(source.kpi_ids, ", ")
  IF source.rsk_ids: text += "\nRisks: " + join(source.rsk_ids, ", ")
  max_len = 2000
ELSE:  # story
  text = source.narrative + "\n\n"
  IF source.notes: text += "Notes:\n" + source.notes + "\n\n"
  text += "Traceability: " + join(
    source.fr_ids + source.nfr_ids + source.rsk_ids + source.kpi_ids, ", "
  )
  IF source.has_assumption: text += "\n[Assumption present — review required]"
  max_len = 32000

text = strip_markdown(text)
IF len(text) > max_len:
  text = text[:max_len - 30] + "\n[Truncated — see backlog for full content]"
RETURN text
```

### build_ac_text(ac_list)
```
IF ac_list is empty: RETURN ""
RETURN join(ac_list, "\n")  # literal newlines inside quoted cell
```

### strip_markdown(text)
```
Remove: **, __, ##, ###, ####, - [ ], - [x], > (blockquote prefix)
Convert: | table | rows | → space-separated plain text
Preserve: plain text content and newlines
```

### encode_row(fields, platform_schema)
```
Apply PLATFORM_SCHEMA.ENCODING rules:
  - Quote each field per ENCODING.quote_char (default: double-quote)
  - Escape internal quote chars per ENCODING.escape (default: double them)
  - Join fields with ENCODING.delimiter (default: comma)
  - Append ENCODING.line_ending (CRLF or LF)
RETURN encoded row string
```

---

## § build_row() — Generic Row Builder

```
build_row(field_map, source, defaults, **context):
  # field_map is an ordered list of { column_name, source_field, transform }
  # source is the epic_entry or story dict
  # context carries: epic_key, epic_entry (for story rows), platform
  row = []
  FOR EACH column_def in field_map:
    raw_value = resolve_field(column_def.source_field, source, context)
    IF raw_value is None or empty:
      value = defaults.get(column_def.column_name, "")
    ELIF column_def.transform:
      value = apply_transform(column_def.transform, raw_value, context)
    ELSE:
      value = raw_value
    row.append(str(value))
  RETURN row

resolve_field(source_field, source, context):
  # source_field may be a dot-path ("epic_entry.title"), a function call,
  # or a literal string prefixed with "$CONST:".
  IF source_field.startswith("$CONST:"): RETURN source_field[7:]
  IF source_field.startswith("epic_entry."): RETURN context.epic_entry[source_field[11:]]
  IF source_field.startswith("context."): RETURN context[source_field[8:]]
  RETURN source.get(source_field, None)
```