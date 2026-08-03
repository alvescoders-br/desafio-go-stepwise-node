# browser-smoke-probe — Phase B: Probe Execution

## Context Contract

- **Inputs:** `SMOKE_INDEX.route_plan`, `SMOKE_INDEX.runtime_url`, `SMOKE_INDEX.mcp_server`, parameter `max_probe_seconds`
- **Outputs:** `SMOKE_INDEX.routes_probed[]`, `SMOKE_INDEX.browser_errors[]`, `SMOKE_INDEX.smoke_route_inventory[]`, `SMOKE_INDEX.browser_status`
- **Carries Forward:** All probe results
- **Flush After:** Raw network request bodies, full console logs, large screenshot binaries — keep only structured detector findings
- **Dependency:** Phase A must be COMPLETE
- **H1 Title:** `# Phase B — Probe Execution`

## Mode-Specific Behavior

- **BUILD:** Probe every entry in `route_plan` until `max_probe_seconds` reached.
- **REPAIR — `route:{path}` directive:** Filter route_plan to entries matching path; re-probe those.
- **REPAIR — `detector:{name}` directive:** Re-run only the named detector across routes_probed; load existing detectors from PRIOR_SMOKE for the other 4.
- **REPAIR — `full`/`global`:** Re-probe everything.

---

## Per-Probe MCP Call Sequence

For each `probe_target` in the filtered probe list:

```
# 1. Resize to viewport
parse "{label}:{W}x{H}" → width, height, label
CALL: browser_resize(width=W, height=H)
       (playwright: mcp__playwright__browser_resize)
       (web-inspector: mcp__mcp-web-inspector__measure_element is NOT this — use evaluate to set window size)

# 2. Clear prior state
CALL: clear_console_logs                                # web-inspector
   OR browser_evaluate("console.clear(); performance.clearResourceTimings()")  # playwright

# 3. Navigate
CALL: browser_navigate(url = runtime_url + probe_target.path)
       (playwright: mcp__playwright__browser_navigate)
       (web-inspector: mcp__mcp-web-inspector__navigate)
CAPTURE: navigation start timestamp

# 4. Wait for network idle (bounded)
CALL: wait_for_network_idle(maxInflightRequests=0, timeout=5000)
CAPTURE: settled / timed_out flag
CAPTURE: navigation end timestamp; load_time_ms = end - start

# 5. Collect data
network_requests = list_network_requests()
console_logs = get_console_logs(level=error AND level=warning)

# 6. Run detectors (see detector rules below)

# 7. Screenshot
screenshot_filename = "{hash(probe_target.path)}-{viewport_label}.png"
CALL: browser_take_screenshot(filename=output_folder/screenshots/screenshot_filename, fullPage=true)

# 8. Inventory (for downstream QE)
testid_count = browser_evaluate("document.querySelectorAll('[data-testid]').length")
anchors = browser_evaluate("[...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'))")
```

When `max_probe_seconds` is reached mid-loop, BREAK and record the early-exit in
`decisions_log`. Any entries not yet probed are listed in `open_questions` with kind
`probe_skipped_timeout`.

---

## Detector 1 — http_error

For each request in `network_requests`:

```
IF req.status >= 400:
  severity =
    "fatal"  IF req is the document request (the page itself returned 4xx/5xx) OR req.status >= 500
    "high"   IF req.url contains "/api/" OR req.url matches XHR pattern
    "medium" IF req.url contains "/static/" OR is a non-critical asset
    "low"    otherwise

  entry = {
    url: req.url,
    method: req.method,
    status: req.status,
    severity: severity,
    initiator: req.initiator,
    evidence: "{method} {url} returned {status}",
    suggested_root_cause: see lookup below
  }

  suggested_root_cause lookup:
    status 500 + url contains /api/  → "server-side exception in handler; check launching-app's runtime.log around this timestamp"
    status 404 + url contains /api/  → "missing route handler or wrong base path; verify the controller is registered"
    status 401 / 403                  → "auth gate; the probe is not authenticated. Either pre-seed an auth session via MCP or treat as expected for protected routes."
    status 404 + url is a script/css  → "build pipeline missing the asset; check vite/webpack output dir and manifest"
    status 502 / 503 / 504            → "upstream service unreachable (DB? Redis?); check bootstrapping-runtime-environment services_running"
    status 400 (Bad Request) on document load → "client sending malformed request; usually due to missing required headers"

  detectors.http_error += entry
```

---

## Detector 2 — console_error

For each entry in `console_logs`:

