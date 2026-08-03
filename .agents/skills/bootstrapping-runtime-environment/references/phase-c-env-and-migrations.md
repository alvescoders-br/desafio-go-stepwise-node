# bootstrapping-runtime-environment — Phase C: Env Synthesis & Migrations

## Context Contract

- **Inputs:** `BOOT_INDEX.stack`, `BOOT_INDEX.services_running[]`, `BOOT_INDEX.source_path`, parameter `env_template_path` (optional)
- **Outputs:** `BOOT_INDEX.env_file_path`, `BOOT_INDEX.env_keys_synthesized[]`, `BOOT_INDEX.env_blockers[]`, `BOOT_INDEX.migrations_applied[]`, `BOOT_INDEX.db_ready`; the actual `.env` file on disk
- **Carries Forward:** `env_file_path` (consumed by `launching-app`), `db_ready` (gate for runtime validation)
- **Flush After:** Raw config-schema file contents — keep only structured `env_keys_synthesized` and `env_blockers`
- **Dependency:** Phase B must be COMPLETE (`services_running` populated)
- **H1 Title:** `# Phase C — Env Synthesis & Migrations`

## Mode-Specific Behavior

- **BUILD:** Run full env synthesis and migrations.
- **REPAIR — directive `env` or `phase-c`:** Re-run env synthesis only. Preserve `migrations_applied`.
- **REPAIR — directive `migrations`:** Re-run migrations only. Preserve `env_file_path`.
- **REPAIR — directive `env_keys_synthesized.{KEY}`:** Surgical — edit one env var in place. Preserve everything else.

---

## Part 1: Env Key Discovery

### When `env_template_path` is provided

```
LOAD env_template_path content
template_keys = parse all KEY=... lines (ignore commented lines starting with #)
COPY env_template_path → {output_folder}/.env (as the starting file)
```

Treat `template_keys` as the authoritative set. Skill still synthesizes values for keys
whose template value is empty, `<>`-placeholder, or matches the pattern
`^<.+>$`.

### When no template is provided

Discover required keys by scanning source code per stack:

**node/nest:**
- Search for `ConfigService.get('KEY')` and `process.env.KEY` references
- Read any `config.schema.ts`, `app.config.ts`, `*.module.ts` files declaring `@Joi.object({ KEY: ... })` or zod schema
- Read any `validation.ts` exported config schema

**python/fastapi/django:**
- Read `settings.py` / `config.py` for `os.environ.get('KEY')` or `os.getenv('KEY', default)`
- Read pydantic-settings classes (`class Settings(BaseSettings)`) — every field is an env var
- Django: `os.environ['KEY']` references and `settings.py` constants reading env

**java/spring:**
- Grep for `@Value("${KEY}")` and `@ConfigurationProperties("prefix")`
- Read `application.yml` / `application.properties` for `${KEY}` references

**ruby/rails:**
- Grep for `ENV['KEY']` and `ENV.fetch('KEY')`
- Read `config/application.rb` and `config/environments/*.rb`

The union of all discovered keys becomes `template_keys`.

---

## Part 2: Value Synthesis

For each key in `template_keys`, derive a value using this resolution table (first match wins):

| Key pattern | Source / Value | Mark as |
|---|---|---|
| `DATABASE_URL` | Synthesize from `services_running` where `role=db` using engine-specific URL format (see below) | synthesized |
| `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Parse from `services_running[db]` fields | synthesized |
| `REDIS_URL` | `redis://{host}:{port}` from `services_running[role=cache]` | synthesized |
| `REDIS_HOST`, `REDIS_PORT` | Same source | synthesized |
| `RABBITMQ_URL` or `AMQP_URL` | `amqp://guest:guest@{host}:{port}` from `services_running[role=queue]` | synthesized |
| `APP_ENV`, `NODE_ENV`, `ENVIRONMENT`, `ENV` | `development` | synthesized |
| `SPRING_PROFILES_ACTIVE` | `dev` | synthesized |
| `PORT`, `APP_PORT`, `SERVER_PORT` | First available port starting 3000 (probe with `lsof -i`) | synthesized |
| `LOG_LEVEL` | `debug` | synthesized |
| `AWS_REGION`, `*_REGION` | `eu-west-1` | assumption |
| `CORRELATION_ID_HEADER` | `X-Correlation-ID` | assumption |
| `AUTH_MODE`, `OIDC_MODE` | `mock_oidc` (only if `dev` mock exists in code) | assumption |
| `MOCK_OIDC_PORT`, `MOCK_OIDC_ISSUER_URL` | `9999`, `http://localhost:9999` | assumption |
| `AUTH_CLIENT_ID`, `AUTH_CLIENT_SECRET` (with mock auth) | `local-client`, `local-secret` | assumption |
| `AUTH_CALLBACK_URL` | `http://localhost:{PORT}/auth/callback` (or first guessed path) | assumption |
| keys matching `^(SECRET|API_KEY|TOKEN|PASSWORD|PRIVATE_KEY)_?` AND no dev default in code | `<REQUIRED_OPERATOR_INPUT>` placeholder | env_blockers |
| any key with `vault:` or `aws-sm:` prefix in template | `<REQUIRED_OPERATOR_INPUT>` placeholder | env_blockers |
| anything else | (best-effort: look for a default in code; else placeholder) | env_blockers if no default found |

### DATABASE_URL synthesis by engine

| engine | URL format |
|---|---|
| postgres | `postgresql://{user}:{password}@{host}:{port}/{db_name}?schema=public` |
| mysql | `mysql://{user}:{password}@{host}:{port}/{db_name}` |
| mongodb | `mongodb://{user}:{password}@{host}:{port}/{db_name}?authSource=admin` |
| sqlite | `file:./dev.db` (or `file::memory:?cache=shared` for in-memory) |

