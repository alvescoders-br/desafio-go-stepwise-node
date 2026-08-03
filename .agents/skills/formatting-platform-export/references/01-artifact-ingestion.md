# Artifact Ingestion — Load Upstream Epics & Stories

## Context Contract
- **Called from:** SKILL.md Step 2
- **Inputs:** epics_output_path, stories_output_path, EXPORT_INDEX
- **Outputs:** EXPORT_INDEX.epic_ids populated, STORY_REGISTRY built
- **Carries forward:** EXPORT_INDEX (lightweight IDs + metadata only), STORY_REGISTRY
- **Flush after:** All loaded artifact text. Retain only the index structures.
- **Dependencies:** epics and stories artifacts must be on disk.

---

## Phase 1: Resolve Artifact Paths

```
# Resolve epics artifact
IF epics_output_path ends in .md (index file):
  EPICS_INDEX_FILE = epics_output_path
  EPICS_FOLDER = parent directory of epics_output_path
ELSE (folder path):
  EPICS_FOLDER = epics_output_path
  EPICS_INDEX_FILE = find EPICS-SPEC-*.md in EPICS_FOLDER

IF EPICS_INDEX_FILE does not exist → LOG gap: "Epics index not found at {epics_output_path}" → EXIT.

# Resolve stories artifact
IF stories_output_path ends in .md:
  STORIES_INDEX_FILE = stories_output_path
  STORIES_FOLDER = parent directory of stories_output_path
ELSE:
  STORIES_FOLDER = stories_output_path
  STORIES_INDEX_FILE = find STORIES-MANIFEST-*.md in STORIES_FOLDER

STORIES_EPICS_SUBFOLDER = STORIES_FOLDER + 'epics/'

IF STORIES_INDEX_FILE does not exist → LOG gap: "Stories index not found at {stories_output_path}" → EXIT.
IF STORIES_EPICS_SUBFOLDER does not exist → LOG gap: "epics/ subfolder missing in stories folder" → EXIT.

LOG: "Epics artifact resolved: {EPICS_FOLDER}"
LOG: "Stories artifact resolved: {STORIES_FOLDER}"
```

---

## Phase 2: Load Epics Metadata

```
# Load the epics index file
READ EPICS_INDEX_FILE

# Extract from the Summary Metrics section:
FOR EACH epic in the index:
  EPIC_ENTRY = {
    id: "EPIC-XX",
    title: "...",
    priority_tier: "Must Have | Should Have | Could Have | Won't Have",
    complexity: "S | M | L | XL",   # from Prioritized Backlog; use "" if absent
    kpi_ids: ["KPI-XX", ...],       # from Backlog traceability; use [] if absent
    rsk_ids: ["RSK-XX", ...],       # from Backlog traceability; use [] if absent
    theme: "..."                     # from Features List; use "" if absent
  }
  EXPORT_INDEX.epic_ids.append(EPIC_ENTRY)

# Ordering: preserve priority-tier order from the epics backlog:
# Must Have → Should Have → Could Have → Won't Have

IF EXPORT_INDEX.epic_ids is empty:
  LOG gap: "No EPIC-IDs extracted from epics index."
  EXIT (cannot generate CSV without epics).

LOG: "Epics loaded: {count} epics in scope."

# FLUSH: Drop EPICS_INDEX_FILE content from memory.
# RETAIN: EXPORT_INDEX.epic_ids
```

---

## Phase 3: Build STORY_REGISTRY (Lightweight Scan)

```
# Do NOT load full story text here. Load per-epic file only in Step 4.
# Here, extract only the ID list and metadata per epic for scope filtering.

READ STORIES_INDEX_FILE

FOR EACH epic entry in the stories index Quick Navigation table:
  EPIC_ID = extract from filename (e.g., "epics/epic-01.md" → "EPIC-01")
  STORY_FILE_PATH = STORIES_EPICS_SUBFOLDER + 'epic-{NN}.md'

  # Scan the story file HEADERS only (H2/H3 lines) to extract story IDs
  # without loading full body. This is a lightweight scan.
  READ first 200 lines of STORY_FILE_PATH
  STORY_IDS = extract all US-XX-NN-TAG patterns found

  STORY_REGISTRY[EPIC_ID] = {
    file_path: STORY_FILE_PATH,
    story_ids: STORY_IDS,
    story_count: len(STORY_IDS)
  }

IF STORY_REGISTRY is empty:
  LOG gap: "No story files found in {STORIES_EPICS_SUBFOLDER}"
  EXIT.

LOG: "Story registry built: {sum of story_counts} stories across {count} epics."

# FLUSH: Drop STORIES_INDEX_FILE content and story file header text.
# RETAIN: STORY_REGISTRY (IDs + file paths only)
```

---

## Phase 4: Apply Scope Filter

```
IF export_scope == "selected":
  # Parse comma-separated IDs
  SELECTED_EPIC_IDS  = [id.strip() for id in selected_epics.split(',') if id.strip()]
  SELECTED_STORY_IDS = [id.strip() for id in selected_stories.split(',') if id.strip()]

  # An epic is in scope if:
  #   a) It is explicitly in SELECTED_EPIC_IDS, OR
  #   b) It is the parent of at least one story in SELECTED_STORY_IDS
  IN_SCOPE_EPICS = []
  FOR EACH epic in EXPORT_INDEX.epic_ids:
    if epic.id in SELECTED_EPIC_IDS:
      IN_SCOPE_EPICS.append(epic.id)
    else:
      # Check if any selected story belongs to this epic
      epic_story_ids = STORY_REGISTRY[epic.id].story_ids
      if any(s in SELECTED_STORY_IDS for s in epic_story_ids):
        IN_SCOPE_EPICS.append(epic.id)

  # Remove out-of-scope epics from index
  FOR EACH epic in EXPORT_INDEX.epic_ids:
    IF epic.id NOT IN IN_SCOPE_EPICS:
      EXPORT_INDEX.skipped_items.append({ id: epic.id, reason: "not in selected scope" })
  EXPORT_INDEX.epic_ids = [e for e in EXPORT_INDEX.epic_ids if e.id in IN_SCOPE_EPICS]

  # For epics that are in scope via story selection, mark which stories are in scope
  EXPORT_INDEX.selected_story_ids = SELECTED_STORY_IDS

  LOG: "Scope filter applied: {count} epics in scope, {count} skipped."

ELSE:  # export_scope == "all"
  LOG: "Scope = all. All {count} epics included."
  EXPORT_INDEX.selected_story_ids = []  # means "all stories"
```

---

## Phase 5: Complete Research Phase

```
# Update EXPORT_INDEX
EXPORT_INDEX.story_ids = flatten(STORY_REGISTRY[epic.id].story_ids
                                  for epic in EXPORT_INDEX.epic_ids)
EXPORT_INDEX.batch_status.research = "COMPLETE @ {timestamp}"

LOG: "Research complete."
LOG: "  Epics in scope: {count}"
LOG: "  Stories in scope: {count}"
LOG: "  STORY_REGISTRY keys: {epic_ids}"

# Final flush
# RETAIN: EXPORT_INDEX, STORY_REGISTRY
# FLUSH: all file contents loaded during this phase
```