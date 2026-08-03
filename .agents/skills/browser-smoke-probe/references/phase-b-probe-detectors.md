# browser-smoke-probe — Phase B: Five-Detector Probe Loop

## Context Contract

- **Inputs:** `BROWSER_SMOKE_INDEX.route_inventory`, `runtime_url`, parameters `max_probe_seconds`, `auth_credentials_path` (optional)
- **Outputs:** `BROWSER_SMOKE_INDEX.probed_routes[]`, `browser_errors[]`, screenshot files
- **Carries Forward:** `browser_errors[]` (consumed by Phase C report), `probed_routes[]` (subset becomes `smoke_route_inventory`)
- **Flush After:** Raw console logs and network request lists beyond per-route caps — keep only classified errors and truncated captures
- **Dependency:** Phase A must be COMPLETE
- **H1 Title:** `# Phase B — Probe & Detectors`

## Mode-Specific Behavior

- **BUILD:** Probe every route in `route_inventory`.
- **REPAIR — directive `probe`:** Re-probe all routes.
- **REPAIR — directive `single-route:{id}`:** Re-probe only that route. Merge new error rows; remove prior rows for that route_id before merge.
- **REPAIR — directive `routes` only:** Phase B is skipped (route selection changed but probe is not re-run unless `probe` is also targeted).

---

## Authentication (Pre-Loop)

Runs once before the per-route loop, when both:
- `auth_credentials_path` is set
- At least one route has `requires_auth: true`

```
LOAD auth_credentials_path → { username, password, login_path?, success_selector? }
login_path = explicit value OR "/login"

browser_navigate(runtime_url + login_path)
browser_wait_for_network_idle(3s)

# Heuristic-driven form fill — works for typical login forms
browser_fill_form(
  username field: input[type=email] OR input[name*=user] OR input[name=email],
  password field: input[type=password]
)
browser_click(button[type=submit] OR button:has-text("Sign in") OR button:has-text("Log in"))
browser_wait_for_network_idle(5s)

# Detect success
auth_state =
  IF current URL is no longer login_path AND no console error mentions auth: SUCCESS
  IF current URL still login_path AND console has error: FAILED
  OTHERWISE: AMBIGUOUS

IF auth_state == FAILED:
  blockers += { kind: "auth_failed", description: "{evidence excerpt}" }
  decisions_log += "auth attempt failed; skipping all requires_auth routes"
  # Continue to per-route loop; routes with requires_auth==true will be skipped there
```

---

## Per-Route Loop

```
start_ms = now()
probed_routes = []
browser_errors = []
budget_exhausted = false

FOR EACH route in route_inventory:
  elapsed_ms = now() - start_ms
  IF elapsed_ms > max_probe_seconds * 1000:
    budget_exhausted = true
    open_questions += {
      id: "OQ-budget-{NN}",
      type: "budget_exhausted",
      description: "max_probe_seconds reached after {N} routes; {M} routes not probed",
      impact: "smoke coverage incomplete"
    }
    BREAK

  IF route.requires_auth AND (auth_credentials_path unset OR auth_state == FAILED):
    decisions_log += "skipped {route.id} ({route.path}): requires_auth not satisfied"
    CONTINUE

  PROBE_RESULT = probe_one_route(route)
  probed_routes += PROBE_RESULT.probed
  browser_errors += PROBE_RESULT.errors

# Post-loop dedup
DEDUPLICATE browser_errors by (class, evidence) — keep first (highest-severity wins by insert order)
CAP browser_errors at 100 entries

UPDATE BROWSER_SMOKE_INDEX.probed_routes, browser_errors, decisions_log
UPDATE BROWSER_SMOKE_INDEX.budget.elapsed_ms = elapsed_ms
```

---

## `probe_one_route(route)`

Per-route procedure. Returns `{ probed: { route metadata + captures }, errors: [...] }`.

```
errors = []
full_url = runtime_url + route.path

# 1. Clear MCP state for this route
browser_clear_console_logs (when MCP supports it; otherwise reset by navigate)

# 2. Navigate
navigate_start = now()
RESPONSE = browser_navigate(full_url)
TRY:
  browser_wait_for_network_idle(timeout=5s)
  network_settled = true
EXCEPT TimeoutError:
  network_settled = false

# 3. Capture state
logs = browser_console_messages(level="error")
warnings = browser_console_messages(level="warning")
all_requests = browser_network_requests
http_status = RESPONSE.status (or infer from logs/network)

# 4. Run five detectors
errors += detect_http_error(route, http_status)
errors += detect_console_errors(route, logs, warnings)
errors += detect_network_anomalies(route, all_requests, network_settled)
errors += detect_css_sanity(route, all_requests)   # IF this is the first probed route
errors += detect_script_load_failures(route, all_requests)

# 5. Screenshot
screenshot_path = "{output_folder}/screenshots/{route.id}-{slug(route.path)}.png"
browser_take_screenshot(full_path=screenshot_path, fullPage=true)

# 6. Truncate captures for the index
probed = {
  id: route.id,
  path: route.path,
  full_url,
  http_status,
  screenshot_path,
  network_settled,
  console_logs_capture: logs[:20] + warnings[:5],
  network_requests_capture: select most informative 50 (status >= 400 first, then by time desc)
}

RETURN { probed, errors }
```

