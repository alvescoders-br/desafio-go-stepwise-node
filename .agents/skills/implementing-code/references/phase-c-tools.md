# Phase C Tools — Self-Verification Before Handoff

## Context Contract
- **Inputs:** IMPL_INDEX (with `project_root`, `build_commands_discovered`, `tech_stack_detected`), context pack `validation-tools.md` (optional)
- **Outputs:** Updated IMPL_INDEX with tool_results, blockers
- **Carries Forward:** IMPL_INDEX
- **Flush After:** Tool stdout/stderr after each execution
- **Dependency:** Phase C Step 2 (Scaffolding Completeness) must be COMPLETE

---

## Purpose

Run deterministic tools **before handoff to code review** so the implementation
agent can self-correct issues that would otherwise trigger a REPAIR cycle.

This step runs a **subset** of tool categories — only those where the agent can
meaningfully fix failures: build, test, lint, and typecheck. Security, coverage,
and complexity are left to the adversarial review phase.

**This reference is loaded by Phase C Step 5 of the implementing-code skill.**

---

## Tool Source

```
INITIALIZE tools = []

IF validation-tools.md exists in context pack directory:
  PARSE the Tool Registry table (see format below)
  FILTER to categories: build, test, lint, typecheck
  NORMALIZE each row into a tool object with:
    - tool_name (from "Tool Name")
    - category (from "Category")
    - command (from "Command")
    - parser (from "Parser")
    - required (from "Required")
    - fail_on (from "Fail On")
    - timeout (from "Timeout")
    - working_dir (from "Working Dir")
  SET tools = list of normalized tool objects
  LOG: "Loaded tools from context pack validation-tools.md (filtered to self-correction categories)"

ELSE:
  // Build + test from IMPL_INDEX.build_commands_discovered
  FOR EACH entry in IMPL_INDEX.build_commands_discovered:
    MAP entry into a normalized tool object with:
      - tool_name: entry.name or synthesized identifier
      - category: "build" or "test" based on entry.type
      - command: entry.command
      - parser: inferred or default parser for the tech stack
      - required: true
      - fail_on: default failure condition for this category
      - timeout: reasonable default per category
      - working_dir: entry.working_dir or IMPL_INDEX.project_root
    APPEND normalized tool object to tools

  // Lint + typecheck from IMPL_INDEX.tech_stack_detected (fallback table)
  AUTO-DETECT lint and typecheck from IMPL_INDEX.tech_stack_detected (see fallback table)
  FOR EACH auto-detected lint/typecheck tool:
    MAP it into the same normalized tool-object shape as above
    APPEND normalized tool object to tools

  LOG: "No validation-tools.md. Using auto-detected build/test + fallback lint/typecheck."

// All subsequent execution steps MUST iterate over the normalized `tools` list:
//   e.g., FOR EACH build_tool IN tools WHERE category == "build"
```

---

## Context Pack: validation-tools.md Format

If present, the file contains a markdown table with tool declarations:

```markdown
# Validation Tools

## Tool Registry

| Tool Name | Category | Command | Parser | Required | Fail On | Timeout | Working Dir |
|-----------|----------|---------|--------|----------|---------|---------|-------------|
| maven-build | build | mvn compile -q | text | true | | 300 | |
| maven-test | test | mvn test | junit | true | | 600 | |
| checkstyle | lint | mvn checkstyle:check | text | false | | 300 | |
```

Phase C only executes rows where Category is `build`, `test`, `lint`, or `typecheck`.
All other categories (security, coverage, complexity, custom) are ignored here —
they run during code review.

---

## Fallback Lint & Typecheck Detection

When no validation-tools.md is present, detect lint and typecheck commands from
the tech stack already discovered in Phase C Step 1:

