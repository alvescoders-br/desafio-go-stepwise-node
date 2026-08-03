# Tool Execution Protocol — Adversarial Verification

## Context Contract
- **Inputs:** `source_path`, `validation_tools` parameter (optional), context pack `validation-tools.md` (optional)
- **Outputs:** TOOL_RESULTS array, issues appended to FINDING_LOG
- **Carries Forward:** Merged tool registry for reporting in Step 10
- **Flush After:** Individual tool stdout/stderr after parsing

---

## Purpose

This reference defines the deterministic (non-AI) quality checks that run during
adversarial code review. Unlike implementing-code (which runs build + test + lint
for self-correction), the review phase runs **all available tool categories** and
treats failures as review findings — it does NOT self-correct.

**This reference is loaded by Step 5 of the reviewing-code skill.**

---

## Tool Sources (Priority Order)

Tools are loaded from three sources. Higher priority wins for matching tool names:

```
1. FALLBACK DEFAULTS (see below) — baseline for detected ecosystems when no
   context pack is present
2. Context pack validation-tools.md — project-specific tool declarations
3. validation_tools parameter — session-level overrides from capability YAML

MERGE RULES:
  - Higher-priority source replaces the entire tool entry (no partial field merge)
  - To DISABLE a default tool: override with { "enabled": false }
  - To ADD a custom tool: define it in source 2 or 3 with a unique tool_name
  - Unknown categories are allowed (treated as optional)
```

---

## Context Pack: validation-tools.md

IF `validation-tools.md` exists in the context pack directory, it is the **primary
source of truth** for which tools to run and how.

### Expected Format

```markdown
# Validation Tools

## Tool Registry

| Tool Name | Category | Command | Parser | Required | Fail On | Timeout | Working Dir |
|-----------|----------|---------|--------|----------|---------|---------|-------------|
| maven-build | build | mvn compile -q | text | true | | 300 | |
| maven-test | test | mvn test | junit | true | | 600 | |
| checkstyle | lint | mvn checkstyle:check | text | false | | 300 | |
| sonar | lint | sonar-scanner -Dsonar.projectKey={project_name} | json | false | critical,blocker | 600 | |
| snyk | security | snyk test --json | json | false | critical,high | 300 | |
| license-check | security | license-checker --failOn UNLICENSED | text | true | UNLICENSED | 120 | |

## Notes
<!-- Optional: any project-specific notes about tool configuration, prerequisites, etc. -->
```

### Parsing Rules

```
IF context pack contains validation-tools.md:
  PARSE the Tool Registry table
  FOR EACH row:
    CREATE tool entry:
      {
        tool_name: row["Tool Name"],
        category: row["Category"],
        enabled: true,
        command: row["Command"],
        parser: row["Parser"] OR "text",
        required: row["Required"] == "true",
        fail_on: split(row["Fail On"], ",") OR [],
        timeout: int(row["Timeout"]) OR 300,
        working_dir: row["Working Dir"] OR source_path
      }
  LOG: "Loaded {count} tools from context pack validation-tools.md"
  ## Fallback defaults are NOT used when validation-tools.md is present,
  ## UNLESS the context pack explicitly includes them.

IF validation-tools.md does NOT exist:
  LOG: "No validation-tools.md in context pack. Using fallback auto-detection."
  USE fallback defaults (see below)
```

---

## Fallback Defaults (When No validation-tools.md Present)

Auto-detection scans `source_path` for known config files and selects commands
per category. When multiple ecosystems coexist (e.g., Java backend + JS frontend),
ALL detected ecosystems are registered.

