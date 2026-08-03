# Tool State Classification — DTR

Every tool documented in the DTR is in one of five lifecycle states. The state column influences how the row is written, what Toolchain Notes subsection it lands in, and how downstream skills (research, planning, validation-tools.md derivation) interpret it.

This file is loaded in **Step 3** of `generating-toolchain-record` after Tab/Field selection but before row writing.

---

## State Definitions

| State | When to apply | How to document the row | Toolchain Notes subsection |
|---|---|---|---|
| **stable** | In use today, no change planned. Default for greenfield decisions and brownfield rows where ASD + PB agree. | `Tool Name vX.Y.Z` (or `SaaS` / `managed`) | none |
| **migrating** | Tool A is being replaced by tool B. ASD/PB confirms a target. | `Target_Tool vY.Y.Y` (the destination) | Migration Entries — record `current_tool vX → target_tool vY` |
| **upgrading** | Same tool, version change in progress. | `Tool Name vX_current` (the deployed version) | Upgrade Entries — record `vX_current → vY_target` |
| **legacy** | Still in production but slated for decommission. | `Tool Name vX (legacy)` | Legacy Entries — include decommission plan or rationale |
| **planned** | Committed in ASD but not yet deployed. | `Tool Name planned` (or version + `planned` suffix if version is known) | Planned Entries — include deployment trigger |

`legacy`, `migrating`, `upgrading` apply only when source documents support them. Without explicit ASD/PB evidence, default to `stable`.

---

## Classification Decision Tree

```
For each tool identified in the ASD/PB:

1. Does the ASD or PB describe a replacement of this tool?
   YES -> state = migrating
          row = target tool (the destination)
          notes = Migration Entries

2. Does the ASD or PB describe a version upgrade in progress?
   YES -> state = upgrading
          row = current deployed version
          notes = Upgrade Entries

3. Is the tool present today AND the ASD/PB marks it for decommission?
   YES -> state = legacy
          row = current tool with " (legacy)" suffix
          notes = Legacy Entries

4. Is the tool committed in the ASD but NOT yet running?
   YES -> state = planned
          row = "planned" (or version + planned suffix)
          notes = Planned Entries

5. Otherwise -> state = stable
              row = standard entry
              no entry in Toolchain Notes (unless inferred or TBD)
```

---

## Mode-Specific Defaults

| Mode | Default state when ambiguous | TBD policy |
|---|---|---|
| greenfield | `stable` (decision recorded for the first time) | `TBD` is normal — open architectural decisions, not gaps |
| brownfield | `stable` for documented current-state rows; `legacy` only if PB or ASD explicitly says so | `TBD` is a documentation gap — log to Toolchain Notes > Gaps |

---

## Cross-Skill Contract

| Consumer skill | Uses state for |
|---|---|
| `validating-architecture-compliance` | Stories that depend on a `legacy` or `migrating` tool may need an ADR or staged delivery. |
| `researching-feature-impl` | `legacy` and `migrating` markers signal "do not extend this code path" or "implement against the target tool." |
| `planning-code-tasks` | `upgrading` rows trigger phased planning (work on current then migrate). |
| `implementing-code` / `reviewing-code` | Do NOT consume DTR directly. They consume the derived `validation-tools.md`. State is preserved via comments or row presence/absence in that file. |

---

## Source Tagging Rules

Every non-stable state classification MUST cite its source:

- ASD section number (e.g., `[Source: ASD §6.3.4]`)
- PB section heading (e.g., `[Source: PB / Current Stack table]`)
- Inferred from build inspection (e.g., `[Source: pom.xml at source_path]`) — only allowed in brownfield mode

If no source can be cited, classify as `stable` and add to TBD or Gaps subsection accordingly.