```
FOR EACH ecosystem in IMPL_INDEX.tech_stack_detected:

  IF "JavaScript/TypeScript" in detected.languages:
    IF package.json scripts.lint exists:
      ADD lint tool: "npm run lint"
    IF tsconfig.json exists:
      ADD typecheck tool: "npx tsc --noEmit"

  IF "Java" in detected.languages:
    IF "Maven" in detected.build_tools:
      ADD lint tool: "mvn checkstyle:check"
      ## typecheck is built into mvn compile — skip
    IF "Gradle" in detected.build_tools:
      ADD lint tool: "gradle check"

  IF "Go" in detected.languages:
    ADD lint tool: "go vet ./..."
    ## typecheck is built into go build — skip

  IF "Python" in detected.languages:
    ADD lint tool: "ruff check ." (fallback: "flake8")
    ADD typecheck tool: "mypy ."

  IF "Rust" in detected.languages:
    ADD lint tool: "cargo clippy -- -D warnings"
    ## typecheck is built into cargo check — skip

  IF "C#" in detected.languages:
    ADD lint tool: "dotnet format --verify-no-changes"
    ## typecheck is built into dotnet build — skip

  IF "Ruby" in detected.languages:
    ADD lint tool: "rubocop"

  IF "PHP" in detected.languages:
    ADD lint tool: "vendor/bin/phpstan analyse"

  IF "Elixir" in detected.languages:
    ADD lint tool: "mix credo"
    ADD typecheck tool: "mix dialyzer"

  IF "Dart" in detected.languages:
    ADD lint tool: "dart analyze"

  IF "Swift" in detected.languages:
    ADD lint tool: "swiftlint"

NOTES:
  - "OR" / "fallback": Try the first command. If exit code indicates not found, try second.
  - "(built into X)": Skip — already covered by build commands.
  - If a lint/typecheck command is not available (exit code 127 or similar),
    log as skipped and continue. Do NOT block on optional tools.
```

---

## Execution Protocol (Self-Correction Loop)

