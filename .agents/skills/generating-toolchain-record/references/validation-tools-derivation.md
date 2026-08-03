# validation-tools.md Derivation from DTR

When `derive_validation_tools` is `true`, this skill emits a runtime command registry at `validation_tools_output_path`. The DTR is the source of identity + version + state; project inspection (build files) and stack defaults are the source of CLI commands.

This reference is loaded in **Step 5 (Derivation)** after the DTR is validated and written.

---

## Source-of-Truth Contract

| Field | Source |
|---|---|
| `Tool Name` | DTR row name |
| `Category` | DTR field → category mapping (table below) |
| `Command` | Project inspection (pom.xml, package.json, build.gradle, Makefile, …) → fallback to stack defaults from `references/stacks/<stack>.md` |
| `Parser` | Stack defaults table below |
| `Required` | DTR field flag (`†` optional → `false`; otherwise `true`) |
| `Fail On` | Default per category (table below) |
| `Timeout` | Default per category (table below) |
| `Working Dir` | Project root or sub-module path from inspection |

If a DTR row is in state `legacy` or `migrating`, **omit the row** from `validation-tools.md` (legacy code is not the verification target). State `planned` rows are also omitted — they are not yet executable. Only `stable` and `upgrading` (current version side) rows are emitted.

---

## DTR Field → Category Mapping

| DTR field | validation-tools.md category |
|---|---|
| Language | (skip — informational only) |
| Framework | (skip — used implicitly by build/test rows) |
| IDE | (skip) |
| Dependency Management | `build` (e.g., `mvn compile`, `npm install`) |
| Unit Testing | `test` |
| Linting & Formatting / Lint | `lint` |
| Static and Dynamic Code Quality Inspection | `security` (when SonarQube/Checkmarx/etc.) or `lint` |
| CI/CD Quality | `coverage` (e.g., JaCoCo, Coverlet) |
| Performance Testing | (skip — not in self-correction scope) |
| Type Checking *(implicit)* | `typecheck` (TS, Mypy, Pyright) |

Categories outside the above set are not emitted. The `validation-tools.md` consumer (`implementing-code` Phase C) only operates on `build / test / lint / typecheck / security / coverage / complexity`.

---

## Default Parser / Fail On / Timeout

| Category | Parser | Fail On | Timeout (s) |
|---|---|---|---|
| build | text | non-zero exit | 300 |
| test | junit (Java/Kotlin), jest (JS/TS), pytest (Python), gotest (Go) | non-zero exit OR test failures > 0 | 600 |
| lint | text | non-zero exit | 300 |
| typecheck | text | non-zero exit | 300 |
| security | text | high+critical findings > 0 | 600 |
| coverage | text | line_coverage < 70% | 300 |

If the project's CI config declares stricter thresholds, prefer those over the defaults — log the override in DTR-AUDIT.

---

## Command Discovery Order

For each emitted row, resolve `Command` in this order:

1. **Project build file inspection** at `source_path` (when present):
   - `pom.xml` → `<plugins>` and `<phase>` mappings → `mvn <goal>`
   - `package.json` → `scripts` block → `npm run <script>` (or `pnpm`/`yarn` if lockfile indicates)
   - `build.gradle` / `build.gradle.kts` → `./gradlew <task>`
   - `pyproject.toml` / `setup.cfg` → resolved from `[tool.pytest.ini_options]`, `[tool.ruff]`, etc.
   - `go.mod` → `go test ./...`, `go vet ./...`, `golangci-lint run`
2. **Stack reference defaults** at `references/stacks/<stack>.md` — every stack file lists canonical CLI patterns.
3. **TBD** — when neither inspection nor stack defaults yield a command, write `TBD` in the Command column and add an entry to DTR Toolchain Notes > Gaps.

---

## Output Format

Write `validation-tools.md` using this exact header so the existing `phase-c-tools.md` parser in `implementing-code` accepts it:

```markdown
# Validation Tools

> Derived from DTR-{SESSION_ID}.md. Do not edit by hand — re-run `generating-toolchain-record` to regenerate. CLI commands are filled from project inspection at `{source_path}` (when available) or stack defaults.

## Tool Registry

| Tool Name | Category | Command | Parser | Required | Fail On | Timeout | Working Dir |
|-----------|----------|---------|--------|----------|---------|---------|-------------|
| {row from DTR Backend.Dependency Management} | build | {discovered} | text | true | | 300 | |
| {row from DTR Backend.Unit Testing}          | test  | {discovered} | {parser} | true | | 600 | |
| {row from DTR Frontend.Linting & Formatting} | lint  | {discovered} | text | false | | 300 | |
…
```

After writing, verify the file is readable by re-parsing the table and counting rows — log to DTR-AUDIT.

---

## Drift Detection

On brownfield REPAIR runs, before regenerating:

1. Read existing `validation-tools.md` (if present at `validation_tools_output_path`).
2. Diff its rows against the new DTR.
3. Log adds/removes/modifies into DTR-AUDIT under `validation_tools_drift`.
4. NEVER preserve a row whose tool is now `legacy` or `migrating` in DTR — delete it; log to drift.

Conflicts where DTR says `Tool A` but `validation-tools.md` ran `Tool B` successfully → trust `validation-tools.md` for execution but flag as DTR_GAP in DTR-AUDIT (DTR likely missed an undocumented dependency).