---

## Detector 1: http_error

```
detect_http_error(route, http_status):
  IF http_status >= 400 AND http_status < 600:
    severity = "high" IF http_status >= 500 OR http_status == 401 OR http_status == 403 ELSE "medium"
    suggested = (
      "server crash or unhandled exception"      IF 500 <= http_status < 600
      ELSE "auth required or denied"             IF http_status in (401, 403)
      ELSE "route not registered or misnamed"    IF http_status == 404
      ELSE "client-side request error"
    )
    RETURN [{
      class: "http_error", route_id: route.id, severity,
      evidence: "{route.path} returned HTTP {http_status}",
      suggested_root_cause: suggested
    }]
  RETURN []
```

---

## Detector 2: console_error

```
detect_console_errors(route, logs, warnings):
  errors = []
  FOR EACH log in logs:
    IF log.text matches /Uncaught.*Error|TypeError|ReferenceError|SyntaxError/i:
      errors += {
        class: "console_error", route_id: route.id, severity: "high",
        evidence: "console.error at {log.source}: {log.text[:200]}",
        suggested_root_cause: heuristic_from_message(log.text)
      }
    ELSE IF log.level == "error":
      errors += { ... severity: "medium" ... }
  
  # Warnings → only emit when matches a known critical-warning pattern
  FOR EACH w in warnings:
    IF w.text matches /CORS|Mixed Content|Mixed-content|insecure|deprecated.*will be removed/i:
      errors += {
        class: "console_error", route_id: route.id, severity: "medium",
        evidence: "console.warn at {w.source}: {w.text[:200]}",
        suggested_root_cause: "warning of compatibility/security concern"
      }
  
  RETURN errors

heuristic_from_message(msg):
  IF "Cannot read prop" OR "undefined is not" → "null/undefined access; defensive guard missing"
  IF "Failed to fetch" OR "NetworkError" → "API endpoint unreachable or CORS"
  IF "Hydration failed" → "SSR/CSR markup mismatch"
  IF "ChunkLoadError" → "stale bundle / cache eviction"
  ELSE → null
```

---

## Detector 3: network_anomaly

Three sub-detectors:

**3a. Redirect cycles**
```
hits_per_url = group all_requests by request.url, count
FOR EACH (url, count) in hits_per_url:
  IF count >= 3:
    matching = filter(all_requests, r => r.url == url)
    time_span = max(matching.start_time) - min(matching.start_time)
    IF time_span < 5000ms:
      errors += {
        class: "network_anomaly", route_id, severity: "high",
        evidence: "redirect cycle: {count} hits to {url} within {time_span}ms",
        suggested_root_cause: "auth redirect loop, router-state loop, or guarded route re-entry"
      }
```

**3b. Never-settling**
```
IF network_settled == false:
  pending_count = count of requests with no response yet
  errors += {
    class: "network_anomaly", route_id, severity: "medium",
    evidence: "network never reached idle within 5s; {pending_count} requests still pending",
    suggested_root_cause: "long-poll, websocket, or runaway async fetch"
  }
```

**3c. Failed XHR/fetch**
```
FOR EACH r in all_requests WHERE r.status >= 400 AND r.url != full_url (i.e. not the document itself):
  severity = "high" IF r.status >= 500 ELSE "medium"
  errors += {
    class: "network_anomaly", route_id, severity,
    evidence: "{r.method} {r.url} returned {r.status}",
    suggested_root_cause: (
      "API endpoint not implemented"     IF r.status == 404
      ELSE "server handler bug"          IF r.status >= 500
      ELSE "auth or input validation"
    )
  }
```

---

## Detector 4: css_sanity

Run ONLY on the first probed route (representative — repeating per route adds noise without signal).

