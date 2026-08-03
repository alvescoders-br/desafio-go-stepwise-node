# Implementation Consistency Rules

Read this reference at the start of Phase A (after writing `_progress.json`) and keep its rules in scope for the entire session. The 26 rules below govern every file write, every test, every IMPL-STATE update.

---

## The 26 Rules

```
RULE 1: Plan Fidelity
  - Create EXACTLY the files specified in phase document
  - Modify ONLY the files specified in phase document
  - Use EXACTLY the patterns referenced in phase document
  - IF deviation needed → Document in IMPL-STATE deviations, explain why
    Format DEVIATIONS section as:
      | Deviation | Planned Approach | Actual Approach | Technical Rationale |
      Each deviation MUST include: what was planned, what was actually done, and why.
      Deviations without rationale are treated as BLOCKING findings in code-review.

RULE 2: Test-Driven Agentic Development (TDAD)
  - When tdad_mode is enabled: Follow Red-Green-Refactor cycle per file
    (write failing test → implement to pass → refactor while green)
  - When tdad_mode is disabled: Write tests WITH implementation (never after)
  - Default: tdad_mode=true for TASK scope, false for FULL_SDLC scope
  - Test cases MUST cover edge cases from phase document
  - Test cases MUST cover failure modes from research
  - When a plan row's `testing_strategy.test_case_id` cites an upstream FTC id
    (from `quality-engineering-design`) AND `test_cases_path` is provided, the
    RED test's assertions MUST derive from that FTC's Gherkin — not a freely
    invented assertion. Never contradict or weaken an FTC's Then clauses.
  - Honor the plan's `type` (level); this skill does NOT reclassify FTCs. Rows
    marked `type: e2e` / `covered_by: qe-web-automation` are out of scope here
    (the automation capability implements them) — do NOT double-author them.
  - `test_case_id: [derived]` rows (no upstream FTC) behave exactly as before.

RULE 3: Research Respect
  - NEVER contradict BINDING ADR decisions (see ADR Binding Protocol in SKILL.md)
  - Advisory ADR deviations must be documented as accepted derogations in IMPL-STATE
  - NEVER ignore implementation landmines
  - ALWAYS use specified technology versions

RULE 4: Progress Transparency (BLOCKING GATE — also EXIT-BLOCKING)
  At Phase A: write IMPL-STATE skeleton. After completing EACH file in Phase B:
  APPEND one row to files_touched (EOL append mode — see execution-protocol.md).
  BLOCKING: Do NOT generate the next file until the append has been confirmed
  as a tool call. Batching updates = lost progress on interruption.
  EXIT-BLOCKING: Before emitting any final response, verify that
  IMPL-STATE-{session_id}.md exists at {progress_folder_path} AND its last write
  timestamp falls inside the current run window. If not — call
  `stepwise session exec-fail` with reason "IMPL-STATE missing or stale at exit".
  Do NOT emit a success summary with a missing or stale IMPL-STATE.

RULE 5: Context Discipline
  - Load ONLY context needed for current unit of work
  - Shed context between phases
  - Reference documents by path, don't duplicate content

RULE 6: Escape Hatch Compliance
  - IF blocked → Follow escape hatch protocol in phase document
  - Document blocker in IMPL-STATE immediately
  - Do NOT proceed past blocker without resolution

RULE 7: File Comment Convention
  - Use the TARGET FILE'S native comment syntax
  - Dockerfiles: # comment
  - Java: // comment
  - HTML/XML: <!-- comment -->
  - SQL: -- comment
  - NEVER put HTML/XML comments in non-HTML/XML files

RULE 8: Scaffolding Completeness
  - After generating all files for a phase, run the
    Scaffolding Completeness Gate (Phase C) BEFORE marking complete
  - Every import/reference must resolve to an existing file
  - Every build config (docker-compose, pom.xml, package.json,
    tsconfig) must reference only files that exist

RULE 9: AGENTS.md Generation (Final Phase)
  - On the FINAL phase (no PENDING phases remain after current):
    generate AGENTS.md at the project root — MANDATORY
  - This is Phase C Step 4 — do NOT skip it after tests pass
  - The sequence is: Compilation → README.md → AGENTS.md → Finalize
  - AGENTS.md is a deliverable artifact, not optional metadata

RULE 10: Memory Bank — active-context.md (Session Lifecycle)
  At SESSION START: write context-pack/active-context.md (current session,
  scope, prior context). At SESSION END: overwrite with final state.
  See execution-protocol.md.

RULE 11: Memory Bank — progress.md (Cumulative Milestone Ledger)
  After EACH phase completes (NOT just the final phase): append one milestone row
  to context-pack/progress.md (append-only, never overwrite).
  Skipping this on intermediate phases breaks per-phase crash recovery — the next
  session cannot tell what was completed.
  See execution-protocol.md Section 4 for format and Artifact Type Registry.

RULE 12: Source File Placement
  - ALL generated source files MUST be under src/ (or equivalent source directory)
  - NEVER place source artifacts in build output directories (target/, dist/, build/, out/)
  - If a file is expected at a specific path, create it there — do NOT inline its
    content into another file as an undocumented deviation
  - If the plan specifies a resource file (JSON, properties, XML), create it in
    src/main/resources/ (or equivalent), not in build output
  - Violation = BLOCKING in code review

RULE 12b: Source Path Normalization (Portability)
  - Before writing any file, validate that `source_path` is a usable path in the CURRENT environment.
  - If `source_path` appears to be an absolute path from a DIFFERENT machine
    (e.g., starts with `/Users/{other-user}/`, `/home/{other-user}/`, `C:\Users\{other-user}\`):
    1. LOG WARNING: "source_path appears to be a foreign absolute path: {source_path}"
    2. Derive a normalized path: use `./source/{project_name}/` as the fallback write location
    3. Report the path substitution in the IMPL-STATE header: `source_path_normalized: ./source/{project_name}/`
    4. CONTINUE using the normalized path for all file writes — do NOT embed the foreign path as a relative component
  - If `source_path` is a valid relative or local absolute path, use it directly.
  - NEVER write to a path like `source/Users/...` or `source/home/...` — these indicate
    an undetected foreign absolute path. If you encounter such a path, apply normalization.
  - Violation = BLOCKING (broken paths produce unreproducible builds across operators)

RULE 13: Template Fragment Integrity
  - When modifying template fragments (Thymeleaf th:fragment, Jinja blocks,
    Blade sections, JSP includes, etc.):
    1. ALL script/style/link tags required by the fragment MUST be INSIDE the
       fragment boundary (e.g., inside the th:fragment element)
    2. Verify that pages using th:replace/th:include/th:insert receive all
       necessary resources (JS libraries, CSS, i18n scripts)
    3. For shared header/footer fragments, ensure dependencies are included
       within or alongside the fragment — not outside the boundary
    4. After modifying a fragment, check ALL pages that reference it
  - This rule applies to any template engine with include/replace mechanics
  - Violation = BLOCKING in code review (pages silently break)

RULE 14: Context Utilization Monitoring (FIC Protocol)
  Monitor context utilization throughout execution. If context exceeds 60%:
  immediately write current IMPL-STATE, mark incomplete items as
  pending — context compaction triggered, and update _progress.json status.
  See execution-protocol.md for FIC monitoring and Recovery Checkpoint format.

RULE 15: TRANSFORM Dependency Ordering
  - Before applying any TRANSFORM from the PLAN-SPEC, check its `depends_on` field.
  - ALL blocking dependencies MUST be applied and verified FIRST.
  - If a blocking TRANSFORM cannot be applied, HALT and log a DEVIATION record.
    Do NOT skip it and proceed to dependents — this causes cascading failures.
  - After applying each TRANSFORM, verify the target file compiles/builds before
    proceeding to the next dependent TRANSFORM.
  - Violation = BLOCKING in code review (downstream transforms built on wrong base)

RULE 16: No Hardcoded Test Data in Production Code
  - Production source files (src/main/, lib/, app/) MUST NOT contain hardcoded
    test data: email addresses, phone numbers, user IDs, API keys, or PII fixtures.
  - Test data belongs ONLY in test files (src/test/, __tests__/, *.spec.*, *.test.*).
  - When implementing mappers, adapters, or converters: use parameterized injection,
    configuration properties, or environment variables — never inline test values.
  - If PLAN-SPEC, loaded required_artifacts, or fallback research contains
    example values, treat them as documentation — do NOT copy them into
    production code verbatim.
  - Violation = HIGH in code review (data contamination)

RULE 17: No Build/Test/Compile Commands During Implementation (Phase B)
  - During Phase B (code generation), you MUST NOT execute any of these commands:
    make build, make apply, make pitest, ./gradlew build, ./gradlew compileJava,
    ./gradlew test, ./gradlew pitest, npm run build, npm test, mvn compile,
    mvn test, cargo build, cargo test, go build, go test, or ANY compilation,
    build, test, lint, or validation command.
  - Your ONLY responsibility in Phase B is to WRITE CODE FILES and update IMPL-STATE.
  - Build verification is handled exclusively by Phase C (verify step).
  - Running build commands during Phase B wastes the entire token budget and will
    cause a timeout — the build output is discarded when Phase B completes.
  - If skip_runtime_validation is set, Phase C also skips builds — but Phase B
    must NEVER run them regardless of this flag.
  - Violation = BLOCKING (timeout waste, lost output)

RULE 18: Protected Directory Integrity
  - If context-pack/constraints.md lists protected directories (vendored libs,
    SDKs, framework dirs, submodules), snapshot their file lists at Phase A start:
    IMPL_INDEX.protected_baseline = [{ dir, file_count }]
  - Use `find {dir} -type f | wc -l` to capture counts. No git required.
  - During implementation, NEVER create, modify, or delete files inside
    protected directories unless the PLAN-SPEC explicitly authorizes it.
  - At Phase C verification, re-count and compare against the baseline.
    If counts changed: flag as a DEVIATION.
  - If no protected directories are listed in context-pack, skip this rule.
  - Violation = HIGH in code review (protected directory contamination)

RULE 19: Emergent File Tracking in IMPL-STATE (EXIT-BLOCKING)
  - EVERY file or directory created, modified, or deleted during implementation
    MUST be added to IMPL-STATE files_touched, REGARDLESS of whether it was in
    the original plan.
  - This includes:
    - Patch directories created as workarounds (e.g., compat shims, polyfills)
    - Temporary or compatibility files needed for build fixes
    - Cleanup operations (mark as action: DELETE in files_touched)
    - Files discovered during REPAIR sub-operations
    - Files restored or replayed during integrity-break recovery
      (see references/recovery-protocol.md)
  - After each REPAIR sub-operation, IMMEDIATELY add entries to files_touched
    before proceeding to the next sub-operation.
  - EXIT-BLOCKING: Before emitting any final response, run
    `git -C {source_path} diff --name-only HEAD~N..HEAD` (where N is the number
    of phases just executed) and verify every file in that list has a
    corresponding row in IMPL-STATE files_touched. If any file is missing — add
    it before exit. Skipping this check leaves files reviewers cannot trace.
  - Code review will flag any file on disk that is NOT in IMPL-STATE files_touched
    as a HIGH finding (undocumented file creation).

RULE 20: Specification Traceability for Implementation Decisions
  - Before implementing ANY value that governs application behavior — constants,
    thresholds, activation conditions, rates, probabilities, feature gates,
    asset requirements, or domain-specific parameters — trace it back to the
    source specification (user stories, NFRs, PRD, acceptance criteria).
  - Do NOT infer, assume, or use "sensible defaults" when the specification
    defines an explicit value or condition. The spec is the single source of truth.
  - Before starting each phase, extract a checklist of spec-defined values that
    the phase will implement. After coding, verify each value matches the spec.
  - This applies to ALL value types, not just numeric:
    - Numeric: speeds, sizes, distances, durations, limits, percentages
    - Conditional: feature activation rules ("active at 100m+"), tier gates,
      unlock criteria, eligibility conditions
    - Behavioral: input models, interaction patterns, state transitions
    - Asset: required fidelity (functional vs placeholder), format, content
  - If the spec is silent on a value, document the assumed default as a
    DEVIATION in IMPL-STATE with rationale, so code-review can verify intent.
  - Violation = HIGH in code review (undocumented spec deviation)

RULE 21: Stepwise Output File Early Write (Anti-Compaction-Loss)
  Write _progress.json with output_contract (see execution-protocol.md for schema).
  After compaction: READ IMPL-STATE header to recover output path — do NOT explore filesystem.

RULE 22: Build Script Reference Completeness
  - After generating any build script (build.gradle.kts, pom.xml, build.xml, Makefile,
    package.json scripts, Cargo.toml, etc.):
    1. Scan the generated content for ALL file path references:
       suppressionFile, keystore, truststore, include paths, config files, resource paths, etc.
    2. For each referenced file path, verify it either:
       (a) Already exists in the project, OR
       (b) Is created in the current or a subsequent phase of this plan.
    3. If neither condition is met, create the file (even an empty placeholder)
       in the current phase. Log as an emergent file in IMPL-STATE.
  - This applies to ALL build tools and package managers, not just Gradle or Maven.
  - Violation = BLOCKING (build fails with FileNotFoundException or missing resource error)

RULE 23: Acceptance Criteria Test Coverage
  - After generating each test file, locate the corresponding acceptance criteria (AC)
    in the plan spec. For each AC:
    1. Verify at least one test method (e.g., @Test, it(), test_*, def test_) exists
       that exercises the specified scenario.
    2. Verify the test includes assertions matching the expected outcome.
    3. For edge cases (disabled features, error scenarios, boundary values), verify
       negative or boundary test cases are explicitly covered.
    4. Flag any AC with no corresponding test assertion as an implementation gap
       before completing the phase.
  - Do NOT mark a phase COMPLETED if any AC has zero test coverage.
  - Violation = HIGH in code review (untested acceptance criterion)

RULE 24: Generated Project Bootstrap Completeness
  - After generating any project that includes a build tool wrapper or bootstrap binary
    (e.g., Gradle wrapper JAR, Maven wrapper JAR, any vendored bootstrap binary):
    1. Verify all required bootstrap binaries are present in the generated output.
       Example: gradle/wrapper/gradle-wrapper.jar is required for ./gradlew to function.
    2. If the agent cannot generate binary files directly, add a MANDATORY bootstrap
       section to the generated README.md explaining how to obtain or regenerate them.
       Example for Gradle:
         ## Prerequisites — Build Tool Bootstrap
         If gradle/wrapper/gradle-wrapper.jar is missing, run once:
           gradle wrapper --gradle-version {version}
    3. Note missing bootstrap assets in IMPL-STATE as emergent setup requirements.
  - Applies to any build tool that uses a self-contained wrapper or bootstrap binary.
  - Violation = BLOCKING (build tool wrapper non-functional without bootstrap binary)

RULE 25: Post-Phase Build Validation (run project test suite before marking DONE)
  - After completing all implementation phases and before marking implementation DONE,
    run the project's full test command (determine from tech stack or
    context-pack/validation-tools.md — e.g., ./gradlew test, mvn test, npm test,
    pytest, cargo test, go test):
    1. A PASSING full test run is the minimum bar for marking implementation complete.
    2. If skip_runtime_validation: 'true' is set in config, this check CANNOT
       be skipped — it is mandatory regardless of that flag.
    3. If the test run fails, diagnose and fix before completing the implementation.
  - This rule is in addition to Phase C build verification (compilation check) — not a
    replacement. Phase C catches compilation errors; this catches runtime startup errors
    and integration failures that only surface during a full test run.
  - Violation = BLOCKING (implementation marked complete with failing test suite)

RULE 26: Deviation Taxonomy (Auto-Fix vs Escalate vs Defer)
  - Before deviating from plan, classify per execution-protocol.md Section 8.
  - D-AUTO (1-3): Fix inline, document in deviations table, max 3 per file.
  - D-ESC (1-3): STOP. Write blocker to IMPL-STATE. Do NOT proceed without guidance.
  - D-DEF (1-3): Note in deviations as DEFERRED. Continue current work.
  - Violation = HIGH in code review (unclassified deviation)
  Deviation types apply to ALL file types — not just source code:
  - D-MARKUP-NNN: HTML/XML structure differs from plan (element hierarchy, attributes, load order)
  - D-STYLE-NNN: CSS/styling approach differs from plan (layout strategy, positioning, responsive breakpoints)
  - D-CONFIG-NNN: Configuration files differ from plan (build config, environment config, manifest)
  Non-code deviations can cause runtime bugs invisible to logic-only code review.
  Same classification rules (D-AUTO / D-ESC / D-DEF) apply.

RULE 27: IMPL-STATE Write Budget (compliance pointer)
  - Comply with context-pack/execution-protocol.md §3.1 (write-budget formula,
    APPEND-ONLY discipline, heartbeat-ratio self-check).
  - Coexists with RULE 4: RULE 4 already mandates one append per completed file
    in Phase B. RULE 27 closes the loophole where the agent rewrites the full
    IMPL-STATE between sub-phases instead of appending — forbidden by §3.1.
  - Violation = HIGH in code review (heartbeat churn / iteration-budget waste).

RULE 28: Parseable-Snapshot Invariant (no half-written files)
  Before opening a NEW target file for editing, every previously-edited file in
  this run MUST be in a syntactically parseable state on disk.

  PRECONDITION CHECKS — run before issuing the write for the next file:
    - size_bytes >= max(200, 5 % of pre-edit size)
    - line_count >= 5
    - file does not start AND end with the same opening token (e.g., file is
      not just `{` or just `public class X {` with nothing else)
    - Per-ecosystem fast parse:
        * Java/Kotlin: last non-blank line is `}` or closes a top-level decl
        * JS/TS:       last non-blank line is `}` or matches `^export ` line
        * Go:          file begins with `package ` declaration
        * Python:      file is importable: `python -c "import <module>"` exit 0
        * Rust:        `cargo check --offline` exit 0 (if cheap)
        * Generic:     if no per-ecosystem rule applies, require non-empty +
                       size precondition only
    - The available `build` validation tool's compile target for the owning
      module returns exit 0 (if compile is in tool registry and cheap enough)

  IF any precondition fails:
    - DO NOT proceed to the next file
    - ATTEMPT to restore the file from its pre-edit content (git stash / git
      restore <path> / fs.copyFile from backup). The skill MUST take one
      backup per file on first open in Phase B.
    - LOG D-ESC-NN escalation: "Parseable-snapshot precondition failed; file
      restored from backup; sub-phase deferred."
    - WRITE final IMPL-STATE with restored snapshot info and EXIT cleanly.

  Violation = BLOCKING in code review (destructive edit / unparseable file
              left on disk).
  Rationale: when the agent iteration cap is hit mid-edit, the partial write
             must NOT be the version that lands on disk. A parseable snapshot
             ensures the user can resume with a known-good baseline.
```

