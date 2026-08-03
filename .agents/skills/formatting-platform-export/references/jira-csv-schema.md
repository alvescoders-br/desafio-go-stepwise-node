# Jira CSV Schema — Platform Schema Reference

## Purpose
Loaded during Step 3 (Plan) when delivery_platform == "jira".
Defines PLATFORM_SCHEMA fields used by the shared row-generation engine.
Keep this in context through Step 4; do NOT flush it between epics.

---

## COLUMN_HEADERS

```
"Issue Type","Summary","Description","Priority","Story Points","Labels","Components","Epic Link","Epic Name","Sprint","Assignee","Reporter","Fix Version/s","Affects Version/s","Custom field (Team)","Custom field (Business Value)","Custom field (Risk)","Custom field (Acceptance Criteria)"
```

Column count: **18**. Every row MUST have exactly 18 quoted fields.
Empty fields: emit `""` — never omit a column or leave a bare comma gap.

---

## ENCODING

```
ENCODING = {
  bom:          "\uFEFF",    # UTF-8 BOM prepended to file (required for Excel)
  line_ending:  "\r\n",     # CRLF — Jira CSV standard
  quote_char:   '"',
  escape:       '""',       # double the quote to escape internal quotes
  delimiter:    ',',
  label_separator: ','      # labels joined with comma (no spaces)
}
```

Write the BOM once, before the header row, in Step 3b. Never re-write it.

---

## EPIC_FIELD_MAP

Ordered list matching COLUMN_HEADERS exactly.

```
EPIC_FIELD_MAP = [
  { column: "Issue Type",                     value: "$CONST:Epic" },
  { column: "Summary",                        source: "epic_key" },
    # epic_key for Jira = "[{jira_project_key}] {epic_title}" (max 60 chars)
  { column: "Description",                    source: "description",  transform: "build_description(epic)" },
  { column: "Priority",                       source: "priority_tier", transform: "map_jira_priority" },
  { column: "Story Points",                   value: "$CONST:" },     # blank — epics don't carry SP
  { column: "Labels",                         value: "$CONST:" },     # blank for epics
  { column: "Components",                     value: "$CONST:" },     # blank for epics
  { column: "Epic Link",                      value: "$CONST:" },     # blank — this IS the epic
  { column: "Epic Name",                      source: "epic_key" },   # Jira uses this to create the epic
  { column: "Sprint",                         value: "$CONST:" },
  { column: "Assignee",                       value: "$CONST:" },
  { column: "Reporter",                       value: "$CONST:" },
  { column: "Fix Version/s",                  value: "$CONST:" },
  { column: "Affects Version/s",              value: "$CONST:" },
  { column: "Custom field (Team)",            value: "$CONST:" },
  { column: "Custom field (Business Value)",  source: "kpi_ids",    transform: "join_ids" },
  { column: "Custom field (Risk)",            source: "rsk_ids",    transform: "join_ids" },
  { column: "Custom field (Acceptance Criteria)", value: "$CONST:" }
]
```

---

## STORY_FIELD_MAP

```
STORY_FIELD_MAP = [
  { column: "Issue Type",                     transform: "map_jira_issue_type(story)" },
  { column: "Summary",                        source: "narrative",   transform: "build_story_summary" },
  { column: "Description",                    source: "story",       transform: "build_description(story)" },
  { column: "Priority",                       source: "context.epic_entry.priority_tier",
                                              transform: "map_jira_priority_with_override" },
  { column: "Story Points",                   source: "complexity",  transform: "map_story_points" },
  { column: "Labels",                         source: "story",       transform: "build_labels" },
  { column: "Components",                     source: "tag",         transform: "map_component" },
  { column: "Epic Link",                      source: "context.epic_key" },
    # CRITICAL: Must match Epic row Summary character-for-character.
    # Store epic_key in epic_entry.platform_key in Step 4 for this lookup.
  { column: "Epic Name",                      value: "$CONST:" },    # blank for stories
  { column: "Sprint",                         value: "$CONST:" },
  { column: "Assignee",                       value: "$CONST:" },
  { column: "Reporter",                       value: "$CONST:" },
  { column: "Fix Version/s",                  value: "$CONST:" },
  { column: "Affects Version/s",              value: "$CONST:" },
  { column: "Custom field (Team)",            value: "$CONST:" },
  { column: "Custom field (Business Value)",  source: "kpi_ids",    transform: "join_ids" },
  { column: "Custom field (Risk)",            source: "rsk_ids",    transform: "join_ids" },
  { column: "Custom field (Acceptance Criteria)", source: "ac_list", transform: "build_ac_text" }
]
```