Default credentials when spinning up new containers (from Phase B image args):

| engine | user | password | db_name |
|---|---|---|---|
| postgres | `postgres` | `postgres` | `{project_name}_dev` |
| mysql | `root` | `mysql` | `{project_name}_dev` |
| mongodb | (no auth on default image) | — | `{project_name}_dev` |

When `existing_db_url` was used in Phase B, the user/password are extracted from that URL.

---

## Part 3: Write .env

```
WRITE atomically:
  - write to {output_folder}/.env.tmp
  - mv {output_folder}/.env.tmp → {output_folder}/.env (atomic on POSIX)

env_file_path = {output_folder}/.env
env_keys_synthesized = [ key for key, status in all_keys if status == "synthesized" ]
env_blockers += [ { kind: "missing_secret", key, description, suggested_remediation } for each blocker key ]
```

Blocker `description` template:
```
"Required env var '{KEY}' has no dev default and no source available. The agent
left a placeholder '<REQUIRED_OPERATOR_INPUT>' in .env. Operator must supply a
real value before launching."
```

Blocker `suggested_remediation`:
- For `SECRET`/`API_KEY` → `"Set in .env or pass via environment when running launching-app"`
- For `VAULT:`/`AWS_SM:` references → `"Fetch from {vault-path} and set in .env, or wire vault integration"`
- For OIDC client IDs/secrets without mock fallback → `"Register an OIDC application in dev IdP and set client_id/secret"`

---

## Part 4: Run Migrations

Branch on `BOOT_INDEX.stack.orm`:

### Prisma

```
duration_start = now()
RUN: cd {source_path} && npx prisma generate
exit_code_1 = $?
IF exit_code_1 != 0:
  blockers += { kind: "migration_failed", phase: "prisma generate", stderr_excerpt }
  STOP migrations.

IF prisma/migrations/ directory exists with prior .sql files:
  RUN: cd {source_path} && DATABASE_URL={DATABASE_URL} npx prisma migrate dev --name auto-{SESSION_ID} --skip-seed
ELSE:
  RUN: cd {source_path} && DATABASE_URL={DATABASE_URL} npx prisma db push --accept-data-loss --skip-generate

exit_code = $?
duration_ms = now() - duration_start

IF exit_code != 0 AND stderr contains "CREATEDB" privilege:
  # Defensive: Phase B should have granted this, but handle the case
  RUN: docker exec {db_container_id} psql -U postgres -c "ALTER USER {dbuser} CREATEDB;"
  RETRY the migration command once
  duration_ms = now() - duration_start (update)

migrations_applied += {
  tool: "prisma",
  command: "{the command actually run}",
  duration_ms,
  exit_code,
  stderr_excerpt: (only if exit_code != 0)
}
```

### TypeORM

```
RUN: cd {source_path} && npm run typeorm migration:run
# or directly: npx typeorm-ts-node-esm migration:run -d {datasource path}
migrations_applied += { tool: "typeorm", command, duration_ms, exit_code }
```

### SQLAlchemy / Alembic

```
RUN: cd {source_path} && alembic upgrade head
migrations_applied += { tool: "alembic", command, duration_ms, exit_code }
```

### Drizzle

```
RUN: cd {source_path} && npx drizzle-kit push
migrations_applied += { tool: "drizzle", command, duration_ms, exit_code }
```

### Hibernate / Flyway

```
RUN: cd {source_path} && ./mvnw flyway:migrate     # if maven
# or: ./gradlew flywayMigrate
migrations_applied += { tool: "flyway", command, duration_ms, exit_code }
```

### ActiveRecord

```
RUN: cd {source_path} && bundle exec rails db:create db:migrate
migrations_applied += { tool: "activerecord", command, duration_ms, exit_code }
```

### None (no ORM detected)

Skip migrations. Set `db_ready = (BOOT_INDEX.stack.db_engine == "none")` (i.e. ready if no DB
needed at all, false otherwise — caller may still manually load schema).

---

## Part 5: Set db_ready

```
db_ready = (
  all migrations_applied[].exit_code == 0
  AND no entries in env_blockers with kind == "missing_secret" for DATABASE_URL/DB_PASSWORD
  AND (stack.db_engine == "none" OR services_running has an entry with role=db AND reachable)
)
```

---

## Source Fidelity Check (before writing)

- [ ] `.env` file exists at `env_file_path` and is non-empty
- [ ] Every key in `env_keys_synthesized` has a concrete value in `.env` (not a placeholder)
- [ ] Every key in `env_blockers` has a `<REQUIRED_OPERATOR_INPUT>` placeholder in `.env`
- [ ] No key appears in both `env_keys_synthesized` and `env_blockers`
- [ ] `migrations_applied` has at least one row when `stack.orm != none`
- [ ] When `db_ready == false`, at least one entry in `env_blockers` OR `migrations_applied[].exit_code != 0` exists (no silent failures)
- [ ] Atomic write used — no partial `.env.tmp` left behind on failure

## Post-Section Protocol

1. **Write** `{output_folder}/.env` (atomic write — tmp then mv). MANDATORY TOOL CALL.
2. **Update** `BOOT_INDEX.env_file_path`, `env_keys_synthesized`, `env_blockers`, `migrations_applied`, `db_ready`
3. **Update** `_progress.json`: `completed: 3`, `items[2] = { phase: "env-and-migrations", status: "COMPLETE" }`
4. **Flush** raw config-schema content and migration stderr (except `stderr_excerpt` recorded in `migrations_applied`)
5. **Verify** `.env` exists, key counts match, `db_ready` matches the rule above
6. **Log:** `"Phase C COMPLETE. Env keys: {N} synthesized, {M} blocked. Migrations: {K} applied ({F} failed). db_ready: {db_ready}."`