```
DETECT project ecosystems by scanning source_path for config files:

┌─────────────────────────────┬────────────┬──────────────────────────────────┬─────────────────────────────┬───────────────────────────────────┬────────────────────────────────┬──────────────────────────────────┐
│ Detected File               │ Language   │ build                            │ test                        │ lint                              │ typecheck                      │ security                         │
├─────────────────────────────┼────────────┼──────────────────────────────────┼─────────────────────────────┼───────────────────────────────────┼────────────────────────────────┼──────────────────────────────────┤
│ package.json                │ JS / TS    │ npm run build                    │ npm test                    │ npm run lint                      │ npx tsc --noEmit               │ npm audit --audit-level=high     │
│ pom.xml                     │ Java       │ mvn compile -q                   │ mvn test                    │ mvn checkstyle:check              │ (built into compile)           │ mvn dependency-check:check       │
│ build.gradle / .gradle.kts  │ Java/Kotlin│ gradle build -x test             │ gradle test                 │ gradle check                     │ (built into compile)           │ gradle dependencyCheckAnalyze    │
│ go.mod                      │ Go         │ go build ./...                   │ go test ./...               │ go vet ./...                      │ (built into compile)           │ govulncheck ./...                │
│ pyproject.toml              │ Python     │ python -m py_compile {main}      │ pytest                      │ ruff check . OR flake8            │ mypy .                         │ pip-audit                        │
│ requirements.txt            │ Python     │ python -m py_compile {main}      │ pytest                      │ ruff check . OR flake8            │ mypy .                         │ pip-audit                        │
│ Cargo.toml                  │ Rust       │ cargo check                      │ cargo test                  │ cargo clippy -- -D warnings       │ (built into check)             │ cargo audit                      │
│ *.csproj / *.sln            │ C# / .NET  │ dotnet build                     │ dotnet test                 │ dotnet format --verify-no-changes │ (built into build)             │ dotnet list package --vulnerable │
│ Gemfile                     │ Ruby       │ —                                │ bundle exec rspec           │ rubocop                           │ sorbet tc (if present)         │ bundle audit                     │
│ composer.json               │ PHP        │ —                                │ vendor/bin/phpunit          │ vendor/bin/phpstan analyse        │ (phpstan covers types)         │ composer audit                   │
│ mix.exs                     │ Elixir     │ mix compile --warnings-as-errors │ mix test                    │ mix credo                         │ mix dialyzer                   │ mix deps.audit                   │
│ pubspec.yaml                │ Dart/Flutter│ dart compile exe {main}         │ dart test                   │ dart analyze                      │ (built into analyze)           │ —                                │
│ Package.swift               │ Swift      │ swift build                      │ swift test                  │ swiftlint                         │ (built into build)             │ —                                │
│ Makefile (only)             │ Unknown    │ make                             │ make test                   │ —                                 │ —                              │ —                                │
└─────────────────────────────┴────────────┴──────────────────────────────────┴─────────────────────────────┴───────────────────────────────────┴────────────────────────────────┴──────────────────────────────────┘

FALLBACK NOTES:
  - "OR" entries: Try the first command. If unavailable, fall back to the second.
  - "(built into X)": Language compiler already performs type checking. Skip category.
  - "—": No standard tool exists for this category. Skip.
  - For Python, prefer ruff (faster, unified) over flake8.
  - For JS/TS, if package.json scripts.lint does not exist, skip lint.
  - For JS/TS, if tsconfig.json does not exist, skip typecheck.
  - ALL fallback tools are created with required: false EXCEPT build and test.
  - Security tools are always optional — they may not be installed.
```

---

## Pre-finding Integrity Sweep (MANDATORY)

This sweep runs BEFORE the standard tool execution. It catches destructive edits
(truncated files, empty files, deletions) that symbol-level checks can miss.

For every file listed in PLAN-SPEC `files_to_create` or `files_to_modify`:

1. Run a size check:
   - POSIX-equivalent: `wc -l <path>` and `wc -c <path>`
   - File-type sanity: `file -b <path>` (any "empty" verdict is BLOCKING)
2. If the file existed before this run, compute post/pre size ratio.
   IF post_size < max(5 % of pre_size, 10 lines, 200 bytes):
     ADD to FINDING_LOG: {
       type: "FAIL",
       severity: "BLOCKING",
       category: "FILE_TRUNCATED_OR_EMPTY",
       location: "{path}",
       description: "Post-edit size collapsed vs pre-edit size — likely destructive edit."
     }
3. Identify the build module / package that owns the file:
   - Java/Kotlin (Gradle / Maven): nearest ancestor with build.gradle(.kts) or pom.xml
   - JS/TS: nearest ancestor with package.json
   - Go: nearest ancestor with go.mod
   - Python: nearest ancestor with pyproject.toml or setup.cfg
   - Rust: nearest ancestor with Cargo.toml
   - .NET: nearest ancestor with *.csproj or *.sln
   - PHP: nearest ancestor with composer.json
   - Other ecosystems from the Fallback Defaults table use the same nearest-config-file rule.
4. Add every distinct owning module to the `build` tool's compile_targets so the
   subsequent build step covers each one. A file whose owning module never gets
   compiled is treated as if the module's build tool returned status FAIL.

This sweep ALWAYS runs, even when validation-tools.md is present.

---

## Tool Categories for Review

The review phase runs **all available categories**. Unlike implementation
self-verification (which focuses on build + test + lint + typecheck), the review
adds security, coverage, and complexity as adversarial checks.

| Category | Purpose | Blocking by default? |
|---|---|---|
| `build` | Compilation / transpilation | Yes |
| `test` | Unit and integration tests | Yes |
| `lint` | Code style and static analysis | No |
| `typecheck` | Static type validation | No |
| `security` | Dependency vulnerability scanning | No |
| `format` | Code formatting consistency | No |
| `coverage` | Code coverage measurement | No |
| `complexity` | Cyclomatic complexity analysis | No |

---

## Tool Schema

