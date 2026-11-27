# Repository provenance evidence

Checked on 27 November 2026 against public GitHub and KinGuard commit
`e08e9e7f9402295d6f335dd5479fa947d5370e36`. This records observable repository
history, not a certification of original authorship dates or third-party rights.

Nishant confirmed that the same local project folder was renamed and modified,
but he does not remember its earlier name or creation date. The disclosure
therefore treats the inherited core as existing work without assigning an
invented date. Public history does not identify the earlier local folder.

## Earlier related projects

| Repository | GitHub repository creation (UTC) | Earliest commit returned by the default-branch history | Relationship supported by inspection |
| --- | --- | --- | --- |
| [Niss54/eldercare](https://github.com/Niss54/eldercare) | 25 March 2026, 15:58:37 | [2042ca81](https://github.com/Niss54/eldercare/commit/2042ca81df7fca2ebe8e72407bdb62d63dfa99fe), 25 March 2026 | Earlier work on family/elder coordination, consent, reminders and emergency alerts. Its FastAPI/Next.js architecture differs from KinGuard's ADK/Firestore/browser dashboard. |
| [Niss54/Care-link](https://github.com/Niss54/Care-link) | 7 August 2026, 18:17:08 | [c00a8e67](https://github.com/Niss54/Care-link/commit/c00a8e672c3ca6facd126580835aac1fad4e9a03), 8 August 2026 | Earlier clinical AI, triage, communication and Indic-language work. Its React/LangGraph/Supabase stack differs from KinGuard. |
| [Niss54/KinGuard](https://github.com/Niss54/KinGuard) | 24 November 2026, 14:04:17 | [f9297f63](https://github.com/Niss54/KinGuard/commit/f9297f630d17bbfd99a8b368daa537f918e17bba), 24 November 2026 | Current submission repository. Repository creation is not the date every included file was originally written. |

Creation dates come from each repository's public GitHub API metadata:
[eldercare](https://api.github.com/repos/Niss54/eldercare),
[Care-link](https://api.github.com/repos/Niss54/Care-link),
[KinGuard](https://api.github.com/repos/Niss54/KinGuard).
Earlier related projects are disclosed as background; inspection did not establish
that either repository supplied KinGuard's code.

## Comparison scope and result

Compared the 224 tracked Git blobs at KinGuard `e08e9e7` with the complete,
non-truncated recursive Git trees for:

- [eldercare at f8a861cd](https://github.com/Niss54/eldercare/tree/f8a861cd8ce42680828371b9bae81ac0e1315576): 356 blobs.
- [Care-link at 5b05de55](https://github.com/Niss54/Care-link/tree/5b05de55a1eb211404149934babc714113520339): 178 blobs.

No identical non-empty Git blobs matched, including tracked binary assets.
The READMEs and directory structures were also inspected. Exact blob comparison
does not detect adapted snippets, renamed symbols, regenerated assets, older
deleted files or work outside these snapshots. It does not prove zero reuse.
Reproduce using `git ls-tree -r <commit>` and compare blob SHA columns, excluding
the empty blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`.

The old disclosure named `Niss54/verigate` and `Niss54/genuproof`. Both repository
lookups returned 404 on the check date. Account-scoped code searches for those
names returned only KinGuard references. They may be private, renamed or erroneous;
their existence, ownership and claimed reuse are not established. The earlier
"idea only" and "written from scratch" assertions are therefore withdrawn, not
silently treated as verified. The core's alleged August prototype date is also
unsubstantiated. An August date printed on a synthetic report is not a development
timestamp.

## Changes recorded during the contest window

The [official rules](https://firebasehybridaihackathon.devpost.com/rules) set the
submission period from 11 to 30 November 2026, Pacific Time. The following are
recorded KinGuard changes within that period. A first appearance in Git is not
proof that all underlying work was first authored then.

| Recorded date (UTC) | Evidence | Scope |
| --- | --- | --- |
| 24 November | [Configuration](https://github.com/Niss54/KinGuard/commit/f9297f63), [receipt primitives](https://github.com/Niss54/KinGuard/commit/457f055), [triage](https://github.com/Niss54/KinGuard/commit/6377c8c) | Initial recorded backend foundation: configuration, receipt chain, triage, communications and booking modules. |
| 25 November | [Dashboard](https://github.com/Niss54/KinGuard/commit/d0ce64e), [HTTP services](https://github.com/Niss54/KinGuard/commit/07c8d4a) | Firebase AI Logic dashboard, Firebase configuration endpoint and hybrid HTTP surfaces, including web ingestion. |
| 25 November | [Tests](https://github.com/Niss54/KinGuard/commit/d031f6e), [docs and assets](https://github.com/Niss54/KinGuard/commit/c8d8165) | Test suites, documentation, architecture diagrams and design previews entered the repository. Original asset creation times are not established. |
| 27 November | [License/build/security](https://github.com/Niss54/KinGuard/commit/2c71870), [configuration/auth](https://github.com/Niss54/KinGuard/commit/3ebbcc3) | Added MIT license, repaired frozen dependency installation, hardened App Check, authentication, intake ownership and signer validation; aligned configuration and docs. |
| 27 November | [Submission regressions](https://github.com/Niss54/KinGuard/commit/e08e9e7) | Preserved emergency symptoms during redaction, rejected stale AI results after case switches, authenticated new-case intake, and added atomic receipt count/head checkpoints with regression tests. |

## Execution evidence

[GitHub CI for e08e9e7](https://github.com/Niss54/KinGuard/actions/runs/45993764329)
passed frozen dependency installation, lint, tests and the offline demo. This
supports the deterministic code paths exercised there. It does not demonstrate
real Firebase inference, provider delivery, a deployed service or a published
submission video. See the [submission checklist](SUBMISSION_CHECKLIST.md).
