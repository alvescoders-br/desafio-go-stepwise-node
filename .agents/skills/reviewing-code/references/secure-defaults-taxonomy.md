# Secure-Defaults Defect Taxonomy

Read this reference at **Step 4.7 (Secure-Default Verification)** and again at
**Step 5** for the deterministic signals. Every defect class here is a
**generated-code security defect that recurs because the convenient default is
the insecure one** — not an exotic exploit. The reviewer's job is to flag the
insecure default, not to teach the concept.

These classes are **technology-agnostic**. The `signal` column gives example
patterns to seed a grep/AST search; adapt them to the stack under review. A hit
on the signal is a *candidate* — confirm the defect against the code
(Zero-Invention) before it enters `FINDING_LOG`.

---

## The one rule that governs every class below

> **Insecure defaults ship.** "It's only for local/dev" is NOT a severity
> downgrade. A default value, a fallback branch, or a bypass that is reachable
> when configuration is absent, wrong, or partial IS the production behavior the
> day someone deploys without the config — which is exactly what happens. A
> defect does not become acceptable because a comment next to it says
> `// dev only` or `// mock mode`. If the safe behavior depends on an env var,
> flag, or file being present, the code must **fail closed** when it is absent.

Rationalizations that do NOT lower severity (do not accept any of these as a
reason to downgrade or skip a finding): "non-production", "local only", "mock
mode", "temporary", "the installer sets it", "it's behind auth in prod", "the
comment already notes it", "documented as a known limitation".

---

## Defect Classes

Severity is **fixed** per class. `SD-01…SD-06` are **BLOCKING** (fail-open or
credential-exposure defaults). `SD-07…SD-10` are **HIGH** unless the finding
also satisfies a BLOCKING class, in which case it is BLOCKING.

