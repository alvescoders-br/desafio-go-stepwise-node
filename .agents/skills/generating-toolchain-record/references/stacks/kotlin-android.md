# Kotlin / Android — DTR Field Reference

Use this file when the ASD describes a native Android application built with Kotlin.

---

## General Development Category

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Language | Kotlin | 2.0 | Current stable; 1.9.x also common; always include major.minor |
| IDE | Android Studio | — | Include the release name if known (e.g., Android Studio Iguana); Xcode not applicable |
| Dependency Management | Gradle | 8.x | Kotlin DSL (`.kts`) is the modern standard; mention if using Groovy DSL |
| Artifact Repository | JFrog Artifactory | — | Or `GitHub Packages`, `Google Maven`; omit if no internal artifact publishing |
| Version Control | GitHub | SaaS | Or `GitLab`, `Bitbucket`, `Azure DevOps` |
| Code Review Tool | GitHub | SaaS | Same as version control |
| Static and Dynamic Code Quality Inspection | SonarQube + Detekt | — | SonarQube for broad quality; `Detekt` for Kotlin-specific static analysis; `Android Lint` (built-in) |
| Lint | Ktlint | — | Or `Detekt` (if not listed above); both are common in Kotlin Android projects |
| Mocking | Mockk | 1.x | Kotlin-idiomatic mocking library; preferred over `Mockito-Kotlin` for new projects |
| Unit Testing | JUnit 5 | 5.x | Or `JUnit 4` (legacy); Android unit tests also use `Robolectric` for framework classes |
| E2E / Integration | Espresso | — | Built into AndroidX; or `UI Automator`, `Maestro` (newer, cross-platform) |
| Monitoring | Firebase Performance Monitoring | managed | Or `Dynatrace`, `New Relic Mobile`, `Datadog Mobile SDK` |
| CI/CD Pipeline Automation | GitHub Actions | — | Or `Bitrise`, `GitLab CI`, `CircleCI`, `Fastlane` (packaging layer) |
| App Distribution for Testing | Firebase App Distribution | managed | Or `Google Play Internal Testing`, `App Center` |
| Security and Obfuscation Tool | R8 | — | Built-in with AGP; `ProGuard` (older); commercial: `DexGuard` for maximum protection |

---

## Monitoring Category

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Performance | Firebase Performance Monitoring | managed | Or `Dynatrace`, `New Relic Mobile`, `Android Profiler` (IDE — development only) |
| Analytics | Firebase Analytics | managed | Or `Mixpanel`, `Amplitude`, `Segment`; Firebase is default for Android |
| Crash Monitoring | Firebase Crashlytics | managed | Or `Sentry`, `Bugsnag`; Crashlytics is the de facto standard for Android |

---

## Other Tools (Mobile)

| Tool Category | Canonical DTR Name | Notes |
|---|---|---|
| UI framework | Jetpack Compose | 1.7.x — modern declarative UI; or `XML Views` (legacy View system) |
| Architecture | MVVM + ViewModel | Via Android Jetpack `ViewModel`; or `MVI` pattern (Orbit MVI, MVIKotlin) |
| State management | Android ViewModel + StateFlow | Built into Jetpack; or `Orbit MVI` for stricter unidirectional flow |
| Navigation | Jetpack Navigation | 2.8.x — built into Jetpack; Compose-compatible |
| HTTP client | Retrofit | 2.x | With `OkHttp` and Gson/Moshi/kotlinx.serialization |
| Serialization | kotlinx.serialization | — | Or `Gson`, `Moshi`; kotlinx.serialization is Kotlin-native |
| Local database | Room Database | 2.6.x | Jetpack component; type-safe SQLite abstraction |
| Dependency injection | Hilt | 2.x | Recommended by Google; built on Dagger 2; or `Koin` (simpler) |
| Async | Kotlin Coroutines + Flow | — | Standard for async in Kotlin Android; built into Kotlin |
| Push notifications | Firebase Cloud Messaging | managed | Via `firebase-messaging` SDK |
| Auth | Firebase Authentication | managed | Or `AppAuth`, `Keycloak Android`, `Auth0 Android SDK` |
| In-app purchases | Google Play Billing Library | 6.x | Or `RevenueCat` (cross-platform subscription management) |
| Deep linking | Jetpack Navigation | — | Built-in deep link support in Navigation component |
| CI/CD (mobile-specific) | Fastlane | — | Handles signing, Play Store upload; or `Gradle Play Publisher` |
| Maps | Google Maps SDK for Android | managed | Or `Mapbox Maps SDK` |

---

## Kotlin Android–Specific Notes

**Jetpack Compose vs. XML Views:**
- `Jetpack Compose` is the modern approach (2021+); preferred for new projects
- `XML Views` with `ViewBinding` is still common in legacy codebases
- Some projects mix both during migration — note in Toolchain Notes

**Gradle:**
- Kotlin DSL (`.kts` files) is the recommended format as of AGP 8.x
- `Version Catalogs` (libs.versions.toml) is now the standard for dependency management
- Always note the Gradle version and AGP (Android Gradle Plugin) version if specified

**R8 / Obfuscation:**
- R8 is enabled by default in release builds via AGP — it combines shrinking + obfuscation
- `DexGuard` is a commercial superset of R8 with stronger protections

**Testing layers:**
- Unit: `JUnit 5` + `Mockk` (runs on JVM, fast)
- Integration: `Robolectric` (Android framework without a device)
- UI: `Espresso` (on-device) or `Maestro` (device farm-friendly)

---

## Common Tool Pairings

| Stack Type | Typical Combination |
|---|---|
| Modern Android app | Kotlin 2.0 + Jetpack Compose + Hilt + Retrofit + Room + Coroutines + Firebase Crashlytics + Firebase Analytics + GitHub Actions |
| Firebase-integrated | Kotlin + Jetpack Compose + Hilt + firebase-auth + Firebase Crashlytics + Firebase Analytics + FCM + GitHub Actions |
| Enterprise Android | Kotlin + Jetpack Compose + Hilt + Retrofit + Room + Orbit MVI + SonarQube + Detekt + Fastlane + Bitrise |
| Google-native | Kotlin + Jetpack Compose + Hilt + Google Maps SDK + Google Play Billing + Firebase suite + Google Play Internal Testing |