```
detect_css_sanity(route, all_requests):
  IF route is not the first probed route: RETURN []
  
  errors = []
  
  # 4a. Raw CSS payload inspection
  css_requests = filter(all_requests, r => r.response_headers.content_type includes "text/css")
  FOR EACH css in css_requests:
    body = browser_evaluate("await fetch('{css.url}').then(r => r.text())")
    IF body matches /^@tailwind\s+(base|components|utilities)\s*;?\s*$/m:
      errors += {
        class: "css_sanity", route_id, severity: "high",
        evidence: "CSS payload {css.url} contains literal '@tailwind' directives — not processed",
        suggested_root_cause: "missing postcss.config.js OR Tailwind PostCSS plugin not in build chain"
      }
      RETURN errors  # one signal is enough
    
    IF body length < 200 AND body matches /@(tailwind|import)/:
      errors += {
        class: "css_sanity", route_id, severity: "high",
        evidence: "CSS payload {css.url} appears unprocessed (length {N}, contains @-directives)",
        suggested_root_cause: "build pipeline returning raw source instead of compiled CSS"
      }
      RETURN errors
  
  # 4b. Computed style sentinel
  body_font = browser_evaluate("getComputedStyle(document.body).fontFamily")
  body_font_lower = body_font.toLowerCase()
  
  # Browser defaults vary: "Times New Roman" (mac safari), "Times" (chrome on mac), "serif"
  IF body_font_lower in {"times", "times new roman", "serif"}:
    # Cross-check against project signals
    framework_signals = browser_evaluate("""
      Array.from(document.querySelectorAll('link[rel=stylesheet]')).map(l => l.href).join(',')
    """)
    project_uses_framework = (
      framework_signals includes "tailwind" OR
      framework_signals includes "bootstrap" OR
      framework_signals includes "/_next/static" OR
      framework_signals includes "/assets/index"
    )
    IF project_uses_framework:
      errors += {
        class: "css_sanity", route_id, severity: "medium",
        evidence: "body fontFamily is browser default ({body_font}) but stylesheets are loaded — styles not applied",
        suggested_root_cause: "stylesheet pipeline broken (PostCSS missing, CSS bundle not imported, or selectors mismatched)"
      }
  
  RETURN errors
```

---

## Detector 5: script_load_failure

```
detect_script_load_failures(route, all_requests):
  errors = []
  FOR EACH r in all_requests:
    IF r.url ends with /\.(m?js|tsx?|jsx?)$/ OR r.response_headers.content_type includes "javascript":
      
      # 5a. HTTP error on JS load
      IF r.status >= 400:
        errors += {
          class: "script_load_failure", route_id, severity: "high",
          evidence: "JS module {r.url} failed: HTTP {r.status}",
          suggested_root_cause: (
            "build output missing the file"            IF r.status == 404
            ELSE "build server crash or proxy issue"
          )
        }
      
      # 5b. MIME-type mismatch
      ELIF r.response_headers.content_type AND
           NOT (r.response_headers.content_type includes "javascript" OR
                r.response_headers.content_type includes "ecmascript"):
        errors += {
          class: "script_load_failure", route_id, severity: "high",
          evidence: "JS module {r.url} served with Content-Type: {r.response_headers.content_type}",
          suggested_root_cause: "MIME type misconfiguration — strict-MIME browsers will reject the module"
        }
  
  RETURN errors
```

---

## Source Fidelity Check (before writing)

- [ ] Every entry in `browser_errors` has all 5 fields (class, route_id, severity, evidence, suggested_root_cause)
- [ ] `class` is one of the 5 documented enum values
- [ ] `severity` is one of high | medium | low
- [ ] `evidence` is non-empty and quotes the actual observed signal
- [ ] Every entry in `probed_routes` corresponds to a route from `route_inventory` (route_id match)
- [ ] Routes with `requires_auth: true` AND no auth credentials are NOT in `probed_routes` (they're skipped, not silently failed)
- [ ] `screenshot_path` files exist on disk
- [ ] When `budget_exhausted == true`, `open_questions` registers it
- [ ] `network_requests_capture` and `console_logs_capture` are truncated per caps; full capture lives in MCP server logs only

## Post-Section Protocol

1. **Update** `BROWSER_SMOKE_INDEX.probed_routes`, `browser_errors`, `decisions_log`, `budget.elapsed_ms`, `blockers`, `open_questions`
2. **Update** `_progress.json`: `completed: 2`
3. **Flush** raw `all_requests` content per route (keep only truncated `network_requests_capture` rows)
4. **Verify** every error has a route_id matching a probed_routes entry
5. **Log:** `"Phase B COMPLETE. Probed {N} routes in {elapsed_ms}ms. Errors: {M} (high: {H}, medium: {M2}, low: {L}). Budget exhausted: {bool}"`
