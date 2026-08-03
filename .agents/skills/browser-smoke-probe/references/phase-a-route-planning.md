# browser-smoke-probe — Phase A: Route Planning

## Context Contract

- **Inputs:** Parameter `routes`, parameter `viewports`, parameter `max_routes`, optional `discovery_package_path`, optional `validated_test_cases_path`
- **Outputs:** `SMOKE_INDEX.route_plan[]`
- **Carries Forward:** `route_plan` (consumed by Phase B probe execution)
- **Flush After:** Raw discovery and test-case file content — keep only structured `route_plan` entries
- **Dependency:** Step 1 (Initialize) must be COMPLETE
- **H1 Title:** `# Phase A — Route Planning`

## Mode-Specific Behavior

- **BUILD:** Build route plan from operator + discovery + test-cases sources. Reserve nav-discovery for Phase B.
- **REPAIR — directive `route-plan` or `phase-a`:** Re-run planning. Preserve `routes_probed` from PRIOR_SMOKE except for routes no longer in the new plan.
- **REPAIR — directive `route:{path}` or `detector:{name}`:** Skip Phase A; reuse PRIOR_SMOKE.route_plan.

---

## Route Source Priority

```
SEED = ["/"]                                # always probe home
+ parameter routes                          # operator wins for explicit list
+ extracted from validated_test_cases_path  # if present
+ extracted from discovery_package_path     # if present
+ <nav-discovered at probe time>            # Phase B adds these dynamically
```

Each route's `source` field records its origin:
- `operator` — from `routes` parameter
- `validated_test_cases` — from web-discovery output
- `discovery` — from prototype-reverse-engineering output
- `nav-discovered` — added during Phase B by parsing anchor hrefs

Deduplicate by `path` (case-sensitive, normalised — trailing slashes stripped except for `/`).

---

## Extracting Routes from `validated_test_cases_path`

When `validated_test_cases_path` is set, the file/dir is the output of `web-discovery`
(structured selectors and validated journeys). Extract routes in this order:

```
IF validated_test_cases_path is a directory:
  SCAN for *.feature, *.json, *.md files
ELSE:
  TREAT as a single file

EXTRACT routes via these patterns (per file):
  - Gherkin "When user navigates to {url}" → extract path component
  - Gherkin "Given the user is on {page}" → match against route_map (when present)
  - JSON field "route": "/path/here"
  - JSON field "url": "{url}"  → parse path
  - Markdown link [Page X](/path/here)
  - Markdown line "Route: /path/here"

DEDUPLICATE the extracted set.
ORDER by occurrence (depth-first within each file).
```

---

## Extracting Routes from `discovery_package_path`

When `discovery_package_path` is set, the file/dir is the output of
`prototype-reverse-engineering`. The most authoritative source is the user-flows file
plus the selector inventory.

```
IF discovery_package_path is a directory:
  CANDIDATES = [
    discovery_package_path/deliverables/user-flows.mmd,
    discovery_package_path/deliverables/user-flows.md,
    discovery_package_path/deliverables/route-inventory.md,
    discovery_package_path/deliverables/selectors-inventory.md
  ]
ELSE:
  CANDIDATES = [discovery_package_path]

FOR EACH file in CANDIDATES that exists:
  EXTRACT routes via these patterns:
    - Mermaid flowchart node labels: "[Page: /students]" → /students
    - Mermaid flowchart edges: "A -->|navigate /enroll| B" → /enroll
    - Markdown headers "## Route: /path" → /path
    - Markdown tables with a "Route" or "URL" column → values from that column
    - Selector inventory entries citing a page: "Page: /dashboard" → /dashboard
```

Routes from discovery are typically more comprehensive than from test cases but may
include flows that the current build does not yet implement. Phase B probes will surface
404s naturally for unimplemented routes — that's a valid signal, not noise.

---

## Viewport Plan

The `viewports` parameter is a list of `label:WIDTHxHEIGHT` strings (e.g.,
`"desktop:1440x900"`, `"mobile:375x667"`, `"tablet:768x1024"`).

For each `(route, viewport)` pair, add one entry to `route_plan`:

```
FOR EACH route in ROUTES:
  FOR EACH viewport in viewports:
    route_plan += { path: route, source: <route_source>, viewport: viewport }
```

Total entries: `len(ROUTES) × len(viewports)`. This pair count must be capped at
`max_routes × len(viewports)` — exceeding this trims FIFO with a `decisions_log` entry.

---

## Trimming to max_routes

```
IF len(unique routes) > max_routes:
  KEEP first max_routes routes in order (operator → validated_test_cases → discovery)
  TRIMMED = remaining routes
  decisions_log += { phase: "phase-a", decision: "trimmed {len(TRIMMED)} routes to fit max_routes={max_routes}", evidence: "list of trimmed paths" }
```

Always preserve `/` as the first entry.

---

## Edge Cases

### Empty operator routes + no discovery/test-cases sources

`route_plan` is `["/"]` × viewports. Phase B will rely entirely on nav-discovery during
the probe of `/`.

### Routes with query strings

Strip query strings during deduplication BUT preserve them when probing (some routes
behave differently with `?returnUrl=...`). Example: `/login` and `/login?returnUrl=/admin`
are TWO distinct probe targets.

### Routes with hash fragments

Strip hash fragments before deduplication AND probing (the browser-smoke-probe walks
top-level routes, not single-page-app sub-views — hash routes typically rely on JS that
the probe doesn't drive interactively).

Exception: Vue/Ember legacy hash routing (`#/route`) — when detected (`<base href>` or
the discovery file declares hash mode), preserve the hash and include it in probe URLs.

### Auth-gated routes

If a route requires authentication, the probe will see a redirect to `/login` (or
similar). That's a valid finding — record the redirect chain. The probe does NOT
attempt to log in (out of smoke scope). Operators can pre-seed an auth session via
the MCP browser before invoking this skill if they want authenticated probing.

---

## Source Fidelity Check (before writing)

- [ ] `route_plan` is non-empty
- [ ] Every entry has `path`, `source`, `viewport` fields
- [ ] `/` appears at least once (as first entry)
- [ ] `source` values are in the allowed set: `operator`, `discovery`, `validated_test_cases`, `nav-discovered`
- [ ] Deduplication is correct: no duplicate `(path, viewport)` pairs
- [ ] When trimming was applied, `decisions_log` has the trim entry

## Post-Section Protocol

1. **Update** `SMOKE_INDEX.route_plan`, `decisions_log`
2. **Update** `_progress.json`: `completed: 1`
3. **Flush** raw discovery/test-case file content
4. **Verify** `route_plan` length matches expected `len(unique routes) × len(viewports)`
5. **Log:** `"Phase A COMPLETE. Routes: {R} unique, viewports: {V}, total probes: {R*V}, sources: {N from operator}/{M from discovery}/{K from test-cases}"`
