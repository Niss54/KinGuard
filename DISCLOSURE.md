# Firebase Hybrid AI Hackathon submission disclosure

Updated 27 November 2026. This disclosure separates the team's statements,
observable repository evidence, and runtime verification still pending.

## Team and ownership

KinGuard is submitted by **Nishant Maurya and Avika Bansal**, with **Nishant
Maurya as team representative**. There are exactly two team members. Nishant
confirms that the project belongs to both of them, that both are Indian college
students, and that both are over 18. These are participant declarations, not
facts inferred from GitHub. See [team declaration](docs/TEAM.md).

## Existing work and reuse

Nishant describes KinGuard as the same existing local project folder renamed
and modified. He does not recall the earlier folder name or original creation
date. We therefore disclose the inherited eldercare core as existing work and
do not claim that every part was created from scratch during this contest.

That baseline includes the eldercare/insurance domain, deterministic triage,
communication and payment/booking guards, ADK coordination, signed receipts,
provider adapters and dashboard foundations. Git records when files entered
this repository; it cannot recover when an earlier local version was written.

Public GitHub also contains Nishant's earlier **eldercare** and **Care-link**
projects, dating to March and August 2026 respectively. Their subject matter is
related. Comparing their inspected snapshots against KinGuard found no identical
non-empty files, including binary assets. This does not establish absence of
adapted code or prove that either repository is the renamed folder's source.
Pinned sources, comparison scope and dates are in the
[provenance evidence](docs/PROVENANCE_EVIDENCE.md).

Earlier text named **Verigate** and **GenuProof** as sources for STEP_UP and
signed-chain ideas. Those repository links could not be resolved, and their
relationship to this folder remains unconfirmed. We retain this notice of the
legacy attribution but withdraw the unsupported claims that reuse was "idea
only" or that the implementations were independently written from scratch.
The alleged August prototype and live-service anecdotes are not submission
execution evidence. The original local creation date remains unknown.

## Submission-period work and recorded changes

The current GitHub repository was created on 24 November 2026. Its history
records the following within the contest period. First appearances in Git are
identified as recorded additions, not proof of first authorship.

| Work | Evidence and scope |
| --- | --- |
| Firebase hybrid interface, recorded 25 November | [Dashboard commit](https://github.com/Niss54/KinGuard/commit/d0ce64e) and [server commit](https://github.com/Niss54/KinGuard/commit/07c8d4a): Firebase AI Logic 13.4.0, App Check, configuration endpoint, advisory symptom normalization and companion summaries, bedside extraction, and authenticated web document ingestion. Earlier local implementation dates are unknown. |
| Build, authentication and privacy fixes, 27 November | [2c71870](https://github.com/Niss54/KinGuard/commit/2c71870) and [3ebbcc3](https://github.com/Niss54/KinGuard/commit/3ebbcc3): MIT license, dependency lock repair, App Check debug initialization, configuration alignment, parent/case and ADK authentication, redaction before symptom transmission, and trusted signer verification. These are reviewable changes against the prior committed version. |
| Intake and receipt-integrity fixes, 27 November | [e08e9e7](https://github.com/Niss54/KinGuard/commit/e08e9e7): symptom-preserving redaction, case-scoped async AI results, authorization for new-case intake, atomic receipt count/head checkpoints and behavioral regressions. |
| Submission documentation, 27 November | GitHub-linked provenance evidence, two-person team/representative declaration, asset/dependency inventory, and removal of unsupported live-verification claims. |

Firebase inference is advisory. The implementation requests on-device inference
on supported desktop Chrome with cloud fallback. Language and device support
must be demonstrated on the actual test environment; mobile, Tamil and Hindi
execution must not be described as verified local inference. Direct-identifier
masking is a best-effort regex filter, not a guarantee of anonymization. Cloud
fallback and configured backend model features can transmit clinical content.

## Third-party code, assets and tools

Dependencies are declared in `pyproject.toml`, `uv.lock` and
`booker/requirements.txt`; the browser loads Firebase and Google Fonts.
Google Stitch is credited for design references, and AI coding assistance was
used in the current remediation. Synthetic documents, architecture generators,
UI previews, the logo and external data references are catalogued in
[third-party materials](docs/THIRD_PARTY.md). Upstream rights are retained.
The team's ownership declaration does not replace applicable third-party terms.

## Simulations and limits

The insurer/TPA adjudicator uses local demo rules, not an insurer's decision
service. Seeded hospital capability and empanelment data are not a live feed.
Recovery check-ins record answers and route matching red flags through the
existing deterministic intake logic; they do not diagnose. Outbound translation
renders an existing record and does not replace its source text.

Receipt signatures and a persisted count/head checkpoint detect the tested
edits and missing-tail cases. A database-wide rollback including the checkpoint
requires an external anchor, which is not implemented.

## Evidence and setup status

[CI at e08e9e7](https://github.com/Niss54/KinGuard/actions/runs/45993764329)
passed installation, lint, tests and the offline demo. API credentials, real
provider/Firebase execution and deployment remain pending setup/verification.
No public demo video or completed Devpost entry is claimed. See the
[submission checklist](docs/SUBMISSION_CHECKLIST.md) for the separate entry steps.
