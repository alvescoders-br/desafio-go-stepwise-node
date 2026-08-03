# launching-app — Phase B: Launch & Health Probe

## Context Contract

- **Inputs:** `LAUNCH_INDEX.launch`, `LAUNCH_INDEX.source_path`, parameter `env_file_path`, parameter `health_endpoint`, parameter `health_probe_method`, parameter `launch_timeout_seconds`, parameter `application_url_override` (optional)
- **Outputs:** `LAUNCH_INDEX.process`, `LAUNCH_INDEX.health_probe`, `LAUNCH_INDEX.launch_status`, `LAUNCH_INDEX.surfaces[]`, `LAUNCH_INDEX.boot_errors[]`
- **Carries Forward:** `process.pid`, `process.runtime_url`, `process.log_path`, `process.surfaces[]` (consumed by Phase C and downstream smoke probes)
- **Flush After:** Raw probe response bodies and full log content — keep only `boot_errors` excerpts and `last_response`
- **Dependency:** Phase A must be COMPLETE
- **H1 Title:** `# Phase B — Launch & Health Probe`

## Mode-Specific Behavior

- **BUILD:** Spawn, capture pid, probe.
- **REPAIR — directive `health_probe`:** Re-probe an existing running process. Do NOT respawn.
- **REPAIR — directive `restart`:** Kill prior pid, then spawn fresh.
- **REPAIR — directive `phase-b`:** Treat as `restart`.
- **RESUME:** Not applicable — short-lived phase.

---

## application_url_override Branch

When `application_url_override` is provided:

```
process.runtime_url = application_url_override
process.reused_existing = true
process.pid = null
process.log_path = ""
process.port = parsed from URL
process.launched_at = now()

# Still run the probe — operator may have given a wrong URL or the service may not be running
GOTO Health Probe section.
```

---

## Pre-Spawn: Reuse Detection

Before spawning, check whether the intended port is already in use AND the occupying process is plausibly ours:

```
intended_port = parse from env_file_path PORT/SERVER_PORT/APP_PORT key
                OR framework default (3000/8000/8080/3000)

PROBE: lsof -i :{intended_port} -P -n -F pcL  (mac) OR ss -tlnp | grep :{intended_port}  (linux)

IF a process is listening on intended_port:
  GET its cwd via: lsof -p {pid} -d cwd -F n  (mac) OR readlink /proc/{pid}/cwd  (linux)
  IF cwd starts with source_path OR cwd is a subdirectory of source_path:
    process.pid = the existing pid
    process.port = intended_port
    process.runtime_url = "http://localhost:{intended_port}"
    process.log_path = "" (we did not launch — log not under our control)
    process.reused_existing = true
    decisions_log += { phase: "phase-b", decision: "reused existing process pid={pid} listening on {port}", evidence: "lsof output" }
    GOTO Health Probe section (skip spawn).
  ELSE:
    # Port is in use by a DIFFERENT project
    boot_errors += { category: "port_collision", excerpt: "port {intended_port} in use by pid {pid} ({cwd})", severity: "high" }
    launch_status = FAILED
    EXIT Phase B (proceed to Phase C reporting).
```

---

## Spawn

```
log_path = {output_folder}/runtime.log
TRUNCATE log_path (start fresh; preserved across re-runs would mix old + new errors)

SPAWN (background):
  cd {launch.cwd}
  set -a; source {env_file_path}; set +a
  exec {launch.command} > {log_path} 2>&1 &
  pid=$!
  echo $pid > {output_folder}/.launch.pid

WAIT 3 seconds.

PROBE: is {pid} still alive?
  RUN: kill -0 {pid} 2>/dev/null
  IF non-zero exit:
    # Died immediately
    TAIL log_path (last 100 lines) → extract boot_errors
    launch_status = FAILED
    process.pid = pid       # record even though dead
    process.log_path = log_path
    EXIT Phase B (proceed to Phase C).

process.pid = pid
process.log_path = log_path
process.launched_at = now()
process.reused_existing = false
```

---

## Port Discovery

After spawn (and 3-second wait), the process should have logged the port it's bound to.

