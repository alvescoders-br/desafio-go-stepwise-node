# Angular — DTR Field Reference

Use this file when the ASD describes a web frontend built with Angular.

---

## General Category

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Language | TypeScript | 5.x | Angular is TypeScript-first; never list as JavaScript |
| Framework | Angular | 18 | Always include the major version; prefix with `Angular` (not `AngularJS`, which is legacy v1) |
| State Management | NgRx | 18 | Or `NGXS` (3.x), `Akita`, `Angular Signal Store` (NgRx 17+ signals), `Angular Services (built-in)` |
| i18n / l10n | @angular/localize | — | Built-in; use `@angular/localize (built-in)`; or `transloco` for runtime i18n |
| Auth Handling | @azure/msal-angular | — | Or `angular-auth-oidc-client`, `Auth0 Angular SDK`, `Keycloak Angular` |
| Marketing Analytics | Google Analytics | SaaS | Or `Mixpanel`, `Segment`, `Amplitude`; omit if none |
| Data Fetching | HttpClient | — | Built-in to Angular; use `HttpClient (built-in)`; for caching: `TanStack Query Angular` |
| Search UI | Algolia | SaaS | Or `Typesense`; omit if no search |
| Real-time | Socket.IO client | 4.x | Or `SignalR client` (Microsoft), `Ably`, `native WebSocket` |
| Offline Support | @angular/service-worker | — | Built-in PWA support; or `Workbox` |
| Data Compliance (UI) | OneTrust | SaaS | Or `Cookiebot`; omit if no cookie consent |
| CMS Integration | Contentful | SaaS | Or `Sitecore`, `AEM Headless`; omit if no CMS |
| Unit Testing | Jest | 29.x | Or `Vitest` (Angular 16+ compatible), `Karma + Jasmine` (legacy — note if migrating) |

---

## Project & Design Category

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| CSS Approach | Angular Material + SCSS | 18 | Or `PrimeNG`, `Tailwind CSS`, `Bootstrap`, `Nebular`; Angular Material is the most common |
| Component Docs | Storybook | 8.x | Or `Compodoc` (API docs generator); omit if no component docs |

---

## Build, Tooling & Deployment Category

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Version Control | GitHub | SaaS | Or `Azure DevOps` (common in MS/Angular shops), `GitLab` |
| Package Manager | npm | 10.x | Or `yarn` (4.x), `pnpm` (9.x) |
| Linting & Formatting | angular-eslint + Prettier | — | `angular-eslint` replaces the deprecated TSLint; always pair with `Prettier` |
| Hosting | Azure Static Web Apps | managed | Or `AWS S3 + CloudFront`, `Netlify`, `Vercel`, `Firebase Hosting` |
| CDN | Azure CDN | managed | Often bundled with Azure Static Web Apps; or `Amazon CloudFront`, `Cloudflare` |
| Error Monitoring | Sentry | SaaS | Or `Datadog Browser SDK`, `Rollbar` |
| CI/CD | GitHub Actions | — | Or `Azure Pipelines` (common in Azure ecosystems), `GitLab CI` |
| CI Audit | Lighthouse CI | — | Or `Angular DevKit budget analysis` (built-in); omit if no CI auditing |
| Bundler | esbuild | — | Angular CLI default from v17; note as `esbuild (Angular CLI default)` |

---

## Other Tools (Web)

| Tool Category | Canonical DTR Name | Notes |
|---|---|---|
| Form handling | Angular Reactive Forms | Built-in; note as `Reactive Forms (built-in)`; or `Angular Forms (template-driven)` |
| Validation | Angular Validators | Built-in; or `zod` for schema-based validation |
| A/B Testing | LaunchDarkly | Or `Firebase A/B Testing` |
| Feature Flags | LaunchDarkly | Or `Unleash`, `ngx-feature-flag` |

---

## Angular-Specific Notes

**State Management nuances:**
- `Angular Signal Store` is the modern approach in Angular 17+ (part of NgRx 17+)
- `NgRx Store` = Redux-style; heavy but proven for large apps
- `Angular Services + BehaviorSubject` = often sufficient for simpler apps (list as `Angular Services (built-in)`)
- `Akita` and `NGXS` are alternatives with less boilerplate than NgRx

**Module vs. Standalone Components (Angular 17+):**
- Angular 17+ uses standalone components by default — no `AppModule`
- Note this in Toolchain Notes if the ASD references Angular architecture decisions

**Data Fetching:**
- `HttpClient` is always present; note it as `HttpClient (built-in)`
- Caching / server state: `TanStack Query Angular` or `NgRx Signal Store` effects

---

## Common Tool Pairings

| Stack Type | Typical Combination |
|---|---|
| Enterprise SPA | TypeScript + Angular 18 + NgRx + HttpClient + Angular Material + SCSS + Jest + Playwright + Azure DevOps + Azure Static Web Apps |
| Azure-integrated | TypeScript + Angular + @azure/msal-angular + Angular Material + Azure Pipelines + Azure Static Web Apps |
| Lightweight SPA | TypeScript + Angular 18 (standalone) + Angular Signal Store + Tailwind CSS + Vitest + GitHub Actions + Netlify |
| Real-time dashboard | TypeScript + Angular + NgRx + SignalR client + Angular Material + Storybook |
