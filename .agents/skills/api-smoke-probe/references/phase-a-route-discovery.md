# api-smoke-probe — Phase A: Route Discovery

## Context Contract

- **Inputs:** `runtime_url`, optional `openapi_url_override`, optional `source_path`, parameter `routes`, parameter `max_routes`
- **Outputs:** `API_SMOKE_INDEX.route_plan[]`, `openapi_source`, `openapi_doc_path`
- **Carries Forward:** `route_plan` (consumed by Phase B probing)
- **Flush After:** Raw openapi.json blob (retain extracted paths + responses only)
- **Dependency:** Step 1 (Initialize) must be COMPLETE
- **H1 Title:** `# Phase A — Route Discovery`

## Mode-Specific Behavior

- **BUILD:** Discover routes via priority chain (operator → openapi-url → source-parse → root-only).
- **REPAIR — directive `phase-a` or `route-plan`:** Re-run discovery; replace `route_plan`.
- **REPAIR — other directives:** Skip; load `route_plan` from PRIOR_SMOKE.

---

## Discovery Priority Chain

```
1. Operator-supplied routes (parameter `routes`)         ← if non-empty, use exclusively
2. OpenAPI auto-discovery                                 ← preferred
3. Source-parse framework route decorators                ← fallback when no OpenAPI
4. Root-only probe                                        ← last resort
+ common health/info probes (always appended)
```

The operator's `routes` parameter is an explicit override. If non-empty, none of the
other sources contribute. This is intentional: when the operator already knows what to
probe (perhaps from `validated_test_cases_path` upstream), respect that.

---

## OpenAPI Auto-Discovery URLs

Probe these URLs in order; first 200 + valid JSON + contains `"paths"` wins:

```
{runtime_url}/openapi.json          ← FastAPI default
{runtime_url}/swagger.json           ← legacy Swagger
{runtime_url}/v3/api-docs            ← Spring Boot springdoc default
{runtime_url}/api-docs               ← NestJS Swagger module default
{runtime_url}/api/openapi.json       ← apps with /api prefix
{runtime_url}/api/docs/openapi.json  ← variant
```

If `openapi_url_override` is set, it is tried FIRST (and is the only URL when no
fallback discovery is wanted — though the chain still runs if it fails).

Each probe uses `--max-time 5` to avoid hanging. Skip silently on non-200.

When a candidate succeeds:
- Save the bytes to `{output_folder}/openapi.snapshot.json` (durable record for audit / REPAIR)
- Parse JSON
- Set `openapi_source = "openapi-url"` and `openapi_doc_path = the snapshot path`

---

## Parsing OpenAPI

The OpenAPI spec object has shape:
```
{
  "openapi": "3.0.x",
  "paths": {
    "/users": {
      "get": { "responses": { "200": {...}, "400": {...} } },
      "post": { ... }
    },
    "/users/{id}": { ... }
  }
}
```

Extract probable probe targets:
```
FOR EACH (path, methods) in spec.paths:
  FOR EACH method in methods.keys():
    IF method.lower() in ["get", "head"]:
      route_plan += {
        method: method.upper(),
        path: path,
        source: "openapi",
        openapi_responses: methods[method].get("responses", {})
      }
```

POST/PUT/DELETE/PATCH are listed in the spec but NOT probed (smoke is read-only). They
are tracked in `open_questions` as `non_probed_documented_routes` for transparency.

### Path templating

