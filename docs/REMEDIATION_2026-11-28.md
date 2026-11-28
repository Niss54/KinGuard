# Audit remediation and verification, 28 November 2026

This records the fixes following the [original audit](READINESS_AUDIT_2026-11-28.md)
of `e31038ff06a547a48f7dc5ee9840e60f80a5fdf6`. The code/configuration gaps listed
there are addressed. This is not a declaration of completed deployment, live
Firebase acceptance, video publication, submission or security certification.

## Changes

| Finding | Resolution |
| --- | --- |
| Case A response could overwrite case B | Requests capture the case and authorization context. A load generation discards older responses, and case/parent data is committed together. Context changes clear case-scoped data. |
| Other delayed patient data | Explanation, intake, upload, handoff link, payment destination and approval-display responses use context guards. Sign-out clears protected data and invalidates pending requests. UPI and mandate UI state are cleared on a case switch. |
| Fresh Nano did not initialize | Dashboard and writable handoff use the same `hybrid.js` lifecycle. The English click path calls and awaits `initializeDeviceModel()`, reports download progress, then attempts inference. An unavailable device uses configured cloud fallback or produces an explicit error. |
| Tamil/Hindi could use English-configured Nano | Mixed/Tamil/Hindi/unsure input defaults to a separate `ONLY_IN_CLOUD` model. Tamil/Hindi explanation buttons force cloud; Indic-script input also forces cloud. Explicit English uses `PREFER_ON_DEVICE` when cloud App Check is configured, otherwise local-only. Romanised input requires the correct language selection. |
| Outdated models | Browser fallback and backend language detection default to `gemini-3.5-flash-lite`. Deployment and env examples match. The detector omits unsupported sampling overrides, uses minimal thinking, and retains language-code allowlist validation. Actual provider output quality remains a live acceptance check. |
| Setup/documentation contradictions | Removed old Chrome flags, stale test counts, unconditional sandbox-sending claims and the contradictory proportionate-deduction status. Updated care-circle reply wording and generated-source labels. Added a consolidated judge guide with native Windows/Bash steps and App Check debug UUID registration. |
| Docker not verified | Built and ran both API and optional booker images. API image includes LICENSE; local audit environments are excluded from build context. Booker has a local-state/secret ignore file and an exec-based JSON command for process signals. |

The existing fixes for PII redaction preserving emergency symptoms, authenticated
new-case intake, trusted signers and atomic receipt/head checkpoints remain covered
by the regression suite. A checkpoint detects a missing tail; rollback of all
records and checkpoints together still requires an external trust anchor.

## Final evidence

| Check | Observed result |
| --- | --- |
| Fresh frozen dependency environment | Environment installed using `uv sync --frozen --extra dev`; final suite executed from `.kinguard/audit-venv`. |
| Full offline suite | **1,293 passed, 1 skipped**, 7 dependency deprecation/experimental warnings; 50.75 seconds. The optional live Memory Bank test skipped. |
| Browser behavior regressions | 11 Node subtests pass, invoked by two pytest cases. They execute the application functions against controlled asynchronous network/SDK responses, including case-load races, sign-out, signed-link access, delayed UPI/handoff results, fresh Nano initialization and language routing. |
| Pinned Firebase SDK compatibility | A local harness exercised the actual downloaded Firebase 13.4.0 Chrome adapter and initializer with a controlled LanguageModel provider: downloadable state triggered one create/download; English selected device; Tanglish/Hindi selected cloud. This did not contact Firebase or run Nano. |
| Lint | `ruff check kinguard tests scripts` passed. |
| Offline spine | Passed; valid receipts verified and deliberately modified payload was rejected. |
| API Docker build | `docker build -t kinguard:submission .` passed with frozen dependencies and project packaging. |
| Booker Docker build | `docker build -t kinguard-booker:submission booker` passed; final build has the JSON command correction. |
| API container HTTP | Health/seed 200; unauthorized intake 401; authorized chest-pain intake 200/HIGH; verification 200/true; unauthorized brief 401; authorized brief 200. Dashboard and shared JS served; model default correct and Firebase reported unconfigured. |
| Booker container HTTP | Health 200 with dry-run true. `/prepare` rejected a loopback/private target before a browser or provider call. No clinic booking was submitted. |
| Browser against API container | Seeded synthetic episode; demo credential opened the Arrival brief; missing Firebase setup was explicit; mild-fever/cough intake created a LOW case with two verified receipts; sign-out cleared protected data. Captured browser error log was empty. Earlier browser attach failures were resolved before this final check. |
| Documentation | Local Markdown link targets passed. Original audit is labelled historical and links here. |
| Repository | GitHub public visibility and MIT detection confirmed. CI results for the pushed commit are available in GitHub Actions; local results above do not substitute for that run. |

All API/container actions used synthetic data and disabled external messaging.
Temporary test containers were used locally, not deployed to a public service.
The earlier credential-pattern scan remains a limited scan, not an exhaustive
assessment of secrets, dependencies, infrastructure or healthcare security.

## Remaining handoff

Follow [JUDGE_GUIDE.md](JUDGE_GUIDE.md) and [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md).

- Avika: Firebase configuration and registered App Check, real fresh-profile Nano
  and cloud tests, output review for the selected models, deployment/test access,
  and a public English demo video.
- Both members: Devpost listing and submitted entry, honest existing-work
  disclosure, and remaining personal eligibility/third-party permission checks.

These are external acceptance and submission tasks. They have not been marked
complete merely because the repository and offline demonstration now pass.
