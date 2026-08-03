# Phase C Pre-Completion Checklist

Read this reference at the **Phase C → Phase D boundary**. Every item below must be verified before you can transition to Phase D.

This file consolidates four checks that previously lived in SKILL.md:
1. TDAD Compliance Check
2. Implementation Completeness Self-Check
3. Plan File Coverage Gate
4. Pre-Completion Quality Checklist (10 items)

---

## 1. TDAD Compliance Check (when tdad_mode enabled)

```
BEFORE marking any phase as COMPLETED when tdad_mode is enabled:

1. EXTRACT all test case IDs from the plan's Phase 1 TDAD RED section:
   - Parse PLAN-SPEC phases[].tdad_red (agent-native) or phase doc RED section (legacy)
   - Build: PLANNED_TEST_IDS = [TC-001, TC-002, ...]
   - ALSO collect the `testing_strategy.test_case_id` values. When a row cites an
     upstream FTC id (e.g. FTC_01_03_02), that FTC id is the PLANNED_TEST_ID and
     the matching test (step 2) SHOULD reference it in a comment or test name.
   - EXCLUDE rows whose `type` is `e2e` with `covered_by: qe-web-automation` — those
     FTCs are owned by the automation capability and are NOT expected as tests here.
   - `[derived]` rows are matched by scenario as usual (no FTC id to reference).

2. SCAN spec files at {source_path} for corresponding tests:
   - Search test directories (src/test/, __tests__/, *.spec.*, *.test.*)
   - For each PLANNED_TEST_ID, verify a test exists that:
     a) References the test case ID in a comment or test name, OR
     b) Covers the exact scenario described by the test case

3. BUILD compliance report:
   TDAD_COMPLIANCE = {
     planned: count(PLANNED_TEST_IDS),
     found: count(matched tests),
     missing: [list of unmatched test case IDs],
     coverage_pct: found / planned * 100
   }

4. ENFORCE:
   IF missing is NOT empty:
     DO NOT mark phase as complete.
     LOG: "TDAD COMPLIANCE FAILED: {missing_count} test cases from plan not found in spec files."
     FOR EACH missing test case ID:
       CREATE the corresponding test file following the plan's test specification.
     Re-run compliance check after creation.

   IF coverage_pct < 100 after retry:
     Mark in IMPL-STATE deviations:
       | TDAD Gap | {missing IDs} | Tests could not be created | {rationale} |
     Proceed only if deviation is documented.
     ## REC-001: a documented deviation is PASS-with-deviation; an UNdocumented
     ## gap is a FAIL the Completion Gate will block on.
     RECORD validations["tdad_compliance"] = { verdict: (deviation documented ? "PASS" : "FAIL"), evidence: {missing IDs} }
   ELSE:
     RECORD validations["tdad_compliance"] = { verdict: "PASS", evidence: "100% planned tests present" }

RATIONALE: TDAD requires every planned test to exist as a failing test (RED)
before implementation begins (GREEN). Skipping test creation defeats the
purpose of test-driven development and causes code review to flag missing
coverage as BLOCKING.
```

---

## 2. Implementation Completeness Self-Check (after Phase B)

```
AFTER implementing all fix patterns for a phase and BEFORE entering Phase C (Verify):

1. EXTRACT fix patterns from the plan:
   - Parse PLAN-SPEC phases[current].transforms[].fix_pattern (agent-native)
     OR phase doc fix descriptions (legacy)
   - Build: PLANNED_PATTERNS = [{ id, key_identifiers: [class names, method names,
     config keys, import paths], target_file }]

2. SCAN modified files for key identifiers:
   FOR EACH pattern IN PLANNED_PATTERNS:
     FOR EACH identifier IN pattern.key_identifiers:
       SEARCH pattern.target_file for identifier
       IF NOT found:
         MARK pattern as UNVERIFIABLE

3. BUILD completeness report in IMPL-STATE:
   implementation_completeness = {
     total_patterns: count(PLANNED_PATTERNS),
     verified: count(verified patterns),
     unverifiable: [{ pattern_id, missing_identifiers, target_file }],
     completeness_pct: verified / total * 100
   }

4. ENFORCE:
   IF unverifiable is NOT empty:
     LOG: "COMPLETENESS CHECK: {unverifiable_count} patterns could not be verified."
     FOR EACH unverifiable pattern:
       - Re-read the plan's fix description
       - Re-read the target file
       - Determine if the pattern was applied with different identifiers (deviation)
         OR if the pattern was missed entirely
       - If missed: implement it now
       - If applied differently: document as DEVIATION in IMPL-STATE

     Report unverifiable patterns as INCOMPLETE in IMPL-STATE:
       | Pattern | Status | Missing Identifiers | Action Taken |

RATIONALE: Implementation agents frequently claim completion based on file
creation alone, without verifying that the specific fix patterns were applied.
This self-check catches "wrote the file but missed the fix" failures before
they reach code review, reducing repair cycles.
```

---

## 3. Plan File Coverage Gate (before C→D transition)

