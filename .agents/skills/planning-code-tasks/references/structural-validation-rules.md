# Structural Validation Rules (Step 3B Pre-Consolidation Gate)

Read this reference at Step 3B. Run all checks BEFORE the consolidation pass (Step 4). If any FAIL, fix inline (max 2 self-correction attempts) before proceeding.

---

## Validation Checks

| ID | Check |
|----|-------|
| SV-01 | **File Existence (MODIFY action):** For each file in `phases[].files_to_modify` with action=MODIFY, verify file exists at `source_path`. Flag: "planned modification of non-existent file — escalate as `[path TBD]` and add to open_questions". |
| SV-01b | **Path Prefix Plausibility (CREATE action):** For each file with action=CREATE, verify the parent directory exists at `source_path` OR the plan explicitly creates it earlier in the same phase. Flag: "planned CREATE under non-existent parent — escalate as `[path TBD]` and add to open_questions". Rationale: a prior calibration (LAC-Android Chapter 2, RC-003) traced repair cycles to plans that specified CREATE paths under non-existent parent directories. |
| SV-01c | **Convention Alignment (CREATE + MODIFY):** For each file path, check the source-tree's existing convention for the same artifact type (e.g., if existing factories live under `app/src/main/java/.../factories/`, a planned `DeepLinkFactories.kt` at the project root is a convention break). Flag: "path does not match existing convention for {artifact_type} — propose alternative or add justification to open_questions". |
| SV-02 | **Circular Dependency Detection:** Build directed graph (phase → depends_on). Flag any cycle with cycle path. Flag self-dependency. |
| SV-03 | **AC Traceability:** For each acceptance criterion, at least one phase must reference it in `testing_strategy` or `files_to_create`. Flag orphaned ACs. |
| SV-04 | **Test-Source Pairing:** For each file in `files_to_create` where `test_file=true`, a corresponding source file must exist in `files_to_create` or `files_to_modify`. Flag tests for phantom files. |
| SV-05 | **TDAD Consistency:** If `tdad_mode=true`, each phase with test coverage must list test work before source work in `implementation_steps`. Flag Red-Green-Refactor order violations. |
| SV-06 | **Forward-Traceability:** For each artifact defined in Phase N (constants, interfaces, types, configuration values, file paths, API endpoints), verify it is referenced by at least one step instruction in Phase N+1 or later. Flag: "artifact defined but never referenced downstream — planning gap." |
| SV-07 | **Call-Site Completeness:** For each new method or function defined in the plan, verify at least one call site is specified (which class calls it, which method invokes it, under what condition). Flag: "method defined but no call site specified — integration gap." |
| SV-08 | **No Research Dereference:** Scan executable sections for "see research", "per research", "per Parameter Schema", "as researched", or source-only pointers where literal implementation values are required. Flag: "execution detail requires RESEARCH-SPEC dereference — inline the literal value or list a non-research artifact in required_artifacts." |
| SV-09 | **FTC Coverage (only when `test_cases_path` was supplied):** For every in-scope FTC in FTC_MAP, verify its id appears in exactly one phase's `testing_strategy.test_case_id`, OR is listed under some phase's `out_of_scope` with reason `deferred-to-e2e` / `covered-elsewhere`. Flag any FTC that is neither planned nor explicitly excluded: "in-scope FTC {id} has no testing_strategy row and no exclusion — coverage gap, add to open_questions." Skip this check entirely when `test_cases_path` was not supplied (no FTC_MAP). |
| SV-10 | **Security-Decisions Presence:** Determine whether the plan has a security surface — scan `scope`/`impact`/`phases` for auth/authz, secret/credential/token/key handling, session or cookie issuance, privileged/admin/internal endpoints, sensitive-data persistence, or file/config writes a secret flows into. IF a surface exists, verify a populated `security_decisions` section is present with at least the relevant rows and that **every access-gating row's `fallback_when_config_absent` is deny/fail-closed** (a grant-on-missing-config fallback is a FAIL — move it to open_questions at impact HIGH). IF no surface exists, verify the explicit `- none: no security surface in scope` declaration is present. Flag: "security surface present but security_decisions missing/incomplete, or a fallback grants on absent config — add fail-closed decisions (SEC-xx) or route the open choice to open_questions." Rationale: prevents the fail-open-auth / plaintext-secret / unthrottled-admin defaults that the downstream code review (secure-defaults SD-01..SD-10) would otherwise bounce back. |

---

## Gate

If FLAGS > 0 after 2 self-correction attempts → document remaining flags in PLAN-AUDIT under `## Structural Validation` and proceed to Step 4. Do NOT block indefinitely.