---

## DEFAULTS

```
DEFAULTS = {
  "Issue Type":                     "Story",
  "Priority":                       "Medium",
  "Story Points":                   "",
  "Labels":                         "",
  "Components":                     "",
  "Epic Link":                      "",
  "Epic Name":                      "",
  "Sprint":                         "",
  "Assignee":                       "",
  "Reporter":                       "",
  "Fix Version/s":                  "",
  "Affects Version/s":              "",
  "Custom field (Team)":            "",
  "Custom field (Business Value)":  "",
  "Custom field (Risk)":            "",
  "Custom field (Acceptance Criteria)": "",
  "label_separator":                ","
}
```

---

## Jira-Specific Transform Functions

### map_jira_priority(tier, story_priority_code)
```
priority_map = {
  "0": "Highest",   # [CRITICAL] story override
  "1": "Highest",   # Must Have
  "2": "High",      # Should Have
  "3": "Medium",    # Could Have
  "4": "Low"        # Won't Have
}
# story_priority_code comes from shared map_priority() in 02-csv-row-generation.md
RETURN priority_map.get(story_priority_code, "Medium")
```

### map_jira_issue_type(story)
```
IF "SPIKE" in story.id:   RETURN "Story"   # label carries spike signal
IF "ENABLER" in story.id: RETURN "Story"   # label carries enabler signal
RETURN "Story"
# Note: Jira "Epic" type is only used for epic rows.
```

### map_component(tag)
```
component_map = {
  "BE":     "Backend",         "FE":     "Frontend",
  "MOBILE": "Mobile",          "DATA":   "Data Platform",
  "INFRA":  "Infrastructure",  "AI":     "AI/ML",
  "QA":     "Quality Engineering", "DESIGN": "Design",
  "FS":     "Full Stack"
}
RETURN component_map.get(tag, "")
```

### join_ids(id_list)
```
IF id_list is empty: RETURN ""
RETURN ", ".join(id_list)   # e.g. "KPI-01, KPI-03"
```

---

## Epic Key Rule (Jira-specific)

```
build_epic_key for Jira:
  key = "[{jira_project_key}] {epic_title}"
  IF len(key) > 60: key = key[:57] + "…"
  RETURN key

CRITICAL: The "Epic Link" value in every child story row MUST be
character-for-character identical to this Epic's "Summary" field.
Store epic_entry.platform_key = epic_key immediately after computing it,
so all story rows for this epic reference the same stored string — never
recompute it per story (risk of truncation drift).
```

---

## IMPORT_STEPS

```
1. Log in to your Jira instance.
2. Navigate to: Project Settings → Issue Types
   Confirm "Epic" and "Story" issue types exist.
3. Go to: Jira Settings → System → External System Import → CSV.
4. Upload: {OUTPUT_FILENAME_PREFIX}-{SESSION_ID}.csv
5. On the column mapping screen:
   - "Issue Type"  → Issue Type
   - "Summary"     → Summary
   - "Epic Name"   → Epic Name  (Jira uses this to create the Epic)
   - "Epic Link"   → Epic Link  (links Story rows to their parent Epic)
   - "Story Points" → Story Points (or your configured SP field name)
   - All other columns → their matching Jira field names.
6. Set "Email for unmapped users" to a valid project member.
7. Click "Begin Import". Review the import log for row-level errors.
8. Post-import: assign sprints, team members, fix versions, and components
   as needed via Jira board or bulk edit.

TIP: Jira processes Epic rows first, then links Story rows by matching
"Epic Link" to the Epic's "Summary". If an Epic row is missing, its child
stories will import without a parent — check the import log for orphan warnings.
```