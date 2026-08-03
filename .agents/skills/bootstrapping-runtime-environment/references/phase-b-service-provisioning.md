# bootstrapping-runtime-environment — Phase B: Service Provisioning

## Context Contract

- **Inputs:** `BOOT_INDEX.stack` (db_engine, needs_redis, needs_queue), `BOOT_INDEX.project_name`, parameter `db_strategy`, parameter `existing_db_url`
- **Outputs:** `BOOT_INDEX.services_running[]`, `BOOT_INDEX.port_collisions[]`, entries in `BOOT_INDEX.decisions_log`
- **Carries Forward:** `services_running[]` — the env-synthesis phase reads `host`/`port`/`user` from this to build connection URLs
- **Flush After:** Full `docker ps` output and port probe results — keep only the structured `services_running` rows
- **Dependency:** Phase A must be COMPLETE
- **H1 Title:** `# Phase B — Service Provisioning`

## Mode-Specific Behavior

- **BUILD:** Run the full decision tree per required service.
- **REPAIR:** Skip when no directive targets `services` or `phase-b`. When targeted, re-run the decision tree and overwrite `services_running[]`. Preserve `env_file_path` and `migrations_applied` from prior run (env synthesis re-runs anyway because connection strings depend on services).
- **RESUME:** Not applicable.

---

## Required Service Enumeration

Build the required-services list from `BOOT_INDEX.stack`:

```
required_services = []
IF stack.db_engine != "none":           required_services += { kind: stack.db_engine, role: "db" }
IF stack.needs_redis == true:           required_services += { kind: "redis",          role: "cache" }
IF stack.needs_queue == "rabbit":       required_services += { kind: "rabbitmq",       role: "queue" }
IF stack.needs_queue == "redis-streams" AND not already added: required_services += { kind: "redis", role: "queue" }
```

If `required_services` is empty → log `"No services needed"` to `decisions_log` and exit phase
with `services_running = []`.

---

## Override Branches (Short-Circuit)

### Branch 1: `existing_db_url` is set

PARSE the URL:
```
DATABASE_URL = postgresql://user:pass@host:port/db_name
              → { kind: parsed-from-url, host, port, db_name, user }
services_running += { name: db_name, kind: stack.db_engine, host, port, reused: true, source: "existing_db_url override" }
```

Skip the decision tree for the DB. Continue evaluation for redis/queue (they may still need provisioning).

### Branch 2: `db_strategy == sqlite-in-memory`

```
services_running += { kind: "sqlite", host: "file::memory:?cache=shared", port: null, reused: false }
```

Skip DB provisioning. Continue evaluation for redis/queue.

### Branch 3: `stack.db_engine == sqlite`

Same as Branch 2 — sqlite never needs a container. Use a file-backed path by default:
```
services_running += { kind: "sqlite", host: "file:./dev.db", port: null, reused: false }
```

---

## Decision Tree (per service in required_services)

When none of the override branches apply, run this for each required service.

### Step 1: Resolve effective strategy

```
effective_strategy = db_strategy
IF effective_strategy == "auto":
  RUN: docker ps --filter "ancestor={image_for_kind}" --format "{{.ID}}\t{{.Names}}\t{{.Ports}}"
  IF any container is running AND its exposed port responds to a connection probe:
    effective_strategy = "reuse-existing-docker"
  ELSE:
    effective_strategy = "spin-up-new-docker"
```

### Step 2: Branch on strategy

**`reuse-existing-docker`:**
```
container_id = first matching container from docker ps
host = "localhost"
port = parse exposed port from docker ps output
PROBE: open TCP connection to host:port (max 3s)
IF probe fails:
  LOG decision conflict: "container running but port not reachable, falling through to spin-up"
  effective_strategy = "spin-up-new-docker"   # retry
ELSE:
  services_running += { name: container_id, kind, host, port, container_id, container_name, reused: true }
  decisions_log += { phase: "phase-b", decision: "reused {kind} container {container_name}", evidence: "docker ps {timestamp}" }
```

**`spin-up-new-docker`:**