```
IF log.type == "error":
  severity = "high"   IF log.message matches /TypeError|ReferenceError|SyntaxError|Uncaught/
  severity = "fatal"  IF log.message matches /Failed to fetch|NetworkError|Loading chunk \d+ failed/

  entry = {
    message: log.message,
    source: log.source (file + line if available),
    line: log.lineNumber,
    severity: severity,
    evidence: "console.error: {first 200 chars of message}",
    suggested_root_cause: see lookup
  }

  suggested_root_cause lookup:
    /Cannot read properties of (null|undefined)/  → "null pointer in client code; check the line cited in source — typically missing data from API call that failed silently"
    /TypeError: .* is not a function/             → "API contract mismatch or import error; verify the imported member exists"
    /ReferenceError: .* is not defined/           → "missing import or build excluded the module"
    /Loading chunk \d+ failed/                    → "stale service worker or asset cache; OR the build output is missing chunks"
    /Failed to fetch/                             → "CORS, network, or backend service unreachable; cross-check with http_error detector"
    /Hydration failed|Text content does not match/→ "SSR/CSR mismatch; server-rendered HTML differs from client render"

  detectors.console_error += entry

IF log.type == "warning":
  IF log.message matches /deprecation|will be removed/: SKIP (noise filter)
  ELIF log.message matches /CORS|Mixed Content|Insecure/:
    severity = "medium"
    entry = (similar shape, with suggested_root_cause "security policy mismatch; check CORS config or upgrade resource to HTTPS")
    detectors.console_error += entry
```

---

## Detector 3 — network_anomaly

### 3a — Redirect loop

```
url_hit_counts = group network_requests by URL within last 8 seconds, count hits per URL
FOR EACH (url, count) in url_hit_counts:
  IF count >= 3:
    IF url path matches probe_target.path OR redirects between 2 URLs that both belong to the same auth flow:
      severity = "fatal"
      entry = {
        kind: "redirect_loop",
        url: url,
        count: count,
        severity: severity,
        evidence: "{count} requests to {url} within 8s",
        suggested_root_cause: "redirect cycle — typically a guard that redirects to /login when on /login. Look for client-side auth interceptors that don't check current path before redirecting."
      }
      detectors.network_anomaly += entry
```

### 3b — Never-settled page

```
IF wait_for_network_idle timed out (5s without idle):
  long_polling_count = count of pending XHR/fetch requests at timeout
  entry = {
    kind: "never_settled",
    severity: "high"  IF long_polling_count >= 3 ELSE "medium",
    evidence: "page did not reach network idle within 5s; {long_polling_count} requests still in flight at timeout",
    suggested_root_cause: "client polling loop OR infinite request retries OR websocket upgrade failures. Check the in-flight request URLs in network_requests."
  }
  detectors.network_anomaly += entry
```

### 3c — Mixed redirect chains

```
document_redirects = trace the document request chain
IF chain length >= 4:
  entry = {
    kind: "long_redirect_chain",
    chain: [list of URLs],
    severity: "medium",
    evidence: "document redirect chain: {url1} → {url2} → {url3} → ... ({N} hops)",
    suggested_root_cause: "long redirect chain may indicate misconfigured base path, https-upgrade middleware, or auth flow with multiple bounces. Verify each redirect is necessary."
  }
  detectors.network_anomaly += entry
```

---

## Detector 4 — css_sanity

### 4a — Raw CSS payload check

```
css_responses = filter network_requests where Content-Type contains "text/css"
FOR EACH css_resp in css_responses:
  body_excerpt = first 500 bytes of response body
  IF body_excerpt contains "@tailwind " (with space — to avoid false positive on "@tailwindcss"):
    entry = {
      kind: "css_not_compiled",
      url: css_resp.url,
      severity: "high",
      evidence: "CSS response from {url} contains literal '@tailwind base;' — directives not processed by PostCSS",
      suggested_root_cause: "missing postcss.config.js or tailwind.config.js content paths misconfigured. Add postcss.config.js with tailwindcss + autoprefixer plugins."
    }
    detectors.css_sanity += entry
  IF body_excerpt contains "@apply" (literal):
    entry = (similar with kind: "css_apply_unprocessed")
    detectors.css_sanity += entry
```

### 4b — Computed-style sentinel