```
{
  "tool_name": {
    "category": "build | test | lint | typecheck | security | format | coverage | complexity | custom",
    "enabled": boolean,
    "command": "executable command string",
    "working_dir": "optional, defaults to source_path",
    "parser": "json | text | junit | custom",
    "timeout": seconds (default: 300),
    "fail_on": ["conditions that make this blocking"],
    "threshold": { "metric": value },
    "required": boolean (if true, unavailable = BLOCKING)
  }
}
```

---

## Execution Protocol

```
FOR each tool in merged_tools where enabled == true:

  LOG: "Executing: {tool.tool_name} ({tool.category})"

  ## Substitute placeholders in command string
  REPLACE {project_name} with project_name parameter
  REPLACE {source_path} with source_path parameter
  REPLACE {main} with detected entry point (if applicable)

  TRY:
    START_TIME = now()

    EXECUTE command:
      working_dir = tool.working_dir OR source_path
      timeout = tool.timeout OR 300
      capture stdout, stderr, exit_code

    ## Sandbox Recovery — retry with project-local cache if sandbox blocks writes
    IF exit_code != 0 AND stderr matches sandbox indicators:
      ## Indicators: "sandbox", "permission denied", "read-only file system",
      ##   "could not resolve", "could not transfer",
      ##   "~/.m2", "~/.gradle", "~/.cargo", "~/.cache",
      ##   "blocked", "not permitted"
      DETECT package manager from command and apply cache flag or env var correctly:
        mvn / mvnw       → -Dmaven.repo.local=./.m2-cache
        gradle / gradlew → --project-cache-dir ./.gradle-cache
        cargo            → CARGO_HOME=./.cargo-cache (prepend as env var)
        pip / pip3       → --cache-dir ./.pip-cache
        npm              → insert flag "--cache ./.npm-cache" immediately after the npm executable in the command (before any subcommand such as "run")
        go               → GOPATH=./.go-cache (prepend as env var)
      LOG: "Sandbox detected. Retrying with project-local cache: {flag}"
      RE-EXECUTE command with cache flag
      CAPTURE: stdout, stderr, exit_code
      ## Continue evaluation with retry result

    EXECUTION_TIME = now() - START_TIME

    PARSE output:
      IF tool.parser == "json":
        PARSE stdout as JSON
      ELSE IF tool.parser == "junit":
        PARSE as JUnit XML
      ELSE IF tool.parser == "text":
        EXTRACT key metrics from text output
      ELSE:
        USE raw output

    EVALUATE results:
      IF exit_code != 0:
        status = "FAIL"
      ELSE IF tool.threshold:
        FOR each metric, threshold in tool.threshold:
          IF parsed_output[metric] violates threshold:
            status = "FAIL"
            violation = { metric, expected: threshold, actual: parsed_output[metric] }
      ELSE IF tool.fail_on:
        FOR each condition in tool.fail_on:
          IF condition present in output:
            status = "FAIL"
      ELSE:
        status = "PASS"

    CREATE tool_result:
      {
        tool: tool.tool_name,
        category: tool.category,
        status: status,
        execution_time: EXECUTION_TIME,
        command: command_used,
        exit_code: exit_code,
        summary: extract_summary(parsed_output),
        details: parsed_output,
        issues: extract_issues(parsed_output, tool.parser)
      }

    APPEND to TOOL_RESULTS

    IF status == "FAIL":
      severity = tool.required ? "BLOCKING" : "HIGH"

      FOR each issue in tool_result.issues:
        ADD to FINDING_LOG: {
          type: "FAIL",
          severity: severity,
          category: "TOOL_{tool.tool_name.upper()}",
          description: issue.description,
          location: issue.location,
          tool: tool.tool_name
        }

  CATCH timeout_error:
    LOG: "Tool {tool.tool_name} timed out after {timeout}s"
    APPEND to TOOL_RESULTS: {
      tool: tool.tool_name,
      status: "TIMEOUT",
      summary: "Execution exceeded {timeout}s limit"
    }
    ADD to FINDING_LOG: {
      type: "WARNING",
      category: "TOOL_TIMEOUT",
      tool: tool.tool_name
    }

  CATCH unavailable_error:
    LOG: "Tool {tool.tool_name} unavailable: {error}"
    APPEND to TOOL_RESULTS: {
      tool: tool.tool_name,
      status: "UNAVAILABLE",
      summary: error.message
    }

    IF tool.required:
      ADD to FINDING_LOG: {
        type: "FAIL",
        severity: "BLOCKING",
        category: "REQUIRED_TOOL_UNAVAILABLE",
        tool: tool.tool_name,
        description: "Required validation tool could not be executed"
      }
    ELSE:
      ADD to FINDING_LOG: {
        type: "WARNING",
        category: "TOOL_UNAVAILABLE",
        tool: tool.tool_name,
        description: "Optional tool unavailable — check skipped"
      }

LOG: "Tool execution complete. Run: {count}. Passed: {pass}. Failed: {fail}. Unavailable: {unavail}."
```
