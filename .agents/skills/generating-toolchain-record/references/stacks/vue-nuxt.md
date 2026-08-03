# Vue / Nuxt — DTR Field Reference

Use this file when the ASD describes a web frontend built with Vue 3, Nuxt, or a Vue-based framework.

---

## General Category

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Language | TypeScript | 5.x | Vue 3 + TypeScript is the current standard; use `JavaScript` only if explicit |
| Framework | Vue 3 + Nuxt | 3.x / 3.12.x | For SPA without SSR: `Vue 3 + Vite`; always include both Vue and meta-framework versions |
| State Management | Pinia | 2.x | Pinia is the official Vue 3 store; `Vuex` is legacy (Vue 2) — note if still in use |
| i18n / l10n | @nuxtjs/i18n | 8.x | Or `vue-i18n` (standalone); omit if single-language |
| Auth Handling | @sidebase/nuxt-auth | — | Or `nuxt-auth-utils`, `Auth0 Vue SDK`, `vue-oidc-client` |
| Marketing Analytics | Google Analytics | SaaS | Or `Mixpanel`, `Segment`, `Amplitude`; omit if none |
| Data Fetching | useFetch | — | Nuxt built-in; note as `useFetch (Nuxt built-in)`; or `TanStack Query Vue`, `Axios` |
| Search UI | Algolia | SaaS | Or `Typesense`; omit if no search |
| Real-time | Socket.IO client | 4.x | Or `native WebSocket`; omit if no real-time |
| Offline Support | @vite-pwa/nuxt | — | Or `Workbox`; omit if not a PWA |
| Data Compliance (UI) | OneTrust | SaaS | Or `Cookiebot`; omit if no cookie consent |
| CMS Integration | Sanity | SaaS | Or `Contentful`, `Strapi`, `Storyblok`; omit if no CMS |
| Unit Testing | Vitest + Vue Test Utils | — | Standard for Vue 3; `Jest + Vue Test Utils` for legacy |

---

## Project & Design Category

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| CSS Approach | Tailwind CSS | 3.x | Or `UnoCSS`, `Vuetify` (Material), `PrimeVue`, `Quasar`, `Element Plus` |
| Component Docs | Storybook | 8.x | Or `Histoire` (Vue-native alternative); omit if no component docs |

---

## Build, Tooling & Deployment Category

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Version Control | GitHub | SaaS | Or `GitLab`, `Azure DevOps`, `Bitbucket` |
| Package Manager | pnpm | 9.x | Or `npm` (10.x), `yarn` (4.x), `bun` (1.x) |
| Linting & Formatting | ESLint + Prettier | — | Or `@antfu/eslint-config` (popular Vue-focused config); `Biome` as alternative |
| Hosting | Vercel | SaaS | Or `Netlify`, `Cloudflare Pages`, `AWS S3 + CloudFront`, `Azure Static Web Apps` |
| CDN | Vercel Edge | managed | Often bundled with hosting; or `Cloudflare`, `Amazon CloudFront` |
| Error Monitoring | Sentry | SaaS | Or `Datadog Browser SDK`, `Rollbar` |
| CI/CD | GitHub Actions | — | Or `GitLab CI`, `Netlify`, `Vercel` (preview deployments) |
| CI Audit | Lighthouse CI | — | Omit if no automated performance auditing |
| Bundler | Vite | 5.x | Built into Vue 3 and Nuxt 3; no separate configuration needed; note as `Vite (built-in)` |

---

## Other Tools (Web)

| Tool Category | Canonical DTR Name | Notes |
|---|---|---|
| Form handling | VeeValidate | Or `FormKit`, `Vuelidate` |
| Validation | Zod | Or `Yup`; often paired with VeeValidate |
| A/B Testing | Firebase A/B Testing | Or `LaunchDarkly` |
| Feature Flags | LaunchDarkly | Or `Unleash`, `Firebase Remote Config` |

---

## Vue / Nuxt–Specific Notes

**Nuxt vs. Vue standalone:**
- `Nuxt 3` = meta-framework with SSR, SSG, ISR, auto-imports, file-based routing
- `Vue 3 + Vite` = SPA only; use when SSR is not needed
- For pure CSR apps, omit `Nuxt` and just list `Vue 3`

**Pinia vs. Vuex:**
- `Pinia` is the official store since Vue 3.2; always use this unless the ASD explicitly mentions Vuex (legacy)
- For very simple apps, `Composables + ref/reactive` replaces a dedicated store

**useFetch vs. TanStack Query:**
- `useFetch` (Nuxt built-in) handles SSR data; mark it as `useFetch (Nuxt built-in)`
- `TanStack Query Vue` is preferred for complex client-side caching scenarios

---

## Common Tool Pairings

| Stack Type | Typical Combination |
|---|---|
| Nuxt SSR app | TypeScript + Vue 3 + Nuxt 3 + Pinia + Tailwind CSS + Vitest + Playwright + GitHub Actions + Vercel |
| Vue SPA | TypeScript + Vue 3 + Vite + Pinia + TanStack Query + Tailwind CSS + Vitest + GitHub Actions + S3 + CloudFront |
| Content/marketing site | TypeScript + Vue 3 + Nuxt 3 + Storyblok + Tailwind CSS + @nuxtjs/i18n + Lighthouse CI |
| Admin dashboard | TypeScript + Vue 3 + Nuxt 3 + Pinia + Element Plus or Vuetify + Storybook + Vitest |