---

## Test Suite Integrity (MANDATORY — all test files)

```
NEVER use xdescribe, xit, fdescribe, or fit in test files.
All test suites and test cases MUST use describe/it (or their framework equivalents).

- Disabling tests (xdescribe, xit, skip, pending) is a PROTOCOL VIOLATION.
- Focusing tests (fdescribe, fit, only) is a PROTOCOL VIOLATION.
- If a test is too complex to implement, escalate as a BLOCKER in IMPL-STATE
  rather than disabling it.
- During Phase C verification, scan all test files for these patterns:
  grep -rE '\b(xdescribe|xit|fdescribe|fit)\b' {source_path} --include="*.spec.*" --include="*.test.*"
  If any match is found: HALT and fix before proceeding.

Violation = BLOCKING in code review (silent test suppression)
```

---

## Test Impact Checklist (after modifying any service/pipe/component)

```
AFTER modifying any service, pipe, component, or directive:

1. SEARCH for ALL spec files importing the modified class:
   - Run: grep -r "import.*{ClassName}" {source_path} --include="*.spec.ts" --include="*.spec.js" --include="*Test.java" --include="*Test.kt"
   - Record each spec file found

2. CHECK TestBed providers in each discovered spec file:
   - Verify the provider/mock for the modified class matches its current constructor signature
   - If constructor parameters changed → update TestBed.configureTestingModule providers

3. CHECK spy factories:
   - If the modified class has new/renamed/removed methods → update corresponding jasmine.createSpyObj or jest.fn() mocks
   - Verify spy return types match updated method signatures

4. CHECK template references (Angular/React/Vue components):
   - If component selector, inputs, or outputs changed → search all template files referencing it
   - Update template bindings to match new interface

5. RECORD all test modifications in IMPL-STATE:
   test_impact_updates: [{ modified_class, spec_files_updated: [], changes: [] }]

IF any spec file imports the modified class but was NOT updated:
  FLAG as INCOMPLETE — do not proceed to next file until resolved.
```

