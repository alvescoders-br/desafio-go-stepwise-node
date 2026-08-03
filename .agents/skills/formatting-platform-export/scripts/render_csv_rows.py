#!/usr/bin/env python3
"""render_csv_rows.py — generate a platform-specific CSV import file from
the AI Pods backlog (epics + stories) artifacts.

Replaces SKILL.md Step 4 prose (atomic per-epic loop) with a single Bash
call. Handles:
  - Markdown parsing of EPICS-SPEC-*.md and per-epic story files
  - Field mapping per platform schema (jira / azure-devops / asana / csv-file)
  - Field transforms (priority, story points, labels, AC text)
  - CSV encoding: UTF-8 BOM (jira/ado/generic) or no-BOM (asana), CRLF, RFC 4180 quoting
  - Scope filter (all | selected by EPIC-IDs / US-IDs)

Usage:
  python render_csv_rows.py \
    --platform jira \
    --epics-index path/to/EPICS-SPEC-*.md \
    --stories-folder path/to/stories/epics/ \
    --output path/to/jira-import-SESSION.csv \
    --jira-project-key PCMS \
    [--scope all|selected] \
    [--selected-epics EPIC-01,EPIC-02] \
    [--selected-stories US-01-01-BE,US-01-03-FE]

Outputs:
  - Writes the CSV file at --output.
  - Prints a JSON summary to stdout: {epics_exported, stories_exported, rows_written,
    skipped, gaps, assumptions}.
  - Exit 0 on success; non-zero on hard failure.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Callable


# ──────────────────────────────────────────────────────────────────────────────
# Platform schemas (data, not code) — bundled inline so the script is single-file.
# ──────────────────────────────────────────────────────────────────────────────


COMMON_DEFAULTS = {
    "label_separator": ", ",
}


SCHEMAS: dict[str, dict] = {
    "jira": {
        "filename_prefix": "jira-import",
        "encoding": {"bom": "﻿", "line_ending": "\r\n", "delimiter": ",",
                     "quote_char": '"', "escape": '""', "label_separator": ","},
        "columns": [
            "Issue Type", "Summary", "Description", "Priority", "Story Points",
            "Labels", "Components", "Epic Link", "Epic Name", "Sprint",
            "Assignee", "Reporter", "Fix Version/s", "Affects Version/s",
            "Custom field (Team)", "Custom field (Business Value)",
            "Custom field (Risk)", "Custom field (Acceptance Criteria)",
        ],
        "epic_map": [
            {"col": "Issue Type", "value": "Epic"},
            {"col": "Summary", "src": "epic_key"},
            {"col": "Description", "transform": "description_epic"},
            {"col": "Priority", "src": "priority_tier", "transform": "jira_priority"},
            {"col": "Story Points", "value": ""},
            {"col": "Labels", "value": ""},
            {"col": "Components", "value": ""},
            {"col": "Epic Link", "value": ""},
            {"col": "Epic Name", "src": "epic_key"},
            {"col": "Sprint", "value": ""},
            {"col": "Assignee", "value": ""},
            {"col": "Reporter", "value": ""},
            {"col": "Fix Version/s", "value": ""},
            {"col": "Affects Version/s", "value": ""},
            {"col": "Custom field (Team)", "value": ""},
            {"col": "Custom field (Business Value)", "src": "kpi_ids", "transform": "join_comma"},
            {"col": "Custom field (Risk)", "src": "rsk_ids", "transform": "join_comma"},
            {"col": "Custom field (Acceptance Criteria)", "value": ""},
        ],
        "story_map": [
            {"col": "Issue Type", "transform": "jira_issue_type"},
            {"col": "Summary", "src": "narrative", "transform": "story_summary"},
            {"col": "Description", "transform": "description_story"},
            {"col": "Priority", "transform": "jira_priority_story"},
            {"col": "Story Points", "src": "complexity", "transform": "story_points"},
            {"col": "Labels", "transform": "labels_jira"},
            {"col": "Components", "src": "tag", "transform": "jira_component"},
            {"col": "Epic Link", "ctx": "epic_key"},
            {"col": "Epic Name", "value": ""},
            {"col": "Sprint", "value": ""},
            {"col": "Assignee", "value": ""},
            {"col": "Reporter", "value": ""},
            {"col": "Fix Version/s", "value": ""},
            {"col": "Affects Version/s", "value": ""},
            {"col": "Custom field (Team)", "value": ""},
            {"col": "Custom field (Business Value)", "src": "kpi_ids", "transform": "join_comma"},
            {"col": "Custom field (Risk)", "src": "rsk_ids", "transform": "join_comma"},
            {"col": "Custom field (Acceptance Criteria)", "src": "ac_list", "transform": "ac_text"},
        ],
    },
    "azure-devops": {
        "filename_prefix": "azure-import",
        "encoding": {"bom": "﻿", "line_ending": "\r\n", "delimiter": ",",
                     "quote_char": '"', "escape": '""', "label_separator": "; "},
        "columns": [
            "Work Item Type", "Title", "Description", "Priority", "Story Points",
            "Tags", "Area Path", "Iteration Path", "Assigned To", "State",
            "Parent", "Acceptance Criteria", "Original Estimate", "Activity",
            "Business Value", "Risk",
        ],
        "epic_map": [
            {"col": "Work Item Type", "value": "Feature"},
            {"col": "Title", "src": "title"},
            {"col": "Description", "transform": "description_epic"},
            {"col": "Priority", "src": "priority_tier", "transform": "ado_priority"},
            {"col": "Story Points", "value": ""},
            {"col": "Tags", "src": "theme", "transform": "ado_epic_tags"},
            {"col": "Area Path", "ctx": "azure_area_path"},
            {"col": "Iteration Path", "value": ""},
            {"col": "Assigned To", "value": ""},
            {"col": "State", "value": "New"},
            {"col": "Parent", "value": ""},
            {"col": "Acceptance Criteria", "value": ""},
            {"col": "Original Estimate", "value": ""},
            {"col": "Activity", "value": "Development"},
            {"col": "Business Value", "src": "kpi_ids", "transform": "join_semicolon"},
            {"col": "Risk", "src": "rsk_ids", "transform": "join_semicolon"},
        ],
        "story_map": [
            {"col": "Work Item Type", "transform": "ado_work_item_type"},
            {"col": "Title", "src": "narrative", "transform": "story_summary"},
            {"col": "Description", "transform": "description_story"},
            {"col": "Priority", "transform": "ado_priority_story"},
            {"col": "Story Points", "src": "complexity", "transform": "story_points"},
            {"col": "Tags", "transform": "story_tags_ado"},
            {"col": "Area Path", "ctx": "azure_area_path"},
            {"col": "Iteration Path", "value": ""},
            {"col": "Assigned To", "value": ""},
            {"col": "State", "value": "New"},
            {"col": "Parent", "ctx": "epic_key"},
            {"col": "Acceptance Criteria", "src": "ac_list", "transform": "ac_text_html"},
            {"col": "Original Estimate", "value": ""},
            {"col": "Activity", "src": "tag", "transform": "ado_activity"},
            {"col": "Business Value", "src": "kpi_ids", "transform": "join_semicolon"},
            {"col": "Risk", "src": "rsk_ids", "transform": "join_semicolon"},
        ],
    },
    "asana": {
        "filename_prefix": "asana-import",
        "encoding": {"bom": "", "line_ending": "\r\n", "delimiter": ",",
                     "quote_char": '"', "escape": '""', "label_separator": ", "},
        "columns": [
            "Name", "Description", "Assignee", "Due Date", "Start Date", "Tags",
            "Section/Column", "Priority", "Story Points", "Projects",
            "Custom Field: Acceptance Criteria", "Custom Field: Domain",
            "Custom Field: Risk IDs", "Custom Field: KPI IDs",
            "Custom Field: Story ID",
        ],
        "epic_map": [
            {"col": "Name", "src": "title"},
            {"col": "Description", "value": ""},
            {"col": "Assignee", "value": ""},
            {"col": "Due Date", "value": ""},
            {"col": "Start Date", "value": ""},
            {"col": "Tags", "value": ""},
            {"col": "Section/Column", "value": "true"},
            {"col": "Priority", "value": ""},
            {"col": "Story Points", "value": ""},
            {"col": "Projects", "ctx": "asana_project_name"},
            {"col": "Custom Field: Acceptance Criteria", "value": ""},
            {"col": "Custom Field: Domain", "value": ""},
            {"col": "Custom Field: Risk IDs", "value": ""},
            {"col": "Custom Field: KPI IDs", "value": ""},
            {"col": "Custom Field: Story ID", "src": "id"},
        ],
        "story_map": [
            {"col": "Name", "src": "narrative", "transform": "story_summary"},
            {"col": "Description", "transform": "description_story"},
            {"col": "Assignee", "value": ""},
            {"col": "Due Date", "value": ""},
            {"col": "Start Date", "value": ""},
            {"col": "Tags", "transform": "story_tags_asana"},
            {"col": "Section/Column", "ctx": "epic_key"},
            {"col": "Priority", "transform": "asana_priority_story"},
            {"col": "Story Points", "src": "complexity", "transform": "story_points"},
            {"col": "Projects", "ctx": "asana_project_name"},
            {"col": "Custom Field: Acceptance Criteria", "src": "ac_list", "transform": "ac_text"},
            {"col": "Custom Field: Domain", "src": "tag", "transform": "domain_label"},
            {"col": "Custom Field: Risk IDs", "src": "rsk_ids", "transform": "join_comma"},
            {"col": "Custom Field: KPI IDs", "src": "kpi_ids", "transform": "join_comma"},
            {"col": "Custom Field: Story ID", "src": "id"},
        ],
    },
    "csv-file": {
        "filename_prefix": "backlog-export",
        "encoding": {"bom": "﻿", "line_ending": "\r\n", "delimiter": ",",
                     "quote_char": '"', "escape": '""', "label_separator": ", "},
        "columns": [
            "Item Type", "Item ID", "Parent ID", "Title", "Description", "Priority",
            "Story Points", "Domain", "Theme", "Persona", "Labels",
            "Acceptance Criteria", "FR IDs", "NFR IDs", "KPI IDs", "Risk IDs",
            "Assumption IDs", "Complexity", "Notes",
        ],
        "epic_map": [
            {"col": "Item Type", "value": "Epic"},
            {"col": "Item ID", "src": "id"},
            {"col": "Parent ID", "value": ""},
            {"col": "Title", "src": "title"},
            {"col": "Description", "transform": "description_epic"},
            {"col": "Priority", "src": "priority_tier", "transform": "generic_priority"},
            {"col": "Story Points", "value": ""},
            {"col": "Domain", "value": ""},
            {"col": "Theme", "src": "theme"},
            {"col": "Persona", "value": ""},
            {"col": "Labels", "value": "epic"},
            {"col": "Acceptance Criteria", "value": ""},
            {"col": "FR IDs", "value": ""},
            {"col": "NFR IDs", "value": ""},
            {"col": "KPI IDs", "src": "kpi_ids", "transform": "join_comma"},
            {"col": "Risk IDs", "src": "rsk_ids", "transform": "join_comma"},
            {"col": "Assumption IDs", "value": ""},
            {"col": "Complexity", "src": "complexity"},
            {"col": "Notes", "value": ""},
        ],
        "story_map": [
            {"col": "Item Type", "transform": "generic_item_type"},
            {"col": "Item ID", "src": "id"},
            {"col": "Parent ID", "ctx": "epic_id"},
            {"col": "Title", "src": "narrative", "transform": "story_summary"},
            {"col": "Description", "transform": "description_story"},
            {"col": "Priority", "transform": "generic_priority_story"},
            {"col": "Story Points", "src": "complexity", "transform": "story_points"},
            {"col": "Domain", "src": "tag", "transform": "domain_label"},
            {"col": "Theme", "ctx": "epic_theme"},
            {"col": "Persona", "src": "narrative", "transform": "extract_persona"},
            {"col": "Labels", "transform": "labels_generic"},
            {"col": "Acceptance Criteria", "src": "ac_list", "transform": "ac_text"},
            {"col": "FR IDs", "src": "fr_ids", "transform": "join_comma"},
            {"col": "NFR IDs", "src": "nfr_ids", "transform": "join_comma"},
            {"col": "KPI IDs", "src": "kpi_ids", "transform": "join_comma"},
            {"col": "Risk IDs", "src": "rsk_ids", "transform": "join_comma"},
            {"col": "Assumption IDs", "src": "asm_ids", "transform": "join_comma"},
            {"col": "Complexity", "src": "complexity"},
            {"col": "Notes", "src": "notes"},
        ],
    },
    "servicenow": {
        "filename_prefix": "servicenow-import",
        "encoding": {"bom": "﻿", "line_ending": "\r\n", "delimiter": ",",
                     "quote_char": '"', "escape": '""', "label_separator": ", "},
        "columns": [
            "Item Type", "Item ID", "Parent ID", "Capability ID", "Capability Title",
            "Feature ID", "Feature Title", "Title", "Description", "Short Description",
            "Priority", "Story Points", "Domain", "Theme", "Persona", "Labels",
            "Acceptance Criteria", "FR IDs", "NFR IDs", "KPI IDs", "Risk IDs",
            "Assumption IDs", "Complexity", "Notes",
        ],
        "epic_map": [
            {"col": "Item Type", "value": "Epic"},
            {"col": "Item ID", "src": "id"},
            {"col": "Parent ID", "value": ""},
            {"col": "Capability ID", "value": ""},
            {"col": "Capability Title", "value": ""},
            {"col": "Feature ID", "value": ""},
            {"col": "Feature Title", "value": ""},
            {"col": "Title", "src": "title"},
            {"col": "Description", "transform": "description_epic"},
            {"col": "Short Description", "transform": "servicenow_short_description_epic"},
            {"col": "Priority", "src": "priority_tier", "transform": "servicenow_priority"},
            {"col": "Story Points", "value": ""},
            {"col": "Domain", "value": ""},
            {"col": "Theme", "src": "theme"},
            {"col": "Persona", "value": ""},
            {"col": "Labels", "value": "epic"},
            {"col": "Acceptance Criteria", "value": ""},
            {"col": "FR IDs", "value": ""},
            {"col": "NFR IDs", "value": ""},
            {"col": "KPI IDs", "src": "kpi_ids", "transform": "join_comma"},
            {"col": "Risk IDs", "src": "rsk_ids", "transform": "join_comma"},
            {"col": "Assumption IDs", "value": ""},
            {"col": "Complexity", "src": "complexity"},
            {"col": "Notes", "value": ""},
        ],
        # Synthetic Capability row — emitted once per epic, only when
        # --servicenow-hierarchy-mode=epic_capability_feature_story. Source
        # object is the epic dict; hierarchy identifiers come from ctx.
        "capability_map": [
            {"col": "Item Type", "value": "Capability"},
            {"col": "Item ID", "ctx": "capability_id"},
            {"col": "Parent ID", "src": "id"},
            {"col": "Capability ID", "ctx": "capability_id"},
            {"col": "Capability Title", "ctx": "capability_title"},
            {"col": "Feature ID", "value": ""},
            {"col": "Feature Title", "value": ""},
            {"col": "Title", "ctx": "capability_title"},
            {"col": "Description", "value": ""},
            {"col": "Short Description", "value": ""},
            {"col": "Priority", "src": "priority_tier", "transform": "servicenow_priority"},
            {"col": "Story Points", "value": ""},
            {"col": "Domain", "value": ""},
            {"col": "Theme", "src": "theme"},
            {"col": "Persona", "value": ""},
            {"col": "Labels", "value": "capability"},
            {"col": "Acceptance Criteria", "value": ""},
            {"col": "FR IDs", "value": ""},
            {"col": "NFR IDs", "value": ""},
            {"col": "KPI IDs", "value": ""},
            {"col": "Risk IDs", "value": ""},
            {"col": "Assumption IDs", "value": ""},
            {"col": "Complexity", "value": ""},
            {"col": "Notes", "value": "AUTO-DERIVED from Epic Theme — v1 pragmatic hierarchy"},
        ],
        # Synthetic Feature row — emitted once per distinct story domain-tag
        # within an epic, only in epic_capability_feature_story mode.
        "feature_map": [
            {"col": "Item Type", "value": "Feature"},
            {"col": "Item ID", "ctx": "feature_id"},
            {"col": "Parent ID", "ctx": "capability_id"},
            {"col": "Capability ID", "ctx": "capability_id"},
            {"col": "Capability Title", "ctx": "capability_title"},
            {"col": "Feature ID", "ctx": "feature_id"},
            {"col": "Feature Title", "ctx": "feature_title"},
            {"col": "Title", "ctx": "feature_title"},
            {"col": "Description", "value": ""},
            {"col": "Short Description", "value": ""},
            {"col": "Priority", "src": "priority_tier", "transform": "servicenow_priority"},
            {"col": "Story Points", "value": ""},
            {"col": "Domain", "ctx": "feature_tag"},
            {"col": "Theme", "src": "theme"},
            {"col": "Persona", "value": ""},
            {"col": "Labels", "value": "feature"},
            {"col": "Acceptance Criteria", "value": ""},
            {"col": "FR IDs", "value": ""},
            {"col": "NFR IDs", "value": ""},
            {"col": "KPI IDs", "value": ""},
            {"col": "Risk IDs", "value": ""},
            {"col": "Assumption IDs", "value": ""},
            {"col": "Complexity", "value": ""},
            {"col": "Notes", "value": "AUTO-DERIVED from Story Domain Tag — v1 pragmatic hierarchy"},
        ],
        "story_map": [
            {"col": "Item Type", "transform": "servicenow_item_type"},
            {"col": "Item ID", "src": "id"},
            {"col": "Parent ID", "ctx": "parent_link_id"},
            {"col": "Capability ID", "ctx": "capability_id"},
            {"col": "Capability Title", "ctx": "capability_title"},
            {"col": "Feature ID", "ctx": "feature_id"},
            {"col": "Feature Title", "ctx": "feature_title"},
            {"col": "Title", "src": "narrative", "transform": "story_summary"},
            {"col": "Description", "transform": "description_story"},
            {"col": "Short Description", "transform": "servicenow_short_description_story"},
            {"col": "Priority", "transform": "servicenow_priority_story"},
            {"col": "Story Points", "src": "complexity", "transform": "story_points"},
            {"col": "Domain", "src": "tag", "transform": "domain_label"},
            {"col": "Theme", "ctx": "epic_theme"},
            {"col": "Persona", "src": "narrative", "transform": "extract_persona"},
            {"col": "Labels", "transform": "labels_generic"},
            {"col": "Acceptance Criteria", "src": "ac_list", "transform": "ac_text"},
            {"col": "FR IDs", "src": "fr_ids", "transform": "join_comma"},
            {"col": "NFR IDs", "src": "nfr_ids", "transform": "join_comma"},
            {"col": "KPI IDs", "src": "kpi_ids", "transform": "join_comma"},
            {"col": "Risk IDs", "src": "rsk_ids", "transform": "join_comma"},
            {"col": "Assumption IDs", "src": "asm_ids", "transform": "join_comma"},
            {"col": "Complexity", "src": "complexity"},
            {"col": "Notes", "src": "notes"},
        ],
    },
}


# ──────────────────────────────────────────────────────────────────────────────
# Markdown parsers
# ──────────────────────────────────────────────────────────────────────────────


EPIC_HEADING_RE = re.compile(r"^#{2,4}\s+(EPIC-\d+)\s*[—:\-–]?\s*(.*)$", re.MULTILINE)
EPIC_LINE_RE = re.compile(
    r"\|\s*(EPIC-\d+)\s*\|"          # id
    r"\s*([^|]+?)\s*\|"               # title
    r"(?:\s*([^|]*?)\s*\|)?"          # priority/tier (optional col)
    r"(?:\s*([^|]*?)\s*\|)?"          # complexity (optional)
    , re.MULTILINE
)
EPIC_SUMMARY_RE = re.compile(
    r"^#{2,4}\s+(EPIC-\d+)\b[^\n]*\n(.*?)(?=^#{2,4}\s+EPIC-\d+|\Z)",
    re.MULTILINE | re.DOTALL,
)
KPI_RE = re.compile(r"\bKPI-\d+\b")
RSK_RE = re.compile(r"\bRSK-\d+\b")
FR_RE = re.compile(r"\bFR-\d+\b")
NFR_RE = re.compile(r"\bNFR-\d+\b")
ASM_RE = re.compile(r"\bASM-\d+\b")
PRIORITY_RE = re.compile(r"\b(Must Have|Should Have|Could Have|Won['’]?t Have)\b")
COMPLEXITY_RE = re.compile(r"\b(XS|S|M|L|XL|XXL)\b")
THEME_RE = re.compile(r"^\*\*Theme\*\*:?\s*(.+)$", re.MULTILINE)
TITLE_LINE_RE = re.compile(r"^Title:\s*(.+)$", re.MULTILINE)


STORY_BLOCK_RE = re.compile(
    r"^#{2,3}\s+(US-\d+(?:-\d+)?(?:-[A-Z]+)?)\b[^\n]*\n(.*?)(?=^#{2,3}\s+US-\d+|\Z)",
    re.MULTILINE | re.DOTALL,
)
NARRATIVE_RE = re.compile(r"\b[Aa]s an? [^\n]+", re.MULTILINE)
TAG_FROM_ID_RE = re.compile(r"^US-\d+-\d+-([A-Z]+)")


def parse_epics_index(path: Path) -> list[dict]:
    """Parse EPICS-SPEC-*.md and return a list of epic dicts.

    Strategy: extract per-epic sections using the EPIC-XX heading, then mine
    metadata from the section text. This is forgiving of small format
    variations across versions of planning-epics output.
    """
    text = path.read_text(encoding="utf-8")
    epics: list[dict] = []
    seen: set[str] = set()
    for match in EPIC_SUMMARY_RE.finditer(text):
        epic_id = match.group(1)
        if epic_id in seen:
            continue
        seen.add(epic_id)
        body = match.group(0)
        title = _extract_epic_title(body, epic_id)
        priority = _first_match(PRIORITY_RE, body) or "Could Have"
        complexity = _first_match(COMPLEXITY_RE, body) or ""
        kpi_ids = sorted(set(KPI_RE.findall(body)))
        rsk_ids = sorted(set(RSK_RE.findall(body)))
        theme_match = THEME_RE.search(body)
        theme = (theme_match.group(1).strip() if theme_match else "")
        epics.append({
            "id": epic_id,
            "title": title,
            "priority_tier": priority,
            "complexity": complexity,
            "kpi_ids": kpi_ids,
            "rsk_ids": rsk_ids,
            "theme": theme,
            "description": "",
        })
    if not epics:
        # Fallback: try table format.
        for tbl in EPIC_LINE_RE.finditer(text):
            epic_id = tbl.group(1)
            if epic_id in seen:
                continue
            seen.add(epic_id)
            epics.append({
                "id": epic_id,
                "title": tbl.group(2).strip(),
                "priority_tier": (tbl.group(3) or "").strip() or "Could Have",
                "complexity": (tbl.group(4) or "").strip(),
                "kpi_ids": [], "rsk_ids": [], "theme": "", "description": "",
            })
    epics.sort(key=lambda e: _priority_rank(e["priority_tier"]))
    return epics


def _priority_rank(tier: str) -> int:
    return {"Must Have": 0, "Should Have": 1, "Could Have": 2, "Won't Have": 3,
            "Won’t Have": 3}.get(tier, 4)


def _first_match(rx: re.Pattern, text: str) -> str:
    m = rx.search(text)
    return m.group(1) if m else ""


def _extract_epic_title(body: str, epic_id: str) -> str:
    head = re.search(rf"^#{{2,4}}\s+{re.escape(epic_id)}\s*[—:\-–]?\s*(.+)$", body, re.MULTILINE)
    if head and head.group(1).strip():
        return head.group(1).strip()
    line = TITLE_LINE_RE.search(body)
    return line.group(1).strip() if line else epic_id


def parse_story_file(path: Path) -> list[dict]:
    """Parse a per-epic story markdown file. Returns a list of story dicts."""
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    stories: list[dict] = []
    for match in STORY_BLOCK_RE.finditer(text):
        sid = match.group(1)
        block = match.group(0)
        narrative = _extract_narrative(block)
        ac = _extract_ac(block)
        tag_match = TAG_FROM_ID_RE.match(sid)
        tag = tag_match.group(1) if tag_match else ""
        complexity = _first_match(COMPLEXITY_RE, block) or ""
        notes = _extract_notes(block)
        stories.append({
            "id": sid,
            "tag": tag,
            "narrative": narrative,
            "ac_list": ac,
            "complexity": complexity,
            "fr_ids": sorted(set(FR_RE.findall(block))),
            "nfr_ids": sorted(set(NFR_RE.findall(block))),
            "rsk_ids": sorted(set(RSK_RE.findall(block))),
            "kpi_ids": sorted(set(KPI_RE.findall(block))),
            "asm_ids": sorted(set(ASM_RE.findall(block))),
            "notes": notes,
            "has_assumption": "[Assumption]" in block,
        })
    return stories


def _extract_narrative(block: str) -> str:
    m = NARRATIVE_RE.search(block)
    if m:
        return m.group(0).strip()
    # Fallback: first non-heading, non-empty line
    for line in block.splitlines()[1:]:
        line = line.strip()
        if line and not line.startswith("#"):
            return line
    return ""


def _extract_ac(block: str) -> list[str]:
    ac: list[str] = []
    in_section = False
    for line in block.splitlines():
        stripped = line.strip()
        if re.match(r"^#{3,5}\s*Acceptance Criteria", stripped, re.IGNORECASE):
            in_section = True
            continue
        if in_section:
            if stripped.startswith("#"):
                break
            if re.match(r"^[-*]\s+", stripped):
                ac.append(re.sub(r"^[-*]\s+", "", stripped))
            elif re.match(r"^\d+\.\s+", stripped):
                ac.append(re.sub(r"^\d+\.\s+", "", stripped))
            elif stripped.lower().startswith(("given ", "when ", "then ", "and ")):
                ac.append(stripped)
    return ac


def _extract_notes(block: str) -> str:
    m = re.search(r"^#{3,5}\s*Notes?\s*\n(.+?)(?=^#{2,5}|\Z)",
                  block, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    if not m:
        return ""
    return m.group(1).strip()


# ──────────────────────────────────────────────────────────────────────────────
# Field transforms
# ──────────────────────────────────────────────────────────────────────────────


PRIORITY_TIER_CODE = {
    "Must Have": "1", "Should Have": "2", "Could Have": "3",
    "Won't Have": "4", "Won’t Have": "4",
}
SP_MAP = {"XS": "1", "S": "2", "M": "3", "L": "5", "XL": "8", "XXL": "13"}
DOMAIN_LABELS = {"BE": "backend", "FE": "frontend", "MOBILE": "mobile",
                 "DATA": "data", "INFRA": "infra", "AI": "ai",
                 "QA": "qa", "DESIGN": "design", "FS": "fullstack"}
JIRA_COMPONENTS = {"BE": "Backend", "FE": "Frontend", "MOBILE": "Mobile",
                   "DATA": "Data Platform", "INFRA": "Infrastructure",
                   "AI": "AI/ML", "QA": "Quality Engineering",
                   "DESIGN": "Design", "FS": "Full Stack"}
ADO_ACTIVITY = {"BE": "Development", "FE": "Development", "MOBILE": "Development",
                "DATA": "Development", "INFRA": "Deployment", "AI": "Development",
                "QA": "Testing", "DESIGN": "Design", "FS": "Development"}


def _join(values: list, sep: str) -> str:
    return sep.join(v for v in (values or []) if v)


def _strip_markdown(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\*\*|__", "", text)
    text = re.sub(r"^[#>]+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*]\s+\[[ xX]\]\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\|.*?\|\s*$", lambda m: m.group(0).replace("|", " ").strip(),
                  text, flags=re.MULTILINE)
    return text.strip()


def _is_critical(story: dict) -> bool:
    return "[CRITICAL]" in (story.get("narrative") or "")


def _domain_label(tag: str) -> str:
    return DOMAIN_LABELS.get(tag or "", (tag or "").lower())


def _build_labels(story: dict, sep: str = ", ") -> str:
    labels: list[str] = [_domain_label(story.get("tag") or "")]
    sid = story.get("id", "")
    if "SPIKE" in sid:
        labels.append("spike")
    if "ENABLER" in sid:
        labels.append("enabler")
    if story.get("has_assumption"):
        labels.append("assumption-present")
    if story.get("rsk_ids"):
        labels.append("risk-flagged")
    return sep.join(l for l in labels if l)


def _ac_text(ac_list: list[str]) -> str:
    return "\n".join(ac_list or [])


def _ac_text_html(ac_list: list[str]) -> str:
    if not ac_list:
        return ""
    return "<ul>" + "".join(f"<li>{x}</li>" for x in ac_list) + "</ul>"


def _description_epic(epic: dict, _ctx: dict) -> str:
    parts = [epic.get("title", "")]
    if epic.get("description"):
        parts.append(epic["description"])
    if epic.get("kpi_ids"):
        parts.append("KPIs: " + ", ".join(epic["kpi_ids"]))
    if epic.get("rsk_ids"):
        parts.append("Risks: " + ", ".join(epic["rsk_ids"]))
    return _strip_markdown("\n\n".join(p for p in parts if p))[:2000]


def _description_story(story: dict, _ctx: dict) -> str:
    parts = [story.get("narrative", "")]
    if story.get("notes"):
        parts.append("Notes:\n" + story["notes"])
    trace = (story.get("fr_ids") or []) + (story.get("nfr_ids") or []) + \
            (story.get("rsk_ids") or []) + (story.get("kpi_ids") or [])
    if trace:
        parts.append("Traceability: " + ", ".join(trace))
    if story.get("has_assumption"):
        parts.append("[Assumption present — review required]")
    return _strip_markdown("\n\n".join(p for p in parts if p))[:32000]


def _build_short_description(text: str, max_len: int = 160) -> str:
    """Derive a distinct, per-row short summary from an already-built
    description string (composition, not a new source). This is the
    structural fix for the "Short Description identical on every row" data
    quality bug observed in an earlier ServiceNow export proof-of-concept —
    it truncates the real per-row text instead of falling back to a static
    template."""
    if not text:
        return ""
    first_sentence = re.split(r"(?<=[.!?])\s+", text.strip(), maxsplit=1)[0]
    single_line = re.sub(r"\s+", " ", first_sentence).strip()
    if len(single_line) <= max_len:
        return single_line
    truncated = single_line[:max_len]
    if " " in truncated:
        truncated = truncated.rsplit(" ", 1)[0]
    return truncated + "..."


def _story_summary(narrative: str, _ctx: dict) -> str:
    if not narrative:
        return ""
    line = next((l for l in narrative.splitlines() if l.strip()), "")
    if len(line) > 255:
        line = line[:252] + "…"
    return line


def _extract_persona(narrative: str, _ctx: dict) -> str:
    if not narrative:
        return ""
    m = re.search(r"[Aa]s an? ([^,\n]+)[,\n]", narrative)
    return m.group(1).strip() if m else ""


# Per-platform priority maps
JIRA_PRIORITY = {"0": "Highest", "1": "Highest", "2": "High",
                 "3": "Medium", "4": "Low"}
ADO_PRIORITY = {"Must Have": "1", "Should Have": "2",
                "Could Have": "3", "Won't Have": "4", "Won’t Have": "4"}
ASANA_PRIORITY = {"Must Have": "High", "Should Have": "Medium",
                  "Could Have": "Low", "Won't Have": "Low", "Won’t Have": "Low"}
GENERIC_PRIORITY = {"Must Have": "High", "Should Have": "Medium",
                    "Could Have": "Low", "Won't Have": "Lowest",
                    "Won’t Have": "Lowest"}
# ServiceNow's public, documented priority scale (1 - Critical .. 5 - Planning;
# "5 - Planning" is reserved — no AI Pods priority_tier maps to it today).
SERVICENOW_PRIORITY = {"Must Have": "1 - Critical", "Should Have": "2 - High",
                       "Could Have": "3 - Moderate", "Won't Have": "4 - Low",
                       "Won’t Have": "4 - Low"}
# Human-readable Feature titles for the synthetic 4-level hierarchy mode
# (distinct from DOMAIN_LABELS above, which stays lowercase for the "Domain" column).
SERVICENOW_FEATURE_LABELS = {"BE": "Backend", "FE": "Frontend", "MOBILE": "Mobile",
                             "DATA": "Data", "INFRA": "Infrastructure", "AI": "AI/ML",
                             "QA": "Quality Assurance", "DESIGN": "Design",
                             "FS": "Full-Stack", "GENERAL": "General"}


# Transforms registered by name. Each takes (raw, ctx) and returns a string.
def _make_transforms() -> dict[str, Callable]:
    def jira_priority(raw, ctx):
        code = PRIORITY_TIER_CODE.get(raw, "3")
        return JIRA_PRIORITY.get(code, "Medium")

    def jira_priority_story(_raw, ctx):
        story = ctx["story"]
        if _is_critical(story):
            return JIRA_PRIORITY["0"]
        tier = ctx["epic"].get("priority_tier", "Could Have")
        return JIRA_PRIORITY.get(PRIORITY_TIER_CODE.get(tier, "3"), "Medium")

    def jira_issue_type(_raw, ctx):
        return "Story"

    def jira_component(raw, ctx):
        return JIRA_COMPONENTS.get(raw or "", "")

    def ado_priority(raw, _ctx):
        return ADO_PRIORITY.get(raw, "3")

    def ado_priority_story(_raw, ctx):
        story = ctx["story"]
        if _is_critical(story):
            return "1"
        tier = ctx["epic"].get("priority_tier", "Could Have")
        return ADO_PRIORITY.get(tier, "3")

    def ado_work_item_type(_raw, ctx):
        sid = ctx["story"].get("id", "")
        if "SPIKE" in sid:
            return "Task"
        return "User Story"

    def ado_activity(raw, _ctx):
        return ADO_ACTIVITY.get(raw or "", "Development")

    def ado_epic_tags(raw, _ctx):
        tags = []
        if raw:
            tags.append(raw.replace(" ", "-").lower())
        tags.append("epic")
        return "; ".join(tags)

    def asana_priority_story(_raw, ctx):
        story = ctx["story"]
        if _is_critical(story):
            return "High"
        tier = ctx["epic"].get("priority_tier", "Could Have")
        return ASANA_PRIORITY.get(tier, "Medium")

    def generic_priority(raw, _ctx):
        return GENERIC_PRIORITY.get(raw, "Medium")

    def generic_priority_story(_raw, ctx):
        story = ctx["story"]
        if _is_critical(story):
            return "High"
        tier = ctx["epic"].get("priority_tier", "Could Have")
        return GENERIC_PRIORITY.get(tier, "Medium")

    def generic_item_type(_raw, ctx):
        sid = ctx["story"].get("id", "")
        if "SPIKE" in sid:
            return "Spike"
        if "ENABLER" in sid:
            return "Enabler"
        return "Story"

    def story_points(raw, _ctx):
        return SP_MAP.get(raw or "", "")

    def domain_label(raw, _ctx):
        return _domain_label(raw or "")

    def labels_jira(_raw, ctx):
        return _build_labels(ctx["story"], ",")

    def labels_generic(_raw, ctx):
        return _build_labels(ctx["story"], ", ")

    def story_tags_ado(_raw, ctx):
        return _build_labels(ctx["story"], "; ")

    def story_tags_asana(_raw, ctx):
        return _build_labels(ctx["story"], ", ")

    def join_comma(raw, _ctx):
        return _join(raw, ", ")

    def join_semicolon(raw, _ctx):
        return _join(raw, "; ")

    def description_epic(_raw, ctx):
        return _description_epic(ctx["epic"], ctx)

    def description_story(_raw, ctx):
        return _description_story(ctx["story"], ctx)

    def story_summary(raw, _ctx):
        return _story_summary(raw or "", _ctx)

    def extract_persona(raw, _ctx):
        return _extract_persona(raw or "", _ctx)

    def ac_text(raw, _ctx):
        return _ac_text(raw or [])

    def ac_text_html(raw, _ctx):
        return _ac_text_html(raw or [])

    def servicenow_priority(raw, _ctx):
        return SERVICENOW_PRIORITY.get(raw, "3 - Moderate")

    def servicenow_priority_story(_raw, ctx):
        story = ctx["story"]
        if _is_critical(story):
            return SERVICENOW_PRIORITY["Must Have"]
        tier = ctx["epic"].get("priority_tier", "Could Have")
        return SERVICENOW_PRIORITY.get(tier, "3 - Moderate")

    def servicenow_item_type(_raw, ctx):
        sid = ctx["story"].get("id", "")
        if "SPIKE" in sid:
            return "Spike"
        if "ENABLER" in sid:
            return "Enabler"
        return "Story"

    def servicenow_short_description_epic(_raw, ctx):
        return _build_short_description(_description_epic(ctx["epic"], ctx))

    def servicenow_short_description_story(_raw, ctx):
        return _build_short_description(_description_story(ctx["story"], ctx))

    return {fn.__name__: fn for fn in [
        jira_priority, jira_priority_story, jira_issue_type, jira_component,
        ado_priority, ado_priority_story, ado_work_item_type, ado_activity,
        ado_epic_tags, asana_priority_story, generic_priority,
        generic_priority_story, generic_item_type, story_points, domain_label,
        labels_jira, labels_generic, story_tags_ado, story_tags_asana,
        join_comma, join_semicolon, description_epic, description_story,
        story_summary, extract_persona, ac_text, ac_text_html,
        servicenow_priority, servicenow_priority_story, servicenow_item_type,
        servicenow_short_description_epic, servicenow_short_description_story,
    ]}


TRANSFORMS = _make_transforms()


# ──────────────────────────────────────────────────────────────────────────────
# Row builder
# ──────────────────────────────────────────────────────────────────────────────


def _resolve(field: dict, source: dict, ctx: dict) -> str:
    if "value" in field:
        return field["value"]
    if "ctx" in field:
        return str(ctx.get(field["ctx"], "") or "")
    raw = None
    src_key = field.get("src")
    if src_key:
        if src_key == "epic_key":
            raw = ctx.get("epic_key")
        else:
            raw = source.get(src_key)
    transform = field.get("transform")
    if transform:
        fn = TRANSFORMS.get(transform)
        if fn is None:
            raise KeyError(f"unknown transform: {transform}")
        return str(fn(raw, ctx) or "")
    return str(raw or "")


def _build_row(field_map: list[dict], source: dict, ctx: dict, n_cols: int) -> list[str]:
    row = [_resolve(field, source, ctx) for field in field_map]
    if len(row) < n_cols:
        row += [""] * (n_cols - len(row))
    elif len(row) > n_cols:
        row = row[:n_cols]
    return row


def _encode_row(row: list[str], encoding: dict) -> str:
    delim = encoding.get("delimiter", ",")
    quote = encoding.get("quote_char", '"')
    escape = encoding.get("escape", '""')
    line_ending = encoding.get("line_ending", "\r\n")
    encoded = []
    for field in row:
        cell = (field or "").replace(quote, escape)
        encoded.append(f"{quote}{cell}{quote}")
    return delim.join(encoded) + line_ending


def _build_epic_key(epic: dict, platform: str, jira_project_key: str) -> str:
    if platform == "jira":
        key = f"[{jira_project_key}] {epic.get('title', '')}".strip()
        if len(key) > 60:
            key = key[:57] + "…"
        return key
    if platform in ("azure-devops", "asana"):
        return epic.get("title", "")
    if platform in ("csv-file", "servicenow"):
        return epic.get("id", "")
    return epic.get("title", "")


# ──────────────────────────────────────────────────────────────────────────────
# Pipeline
# ──────────────────────────────────────────────────────────────────────────────


def run(args: argparse.Namespace) -> int:
    schema = SCHEMAS.get(args.platform)
    if schema is None:
        print(f"error: unknown platform: {args.platform}", file=sys.stderr)
        return 2
    if args.platform == "jira" and not args.jira_project_key:
        print("error: --jira-project-key is required for platform=jira", file=sys.stderr)
        return 2

    epics = _load_epics(args)
    if not epics:
        print("error: no epics found", file=sys.stderr)
        return 3

    selected_epics: set[str] = set(_split(args.selected_epics))
    selected_stories: set[str] = set(_split(args.selected_stories))

    if args.scope == "selected":
        epics = [e for e in epics if e["id"] in selected_epics or
                 _has_selected_story(e, selected_stories, args)]

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    encoding = schema["encoding"]
    rows_written = 0
    epics_exported: list[str] = []
    stories_exported: list[str] = []
    skipped: list[dict] = []
    gaps: list[dict] = []
    assumptions: list[str] = []

    with output_path.open("w", encoding="utf-8", newline="") as fh:
        bom = encoding.get("bom", "")
        if bom:
            fh.write(bom)
        # header row (raw — not quoted, per CSV convention; keep parity with the
        # existing skill's COLUMN_HEADERS which are pre-quoted in the docs).
        # For consistency with import tools, we emit quoted headers too.
        fh.write(_encode_row(schema["columns"], encoding))
        n_cols = len(schema["columns"])

        for epic in epics:
            epic_id = epic["id"]
            if args.scope == "selected" and epic_id not in selected_epics and not _has_selected_story(epic, selected_stories, args):
                continue

            stories = _load_stories(epic, args)
            if args.scope == "selected" and selected_stories:
                stories = [s for s in stories if s["id"] in selected_stories]

            ctx_base = {
                "epic": epic,
                "epic_id": epic_id,
                "epic_theme": epic.get("theme", ""),
                "azure_area_path": args.azure_area_path or "",
                "asana_project_name": args.asana_project_name or "",
                # ServiceNow hierarchy context — inert for every other platform
                # (their field maps never reference these ctx keys).
                "parent_link_id": "",
                "capability_id": "",
                "capability_title": "",
                "feature_id": "",
                "feature_title": "",
            }
            epic_key = _build_epic_key(epic, args.platform, args.jira_project_key or "")
            ctx_base["epic_key"] = epic_key
            ctx_base["parent_link_id"] = epic_key

            try:
                epic_row = _build_row(schema["epic_map"], epic, ctx_base, n_cols)
            except KeyError as exc:
                gaps.append({"epic": epic_id, "reason": f"transform error: {exc}"})
                skipped.append({"id": epic_id, "reason": "transform error"})
                continue

            fh.write(_encode_row(epic_row, encoding))
            rows_written += 1
            epics_exported.append(epic_id)

            # Synthetic Capability/Feature rows — ServiceNow, opt-in only.
            # Default hierarchy mode (epic_story) and every other platform
            # skip this block entirely: zero behavior change.
            tag_to_feature: dict[str, dict] = {}
            if (args.platform == "servicenow"
                    and args.servicenow_hierarchy_mode == "epic_capability_feature_story"):
                cap_ctx = dict(ctx_base)
                cap_ctx["capability_id"] = f"CAP-{epic_id}"
                cap_ctx["capability_title"] = epic.get("theme") or f"{epic_id} Capability"
                capability_row = _build_row(schema["capability_map"], epic, cap_ctx, n_cols)
                fh.write(_encode_row(capability_row, encoding))
                rows_written += 1

                tags_present = sorted({(s.get("tag") or "GENERAL") for s in stories})
                for tag in tags_present:
                    feat_ctx = dict(cap_ctx)
                    feat_ctx["feature_id"] = f"FEAT-{epic_id}-{tag}"
                    feat_ctx["feature_title"] = (
                        f"{epic.get('title', '')} — {SERVICENOW_FEATURE_LABELS.get(tag, tag.title())}"
                    )
                    feat_ctx["feature_tag"] = tag
                    feature_row = _build_row(schema["feature_map"], epic, feat_ctx, n_cols)
                    fh.write(_encode_row(feature_row, encoding))
                    rows_written += 1
                    tag_to_feature[tag] = {
                        "feature_id": feat_ctx["feature_id"],
                        "feature_title": feat_ctx["feature_title"],
                        "capability_id": cap_ctx["capability_id"],
                        "capability_title": cap_ctx["capability_title"],
                    }

            for story in stories:
                ctx = dict(ctx_base, story=story)
                if tag_to_feature:
                    story_tag = story.get("tag") or "GENERAL"
                    link = tag_to_feature.get(story_tag)
                    if link:
                        ctx["parent_link_id"] = link["feature_id"]
                        ctx["capability_id"] = link["capability_id"]
                        ctx["capability_title"] = link["capability_title"]
                        ctx["feature_id"] = link["feature_id"]
                        ctx["feature_title"] = link["feature_title"]
                    else:
                        # Should not happen — tag_to_feature is built from this
                        # same `stories` list — but if it ever does, surface it
                        # instead of silently orphaning the story from its
                        # Feature/Capability (broken Parent ID chain).
                        gaps.append({
                            "story": story["id"],
                            "reason": f"no Feature entry for tag '{story_tag}' in "
                                      f"epic_capability_feature_story mode — Parent ID "
                                      f"falls back to the Epic directly",
                        })
                story_row = _build_row(schema["story_map"], story, ctx, n_cols)
                fh.write(_encode_row(story_row, encoding))
                rows_written += 1
                stories_exported.append(story["id"])
                if story.get("has_assumption"):
                    assumptions.append(f"{story['id']}: assumption present")

    summary = {
        "platform": args.platform,
        "output": str(output_path),
        "rows_written": rows_written,
        "epics_exported": epics_exported,
        "stories_exported": stories_exported,
        "skipped": skipped,
        "gaps": gaps,
        "assumptions": assumptions,
        "header_columns": len(schema["columns"]),
    }
    print(json.dumps(summary, indent=2, sort_keys=False))
    return 0


def _split(value: str | None) -> list[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def _has_selected_story(epic: dict, selected: set[str], args: argparse.Namespace) -> bool:
    if not selected:
        return False
    for story in _load_stories(epic, args, headers_only=True):
        if story["id"] in selected:
            return True
    return False


def _load_epics(args: argparse.Namespace) -> list[dict]:
    if args.epics_json:
        with open(args.epics_json, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict) and "epics" in data:
            return data["epics"]
        if isinstance(data, list):
            return data
        return []
    if args.epics_index:
        return parse_epics_index(Path(args.epics_index))
    print("error: provide --epics-index or --epics-json", file=sys.stderr)
    return []


def _load_stories(epic: dict, args: argparse.Namespace, headers_only: bool = False) -> list[dict]:
    if args.stories_json:
        with open(args.stories_json, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            return data.get(epic["id"], [])
        return []
    if args.stories_folder:
        # Expect path: {stories_folder}/epic-{nn}.md
        epic_num = epic["id"].split("-", 1)[-1].lstrip("0").rjust(2, "0")
        candidate = Path(args.stories_folder) / f"epic-{epic_num}.md"
        if not candidate.exists():
            # fallback: search any file containing the epic id
            for p in Path(args.stories_folder).glob("*.md"):
                if epic["id"].lower() in p.name.lower():
                    candidate = p
                    break
        return parse_story_file(candidate)
    return []


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Render a platform-specific CSV import file from AI Pods backlog artifacts."
    )
    p.add_argument("--platform", required=True, choices=list(SCHEMAS.keys()))
    p.add_argument("--output", required=True, help="CSV output path")
    p.add_argument("--epics-index", help="Path to EPICS-SPEC-*.md")
    p.add_argument("--epics-json", help="Path to JSON of pre-parsed epics (alternative to --epics-index)")
    p.add_argument("--stories-folder", help="Path to stories/epics/ folder (per-epic md files)")
    p.add_argument("--stories-json",
                   help="Path to JSON map {EPIC-ID: [story dicts]} (alternative to --stories-folder)")
    p.add_argument("--scope", choices=["all", "selected"], default="all")
    p.add_argument("--selected-epics", help="Comma-separated EPIC-IDs (used when scope=selected)")
    p.add_argument("--selected-stories", help="Comma-separated US-IDs (used when scope=selected)")
    p.add_argument("--jira-project-key", help="Required for platform=jira (e.g. PCMS)")
    p.add_argument("--azure-area-path", help="Optional Azure DevOps Area Path")
    p.add_argument("--asana-project-name", help="Optional Asana project name")
    p.add_argument("--servicenow-hierarchy-mode",
                   choices=["epic_story", "epic_capability_feature_story"],
                   default="epic_story",
                   help="ServiceNow only. epic_story (default, 2 levels, identical to "
                        "csv-file) or epic_capability_feature_story (4 levels, synthetic "
                        "Capability/Feature rows derived from Epic Theme + Story Domain tag)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