```
PORT_DISCOVERY_PATTERNS = [
  /listening on port (\d+)/i,
  /Listening on http[s]?:\/\/[^:]+:(\d+)/i,
  /Server (?:running|started|ready) (?:on|at) http[s]?:\/\/[^:]+:(\d+)/i,
  /Local:\s+http[s]?:\/\/[^:]+:(\d+)/,            # Vite / Next dev server
  /running on port (\d+)/i,
  /Uvicorn running on http[s]?:\/\/[^:]+:(\d+)/,  # uvicorn
  /\* Running on http[s]?:\/\/[^:]+:(\d+)/,       # Flask debug
  /Started [A-Za-z]+Application.*on port\(s\):\s*(\d+)/, # Spring Boot
  /Started.*Puma.*tcp:\/\/[^:]+:(\d+)/,           # Rails / Puma
]

TAIL log_path (last 50 lines)
FOR EACH pattern in PORT_DISCOVERY_PATTERNS:
  MATCH against log content
  IF match: discovered_port = first capture group; BREAK

IF no match found:
  WAIT additional 5 seconds (some frameworks log readiness slowly)
  RETRY pattern match
  IF still no match:
    # Fall back to env PORT or framework default
    discovered_port = env PORT key OR framework_default_for(launch.framework)
    decisions_log += { phase: "phase-b", decision: "port not discovered from log; fell back to {discovered_port}", evidence: "log_path scan" }

process.port = discovered_port
process.runtime_url = "http://localhost:{discovered_port}"
```

---

## Health Probe Loop

```
attempts = 0
start_time = now()
backoff = [1, 2, 4, 8, 8, 8, ...]  # seconds; capped at 8

WHILE (now() - start_time) < launch_timeout_seconds:
  attempts += 1

  # Mid-loop liveness check
  IF process.pid AND NOT process.reused_existing:
    IF NOT (kill -0 {process.pid}): 
      # Process died during probe
      TAIL log_path (last 200 lines) → extract boot_errors
      launch_status = FAILED
      health_probe.final_status = FAIL
      BREAK

  SWITCH health_probe_method:
    CASE "http":
      RESPONSE = HTTP GET {runtime_url}{current_endpoint} (timeout 5s)
      health_probe.last_response = "{status} {first 200 bytes of body}"
      IF status >= 200 AND status < 400:
        health_probe.final_status = PASS
        BREAK_OUTER  # exit WHILE
      IF status == 404 AND attempts == 1 AND current_endpoint == "/health":
        current_endpoint = "/"
        decisions_log += { phase: "phase-b", decision: "/health 404; falling back to /", evidence: "first probe attempt" }
        continue (without sleeping)
      IF connection refused / connection reset:
        health_probe.last_response = "not ready (connection refused)"
        # fall through to sleep
      ELSE:
        # 4xx other than 404, or 5xx — record but continue trying (server may still be initialising)
        # fall through to sleep

    CASE "port":
      TCP_OPEN: connect to localhost:{port}, timeout 2s
      IF success:
        health_probe.final_status = PASS
        BREAK_OUTER
      ELSE:
        health_probe.last_response = "tcp connect failed"

    CASE "log":
      READY_MARKERS = framework-specific list:
        nest:    "Application successfully started" | "Nest application successfully started"
        fastapi: "Application startup complete"
        spring:  "Started .*Application in .* seconds"
        rails:   "Listening on tcp://"
        django:  "Starting development server at"
        next:    "ready started server on"
        vite:    "ready in" | "Local:"
      TAIL log_path (last 50 lines)
      IF any marker matches: 
        health_probe.final_status = PASS
        BREAK_OUTER

  SLEEP backoff[min(attempts - 1, len(backoff) - 1)]

# Loop exit conditions:
IF health_probe.final_status == PASS:
  launch_status = RUNNING
ELIF process is still alive (not reused, not dead):
  health_probe.final_status = TIMEOUT
  launch_status = TIMEOUT
ELSE:
  health_probe.final_status = FAIL  # set above when process died
  launch_status = FAILED

health_probe.attempts = attempts
health_probe.elapsed_ms = (now() - start_time) * 1000
health_probe.method = health_probe_method
health_probe.target = (runtime_url + current_endpoint) | port | "log_marker"
```

---

## Runtime Surface Detection

After a service reaches `launch_status == RUNNING`, classify what can be smoked at
that URL. Do not infer browser capability from service role alone; a monolith,
server-rendered app, admin UI, or API service may expose both browser and API
surfaces on the same port.