---

## Prove-It Pattern — Bug Fix Protocol

When fixing a defect (bug ticket, regression, or discovered issue during implementation):

```
STEP 1: Write a test that reproduces the bug
  - Test MUST fail before the fix (RED state)
  - Test name describes the defect: test_[component]_[defect_description]
  - If the test passes before fix → your test doesn't capture the bug. Rewrite.

STEP 2: Confirm the test fails
  - Run the test. Verify it fails for the EXPECTED reason.
  - If it fails for a different reason → fix the test first.

STEP 3: Implement the minimal fix
  - Change only what is necessary to make the failing test pass.
  - Do not refactor, do not "improve nearby code."

STEP 4: Verify the test passes (GREEN state)
  - Run the specific test. It must pass.
  - Run the full test suite. No regressions.

STEP 5: Document
  - Log in IMPL-STATE: defect ID, test file, fix file, before/after behavior.
```

VIOLATION: Fixing a bug without a reproducing test means the fix is unverifiable. If the bug recurs, there is no automated guard. This is a BLOCKING practice when `tdad_mode` is enabled.

---

## Common Rationalizations (and counters)

| Excuse | Why It Fails | Counter |
|--------|-------------|---------|
| "The plan is close enough, I'll adapt as I go" | Undocumented deviations become BLOCKING findings in review. The plan is the contract. | Follow the plan exactly. If deviation needed, document in IMPL-STATE deviations table with rationale BEFORE implementing. |
| "Tests slow me down, I'll add them after" | Code without tests is unverifiable. Post-hoc tests validate assumptions, not behavior. | TDAD is non-negotiable when enabled. Even with TDAD off, tests are written WITH implementation, never after. |
| "This file isn't in the plan but it's obviously needed" | Creating unplanned files violates Plan Fidelity (Rule 1). Review will flag as undocumented deviation. | Log a deviation with rationale. If the file is truly needed, the deviation record protects you. |
| "The build passes, so the phase is complete" | A passing build proves compilation, not correctness. Scaffolding gates, test coverage, and plan adherence are separate checks. | Complete ALL Phase C verification steps: scaffolding gate, plan adherence, tool verification, README generation. |
| "I'll fix that edge case in the next phase" | Edge cases deferred without tracking become silent defects. Downstream phases don't re-verify prior work. | Either implement the edge case now (if in plan) or log it in open_questions with explicit tracking. |
| "The refactor improved the code even though it wasn't planned" | Unplanned refactoring violates scope discipline. Review will challenge undocumented changes. | Resist the urge. Log the improvement opportunity in open_questions for future work. |

---

## Red Flags

Signs that this skill is being misapplied or circumvented:
- Code files exist without corresponding test files
- IMPL-STATE deviations table is empty despite actual deviations from plan
- Phase marked COMPLETE but tool_results section shows failures or is empty
- Files created that don't appear in the plan document
- Build passes but no tests were executed
- Multiple phases completed in a single pass without per-phase verification
- TDAD mode enabled but no Red-Green-Refactor cycle evidence in execution_log
- README.md or AGENTS.md missing at end of final phase
- Test files contain xdescribe, xit, fdescribe, or fit (disabled/focused tests)
