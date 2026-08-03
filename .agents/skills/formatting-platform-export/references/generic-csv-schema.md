# Generic CSV Schema — Platform Schema Reference

## Purpose
Loaded during Step 3 (Plan) when delivery_platform == "csv-file".
Produces a portable, platform-agnostic CSV that can be opened in Excel,
Google Sheets, or used as a source for manual import into any tool.
No platform-specific column names or hierarchy encoding.

---

## COLUMN_HEADERS

```
"Item Type","Item ID","Parent ID","Title","Description","Priority","Story Points","Domain","Theme","Persona","Labels","Acceptance Criteria","FR IDs","NFR IDs","KPI IDs","Risk IDs","Assumption IDs","Complexity","Notes"
```

Column count: **19**. Every row MUST have exactly 19 quoted fields.

---

## ENCODING

```
ENCODING = {
  bom:            "\uFEFF",    # UTF-8 BOM for Excel compatibility
  line_ending:    "\r\n",
  quote_char:     '"',
  escape:         '""',
  delimiter:      ',',
  label_separator: ', '
}
```

---

## EPIC_FIELD_MAP

```
EPIC_FIELD_MAP = [
  { column: "Item Type",          value: "$CONST:Epic" },
  { column: "Item ID",            source: "id" },             # EPIC-01
  { column: "Parent ID",          value: "$CONST:" },         # top-level
  { column: "Title",              source: "title" },
  { column: "Description",        source: "epic",  transform: "build_description(epic)" },
  { column: "Priority",           source: "priority_tier", transform: "map_generic_priority" },
  { column: "Story Points",       value: "$CONST:" },         # blank for epics
  { column: "Domain",             value: "$CONST:" },         # blank for epics
  { column: "Theme",              source: "theme" },
  { column: "Persona",            value: "$CONST:" },
  { column: "Labels",             value: "$CONST:epic" },
  { column: "Acceptance Criteria", value: "$CONST:" },
  { column: "FR IDs",             value: "$CONST:" },         # not at epic level
  { column: "NFR IDs",            value: "$CONST:" },
  { column: "KPI IDs",            source: "kpi_ids", transform: "join_ids" },
  { column: "Risk IDs",           source: "rsk_ids", transform: "join_ids" },
  { column: "Assumption IDs",     value: "$CONST:" },
  { column: "Complexity",         source: "complexity" },
  { column: "Notes",              value: "$CONST:" }
]
```

---

## STORY_FIELD_MAP

```
STORY_FIELD_MAP = [
  { column: "Item Type",          transform: "map_generic_item_type(story)" },
  { column: "Item ID",            source: "id" },             # US-01-03-BE
  { column: "Parent ID",          source: "context.epic_entry.id" },  # EPIC-01
  { column: "Title",              source: "narrative", transform: "build_story_summary" },
  { column: "Description",        source: "story",     transform: "build_description(story)" },
  { column: "Priority",           source: "context.epic_entry.priority_tier",
                                  transform: "map_generic_priority_with_override" },
  { column: "Story Points",       source: "complexity", transform: "map_story_points" },
  { column: "Domain",             source: "tag",        transform: "build_domain_tag_label" },
  { column: "Theme",              source: "context.epic_entry.theme" },
  { column: "Persona",            source: "narrative",  transform: "extract_persona" },
  { column: "Labels",             source: "story",      transform: "build_labels_generic" },
  { column: "Acceptance Criteria", source: "ac_list",   transform: "build_ac_text" },
  { column: "FR IDs",             source: "fr_ids",     transform: "join_ids" },
  { column: "NFR IDs",            source: "nfr_ids",    transform: "join_ids" },
  { column: "KPI IDs",            source: "kpi_ids",    transform: "join_ids" },
  { column: "Risk IDs",           source: "rsk_ids",    transform: "join_ids" },
  { column: "Assumption IDs",     source: "asm_ids",    transform: "join_ids" },
  { column: "Complexity",         source: "complexity" },
  { column: "Notes",              source: "notes" }
]
```

---

## DEFAULTS

```
DEFAULTS = {
  "Item Type":             "Story",
  "Item ID":               "",
  "Parent ID":             "",
  "Title":                 "",
  "Description":           "",
  "Priority":              "Medium",
  "Story Points":          "",
  "Domain":                "",
  "Theme":                 "",
  "Persona":               "",
  "Labels":                "",
  "Acceptance Criteria":   "",
  "FR IDs":                "",
  "NFR IDs":               "",
  "KPI IDs":               "",
  "Risk IDs":              "",
  "Assumption IDs":        "",
  "Complexity":            "",
  "Notes":                 "",
  "label_separator":       ", "
}
```

---

## Generic Transform Functions

### map_generic_priority(tier)
```
priority_map = {
  "Must Have":   "High",
  "Should Have": "Medium",
  "Could Have":  "Low",
  "Won't Have":  "Lowest"
}
RETURN priority_map.get(tier, "Medium")
```

### map_generic_item_type(story)
```
IF "SPIKE" in story.id:   RETURN "Spike"
IF "ENABLER" in story.id: RETURN "Enabler"
RETURN "Story"
```

### extract_persona(narrative)
```
# Extract the role from "As a {role}, I want..."
match = regex_match(r"[Aa]s an? ([^,]+),", narrative)
IF match: RETURN match.group(1).strip()
RETURN ""
```

### build_labels_generic(story)
```
labels = [build_domain_tag_label(story.tag)]
IF "SPIKE" in story.id:   labels.append("spike")
IF "ENABLER" in story.id: labels.append("enabler")
IF story.has_assumption:  labels.append("assumption-present")
IF story.rsk_ids:         labels.append("risk-flagged")
RETURN ", ".join(labels)
```

### join_ids(id_list)
```
IF id_list is empty: RETURN ""
RETURN ", ".join(id_list)
```

---

## Epic Key Rule (Generic CSV-specific)

```
build_epic_key for csv-file:
  RETURN epic_entry.id    # e.g. "EPIC-01"
  # Generic CSV uses the EPIC-ID as the Parent ID for child stories.
  # The "Parent ID" column in story rows holds the parent epic's Item ID.
  # No string-matching trick needed — IDs are stable and unambiguous.
```

---

## IMPORT_STEPS

```
This file is a generic, platform-agnostic CSV export. It is designed to be:
- Opened directly in Excel or Google Sheets for review.
- Used as source data for manual import into any project management tool.
- Transformed into a platform-specific format using a secondary mapping step.

Opening in Excel:
  1. Open Excel → Data → Get Data → From Text/CSV.
  2. Select: backlog-export-{SESSION_ID}.csv
  3. Set Delimiter: Comma. Set File Origin: 65001 (UTF-8).
  4. Click Load.

Opening in Google Sheets:
  1. File → Import → Upload → select the CSV file.
  2. Import Location: New spreadsheet.
  3. Separator type: Comma.
  4. Click Import.

Column structure:
  - "Item ID" is the unique identifier for each row.
  - "Parent ID" links a Story or Spike to its parent Epic (contains the Epic's Item ID).
  - "Priority" uses plain English labels: High, Medium, Low, Lowest.
  - "Story Points" contains numeric values only (blank for Epics).
  - "Acceptance Criteria" contains plain text, one criterion per line.
  - All traceability IDs (FR IDs, NFR IDs, etc.) are comma-separated.

TIP: Use the "Parent ID" column to reconstruct the hierarchy in any tool
that supports parent-child relationships (Notion, Linear, Monday.com, etc.).
```