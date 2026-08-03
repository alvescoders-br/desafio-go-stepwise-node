# launching-app — Phase A: Launch Command Detection

## Context Contract

- **Inputs:** `LAUNCH_INDEX.source_path`, parameter `launch_command_override` (optional)
- **Outputs:** `LAUNCH_INDEX.launch` (command, cwd, package_manager, framework, detected_from, override_applied)
- **Carries Forward:** `launch.command` (consumed by Phase B spawn), `launch.cwd`
- **Flush After:** Raw manifest file contents — keep only structured `launch` fields
- **Dependency:** Step 1 (Initialize) must be COMPLETE
- **H1 Title:** `# Phase A — Launch Command Detection`

## Mode-Specific Behavior

- **BUILD:** Run detection unless `launch_command_override` is set, in which case the override wins.
- **REPAIR — directive `launch_command` or `phase-a`:** Re-run detection. Preserve `process` and `health_probe` from PRIOR_LAUNCH.
- **REPAIR — directive `restart`:** Phase A is re-run as part of restart (preserving operator overrides if still passed).

---

## Override Branch

When `launch_command_override` is provided:

```
LAUNCH_INDEX.launch = {
  command: launch_command_override,
  cwd: source_path,                       # default; override does not change cwd
  package_manager: "unknown",             # not detected when overridden
  framework: "unknown",
  detected_from: "operator override",
  override_applied: true
}
decisions_log += { phase: "phase-a", decision: "command override applied", evidence: "parameter: launch_command_override" }
```

Skip the detection matrix. Proceed to Phase B.

---

## Detection Matrix

### Node.js

Read `source_path/package.json`. Inspect `scripts` keys in priority order:

| Script key (in `package.json:scripts`) | Verdict (preferred dev command) |
|---|---|
| `start:dev` | `npm run start:dev` (or pnpm/yarn/bun equivalent) |
| `dev` | `npm run dev` |
| `start` AND `nodemon` in devDependencies | `npm run start` |
| `start` (only — no nodemon) | `npm run start` |
| `nest start --watch` script | `npm run start:dev` (NestJS convention) |
| (none) | log blocker `no_dev_script_found` |

Detect package manager from lockfile (as in `bootstrapping-runtime-environment.phase-a`):
`pnpm-lock.yaml` → `pnpm`; `yarn.lock` → `yarn`; `bun.lockb` → `bun`; otherwise `npm`.

Translate `npm run X` to the detected manager:
- pnpm: `pnpm run X` or just `pnpm X`
- yarn: `yarn X`
- bun: `bun run X` or `bun X`

### Python

Read `source_path/pyproject.toml` (poetry / pdm) OR `source_path/Pipfile` (pipenv) OR `requirements.txt`.

| Signal | Verdict |
|---|---|
| `pyproject.toml` declares `[tool.poetry.scripts]` with `dev` entry | `poetry run dev` |
| `Pipfile` declares `[scripts] dev = "..."` | `pipenv run dev` |
| FastAPI app discovered (import `fastapi` AND `app = FastAPI()` in `main.py` or `app.py`) | `uvicorn main:app --reload --port {PORT}` |
| Flask app discovered (`app = Flask(__name__)` in `app.py`) | `flask --app app run --debug --port {PORT}` |
| Django (`manage.py` exists at root) | `python manage.py runserver 0.0.0.0:{PORT}` |
| (none) | log blocker `no_dev_command_found` |

When `{PORT}` appears, substitute the value read from `env_file_path` (key `PORT`), defaulting to:
- FastAPI/Flask: `8000`
- Django: `8000`

### Java

Read `source_path/pom.xml` OR `source_path/build.gradle` / `build.gradle.kts`.

| Signal | Verdict |
|---|---|
| Maven + `spring-boot-maven-plugin` declared | `./mvnw spring-boot:run` |
| Gradle + `org.springframework.boot` plugin | `./gradlew bootRun` |
| Maven, no spring-boot plugin, `quarkus-maven-plugin` | `./mvnw quarkus:dev` |
| Generic Maven with `exec-maven-plugin` and `mainClass` configured | `./mvnw compile exec:java` |
| (none) | log blocker `no_dev_command_found` |

### Ruby

Read `source_path/Gemfile`.

| Signal | Verdict |
|---|---|
| `rails` gem | `bin/rails server --binding 0.0.0.0 --port {PORT}` |
| `sinatra` gem | `bundle exec ruby {entry_file}.rb` |
| `roda` gem | `bundle exec rackup` |
| (none) | log blocker `no_dev_command_found` |

Default PORT for Rails: `3000`.

### Go

Read `source_path/go.mod` and the root directory.

| Signal | Verdict |
|---|---|
| `main.go` in source_path root | `go run main.go` |
| `cmd/{name}/main.go` exists | `go run ./cmd/{name}` |
| Air config file (`.air.toml`) | `air` (hot reload via Air) |
| (none) | log blocker `no_dev_command_found` |

### .NET

Read `source_path/*.csproj`.

| Signal | Verdict |
|---|---|
| Any `.csproj` in source_path | `dotnet watch run --project {csproj path}` |
| (none) | log blocker `no_dev_command_found` |

---

## Special Cases

### Monorepo workspaces

If `package.json:workspaces` is defined AND `source_path` is the workspace root:
- Detection still runs against the root `package.json`'s `scripts`.
- If no top-level `dev` exists, fall back to detecting the API app explicitly: look for `apps/api/package.json` and use `npm run --workspace apps/api start:dev` (or equivalent).
- Log decision: `"monorepo workspace detected; targeting apps/api by convention"`.

### Multiple entry points (api + web)

The skill launches ONE process per invocation. When both API and web are present:
- Default to the API (`apps/api` or whatever the framework decoration declares as backend).
- If the operator wants to launch the web app, they must pass `launch_command_override` or split into two invocations.
- Log decision: `"both api and web detected; launching api by default; pass launch_command_override for web"`.

### Watch mode caveats

Dev commands typically run with file watchers (`--watch`, `nodemon`, `air`, `dotnet watch`). This is **desired** — the smoke fix loop relies on hot reload picking up code edits. The skill does NOT switch to production mode for smoke validation.

---

## Source Fidelity Check (before writing)

- [ ] `launch.command` is non-empty
- [ ] `launch.command` does not include interactive flags (`--interactive`, `-i`) or commands known to prompt (`npx create-*`, `yo`)
- [ ] `launch.cwd` exists and contains the manifest cited in `detected_from`
- [ ] When `override_applied == true`, `detected_from == "operator override"`
- [ ] When detection fails (no dev command found), `blockers` has an entry with kind `no_dev_command_found` AND `decisions_log` records the failure with a list of files inspected
- [ ] Package manager rewriting (npm → pnpm/yarn/bun) is applied when a non-npm lockfile is present

## Post-Section Protocol

1. **Update** `LAUNCH_INDEX.launch`, `LAUNCH_INDEX.decisions_log`
2. **Update** `_progress.json`: `completed: 1`
3. **Flush** raw manifest content
4. **Verify** `launch.command` is set OR `blockers` has the failure entry
5. **Log:** `"Phase A COMPLETE. Command: {launch.command} (cwd: {launch.cwd}, source: {detected_from})"`