```
IF bash tool is NOT available:
  LOG: "Bash not available. Tool verification skipped."
  SKIP this step entirely
  RETURN

TOOL_RESULTS = []
ATTEMPT_COUNT = 0
MAX_ATTEMPTS = 3

## ──────────────────────────────────────────────────────────
## Completion gates (consumed by Phase C Completion Gate + Phase D)
## ──────────────────────────────────────────────────────────
## These start optimistic and are only downgraded by an UNRESOLVED build/test
## failure (i.e., one that survives the MAX_ATTEMPTS self-correction budget).
## They are the signal that lets the Completion Gate BLOCK `complete`.
BUILD_GATE = "PASS"   ## PASS | FAIL_GENUINE | FAIL_ENVIRONMENTAL
TEST_GATE  = "PASS"   ## PASS | FAIL_GENUINE | FAIL_ENVIRONMENTAL

## ──────────────────────────────────────────────────────────
## Failure classification (loop-safe — classify ONCE, never retry past MAX_ATTEMPTS)
## ──────────────────────────────────────────────────────────
## Called only AFTER the self-correction budget is exhausted. It decides how the
## failure is routed downstream; it NEVER re-runs the command.
##
## ENVIRONMENTAL — the code may be correct; the runner could not execute it.
##   Match any in stderr (case-insensitive): the SANDBOX INDICATORS listed below,
##   plus connectivity/infra signals:
##     "connection refused", "ECONNREFUSED", "ETIMEDOUT", "could not connect",
##     "service unavailable", "host not found", "no such host", "DNS",
##     "address already in use", "container ... not running", "database is starting up".
##   → classify FAIL_ENVIRONMENTAL  (Phase D maps this to BLOCKED → human, NOT REPAIR)
##
## GENUINE — assertion failures, compile errors, logic bugs, missing symbols, etc.
##   Anything that is NOT environmental.
##   → classify FAIL_GENUINE  (Phase D maps this to FAILED → orchestrator REPAIR)

## ──────────────────────────────────────────────────────────
## Sandbox Recovery Protocol (applied to ALL tool executions)
## ──────────────────────────────────────────────────────────
## After EVERY tool execution, before analyzing the result, check if the
## failure was caused by a sandbox blocking writes to user-home directories.
## If so, retry ONCE with a project-local cache path.
##
## SANDBOX INDICATORS (match any in stderr):
##   "sandbox", "permission denied", "read-only file system",
##   "could not resolve", "could not transfer",
##   "~/.m2", "~/.gradle", "~/.cargo", "~/.cache",
##   "blocked", "not permitted"
##
## CACHE FLAGS by package manager:
##   mvn / mvnw       → append: -Dmaven.repo.local=./.m2-cache
##   gradle / gradlew → append: --project-cache-dir ./.gradle-cache
##   cargo            → prepend: CARGO_HOME=./.cargo-cache
##   pip / pip3       → append: --cache-dir ./.pip-cache
##   npm              → insert before subcommand: --cache ./.npm-cache (e.g., `npm --cache ./.npm-cache run <script>`)
##   go               → prepend: GOPATH=./.go-cache
##
## APPLY: After each EXECUTE + CAPTURE block below, if exit_code != 0
## AND stderr matches any sandbox indicator, detect the package manager
## from the command, append/prepend the cache flag, LOG the retry, and
## RE-EXECUTE. Use the retry result for all subsequent evaluation.
## ──────────────────────────────────────────────────────────

## Phase 1: Build commands (from IMPL_INDEX or context pack)
FOR EACH build_tool in tools where category == "build":
  EXECUTE build_tool.command via bash
  CAPTURE: stdout, stderr, exit_code

  IF exit_code == 0:
    LOG: "BUILD PASS: {command}"
    APPEND to TOOL_RESULTS: { tool: build_tool.tool_name, status: "PASS" }
  ELSE:
    LOG: "BUILD FAIL: {command}"
    ANALYZE stderr for fixable patterns:
      - Missing file → Create it
      - Import error → Fix import path
      - Type error → Fix type annotation
      - Version mismatch → Fix version in config
      - Syntax error → Fix syntax

    IF fixable AND ATTEMPT_COUNT < MAX_ATTEMPTS:
      ATTEMPT_COUNT += 1
      APPLY fix → WRITE file → RE-RUN command
      LOG: "Self-correction attempt {N}: {fix_description}"
    ELSE:
      ## Self-correction budget spent. Do NOT loop — classify ONCE and move on.
      CLASSIFY failure (see Failure classification above) → FAILURE_CLASS
      SET BUILD_GATE = FAILURE_CLASS   ## FAIL_GENUINE or FAIL_ENVIRONMENTAL
      LOG: "Build error persists after {N} attempts. Classified {FAILURE_CLASS}. Will BLOCK completion at the gate."
      UPDATE IMPL_INDEX.blockers: { description: error, resolution: ("Manual fix needed" if GENUINE else "Environmental — runner could not build") }
      APPEND to TOOL_RESULTS: { tool: build_tool.tool_name, category: "build", status: "FAIL", failure_class: FAILURE_CLASS, details: stderr }

## Phase 2: Test commands
FOR EACH test_tool in tools where category == "test":
  EXECUTE test_tool.command via bash
  CAPTURE: stdout, stderr, exit_code

  IF exit_code == 0:
    LOG: "TEST PASS: {command}"
    APPEND to TOOL_RESULTS: { tool: test_tool.tool_name, status: "PASS" }
  ELSE:
    LOG: "TEST FAIL: {command}"
    ANALYZE output for fixable test failures:
      - Assertion error with clear expected/actual → Fix source or test
      - Missing test dependency → Add dependency
      - Configuration error → Fix test config

    IF fixable AND ATTEMPT_COUNT < MAX_ATTEMPTS:
      ATTEMPT_COUNT += 1
      APPLY fix → WRITE file → RE-RUN command
      LOG: "Self-correction attempt {N}: {fix_description}"
    ELSE:
      ## Self-correction budget spent. Do NOT loop — classify ONCE and move on.
      ## A recorded test FAIL here BLOCKS `complete` at the Phase C Completion Gate;
      ## it no longer falls through to COMPLETED_WITH_WARNINGS.
      CLASSIFY failure (see Failure classification above) → FAILURE_CLASS
      SET TEST_GATE = FAILURE_CLASS   ## FAIL_GENUINE or FAIL_ENVIRONMENTAL
      LOG: "Test failure persists after {N} attempts. Classified {FAILURE_CLASS}. Will BLOCK completion at the gate."
      UPDATE IMPL_INDEX.blockers: { description: error, resolution: ("Manual fix needed" if GENUINE else "Environmental — runner could not execute tests") }
      APPEND to TOOL_RESULTS: { tool: test_tool.tool_name, category: "test", status: "FAIL", failure_class: FAILURE_CLASS, details: stderr }

## Phase 3: Lint commands (best-effort, no blocking)
FOR EACH lint_tool in tools where category == "lint":
  EXECUTE lint_tool.command via bash
  CAPTURE: stdout, stderr, exit_code

  IF exit_code == 0:
    LOG: "LINT PASS: {command}"
  ELSE IF command not found (exit code 127 or "not found" in stderr):
    LOG: "Lint tool not available: {command}. Skipping."
    APPEND to TOOL_RESULTS: { tool: lint_tool.tool_name, status: "UNAVAILABLE" }
    CONTINUE
  ELSE:
    LOG: "LINT ISSUES: {command}"
    ANALYZE output for auto-fixable issues:
      - Formatting → Apply auto-fix if tool supports --fix flag
      - Unused imports → Remove them
      - Missing semicolons, trailing whitespace → Fix

    IF fixable AND ATTEMPT_COUNT < MAX_ATTEMPTS:
      ATTEMPT_COUNT += 1
      APPLY fix → WRITE file → RE-RUN command
    ELSE:
      LOG: "Lint issues logged. Non-blocking — proceeding."
      APPEND to TOOL_RESULTS: { tool: lint_tool.tool_name, status: "WARN", details: stdout }

## Phase 4: Typecheck commands (best-effort, no blocking)
FOR EACH typecheck_tool in tools where category == "typecheck":
  EXECUTE typecheck_tool.command via bash
  CAPTURE: stdout, stderr, exit_code

  IF exit_code == 0:
    LOG: "TYPECHECK PASS: {command}"
  ELSE IF command not found:
    LOG: "Typecheck tool not available: {command}. Skipping."
    APPEND to TOOL_RESULTS: { tool: typecheck_tool.tool_name, status: "UNAVAILABLE" }
    CONTINUE
  ELSE:
    LOG: "TYPECHECK ISSUES: {command}"
    ANALYZE output for fixable type errors:
      - Missing type annotation → Add it
      - Wrong type → Fix assignment or signature
      - Missing generic parameter → Add it

    IF fixable AND ATTEMPT_COUNT < MAX_ATTEMPTS:
      ATTEMPT_COUNT += 1
      APPLY fix → WRITE file → RE-RUN command
    ELSE:
      LOG: "Type issues logged. Non-blocking — proceeding."
      APPEND to TOOL_RESULTS: { tool: typecheck_tool.tool_name, status: "WARN", details: stdout }

UPDATE IMPL_INDEX.tool_results = TOOL_RESULTS
UPDATE IMPL_INDEX.build_gate = BUILD_GATE
UPDATE IMPL_INDEX.test_gate  = TEST_GATE
UPDATE IMPL_STATE_FILE (tool_results section) with all tool verification results

LOG: "Tool verification complete. Build: {BUILD_GATE}. Test: {TEST_GATE}. Lint: {status}. Typecheck: {status}."

## ⛔ LOOP-SAFETY INVARIANT — read before proceeding ⛔
## Self-correction is OVER. ATTEMPT_COUNT is capped at MAX_ATTEMPTS (3) for the
## whole of this routine and is NOT reset per category. Do NOT re-enter Phase 1/2
## to "try once more" because BUILD_GATE/TEST_GATE is FAIL — the budget is spent.
## The FAIL is now a recorded fact that the Phase C Completion Gate reads and that
## Phase D turns into a terminal status (FAILED → orchestrator REPAIR, or BLOCKED →
## human). Re-running tests here would create the exact infinite loop this design
## forbids. Proceed to documentation generation, then the Completion Gate.
```

