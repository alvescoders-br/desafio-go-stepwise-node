# Asana CSV Schema — Platform Schema Reference

## Purpose
Loaded during Step 3 (Plan) when delivery_platform == "asana".
Defines PLATFORM_SCHEMA fields used by the shared row-generation engine.
Keep in context through Step 4; do NOT flush between epics.

## Asana CSV Import Overview
Asana imports tasks via CSV through:
  Project → Import → CSV (from the project's "+" menu or via asana.com/guide/help/api/csv-importer)
Asana's CSV format is flat — it does not support true parent-child hierarchy
in the CSV itself. Hierarchy is approximated by:
  1. Sections: Epic titles become Section headers (rows with only a "Name" value
     and no other fields except "Section/Column").
  2. Tasks: User Stories are tasks listed after their parent Epic's section row.
  3. The "Projects" column pre-assigns tasks to a project.

Asana does NOT support a native "Epic" work item type via CSV. Epics become
Section rows; Stories become Task rows inside those sections.

---

## COLUMN_HEADERS

```
"Name","Description","Assignee","Due Date","Start Date","Tags","Section/Column","Priority","Story Points","Projects","Custom Field: Acceptance Criteria","Custom Field: Domain","Custom Field: Risk IDs","Custom Field: KPI IDs","Custom Field: Story ID"
```

Column count: **15**. Every row MUST have exactly 15 quoted fields.

---

## ENCODING

```
ENCODING = {
  bom:            "",         # Asana CSV: NO BOM (causes import errors)
  line_ending:    "\r\n",
  quote_char:     '"',
  escape:         '""',
  delimiter:      ',',
  label_separator: ', '       # Asana tags: comma-space separated
}
```

Do NOT prepend a BOM to this file. Asana's importer does not accept BOM and
will reject or misparse the first row.

---

## Section Row (Epic → Asana Section)

Asana sections are created by a special row where only "Name" is set and
"Section/Column" is `"true"`. All other columns MUST be `""`.

```
SECTION_ROW_MAP = [
  { column: "Name",                          source: "title" },
  { column: "Description",                   value: "$CONST:" },
  { column: "Assignee",                      value: "$CONST:" },
  { column: "Due Date",                      value: "$CONST:" },
  { column: "Start Date",                    value: "$CONST:" },
  { column: "Tags",                          value: "$CONST:" },
  { column: "Section/Column",               value: "$CONST:true" },
  { column: "Priority",                      value: "$CONST:" },
  { column: "Story Points",                  value: "$CONST:" },
  { column: "Projects",                      source: "context.asana_project_name" },
  { column: "Custom Field: Acceptance Criteria", value: "$CONST:" },
  { column: "Custom Field: Domain",          value: "$CONST:" },
  { column: "Custom Field: Risk IDs",        value: "$CONST:" },
  { column: "Custom Field: KPI IDs",         value: "$CONST:" },
  { column: "Custom Field: Story ID",        source: "id" }
]
```

> **Note:** For Asana, the "Epic row" in the row-generation engine refers to
> this Section Row — not a standard task row. The engine's `build_row()` call
> for epics should use `SECTION_ROW_MAP` (aliased as `EPIC_FIELD_MAP` below).

---

## EPIC_FIELD_MAP

Alias for SECTION_ROW_MAP — use this name so the shared engine finds it.

```
EPIC_FIELD_MAP = SECTION_ROW_MAP  (defined above)
```

---

## STORY_FIELD_MAP

AI Pods User Stories map to Asana **Tasks** within the Section.

```
STORY_FIELD_MAP = [
  { column: "Name",              source: "narrative", transform: "build_story_summary" },
  { column: "Description",       source: "story",     transform: "build_description(story)" },
  { column: "Assignee",          value: "$CONST:" },
  { column: "Due Date",          value: "$CONST:" },
  { column: "Start Date",        value: "$CONST:" },
  { column: "Tags",              source: "story",     transform: "build_story_tags_asana" },
  { column: "Section/Column",    source: "context.epic_key" },
    # Asana places the task in the section matching this value.
    # epic_key for Asana = plain epic title string.
  { column: "Priority",          source: "context.epic_entry.priority_tier",
                                 transform: "map_asana_priority" },
  { column: "Story Points",      source: "complexity", transform: "map_story_points" },
  { column: "Projects",          source: "context.asana_project_name" },
  { column: "Custom Field: Acceptance Criteria", source: "ac_list",
                                 transform: "build_ac_text" },
  { column: "Custom Field: Domain", source: "tag",   transform: "build_domain_tag_label" },
  { column: "Custom Field: Risk IDs", source: "rsk_ids", transform: "join_ids_comma" },
  { column: "Custom Field: KPI IDs",  source: "kpi_ids", transform: "join_ids_comma" },
  { column: "Custom Field: Story ID", source: "id" }
]
```

---

## DEFAULTS

```
DEFAULTS = {
  "Name":                          "",
  "Description":                   "",
  "Assignee":                      "",
  "Due Date":                      "",
  "Start Date":                    "",
  "Tags":                          "",
  "Section/Column":                "",
  "Priority":                      "Medium",
  "Story Points":                  "",
  "Projects":                      "",   # populated from asana_project_name if provided
  "Custom Field: Acceptance Criteria": "",
  "Custom Field: Domain":          "",
  "Custom Field: Risk IDs":        "",
  "Custom Field: KPI IDs":         "",
  "Custom Field: Story ID":        "",
  "label_separator":               ", "
}
```

---

## Asana-Specific Transform Functions

### map_asana_priority(tier)
```
# Asana priority labels (standard)
priority_map = {
  "Must Have":   "High",
  "Should Have": "Medium",
  "Could Have":  "Low",
  "Won't Have":  "Low"
}
IF story has [CRITICAL] override: RETURN "High"
RETURN priority_map.get(tier, "Medium")
```

### build_story_tags_asana(story)
```
tags = [build_domain_tag_label(story.tag)]
IF "SPIKE" in story.id:   tags.append("spike")
IF "ENABLER" in story.id: tags.append("enabler")
IF story.has_assumption:  tags.append("assumption-present")
IF story.rsk_ids:         tags.append("risk-flagged")
RETURN ", ".join(tags)    # Asana uses comma-space separator
```

### join_ids_comma(id_list)
```
IF id_list is empty: RETURN ""
RETURN ", ".join(id_list)
```

---

## Epic Key Rule (Asana-specific)

```
build_epic_key for asana:
  RETURN epic_entry.title
  # Asana places tasks into sections by matching "Section/Column" to
  # the section's "Name". The Section row must use the exact same title string.
  # CRITICAL: store epic_entry.platform_key = epic_entry.title immediately
  # so all story rows use the same string without recomputation.
```

---

## Row Order Requirement

Section rows (Epics) MUST appear immediately before their child Task rows.
The row-generation loop already satisfies this. Do NOT reorder rows.

---

## Custom Fields Prerequisite

The columns `Custom Field: Acceptance Criteria`, `Custom Field: Domain`,
`Custom Field: Risk IDs`, `Custom Field: KPI IDs`, and `Custom Field: Story ID`
MUST exist as custom fields in the Asana project before import.
If they do not exist, Asana will ignore those columns on import (no error,
but data is lost). Create them manually in Asana project settings
(Settings → Fields → Add field) before running the import.

---

## IMPORT_STEPS

```
1. Ensure Custom Fields exist in your Asana project:
   - "Acceptance Criteria" (Text field)
   - "Domain" (Text field)
   - "Risk IDs" (Text field)
   - "KPI IDs" (Text field)
   - "Story ID" (Text field)
   Create these in: Project Settings → Fields → Add Field.

2. In Asana, open the target project.

3. Click the "+" button in the project header → Import → CSV.
   (Or go to My Tasks → Import if adding to My Tasks.)

4. Upload: asana-import-{SESSION_ID}.csv

5. On the column mapping screen, verify:
   - "Name"           → Name
   - "Description"    → Notes/Description
   - "Section/Column" → Section (places tasks into the correct epic section)
   - "Priority"       → Priority
   - "Tags"           → Tags
   - Custom fields    → their matching custom field names

6. Click "Import". Asana will create Sections first, then Tasks within them.

7. Post-import: assign due dates, team members, and sprints (via Timeline)
   as needed.

TIP: Section rows (Epic titles) appear as collapsible sections in the List view.
Tasks are grouped under their parent section automatically.

TIP: If your Asana workspace uses Portfolios, you can add the imported project
to a Portfolio after import to track it alongside other projects.
```