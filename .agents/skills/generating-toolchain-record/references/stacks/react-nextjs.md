# React / Next.js — DTR Field Reference

Use this file when the ASD describes a web frontend built with React, Next.js, Remix, or a React-based framework.

---

## General Category

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Language | TypeScript | 5.x | Use `JavaScript` only if TypeScript is explicitly absent |
| Framework | React + Next.js | 18 / 14 | Or `React + Vite` (SPA), `Remix`, `Gatsby`; always name both React and the meta-framework |
| State Management | Zustand | 4.x | Or `Redux Toolkit` (2.x), `Jotai`, `Recoil`, `Context API (built-in)`, `TanStack Store` |
| i18n / l10n | next-intl | — | Or `react-i18next`, `FormatJS`; omit if single-language only |
| Auth Handling | NextAuth.js | — | Or `MSAL.js` (Microsoft), `Keycloak JS`, `react-oidc-context`, `Auth0 React SDK` |
| Marketing Analytics | Google Analytics | SaaS | Or `Mixpanel`, `Segment`, `Amplitude`, `PostHog`; omit if no analytics |
| Data Fetching | TanStack Query | 5.x | Or `RTK Query`, `SWR`, `Apollo Client` (GraphQL), `Next.js (built-in)` for SSR data |
| Search UI | Algolia | SaaS | Or `Pagefind` (static), `Typesense`; omit if no search |
| Real-time | Socket.IO client | 4.x | Or `Ably`, `Pusher`, `Supabase Realtime`, `native WebSocket`; omit if no real-time |
| Offline Support | next-pwa | — | Or `Workbox`; omit if not a PWA |
| Data Compliance (UI) | OneTrust | SaaS | Or `Cookiebot`, custom implementation; omit if no cookie consent needed |
| CMS Integration | Contentful | SaaS | Or `Sanity`, `Strapi`, `AEM Headless`; omit if content is from own APIs |
| Unit Testing | Jest + React Testing Library | 29.x | Or `Vitest + React Testing Library` (faster, ESM-native) |
| E2E Testing | Playwright | 1.x | Or `Cypress`; list in Other Tools if not in standard DTR field |

---

## Project & Design Category

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| CSS Approach | Tailwind CSS | 3.x | Or `Styled Components`, `CSS Modules`, `Emotion`, `Material UI`, `shadcn/ui + Tailwind CSS` |
| Component Docs | Storybook | 8.x | Or `Chromatic` (cloud Storybook); omit if no component documentation |

---

## Build, Tooling & Deployment Category

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Version Control | GitHub | SaaS | Or `GitLab`, `Azure DevOps`, `Bitbucket` |
| Package Manager | pnpm | 9.x | Or `npm` (10.x), `yarn` (4.x), `bun` (1.x) |
| Linting & Formatting | ESLint + Prettier | — | Or `Biome` (all-in-one replacement); `next lint` wraps ESLint |
| Hosting | Vercel | SaaS | Or `AWS S3 + CloudFront`, `Netlify`, `Azure Static Web Apps`, `Cloudflare Pages` |
| CDN | Vercel Edge | managed | Often bundled with hosting; or `Amazon CloudFront`, `Cloudflare` |
| Error Monitoring | Sentry | SaaS | Or `Datadog Browser SDK`, `LogRocket`, `Rollbar` |
| CI/CD | GitHub Actions | — | Or `GitLab CI`, `Azure Pipelines`, `CircleCI`, `Vercel` (preview deployments) |
| CI Audit | Lighthouse CI | — | Or `WebPageTest`; omit if no automated performance auditing in CI |
| Bundler | Turbopack | — | Next.js 14+ default (dev); `Webpack` (production/legacy); `Vite` for non-Next.js React |

---

## Other Tools (Web)

| Tool Category | Canonical DTR Name | Notes |
|---|---|---|
| A/B Testing | LaunchDarkly | Or `GrowthBook`, `Optimizely`, `Firebase A/B Testing` |
| Feature Flags | LaunchDarkly | Or `Unleash`, `Firebase Remote Config` |
| Form handling | React Hook Form | Or `Formik`; list if forms are a significant part of the app |
| Validation | Zod | Or `Yup`, `Valibot` |
| Animation | Framer Motion | Or `React Spring`, `CSS animations` (omit if none) |

---

## Framework-Specific Notes

**Next.js (SSR/SSG/ISR)**
- Data Fetching: `Next.js (built-in)` for server components; `TanStack Query` for client-side
- Bundler: `Turbopack` (dev) / `Webpack` (legacy prod) — note both if mixed
- Auth: `NextAuth.js` or `Auth.js` (provider-agnostic)
- Hosting: `Vercel` (native); or any Node.js host for SSR

**React + Vite (SPA)**
- Bundler: `Vite` (3.x / 5.x)
- No built-in SSR; client-rendered only
- Hosting: Any static host (S3, Netlify, Cloudflare Pages)

---

## Common Tool Pairings

| Stack Type | Typical Combination |
|---|---|
| Next.js full-stack | TypeScript + React 18 + Next.js 14 + TanStack Query + Zustand + Tailwind CSS + Vitest + Playwright + GitHub Actions + Vercel |
| React SPA | TypeScript + React + Vite + Redux Toolkit + RTK Query + CSS Modules + Jest + RTL + GitHub Actions + S3 + CloudFront |
| Dashboard / admin | TypeScript + React + Next.js + shadcn/ui + Tailwind CSS + TanStack Table + Zustand + Storybook |
| Real-time collab | TypeScript + React + Next.js + Socket.IO client + Zustand + Tailwind CSS + Playwright |
