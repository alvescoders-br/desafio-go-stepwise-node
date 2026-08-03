# Azure DevOps CSV Schema — Platform Schema Reference

## Purpose
Loaded during Step 3 (Plan) when delivery_platform == "azure-devops".
Defines PLATFORM_SCHEMA fields used by the shared row-generation engine.
Keep in context through Step 4; do NOT flush between epics.

## Azure DevOps CSV Import Overview
Azure DevOps (ADO) imports work items via CSV through:
  Boards → Work Items → Import Work Items (CSV)
The CSV creates a flat list of work items. Parent-child hierarchy is
established via the "Parent" column, which contains the Title of the parent
work item. Epics MUST appear before their child Features/Stories in the file.

Work item type hierarchy used in this export:
  Epic → Feature (mapped from AI Pods Epic) → User Story → Task
  For this skill: AI Pods Epics → ADO "Feature"; AI Pods Stories → ADO "User Story".
  If the ADO project uses "Epic" as the top level, set item type accordingly —
  the schema uses "Feature" as the default parent type and "User Story" for stories.

---

## COLUMN_HEADERS

```
"Work Item Type","Title","Description","Priority","Story Points","Tags","Area Path","Iteration Path","Assigned To","State","Parent","Acceptance Criteria","Original Estimate","Activity","Business Value","Risk"
```

Column count: **16**. Every row MUST have exactly 16 quoted fields.

---

## ENCODING

```
ENCODING = {
  bom:            "\uFEFF",    # UTF-8 BOM — required for ADO CSV import
  line_ending:    "\r\n",
  quote_char:     '"',
  escape:         '""',
  delimiter:      ',',
  label_separator: '; '        # ADO tags separated by semicolons
}
```

---

## EPIC_FIELD_MAP

AI Pods Epics map to ADO **Features** (mid-level container work item type).

```
EPIC_FIELD_MAP = [
  { column: "Work Item Type",   value: "$CONST:Feature" },
  { column: "Title",            source: "title" },
    # ADO Title = plain epic title (no project key prefix needed)
  { column: "Description",      source: "epic",  transform: "build_description(epic)" },
  { column: "Priority",         source: "priority_tier", transform: "map_ado_priority" },
  { column: "Story Points",     value: "$CONST:" },          # blank for features
  { column: "Tags",             source: "theme",  transform: "build_epic_tags" },
  { column: "Area Path",        source: "context.azure_area_path",
                                transform: "use_or_default_area_path" },
  { column: "Iteration Path",   value: "$CONST:" },          # assign post-import
  { column: "Assigned To",      value: "$CONST:" },
  { column: "State",            value: "$CONST:New" },
  { column: "Parent",           value: "$CONST:" },          # top-level feature
  { column: "Acceptance Criteria", value: "$CONST:" },       # blank for features
  { column: "Original Estimate", value: "$CONST:" },
  { column: "Activity",         value: "$CONST:Development" },
  { column: "Business Value",   source: "kpi_ids",  transform: "join_ids_semicolon" },
  { column: "Risk",             source: "rsk_ids",  transform: "join_ids_semicolon" }
]
```

---

## STORY_FIELD_MAP

AI Pods User Stories map to ADO **User Stories**.

```
STORY_FIELD_MAP = [
  { column: "Work Item Type",   transform: "map_ado_work_item_type(story)" },
  { column: "Title",            source: "narrative", transform: "build_story_summary" },
  { column: "Description",      source: "story",     transform: "build_description(story)" },
  { column: "Priority",         source: "context.epic_entry.priority_tier",
                                transform: "map_ado_priority_with_override" },
  { column: "Story Points",     source: "complexity", transform: "map_story_points" },
  { column: "Tags",             source: "story",     transform: "build_story_tags_ado" },
  { column: "Area Path",        source: "context.azure_area_path",
                                transform: "use_or_default_area_path" },
  { column: "Iteration Path",   value: "$CONST:" },
  { column: "Assigned To",      value: "$CONST:" },
  { column: "State",            value: "$CONST:New" },
  { column: "Parent",           source: "context.epic_key" },
    # Parent = Feature Title — must match EPIC_FIELD_MAP "Title" exactly.
  { column: "Acceptance Criteria", source: "ac_list", transform: "build_ac_text_html" },
  { column: "Original Estimate", value: "$CONST:" },
  { column: "Activity",         source: "tag",      transform: "map_ado_activity" },
  { column: "Business Value",   source: "kpi_ids",  transform: "join_ids_semicolon" },
  { column: "Risk",             source: "rsk_ids",  transform: "join_ids_semicolon" }
]
```

