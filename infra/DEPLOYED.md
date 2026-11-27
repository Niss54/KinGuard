# Deployment status

No deployment of this submission has been verified. Credentials are pending. Legacy project IDs, URLs and handset anecdotes are not evidence of a working current service.

Use `.env.example`, `infra/deploy_cloud_run.sh` and the README for setup. Keep credentials outside Git. Use synthetic records and a stable signing key. After deployment, verify App Check, actual inference source, authenticated intake, document storage and receipt verification.

Receipt and completeness checkpoint writes are atomic. Old chains without checkpoints fail closed. Do not automatically reconstruct checkpoints from possibly truncated rows: review against independent retained evidence, or start fresh synthetic cases. Database-wide rollback including the checkpoint requires an external anchor to detect; this app does not provide one.

Record the actual deployed commit, URL and test evidence here only after running them. Video and Devpost remain separate deliverables.
