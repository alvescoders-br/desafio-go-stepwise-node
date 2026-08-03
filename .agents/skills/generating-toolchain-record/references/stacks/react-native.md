# React Native — DTR Field Reference

Use this file when the ASD describes a mobile application built with React Native (bare or Expo).

---

## General Development Category

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Language | TypeScript | 5.x | React Native supports JS but TypeScript is standard for new projects |
| IDE | Visual Studio Code | — | Standard for React Native; `Android Studio` and `Xcode` still needed for native builds |
| Dependency Management | npm | 10.x | Or `yarn` (4.x), `pnpm` (9.x), `bun` (1.x) |
| Artifact Repository | — | — | Usually omit; builds go to app stores or Firebase App Distribution |
| Version Control | GitHub | SaaS | Or `GitLab`, `Bitbucket`, `Azure DevOps` |
| Code Review Tool | GitHub | SaaS | Same as version control |
| Static and Dynamic Code Quality Inspection | SonarQube | — | Or `SonarCloud`; supplemented by ESLint rules |
| Lint | ESLint | — | Standard; with `@react-native/eslint-config`; add Prettier for formatting |
| Mocking | Jest | 29.x | Jest's built-in mocking; or `jest-mock-extended` for typed mocks |
| Unit Testing | Jest + React Native Testing Library | 29.x | `@testing-library/react-native` is the standard testing utility |
| E2E / Integration | Detox | 20.x | Or `Maestro` (simpler, cross-platform); Detox is most widely used for RN |
| Monitoring | Datadog Mobile SDK | SaaS | Or `New Relic Mobile`, `Dynatrace` |
| CI/CD Pipeline Automation | GitHub Actions | — | With `Fastlane` for iOS/Android signing; or `Bitrise`, `EAS Build` (Expo) |
| App Distribution for Testing | Firebase App Distribution | managed | Or `TestFlight` (iOS), `EAS Update` (Expo), `App Center` |
| Security and Obfuscation Tool | Hermes | — | Built-in JS engine that bytecode-compiles JS; commercial option: `JScrambler` |

---

## Monitoring Category

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Performance | Datadog Mobile SDK | SaaS | Or `Firebase Performance Monitoring`, `New Relic Mobile` |
| Analytics | Segment | SaaS | Or `Firebase Analytics`, `Mixpanel`, `Amplitude` |
| Crash Monitoring | Sentry | 5.x | Or `Firebase Crashlytics`, `Bugsnag`; Sentry has best-in-class React Native support |

---

## Other Tools (Mobile)

| Tool Category | Canonical DTR Name | Notes |
|---|---|---|
| State management | Redux Toolkit | 2.x | Or `Zustand`, `Jotai`, `TanStack Query` (server state) |
| Navigation | React Navigation | 6.x | Industry standard; `Expo Router` for Expo-managed projects |
| HTTP client | Axios | 1.x | Or `fetch` (built-in), `TanStack Query` (wraps fetch/axios) |
| Local storage | MMKV | 2.x | Or `AsyncStorage`, `WatermelonDB` (complex data), `SQLite` |
| Push notifications | Firebase Cloud Messaging | managed | Via `@react-native-firebase/messaging` (bare) or `expo-notifications` (Expo) |
| Deep linking | React Navigation | 6.x | Deep link support built into React Navigation; or `Branch` for attribution |
| In-app purchases | RevenueCat | — | Or `react-native-iap` (manual); RevenueCat is the modern choice |
| Auth | react-native-app-auth | — | Generic OIDC; or `@azure/msal-react-native`, `Auth0 React Native SDK` |
| CI/CD (mobile-specific) | Fastlane | — | iOS codesigning, TestFlight upload, Android Play Store upload |
| Maps | react-native-maps | — | Google Maps or Apple Maps via same API |
| Camera / media | react-native-vision-camera | — | Or `expo-camera` for Expo |

---

## Bare vs. Expo

**Bare React Native:**
- Full access to native modules; use `Fastlane` + `GitHub Actions` for CI/CD
- `react-native-firebase` for Firebase integration

**Expo (managed or bare):**
- `EAS Build` replaces Fastlane for cloud builds
- `expo-notifications` replaces `react-native-firebase/messaging` for push
- `Expo Router` replaces `React Navigation` for file-based routing
- Note Expo SDK version: `Expo SDK 51`, `Expo SDK 52`

---

## React Native–Specific Notes

**Testing setup:**
- Jest is pre-configured in the React Native template
- `@testing-library/react-native` is the correct package name (not React Testing Library)
- Detox requires native build steps; add to Toolchain Notes if setup complexity is noted

**Obfuscation:**
- Hermes (built-in bytecode compilation) provides basic obfuscation
- Commercial: `JScrambler` for production apps requiring strong obfuscation
- Note in Toolchain Notes if app store security review requires stronger measures

**Platform versions:**
- iOS minimum: note if ASD specifies (e.g., iOS 16+)
- Android minimum: note if ASD specifies (e.g., Android 9+, API 28)

---

## Common Tool Pairings

| Stack Type | Typical Combination |
|---|---|
| Standard mobile app | TypeScript + React Native 0.74 + Redux Toolkit + React Navigation + Axios + MMKV + Sentry + Firebase Analytics + GitHub Actions + Fastlane |
| Firebase-integrated | TypeScript + React Native + Zustand + React Navigation + react-native-firebase + Sentry + GitHub Actions |
| Expo-managed | TypeScript + React Native (Expo SDK 52) + Expo Router + Zustand + EAS Build + expo-notifications + Sentry |
| Real-time features | TypeScript + React Native + TanStack Query + Socket.IO + Redux Toolkit + Detox + GitHub Actions |
