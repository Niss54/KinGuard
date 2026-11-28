# Submission readiness audit, 28 November 2026

Audited commit: `e31038ff06a547a48f7dc5ee9840e60f80a5fdf6`.
Checks were performed on 27 and 28 November; the checkout was unchanged when
work resumed. This is an assessment of that commit, not a record of fixes.

**Historical findings:** the code and documentation findings below were addressed
after this audit. See [remediation and final verification](REMEDIATION_2026-11-28.md)
for the updated results. Do not read the original verdict below as the status of
the fixed checkout. Live-provider and external submission items remain pending.

**Verdict: not fully submission-ready, even with API credentials and deployment
excluded as pending setup.** The deterministic demo and installation work, but
case-loading correctness, first-run Nano initialization, language routing and
documentation still need attention. These findings do not establish automatic
disqualification. They weaken the functioning-project and accurately-described
behavior requirements.

## Verification performed

| Check | Result | Boundary |
| --- | --- | --- |
| Fresh dependency installation | Passed `uv sync --frozen --extra dev` into `.kinguard/audit-venv`; 84 packages installed | Actual package downloads and project build succeeded. Initial sandbox cache/DNS failures were resolved by using a workspace cache and approved network access. |
| Full tests, existing environment | 1,286 passed, 1 skipped, 7 warnings | `PYTHONUTF8=1`, memory store; 30.19 seconds. |
| Full tests, fresh environment | 1,286 passed, 1 skipped, 7 warnings | 41.98 seconds. The live Memory Bank test is conditional and skipped without its resource. |
| Lint | Passed | `ruff check kinguard tests scripts`. |
| Offline spine | Passed | Receipt verification succeeded before tampering and rejected the altered receipt afterward. Missing-key warnings do not demonstrate a real model call. |
| GitHub CI | [Passed for the audited commit](https://github.com/Niss54/KinGuard/actions/runs/46042310961) | Installation, lint, tests and offline spine. |
| Local HTTP smoke | Passed | Health 200; scratch seed 200; unauthenticated intake 401; authenticated chest-pain intake 200/HIGH; public verification 200/true; private brief 401 without bearer and 200 with demo bearer. |
| Desktop browser | Passed basic flow | Seeded a synthetic episode, used demo credential, visited Now/Arrival/Routing/Record/Claim/Audit, exercised the access-gate proof and checked missing-Firebase configuration handling. |
| Phone-width browser | Passed inspected flow at 402 x 874 | Routing and intake layouts were usable; mild-fever/cough input opened a LOW case with two verified receipts. This is viewport emulation, not a physical handset or on-device inference test. |
| Local Markdown links | No missing targets found | Checked tracked Markdown relative-link targets; external links and every heading anchor were not exhaustively validated. |
| Public repository and license | Passed | GitHub reported public visibility and MIT detection. |
| Credential-pattern scan | No matches in 371 historical Git blobs | Checked Google/GitHub/AWS key patterns, private-key blocks and service-account private-key fields. This is a limited pattern scan, not proof that every possible secret or PII is absent. |
| Docker build | Not verified | Docker CLI exists; the Linux engine was unavailable. No container-image success is claimed. |
| Real providers | Not exercised | Firebase/Nano/cloud, App Check token exchange, Firestore transactions against a real service, WhatsApp, payments and booking providers remain outside this offline audit. |

## Findings requiring attention

### 1. High: delayed case loads can mix two patients' screen state

Location: `kinguard/webui/index.html`, `load()` around lines 2418-2445.

`load()` writes each awaited response into global state and re-reads `S.caseId`
between requests. It has no request-generation or captured-case check. The
explanation-specific guard does not protect this general loader.

Reproduction using the actual extracted functions and controlled API promises:

1. Start loading case A and pause its brief response.
2. Switch to case B and complete B's load.
3. Complete the delayed A brief.

Observed final state:

```json
{"caseId":"B","brief":"/api/cases/A/brief","parentId":"parent-B","bills":"/api/cases/B/bills"}
```

This demonstrates mixed client state, not an authentication bypass: the caller
in the reproduction could load both cases. A user can nevertheless see the wrong
patient's brief beneath the active case. Capture the case/identity and generation,
fetch into temporary state, and commit only while the request remains current.
Cover case switches and sign-out while requests are pending.

### 2. High: the app does not initialize/download Nano for a fresh user

Locations: `kinguard/webui/index.html` model setup around line 2550 and requests
around 2689/2836; `kinguard/server.py` generated handoff script around 3065-3113.

Neither surface calls `initializeDeviceModel()`. The
[official Firebase setup](https://firebase.google.com/docs/ai-logic/hybrid/web/get-started)
requires calling it after/on a user interaction before prompting. The exact
[13.4.0 SDK used by this app](https://www.gstatic.com/firebasejs/13.4.0/firebase-ai.js)
was downloaded and inspected. Its adapter, tested with a stub LanguageModel
provider reporting `downloadable`, selected cloud eligibility and made zero
download/create calls when only availability was checked.

A pre-downloaded model may still work. The defect is the missing first-run
initialization path; it is not proof that every warmed Nano environment fails.
Add user-triggered initialization, progress/error handling, and distinguish
downloadable/downloading/available before claiming on-device readiness.

### 3. High: Tamil/Hindi cloud routing is promised but not enforced

Locations: README lines 13-15 and 718-720; dashboard `initHybridAI()`,
`runHybridNormalize()` and `runHybridExplain()`.

The app uses the same `PREFER_ON_DEVICE` model for all languages. The selected
explanation language changes the prompt, not model routing or language options.
The pinned SDK's default expected text input/output language is English, and its
on-device request eligibility test checks content types rather than detecting
the natural language of each text prompt.

With the pinned adapter reporting `available`, both Tamil and Hindi text requests
were accepted as eligible for on-device execution while expected outputs remained
`["en"]`. This was a routing test, not real Tamil/Hindi inference. An eventual
model error might trigger fallback, but that is not the explicit language route
the README promises. Select a cloud-only model for unsupported languages or
implement supported-language configuration and tested fallback. Do not infer
execution source from an intended language or a ready badge.

### 4. Medium: model defaults need migration before judging

Locations: `.env.example` lines 16/34, `kinguard/server.py` line 333 and
`kinguard/comms/detect_language.py` line 45.

The backend language detector defaults to `gemini-2.5-flash-lite`, while the
environment template recommends Vertex mode. Firebase's
[model lifecycle table](https://firebase.google.com/docs/ai-logic/faq-and-troubleshooting)
lists that model as retired on the Vertex/Agent Platform provider since
20 October 2026. The detector catches failures and falls back, so this is not
necessarily a whole-app crash, but language detection will not work as advertised
with that default provider/model combination.

The browser explicitly uses GoogleAIBackend with `gemini-2.5-flash`. Starting
1 December 2026, that provider routes this alias to `gemini-3.5-flash-lite`.
This is a behavior/configuration migration risk during judging, not a claim that
today's browser endpoint is already shut down. Choose a supported explicit model
and test its actual output when credentials are configured. See the
[Firebase release notice](https://firebase.google.com/support/releases).

### 5. Medium: setup instructions and runtime claims are not fully aligned

Documentation exists and is substantial: README, architecture, environment
template, disclosure, provenance evidence, team declaration, third-party inventory,
license and submission checklist are present. The remaining problems are accuracy
and reproducibility, rather than a missing README.

| Gap | Evidence | Required correction |
| --- | --- | --- |
| Old Nano setup instructions | README 719 lists the older Prompt API flag; current Firebase setup uses `prompt-api-for-gemini-nano-multimodal-input`. | Update the supported Chrome/platform prerequisites and first-run download steps against the current guide. |
| App Check debug instructions incomplete in the main walkthrough | README 718 says set the debug flag; `.env.example` mentions registering the UUID, but the walkthrough does not explain obtaining and registering it. | Give a complete console/debug-token setup and describe an actual inference-source acceptance check. |
| Stale test count | README 726 and architecture 154 say 1,279. | Use the audited 1,286 passed plus one conditional skip, dated to this commit, or avoid hard-coded counts. |
| Contradictory implementation status | `docs/CITATIONS.md` 83 says proportionate deduction is NOT implemented; line 91 says it is modelled. | Reconcile the table with the implementation and keep policy-specific limitations explicit. |
| Unverified provider state remains in prose | Architecture 230 asserts sender template state; dashboard 692 says this deployment sends through a sandbox even in the no-provider run. | Use configuration-dependent status or conditional wording. |
| Setup paths are spread across files | README quick start assumes Make/Bash; Node is stated in the checklist, not at the main entry point. | Provide one judge walkthrough with Python/uv/Node prerequisites, Windows/Bash commands, seed/login steps and expected outputs. |

## Eligibility and submission evidence

The [official rules](https://firebasehybridaihackathon.devpost.com/rules) require
a functioning project, actual Firebase AI Logic use, public source with an
open-source license, a submission-period contribution summary for existing work,
English submission materials, and a publicly visible YouTube demonstration linked
from the entry. The first three minutes are the evaluated video window. A team
must consist of eligible members, list them on Devpost, and authorize a
representative. Working-project access may be a demo or test build; hosting is
encouraged rather than the only route.

What is recorded correctly:

- Public MIT repository and real Firebase imports/call sites.
- Exactly two declared team members: Nishant Maurya and Avika Bansal; Nishant is
  representative. Both are declared Indian college students and over 18.
- Existing renamed local project is disclosed; unknown original dates have not
  been invented. Related repositories, comparison limits and recorded changes
  have evidence links. Unknown dates alone do not prove an eligibility violation.
- Simulated insurer/payment behavior and the receipt-checkpoint trust limit are
  documented. A shared demo bearer is not presented as per-user identity.

Still unverified outside this repository:

- Public functioning-demo YouTube URL, English narration/subtitles, and the final
  video matching the submitted implementation.
- Submitted Devpost entry, selected Web/Chrome platform, Firebase usage description,
  contribution summary, test instructions and both team members added.
- Applicable third-party permissions and remaining residence/employment/conflict
  eligibility declarations. Student/age declarations do not establish every rule.
- Free working-demo/test-build access throughout judging.

The entry deadline is **1 December 2026, 03:30 IST**. Judging access must continue
through **17 December 2026, 03:30 IST**, based on the official Pacific times.

## Close-out order

1. Fix the case loader race and add a delayed-response regression.
2. Implement first-run device initialization and explicit supported-language routing.
3. Migrate model defaults and reconcile the setup/docs/status claims.
4. With credentials configured, demonstrate actual on-device and cloud responses
   with App Check and preserve the SDK-reported inference source.
5. Complete the external video/Devpost/team/access checklist.

The audit did not modify application logic. Passing offline tests is evidence for
the tested paths, not proof of all provider behavior or a guarantee of eligibility.
