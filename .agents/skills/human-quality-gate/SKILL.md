---
name: human-quality-gate
description: Simple human validation checkpoint. Review artifacts against criteria and approve or reject with feedback. Use when workflows require human sign-off on generated artifacts (PRDs, epics, user stories, code deliverables), quality gates, or artifact review checkpoints.
license: MIT
metadata:
  version: "2.0.0"
  author: aipods
  category: meta
---

# Human Quality Gate

This is a simple human checkpoint in the workflow. Review the generated artifacts, check them against the quality criteria, and make a decision:

- **APPROVE**: Artifacts meet quality standards → workflow continues
- **REJECT**: Artifacts need improvement → provide feedback for retry

## Prerequisites

- Generated artifacts are available at the specified path
- Quality criteria document is available for reference
- You understand what upstream artifacts were used as inputs

## Step-by-step instructions

### Step 1: Review Artifacts

Open and examine the generated artifacts. Check for completeness, clarity, and correctness.

**Parameter:** `artifacts_path` — Path to the artifacts (e.g., `./outputs/epics.md`, `./outputs/user-stories.md`, `./outputs/prd.md`)

### Step 2: Check Against Criteria

Open the `quality_criteria_path` document. Review each criterion listed and verify that artifacts meet the stated requirements. Note any gaps, errors, or areas needing improvement.

**Parameter:** `quality_criteria_path` — Path to quality criteria (default: `./criteria/`)

### Step 3: Review Upstream Context

If `upstream_artifacts` are provided:

- Review the source documents that were used as inputs
- Verify that generated artifacts align with and properly reference source material
- Check for any missing information that should have been included

**Parameter:** `upstream_artifacts` — Optional array of source artifact paths (e.g., `["./outputs/prd.md", "./outputs/features.md"]`)

### Step 4: Make Decision

- **TO APPROVE:** If artifacts meet quality criteria: Simply confirm "OK" or "APPROVED"
- **TO REJECT:** If artifacts need improvement: Fail and provide clear, specific feedback explaining what needs to be fixed

## Handling automated verification signals (invariants)

Some upstream steps produce automated review verdicts (e.g. a platform-conformance
or artifact-verification report, or an escalated automated verdict gate). When such
signals are present, they are **advisory inputs to your judgment — never a substitute
for it**. Three invariants hold on every correctness/platform gate:

1. **Automated signals route and pre-filter; they never auto-skip this gate.** A
   PASS verdict does not relieve you of review; a low-disagreement / "confident"
   signal is exactly the confident-but-wrong failure mode to watch for. You remain
   the terminal authority.
2. **Correctness and platform gates are never auto-approved.** Read the conformance
   findings / verification report. Treat any BLOCKER finding or FAILED verdict as a
   strong reason to REJECT with feedback. If the work was escalated here because an
   automated verdict gate exhausted its retries, the iteration trail is in the
   session's navigation history — review it before deciding.
3. **False positives are worse than false negatives — escalate when uncertain.**
   When unsure whether the work is correct, REJECT (or hold) rather than approve.
   Wrongly passing bad work is more costly than wrongly failing good work.

## Parameters

Provided by the capability via step context. The capability interpolates these from its parameters.

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| artifacts_path | Yes | — | Path to artifacts to validate |
| quality_criteria_path | Yes | `./criteria/` | Path to quality criteria document |
| upstream_artifacts | No | — | Paths to source artifacts for consistency checking (comma-separated) |