```
sentinel_styles = browser_evaluate("""
  ({
    bodyFont: getComputedStyle(document.body).fontFamily,
    bodyBg: getComputedStyle(document.body).backgroundColor,
    h1Color: document.querySelector('h1') ? getComputedStyle(document.querySelector('h1')).color : null,
    distinctClassesCount: document.styleSheets ? [...document.styleSheets].reduce((acc, s) => { try { return acc + s.cssRules.length; } catch (e) { return acc; } }, 0) : 0
  })
""")

IF sentinel_styles.bodyFont in ["Times New Roman", "serif", "Times"]:
  AND sentinel_styles.distinctClassesCount < 50:
    entry = {
      kind: "styles_not_applied",
      severity: "high",
      evidence: "body font-family: '{bodyFont}', stylesheet rule count: {distinctClassesCount}",
      suggested_root_cause: "page renders with browser default styles. CSS bundle either missing, blocked, or unprocessed. Check the @tailwind directive in served CSS (Detector 4a) and verify the build outputs processed CSS."
    }
    detectors.css_sanity += entry
```

### 4c — Overflow extreme

```
body_metrics = browser_evaluate("""
  ({
    scrollHeight: document.body.scrollHeight,
    scrollWidth: document.body.scrollWidth,
    viewportH: window.innerHeight,
    viewportW: window.innerWidth
  })
""")

IF body_metrics.scrollHeight > body_metrics.viewportH * 20:
  AND body_metrics.scrollHeight > 5000:  # avoid false positive on legit long pages
    entry = {
      kind: "overflow_extreme",
      severity: "medium",
      evidence: "body.scrollHeight={scrollHeight}px vs viewport={viewportH}px (ratio {scrollHeight/viewportH:.1f}x)",
      suggested_root_cause: "extreme vertical overflow suggests unstyled content (giant images, unconstrained SVG, missing layout container). Combine with css_not_compiled finding for high confidence."
    }
    detectors.css_sanity += entry
```

---

## Detector 5 — script_load_failure

```
FOR EACH req in network_requests where Content-Type contains "javascript" OR url ends with ".js":
  IF req.status >= 400:
    entry = {
      kind: "asset_404" IF req.status == 404 ELSE "asset_error",
      url: req.url,
      status: req.status,
      severity: "fatal" IF req.status == 404 ELSE "high",
      evidence: "{method} {url} returned {status}",
      suggested_root_cause: "missing JS asset; check build output dir, asset manifest, and vite/webpack base path"
    }
    detectors.script_load_failure += entry

# Console-based module errors
module_errors = filter console_logs for /Cannot find module|Failed to resolve module|404 .*\.(js|mjs)/
FOR EACH e in module_errors:
  entry = {
    kind: "module_not_found",
    message: e.message,
    severity: "fatal",
    evidence: "console.error: {first 200 chars}",
    suggested_root_cause: "import path mismatch in source code, OR module not in package.json, OR tsconfig paths misconfigured"
  }
  detectors.script_load_failure += entry
```

---

## Aggregation: browser_errors[]

After all detectors run per route, flatten into a single cross-route error list:

```
FOR EACH routes_probed entry:
  FOR EACH detector_name in [http_error, console_error, network_anomaly, css_sanity, script_load_failure]:
    FOR EACH item in routes_probed_entry.detectors[detector_name]:
      browser_errors += {
        detector: detector_name,
        route: routes_probed_entry.path,
        viewport: routes_probed_entry.viewport,
        severity: item.severity,
        evidence: item.evidence,
        suggested_root_cause: item.suggested_root_cause
      }

DEDUPLICATE browser_errors by (detector, evidence) — keep first occurrence
SORT by severity (fatal → high → medium → low) then by route
```

---

## browser_status Derivation

```
IF any browser_errors entry has severity in {fatal, high}: browser_status = FAIL
ELIF browser_errors is empty: browser_status = PASS
ELSE: browser_status = PASS  # medium/low tolerated as warnings, do not block fix loop
```

---

## Source Fidelity Check (before writing)

- [ ] Every `routes_probed` entry has `detectors {}` with all 5 keys (arrays, may be empty)
- [ ] Every `browser_errors` entry has `detector`, `route`, `severity`, `evidence`, `suggested_root_cause`
- [ ] `browser_status` matches the derivation rule
- [ ] Screenshots exist on disk for every successfully probed route (verify with stat)
- [ ] `smoke_route_inventory` row count matches `routes_probed` row count
- [ ] When `max_probe_seconds` triggered early exit, `decisions_log` has the entry AND `open_questions` lists skipped routes

## Post-Section Protocol

1. **Update** `SMOKE_INDEX.routes_probed`, `browser_errors`, `smoke_route_inventory`, `browser_status`, `decisions_log`
2. **Update** `_progress.json`: `completed: 2`
3. **Flush** raw network/console payloads (keep only structured detector entries)
4. **Verify** screenshot files exist; `browser_status` matches rule
5. **Log:** `"Phase B COMPLETE. Routes probed: {N}, errors: {M} (fatal: {F}, high: {H}, medium: {M}, low: {L}), browser_status: {status}"`