---

## DEFAULTS

```
DEFAULTS = {
  "Work Item Type":       "User Story",
  "Priority":             "3",
  "Story Points":         "",
  "Tags":                 "",
  "Area Path":            "",          # populated from azure_area_path if provided
  "Iteration Path":       "",
  "Assigned To":          "",
  "State":                "New",
  "Parent":               "",
  "Acceptance Criteria":  "",
  "Original Estimate":    "",
  "Activity":             "Development",
  "Business Value":       "",
  "Risk":                 "",
  "label_separator":      "; "
}
```

---

## Azure DevOps–Specific Transform Functions

### map_ado_priority(tier)
```
# ADO Priority: 1 (highest) to 4 (lowest)
priority_map = {
  "Must Have":   "1",
  "Should Have": "2",
  "Could Have":  "3",
  "Won't Have":  "4"
}
RETURN priority_map.get(tier, "3")
```

### map_ado_work_item_type(story)
```
IF "SPIKE" in story.id:   RETURN "Task"        # spikes are tasks in ADO
IF "ENABLER" in story.id: RETURN "User Story"  # enablers stay as stories
RETURN "User Story"
```

### map_ado_activity(tag)
```
activity_map = {
  "BE": "Development", "FE": "Development", "MOBILE": "Development",
  "DATA": "Development", "INFRA": "Deployment", "AI": "Development",
  "QA": "Testing", "DESIGN": "Design", "FS": "Development"
}
RETURN activity_map.get(tag, "Development")
```

### build_epic_tags(theme)
```
# ADO tags are semicolon-separated; derive from theme + backlog signal
tags = []
IF theme: tags.append(theme.replace(" ", "-").lower())
tags.append("epic")
RETURN "; ".join(tags)
```

### build_story_tags_ado(story)
```
tags = [build_domain_tag_label(story.tag)]
IF "SPIKE" in story.id:  tags.append("spike")
IF "ENABLER" in story.id: tags.append("enabler")
IF story.has_assumption: tags.append("assumption-present")
IF story.rsk_ids:        tags.append("risk-flagged")
RETURN "; ".join(tags)
```

### build_ac_text_html(ac_list)
```
# ADO Acceptance Criteria field accepts HTML
IF ac_list is empty: RETURN ""
items = ["<li>" + ac + "</li>" for ac in ac_list]
RETURN "<ul>" + "".join(items) + "</ul>"
```

### join_ids_semicolon(id_list)
```
IF id_list is empty: RETURN ""
RETURN "; ".join(id_list)
```

### use_or_default_area_path(area_path)
```
IF area_path is not empty: RETURN area_path
RETURN ""   # ADO defaults to root area path on import
```

---

## Epic Key Rule (Azure DevOps–specific)

```
build_epic_key for azure-devops:
  RETURN epic_entry.title
  # ADO links stories to parent by matching "Parent" column value
  # to the "Title" of the Feature row. No truncation — use full title.
  # CRITICAL: store epic_entry.platform_key = epic_entry.title immediately
  # so all story rows reference the same string without recomputation.
```

---

## Row Order Requirement

Feature rows MUST appear before their child User Story rows. The row-generation
loop (per-epic, in priority-tier order) already satisfies this: the Feature row
is written first, followed immediately by all its User Story rows, before moving
to the next Feature. Do NOT sort or reorder rows after generation.

---

## IMPORT_STEPS

```
1. Log in to your Azure DevOps organization.
2. Navigate to: Boards → Work Items.
3. Click the "Import Work Items" button (top-right area, CSV icon).
4. Upload: azure-import-{SESSION_ID}.csv
5. Review the preview table — verify columns are mapped correctly:
   - "Work Item Type" → Work Item Type
   - "Title"          → Title
   - "Parent"         → Parent (links User Stories to their parent Feature)
   - "Story Points"   → Story Points
   - "Acceptance Criteria" → Acceptance Criteria
6. Click "Import". Monitor the import progress bar.
7. After import, review any rows flagged with warnings in the results pane.
8. Post-import: assign Iteration Paths (sprints), Area Paths (if not pre-set),
   and team members via the Work Items view or bulk edit.

TIP: ADO resolves the "Parent" field by matching the value to the "Title" of
another work item in the same import file. If a Feature row is missing,
its child User Stories will import as orphans — check the results for
"Parent not found" warnings.

TIP: If your ADO project uses "Epic" as the top-level type (above Feature),
you can add a manual Epic work item in ADO after import and link Features to it
via the work item relationship editor.
```