| id | class | severity | what to flag | example signal (adapt to stack) |
|----|-------|----------|--------------|---------------------------------|
| **SD-01** | Auth/authz fails open | BLOCKING | An authentication or authorization check that **grants access when its config is missing, empty, or unparseable** — e.g. "if the JWKS/issuer/secret is not set, accept any token/cookie". The safe form rejects (fail closed) and, in a production build, refuses to start. | `if (!process.env.*SECRET*` / `*ISSUER*` / `*JWKS*`)` near a `return NextResponse.next()` / `allow` / `authenticated = true`; `== 'local-dev'`; any auth branch guarded by env presence with the permissive branch on absence |
| **SD-02** | Dev/mock bypass reachable in production | BLOCKING | A bypass, mock identity, seeded token, or debug backdoor whose only guard is the **absence** of config (not an explicit `NODE_ENV/APP_ENV === 'production'` deny). Also: a login/bypass helper committed under a web-served path (`public/`, `static/`, `www/`). | `mock`, `bypass`, `backdoor`, `test-user`, `local-dev`, `x-debug`, `impersonate`; helper files under `public/`, `static/` matching `login`/`admin`/`auth` |
| **SD-03** | Secrets written unencrypted / world-readable at rest | BLOCKING | Credentials, tokens, or private keys written to a file **without a restrictive mode** and/or under a **shared/temp path** (`/tmp`, world-readable dir). The safe form writes outside shared dirs with owner-only permissions (e.g. `0600`) and, where the platform supports it, encrypts at rest. | writes to `/tmp/`, `os.tmpdir()`, `/var/tmp/` of anything named `*token*`/`*secret*`/`*credential*`/`*vault*`; `writeFile`/`open(...,'w')` of secrets with no adjacent `chmod`/`mode: 0o600`/`0600` |
| **SD-04** | Secret material duplicated across multiple sinks | BLOCKING | The same credential copied verbatim into **more than one** config/file/env sink by generated or installer code (each copy is a leak surface), especially without restrictive permissions on the files written. The safe form has one canonical secret store referenced by the others. | an installer/`install.*` that writes the same `*_TOKEN`/`*_KEY`/`*_SECRET` into ≥2 of: `*.json` config, `.env*`, home-dir dotfiles, project files; no `chmodSync(..., 0o600)` after write |
| **SD-05** | Secret written without tightening file permissions | BLOCKING | Any code that writes a file containing a secret and does **not** set owner-only permissions immediately after (regardless of directory). Distinct from SD-03: this fires even outside `/tmp`. | `writeFile`/`writeFileSync`/`open(...,'w')` of secret-bearing content with no `chmod`/`fchmod`/`mode` argument in the same block |
| **SD-06** | Secrets committed / not ignored | BLOCKING | A generated `.env.local`, `mcp.json`, credentials file, or key that is not covered by `.gitignore`, or a secret literal hardcoded in tracked source. `.gitignore` alone is fragile (`git add -f`); prefer that the generator also writes to paths outside the repo. | secret-bearing filenames absent from `.gitignore`; long high-entropy string literals assigned to `*key*`/`*secret*`/`*token*` in tracked files |
| **SD-07** | Auth-bearing cookie/token without protective flags | HIGH | A session/auth cookie set without `HttpOnly` **and** `Secure` (and a sane `SameSite`), or a bearer token placed where script can read it. BLOCKING when the same cookie is also the sole auth credential accepted by a privileged route (compounds with SD-01). | `Set-Cookie`/`cookies.set(` for `*token*`/`*session*`/`*auth*` missing `httpOnly`/`secure`; auth token written to `localStorage` |
| **SD-08** | Privileged endpoint without authn/authz or rate limiting | HIGH | An admin/credentials/privileged route that is unauthenticated, unauthorized, or has **no throttling** on a credential-checking path (brute-force surface). The safe form authenticates, authorizes, and rate-limits. | route files under `*/admin/*`, `*/credentials/*`, `*/internal/*` with no auth middleware/guard in the handler and no rate-limit/limiter call |
| **SD-09** | Audit/security log that cannot survive or observe what it claims | HIGH | An audit or security-event log that is **in-memory only**, written to a store the enforcement path cannot reach, or lost on restart — while the code/spec claims durable auditing. Flag the gap between the claim and the sink. | `auditLog`/`securityEvent` pushed to an in-process array/`Map`/module singleton with no durable sink (db/file/service); a comment admitting events are dropped or go to a separate bundle |
| **SD-10** | Secret with no rotation / no canonical source | HIGH | A generated shared secret (`CRON_SECRET`, signing key, webhook secret) that exists only inside generated configs with no canonical store or rotation path — regeneration silently desyncs consumers. | generated `*_SECRET`/`*_KEY` present only in emitted config files, no reference to a secret manager / canonical env source |

---

## How to apply (Step 4.7)

```
READ this taxonomy.
DETERMINE the security surface of SCOPE: does any file in review touch
  authentication/authorization, secret/credential handling, session/cookie
  issuance, a privileged or admin endpoint, persistence of sensitive data,
  or code that writes files/config a secret flows into?

IF no security surface exists in SCOPE:
  LOG: "Secure-default verification: no security surface in scope."
  SKIP the class checks (do NOT invent findings).

ELSE FOR each defect class SD-01..SD-10:
  1. Run the class signal against SCOPE (grep/AST) — see Step 5 for the
     deterministic subset. Signals are seeds, not verdicts.
  2. For each candidate, CONFIRM against the actual code (read it; a signal
     hit inside a genuinely production-guarded branch is not a defect).
  3. Do NOT downgrade on any rationalization listed above.
  4. On a confirmed defect, ADD to FINDING_LOG:
       {
         type: "FAIL",
         severity: "<fixed severity for the class>",
         category: "SECURE_DEFAULT_<SD-id>",
         file: "<path>", line: "<range>",
         description: "<what fails open / what leaks>",
       }
     with the REPAIR feedback quality fields (BEFORE/AFTER/verification hint)
     from references/severity-taxonomy.md. The AFTER snippet must show the
     fail-closed / restricted-permission / durable-sink form.
```

## Deterministic subset (run at Step 5)

SD-01, SD-02 (helper-under-public path), SD-03, SD-05, SD-06 (gitignore
coverage), and SD-07 (cookie flags) have **exactly-checkable** signals — they are
grep/AST facts, not judgment calls. Run them as security-category tool checks in
Step 5 so a persuasive "it's fine for dev" narrative cannot suppress them: the
signal fires mechanically, then you confirm and classify. SD-08, SD-09, SD-10
require reading intent and stay in the Step 4.7 judgment pass.

A confirmed BLOCKING secure-default defect makes `review_status = FAILED`
(blocking_count ≥ 1), which the code-review verdict gate routes back to
`implementation` in REPAIR — the defect never reaches the human gate unflagged.
