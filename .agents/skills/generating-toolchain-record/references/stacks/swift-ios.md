# Swift / iOS — DTR Field Reference

Use this file when the ASD describes a native iOS application built with Swift.

---

## General Development Category

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Language | Swift | 5.10 | Or `Swift 6.0` (strict concurrency model); always include minor version |
| IDE | Xcode | 15 / 16 | Xcode version is tied to Swift and iOS SDK version; Visual Studio Code is secondary only |
| Dependency Management | Swift Package Manager | — | Built-in to Xcode since Xcode 11; note as `Swift Package Manager (built-in)`; `CocoaPods` is legacy |
| Artifact Repository | — | — | Usually omit; builds go to TestFlight / App Store; binaries: `GitHub Releases` |
| Version Control | GitHub | SaaS | Or `GitLab`, `Bitbucket`, `Azure DevOps` |
| Code Review Tool | GitHub | SaaS | Same as version control |
| Static and Dynamic Code Quality Inspection | SonarQube + SwiftLint | — | SonarQube for broad analysis; `SwiftLint` for Swift-specific style/quality |
| Lint | SwiftLint | 0.55.x | Standard Swift linter; often configured with `.swiftlint.yml` |
| Mocking | Cuckoo | — | Or `Mockolo` (code-gen mocks), `Mockingbird`; or manual protocol stubs |
| Unit Testing | XCTest | — | Built into Xcode; note as `XCTest (built-in)`; modern alternative: `Swift Testing` (Xcode 16+) |
| E2E / Integration | XCUITest | — | Built into Xcode; or `Maestro` (cross-platform, device farm-friendly) |
| Monitoring | Firebase Performance Monitoring | managed | Or `Datadog Mobile SDK`, `Dynatrace`, `New Relic Mobile` |
| CI/CD Pipeline Automation | GitHub Actions | — | With `Fastlane` for codesigning and TestFlight upload; or `Bitrise`, `Xcode Cloud` |
| App Distribution for Testing | TestFlight | managed | Apple's official beta distribution; or `Firebase App Distribution` for internal builds |
| Security and Obfuscation Tool | iXGuard | — | Commercial (GuardSquare); or `SwiftShield` (open-source symbol obfuscation); omit for internal apps |

---

## Monitoring Category

| Field | Canonical DTR Name | Typical Version | Notes |
|---|---|---|---|
| Performance | Firebase Performance Monitoring | managed | Or `Datadog Mobile SDK`, `MetricKit` (Apple, built-in), `Instruments` (dev-only — omit from DTR) |
| Analytics | Firebase Analytics | managed | Or `Mixpanel`, `Amplitude`, `Segment`, `Adjust` |
| Crash Monitoring | Firebase Crashlytics | managed | Or `Sentry`, `Bugsnag`; Crashlytics is widely used in iOS projects |

---

## Other Tools (Mobile)

| Tool Category | Canonical DTR Name | Notes |
|---|---|---|
| UI framework | SwiftUI | Modern declarative UI (iOS 14+); or `UIKit` (legacy, still widely used) |
| Architecture | MVVM + Combine | Common pattern; or `TCA (The Composable Architecture)` (pointfreeco), `VIPER` |
| State management | Combine | Apple's reactive framework; or `TCA`, `RxSwift` (legacy) |
| Navigation | NavigationStack | Built-in SwiftUI navigation (iOS 16+); `Coordinator` pattern for UIKit |
| HTTP client | URLSession | Built-in (`URLSession (built-in)`); or `Alamofire` (5.x), `Moya` (wraps Alamofire) |
| Serialization | Codable | Built-in Swift protocol; no extra library needed |
| Local storage | Core Data | Apple framework; or `SwiftData` (iOS 17+), `Realm`, `GRDB` |
| Dependency injection | Resolver | Or `Swinject`, `Factory`, `pointfreeco/swift-dependencies` (TCA-oriented) |
| Async | Swift Concurrency (async/await) | Built-in since Swift 5.5; or `Combine`; avoid `RxSwift` in new projects |
| Push notifications | APNs | Built-in via `UNUserNotificationCenter`; cloud delivery: `Firebase Cloud Messaging` |
| Auth | firebase_auth | Or `ASWebAuthenticationSession (built-in)`, `AppAuth`, `Auth0 iOS SDK` |
| In-app purchases | StoreKit 2 | Built-in (iOS 15+); or `RevenueCat` (cross-platform subscription management) |
| Deep linking | Universal Links | Apple-native; or `Branch` (attribution + deferred linking) |
| CI/CD (iOS-specific) | Fastlane | Codesigning, TestFlight upload, App Store Connect API; pairs with GitHub Actions |
| Maps | MapKit | Built-in Apple maps; or `Google Maps SDK for iOS`, `Mapbox Maps SDK` |

---

## Swift iOS–Specific Notes

**SwiftUI vs. UIKit:**
- `SwiftUI` is the modern approach; minimum deployment target iOS 14 or higher
- `UIKit` remains necessary for complex custom controls or supporting iOS 13
- Mixed codebases are common during transition — note in Toolchain Notes

**Swift Concurrency:**
- `async/await` + `Actor` is the modern replacement for `DispatchQueue` / `OperationQueue`
- `Swift 6.0` enforces strict concurrency — a breaking change worth noting if the ASD targets it

**Codesigning & provisioning:**
- Fastlane `match` manages certificates and provisioning profiles in a shared repo
- `Xcode Cloud` is Apple's managed CI/CD alternative to GitHub Actions + Fastlane

**Dependency management:**
- `Swift Package Manager` (SPM) is the standard and Xcode-native
- `CocoaPods` is legacy; if the ASD mentions it, note in Toolchain Notes that migration to SPM may be planned
- `Carthage` is effectively deprecated

**Testing:**
- `Swift Testing` (available in Xcode 16 / Swift 6) replaces XCTest with a cleaner API
- `XCTest` remains the standard for projects on Xcode 15

---

## Common Tool Pairings

| Stack Type | Typical Combination |
|---|---|
| Modern iOS app | Swift 5.10 + SwiftUI + async/await + Firebase Crashlytics + Firebase Analytics + GitHub Actions + Fastlane + TestFlight |
| UIKit legacy | Swift 5.x + UIKit + Coordinator + Combine + Alamofire + Firebase Crashlytics + Bitrise + TestFlight |
| TCA architecture | Swift + SwiftUI + TCA + pointfreeco/swift-dependencies + XCTest + GitHub Actions + Fastlane |
| Enterprise with auth | Swift + SwiftUI + AppAuth + Auth0 iOS SDK + Firebase Crashlytics + Datadog Mobile SDK + Xcode Cloud |