| kind | image | default port | container name | extra args |
|---|---|---|---|---|
| postgres | `postgres:16-alpine` | 5432 | `{project_name}-postgres` | `-e POSTGRES_PASSWORD=postgres -e POSTGRES_DB={project_name}_dev` |
| mysql | `mysql:8` | 3306 | `{project_name}-mysql` | `-e MYSQL_ROOT_PASSWORD=mysql -e MYSQL_DATABASE={project_name}_dev` |
| mongodb | `mongo:7` | 27017 | `{project_name}-mongo` | (none) |
| redis | `redis:7-alpine` | 6379 | `{project_name}-redis` | (none) |
| rabbitmq | `rabbitmq:3-management-alpine` | 5672 | `{project_name}-rabbit` | (management UI on 15672) |

```
RUN: docker run -d --name {container_name} -p {host_port}:{default_port} {extra_args} {image}
WAIT_FOR_READY (max 30s, exponential backoff probe):
  - postgres: pg_isready or psql -c "SELECT 1"
  - mysql: mysqladmin ping
  - mongodb: mongosh --eval "db.adminCommand('ping')"
  - redis: redis-cli ping
  - rabbitmq: rabbitmq-diagnostics ping

IF ready within 30s:
  services_running += { name, kind, host: "localhost", port: host_port, container_id, container_name, reused: false }
  decisions_log += { phase: "phase-b", decision: "spun up {kind} container", evidence: "docker run output" }
ELSE:
  blockers += { kind: "service_not_ready", description: "{kind} container did not become ready in 30s" }
  STOP this service; continue with the next.
```

---

## Port Collision Handling

For `spin-up-new-docker` only — when binding to `{default_port}`:

```
PROBE: is {default_port} in use by ANY process?
  RUN: lsof -i :{default_port} 2>/dev/null || ss -tlnp | grep :{default_port}
IF in use AND occupying process is NOT a docker container we'd reuse:
  port_collisions += { port: default_port, occupying_process: <name>, attempted_at: <timestamp> }
  TRY successive ports: default_port + 1, default_port + 2, ... up to 5 attempts
  ON success: use the available port; decisions_log += "port collision: used {N} instead of {default_port}"
  ON exhaustion: blockers += { kind: "port_collision", description: "ports {N..N+5} all occupied" }; STOP this service
```

---

## Special Case: Postgres CREATEDB Privilege for Prisma Shadow DB

When `BOOT_INDEX.stack.orm == "prisma"` AND the postgres service is provisioned with a
non-superuser:

```
RUN: docker exec {container_id} psql -U postgres -c "ALTER USER {dbuser} CREATEDB;"
decisions_log += {
  phase: "phase-b",
  decision: "granted CREATEDB to {dbuser} for prisma shadow database",
  evidence: "postgres superuser grant"
}
```

Skip this step when:
- The DB engine is not postgres
- The configured DB user is already `postgres` (superuser by default)
- `existing_db_url` was used (out of skill's scope to ALTER USER on external DBs — log a blocker if migrations later fail)

---

## Source Fidelity Check (before writing)

- [ ] Every service in `required_services` has either: a row in `services_running` OR a row in `blockers`
- [ ] Every `services_running` row has a `reused` boolean and a non-empty `evidence` field in the matching `decisions_log` entry
- [ ] `port_collisions[]` only contains entries where collision was actually observed (not predicted)
- [ ] `decisions_log` includes a row for every container reused AND every container spun up
- [ ] When `existing_db_url` was used, no extra DB container was spun up

## Post-Section Protocol

1. **Update** `BOOT_INDEX.services_running`, `BOOT_INDEX.port_collisions`, `BOOT_INDEX.decisions_log`
2. **Update** `_progress.json`: `completed: 2`, `items[1] = { phase: "service-provisioning", status: "COMPLETE" }`
3. **Flush** docker ps output and port probe traces from memory — keep only structured rows
4. **Verify** every required_services kind has at least one matching `services_running` or `blockers` entry
5. **Log:** `"Phase B COMPLETE. Services: {N} running ({reused_count} reused, {spunup_count} spun-up), {collision_count} port collisions, {blocker_count} service blockers."`