---

## POST-VERIFICATION: GENERATE DOCUMENTATION ARTIFACTS

```
Tool verification is complete. You are NOT done with Phase C.

YOUR NEXT ACTIONS (execute in this exact order):

STEP A — Generate README.md:
  VERIFY README.md exists at {IMPL_INDEX.project_root}/README.md
  IF NOT exists:
    Return to phase-c-verify.md and execute Step 4 (Generate README.md) NOW.
  IF exists:
    LOG: "README.md verified. Proceeding."

STEP B — Generate AGENTS.md (final phase only):
  CHECK: Are there remaining PENDING phases in IMPL_INDEX after this one?
  IF NO (this is the final phase):
    VERIFY AGENTS.md exists at {IMPL_INDEX.project_root}/AGENTS.md
    IF NOT exists:
      Return to phase-c-verify.md and execute Step 5 (Generate AGENTS.md) NOW.
    IF exists:
      LOG: "AGENTS.md verified. Proceeding."

STEP C — Phase C Completion Gate:
  Return to phase-c-verify.md and execute the Phase C Completion Gate.
  ALL checks must pass before proceeding to Phase D.

DO NOT emit a final response. DO NOT write a session summary.
BUILD SUCCESS means tool verification passed — the session is NOT over.
Phase D (finalize) is STILL required. Missing it causes downstream pipeline failure
(source_path output parameter will not be set).
```
