#!/usr/bin/env bash
# Deploy KinGuard to Cloud Run.
#
#   ./infra/deploy_cloud_run.sh
#
# Requires: gcloud authenticated, KINGUARD_SIGNING_KEY_B64 set to a stable key
# (an ephemeral key means receipt chains stop verifying across restarts).
#
# Public access uses --no-invoker-iam-check rather than --allow-unauthenticated.
# The latter grants roles/run.invoker to allUsers, which this organization's
# domain-restricted-sharing policy (constraints/iam.allowedPolicyMemberDomains)
# refuses — and the deploy reports that refusal as a warning, not an error, so
# the service silently ends up unreachable. Disabling the invoker check is
# Google's documented alternative for projects under DRS, and it is scoped to
# this one service instead of weakening an org-wide control.
#
# To make the service private again after judging:
#   gcloud run services update kinguard --region "$REGION" --invoker-iam-check
set -euo pipefail

# --no-cpu-throttling is load-bearing, not a performance tweak. Reading a
# photographed bill takes about fifteen seconds and Twilio abandons a webhook at
# roughly the same mark, so the webhook acknowledges immediately and finishes in
# a background task. Cloud Run throttles CPU once the response returns, which
# would leave that task suspended and the family holding an acknowledgement that
# never became an answer.
#
# Do NOT put comments between the continued lines of the gcloud command below.
# A backslash-newline joins the lines, so a `#` there comments out every flag
# that follows it — silently, and `bash -n` will not tell you.

# NOTE: the separator is ^|^ and NOT the more usual ^@^. An email address
# contains @, so KINGUARD_DEMO_FAMILY_EMAIL split mid-value and gcloud rejected the
# whole flag with "Bad syntax for dict arg: [kinguard.ai]". Any separator
# here has to be a character that appears in NO value: not @ (emails), not + or
# / or = (base64 keys, phone numbers), not : or . or - (URLs). Pipe is safe.
#
# NOTE: --set-env-vars must appear ONCE. gcloud replaces rather than merges on
# a repeat, so a second flag silently discards everything the first one set.
# The "^@^" prefix changes the delimiter to @ so values may contain commas.

PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-kinguard-hack}"
REGION="${KINGUARD_REGION:-asia-south1}"
SERVICE="${KINGUARD_SERVICE:-kinguard}"
MODEL="${KINGUARD_MODEL:-gemini-3.5-flash}"

if [[ -z "${KINGUARD_SIGNING_KEY_B64:-}" ]]; then
  echo "KINGUARD_SIGNING_KEY_B64 is not set." >&2
  echo "Mint one with: uv run python -m kinguard.provenance.keygen" >&2
  echo "Deploying without it would give every revision a fresh signing key," >&2
  echo "so receipts written before a restart would stop verifying." >&2
  exit 1
fi

echo "Deploying ${SERVICE} to ${REGION} in ${PROJECT_ID} (model ${MODEL})"

