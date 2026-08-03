# ServiceNow CSV Schema — Platform Schema Reference

## Purpose
Loaded during Step 3 (Plan) when delivery_platform == "servicenow".
Produces a CSV staging file for ServiceNow's standard **Import Set +
Transform Map** ingestion path (System Import Sets → Load Data → Data
Source → Transform Map → Run Transform).

## Why this schema does not use ServiceNow internal field names
ServiceNow Import Sets accept **any** CSV column names — the receiving
Transform Map (owned and configured by the customer's ServiceNow admin)
performs the actual column→table-field mapping on their instance. There is
no confirmed, SME-reviewed set of internal table/field names (e.g. specific
`rm_story`/`sn_agile_capability` field names) available for this schema —
inventing them would violate the Zero Invention Policy. This schema
therefore uses generic, human-readable column names (same discipline as
`generic-csv-schema.md`), plus one ServiceNow-aligned convention that *is*
public and confirmed: the standard priority scale (see `Priority` below).
**This is a deliberate integration design, not a placeholder** — the actual
field mapping happens once, in the customer's Transform Map UI, not here.

---

## COLUMN_HEADERS

```
"Item Type","Item ID","Parent ID","Capability ID","Capability Title","Feature ID","Feature Title","Title","Description","Short Description","Priority","Story Points","Domain","Theme","Persona","Labels","Acceptance Criteria","FR IDs","NFR IDs","KPI IDs","Risk IDs","Assumption IDs","Complexity","Notes"
```

Column count: **24**. Every row MUST have exactly 24 quoted fields.

The four hierarchy columns (`Capability ID`, `Capability Title`, `Feature
ID`, `Feature Title`) exist in every row regardless of `hierarchy_mode`, so
the customer's Transform Map column mapping never has to change between
modes — they're simply blank when unused (see Hierarchy Mode below).

---

## ENCODING

```
ENCODING = {
  bom:            "﻿",    # UTF-8 BOM — ServiceNow Import Set Data Source upload expects UTF-8
  line_ending:    "\r\n",
  quote_char:     '"',
  escape:         '""',
  delimiter:      ',',
  label_separator: ', '
}
```

---

## Hierarchy Mode

ServiceNow Strategic Portfolio Management natively supports a 4-level
Enterprise Agile Planning hierarchy (Epic → Capability → Feature → Story).
AI Pods' backlog artifacts only model 2 levels (Epic → Story). Rather than
generating new upstream content, this schema supports an **optional,
synthetic** 4-level expansion derived entirely from fields that already
exist in the epics/stories artifacts — controlled by the
`--servicenow-hierarchy-mode` flag on `render_csv_rows.py`:

| Mode | Behavior |
|---|---|
| `epic_story` (default) | Identical to `generic-csv-schema.md`'s 2-level output. `Capability ID/Title`, `Feature ID/Title` columns are blank on every row. `Parent ID` on a Story row is its Epic's `Item ID`, exactly as today. |
| `epic_capability_feature_story` | One synthetic **Capability** row per Epic and one synthetic **Feature** row per distinct story domain-tag within that Epic — see below. |

### Synthetic Capability/Feature derivation (4-level mode only)

```
FOR EACH epic:
  CAPABILITY_ID    = "CAP-{epic.id}"                       # e.g. CAP-EPIC-01
  CAPABILITY_TITLE = epic.theme OR "{epic.id} Capability"  # derived from the Epic's existing Theme field
  EMIT one Capability row: Parent ID = epic.id, Item ID = CAPABILITY_ID

  DISTINCT_TAGS = sorted distinct story.tag values across this epic's stories
  FOR EACH tag in DISTINCT_TAGS:
    FEATURE_ID    = "FEAT-{epic.id}-{tag}"                 # e.g. FEAT-EPIC-01-BE
    FEATURE_TITLE = "{epic.title} — {domain_label(tag)}"   # e.g. "Task Lifecycle Management — Backend"
    EMIT one Feature row: Parent ID = CAPABILITY_ID, Capability ID = CAPABILITY_ID,
                          Capability Title = CAPABILITY_TITLE

  FOR EACH story in this epic:
    story.context.parent_link_id   = FEAT-{epic.id}-{story.tag}   # or FEAT-{epic.id}-GENERAL if tag unrecognized
    story.context.capability_id    = CAPABILITY_ID
    story.context.capability_title = CAPABILITY_TITLE
    story.context.feature_id       = FEAT-{epic.id}-{story.tag}
    story.context.feature_title    = "{epic.title} — {domain_label(story.tag)}"
```

Every synthetic Capability/Feature row gets `Notes: "AUTO-DERIVED from
Epic Theme/Story Domain Tag — v1 pragmatic hierarchy"`.

### v1 limitations — a conscious scope decision, not a bug

| What's not covered | Why |
|---|---|
| Cross-epic Capability roll-up | Each Epic produces exactly one Capability (`CAP-{epic.id}`). If two Epics share a `theme`, two distinct Capabilities are still emitted with the same title — a strict 1:1 Epic→Capability tree, not a real many-to-one portfolio roll-up. |
| Feature as a product decision | Features here are technical buckets (one per story domain-tag: Backend, Frontend, Data, …), not a product owner's judgment of what constitutes a customer-facing Feature. |
| Independent Capability/Feature priority or estimation | Priority is inherited from the parent Epic's `priority_tier` (Zero Invention — no new judgment is fabricated at the synthetic levels). |
| Portfolio-level strategic intent | 100% mechanically derived from `theme` and domain-tag already present in the artifacts. Every synthetic row is flagged `AUTO-DERIVED` in `Notes` so the ServiceNow portfolio owner treats it as a starting point requiring review, not authoritative SPM planning data. |
| Unrecognized domain tags | Any story tag outside `{BE, FE, DATA, INFRA, AI, QA, DESIGN, FS}` falls into a fallback Feature `FEAT-{epic.id}-GENERAL`. |

---

## EPIC_FIELD_MAP

```
EPIC_FIELD_MAP = [
  { column: "Item Type",          value: "$CONST:Epic" },
  { column: "Item ID",            source: "id" },
  { column: "Parent ID",          value: "$CONST:" },                 # top-level, always
  { column: "Capability ID",      value: "$CONST:" },                 # populated only in 4-level mode, on the synthetic Capability row itself
  { column: "Capability Title",   value: "$CONST:" },
  { column: "Feature ID",         value: "$CONST:" },
  { column: "Feature Title",      value: "$CONST:" },
  { column: "Title",              source: "title" },
  { column: "Description",        source: "epic",  transform: "build_description(epic)" },
  { column: "Short Description",  source: "epic",  transform: "build_short_description(epic)" },
  { column: "Priority",           source: "priority_tier", transform: "map_servicenow_priority" },
  { column: "Story Points",       value: "$CONST:" },                 # blank for epics
  { column: "Domain",             value: "$CONST:" },                 # blank for epics
  { column: "Theme",              source: "theme" },
  { column: "Persona",            value: "$CONST:" },
  { column: "Labels",             value: "$CONST:epic" },
  { column: "Acceptance Criteria", value: "$CONST:" },
  { column: "FR IDs",             value: "$CONST:" },
  { column: "NFR IDs",            value: "$CONST:" },
  { column: "KPI IDs",            source: "kpi_ids", transform: "join_ids" },
  { column: "Risk IDs",           source: "rsk_ids", transform: "join_ids" },
  { column: "Assumption IDs",     value: "$CONST:" },
  { column: "Complexity",         source: "complexity" },
  { column: "Notes",              value: "$CONST:" }
]
```

## CAPABILITY_FIELD_MAP (synthetic row, 4-level mode only)

```
CAPABILITY_FIELD_MAP = [
  { column: "Item Type",          value: "$CONST:Capability" },
  { column: "Item ID",            source: "capability_id" },
  { column: "Parent ID",          source: "epic.id" },
  { column: "Capability ID",      source: "capability_id" },
  { column: "Capability Title",   source: "capability_title" },
  { column: "Feature ID",         value: "$CONST:" },
  { column: "Feature Title",      value: "$CONST:" },
  { column: "Title",              source: "capability_title" },
  { column: "Priority",           source: "epic.priority_tier", transform: "map_servicenow_priority" },
  { column: "Theme",              source: "epic.theme" },
  { column: "Labels",             value: "$CONST:capability" },
  { column: "Notes",              value: "$CONST:AUTO-DERIVED from Epic Theme — v1 pragmatic hierarchy" }
  # all other columns: "$CONST:" (blank)
]
```

## FEATURE_FIELD_MAP (synthetic row, 4-level mode only)

```
FEATURE_FIELD_MAP = [
  { column: "Item Type",          value: "$CONST:Feature" },
  { column: "Item ID",            source: "feature_id" },
  { column: "Parent ID",          source: "capability_id" },
  { column: "Capability ID",      source: "capability_id" },
  { column: "Capability Title",   source: "capability_title" },
  { column: "Feature ID",         source: "feature_id" },
  { column: "Feature Title",      source: "feature_title" },
  { column: "Title",              source: "feature_title" },
  { column: "Priority",           source: "epic.priority_tier", transform: "map_servicenow_priority" },
  { column: "Domain",             source: "tag" },
  { column: "Theme",              source: "epic.theme" },
  { column: "Labels",             value: "$CONST:feature" },
  { column: "Notes",              value: "$CONST:AUTO-DERIVED from Story Domain Tag — v1 pragmatic hierarchy" }
  # all other columns: "$CONST:" (blank)
]
```

## STORY_FIELD_MAP

```
STORY_FIELD_MAP = [
  { column: "Item Type",          transform: "map_servicenow_item_type(story)" },
  { column: "Item ID",            source: "id" },
  { column: "Parent ID",          source: "context.parent_link_id" },
    # epic_story mode: = context.epic_entry.id (same as generic-csv-schema.md)
    # epic_capability_feature_story mode: = the synthetic Feature's Item ID
  { column: "Capability ID",      source: "context.capability_id" },     # blank in epic_story mode
  { column: "Capability Title",   source: "context.capability_title" },
  { column: "Feature ID",         source: "context.feature_id" },
  { column: "Feature Title",      source: "context.feature_title" },
  { column: "Title",              source: "narrative", transform: "build_story_summary" },
  { column: "Description",        source: "story",     transform: "build_description(story)" },
  { column: "Short Description",  source: "story",     transform: "build_short_description(story)" },
  { column: "Priority",           source: "context.epic_entry.priority_tier",
                                  transform: "map_servicenow_priority_with_override" },
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
  "Capability ID":         "",
  "Capability Title":      "",
  "Feature ID":            "",
  "Feature Title":         "",
  "Short Description":     "",
  "Priority":              "3 - Moderate",
  "label_separator":       ", "
  # all other columns default to "" — same convention as generic-csv-schema.md
}
```

---

## ServiceNow-Specific Transform Functions

### map_servicenow_priority(tier)
```
# ServiceNow's public, documented priority scale (also used by the
# researching-prd skill's ServiceNow-aligned field convention).
priority_map = {
  "Must Have":   "1 - Critical",
  "Should Have": "2 - High",
  "Could Have":  "3 - Moderate",
  "Won't Have":  "4 - Low"
}
# "5 - Planning" exists in ServiceNow's scale but no AI Pods priority_tier
# maps to it today — reserved for manual reclassification post-import.
RETURN priority_map.get(tier, "3 - Moderate")
```

### map_servicenow_priority_with_override(epic_tier, story_override)
```
RETURN map_servicenow_priority(story_override OR epic_tier)
```

### map_servicenow_item_type(story)
```
IF "SPIKE" in story.id:   RETURN "Spike"
IF "ENABLER" in story.id: RETURN "Enabler"
RETURN "Story"
```

### build_short_description(text, max_len=160)
```
# Derives a distinct, per-row summary from the SAME description text
# build_description() already produced for that row — never a static
# template. This is the structural fix for the data-quality bug observed
# in an earlier customer proof-of-concept, where "Short Description" was
# left identical to "Description" (or a static placeholder) on every row.
IF text is empty: RETURN ""
first_sentence = split on [.!?] followed by whitespace, take first segment
single_line = collapse whitespace, strip
IF len(single_line) <= max_len: RETURN single_line
RETURN single_line[:max_len] truncated at last word boundary + "..."
```

---

## Epic Key Rule

```
build_epic_key for servicenow:
  RETURN epic_entry.id     # e.g. "EPIC-01" — identical to csv-file.
  # hierarchy_mode=epic_capability_feature_story does NOT change this —
  # it only changes what a STORY's Parent ID points to (the synthetic
  # Feature, not the Epic directly). The Epic's own Parent ID is always blank.
```

---

## IMPORT_STEPS

```
1. In ServiceNow: System Import Sets > Load Data.
2. Create or reuse a Data Source, upload servicenow-import-{SESSION_ID}.csv
   (or use the delivering-servicenow-backlog skill / servicenow-delivery
   capability to push it via the instance's REST API instead of a manual
   upload — see capability_servicenow-delivery.yaml).
3. Create or reuse a Transform Map: staging table → your target table(s)
   (e.g. rm_epic / rm_story, or your Strategic Portfolio Management planning
   item tables). This mapping is owned and configured by your ServiceNow
   admin — this skill does not assume or hardcode any specific table.
4. Map each CSV column to its destination field in the Transform Map UI
   (one-time setup per ServiceNow instance/table).
5. Run Transform. Review Transform History for errors or skipped rows.
6. Verify the Parent ID chain post-import:
   - hierarchy_mode=epic_story (default):  Story → Epic
   - hierarchy_mode=epic_capability_feature_story: Story → Feature → Capability → Epic
7. Rows with Notes starting "AUTO-DERIVED" (synthetic Capability/Feature
   rows, 4-level mode only) require manual review by the portfolio owner —
   they are a mechanical starting point, not authoritative SPM planning data.

Column structure notes:
  - "Item ID" is the unique identifier for each row.
  - "Parent ID" links a row to its immediate parent in the active hierarchy mode.
  - "Priority" uses ServiceNow's standard scale: 1 - Critical, 2 - High,
    3 - Moderate, 4 - Low, 5 - Planning (reserved).
  - "Capability ID/Title" and "Feature ID/Title" are blank unless
    hierarchy_mode=epic_capability_feature_story.
  - All traceability IDs (FR IDs, NFR IDs, etc.) are comma-separated.
```