```
surfaces = []

IF launch_status == RUNNING AND process.runtime_url is not empty:
  # Browser surface signals. Any one strong signal is enough.
  ROOT_RESPONSE = health_probe.last_response if it came from "/" ELSE bounded GET runtime_url + "/"
  IF ROOT_RESPONSE content-type contains "text/html"
     OR ROOT_RESPONSE body excerpt contains "<html"
     OR ROOT_RESPONSE body excerpt contains "<form"
     OR ROOT_RESPONSE body excerpt contains "<script"
     OR ROOT_RESPONSE body excerpt contains "<a ":
    surfaces += {
      kind: "browser",
      url: process.runtime_url,
      evidence: "HTML response at service root or health fallback",
      confidence: "high"
    }
  ELIF launch.role == "web":
    surfaces += {
      kind: "browser",
      url: process.runtime_url,
      evidence: "planned role=web",
      confidence: "medium"
    }

  # API surface signals. Any one strong signal is enough.
  IF launch.role == "api":
    surfaces += {
      kind: "api",
      url: process.runtime_url,
      evidence: "planned role=api",
      confidence: "medium"
    }
  IF source route scan, OpenAPI discovery, framework router/controller discovery,
     a route path containing "/api/", or an application/json probe response exists:
    surfaces += {
      kind: "api",
      url: process.runtime_url,
      evidence: "API route or JSON response detected",
      confidence: "high"
    }

DEDUPE surfaces by (kind, url), retaining the highest confidence evidence.

IF surfaces is empty:
  open_questions += {
    id: "OQ-SURFACE-01",
    type: "surface_detection",
    description: "Service is RUNNING but no browser/api surface could be inferred",
    impact: "local-runtime-validation may skip smoke probes for this service"
  }
```

The resulting `surfaces[]` array is part of each `runtime_info.json.services[]`
entry and is the preferred contract for smoke probe selection.

---

## Boot-Error Extraction

When `launch_status != RUNNING`, classify the last lines of `log_path`:

```
TAIL log_path (last 200 lines)
FOR EACH line:
  CLASSIFY line into one of:
    - "config_error": matches /Config validation error|InvalidConfig|env var .* (required|missing)|ValidationError/i
    - "dependency_missing": matches /Cannot find module|ModuleNotFoundError|ImportError|ClassNotFoundException|gem .* could not be found/i
    - "port_collision": matches /EADDRINUSE|Address already in use|Port \d+ is already in use/i
    - "db_connection": matches /ECONNREFUSED.*:5432|.*:3306|.*:27017|Authentication failed|password authentication failed/i
    - "schema_drift": matches /relation .* does not exist|Unknown column|column .* does not exist|table .* doesn't exist/i
    - "uncaught_exception": matches /UnhandledPromiseRejection|Traceback \(most recent call last\)|Exception in thread "main"|FATAL/i
    - "generic": anything containing "Error:" or "Exception" not matched above

  SEVERITY:
    fatal: lines causing process death (last 5 lines before death)
    high: any classified non-generic error
    low: generic

  boot_errors += { category, line_number, excerpt: (line trimmed to 240 chars), severity }

DEDUPLICATE boot_errors by (category, excerpt) — keep first occurrence.
CAP boot_errors at 50 entries (FIFO trim).
```

---

## Source Fidelity Check (before writing)

- [ ] `process.pid` is set when we spawned; `process.reused_existing == true` when we did not
- [ ] `process.port` is a positive integer; `process.runtime_url` matches `http://localhost:{port}` (or is the override URL)
- [ ] `process.log_path` is the absolute path written to `{output_folder}/runtime.log` (or empty when reused/overridden)
- [ ] `health_probe.attempts >= 1`
- [ ] `health_probe.final_status` ∈ { PASS, FAIL, TIMEOUT }
- [ ] `process.surfaces[]` exists for every service. RUNNING HTTP services should have at least one `browser` or `api` surface, or an `OQ-SURFACE-*` open question.
- [ ] When `launch_status == FAILED` or `TIMEOUT`, `boot_errors` has at least one entry (zero entries → register `OQ-XX` open question about silent failure)
- [ ] When `launch_status == RUNNING`, `boot_errors` may be empty
- [ ] `.launch.pid` sidecar file is written (used by capability teardown to find the pid)

## Post-Section Protocol

1. **Update** `LAUNCH_INDEX.process`, `health_probe`, `launch_status`, `boot_errors`, `decisions_log`
2. **Update** `_progress.json`: `completed: 2`
3. **Flush** raw log content (keep only `boot_errors` excerpts and `last_response`)
4. **Verify** `runtime_info.json` would have consistent values (pid + port + url match)
5. **Log:** `"Phase B COMPLETE. launch_status: {launch_status}, runtime_url: {runtime_url}, probe attempts: {attempts}, boot_errors: {N}"`
