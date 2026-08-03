# browser-smoke-probe — Phase A: Route Selection

## Context Contract

- **Inputs:** `BROWSER_SMOKE_INDEX.runtime_url`, parameters `max_routes`, `discovery_package_path` (optional), `validated_test_cases_path` (optional), `auth_credentials_path` (optional)
- **Outputs:** `BROWSER_SMOKE_INDEX.route_inventory[]`, entries in `decisions_log`
- **Carries Forward:** `route_inventory[]` (consumed by Phase B probe loop)
- **Flush After:** Raw user-flows.mmd content, test-case file contents — keep only structured `route_inventory` rows
- **Dependency:** Step 1 (Initialize + Reachability) must be COMPLETE
- **H1 Title:** `# Phase A — Route Selection`

## Mode-Specific Behavior

- **BUILD:** Run full source-aware selection.
- **REPAIR — directive `routes` or `phase-a`:** Re-select. Preserve `probed_routes` if any from PRIOR_SMOKE.
- **REPAIR — directive `single-route:{id}`:** Skip — Phase A just preserves the prior route_inventory and Phase B restricts to the targeted id.

---

## Route Source Priority (decreasing)

| Source | Priority | When |
|---|---|---|
| `homepage` | 1 | Always include `/` |
| `homepage` (auth landing) | 1 | When `auth_credentials_path` is set: add `/login` and primary post-auth landing |
| `user-flows.mmd` | 2 | When `discovery_package_path` is set and the file exists |
| `selectors-inventory` | 2 | When `discovery_package_path/selectors-inventory.md` exists |
| `validated_test_cases` | 2 | When `validated_test_cases_path` is set |
| `mainnav` (anchor discovery) | 3 | Fill remaining slots up to `max_routes` |

**Tie-break:** within same priority, prefer routes that don't `requires_auth` (probe public routes first; auth flow ordering matters because the smoke probe authenticates ONCE at the top of Phase B).

---

## Source: user-flows.mmd

`prototype-reverse-engineering` produces a Mermaid user-flow catalog. Pages declared
as nodes typically use this pattern:

```
graph TD
  Home[/] --> Login[/login]
  Login --> Dashboard[/dashboard]
  Dashboard --> Students[/students]
  Students --> StudentDetail[/students/:id]
```

Extraction rule:
- Each node label between `[` and `]` is a route path
- Parameterised paths like `/students/:id` are kept as-is — the probe substitutes
  a default placeholder value (`/students/1` for `:id`, `/items/test` for `:slug`)
- Skip nodes that look like modal labels (`[Confirm Modal]` — no leading `/`)

After parsing, add each unique path to `route_inventory` with `source: "user-flows.mmd"`.

When the file does not exist OR parses to zero routes, log:
```
decisions_log += {
  phase: "phase-a",
  decision: "user-flows.mmd absent or empty; falling back to mainnav discovery",
  evidence: "discovery_package_path scan"
}
```

---

## Source: selectors-inventory.md

If `discovery_package_path/selectors-inventory.md` exists, parse for `route:` fields
or markdown headings of the form `## Route: /xxx`. Add to `route_inventory` with
`source: "selectors-inventory"`.

---

## Source: validated_test_cases

`web-discovery` produces validated test cases with selectors and routes. The TCs
typically declare a `route` or `url` field per scenario. Extract those.

```
LOAD validated_test_cases_path
FOR EACH file matching *.{json,yaml,md}:
  PARSE for fields: route | url | path
  ADD unique paths to route_inventory
```

Mark `requires_auth: true` if the TC declares an auth-gated scenario.

---

## Source: mainnav anchor discovery

Only run when the above sources produce fewer than `max_routes` routes:

```
browser_navigate(runtime_url)
browser_wait_for_network_idle(2s)

candidate_hrefs = browser_evaluate("""
  Array.from(document.querySelectorAll(
    'nav a, header a, [role=\"navigation\"] a, aside a'
  )).map(a => a.getAttribute('href'))
   .filter(h => h && h.startsWith('/') && !h.includes('#'))
""")

# Deduplicate; cap at remaining budget
needed = max_routes - len(route_inventory)
new_paths = unique(candidate_hrefs)[:needed]

FOR EACH path in new_paths:
  route_inventory += {
    id: "r-{NNN}",
    path,
    source: "mainnav",
    priority: 3,
    requires_auth: false  # presence on public nav strongly suggests no auth, but the probe will surface 401 if wrong
  }
```

---

## Source: anchor-from-{path}

This is an OPTIONAL escalation: after probing a route, the probe may discover
additional in-page anchors and add them to the queue. Disabled by default — the
parent capability's `max_routes` cap prevents unbounded crawl. When enabled in a
future iteration, the source label becomes `anchor-from-{originating-path}`.

For v1.0 this is not used. Document it here so the source enum is complete.

---

## ID Format

Route IDs follow `r-{NNN}` zero-padded to 3 digits:

- `r-001` → always the root `/`
- `r-002`+ → in priority order, with insertion order within same priority

When REPAIR adds a single route post-hoc, increment the highest existing id by 1.

---

## Cap & Order

```
SORT route_inventory BY (priority ASC, source_rank ASC, insertion_order ASC)
TRUNCATE to max_routes entries
RE-NUMBER ids r-001..r-N in the final sorted order

# source_rank ordering: homepage < user-flows.mmd < selectors-inventory < validated_test_cases < mainnav
```

When truncation drops routes, log:
```
decisions_log += {
  phase: "phase-a",
  decision: "{K} candidates dropped by max_routes={N} cap",
  evidence: "route inventory before truncation"
}
```

---

## Source Fidelity Check (before writing)

- [ ] Every entry in `route_inventory` has all 5 fields (id, path, source, priority, requires_auth)
- [ ] Every `source` value is one of the documented enum values
- [ ] Every `path` starts with `/`
- [ ] No duplicate paths
- [ ] `len(route_inventory) <= max_routes`
- [ ] Decisions for fallback / truncation are recorded in `decisions_log`
- [ ] When `auth_credentials_path` is unset, no entry has `requires_auth: true` unless the source explicitly tagged it that way (the probe will skip those)

## Post-Section Protocol

1. **Update** `BROWSER_SMOKE_INDEX.route_inventory`, `decisions_log`
2. **Update** `_progress.json`: `completed: 1`
3. **Flush** raw user-flows/selectors/TC file content from memory
4. **Verify** route_inventory has at least one entry (root); if empty, that's a blocker
5. **Log:** `"Phase A COMPLETE. {N} routes selected. Sources: {distinct labels}"`
