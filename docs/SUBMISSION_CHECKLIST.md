# Submission checklist

Passing tests do not establish eligibility or a submitted entry.

- [x] Standard MIT LICENSE exists. Recheck public repository visibility at submission time.
- [ ] Author confirms ownership, third-party permissions and prior-work provenance. Legacy August dates are unverified.
- [ ] Author confirms the actual submission-period contributions in DISCLOSURE.md and Devpost.
- [ ] Demonstrate actual Firebase AI Logic on-device inference and cloud fallback with App Check using synthetic data. Record the actual inference source.
- [ ] Publish a functioning demo publicly on YouTube, at most three minutes, with English narration or subtitles; add its URL to Devpost.
- [ ] Complete Devpost description, platform, repository URL and testing instructions, and submit. A draft is not a submission.
- [ ] Provide a free working demo or test build throughout judging. Hosting is encouraged. Test-build installation instructions must work.
- [ ] Confirm personal/team eligibility, team listing, ownership and applicable permissions. Include no secrets or private patient records.

Official rules: https://firebasehybridaihackathon.devpost.com/rules
Deadline: November 30, 2026, 2:00 PM PST (December 1, 2026, 03:30 IST). Recheck the official page before submitting.

## Reproduction and limits

Run `uv sync --frozen --extra dev`, tests and the offline demo from the README. Set `PYTHONUTF8=1` on Windows. Node is required for behavioral JavaScript regressions. The shared demo bearer is for synthetic records, not per-user identity. Every POST /api/intake requires a family bearer, including new cases. Offline tests do not prove real model calls.

Receipt and count/head checkpoint commit atomically. Tail deletion is detected against the checkpoint. Old chains without a checkpoint fail closed; do not automatically bless their visible prefix. Database-wide rollback including checkpoints requires an external trust anchor, which is not implemented.
