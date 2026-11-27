# Submission checklist

Passing tests do not establish eligibility or a submitted entry.

- [x] Standard MIT LICENSE exists. Recheck public repository visibility at submission time.
- [x] Nishant confirms the project belongs to Nishant Maurya and Avika Bansal, with exactly two team members.
- [x] Nishant confirms both members are Indian college students, both over 18; Nishant is team representative. See [team declaration](TEAM.md).
- [x] Disclose the renamed existing local project; its original name/date are not recalled. Do not claim all work was created from scratch in the contest.
- [x] Document related GitHub projects, comparison limits and commit-linked changes in [provenance evidence](PROVENANCE_EVIDENCE.md) and [DISCLOSURE.md](../DISCLOSURE.md).
- [x] Inventory dependencies, fonts, design references and demo assets in [third-party materials](THIRD_PARTY.md).
- [ ] Confirm applicable third-party permissions and disclose any additional copied/adapted material not already identified in the inventory. Unavailable legacy references are explicitly marked unconfirmed.
- [ ] Include the accurate prior-work disclosure and submission-period change summary in Devpost.
- [ ] Demonstrate actual Firebase AI Logic on-device inference and cloud fallback with App Check using synthetic data. Record the actual inference source.
- [ ] Publish a functioning demo publicly on YouTube, at most three minutes, with English narration or subtitles; add its URL to Devpost.
- [ ] Complete Devpost description, platform, repository URL and testing instructions, and submit. A draft is not a submission.
- [ ] Provide a free working demo or test build throughout judging. Hosting is encouraged. Test-build installation instructions must work.
- [ ] Both members review the remaining residence, sanctions, employment/conflict and applicable permission conditions in the official rules. The recorded age/student declarations do not certify all eligibility conditions.
- [ ] Add both team members to the Devpost project and identify Nishant as representative. Repository credits alone do not do this.
- [ ] Check the final repository, video and testing instructions contain no secrets or private patient records.

Official rules: https://firebasehybridaihackathon.devpost.com/rules
Deadline: November 30, 2026, 2:00 PM PST (December 1, 2026, 03:30 IST). Recheck the official page before submitting.

## Reproduction and limits

Run `uv sync --frozen --extra dev`, tests and the offline demo from the README. Set `PYTHONUTF8=1` on Windows. Node is required for behavioral JavaScript regressions. The shared demo bearer is for synthetic records, not per-user identity. Every POST /api/intake requires a family bearer, including new cases. Offline tests do not prove real model calls.

Receipt and count/head checkpoint commit atomically. Tail deletion is detected against the checkpoint. Old chains without a checkpoint fail closed; do not automatically bless their visible prefix. Database-wide rollback including checkpoints requires an external trust anchor, which is not implemented.
