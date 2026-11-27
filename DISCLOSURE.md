# Firebase Hybrid AI Hackathon Submission Disclosure

## Firebase Hybrid AI Hackathon (https://firebasehybridaihackathon.devpost.com/)

Submitted under the **Firebase Hybrid AI Hackathon** guidelines:

* **Core Platform & Architecture:** The FastAPI + Google ADK multi-agent backend, Ed25519 provenance chain, deterministic severity/comms/payment/booking guards, WhatsApp integration, Playwright clinic booker, and `/app` & `/handoff/{token}` interfaces.
* **Core Value:** An eldercare & Indian health-insurance coordination engine where deterministic Python code holds life-safety, DPDP privacy, and financial boundaries.
* **Firebase Hybrid AI & Security Implementation (new in this submission):**
  1. `GET /api/firebase-config` + `KINGUARD_FIREBASE_*` environment and Cloud Run deployment configuration.
  2. Client-side **Firebase AI Logic (`firebase/ai` v13.4.0, `InferenceMode.PREFER_ON_DEVICE`)** and **Firebase App Check** integration in `/app` and `/handoff/{token}`:
     - Deterministic client-side PII redaction (`maskPII`) executed in-browser before sending symptom text to any model or `/api/intake`, paired with advisory symptom normalisation (`intake.hybrid_normalized` receipt). On-device Gemini Nano targets supported desktop Chrome (English); Tamil/Tanglish/Hindi and mobile/non-Nano browsers route through Cloud Gemini (`gemini-2.5-flash`) fallback gated by App Check.
     - Plain-language & multilingual (English/Tamil/Hindi) Arrival, Record, and Claim companion summaries (local on-device in desktop Chrome when Nano supports the language; App-Check-gated Cloud Gemini fallback otherwise).
     - Bedside clinician order & mobility extraction prior to explicit human confirmation (`PREFER_ON_DEVICE` desktop Chrome Nano or Cloud Gemini fallback).
  3. Authenticated web document/bill ingestion endpoint `POST /api/cases/{case_id}/documents/ingest`.
  4. Server-side hardening: parent-case ownership validation on `POST /api/intake` / `run_triage`, authentication enforcement on ADK session/execution endpoints, atomic receipt-and-checkpoint persistence preventing concurrent overwrites, and trusted signer public-key pinning in `verify_chain`.
  5. Hybrid AI & security/provenance test coverage (`tests/test_hybrid_ai_surface.py`, `tests/test_security_and_provenance.py`).

---

## Prior Work & Project Provenance

## Summary

The repository contains an existing eldercare coordination core and Firebase hybrid inference additions. Git timestamps alone do not establish when the original core was authored. Legacy material mentions August 2026, but those dates, deployment anecdotes and original provenance are unverified. They must not be presented as confirmed execution evidence.

The intended submission contributions are Firebase AI Logic/App Check, web document ingestion and the security/integrity fixes listed above. Before submitting, the author must confirm which work was completed during the contest window, identify incorporated third-party work, and confirm ownership. This is a disclosure draft, not proof of those facts.

**Current status:** Credentials, real provider verification and deployment are pending. No active public demo, video publication or Devpost submission is claimed.

## Pattern 1 — confidence-gated evidence decisioning (STEP_UP)

**Prior work:** Verigate (github.com/Niss54/verigate) — deterministic AI agent
payment authorization, where an action below a confidence threshold triggers a
step-up rather than proceeding or failing outright.

**What was reused:** the idea. A three-way gate (`PASS` / `STEP_UP` / `BLOCK`)
driven by a weighted completeness score, where the middle state means "gather
more before proceeding" rather than "reject".

**What is new here:** the entire implementation. The scoring dimensions are
claim-packet-specific (policy number, admission summary, itemised bills,
diagnostics, attached documents, matched policy clauses), the thresholds are
tuned to first-pass claim approval, and the enrichment actions are drawn from
the parent's health knowledge base. See `kinguard/tools/evidence_tools.py`.

**Important scoping note:** in KinGuard, STEP_UP operates on the packet *we*
submit. It is not inside the insurer's adjudication loop and it does not
pre-empt a denial. Its job is pre-submission enrichment to raise first-pass
approval odds. Describing it as "prevents denials" would overstate what the
agent controls, and the agent's own instructions forbid that phrasing.

