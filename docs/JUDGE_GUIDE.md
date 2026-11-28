# Judge setup and verification

This guide separates a reproducible synthetic offline demonstration from the
Firebase execution that needs a configured project. No hosted URL or recorded
live Firebase success is claimed. Configuration, deployment and video are
assigned to Avika Bansal; Nishant Maurya is the team representative.

## Prerequisites

- Git, Python 3.12 or later, [uv](https://docs.astral.sh/uv/getting-started/installation/),
  and Node.js 22 (used by behavioral JavaScript regression tests).
- Internet for the first dependency installation. The offline suite and
  deterministic demo do not need model credentials.
- Docker Desktop with its Linux engine running only for the container check.
- For Firebase: an enabled Firebase project, registered Web App, Firebase AI Logic
  using **Gemini Developer API**, App Check, and network access to Firebase/Google.
  Backend Vertex credentials are separate from browser Firebase configuration.
- For Nano: compatible hardware and desktop Chrome 139+. A mobile phone can test
  cloud fallback, but cannot demonstrate this web app's on-device Nano path.

Use synthetic records throughout judging. The shared demo credential is public
and grants access to synthetic demo records; it is not private patient identity.

## Install and run without API keys

Clone the repository and enter its root. Do not copy `.env.example` unchanged for
the offline run: its production-oriented defaults include Firestore and models.
The explicit environment values below override an existing local env file.

PowerShell:

```powershell
git clone https://github.com/Niss54/KinGuard.git
cd KinGuard
uv sync --frozen --extra dev
$env:PYTHONUTF8 = "1"
$env:KINGUARD_STORE_BACKEND = "memory"
$env:KINGUARD_WHATSAPP_MODE = "off"
$env:KINGUARD_VOICE_MODE = "off"
$env:KINGUARD_TRANSLATE_MODE = "off"
$env:KINGUARD_DETECT_LANGUAGE_MODE = "off"
$env:KINGUARD_PUBSUB_ENABLED = "false"
$env:KINGUARD_PAYMENT_MODE = "simulated"
$env:KINGUARD_TPA_MODE = "simulated"
$env:KINGUARD_DEMO_TOKEN = "kinguard-demo-family-token"
uv run ruff check kinguard tests scripts
uv run pytest -q
uv run python scripts/demo_spine.py
uv run uvicorn kinguard.server:app --host 127.0.0.1 --port 8080
```

Bash (macOS/Linux/WSL):

```bash
git clone https://github.com/Niss54/KinGuard.git
cd KinGuard
uv sync --frozen --extra dev
export PYTHONUTF8=1 KINGUARD_STORE_BACKEND=memory
export KINGUARD_WHATSAPP_MODE=off KINGUARD_VOICE_MODE=off
export KINGUARD_TRANSLATE_MODE=off KINGUARD_DETECT_LANGUAGE_MODE=off
export KINGUARD_PUBSUB_ENABLED=false KINGUARD_PAYMENT_MODE=simulated
export KINGUARD_TPA_MODE=simulated
export KINGUARD_DEMO_TOKEN=kinguard-demo-family-token
uv run ruff check kinguard tests scripts
uv run pytest -q
uv run python scripts/demo_spine.py
uv run uvicorn kinguard.server:app --host 127.0.0.1 --port 8080
```

Expected: lint passes, offline tests pass (the live Memory Bank test skips without
its optional configuration), and the spine prints a successful chain verification
followed by detected tampering in its deliberately modified example. The server
keeps running until Ctrl+C. The memory store resets when the process restarts.

## Seed, sign in and inspect the result

1. Open `http://127.0.0.1:8080/app`.
2. Click **Seed a synthetic episode**, then **Use the demo credential** at the
   access gate. If the UI is already
   showing a case, the terminal seed below gives a fresh case ID to open.
3. Inspect Now, Brief, Routing, Record, Claim and Audit. Bills and payments are
   synthetic/simulated. A receipt does not establish real payment or delivery.
4. Open intake, enter `chest pain, sweating`, and use step 2 (deterministic triage).
   Expect HIGH. Repeat with `mild fever and cough`; expect LOW. No Firebase response
   is expected until Firebase is configured. Step 1 should explain missing setup.
5. Switch between two case IDs while a refresh is pending. All visible brief,
   bill and parent data must belong to the selected case. Sign-out must clear
   protected data; a delayed response must not restore it.

Terminal check, while the server runs in the first terminal:

```powershell
$base = "http://127.0.0.1:8080"
Invoke-RestMethod "$base/api/healthz"
$seed = Invoke-RestMethod -Method Post "$base/api/demo/seed?episode=true"
$seed.case_id
$headers = @{ Authorization = "Bearer kinguard-demo-family-token" }
Invoke-RestMethod "$base/api/cases/$($seed.case_id)/brief" -Headers $headers
Invoke-RestMethod "$base/api/cases/$($seed.case_id)/verify"
```

Bash equivalent (uses Python, no `jq` prerequisite):

```bash
base=http://127.0.0.1:8080
curl -fsS "$base/api/healthz"
case_id=$(curl -fsS -X POST "$base/api/demo/seed?episode=true" |
  uv run python -c 'import json,sys; print(json.load(sys.stdin)["case_id"])')
printf '%s\n' "$case_id"
curl -fsS -H 'Authorization: Bearer kinguard-demo-family-token' "$base/api/cases/$case_id/brief"
curl -fsS "$base/api/cases/$case_id/verify"
```

Expected: HTTP 200, a case ID, an authorized brief and `verified: true`. Without
the bearer the brief returns 401. Verification is intentionally public and does
not return the medical record. New and existing intake requests both require
family authorization. `verified` checks integrity against the stored head/count;
rollback of the entire database including checkpoints needs an external anchor,
which this prototype does not implement.

## Firebase and App Check setup (Avika)

1. In Firebase Console, register a Web App and enable AI Logic with **Gemini
   Developer API**. Populate the matching public web configuration fields from
   `.env.example` in ignored `.local.env`. At minimum the API key, project ID and
   app ID must be present. Set `KINGUARD_FIREBASE_MODEL=gemini-3.5-flash-lite`.
   Remove old model overrides in shell/deployment configuration too.
2. For local development set `KINGUARD_FIREBASE_APPCHECK_DEBUG=true` and restart
   the server. A blank reCAPTCHA site key is supported in this debug mode.
3. Open browser developer tools Console, reload `/app`, and copy the **App Check
   debug token UUID** printed by Firebase. It is not the Firebase web API key.
4. Firebase Console > App Check > Apps > the Web App's menu > **Manage debug
   tokens** > Add debug token. Give this browser a label and save the UUID.
5. Reload and attempt a cloud request using Mixed/Tamil/Hindi/unsure input.
   Expect actual generated content and the **Cloud Fallback** source badge. A
   configured badge alone is not a successful request. For 401/403 errors check
   token registration against the same project/app, provider enablement, domain
   restrictions and quota. Do not disable App Check to conceal failures.
6. Treat the debug token as a credential. Keep it out of Git, screenshots and
   video; revoke it after use. For the public deployment set debug **false**, add
   a reCAPTCHA Enterprise site key, register the deployment domain and verify
   production App Check. Do not ship a public debug-token walkthrough as access.

See [Firebase debug provider instructions](https://firebase.google.com/docs/app-check/web/debug-provider)
and [Firebase hybrid setup](https://firebase.google.com/docs/ai-logic/hybrid/web/get-started).

## Fresh-browser Nano and multilingual acceptance (Avika)

Enable `chrome://flags/#prompt-api-for-gemini-nano-multimodal-input` in desktop
Chrome and relaunch, following the current Firebase setup guide. Use a compatible
machine with space for the model download. On a fresh Chrome profile:

| Action | Required evidence |
| --- | --- |
| Select **English (prefer on-device)**, enter `mild fever and cough`, click Normalise | Download starts from that click, progress is visible, and the request waits for initialization. After completion, valid symptom JSON and actual `on_device` source are shown. |
| Use Tamil/Hindi/Tanglish input with the default mixed-language selection | Actual `in_cloud` response. These requests use a distinct `ONLY_IN_CLOUD` model, even when Nano is already available. |
| Use Tamil/Hindi explanation buttons | Cloud result in the requested language, with content checked against the displayed record. |
| Use an unsupported browser/device with English selected | Cloud response after Nano is unavailable; no invented on-device badge. |
| Invalid/unregistered App Check token | A visible request error, never a fabricated success. |
| Change text/language or case while a response is pending | Old normalized results and explanations do not appear in the new input/case. |
| Writable clinician handoff, same language choices | Same initialization/routing rules; edited note fields are not overwritten by a delayed extraction. |

Indic-script text forces cloud even when English was selected. Romanised Tamil or
Hindi cannot reliably be detected from spelling; keep mixed input on the default
selection. Client redaction is heuristic and can miss identifiers. Cloud record
explanations transmit the selected summary snapshot; do not describe that as zero
server exposure. All AI output is advisory and requires checking.

The backend language detector also defaults to `gemini-3.5-flash-lite` and accepts
only its documented language-code allowlist. Verify representative English, Hindi,
Tamil and uncertain examples with the configured backend before recording; empty
or unsupported outputs fail closed. Model migrations can change output quality.
The detector omits unsupported sampling overrides and requests minimal thinking;
see the [model's migration notes](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-5-flash-lite).

## Docker

From the repository root, with Docker's Linux engine running:

```text
docker build -t kinguard:submission .
docker run --rm --name kinguard-submission -p 127.0.0.1:8080:8080 -e KINGUARD_STORE_BACKEND=memory -e KINGUARD_WHATSAPP_MODE=off -e KINGUARD_TRANSLATE_MODE=off -e KINGUARD_DETECT_LANGUAGE_MODE=off kinguard:submission
```

Repeat the seed/brief/verify checks above. This does not supply Firebase settings
to the image. The optional clinic booker has a separate `booker/Dockerfile`; it is
not required for the offline intake demo. Deployment details: [Cloud Run setup](../infra/DEPLOYED.md).

## Evidence to attach before submission

- Avika: working deployed URL or accessible test build, production App Check,
  actual Firebase on-device/cloud evidence, selected model IDs and tested Chrome
  version. Check generated outputs, not just connection success.
- Avika: public functioning-demo YouTube URL, English narration/subtitles,
  presentation at most three minutes. Show real results with synthetic data.
- Nishant and Avika: both listed on Devpost; accurate [prior-work disclosure](../DISCLOSURE.md),
  [third-party inventory](THIRD_PARTY.md), remaining permission/eligibility
  declarations, platform selection and a submitted entry.
- Verify free testing access throughout judging. A repository, video draft or
  unsubmitted Devpost draft does not establish that the entry is complete.

Track these in the [submission checklist](SUBMISSION_CHECKLIST.md). No code test
can certify personal eligibility, unseen third-party rights or an external upload.