gcloud run deploy "${SERVICE}" \
  --source . \
  --project "${PROJECT_ID}" \
  --region "${REGION}" \
  --no-invoker-iam-check \
  --ingress all \
  --memory 1Gi \
  --cpu 1 \
  --timeout 600 \
  --no-cpu-throttling \
  --set-env-vars "^|^GOOGLE_GENAI_USE_VERTEXAI=TRUE|GOOGLE_CLOUD_PROJECT=${PROJECT_ID}|GOOGLE_CLOUD_LOCATION=global|KINGUARD_MODEL=${MODEL}|KINGUARD_STORE_BACKEND=firestore|KINGUARD_TPA_MODE=simulated|KINGUARD_WHATSAPP_MODE=${KINGUARD_WHATSAPP_MODE:-off}|KINGUARD_PUBSUB_ENABLED=${KINGUARD_PUBSUB_ENABLED:-false}|KINGUARD_DEMO_TOKEN=${KINGUARD_DEMO_TOKEN:-kinguard-demo-family-token}|KINGUARD_SIGNING_KEY_B64=${KINGUARD_SIGNING_KEY_B64}|KINGUARD_ARTIFACT_BUCKET=${KINGUARD_ARTIFACT_BUCKET:-}|KINGUARD_DEMO_FAMILY_E164=${KINGUARD_DEMO_FAMILY_E164:-+14155550142}|KINGUARD_MAPS_API_KEY=${KINGUARD_MAPS_API_KEY:-}|KINGUARD_PUBLIC_BASE_URL=${KINGUARD_PUBLIC_BASE_URL:-}|KINGUARD_VOICE_MODE=${KINGUARD_VOICE_MODE:-off}|TWILIO_VOICE_FROM=${TWILIO_VOICE_FROM:-}|TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID:-}|TWILIO_API_KEY_SID=${TWILIO_API_KEY_SID:-}|TWILIO_WHATSAPP_FROM=${TWILIO_WHATSAPP_FROM:-}|KINGUARD_GOOGLE_CLIENT_ID=${KINGUARD_GOOGLE_CLIENT_ID:-}|KINGUARD_DEMO_FAMILY_EMAIL=${KINGUARD_DEMO_FAMILY_EMAIL:-}|KINGUARD_DEMO_FAMILY_NAME=${KINGUARD_DEMO_FAMILY_NAME:-}|KINGUARD_TRANSLATE_MODE=${KINGUARD_TRANSLATE_MODE:-gemini}|KINGUARD_RECOVERY_WINDOW_DAYS=${KINGUARD_RECOVERY_WINDOW_DAYS:-14}|KINGUARD_RECOVERY_HOUR=${KINGUARD_RECOVERY_HOUR:-9}|KINGUARD_DEMO_PARENT_E164=${KINGUARD_DEMO_PARENT_E164:-}|KINGUARD_DEMO_PARENT_LANGUAGE=${KINGUARD_DEMO_PARENT_LANGUAGE:-ta}|KINGUARD_DEMO_FAMILY_LANGUAGE=${KINGUARD_DEMO_FAMILY_LANGUAGE:-en}|KINGUARD_DEMO_FAMILY_TZ=${KINGUARD_DEMO_FAMILY_TZ:-America/Los_Angeles}|KINGUARD_PAYMENT_MODE=${KINGUARD_PAYMENT_MODE:-simulated}|RAZORPAY_KEY_ID=${RAZORPAY_KEY_ID:-}|RAZORPAY_KEY_SECRET=${RAZORPAY_KEY_SECRET:-}|RAZORPAY_WEBHOOK_SECRET=${RAZORPAY_WEBHOOK_SECRET:-}|RAZORPAYX_KEY_ID=${RAZORPAYX_KEY_ID:-}|RAZORPAYX_KEY_SECRET=${RAZORPAYX_KEY_SECRET:-}|RAZORPAYX_ACCOUNT_NUMBER=${RAZORPAYX_ACCOUNT_NUMBER:-}|KINGUARD_PLACES_API_KEY=${KINGUARD_PLACES_API_KEY:-}|KINGUARD_DIAGNOSTICS_MODE=${KINGUARD_DIAGNOSTICS_MODE:-seeded}|KINGUARD_DEMO_CIRCLE_NAME=${KINGUARD_DEMO_CIRCLE_NAME:-}|KINGUARD_DEMO_CIRCLE_E164=${KINGUARD_DEMO_CIRCLE_E164:-}|KINGUARD_DEMO_CIRCLE_LANGUAGE=${KINGUARD_DEMO_CIRCLE_LANGUAGE:-ta}|KINGUARD_BOOKER_URL=${KINGUARD_BOOKER_URL:-}|KINGUARD_BOOKING_CHANNELS=${KINGUARD_BOOKING_CHANNELS:-web}|KINGUARD_DEMO_ROLE_TAGS=${KINGUARD_DEMO_ROLE_TAGS:-off}|KINGUARD_MEMORY_BANK=${KINGUARD_MEMORY_BANK:-}|KINGUARD_DETECT_LANGUAGE_MODE=${KINGUARD_DETECT_LANGUAGE_MODE:-gemini}|KINGUARD_SANDBOX=${KINGUARD_SANDBOX:-off}|KINGUARD_SANDBOX_DAILY_CAP=${KINGUARD_SANDBOX_DAILY_CAP:-25}|KINGUARD_SANDBOX_TTL_HOURS=${KINGUARD_SANDBOX_TTL_HOURS:-24}|KINGUARD_FIREBASE_API_KEY=${KINGUARD_FIREBASE_API_KEY:-}|KINGUARD_FIREBASE_AUTH_DOMAIN=${KINGUARD_FIREBASE_AUTH_DOMAIN:-}|KINGUARD_FIREBASE_PROJECT_ID=${KINGUARD_FIREBASE_PROJECT_ID:-}|KINGUARD_FIREBASE_STORAGE_BUCKET=${KINGUARD_FIREBASE_STORAGE_BUCKET:-}|KINGUARD_FIREBASE_MESSAGING_SENDER_ID=${KINGUARD_FIREBASE_MESSAGING_SENDER_ID:-}|KINGUARD_FIREBASE_APP_ID=${KINGUARD_FIREBASE_APP_ID:-}|KINGUARD_FIREBASE_MODEL=${KINGUARD_FIREBASE_MODEL:-gemini-2.5-flash}|KINGUARD_FIREBASE_RECAPTCHA_SITE_KEY=${KINGUARD_FIREBASE_RECAPTCHA_SITE_KEY:-}|KINGUARD_FIREBASE_APPCHECK_DEBUG=${KINGUARD_FIREBASE_APPCHECK_DEBUG:-false}" \
  --set-secrets "TWILIO_API_KEY_SECRET=twilio-api-key-secret:latest,TWILIO_AUTH_TOKEN=twilio-auth-token:latest,KINGUARD_LINK_SECRET=kinguard-link-secret:latest"

URL=$(gcloud run services describe "${SERVICE}" --project "${PROJECT_ID}" --region "${REGION}" --format='value(status.url)')
echo
echo "Deployed: ${URL}"
echo "Health:   curl ${URL}/api/healthz"