```
After completing each phase, verify that EVERY file listed in the phase's
files_to_modify / files_to_create has been either:

1. MODIFIED/CREATED with changes documented in IMPL-STATE files_touched
2. DOCUMENTED as a DEVIATION with rationale in IMPL-STATE deviations table

ENFORCEMENT PROTOCOL:

1. EXTRACT planned file list:
   - Agent-native: PLAN-SPEC phases[current].transforms[].target (files_to_modify)
     + phases[current].new_files[] (files_to_create)
   - Legacy: Parse phase document file listing sections

2. CROSS-REFERENCE against IMPL-STATE files_touched:
   FOR EACH planned_file IN planned_files:
     IF planned_file NOT IN files_touched AND planned_file NOT IN deviations:
       MARK as MISSING

3. ENFORCE:
   IF MISSING list is NOT empty:
     LOG: "PLAN FILE COVERAGE FAILED: {count} planned files not addressed."
     FOR EACH missing file:
       - Implement it now (return to Phase B for that file), OR
       - Document as DEVIATION with rationale ("file not needed because...")
     Re-run coverage check after resolution.

   Phase is NOT complete until MISSING list is empty.

4. RECORD in IMPL-STATE:
   plan_file_coverage = {
     planned_files: count,
     touched: count,
     deviated: count,
     missing: count,
     coverage_pct: (touched + deviated) / planned_files * 100
   }
   ## REC-001: record the gate verdict so the Phase C Completion Gate enforces it.
   validations["plan_file_coverage"] = { verdict: (missing == 0 ? "PASS" : "FAIL"), evidence: {missing list} }

Violation = BLOCKING in code review (silently skipped planned work)
```

---

## 4. Pre-Completion Quality Checklist

Before proceeding to Phase D, verify ALL of the following. Failure to check these
is the #1 source of code-review BLOCKING findings.

```
PRE-COMPLETION QUALITY CHECKLIST:

1. READ-BEFORE-WRITE: Every file you modify must be read with the Read tool FIRST.
   Never use Write/Edit on a file path you have not read in the current session.

2. RESILIENCE PATTERNS: For every call to an external service (database, API, etc.):
   - Implement retry (minimum 3 attempts with exponential backoff)
   - Implement alert/notification on permanent failure (after all retries exhausted)
   - Add circuit breaker if the service is flagged as unreliable in context

3. HTTP EXCEPTION MAPPING: After implementation, verify every domain exception
   is mapped to an HTTP status code in the project's exception handler.
   If a new exception class was created and no handler mapping exists, add it.

4. PMD COMPLIANCE: Never use numeric or string literals directly in code.
   Define named constants (private static final) for all magic values.

5. INTEGRATION TESTS: Each acceptance criterion requires at least one integration test.
   Happy path, error/negative path, and boundary conditions must be covered.

6. HTTP STATUS CODES: Use the security library's actual HTTP status codes
   (see build-environment.md in context pack). Do not assume standard HTTP codes —
   verify against context pack documentation.

7. EMIT source_path AT THESE CHECKPOINTS (not just at the end):
   - After first successful compilation pass (gradlew compileJava, mvn compile, npm run build)
   - After test suite passes (gradlew test, mvn test, npm test)
   - FINAL EMIT: before writing any closing summary
   Use the same source_path value each time — repeat emissions are safe.

8. SPRING BOOT TEST CONTEXT RULES (Java/Spring Boot projects):
   When creating a new @Service, @Component, or use case class:
   - Search for @SpringBootTest test classes that might load the full context
   - Check for existing @TestConfiguration class — if found, add new bean definition
   - If @Service annotated: verify component scan covers its package
   - For @WebMvcTest / @DataJpaTest: add @MockBean for the new service
   - Always run ./gradlew test to verify test context before declaring complete

9. PACKAGE.JSON / BUILD MANIFEST VERIFICATION:
   Before completing the implementation step:
   - Verify package.json (or pom.xml, build.gradle, Makefile) exists in {source_path}
   - If package.json absent AND validation-tools.md requires npm scripts:
     Create package.json with: { "scripts": { "build": "exit 0", "test": "exit 0" } }
   - If a test runner is configured in validation-tools.md, implement it
   - Run npm run build && npm test — both MUST exit 0 before completing
   - TOOL-OUTPUT RETENTION (execution-protocol.md §10.5.3): run build/test in full,
     but retain only the verdict on success (exit code + pass/fail counts) and only
     the failing slice on failure. Redirect verbose output to a file
     (e.g. `npm test > .runlogs/test.txt 2>&1`) and `grep`/`tail` on demand; never
     let a full passing log persist in context — across the implementation loop's
     many round-trips, re-sent raw logs are a primary token-cost driver. Record the
     counts in IMPL-STATE `tool_results`, not the raw log.

10. DESIGN IMAGE AUDIT (when design_images_path is set):
    If design_images_path parameter is set and contains image files:
    - Verify at least one image is referenced in front-end HTML (via <img> or CSS background)
    - If not referenced: copy images to source directory and add references
    - Log: "Design image audit: {N} images found, {M} referenced in HTML"
```

---

## Verification Checklist

Every item requires **evidence**, not assertion. "Seems right" is never sufficient.

- [ ] Every file in plan exists at `source_path` — Evidence: `find` output listing all planned files
- [ ] Every planned test file exists and executes — Evidence: test runner output with pass/fail counts
- [ ] Build succeeds — Evidence: build command output (exit code 0)
- [ ] IMPL-STATE `phases[].status` matches actual completion — Evidence: status field matches file count
- [ ] IMPL-STATE final markers are clean — Evidence: no `WFF-SECTION:.*:pending` remains for terminal sections; empty blockers/deviations/execution_log have explicit `none` rows
- [ ] All deviations documented with rationale — Evidence: IMPL-STATE deviations table is complete
- [ ] No unplanned files created — Evidence: diff of plan file list vs actual files
- [ ] TDAD cycle followed (if enabled) — Evidence: execution_log shows RED→GREEN→REFACTOR per file
- [ ] Scaffolding completeness gate passed — Evidence: all imports/references resolve
- [ ] README.md contains build/run/test instructions — Evidence: file exists with required sections
- [ ] Memory Bank updated — Evidence: progress.md contains milestone row
