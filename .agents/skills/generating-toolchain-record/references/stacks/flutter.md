# Flutter / Dart — DTR Field Reference

Use this file when the ASD describes a mobile (or cross-platform) application built with Flutter.

---

## General Development Category

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Language | Dart | 3.x | Always list Dart, not Flutter; Flutter version goes in Framework |
| IDE | Visual Studio Code | — | Or `Android Studio`; VS Code is more common for Flutter |
| Dependency Management | Pub | — | Flutter's built-in package manager (pub.dev); list as `Pub (built-in)` |
| Artifact Repository | — | — | Usually omit; builds go to app stores or Firebase App Distribution |
| Version Control | GitHub | SaaS | Or `GitLab`, `Bitbucket`, `Azure DevOps` |
| Code Review Tool | GitHub | SaaS | Same as version control in most setups |
| Static and Dynamic Code Quality Inspection | DCM | — | Dart Code Metrics; or `SonarQube + Dart`; note `flutter analyze` as built-in |
| Lint | Dart Analyzer | — | Built-in; enforced via `analysis_options.yaml` + `flutter_lints` package |
| Mocking | Mocktail | — | Or `Mockito for Dart`; `Mocktail` is more ergonomic with null safety |
| Unit Testing | flutter_test | — | Built-in Flutter testing framework; note as `flutter_test (built-in)` |
| E2E / Integration | Patrol | — | Or `integration_test (built-in)`, `Maestro`; `Detox` is React Native — not applicable |
| Monitoring | Datadog Mobile SDK | SaaS | Or `Firebase Performance Monitoring`; general app monitoring |
| CI/CD Pipeline Automation | GitHub Actions | — | Or `Codemagic`, `Bitrise`, `Fastlane` (signing + distribution) |
| App Distribution for Testing | Firebase App Distribution | managed | Or `TestFlight` (iOS only), `Google Play Internal Testing` |
| Security and Obfuscation Tool | Flutter CLI | — | Use `--obfuscate --split-debug-info` flags; note as `Flutter CLI (--obfuscate)` |

---

## Monitoring Category

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Performance | Firebase Performance Monitoring | managed | Or `Datadog Mobile SDK`, `New Relic Mobile` |
| Analytics | Firebase Analytics | managed | Or `Segment`, `Mixpanel`, `Amplitude`; Firebase is most common for Flutter |
| Crash Monitoring | Firebase Crashlytics | managed | Or `Sentry` (4.x), `Bugsnag`; always include — Crashlytics is default for Flutter |

---

## Other Tools (Mobile)

| Tool Category | Canonical DTR Name | Notes |
|---|---|---|
| State management | Riverpod | 2.x (code gen) | Or `flutter_bloc` (Bloc pattern), `Provider` (legacy), `GetX`, `MobX` |
| Navigation | go_router | 14.x | Built on Flutter Navigator 2.0; standard for new projects |
| HTTP client | Dio | 5.x | Or `http` (built-in, simpler) |
| Local storage | Hive | 2.x | Or `Drift` (SQLite, type-safe), `Isar`, `SharedPreferences` |
| Push notifications | Firebase Cloud Messaging | managed | Via `firebase_messaging` package |
| Deep linking | go_router (built-in) | — | Deep link support is built into `go_router` |
| In-app purchases | RevenueCat | — | Or `in_app_purchase` (Flutter built-in) |
| Auth | firebase_auth | managed | Or `flutter_appauth` (generic OIDC), `Auth0 Flutter SDK` |
| Localization | Flutter Intl | — | ARB files + `intl` package; or `easy_localization` |
| Feature flags | Firebase Remote Config | managed | Or `LaunchDarkly Flutter SDK` |
| Maps | Google Maps Flutter | managed | Or `Mapbox GL` |
| CI/CD (mobile-specific) | Fastlane | — | Handles iOS signing, app store upload; pairs with GitHub Actions |

---

## Flutter-Specific Notes

**State management choice matters for DTR:**
- List the primary state management solution; don't list all that exist
- `Riverpod 2.x` with code generation is the modern recommendation
- `flutter_bloc` = explicit if the ASD mentions "BLoC pattern"

**Obfuscation:**
- Flutter obfuscation is via CLI flags, not a separate tool — note as `Flutter CLI (--obfuscate)`
- `--split-debug-info` stores symbols separately for stack trace deobfuscation

**Cross-platform structure:**
- A single Flutter project targets iOS + Android (and optionally Web/Desktop)
- Use one Mobile tab unless the ASD describes platform-specific native modules that need separate tabs

**Packages use `pub.dev` versioning:**
- Version format: `2.3.0` (semver); check pub.dev for current stable

---

## Common Tool Pairings

| Stack Type | Typical Combination |
|---|---|
| Mobile app (standard) | Dart + Flutter + Riverpod + go_router + Dio + Hive + Firebase Crashlytics + Firebase Analytics + Firebase Performance + GitHub Actions |
| Firebase-heavy | Dart + Flutter + Riverpod + firebase_auth + Firebase Crashlytics + Firebase Analytics + Firebase Remote Config + FCM |
| RevenueCat subscription | Dart + Flutter + Riverpod + RevenueCat + Firebase Crashlytics + Firebase Analytics + Codemagic |
| Enterprise | Dart + Flutter + flutter_bloc + Dio + Drift + Sentry + Datadog Mobile SDK + GitHub Actions + Fastlane |