OpenAPI paths often contain `{id}` style placeholders. For probes:
- If the path contains `{var}`, substitute with `1` as a default (most APIs accept this for smoke)
- Record the substitution in `decisions_log`
- A 404 on `/users/1` is a valid smoke result — record it. Severity is `medium`, not `high`
  (the route exists; the specific record doesn't).

---

## Source-Parse Fallback (when no OpenAPI is exposed)

When OpenAPI auto-discovery returns nothing AND `source_path` is set, parse source
files for route decorators.

### NestJS
```
GLOB {source_path}/src/**/*.controller.ts (and .controller.js)
PATTERNS:
  @Controller('{prefix}')              → captures controller prefix
  @Get()                                → captures '/'
  @Get('{sub-path}')                    → captures sub-path
  @Get(':id')                           → captures /:id
COMPOSE final path = controller_prefix + method_path (handling leading/trailing slashes)
```

### FastAPI
```
GLOB {source_path}/**/*.py
PATTERNS:
  @app.get("{path}")
  @router.get("{path}")
  @app.api_route("{path}", methods=["GET"])
```

### Spring Boot
```
GLOB {source_path}/src/main/java/**/*.java (and .kt)
PATTERNS:
  @RequestMapping("{base-path}")        → class-level prefix
  @GetMapping("{sub-path}")
  @GetMapping(value = "{sub-path}")
  @RequestMapping(value = "{sub-path}", method = RequestMethod.GET)
```

### Flask
```
GLOB {source_path}/**/*.py
PATTERNS:
  @app.route("{path}")                  → defaults to GET
  @app.route("{path}", methods=["GET"])
  @blueprint.route("{path}")
```

### Django
```
GLOB {source_path}/**/urls.py
PATTERNS:
  path("{path}", ...)
  re_path(r"^{path}$", ...)
```

### Rails
```
GLOB {source_path}/config/routes.rb
PATTERNS:
  get "{path}", to: ...
  resources :{resource}                  → expand to /:resource and /:resource/:id GETs
```

### Express
```
GLOB {source_path}/**/*.js,*.ts (excluding node_modules)
PATTERNS:
  app.get("{path}", ...)
  router.get("{path}", ...)
  app.use("{prefix}", routerWith)        → records prefix for prefix-merge
```

Add each extracted route with `source: "source-parse"`. If no source files yielded
matches, fall through to root-only.

---

## Common Health/Info Probes (always appended)

Even when discovery succeeded, append these probes if not already present:

```
common_probes = [
  "/health",
  "/healthz",
  "/api/health",
  "/ready",
  "/readyz",
  "/metrics",
  "/"
]
```

These commonly exist on production-grade services and reveal a lot about service
health. A 404 on `/health` is recorded as `low` severity (not all services expose it).
A 200 is normal. A 500 on `/health` is `fatal` (service is reporting unhealthy).

---

## max_routes Trimming

```
IF len(route_plan) > max_routes:
  PRIORITY ORDER for keeping:
    1. operator-supplied routes (always keep all)
    2. openapi routes in declaration order
    3. source-parse routes in file order
    4. common-probe routes (`/health` first, then `/`, then others)
  TRIMMED = entries beyond max_routes in the above priority
  decisions_log += { phase: "phase-a", decision: "trimmed {N} routes to fit max_routes={max_routes}", evidence: "list of trimmed routes" }
```

---

## Source Fidelity Check (before writing)

- [ ] `route_plan` is non-empty
- [ ] Every entry has `method ∈ {GET, HEAD}`, `path` (starts with `/`), `source ∈ {operator, openapi, source-parse, common-probe, default}`
- [ ] `openapi_source` matches the actual source used
- [ ] If `openapi_doc_path` is set, the file exists on disk
- [ ] No duplicate `(method, path)` pairs
- [ ] When trimmed, `decisions_log` has the trim entry
- [ ] Path-template substitutions recorded in `decisions_log`

## Post-Section Protocol

1. **Update** `API_SMOKE_INDEX.route_plan`, `openapi_source`, `openapi_doc_path`, `decisions_log`
2. **Update** `_progress.json`: `completed: 1`
3. **Flush** raw openapi.json content (keep extracted paths + responses only)
4. **Verify** route count, source distribution
5. **Log:** `"Phase A COMPLETE. Routes: {N} (operator: {O}, openapi: {P}, source-parse: {S}, common: {C}), source: {openapi_source}"`
