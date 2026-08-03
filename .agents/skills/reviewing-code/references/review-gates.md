# Review Gates — Pre-Flight & Output Existence

Two gates that bracket the review session. The Pre-Flight gate runs **before Step 1**; the Output Existence gate runs **before exit**. Both are mandatory.

---

## Pre-Flight Validation (MANDATORY before Step 1)

```
BEFORE starting the review, validate that all required inputs are accessible:

1. SOURCE FILE ACCESSIBILITY CHECK:
   - Run: ls -la {source_path} to confirm directory exists and is readable
   - Run: ls -la {plan_folder_path} to confirm plan folder exists
   - Run: ls -la {research_folder_path} to confirm research folder exists
   - Run: ls -la {progress_folder_path} to confirm progress folder exists
   - IF ANY path is inaccessible → ABORT with clear error:
     "PRE-FLIGHT FAILED: {path} is not accessible. Verify the path exists and
      the agent has read permissions. Do not proceed with review."

2. PLAN FILE CROSS-CHECK:
   - Extract the list of source files referenced in the plan
   - For each referenced file, verify it exists at {source_path}/{relative_path}
   - LOG missing files as: "PRE-FLIGHT WARNING: {file} referenced in plan but
     not found at expected location"
   - If >50% of planned files are missing → ABORT: "Source tree does not match
     plan. Verify source_path points to the correct implementation output."

3. OUTPUT FORMAT VALIDATION (before marking complete):
   - REVIEW-SPEC must contain ALL mandatory sections:
     header, summary, findings, traceability, tool_results, ac_status
   - findings section must use structured format:
     | ID | Severity | File | Line | Description | Evidence | Recommendation |
   - If any mandatory section is missing or empty → do NOT mark as complete.
     Fill the missing section or mark status as INCOMPLETE with explanation.
   - review_feedback output parameter must match findings:
     one line per BLOCKING/HIGH finding in format [SEVERITY] [FILE] [DESCRIPTION]
```

---

## Output Existence Validation (MANDATORY before exit)

Before completing execution:

1. Verify SPEC_FILE (REVIEW-SPEC-*.md) exists at validation_output_path and is non-empty
2. Verify AUDIT_FILE (REVIEW-AUDIT-*.md) exists and is non-empty
3. IF NO output files exist:
   - Do NOT exit with success
   - Call `stepwise session exec-fail` with message:
     "No review output produced — possible provider error. Retry required."
4. Only exit successfully if at least SPEC_FILE is present and non-empty