## Pattern 2 — signed hash-chain provenance

**Prior work:** GenuProof (github.com/Niss54/genuproof) — anti-counterfeiting and
product authentication, using a hash-chained ledger of signed events in a
single-table PK/SK Firestore layout.

**What was reused:** the idea. Each record's hash covers the previous record's
hash, so a silent edit to an earlier entry invalidates every entry after it; and
the single-table PK/SK layout that makes one entity's whole chain a single range
read.

**What is new here:** the entire implementation. `kinguard/provenance/chain.py`
is written from scratch — Ed25519 signatures over a canonical JSON encoding, a
receipt schema built around agent decisions (`triage.decision`, `evidence.assessed`,
`claim.submitted`, `comms.blocked`), and a verifier that distinguishes an altered
payload from a dropped receipt from a bad signature.

## The simulated adjudicator's rules are our construction

`kinguard/tpa/adjudicator.py` decides PASS / PARTIAL / QUERY / DENY using
deterministic local rules. Those rules are **our own construction from published
convention**, not any insurer's or TPA's actual adjudication logic, and no
insurer was consulted.

Specifically, the per-day sub-limit percentages (room rent 1% of sum insured per
day, ICU 2% per day) are the conventional caps widely used across Indian health
policies. They are applied here as a plausible stand-in so the claim path
produces defensible arithmetic. **No real policy schedule was copied**, and the
demo seeds no bespoke sub-limit values — the caps derive from the convention
applied to the sum insured already on the synthetic policy, so the numbers land
wherever the arithmetic puts them.

A richer adjudicator looks more like a real integration than the earlier stub
did, so the label works harder: every adjudication payload, receipt, and agent
report carries `SIMULATED — deterministic local rules, not an insurer`.

## Gemini is used for translation, and only as a rendering of a record

Outbound Tamil is a Gemini call, and that is worth stating precisely because
the failure mode is subtle. The model is never asked what to say. It is handed
text that is already on the record — a bill summary read off a photograph, a
fixed check-in template, a status line — and asked to say that same thing in
Tamil.

Three properties are enforced in code rather than in the prompt:

- `translate.render` **refuses** a call with no source text or no named source
  record. There is no path that produces Tamil for text nobody wrote down.
- The compliance gate rules on the **English** before anything is rendered.
  `CLINICAL_PATTERNS` are English regexes and would not recognise a lab value
  in Tamil script, so gating after translation would have been a hole the width
  of the alphabet.
- Every failure — timeout, empty reply, engine switched off — returns the
  recorded English with a line saying it could not be rendered. There is no
  mode that produces a partial or guessed translation.

The English record remains the source of truth. The Tamil is derived from it,
says so in the message, and the receipt carries the SHA-256 of the English the
gate ruled on.

## Recovery check-ins present and record. They never advise or diagnose

The recovery feature asks a fixed question once a day and stores the answer. It
holds no opinion about the answer, and the check-in record has no field an
opinion could be written into — a test asserts the exact field set, and fails
the day somebody adds `severity`.

One thing deliberately **is** allowed to happen to a concerning answer: the
deterministic severity table already used by every other intake sees it, and if
a red flag matches, a case opens and the family is told. That is not the
recovery feature deciding anything — it is the recovery feature declining to
make an exception. The alert it produces reports what was heard and names no
cause, no condition and no course of action beyond "call her, and if you cannot,
call 108".

The phase label on a check-in (`acute` / `recovery`) is computed from stored
state — an open window, a prompt sent within 24 hours — and never from reading
her words.

## Third-party dependencies

Standard open-source libraries, unmodified, declared in `pyproject.toml`:
`google-adk`, `google-cloud-firestore`, `google-cloud-pubsub`, `pydantic`,
`cryptography`, `fastapi`, `uvicorn`, `python-dotenv`.

## Repository history

Commit history records checkout changes, not original authorship dates. Original core provenance and submission-period contributions require author confirmation. See [submission checklist](docs/SUBMISSION_CHECKLIST.md).
