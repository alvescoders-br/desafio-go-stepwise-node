# Quality Gates — Rationalizations, Red Flags, Verification

Read this reference at the **Step 4 → Step 5 boundary** (after running the 18 quality validation checks, before writing outputs). The three sections below catch superficial research and surface evidence gaps before the spec is finalized.

---

## Common Rationalizations (Anti-Rationalization Table)

| Excuse | Why It Fails | Counter |
|--------|-------------|---------|
| "The architecture docs are comprehensive, I don't need deep code research" | Architecture defines WHAT to build. Code research identifies HOW to integrate with existing code. Different concerns. | Research must analyze actual source code patterns, not just architecture diagrams. |
| "I'll figure out the integration points during implementation" | Discovering integration points during implementation causes plan deviations and rework. Research prevents surprises. | Map every integration point, dependency, and affected file BEFORE planning begins. |
| "The existing code is straightforward, no research needed" | Straightforward code still has conventions, patterns, and implicit contracts. Violating them causes review rejections. | Even clean codebases have undocumented conventions. Research identifies patterns the implementing agent must follow. |
| "This is a greenfield project, there's nothing to research" | Greenfield still has: tech stack constraints, ADR decisions, architecture patterns, and NFR requirements to analyze. | Research scope shifts from existing code to upstream artifacts. The analysis is different, not absent. |
| "The user stories are detailed enough to start planning" | User stories define WHAT the user wants. Research identifies HOW the codebase supports it and WHERE the gaps are. | Research bridges the gap between requirements (stories) and implementation reality (code). |

---

## Red Flags

Signs that code design research is being conducted superficially:

- Research output doesn't reference actual source files (analysis based on assumptions, not code)
- Zero integration points identified for a brownfield project (every change integrates somewhere)
- Tech stack analysis missing when ADRs specify technology choices
- No file impact assessment (implementing agent won't know what to modify)
- Research completed without reading source_path contents (when source_path was provided)
- Pattern analysis section empty despite existing codebase
- All items marked `status: complete` but affected_files list is empty
- No open_questions on a complex multi-story research (indicates insufficient depth)
- Research doesn't reference upstream artifacts (PRD, epics, ADRs, architecture)

---

## Verification Checklist with Evidence

Every item requires **evidence**, not assertion. "Seems right" is never sufficient.

- [ ] Source code analyzed (when available) — Evidence: file:line references in analysis sections
- [ ] Integration points mapped — Evidence: explicit list of files/modules where new code connects to existing code
- [ ] Tech stack constraints documented — Evidence: references to ADRs and architecture specs
- [ ] Affected files identified — Evidence: affected_files list with modification type (create/modify/delete)
- [ ] Pattern analysis completed — Evidence: existing code patterns documented with examples from source
- [ ] All user stories addressed — Evidence: story-to-research traceability (every story has analysis)
- [ ] NFR implications assessed — Evidence: performance, security, scalability considerations per story
- [ ] Open questions captured — Evidence: open_questions section with unresolvable items
- [ ] Zero Invention Policy respected — Evidence: every claim traces to source code, ADR, or architecture doc
